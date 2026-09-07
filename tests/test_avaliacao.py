"""Testes do motor de avaliação.  Correr com:  python3 -m unittest -v"""

from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from avaliador import FonteCSV, Viatura, avaliar, carregar_config
from avaliador.comparaveis import ajustar, mediana_ponderada, percentil, remover_outliers, selecionar
from avaliador.config import CONFIG_PADRAO
from avaliador.fontes import CAMINHO_EXEMPLO, ler_csv
from avaliador.modelos import Anuncio


def anuncio(**kw) -> Anuncio:
    base = dict(
        id="X", fonte="teste", marca="Renault", modelo="Clio", versao="1.0 TCe", ano=2019,
        combustivel="Gasolina", caixa="Manual", quilometros=80000, potencia_cv=90, preco=12000.0,
    )
    base.update(kw)
    return Anuncio(**base)


def cfg_teste() -> dict:
    return copy.deepcopy(CONFIG_PADRAO)


class TestAjustes(unittest.TestCase):
    def test_desconto_negociacao(self):
        c = ajustar(anuncio(preco=10000), Viatura("Renault", "Clio", 2019, 80000, "Gasolina"), cfg_teste())
        self.assertAlmostEqual(c.preco_transacao, 9500.0)

    def test_anuncio_com_mais_km_sobe_valor_da_viatura(self):
        v = Viatura("Renault", "Clio", 2019, 50000, "Gasolina")
        c = ajustar(anuncio(quilometros=100000), v, cfg_teste())
        self.assertGreater(c.ajuste_km, 0)
        self.assertGreater(c.preco_ajustado, c.preco_transacao)

    def test_viatura_mais_recente_sobe_valor(self):
        v = Viatura("Renault", "Clio", 2021, 80000, "Gasolina")
        c = ajustar(anuncio(ano=2019), v, cfg_teste())
        self.assertGreater(c.ajuste_ano, 0)

    def test_viatura_mais_antiga_desce_valor(self):
        v = Viatura("Renault", "Clio", 2017, 80000, "Gasolina")
        c = ajustar(anuncio(ano=2019), v, cfg_teste())
        self.assertLess(c.ajuste_ano, 0)

    def test_identico_tem_peso_1(self):
        v = Viatura("Renault", "Clio", 2019, 80000, "Gasolina")
        c = ajustar(anuncio(), v, cfg_teste())
        self.assertAlmostEqual(c.peso, 1.0)
        self.assertAlmostEqual(c.ajuste_km, 0.0)
        self.assertAlmostEqual(c.ajuste_ano, 0.0)


class TestEstatisticas(unittest.TestCase):
    def test_percentil(self):
        self.assertEqual(percentil([1, 2, 3, 4, 5], 50), 3)
        self.assertEqual(percentil([1, 2, 3, 4], 50), 2.5)
        self.assertEqual(percentil([7], 90), 7)

    def test_mediana_ponderada_favorece_pesos(self):
        self.assertEqual(mediana_ponderada([10, 20, 30], [1, 1, 10]), 30)
        self.assertEqual(mediana_ponderada([10, 20, 30], [1, 1, 1]), 20)

    def test_remover_outliers(self):
        v = Viatura("Renault", "Clio", 2019, 80000, "Gasolina")
        precos = [11800, 12000, 12100, 12200, 11900, 12050, 25000, 5000]
        comps = [ajustar(anuncio(id=str(i), preco=p), v, cfg_teste()) for i, p in enumerate(precos)]
        mantidos, removidos = remover_outliers(comps)
        self.assertEqual(len(removidos), 2)
        self.assertEqual({c.anuncio.id for c in removidos}, {"6", "7"})

    def test_poucos_comparaveis_nao_remove_outliers(self):
        v = Viatura("Renault", "Clio", 2019, 80000, "Gasolina")
        comps = [ajustar(anuncio(id=str(i), preco=p), v, cfg_teste()) for i, p in enumerate([12000, 12100, 30000])]
        mantidos, removidos = remover_outliers(comps)
        self.assertEqual(len(mantidos), 3)


class TestSelecao(unittest.TestCase):
    def test_filtra_por_marca_modelo_combustivel(self):
        anuncios = [
            anuncio(id="a"),
            anuncio(id="b", combustivel="Diesel"),
            anuncio(id="c", modelo="Mégane"),
            anuncio(id="d", marca="peugeot"),
            anuncio(id="e", marca="RENAULT", modelo="clio"),  # normalização de maiúsculas
        ]
        v = Viatura("Renault", "Clio", 2019, 80000, "Gasolina")
        sel, _ = selecionar(anuncios, v, cfg_teste())
        self.assertEqual({a.id for a in sel}, {"a", "e"} | set())  # apenas os Clio gasolina
        self.assertNotIn("b", {a.id for a in sel})

    def test_alarga_criterios_quando_faltam_comparaveis(self):
        anuncios = [anuncio(id="a"), anuncio(id="b", ano=2016), anuncio(id="c", ano=2022)]
        v = Viatura("Renault", "Clio", 2019, 80000, "Gasolina")
        sel, avisos = selecionar(anuncios, v, cfg_teste())
        self.assertEqual(len(sel), 3)
        self.assertTrue(any("alargados" in a for a in avisos))

    def test_relaxa_caixa_quando_faltam_comparaveis(self):
        anuncios = [anuncio(id="a"), anuncio(id="b", caixa="Automática"), anuncio(id="c", caixa="Automática")]
        v = Viatura("Renault", "Clio", 2019, 80000, "Gasolina", caixa="Manual")
        sel, avisos = selecionar(anuncios, v, cfg_teste())
        self.assertEqual(len(sel), 3)
        self.assertTrue(any("caixa" in a for a in avisos))


class TestAvaliacao(unittest.TestCase):
    def setUp(self):
        self.v = Viatura("Renault", "Clio", 2019, 80000, "Gasolina", estado=3)
        self.anuncios = [
            anuncio(id=str(i), ano=2018 + i % 3, quilometros=70000 + i * 4000, preco=12000 + (i % 4) * 150)
            for i in range(10)
        ]

    def test_proposta_abaixo_do_valor_de_mercado(self):
        r = avaliar(self.v, self.anuncios, cfg_teste())
        self.assertTrue(r.suficiente)
        self.assertLess(r.proposta_compra, r.valor_mercado)
        self.assertLessEqual(r.intervalo[0], r.valor_mercado)
        self.assertGreaterEqual(r.intervalo[1], r.valor_mercado)

    def test_decomposicao_da_proposta(self):
        cfg = cfg_teste()
        cfg["arredondamento_eur"] = 0
        r = avaliar(self.v, self.anuncios, cfg)
        d = r.detalhe
        esperado = d["valor_mercado_bruto"] - d["margem_eur"] - d["custos_fixos_eur"] - d["recondicionamento_eur"]
        self.assertAlmostEqual(r.proposta_compra, esperado, places=1)

    def test_estado_mau_baixa_valor(self):
        bom = avaliar(Viatura("Renault", "Clio", 2019, 80000, "Gasolina", estado=5), self.anuncios, cfg_teste())
        mau = avaliar(Viatura("Renault", "Clio", 2019, 80000, "Gasolina", estado=1), self.anuncios, cfg_teste())
        self.assertGreater(bom.valor_mercado, mau.valor_mercado)
        self.assertGreater(bom.proposta_compra, mau.proposta_compra)

    def test_sem_comparaveis_suficientes(self):
        r = avaliar(self.v, self.anuncios[:2], cfg_teste())
        self.assertFalse(r.suficiente)
        self.assertIsNone(r.valor_mercado)
        self.assertEqual(r.confianca, "insuficiente")
        self.assertTrue(r.avisos)

    def test_arredondamento(self):
        r = avaliar(self.v, self.anuncios, cfg_teste())
        self.assertEqual(r.valor_mercado % 50, 0)
        self.assertEqual(r.proposta_compra % 50, 0)

    def test_para_dict_serializavel(self):
        r = avaliar(self.v, self.anuncios, cfg_teste())
        json.dumps(r.para_dict(), ensure_ascii=False)

    def test_estado_invalido(self):
        with self.assertRaises(ValueError):
            Viatura("Renault", "Clio", 2019, 80000, "Gasolina", estado=7)


class TestFontes(unittest.TestCase):
    def test_csv_exemplo_carrega(self):
        fonte = FonteCSV(CAMINHO_EXEMPLO)
        anuncios = fonte.carregar()
        self.assertGreater(len(anuncios), 200)
        self.assertIn("Renault", fonte.catalogo())
        self.assertIn("Clio", fonte.catalogo()["Renault"])

    def test_avaliacao_com_dados_exemplo(self):
        fonte = FonteCSV(CAMINHO_EXEMPLO)
        v = Viatura("Renault", "Clio", 2019, 85000, "Gasolina")
        r = avaliar(v, fonte.obter("Renault", "Clio"), carregar_config())
        self.assertTrue(r.suficiente)
        self.assertGreater(r.valor_mercado, 5000)
        self.assertLess(r.valor_mercado, 20000)

    def test_csv_com_colunas_em_falta(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "mau.csv"
            p.write_text("id,marca\n1,Renault\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                ler_csv(p)

    def test_config_json_funde_com_padrao(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "config.json"
            p.write_text(json.dumps({"proposta": {"margem_pct": 20}}), encoding="utf-8")
            cfg = carregar_config(p)
            self.assertEqual(cfg["proposta"]["margem_pct"], 20)
            self.assertEqual(cfg["proposta"]["custos_fixos_eur"], CONFIG_PADRAO["proposta"]["custos_fixos_eur"])


if __name__ == "__main__":
    unittest.main()
