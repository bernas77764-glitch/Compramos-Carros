"""Parâmetros de negócio do avaliador.

Todos os valores podem ser afinados em ``dados/config.json`` sem tocar no
código. Os valores abaixo são apenas um ponto de partida razoável para o
mercado português e devem ser calibrados com dados reais (ver
``docs/ESTUDO_VIABILIDADE.md``).
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

CAMINHO_CONFIG_PADRAO = Path(__file__).resolve().parent.parent / "dados" / "config.json"

CONFIG_PADRAO: dict[str, Any] = {
    # Como escolher anúncios comparáveis
    "criterios": {
        "tolerancia_anos": 2,  # ± anos em relação à viatura
        "tolerancia_km": 60000,  # ± km em relação à viatura
        "minimo_comparaveis": 3,  # abaixo disto não se dá valor
    },
    # Como ajustar o preço de cada anúncio à viatura em avaliação
    "ajustes": {
        "pct_por_10000_km": 1.5,  # % do preço por cada 10 000 km de diferença
        "pct_por_ano": 6.0,  # % do preço por cada ano de diferença
        "desconto_negociacao_pct": 5.0,  # preço de anúncio → preço real de transação
    },
    # Ajuste ao valor de mercado consoante o estado (1 mau … 5 impecável), em %
    "estado": {"1": -15.0, "2": -8.0, "3": 0.0, "4": 3.0, "5": 6.0},
    # Como passar do valor de mercado à proposta de compra
    "proposta": {
        "margem_pct": 12.0,  # margem bruta pretendida sobre o valor de mercado
        "custos_fixos_eur": 350.0,  # transporte, legalização, preparação, etc.
        "recondicionamento_por_estado_eur": {
            "1": 1500.0,
            "2": 800.0,
            "3": 400.0,
            "4": 150.0,
            "5": 0.0,
        },
    },
    # Classificação da confiança da estimativa
    "confianca": {
        "cv_alta": 0.08,  # coeficiente de variação (desvio/média) abaixo disto = alta
        "cv_media": 0.15,
        "n_alta": 8,  # nº de comparáveis a partir do qual pode ser alta
        "n_media": 4,
    },
    # Arredondamento dos valores apresentados (em €)
    "arredondamento_eur": 50,
}


def _fundir(base: dict[str, Any], extra: dict[str, Any]) -> dict[str, Any]:
    resultado = copy.deepcopy(base)
    for chave, valor in extra.items():
        if isinstance(valor, dict) and isinstance(resultado.get(chave), dict):
            resultado[chave] = _fundir(resultado[chave], valor)
        else:
            resultado[chave] = valor
    return resultado


def carregar_config(caminho: str | Path | None = None) -> dict[str, Any]:
    """Devolve a configuração: valores padrão fundidos com o JSON, se existir."""
    caminho = Path(caminho) if caminho else CAMINHO_CONFIG_PADRAO
    if caminho.exists():
        with caminho.open(encoding="utf-8") as f:
            return _fundir(CONFIG_PADRAO, json.load(f))
    return copy.deepcopy(CONFIG_PADRAO)
