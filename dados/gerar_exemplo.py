"""Gera um ficheiro CSV de anúncios sintéticos mas realistas para o mercado português.

Uso:  python3 dados/gerar_exemplo.py [caminho_saida.csv]

Os dados são determinísticos (semente fixa) e servem apenas para demonstrar o
protótipo. Substitua-os por uma exportação real de anúncios quando possível.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from avaliador.fontes import escrever_csv  # noqa: E402
from avaliador.modelos import Anuncio  # noqa: E402

SEMENTE = 42

# (marca, modelo, preço novo aprox. €, [(versão, combustível, cv, caixa)], nº anúncios)
MODELOS = [
    ("Renault", "Clio", 19000, [("1.0 TCe 90 Intens", "Gasolina", 90, "Manual"), ("1.0 SCe 75 Zen", "Gasolina", 75, "Manual"), ("1.5 dCi 85 Limited", "Diesel", 85, "Manual"), ("1.3 TCe 130 RS Line EDC", "Gasolina", 130, "Automática")], 26),
    ("Renault", "Mégane", 26000, [("1.5 dCi 115 Limited", "Diesel", 115, "Manual"), ("1.3 TCe 140 GT Line", "Gasolina", 140, "Manual"), ("1.5 Blue dCi 115 EDC", "Diesel", 115, "Automática")], 18),
    ("Peugeot", "208", 20000, [("1.2 PureTech 75 Active", "Gasolina", 75, "Manual"), ("1.2 PureTech 100 Allure", "Gasolina", 100, "Manual"), ("1.5 BlueHDi 100 Style", "Diesel", 100, "Manual")], 24),
    ("Peugeot", "308", 27000, [("1.5 BlueHDi 130 Allure", "Diesel", 130, "Manual"), ("1.2 PureTech 130 GT Line EAT8", "Gasolina", 130, "Automática")], 16),
    ("Peugeot", "2008", 25000, [("1.2 PureTech 100 Active", "Gasolina", 100, "Manual"), ("1.5 BlueHDi 110 Allure", "Diesel", 110, "Manual")], 14),
    ("Volkswagen", "Golf", 28000, [("1.0 TSI 110 Life", "Gasolina", 110, "Manual"), ("1.6 TDI 115 Confortline", "Diesel", 115, "Manual"), ("2.0 TDI 150 DSG", "Diesel", 150, "Automática")], 22),
    ("Volkswagen", "Polo", 21000, [("1.0 TSI 95 Confortline", "Gasolina", 95, "Manual"), ("1.0 MPI 80 Trendline", "Gasolina", 80, "Manual"), ("1.6 TDI 95", "Diesel", 95, "Manual")], 22),
    ("Toyota", "Yaris", 21000, [("1.5 Hybrid Comfort", "Híbrido", 116, "Automática"), ("1.0 VVT-i Comfort", "Gasolina", 72, "Manual")], 18),
    ("Toyota", "Corolla", 30000, [("1.8 Hybrid Comfort", "Híbrido", 122, "Automática"), ("2.0 Hybrid Exclusive", "Híbrido", 184, "Automática")], 12),
    ("Opel", "Corsa", 18500, [("1.2 75 Edition", "Gasolina", 75, "Manual"), ("1.2 Turbo 100 Elegance", "Gasolina", 100, "Manual"), ("1.5 D 100 Edition", "Diesel", 100, "Manual")], 20),
    ("Seat", "Ibiza", 18500, [("1.0 TSI 95 Style", "Gasolina", 95, "Manual"), ("1.0 MPI 80 Reference", "Gasolina", 80, "Manual"), ("1.6 TDI 95 Style", "Diesel", 95, "Manual")], 20),
    ("Seat", "Leon", 26000, [("1.6 TDI 115 Style", "Diesel", 115, "Manual"), ("1.5 TSI 130 FR", "Gasolina", 130, "Manual"), ("2.0 TDI 150 FR DSG", "Diesel", 150, "Automática")], 18),
    ("BMW", "Série 1", 35000, [("116d Advantage", "Diesel", 116, "Manual"), ("118d Line Sport Auto", "Diesel", 150, "Automática"), ("118i Auto", "Gasolina", 136, "Automática")], 18),
    ("Mercedes-Benz", "Classe A", 37000, [("A 180 d Style", "Diesel", 116, "Automática"), ("A 200 AMG Line", "Gasolina", 163, "Automática")], 16),
    ("Nissan", "Qashqai", 30000, [("1.5 dCi 115 N-Connecta", "Diesel", 115, "Manual"), ("1.3 DIG-T 140 Acenta", "Gasolina", 140, "Manual")], 16),
    ("Dacia", "Sandero", 13000, [("1.0 SCe 75 Comfort", "Gasolina", 75, "Manual"), ("1.0 TCe 90 Stepway", "Gasolina", 90, "Manual"), ("1.5 dCi 90 Stepway", "Diesel", 90, "Manual")], 20),
    ("Ford", "Fiesta", 17500, [("1.1 Ti-VCT 75 Trend", "Gasolina", 75, "Manual"), ("1.0 EcoBoost 100 Titanium", "Gasolina", 100, "Manual"), ("1.5 TDCi 85 Trend", "Diesel", 85, "Manual")], 18),
    ("Ford", "Focus", 25000, [("1.5 TDCi 120 Titanium", "Diesel", 120, "Manual"), ("1.0 EcoBoost 125 ST-Line", "Gasolina", 125, "Manual")], 14),
    ("Hyundai", "i20", 18000, [("1.2 MPI 84 Comfort", "Gasolina", 84, "Manual"), ("1.0 T-GDi 100 Style", "Gasolina", 100, "Manual")], 12),
    ("Fiat", "500", 16000, [("1.2 69 Lounge", "Gasolina", 69, "Manual"), ("1.0 Hybrid 70 Dolcevita", "Híbrido", 70, "Manual")], 14),
    ("Citroën", "C3", 18000, [("1.2 PureTech 83 Feel", "Gasolina", 83, "Manual"), ("1.5 BlueHDi 100 Shine", "Diesel", 100, "Manual")], 14),
    ("Audi", "A3", 34000, [("30 TDI Sportback", "Diesel", 116, "Manual"), ("35 TFSI S tronic", "Gasolina", 150, "Automática")], 14),
    ("Skoda", "Octavia", 28000, [("1.6 TDI 115 Ambition", "Diesel", 115, "Manual"), ("2.0 TDI 150 Style DSG", "Diesel", 150, "Automática")], 12),
]

FONTES = [("standvirtual", 0.55), ("olx", 0.25), ("autoscout24", 0.20)]
ANO_ATUAL = 2026
ANOS = list(range(2014, 2025))
PESOS_ANOS = [1, 2, 3, 4, 5, 6, 6, 6, 5, 4, 3]  # mais anúncios entre 2017 e 2022


def _escolher_fonte(r: random.Random) -> str:
    return r.choices([f for f, _ in FONTES], weights=[p for _, p in FONTES])[0]


def _preco(r: random.Random, preco_novo: float, ano: int, km: int, combustivel: str) -> float:
    idade = max(1, ANO_ATUAL - ano)
    # Curva de depreciação típica: ~20 % no 1º ano, ~9 % ao ano depois.
    valor = preco_novo * 0.80 * (0.91 ** (idade - 1))
    km_esperados = idade * 15000
    valor *= 1 - 0.015 * (km - km_esperados) / 10000  # ±1,5 % por 10 000 km face ao esperado
    if combustivel == "Diesel":
        valor *= 0.97  # diesel ligeiramente penalizado no mercado atual
    if combustivel == "Híbrido":
        valor *= 1.05
    valor *= r.gauss(1.0, 0.06)  # dispersão normal entre vendedores
    # ~4 % dos anúncios são atípicos (preço absurdo, erro de digitação, dealer premium)
    sorte = r.random()
    if sorte < 0.02:
        valor *= r.uniform(1.30, 1.45)
    elif sorte < 0.04:
        valor *= r.uniform(0.60, 0.72)
    return max(1000.0, round(valor / 50) * 50)


def gerar() -> list[Anuncio]:
    r = random.Random(SEMENTE)
    anuncios: list[Anuncio] = []
    contador = 1
    for marca, modelo, preco_novo, versoes, n in MODELOS:
        for _ in range(n):
            versao, combustivel, cv, caixa = r.choice(versoes)
            ano = r.choices(ANOS, weights=PESOS_ANOS)[0]
            idade = max(1, ANO_ATUAL - ano)
            km = int(max(5000, r.lognormvariate(0, 0.35) * idade * 15000))
            km = round(km / 500) * 500
            fonte = _escolher_fonte(r)
            dia = r.randint(1, 6)
            anuncios.append(
                Anuncio(
                    id=f"A{contador:04d}",
                    fonte=fonte,
                    marca=marca,
                    modelo=modelo,
                    versao=versao,
                    ano=ano,
                    combustivel=combustivel,
                    caixa=caixa,
                    quilometros=km,
                    potencia_cv=cv,
                    preco=_preco(r, preco_novo, ano, km, combustivel),
                    data_recolha=f"2026-09-{dia:02d}",
                    url=f"https://exemplo.local/{fonte}/{contador}",
                )
            )
            contador += 1
    return anuncios


def main(argv: list[str]) -> int:
    saida = Path(argv[1]) if len(argv) > 1 else Path(__file__).resolve().parent / "anuncios_exemplo.csv"
    anuncios = gerar()
    escrever_csv(saida, anuncios)
    print(f"{len(anuncios)} anúncios escritos em {saida}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
