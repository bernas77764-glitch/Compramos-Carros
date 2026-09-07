"""Motor de avaliação: dos anúncios comparáveis à proposta de compra."""

from __future__ import annotations

import statistics
from typing import Any

from .comparaveis import ajustar, mediana_ponderada, percentil, remover_outliers, selecionar
from .config import carregar_config
from .modelos import Anuncio, ResultadoAvaliacao, Viatura


def _arredondar(valor: float, passo: float) -> float:
    if passo <= 0:
        return round(valor, 2)
    return round(round(valor / passo) * passo, 2)


def classificar_confianca(n: int, cv: float, cfg: dict[str, Any]) -> str:
    if n >= cfg["n_alta"] and cv <= cfg["cv_alta"]:
        return "alta"
    if n >= cfg["n_media"] and cv <= cfg["cv_media"]:
        return "media"
    return "baixa"


def avaliar(viatura: Viatura, anuncios: list[Anuncio], cfg: dict[str, Any] | None = None) -> ResultadoAvaliacao:
    """Avalia a viatura com base nos anúncios fornecidos.

    Passos:
    1. selecionar comparáveis (alargando critérios se necessário);
    2. ajustar cada preço ao ano/km da viatura e descontar a negociação;
    3. remover preços atípicos (IQR);
    4. valor de mercado = mediana ponderada × fator de estado;
    5. proposta = valor de mercado − margem − custos fixos − recondicionamento.
    """
    cfg = cfg or carregar_config()
    selecionados, avisos = selecionar(anuncios, viatura, cfg)
    minimo = cfg["criterios"]["minimo_comparaveis"]
    if len(selecionados) < minimo:
        return ResultadoAvaliacao(
            viatura=viatura,
            valor_mercado=None,
            intervalo=None,
            proposta_compra=None,
            n_comparaveis=len(selecionados),
            confianca="insuficiente",
            comparaveis=[ajustar(a, viatura, cfg) for a in selecionados],
            detalhe={},
            avisos=avisos,
        )

    comparaveis = [ajustar(a, viatura, cfg) for a in selecionados]
    comparaveis, removidos = remover_outliers(comparaveis)
    if removidos:
        avisos.append(f"{len(removidos)} anúncio(s) ignorado(s) por preço atípico (fora do intervalo interquartil).")
    comparaveis.sort(key=lambda c: c.peso, reverse=True)

    valores = [c.preco_ajustado for c in comparaveis]
    pesos = [c.peso for c in comparaveis]
    base = mediana_ponderada(valores, pesos)
    ordenados = sorted(valores)
    p25, p75 = percentil(ordenados, 25), percentil(ordenados, 75)

    ajuste_estado_pct = float(cfg["estado"][str(viatura.estado)])
    fator_estado = 1 + ajuste_estado_pct / 100
    passo = float(cfg.get("arredondamento_eur", 0))

    valor_mercado_bruto = base * fator_estado
    valor_mercado = _arredondar(valor_mercado_bruto, passo)
    intervalo = (_arredondar(p25 * fator_estado, passo), _arredondar(p75 * fator_estado, passo))

    pr = cfg["proposta"]
    margem_eur = valor_mercado_bruto * pr["margem_pct"] / 100
    custos_fixos = float(pr["custos_fixos_eur"])
    recondicionamento = float(pr["recondicionamento_por_estado_eur"][str(viatura.estado)])
    proposta_bruta = max(0.0, valor_mercado_bruto - margem_eur - custos_fixos - recondicionamento)
    proposta = _arredondar(proposta_bruta, passo)

    media = statistics.mean(valores)
    desvio = statistics.pstdev(valores) if len(valores) > 1 else 0.0
    cv = desvio / media if media else 1.0
    confianca = classificar_confianca(len(valores), cv, cfg["confianca"])
    if confianca == "baixa":
        avisos.append("Confiança baixa: poucos comparáveis ou preços muito dispersos. Confirmar manualmente.")

    detalhe = {
        "mediana_ponderada": round(base, 2),
        "p25": round(p25, 2),
        "p75": round(p75, 2),
        "ajuste_estado_pct": ajuste_estado_pct,
        "valor_mercado_bruto": round(valor_mercado_bruto, 2),
        "margem_pct": pr["margem_pct"],
        "margem_eur": round(margem_eur, 2),
        "custos_fixos_eur": custos_fixos,
        "recondicionamento_eur": recondicionamento,
        "proposta_bruta": round(proposta_bruta, 2),
        "coef_variacao": round(cv, 4),
        "outliers_removidos": len(removidos),
        "desconto_negociacao_pct": cfg["ajustes"]["desconto_negociacao_pct"],
    }
    return ResultadoAvaliacao(
        viatura=viatura,
        valor_mercado=valor_mercado,
        intervalo=intervalo,
        proposta_compra=proposta,
        n_comparaveis=len(valores),
        confianca=confianca,
        comparaveis=comparaveis,
        detalhe=detalhe,
        avisos=avisos,
    )
