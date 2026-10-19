# Compramos Carros — Avaliador automático de viaturas (protótipo)

> **Site compramoscarros.pt:** está na pasta [`site/`](site/). Ver [`docs/SITE.md`](docs/SITE.md)
> para editar textos, configurar os formulários e publicar no domínio.

Protótipo para estudar a viabilidade de **automatizar a atribuição de valor** a viaturas usadas.
Parte de anúncios de mercado (Standvirtual, OLX, AutoScout24, …), encontra os anúncios
comparáveis, ajusta-os ao ano e quilometragem da viatura e calcula:

- **Valor de mercado estimado** (com intervalo e nível de confiança);
- **Proposta de compra** = valor de mercado − margem − custos fixos − recondicionamento.

O cálculo é totalmente transparente: cada resultado mostra os anúncios usados, os ajustes
aplicados a cada um e o peso que teve na estimativa.

> Estado: **protótipo de estudo**. Os anúncios incluídos são sintéticos (gerados) e os
> parâmetros são um ponto de partida por afinar. Ver [`docs/ESTUDO_VIABILIDADE.md`](docs/ESTUDO_VIABILIDADE.md).

## Requisitos

Python 3.10 ou superior. **Sem dependências externas.**

## Como usar

```bash
# 1. Avaliar uma viatura na linha de comandos
python3 -m avaliador avaliar --marca Renault --modelo Clio --ano 2019 --km 85000 \
    --combustivel Gasolina --caixa Manual --estado 3

# ... ou obter o resultado em JSON (para integrar noutro sistema)
python3 -m avaliador avaliar --marca Renault --modelo Clio --ano 2019 --km 85000 \
    --combustivel Gasolina --json

# 2. Ver que marcas/modelos existem na fonte de anúncios
python3 -m avaliador modelos

# 3. Interface web local (formulário + resultado com comparáveis)
python3 -m avaliador servir --porta 8000      # abrir http://localhost:8000

# 4. Correr os testes
python3 -m unittest -v
```

Exemplo de saída:

```
Viatura: Renault Clio 2019, Gasolina, Manual, 85 000 km, estado 3/5
Comparáveis usados: 8   Confiança: ALTA

Valor de mercado estimado:       8 300 €   (intervalo 7 950 € – 8 650 €)
  Mediana ponderada dos comparáveis ajustados: 8 286 €
  Ajuste por estado (3/5): +0 %

Proposta de compra:              6 550 €
  Margem (12 %):                    -994 €
  Custos fixos:                     -350 €
  Recondicionamento (estado 3):     -400 €

Comparáveis (ordenados por semelhança):
  ID     Fonte        Ano         Km Caixa          Anúncio    Aj. km   Aj. ano   Ajustado  Peso
  A0023  standvirtual 2018    85 500 Manual           7 300        +5      +416      7 356  0.49
  ...
```

Códigos de saída do comando `avaliar`: `0` avaliação feita, `2` comparáveis insuficientes, `1` erro.

## Usar os seus próprios anúncios

Crie um CSV com estas colunas (a ordem não importa; `data_recolha` e `url` são opcionais):

| coluna | exemplo | notas |
|---|---|---|
| `id` | `SV123456` | identificador único |
| `fonte` | `standvirtual` | de onde veio o anúncio |
| `marca` | `Renault` | |
| `modelo` | `Clio` | |
| `versao` | `1.0 TCe 90 Intens` | informativo |
| `ano` | `2019` | ano de matrícula |
| `combustivel` | `Gasolina` | `Gasolina`, `Diesel`, `Híbrido`, `Elétrico` |
| `caixa` | `Manual` | `Manual` ou `Automática` |
| `quilometros` | `85000` | |
| `potencia_cv` | `90` | informativo |
| `preco` | `9500` | preço pedido no anúncio, em € |
| `data_recolha` | `2026-09-07` | opcional |
| `url` | `https://…` | opcional |

Depois aponte o avaliador para ele:

```bash
python3 -m avaliador --anuncios /caminho/anuncios.csv avaliar --marca ... --modelo ...
python3 -m avaliador --anuncios /caminho/anuncios.csv servir
```

O ficheiro `dados/anuncios_exemplo.csv` (398 anúncios sintéticos) foi gerado por
`python3 dados/gerar_exemplo.py` e serve apenas para demonstração.

## Afinar os parâmetros de negócio

Tudo está em [`dados/config.json`](dados/config.json) (qualquer chave omitida usa o valor
padrão de `avaliador/config.py`):

| secção | parâmetro | significado |
|---|---|---|
| `criterios` | `tolerancia_anos`, `tolerancia_km` | quão parecido tem de ser um anúncio para contar como comparável |
| | `minimo_comparaveis` | abaixo disto não é dado valor automático |
| `ajustes` | `pct_por_10000_km` | % do preço por cada 10 000 km de diferença |
| | `pct_por_ano` | % do preço por cada ano de diferença |
| | `desconto_negociacao_pct` | diferença típica entre preço pedido e preço real de venda |
| `estado` | `"1"` … `"5"` | ajuste (%) ao valor de mercado consoante o estado da viatura |
| `proposta` | `margem_pct` | margem bruta pretendida |
| | `custos_fixos_eur` | transporte, legalização, preparação |
| | `recondicionamento_por_estado_eur` | custo esperado de reparações por nível de estado |
| `confianca` | `cv_*`, `n_*` | limiares para classificar a confiança (nº de comparáveis e dispersão) |
| `arredondamento_eur` | | arredondamento dos valores apresentados |

## Como funciona (resumo)

1. **Selecionar comparáveis** — mesma marca, modelo e combustível; ano dentro de ±2 anos;
   km dentro de ±60 000. Se houver poucos, os critérios são alargados e o resultado avisa.
2. **Ajustar cada anúncio** — aplica-se o desconto de negociação, e o preço é corrigido
   "como se" o anúncio tivesse o ano e os km da viatura em avaliação.
3. **Remover atípicos** — regra do intervalo interquartil (IQR) descarta preços absurdos.
4. **Valor de mercado** — mediana ponderada (anúncios mais parecidos pesam mais) × fator de estado.
5. **Proposta** — valor de mercado − margem − custos fixos − recondicionamento.
6. **Confiança** — alta / média / baixa consoante nº de comparáveis e dispersão dos preços.

## Estrutura

```
avaliador/
  modelos.py      estruturas de dados (Anuncio, Viatura, Comparavel, ResultadoAvaliacao)
  fontes.py       leitura de anúncios (CSV); interface para outras fontes no futuro
  comparaveis.py  seleção, ajuste, outliers, mediana ponderada
  avaliacao.py    motor: avaliar(viatura, anuncios, cfg) → ResultadoAvaliacao
  config.py       parâmetros padrão + leitura de dados/config.json
  cli.py          linha de comandos
  servidor.py     interface web mínima (biblioteca padrão)
dados/
  anuncios_exemplo.csv   398 anúncios sintéticos
  gerar_exemplo.py       gerador dos anúncios sintéticos
  config.json            parâmetros de negócio
docs/
  ESTUDO_VIABILIDADE.md  abordagens, fontes de dados, riscos, faseamento
tests/
  test_avaliacao.py      23 testes unitários
```

## Aviso sobre fontes de dados

O Standvirtual, OLX e AutoScout24 **proíbem a recolha automática (scraping)** nos seus
termos de serviço. Este protótipo não faz scraping: lê anúncios de um ficheiro que o
utilizador fornece. As alternativas (exportação manual, APIs/parcerias, fornecedores de
dados de mercado) estão discutidas no estudo de viabilidade.
