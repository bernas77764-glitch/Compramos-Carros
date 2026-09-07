"""Avaliador automático de viaturas usadas — protótipo.

Estima o valor de mercado de uma viatura a partir de anúncios comparáveis
(Standvirtual, OLX, AutoScout24, ...) e calcula uma proposta de compra
aplicando margem, custos fixos e recondicionamento.
"""

from .avaliacao import avaliar
from .config import carregar_config
from .fontes import FonteCSV
from .modelos import Anuncio, Comparavel, ResultadoAvaliacao, Viatura

__all__ = [
    "Anuncio",
    "Comparavel",
    "FonteCSV",
    "ResultadoAvaliacao",
    "Viatura",
    "avaliar",
    "carregar_config",
]
