# Benchmarking e Performance de Modelos: Relatório Técnico de Engenharia e Auditoria Preditiva

Este relatório técnico detalha o pipeline de engenharia de dados, preparação de variáveis (*features*), classificação binária e avaliação do projeto **NPS Preditivo**. O objetivo do modelo é estimar a probabilidade de uma transação ser associada a um cliente detrator (`is_detractor`) e apoiar a priorização operacional.

---

## 🛠️ 1. Engenharia de Dados, Higienização e Blindagem de Vazamento (Data Leakage)

### 1.1. Ingestão e Testes Rigorosos de Consistência
A base de dados bruta `desafio_nps_fase_1.csv` foi carregada por meio de rotinas modulares implementadas em `src/dataset.py`. O pipeline executa testes rígidos de integridade estatística antes de disponibilizar os dados para treinamento:
* **Unicidade de Identificadores:** Confirmação de que `customer_id` e `order_id` são chaves primárias perfeitas e representam transações individuais e únicas (2.500 registros únicos).
* **Limites Teóricos das Notas:** Verificação de que o campo `nps_score` encontra-se no intervalo fechado de **0.0 a 10.0**. A coluna contém notas decimais, que são mantidas sem arredondamento.
* **Consistência de Sinais Numéricos:** Varredura automática em 14 variáveis operacionais críticas para assegurar a ausência de valores negativos incoerentes (como idade, tempo de relacionamento, atrasos logísticos ou contatos com suporte).

### 1.2. Binarização Qualificada da Target
De acordo com os fundamentos metodológicos consagrados do Net Promoter Score tradicional, criamos a nossa variável de destino binária (`is_detractor`) seguindo a regra matemática rigorosa:
$$is\_detractor = \begin{cases} 1, & \text{se } nps\_score < 7 \text{ (Cliente Detrator)} \\ 0, & \text{se } nps\_score \ge 7 \text{ (Cliente Não Detrator)} \end{cases}$$
Como a nota é decimal, a regra inclui qualquer valor abaixo de 7 (por exemplo, 6,9). Aplicada à base de 2.500 pedidos, resulta em **84,36% de detratores** (2.109) e 391 não detratores. Os resultados de avaliação anteriores à correção do limiar não são comparáveis; o pipeline e todos os artefatos de modelagem devem ser regenerados com a nova target.

### 1.3. Prevenção Absoluta contra Vazamento de Dados (Data Leakage)
O vazamento de dados ocorre quando variáveis coletadas após a ocorrência da target ou que contêm a resposta direta do problema são incluídas no treinamento, produzindo métricas otimistas e risco de perda de desempenho em dados novos.
Para controlar esse risco, estruturamos o arquivo de configurações centralizadas `src/config.py` e definimos a lista `EXCLUDED_FROM_MODEL` contendo as variáveis bloqueadas:
* `customer_id` e `order_id`: Identificadores únicos sem poder de generalização preditiva.
* `nps_score`: Nota de satisfação da qual a própria target foi derivada.
* `repeat_purchase_30d`: Sinal de recompra coletado 30 dias após o fechamento da jornada.
* `csat_internal_score`: Score interno de satisfação cujo momento de coleta não está definido.

---

## 🧬 2. Pipeline de Pré-processamento Modular (ColumnTransformer)

O módulo de engenharia de features (`src/features.py`) utiliza os pipelines unificados do Scikit-Learn:

Antes do pré-processamento, o pipeline aplica winsorização IQR às variáveis `customer_service_contacts`, `delivery_delay_days` e `complaints_count`. O transformador aprende os limites exclusivamente no subconjunto usado por `fit`: portanto, cada fold da validação cruzada calcula seus próprios limites com os dados de treino daquele fold, e o holdout usa limites aprendidos no treino de 80%. O mesmo transformador serializado aplica esses limites durante inferência. Os relatórios descritivos podem continuar usando o dataset winsorizado em `src/dataset.py`; esse artefato não é a entrada do treinamento do modelo.

```python
preprocessor = ColumnTransformer(
    transformers=[
        ("num", num_transformer, num_features),
        ("cat", cat_transformer, cat_features)
    ],
    remainder="drop"
)
```

1. **Pipeline de Recursos Numéricos:** Aplicado a 13 variáveis contínuas e discretas (como idade, valor do pedido, atrasos logísticos, contatos e tempo de resolução do suporte). Trata eventuais dados nulos usando imputação pela mediana (`SimpleImputer`) e padroniza as escalas estatísticas com `StandardScaler`, centralizando a média em 0 e ajustando o desvio padrão para 1.
2. **Pipeline de Recursos Categóricos:** Aplicado à variável geográfica `customer_region`. Trata nulos usando categoria constante e codifica as regiões via codificação One-Hot (`OneHotEncoder`).
3. **Tratamento de Categorias Desconhecidas:** Configuramos o parâmetro `handle_unknown="ignore"` no One-Hot Encoder para garantir estabilidade em ambiente de produção. Se uma nova região surgir em inferências futuras, o modelo não quebrará o sistema, simplesmente ignorando a nova coluna de forma segura.

---

## 📊 3. Benchmarking de Algoritmos via Validação Cruzada (Stratified 5-Fold CV)

Para simular um ambiente de testes rigoroso e livre de vieses de seleção, dividimos a base original de forma estratificada: **80% para o conjunto de treinamento (2.000 pedidos)** e **20% reservados para o holdout de teste cego (500 pedidos)**. A estratificação assegura que a proporção atual de **84,36%** de detratores seja preservada nos dois subconjuntos.

Realizamos uma **Validação Cruzada Estratificada com 5 dobras** exclusivamente no conjunto de treino para comparar e auditar o desempenho de três estimadores concorrentes:

| Algoritmo Concorrente | ROC-AUC (Média +/- DP) | Average Precision (Média) | Acurácia (Média +/- DP) | F1-Score (Média +/- DP) |
| :--- | :---: | :---: | :---: | :---: |
| **DummyClassifier** (Baseline) | 0.5000 (+/- 0.0000) | 0.8435 (+/- 0.0012) | 0.8435 (+/- 0.0012) | 0.9151 (+/- 0.0007) |
| **RandomForestClassifier** | 0.8764 (+/- 0.0206) | 0.9722 (+/- 0.0051) | 0.8685 (+/- 0.0049) | 0.9263 (+/- 0.0028) |
| **LogisticRegression** (Campeão) | **0.8964 (+/- 0.0113)** | **0.9790 (+/- 0.0027)** | **0.8685 (+/- 0.0060)** | **0.9245 (+/- 0.0040)** |

*As tabelas com as métricas de auditoria foram salvas de forma transparente no repositório em `reports/model_cv_metrics.csv`.*

### Raciocínio para Seleção do Modelo:
A **Regressão Logística** foi selecionada por apresentar a melhor ROC-AUC (0.8964) e a melhor Average Precision (0.9790) na validação cruzada desta execução. A diferença para a floresta aleatória foi pequena em algumas métricas, por isso a escolha também considera interpretabilidade.

Além do desempenho observado, a escolha considera a **interpretabilidade do modelo linear**. Os coeficientes podem apoiar a análise da direção das associações, sem representar, por si só, relações causais. Modelos mais complexos continuam sendo alternativas para comparações futuras.

---

## 🎯 4. Desempenho Final no Holdout (Métricas do Experimento)

Após treinar o pipeline final em 80% da base, avaliamos a Regressão Logística uma vez no conjunto de holdout, composto por 500 registros não vistos:

* **ROC-AUC (Área sob a Curva ROC):** **0.8687**, indicando boa capacidade de ordenação nesta amostra.
* **Average Precision (AP):** **0.9740** (alto rigor de ordenação na identificação da classe positiva).
* **Acurácia Geral:** **85,80%**.
* **F1-Score:** **0.9190**.
* **Precisão (Precision):** **88,57%**, indicando a proporção de previsões positivas corretas na amostra de teste.
* **Revocação (Recall):** **95,50%**. Na amostra de teste, essa foi a proporção de detratores identificada pelo modelo no limiar utilizado; não representa garantia de desempenho em produção.

*As métricas finais foram exportadas para o arquivo gerencial `reports/model_metrics.csv`.*

---

## 🔍 5. Diagnóstico de Força das Features: Importância por Permutação

Para identificar as reais alavancas geradoras de atrito na operação, aplicamos o método de **Importância por Permutação** no conjunto de holdout, medindo a queda média na ROC-AUC após embaralhar aleatoriamente os valores de cada variável preditora:

```
                      feature  importance_mean  importance_std
1        delivery_delay_days         0.192769        0.015512
2           complaints_count         0.127342        0.017412
3       resolution_time_days         0.023329        0.007790
4  customer_service_contacts         0.001656        0.002491
5              discount_value         0.000279        0.000166
6        payment_installments         0.000197        0.000095
```

*A tabela completa foi exportada e registrada em `reports/model_feature_importance.csv`.*

### 💡 Análise do Diagnóstico:
* **delivery_delay_days (Importância: ~0.193):** Foi a variável com maior importância por permutação nesta execução; atrasos aparecem como sinal operacional relevante associado ao risco.
* **complaints_count (Importância: ~0.127):** Também apresentou importância relevante, seguida por tempo de resolução (~0.023) e contatos com atendimento (~0.002).
* **Demais variáveis:** Tiveram importância próxima de zero nesta amostra. A importância por permutação descreve o comportamento do modelo e não comprova causalidade.

---

## ⚠️ 6. Limitações e Fronteiras do Modelo Preditivo

Para manter o rigor e a transparência perante a banca examinadora do **Tech Challenge**, listamos as limitações técnicas e de dados identificadas:

1. **Vieses de Autoseleção (O Meio Silencioso):** O modelo aprendeu os padrões de comportamento com base na base de dados de clientes que aceitaram responder à pesquisa de NPS. Clientes que não respondem à pesquisa voluntária (o meio silencioso) podem possuir padrões de insatisfação distintos, o que exige cautela na generalização do modelo em produção.
2. **Ausência de Variáveis Críticas de Produto (Ponto Cego):** O dataset ignora variáveis fundamentais como a qualidade física do produto recebido, a usabilidade do aplicativo, ações agressivas de preços da concorrência ou a reputação da marca na mídia tradicional. O modelo atual assume que toda insatisfação decorre de logística e atendimento.
3. **Estabilidade de Limiar de Risco (Trade-off de Erro):** A definição do limiar de probabilidade preditiva para classificar um cliente em "Risco Crítico" (atualmente fixado em 75%) deve ser acompanhada de uma análise financeira de ROI: o custo operacional de contactar preventivamente um cliente (com cupons de desconto) versus o valor do Lifetime Value (LTV) recuperado.

---

*O pipeline preditivo serializado foi salvo em `models/detractor_classifier.joblib` e está disponível para execução local. O uso em produção ainda requer validação temporal, monitoramento e integração com os sistemas operacionais.*
