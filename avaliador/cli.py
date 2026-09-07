"""Interface de linha de comandos.

    python3 -m avaliador avaliar --marca Renault --modelo Clio --ano 2019 --km 85000 --combustivel Gasolina
    python3 -m avaliador modelos
    python3 -m avaliador servir --porta 8000
"""

from __future__ import annotations

import argparse
import json
import sys

from .avaliacao import avaliar
from .config import carregar_config
from .fontes import FonteCSV
from .modelos import ResultadoAvaliacao, Viatura


def eur(valor: float | None) -> str:
    if valor is None:
        return "—"
    return f"{valor:,.0f} €".replace(",", " ")


def formatar_texto(res: ResultadoAvaliacao) -> str:
    linhas = [f"Viatura: {res.viatura.descricao()}"]
    if not res.suficiente:
        linhas.append("Resultado: SEM VALOR — comparáveis insuficientes.")
        for a in res.avisos:
            linhas.append(f"  ! {a}")
        return "\n".join(linhas)

    d = res.detalhe
    minimo, maximo = res.intervalo  # type: ignore[misc]
    linhas += [
        f"Comparáveis usados: {res.n_comparaveis}   Confiança: {res.confianca.upper()}",
        "",
        f"Valor de mercado estimado:  {eur(res.valor_mercado):>12}   (intervalo {eur(minimo)} – {eur(maximo)})",
        f"  Mediana ponderada dos comparáveis ajustados: {eur(d['mediana_ponderada'])}",
        f"  Ajuste por estado ({res.viatura.estado}/5): {d['ajuste_estado_pct']:+.0f} %",
        "",
        f"Proposta de compra:         {eur(res.proposta_compra):>12}",
        f"  {'Margem (' + format(d['margem_pct'], '.0f') + ' %):':<30}{'-' + eur(d['margem_eur']):>10}",
        f"  {'Custos fixos:':<30}{'-' + eur(d['custos_fixos_eur']):>10}",
        f"  {'Recondicionamento (estado ' + str(res.viatura.estado) + '):':<30}{'-' + eur(d['recondicionamento_eur']):>10}",
        "",
        "Comparáveis (ordenados por semelhança):",
        f"  {'ID':<6} {'Fonte':<12} {'Ano':<5} {'Km':>8} {'Caixa':<11} {'Anúncio':>10} {'Aj. km':>9} {'Aj. ano':>9} {'Ajustado':>10} {'Peso':>5}",
    ]
    for c in res.comparaveis:
        a = c.anuncio
        linhas.append(
            f"  {a.id:<6} {a.fonte:<12} {a.ano:<5} {a.quilometros:>8,} {a.caixa:<11} {a.preco:>10,.0f} "
            f"{c.ajuste_km:>+9,.0f} {c.ajuste_ano:>+9,.0f} {c.preco_ajustado:>10,.0f} {c.peso:>5.2f}".replace(",", " ")
        )
    if res.avisos:
        linhas.append("")
        linhas.append("Avisos:")
        for a in res.avisos:
            linhas.append(f"  ! {a}")
    return "\n".join(linhas)


def _cmd_avaliar(args: argparse.Namespace) -> int:
    fonte = FonteCSV(args.anuncios)
    cfg = carregar_config(args.config)
    viatura = Viatura(
        marca=args.marca,
        modelo=args.modelo,
        ano=args.ano,
        quilometros=args.km,
        combustivel=args.combustivel,
        caixa=args.caixa or "",
        potencia_cv=args.cv or 0,
        estado=args.estado,
    )
    res = avaliar(viatura, fonte.obter(viatura.marca, viatura.modelo), cfg)
    if args.json:
        print(json.dumps(res.para_dict(), ensure_ascii=False, indent=2))
    else:
        print(formatar_texto(res))
    return 0 if res.suficiente else 2


def _cmd_modelos(args: argparse.Namespace) -> int:
    fonte = FonteCSV(args.anuncios)
    total = len(fonte.carregar())
    print(f"{total} anúncios em {fonte.caminho}\n")
    for marca, modelos in fonte.catalogo().items():
        contagens = ", ".join(f"{m} ({len(fonte.obter(marca, m))})" for m in modelos)
        print(f"{marca}: {contagens}")
    return 0


def _cmd_servir(args: argparse.Namespace) -> int:
    from .servidor import servir

    servir(porta=args.porta, caminho_anuncios=args.anuncios, caminho_config=args.config)
    return 0


def criar_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="avaliador", description="Avaliador automático de viaturas usadas (protótipo).")
    p.add_argument("--anuncios", help="CSV de anúncios (padrão: dados/anuncios_exemplo.csv)")
    p.add_argument("--config", help="JSON de parâmetros (padrão: dados/config.json)")
    sub = p.add_subparsers(dest="comando", required=True)

    a = sub.add_parser("avaliar", help="avaliar uma viatura")
    a.add_argument("--marca", required=True)
    a.add_argument("--modelo", required=True)
    a.add_argument("--ano", type=int, required=True)
    a.add_argument("--km", type=int, required=True)
    a.add_argument("--combustivel", required=True, help="Gasolina | Diesel | Híbrido | Elétrico")
    a.add_argument("--caixa", help="Manual | Automática (omitir = indiferente)")
    a.add_argument("--cv", type=int, help="potência em cv (informativo)")
    a.add_argument("--estado", type=int, default=3, choices=range(1, 6), help="1 mau … 5 impecável (padrão 3)")
    a.add_argument("--json", action="store_true", help="saída em JSON")
    a.set_defaults(func=_cmd_avaliar)

    m = sub.add_parser("modelos", help="listar marcas/modelos disponíveis na fonte")
    m.set_defaults(func=_cmd_modelos)

    s = sub.add_parser("servir", help="arrancar a interface web local")
    s.add_argument("--porta", type=int, default=8000)
    s.set_defaults(func=_cmd_servir)
    return p


def main(argv: list[str] | None = None) -> int:
    args = criar_parser().parse_args(argv)
    try:
        return args.func(args)
    except (FileNotFoundError, ValueError) as e:
        print(f"Erro: {e}", file=sys.stderr)
        return 1
    except BrokenPipeError:  # ex.: saída encaminhada para `head`
        return 0
