"""Estruturas de dados usadas pelo avaliador."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class Anuncio:
    """Um anúncio de venda recolhido do mercado (Standvirtual, OLX, AutoScout24, ...)."""

    id: str
    fonte: str
    marca: str
    modelo: str
    versao: str
    ano: int
    combustivel: str
    caixa: str
    quilometros: int
    potencia_cv: int
    preco: float
    data_recolha: str = ""
    url: str = ""

    def para_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Viatura:
    """A viatura que o cliente pretende vender."""

    marca: str
    modelo: str
    ano: int
    quilometros: int
    combustivel: str
    caixa: str = ""  # vazio = indiferente
    potencia_cv: int = 0  # 0 = desconhecido
    estado: int = 3  # 1 (mau) .. 5 (impecável)

    def __post_init__(self) -> None:
        if not 1 <= int(self.estado) <= 5:
            raise ValueError("estado tem de estar entre 1 e 5")
        self.estado = int(self.estado)
        if self.quilometros < 0:
            raise ValueError("quilometros não pode ser negativo")

    def para_dict(self) -> dict[str, Any]:
        return asdict(self)

    def descricao(self) -> str:
        partes = [f"{self.marca} {self.modelo} {self.ano}", self.combustivel]
        if self.caixa:
            partes.append(self.caixa)
        partes.append(f"{self.quilometros:,} km".replace(",", " "))
        partes.append(f"estado {self.estado}/5")
        return ", ".join(partes)


@dataclass
class Comparavel:
    """Um anúncio depois de ajustado à viatura em avaliação."""

    anuncio: Anuncio
    preco_transacao: float  # preço do anúncio após desconto de negociação
    ajuste_km: float  # € somados/subtraídos pela diferença de km
    ajuste_ano: float  # € somados/subtraídos pela diferença de ano
    preco_ajustado: float  # preço "como se fosse" a viatura em avaliação
    peso: float  # 1.0 = idêntico; decresce com a distância em ano/km

    def para_dict(self) -> dict[str, Any]:
        return {
            "anuncio": self.anuncio.para_dict(),
            "preco_transacao": round(self.preco_transacao, 2),
            "ajuste_km": round(self.ajuste_km, 2),
            "ajuste_ano": round(self.ajuste_ano, 2),
            "preco_ajustado": round(self.preco_ajustado, 2),
            "peso": round(self.peso, 4),
        }


@dataclass
class ResultadoAvaliacao:
    viatura: Viatura
    valor_mercado: float | None  # None quando não há comparáveis suficientes
    intervalo: tuple[float, float] | None  # P25–P75 dos comparáveis ajustados
    proposta_compra: float | None
    n_comparaveis: int
    confianca: str  # "alta" | "media" | "baixa" | "insuficiente"
    comparaveis: list[Comparavel] = field(default_factory=list)
    detalhe: dict[str, Any] = field(default_factory=dict)
    avisos: list[str] = field(default_factory=list)

    @property
    def suficiente(self) -> bool:
        return self.valor_mercado is not None

    def para_dict(self) -> dict[str, Any]:
        return {
            "viatura": self.viatura.para_dict(),
            "valor_mercado": self.valor_mercado,
            "intervalo": list(self.intervalo) if self.intervalo else None,
            "proposta_compra": self.proposta_compra,
            "n_comparaveis": self.n_comparaveis,
            "confianca": self.confianca,
            "comparaveis": [c.para_dict() for c in self.comparaveis],
            "detalhe": self.detalhe,
            "avisos": self.avisos,
        }
