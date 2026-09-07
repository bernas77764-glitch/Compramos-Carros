# Estudo de viabilidade — automatização da avaliação de viaturas

**Contexto.** Negócio de compra de viaturas usadas a particulares. Hoje, o valor é atribuído
por um avaliador que consulta anúncios online (Standvirtual, OLX, AutoScout24) e aplica uma
margem. Pretende-se perceber se este processo pode ser automatizado, com que fiabilidade, com
que dados e em que fases.

**Conclusão em duas linhas.** É viável automatizar a *primeira estimativa* com um motor de
comparáveis de mercado (é o que este protótipo faz). Não é realista, nem desejável, retirar o
avaliador humano da decisão final nesta fase: o maior risco não está no cálculo mas na
qualidade e na legalidade da recolha de dados, e no estado real da viatura, que nenhum anúncio
captura. A automatização deve começar como **ferramenta de apoio** e evoluir para decisão
autónoma à medida que se acumula histórico próprio para a calibrar.

---

## 1. Como funciona o processo hoje vs. automatizado

| | Hoje (manual) | Automatizado (protótipo) |
|---|---|---|
| Recolha de comparáveis | avaliador pesquisa no site, filtra à vista | filtro sistemático por marca/modelo/combustível/ano/km |
| Ajuste ao carro concreto | "de cabeça" (mais km, mais antigo…) | ajustes explícitos e parametrizáveis por km e ano |
| Preço pedido → preço real | intuição | desconto de negociação configurável |
| Preços absurdos | ignorados à vista | removidos por regra estatística (IQR) |
| Margem e custos | variam de avaliador para avaliador | uniformes e auditáveis |
| Rastreabilidade | nenhuma | cada proposta guarda os comparáveis e ajustes usados |
| Tempo por avaliação | 10–20 min | segundos (+ validação humana) |

O ganho imediato não é substituir o avaliador, é **uniformizar** (duas pessoas chegam ao mesmo
número), **acelerar** e **registar** (para poder medir e melhorar depois).

## 2. Abordagens possíveis

### A. Comparáveis de mercado (implementada no protótipo)
Estima o valor a partir de anúncios semelhantes, ajustados ao carro em avaliação. É o método
que o negócio já usa informalmente, apenas sistematizado.

- **Prós:** não precisa de histórico próprio; transparente (mostra os anúncios usados);
  reflete o mercado atual; fácil de explicar a um cliente.
- **Contras:** depende de haver anúncios suficientes (modelos raros ficam sem valor);
  preços de anúncio ≠ preços de transação; não vê o estado real do carro.
- **Quando falha:** modelos pouco comuns, versões especiais (RS, AMG, M), carros muito
  antigos ou muito recentes, importados, elétricos com bateria degradada.

### B. Modelo estatístico com histórico próprio
Treinar um modelo (regressão ou gradient boosting) com as avaliações e revendas passadas do
próprio negócio: o que se pagou, por quanto se vendeu, em quanto tempo.

- **Prós:** aprende a *margem real* e o *tempo de rotação* por segmento; captura padrões que
  o avaliador não formaliza.
- **Contras:** precisa de algumas centenas de registos com resultado conhecido; hoje não
  existem (as avaliações vivem em conversas e não num ficheiro).
- **Caminho:** o protótipo já devolve JSON; basta guardar cada avaliação + decisão final +
  valor de revenda para começar a construir o dataset. Ver fase 1.

### C. Fornecedores comerciais de valores residuais
Eurotax/Autovista, Indicata (Autorola), JATO, ou os guias de valores usados por seguradoras e
financeiras. Vendem valores de referência por versão/ano/km via API ou subscrição.

- **Prós:** cobertura total de modelos; legalmente limpo; usados pelo setor.
- **Contras:** custo de subscrição (tipicamente centenas de €/mês, a negociar); valores
  "de tabela" que podem divergir do mercado local; menos transparente para o cliente.
- **Encaixe:** pode ser uma *segunda opinião* automática ao lado dos comparáveis, ou o
  fallback quando não há comparáveis suficientes.

**Recomendação:** A agora (feito), B a partir do momento em que houver registo, C a avaliar
por custo se o volume justificar ou se os modelos sem comparáveis forem frequentes.

## 3. Fontes de dados de mercado — o ponto crítico

O protótipo lê anúncios de um CSV. A questão é **como alimentar esse CSV** de forma regular.

| Opção | Legalidade | Esforço | Fiabilidade | Comentário |
|---|---|---|---|---|
| Exportação manual (copiar anúncios para o CSV) | ✅ | alto e contínuo | boa | viável para começar; 20–30 min/dia para os modelos mais frequentes |
| Scraping do Standvirtual/OLX/AutoScout24 | ❌ proibido pelos termos de serviço; proteção anti-bot ativa | médio | frágil (quebra a cada alteração do site; risco de bloqueio de IP/conta) | **não recomendado** como base do negócio |
| API oficial / parceria com o portal | ✅ | baixo depois de acordado | muito boa | Standvirtual (OLX Group) e AutoScout24 têm programas para profissionais; vale a pena perguntar |
| Fornecedor de dados de anúncios (agregadores B2B) | ✅ | baixo | boa | existem no mercado europeu; custo a pedir |
| Fornecedor de valores residuais (opção C acima) | ✅ | baixo | boa | não são anúncios, são valores de tabela |
| Histórico próprio de compras e revendas | ✅ | zero (só registar) | a melhor a prazo | é o único dado que ninguém mais tem |

Nota sobre RGPD: anúncios de viaturas raramente contêm dados pessoais para além do nome/telefone
do vendedor, que **não** devem ser guardados. O CSV do protótipo não tem essas colunas de
propósito.

## 4. Riscos e limitações

1. **Preço de anúncio não é preço de venda.** O desconto de negociação (5 % por defeito) é
   uma estimativa; deve ser calibrado comparando anúncios com o que realmente se pagou.
2. **O estado do carro não está nos anúncios.** O ajuste por estado (1–5) depende do
   avaliador. Um formulário público em que o cliente escolhe "impecável" está sujeito a
   otimismo; num site, mostrar sempre um *intervalo* e nunca um número fechado.
3. **Poucos comparáveis.** O motor recusa dar valor abaixo de 3 comparáveis e avisa quando
   alarga critérios. Isto é uma funcionalidade, não uma falha: é melhor "não sei" do que um
   número inventado.
4. **Sazonalidade e mercado.** Descapotáveis no verão, 4×4 no inverno, choques de mercado
   (ex.: diesel). Os anúncios refletem isto automaticamente; parâmetros fixos não.
5. **Parâmetros por defeito são palpites informados.** 1,5 %/10 000 km, 6 %/ano, 12 % de
   margem: têm de ser validados com dados reais. O ficheiro `config.json` existe para isso.
6. **Dependência de terceiros.** Qualquer fonte externa pode mudar preço, formato ou
   condições. O código isola a fonte numa interface para que a troca seja localizada.

## 5. Faseamento proposto

### Fase 0 — Protótipo (feito)
Motor de comparáveis, CLI, interface web local, testes, dados sintéticos.
**Critério de saída:** a equipa consegue correr e perceber o resultado.

### Fase 1 — Piloto interno com dados reais (2–4 semanas)
- Alimentar o CSV com anúncios reais dos 10–15 modelos mais frequentes (exportação manual
  ou parceria, ver §3).
- Correr o avaliador **em paralelo** com o avaliador humano em todas as avaliações.
- **Registar** cada caso: dados do carro, valor automático, valor humano, proposta feita,
  aceite ou não, e mais tarde o valor de revenda.
- **Critério de saída:** ≥ 100 casos registados; erro médio absoluto entre valor automático e
  valor humano conhecido por segmento.

### Fase 2 — Calibração (1–2 semanas, depois da fase 1)
- Afinar `config.json` com os dados da fase 1: desconto de negociação, %/km, %/ano, margem
  por segmento, custos reais de recondicionamento por nível de estado.
- Decidir limiares de confiança: acima de que confiança a proposta automática pode sair sem
  revisão humana.
- **Critério de saída:** erro médio abaixo de um limiar acordado (ex.: 5 % do valor) nos
  segmentos principais.

### Fase 3 — Automatização com supervisão
- Propostas de confiança "alta" saem automaticamente; "média" e "baixa" vão para revisão.
- Opcional: formulário no site com intervalo de valor (não número fechado) e contacto.
- Opcional: modelo estatístico (abordagem B) treinado no histórico acumulado.
- Opcional: fonte comercial (abordagem C) como fallback para modelos sem comparáveis.

## 6. Métricas para decidir se está a funcionar

| Métrica | Como medir | Objetivo indicativo |
|---|---|---|
| Erro face ao avaliador humano | \|valor automático − valor humano\| / valor humano | < 5–8 % nos modelos correntes |
| Cobertura | % de pedidos com comparáveis suficientes | > 80 % do volume |
| Taxa de aceitação da proposta | propostas aceites / propostas feitas | igual ou melhor que a manual |
| Margem realizada | (revenda − compra − custos) / compra | ≥ margem parametrizada |
| Tempo por avaliação | cronometrar | < 5 min incluindo revisão |

## 7. Esforço e custos estimados

| Item | Estimativa |
|---|---|
| Fase 1 — recolha manual de anúncios | 20–30 min/dia de uma pessoa |
| Fase 1 — registo das avaliações | 2–3 min por caso (formulário ou folha de cálculo) |
| Fase 2 — calibração | 1–2 dias de trabalho técnico |
| Fase 3 — integração no site / CRM | 1–2 semanas de desenvolvimento, dependendo do site |
| Fonte de dados comercial (se necessária) | a pedir orçamento; ordem de grandeza: centenas de €/mês |
| Infraestrutura | nula até à fase 3 (corre num portátil); depois um servidor pequeno |

## 8. Decisões pendentes (para o dono do negócio)

1. Que fonte de anúncios usar na fase 1: exportação manual ou contactar o Standvirtual /
   AutoScout24 sobre acesso profissional?
2. Quem regista as avaliações e onde (folha de cálculo partilhada chega para começar)?
3. Quais os 10–15 modelos que representam a maior parte do volume?
4. Margem, custos fixos e custos de recondicionamento reais para substituir os valores
   padrão em `config.json`.
