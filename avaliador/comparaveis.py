"""Seleção e ajuste de anúncios comparáveis.

A lógica segue o método dos comparáveis usado em avaliação imobiliária:
1. escolher anúncios semelhantes (mesma marca/modelo/combustível, ano e km próximos);
2. ajustar o preço de cada um "como se" tivesse o ano e os km da viatura em avaliação;
3. remover preços atípicos;
4. resumir com uma mediana ponderada pela semelhança.
"""

from __future__ import annotations

from typing import Any

from .modelos import Anuncio, Comparavel, Viatura


def _norm(texto: str) -> str:
    return " ".join(str(texto).strip().lower().split())


def filtrar(
    anuncios: list[Anuncio],
    viatura: Viatura,
    tolerancia_anos: int,
    tolerancia_km: int,
    exigir_caixa: bool,
) -> list[Anuncio]:
    """Anúncios que cumprem os critérios de semelhança."""
    marca, modelo, comb = _norm(viatura.marca), _norm(viatura.modelo), _norm(viatura.combustivel)
    caixa = _norm(viatura.caixa) if viatura.caixa else ""
    resultado = []
    for a in anuncios:
        if _norm(a.marca) != marca or _norm(a.modelo) != modelo:
            continue
        if _norm(a.combustivel) != comb:
            continue
        if exigir_caixa and caixa and _norm(a.caixa) != caixa:
            continue
        if abs(a.ano - viatura.ano) > tolerancia_anos:
            continue
        if abs(a.quilometros - viatura.quilometros) > tolerancia_km:
            continue
        resultado.append(a)
    return resultado


def selecionar(
    anuncios: list[Anuncio], viatura: Viatura, cfg: dict[str, Any]
) -> tuple[list[Anuncio], list[str]]:
    """Seleciona comparáveis, alargando os critérios se forem poucos.

    Devolve (anúncios, avisos). Os avisos explicam ao avaliador quando a
    seleção teve de ser alargada — importante para confiar (ou não) no valor.
    """
    c = cfg["criterios"]
    minimo = c["minimo_comparaveis"]
    anos, km = c["tolerancia_anos"], c["tolerancia_km"]
    tentativas: list[tuple[int, int, bool, str | None]] = [
        (anos, km, True, None),
    ]
    if viatura.caixa:
        tentativas.append(
            (anos, km, False, "Poucos anúncios com a mesma caixa; a considerar também outras caixas de velocidades.")
        )
    tentativas.append(
        (
            anos + 1,
            int(km * 1.5),
            False,
            f"Critérios alargados para ±{anos + 1} anos e ±{int(km * 1.5):,} km por falta de comparáveis próximos.".replace(
                ",", " "
            ),
        )
    )

    avisos: list[str] = []
    selecionados: list[Anuncio] = []
    for t_anos, t_km, exigir_caixa, aviso in tentativas:
        selecionados = filtrar(anuncios, viatura, t_anos, t_km, exigir_caixa)
        if len(selecionados) >= minimo:
            if aviso:
                avisos.append(aviso)
            return selecionados, avisos
    avisos.append(
        f"Apenas {len(selecionados)} comparável(is) encontrado(s); são necessários pelo menos {minimo}. "
        "Avaliação manual recomendada."
    )
    return selecionados, avisos


def ajustar(anuncio: Anuncio, viatura: Viatura, cfg: dict[str, Any]) -> Comparavel:
    """Ajusta o preço do anúncio ao ano e km da viatura em avaliação."""
    aj = cfg["ajustes"]
    preco_transacao = anuncio.preco * (1 - aj["desconto_negociacao_pct"] / 100)

    # Se o anúncio tem mais km do que a viatura, a viatura vale mais (ajuste positivo).
    dif_km = anuncio.quilometros - viatura.quilometros
    ajuste_km = preco_transacao * (aj["pct_por_10000_km"] / 100) * (dif_km / 10000)

    # Se a viatura é mais recente do que o anúncio, vale mais (ajuste positivo).
    dif_ano = viatura.ano - anuncio.ano
    ajuste_ano = preco_transacao * (aj["pct_por_ano"] / 100) * dif_ano

    preco_ajustado = preco_transacao + ajuste_km + ajuste_ano
    # Peso: anúncios mais parecidos contam mais na mediana.
    peso = 1.0 / (1.0 + abs(dif_ano) + abs(dif_km) / 20000)
    return Comparavel(
        anuncio=anuncio,
        preco_transacao=preco_transacao,
        ajuste_km=ajuste_km,
        ajuste_ano=ajuste_ano,
        preco_ajustado=preco_ajustado,
        peso=peso,
    )


def percentil(valores_ordenados: list[float], p: float) -> float:
    """Percentil com interpolação linear (valores já ordenados)."""
    if not valores_ordenados:
        raise ValueError("lista vazia")
    if len(valores_ordenados) == 1:
        return valores_ordenados[0]
    pos = (len(valores_ordenados) - 1) * p / 100
    i = int(pos)
    fracao = pos - i
    if i + 1 < len(valores_ordenados):
        return valores_ordenados[i] + (valores_ordenados[i + 1] - valores_ordenados[i]) * fracao
    return valores_ordenados[i]


def remover_outliers(
    comparaveis: list[Comparavel], minimo: int = 5, fator: float = 1.5
) -> tuple[list[Comparavel], list[Comparavel]]:
    """Regra do intervalo interquartil (IQR). Devolve (mantidos, removidos)."""
    if len(comparaveis) < minimo:
        return comparaveis, []
    ordenados = sorted(c.preco_ajustado for c in comparaveis)
    q1, q3 = percentil(ordenados, 25), percentil(ordenados, 75)
    iqr = q3 - q1
    inferior, superior = q1 - fator * iqr, q3 + fator * iqr
    mantidos = [c for c in comparaveis if inferior <= c.preco_ajustado <= superior]
    removidos = [c for c in comparaveis if not inferior <= c.preco_ajustado <= superior]
    return mantidos, removidos


def mediana_ponderada(valores: list[float], pesos: list[float]) -> float:
    if not valores:
        raise ValueError("lista vazia")
    pares = sorted(zip(valores, pesos))
    total = sum(pesos)
    acumulado = 0.0
    for valor, peso in pares:
        acumulado += peso
        if acumulado >= total / 2:
            return valor
    return pares[-1][0]
