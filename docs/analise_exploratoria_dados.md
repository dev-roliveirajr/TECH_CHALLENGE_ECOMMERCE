# Análise Exploratória de Dados (AED)

## 📋 1. Contexto

Este documento apresenta a análise exploratória dos dados da base de dados "desafio_nps_fase_1". A base reúne informações sobre pedidos, logística, atendimento e percepção de satisfação do cliente, com foco em responder uma pergunta de negócio simples e central: quais sinais operacionais estão associados à piora da experiência e à detração?

A análise foi conduzida com uma lógica de EDA clássica, em que primeiro verificamos a qualidade da base, depois avaliamos distribuições, tendências centrais e relações entre variáveis, e, por fim, identificamos indícios de ruptura operacional que possam orientar ações preventivas. O objetivo não é provar causalidade absoluta, mas apontar fatores que merecem atenção no processo decisório e orientar a etapa posterior de modelagem.

## 🧾 2. Visão geral da base

A amostra contém **2.500 registros** e **19 colunas** na base bruta disponível em `data/raw/desafio_nps_fase_1.csv`. Os dados cobrem tanto aspectos do pedido quanto indicadores operacionais e de relacionamento. A variável principal de interesse é `nps_score`, que representa a nota de satisfação do cliente em uma escala de 0 a 10.

### 2.1. Estrutura da base

| Aspecto | Valor |
| :--- | :---: |
| Número de registros | 2.500 |
| Número de colunas | 19 |
| Valores ausentes | 0 |
| Registros duplicados | 0 |

### 2.2. Principais variáveis da base

- `delivery_delay_days`: mede o atraso logístico em dias. É uma variável central na base porque representa diretamente a performance da entrega e o nível de fricção percebido pelo cliente.
- `complaints_count`: indica a quantidade de reclamações registradas. Valores mais altos sugerem maior volume de problemas e maior complexidade na experiência do cliente.
- `customer_service_contacts`: representa o número de contatos com o atendimento. Esse indicador capta a necessidade de suporte e o atrito enfrentado pelo cliente durante a resolução de problemas.
- `resolution_time_days`: mede o tempo necessário para resolver a demanda do cliente. Esse indicador é relevante para descrever a extensão do problema e a persistência da fricção operacional.
- `order_value`: expressa o valor monetário do pedido e caracteriza a estrutura da transação. Embora seja relevante para o perfil do pedido, ela funciona mais como contexto do negócio do que como indicador direto de experiência.
- `freight_value`: representa o custo do frete e também é uma característica da transação, com menor destaque quando comparada às variáveis operacionais de entrega e atendimento.
- `customer_age`: descreve a faixa etária dos clientes e ajuda a caracterizar o perfil do consumidor na amostra.
- `customer_tenure_months`: indica o tempo de relacionamento do cliente com a empresa e pode sinalizar diferentes graus de familiaridade com a operação.

### 2.3. Magnitude das variáveis centrais

| Variável | Média | Mediana | Máximo |
| :--- | :---: | :---: | :---: |
| `delivery_delay_days` | 2,19 | 2,00 | 8 |
| `complaints_count` | 4,15 | 4,00 | 11 |
| `customer_service_contacts` | 1,52 | 1,00 | 7 |
| `resolution_time_days` | 5,49 | 6,00 | 11 |
| `order_value` | 434,26 | 375,52 | 1.983,81 |
| `freight_value` | 38,22 | 38,50 | 76,13 |
| `customer_age` | 43,40 | 43,00 | 69 |
| `customer_tenure_months` | 61,32 | 62,00 | 119 |

### 2.4. Outliers e tratamento aplicado

Durante a análise exploratória, três variáveis operacionais apresentaram comportamento de outlier mais evidente e mereceram atenção especial: `customer_service_contacts`, `delivery_delay_days` e `complaints_count`.

- `customer_service_contacts`:
  - Q1 = 1.00
  - Q3 = 2.00
  - IQR = 1.00
  - Limites: [-0.50, 3.50]
  - Outliers: 176

- `delivery_delay_days`:
  - Q1 = 1.00
  - Q3 = 3.00
  - IQR = 2.00
  - Limites: [-2.00, 6.00]
  - Outliers: 17

- `complaints_count`:
  - Q1 = 3.00
  - Q3 = 5.00
  - IQR = 2.00
  - Limites: [0.00, 8.00]
  - Outliers: 29

Esses valores sugerem que o problema não é um ruído geral, mas a presença de casos operacionais muito extremos. Em e-commerce, isso pode representar episódios de logística crítica, contato excessivo com suporte ou recorrência de reclamações, que são eventos relevantes para a experiência do cliente.

Para preservar a informação sem deixar que casos extremos dominem a análise, aplicamos uma estratégia de winsorização por regra IQR:

- limite inferior = Q1 - 1.5 × IQR
- limite superior = Q3 + 1.5 × IQR
- valores fora desse intervalo são ajustados para os limites calculados, em vez de serem removidos.

Essa abordagem foi escolhida porque:

1. mantém o conjunto de dados completo;
2. reduz a influência de observações extremas sem perder a amostra total;
3. preserva o sinal de risco operacional que pode ser relevante para a detração.

#### Dataset processado após winsorização

Com base nos limites IQR calculados, os valores extremos das três variáveis foram ajustados[^1] para o limite correspondente, preservando o conjunto de dados e reduzindo a influência dos casos mais críticos sobre as métricas e os modelos.

- `customer_service_contacts`:
  - Limite aplicado: [-0.50, 3.50]
  - Máximo observado após tratamento: 3.50
  - Mínimo observado após tratamento: 0.00
  - Outliers fora do limite original: 0

- `delivery_delay_days`:
  - Limite aplicado: [-2.00, 6.00]
  - Máximo observado após tratamento: 6.00
  - Mínimo observado após tratamento: 0.00
  - Outliers fora do limite original: 0

- `complaints_count`:
  - Limite aplicado: [0.00, 8.00]
  - Máximo observado após tratamento: 8.00
  - Mínimo observado após tratamento: 0.00
  - Outliers fora do limite original: 0

Essa abordagem mantém a informação operacional relevante, reduzindo a influência de observações atípicas sem excluir o caso do conjunto.

### 2.5. Composição do NPS (nps_score)

A classificação clássica do NPS foi observada da seguinte forma:

| Aspecto | Valor |
| :--- | :---: |
| Faixa de NPS | 0 a 10 |
| Nota média | 4,379 |
| Mediana da nota | 4,400 |
| NPS observado | -69,64% |

- **Detratores (0 a 6):** 74,04%
- **Neutros (7 a 8):** 21,56%
- **Promotores (9 a 10):** 4,40%

### 2.6. Variável alvo: `is_detractor`

A partir da nota de NPS, foi derivada a variável alvo binária `is_detractor`, definida como:

- `1` quando `nps_score <= 6` (cliente detrator),
- `0` quando `nps_score > 6` (cliente não detrator).

Essa regra segue a classificação tradicional do NPS, em que notas de 0 a 6 são consideradas detratoras. A variável alvo permite comparar o comportamento operacional de clientes detratores e não detratores, além de orientar a etapa posterior de modelagem preditiva.

---

## 👥 3. Perfis Extremos de Clientes
A análise descritiva e os cruzamentos de dados revelam duas personas bem marcadas no e-commerce:

### 🔴 Persona Detratora Crítica (O Cliente Ferido)
*   **Características Operacionais:** Experimentou um atraso logístico de $\\ge 3$ dias, tentou contato com o suporte $\\ge 3$ vezes para resolver o problema e registrou $\\ge 4$ reclamações na base de dados.
*   **Impacto Financeiro:** Taxa de recompra em 30 dias de **0%**. Este cliente abandona a nossa marca, espalha um boca a boca negativo pesado e migra para a concorrência.

### 🟢 Persona Promotora (O Cliente Encantado)
*   **Características Operacionais:** Recebeu seu pedido estritamente dentro do prazo prometido (0 dia de atraso), não teve necessidade de ligar ou mandar mensagem para o atendimento (0 contatos) e possui 0 reclamações.
*   **Impacto Financeiro:** Forte propensão à recompra recorrente dentro de 30 dias, reduzindo drasticamente o nosso Custo de Aquisição de Clientes (CAC) por meio da indicação orgânica (boca a boca positivo).

---

## 📉 4. Ponto de ruptura operacional

Um dos achados mais relevantes da análise exploratória é o comportamento não linear do atraso logístico. A tendência observada sugere que a experiência do cliente permanece relativamente estável até certo limiar, mas entra em colapso quando o atraso se torna mais relevante.

Os pontos mais importantes observados nesta amostra foram:

- **sem atraso:** taxa de detração de 36,46%
- **1 a 2 dias de atraso:** taxa de detração de 59,67% a 75,39%
- **3 dias ou mais:** taxa de detração de 89,71% a 99,14%
- **6 dias ou mais:** detração próxima a 100%

Esse comportamento indica que a decisão operacional não deve ser guiada apenas pela média geral. Há um ponto de ruptura claro, em que a experiência do cliente muda de forma abrupta e a detração se acelera. Esse achado é importante porque coloca em evidência a necessidade de ações preventivas antes que o atraso ultrapasse um limite crítico.

---

## 🔗 5. Relações entre variáveis e possíveis sinais de leakage

Ao analisar a base, observamos que as variáveis relacionadas à jornada pós-compra podem carregar informação muito próxima do resultado final, especialmente quando há coleta de satisfação e recompra em momentos posteriores.

### 5.1. Associações observadas

Quando olhamos para as correlações, a associação mais forte aparece entre a variável alvo e indicadores de experiência, como:

- `delivery_delay_days`
- `complaints_count`
- `customer_service_contacts`
- `resolution_time_days`

### 5.2. Risco de leakage

A variável alvo e variáveis de resultado que surgem após o evento de compra devem ser tratadas com cuidado na modelagem preditiva:

- `nps_score`: é a própria métrica de satisfação, portanto não pode ser usada como feature preditiva em uma modelagem de risco operacional.
- `repeat_purchase_30d`: informa resultado posterior à compra e pode refletir comportamento já influenciado pela experiência anterior.
- `csat_internal_score`: pode ser uma medida interna de satisfação coletada em paralelo à experiência e, quando usada como entrada, tende a produzir um modelo otimista demais em validação, mas pouco útil em produção.

A análise exploratória pode usar essas variáveis para caracterizar o problema e compreender a dinâmica da experiência; no entanto, o pipeline de modelagem deve mantê-las fora do conjunto de dados de entrada para preservar a validade preditiva do modelo e evitar utilização de informação que só existe depois da ocorrência do evento de interesse.

---

## 🔬 6. Validação Estatística
Para subsidiar a construção do modelo preditivo, foram conduzidos testes estatísticos na base de 2.500 transações. A intenção desta etapa foi confirmar se os padrões observados na EDA eram estatisticamente consistentes e não fruto de ruído aleatório.

### A. Teste de Normalidade de Shapiro-Wilk (Nota de Satisfação)
*   **Hipótese Nula ($H_0$):** As notas de satisfação (`nps_score`) seguem uma distribuição normal padrão.
*   **Hipótese Alternativa ($H_1$):** As notas de satisfação NÃO seguem uma distribuição normal.
*   **Resultado do Teste:** Estatística de teste $= 0,9817$, **p-valor $= 2,1430 \times 10^{-17}$**.
*   **Conclusão Estatística:** Como o p-valor é menor que o nível de significância de $5\%$ ($\\alpha = 0,05$), rejeitamos a hipótese nula. As notas apresentam evidência de não normalidade, o que motivou o uso de testes não paramétricos nesta análise.

### B. Coeficiente de Correlação de Spearman (Fatores de Fricção)
Assumindo a não normalidade das notas, calculamos a correlação por postos de **Spearman** (que mede relações monotônicas, lineares ou curvilíneas) com a target `is_detractor`:

| Variável Operacional | Correlação de Spearman ($r_s$) | Significado Prático |
| :--- | :---: | :--- |
| **`nps_score`** | $-0,7595$ | Correlação negativa forte, pois a target é derivada dessa variável. |
| **`repeat_purchase_30d`** | $-0,5220$ | Associação negativa com a recompra observada. |
| **`complaints_count`** | $+0,4527$ | Associação positiva com a detração. |
| **`delivery_delay_days`** | $+0,4202$ | Associação positiva entre atraso e detração. |
| **`csat_internal_score`** | $-0,4107$ | Associação negativa com a detração. |
| **`customer_service_contacts`** | $+0,2418$ | Associação positiva moderada com o atrito. |
| **`resolution_time_days`** | $+0,1509$ | Associação positiva fraca com o atrito. |
| **`customer_region_code`** | $+0,0088$ | Associação praticamente nula com a detração. |
| **`order_value_q`** | $-0,0282$ | Associação positiva fraca com o atrito. |
| **`freight_value_q`** | $+0,0277$ | Associação positiva fraca com o atrito. |
| **`payment_installments`** | $-0,0193$ | Associação praticamente nula com o atrito. |

### C. Teste de Diferença de Médias de Mann-Whitney U (Atraso Logístico)
Comparamos se os dias de atraso logístico (`delivery_delay_days`) dos detratores diferem significativamente dos não detratores:
*   **Hipótese Nula ($H_0$):** A distribuição de dias de atraso é idêntica entre detratores e não detratores.
*   **Hipótese Alternativa ($H_1$):** A distribuição de dias de atraso é diferente entre os dois grupos.
*   **Resultado do Teste:** Estatística $U = 925.586,5$, **p-valor $= 6,0051 \times 10^{-98}$**.
*   **Médias Observadas:** Detratores $= 2,534$ dias de atraso versus não detratores $= 1,197$ dias.
*   **Conclusão Estatística:** Rejeitamos a hipótese nula com $p < 0,05$. Nesta amostra, o atraso médio foi maior entre detratores.

*O teste de Mann-Whitney U aplicado ao tempo total de entrega (`delivery_time_days`) resultou em p-valor $= 0,556$. Nesta amostra, não foi identificada diferença estatisticamente significativa entre os grupos.*

### D. Teste Qui-Quadrado de Independência (Isenção Geográfica)
Avaliamos se a proporção de detratores difere por região geográfica (`customer_region`):
*   **Hipótese Nula ($H_0$):** A região geográfica e o risco de detração são independentes.
*   **Hipótese Alternativa ($H_1$):** Há associação entre a região e a detração.
*   **Resultado do Teste:** Estatística $\\chi^2 = 0,6264$, **p-valor $= 0,9601$**, com $4$ graus de liberdade.
*   **Conclusão Estatística:** Como o p-valor é superior a $5\%$, não rejeitamos a hipótese nula. Nesta amostra, não foi identificada associação estatisticamente significativa entre região e detração.

### E. Teste Qui-Quadrado de Independência (Estrutura do Pedido)
Avaliamos se a proporção de detratores difere ao longo de faixas de valor do pedido, valor do frete e número de parcelas:

#### E1. Valor do pedido (`order_value`)
*   **Hipótese Nula ($H_0$):** O valor do pedido e o risco de detração são independentes.
*   **Hipótese Alternativa ($H_1$):** Há associação entre valor do pedido e detração.
*   **Resultado do Teste:** Estatística $\\chi^2 = 3,1695$, **p-valor $= 0,3662$**, com $3$ graus de liberdade.
*   **Conclusão Estatística:** Como o p-valor é maior que $5\%$, não rejeitamos a hipótese nula. Nesta amostra, o valor do pedido não apresentou associação estatisticamente significativa com a detração.

#### E2. Valor do frete (`freight_value`)
*   **Hipótese Nula ($H_0$):** O valor do frete e o risco de detração são independentes.
*   **Hipótese Alternativa ($H_1$):** Há associação entre valor do frete e detração.
*   **Resultado do Teste:** Estatística $\\chi^2 = 3,0885$, **p-valor $= 0,3782$**, com $3$ graus de liberdade.
*   **Conclusão Estatística:** Como o p-valor é maior que $5\%$, não rejeitamos a hipótese nula. Nesta amostra, o valor do frete também não apresentou associação estatisticamente significativa com a detração.

#### E3. Número de parcelas (`payment_installments`)
*   **Hipótese Nula ($H_0$):** O número de parcelas e o risco de detração são independentes.
*   **Hipótese Alternativa ($H_1$):** Há associação entre número de parcelas e detração.
*   **Resultado do Teste:** Estatística $\\chi^2 = 5,2401$, **p-valor $= 0,8746$**, com $10$ graus de liberdade.
*   **Conclusão Estatística:** Como o p-valor é maior que $5\%$, não rejeitamos a hipótese nula. Nesta amostra, a estrutura do parcelamento do pedido também não apresentou associação estatisticamente significativa com a detração.

**Interpretação prática:** os componentes da estrutura do pedido, quando avaliados de forma isolada, não parecem explicar a variação do NPS de forma significativa nesta base. Em outras palavras, o principal motor de detração observado parece estar mais associado a fatores operacionais de entrega e atendimento do que ao valor do pedido, ao frete ou ao parcelamento.

---

## ⚠️ 7. Limitações e riscos

A análise exploratória oferece evidência útil sobre associação e risco, mas há limites importantes que precisam ser reconhecidos:

- a base é observacional e, portanto, não permite conclusões causais definitivas;
- algumas variáveis funcionam como proxy de experiência, e não como explicação causal direta;
- o NPS é uma métrica coletada após a jornada, o que limita a capacidade de usar a variável como entrada em decisões em tempo real sem cuidado;
- dados de atendimento e reclamações podem refletir a mesma experiência emocional do cliente, e não eventos totalmente independentes;
- o estudo descreve a amostra analisada e não necessariamente a população total em todos os contextos operacionais.

Esses limites não invalidam os achados; apenas reforçam a necessidade de uma leitura responsável e orientada a decisão, com validação contínua em dados novos.

---

## 🖼️ 8. Visualizações Científicas Geradas
Os gráficos profissionais que comprovam visualmente estes insights foram gerados de forma automatizada pelo script `plots.py` e salvos na pasta `reports/figures/` do repositório:
1.  `nps_distribution.png`: Mostra o histograma assimétrico das notas de NPS em contraponto com a média aritmética, além do gráfico de probabilidade normal (Q-Q Plot) que ilustra a não normalidade.
2.  `detraction_rate_by_delay.png`: Ilustra a curva exponencial do colapso da experiência, evidenciando as taxas de detração escalando a cada dia de atraso.
3.  `delivery_delay_boxplot.png`: Apresenta diagramas de caixa que comprovam a diferença drástica de atraso sofrido por detratores vs. não detratores.
4.  `detraction_by_order_structure.png`: Compara a taxa de detração em relação à estrutura do pedido, incluindo valor do pedido, valor do frete e número de parcelas, reforçando que a composição da compra não parece ser o principal fator de insatisfação.
5.  `spearman_correlation_matrix.png`: Um mapa de calor das correlações de Spearman de todas as variáveis operacionais com a detração.
6.  `detraction_by_region.png`: Gráfico de barras empilhadas que ilustra visualmente a independência da taxa de detração entre as diferentes regiões do país.

[^1]: É importante deixar claro que esse bloco refere-se ao artefato gerado pelo pipeline em `src/dataset.py`, e não à base bruta de exploração original. A base raw mantém a estrutura inicial do CSV, enquanto a versão processada é produzida ao executar o pipeline, que aplica a winsorização nas colunas selecionadas antes de salvar o arquivo final em `data/processed/processed_nps_data.csv`.
