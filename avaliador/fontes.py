"""Fontes de anúncios de mercado.

Neste protótipo os anúncios vêm de um ficheiro CSV (exportação manual ou
gerado pelo script ``dados/gerar_exemplo.py``). A interface ``FonteAnuncios``
permite trocar por uma API comercial ou outra origem sem alterar o motor.

Nota legal: o Standvirtual, OLX e AutoScout24 proíbem a recolha automática
(scraping) nos termos de serviço. Ver ``docs/ESTUDO_VIABILIDADE.md`` para as
alternativas.
"""

from __future__ import annotations

import csv
from abc import ABC, abstractmethod
from pathlib import Path

from .modelos import Anuncio

CAMINHO_EXEMPLO = Path(__file__).resolve().parent.parent / "dados" / "anuncios_exemplo.csv"

COLUNAS = [
    "id",
    "fonte",
    "marca",
    "modelo",
    "versao",
    "ano",
    "combustivel",
    "caixa",
    "quilometros",
    "potencia_cv",
    "preco",
    "data_recolha",
    "url",
]


def _norm(texto: str) -> str:
    return " ".join(str(texto).strip().lower().split())


class FonteAnuncios(ABC):
    """Interface de uma fonte de anúncios."""

    @abstractmethod
    def obter(self, marca: str, modelo: str) -> list[Anuncio]:
        """Anúncios da marca/modelo indicados."""

    @abstractmethod
    def catalogo(self) -> dict[str, list[str]]:
        """Marcas e modelos disponíveis: {marca: [modelo, ...]}."""


class FonteCSV(FonteAnuncios):
    """Anúncios lidos de um ficheiro CSV com as colunas de ``COLUNAS``."""

    def __init__(self, caminho: str | Path | None = None) -> None:
        self.caminho = Path(caminho) if caminho else CAMINHO_EXEMPLO
        self._anuncios: list[Anuncio] | None = None

    def carregar(self) -> list[Anuncio]:
        if self._anuncios is None:
            self._anuncios = ler_csv(self.caminho)
        return self._anuncios

    def obter(self, marca: str, modelo: str) -> list[Anuncio]:
        m, mo = _norm(marca), _norm(modelo)
        return [a for a in self.carregar() if _norm(a.marca) == m and _norm(a.modelo) == mo]

    def catalogo(self) -> dict[str, list[str]]:
        cat: dict[str, set[str]] = {}
        for a in self.carregar():
            cat.setdefault(a.marca, set()).add(a.modelo)
        return {marca: sorted(modelos) for marca, modelos in sorted(cat.items())}


def ler_csv(caminho: str | Path) -> list[Anuncio]:
    caminho = Path(caminho)
    if not caminho.exists():
        raise FileNotFoundError(f"Ficheiro de anúncios não encontrado: {caminho}")
    anuncios: list[Anuncio] = []
    with caminho.open(encoding="utf-8", newline="") as f:
        leitor = csv.DictReader(f)
        em_falta = [c for c in COLUNAS if c not in (leitor.fieldnames or []) and c not in ("data_recolha", "url")]
        if em_falta:
            raise ValueError(f"Colunas em falta no CSV: {', '.join(em_falta)}")
        for n, linha in enumerate(leitor, start=2):
            try:
                anuncios.append(
                    Anuncio(
                        id=linha["id"].strip(),
                        fonte=linha["fonte"].strip(),
                        marca=linha["marca"].strip(),
                        modelo=linha["modelo"].strip(),
                        versao=linha.get("versao", "").strip(),
                        ano=int(linha["ano"]),
                        combustivel=linha["combustivel"].strip(),
                        caixa=linha["caixa"].strip(),
                        quilometros=int(float(linha["quilometros"])),
                        potencia_cv=int(float(linha["potencia_cv"] or 0)),
                        preco=float(linha["preco"]),
                        data_recolha=(linha.get("data_recolha") or "").strip(),
                        url=(linha.get("url") or "").strip(),
                    )
                )
            except (KeyError, ValueError) as e:
                raise ValueError(f"Linha {n} inválida no CSV: {e}") from e
    return anuncios


def escrever_csv(caminho: str | Path, anuncios: list[Anuncio]) -> None:
    with Path(caminho).open("w", encoding="utf-8", newline="") as f:
        escritor = csv.DictWriter(f, fieldnames=COLUNAS)
        escritor.writeheader()
        for a in anuncios:
            escritor.writerow(a.para_dict())
