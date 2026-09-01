# NPS Preditivo: De Reativo ao Proativo na Experiência do Cliente no E-Commerce

Este repositório contém a solução para o desenvolvimento de um **modelo preditivo de Net Promoter Score (NPS)** voltado para e-commerce. O objetivo é usar dados operacionais de logística, pedidos e atendimento para estimar o risco de um cliente se tornar **Detrator** antes da pesquisa de satisfação, apoiando a priorização de ações pelas áreas de negócio.

---

## 🗺️ 1. Descrição do Projeto

O projeto parte de um problema do varejo digital: a insatisfação costuma ser observada depois que a jornada de compra termina e a pesquisa de NPS é aplicada. A solução proposta transforma sinais operacionais disponíveis em uma estimativa de risco, criando a possibilidade de priorizar casos antes da coleta da pesquisa.

### Problema de negócio

A dor central do projeto não é apenas a baixa nota de satisfação em si, mas a incapacidade de agir antes que o problema se consolide. Em e-commerce, o atraso na entrega, o tempo de resposta do suporte e o acúmulo de reclamações podem transformar uma transação em uma experiência negativa que afeta retenção, reputação e recorrência. Esse contexto é aprofundado em [docs/analise_negocio.md](docs/analise_negocio.md), que explica a relevância do NPS para a operação, os stakeholders envolvidos e o impacto do problema em logística, atendimento, CRM e experiência do cliente.

### O que foi descoberto

Na amostra analisada, os principais indicadores associados ao risco foram operacionais. Atrasos na entrega, reclamações acumuladas e tempo elevado de resolução apresentaram associação com a detração, com aumento expressivo das taxas observadas a partir de aproximadamente 3 dias de atraso. Esses achados estão detalhados em [docs/analise_exploratoria_dados.md](docs/analise_exploratoria_dados.md).

### O que foi feito

Para transformar esses sinais em decisão, foi implementado um pipeline de Ciência de Dados com preparação dos dados, engenharia de features, controle de leakage, seleção de modelos e avaliação preditiva. A abordagem considera a variável alvo `is_detractor`, exclui colunas não disponíveis ou inadequadas para a previsão e compara modelos usando validação cruzada. A parte técnica está detalhada em [docs/avaliacao_modelos_e_desempenho.md](docs/avaliacao_modelos_e_desempenho.md).

### Conclusão

A conclusão, limitada à amostra analisada, é que os fatores operacionais (**logistica** e **atendimento**) apresentaram maior associação com a detração do que a estrutura do **pedido** (valor ou frete). A análise também indica que a **região geográfica** não apresentou relação estatisticamente relevante com a chance de o cliente se tornar detrator.

O score preditivo pode apoiar a priorização operacional antes da coleta do NPS, mas sua aplicação deve ser validada em dados novos e em um experimento controlado. As recomendações para logística e atendimento estão em [docs/estrategias_logistica_e_atendimento.md](docs/estrategias_logistica_e_atendimento.md).

### Apresentação do storytelling e vídeo

A apresentação do storytelling do projeto está disponível em [docs/apresentacao_storytelling.pdf](docs/apresentacao_storytelling.pdf). O vídeo da apresentação será disponibilizado em "link do vídeo no YouTube", reunindo os principais achados, a solução preditiva e as recomendações de negócio do projeto.

---

## 🗂️ 2. Estrutura de Pastas do Projeto

O repositório está organizado da seguinte forma:

```text
project/
├── data/
│   ├── interim/
│   ├── processed/
│   │   ├── processed_nps_data.csv
│   │   └── scored_orders.csv
│   └── raw/
│       └── desafio_nps_fase_1.csv
├── docs/
│   ├── analise_negocio.md
│   ├── analise_exploratoria_dados.md
│   ├── avaliacao_modelos_e_desempenho.md
│   ├── estrategias_logistica_e_atendimento.md
│   └── apresentacao_storytelling.pdf
├── models/
│   └── detractor_classifier.joblib
├── notebooks/
│   ├── aed_nps.ipynb
│   ├── avaliacao_modelos.ipynb
│   ├── manipulacao_dataset.ipynb
│   ├── predicao.ipynb
│   └── pre_processamento.ipynb
├── reports/
│   ├── business_metrics.csv
│   ├── business_metrics.html
│   ├── figures/
│   ├── model_cv_metrics.csv
│   ├── model_feature_importance.csv
│   └── model_metrics.csv
├── src/
│   ├── __init__.py
│   ├── business_metrics.py
│   ├── business_metrics_html_report.py
│   ├── config.py
│   ├── dataset.py
│   ├── features.py
│   ├── modeling/
│   │   ├── __init__.py
│   │   ├── predict.py
│   │   └── train.py
│   └── plots.py
├── tests/
│   ├── conftest.py
│   ├── test_business_metrics.py
│   ├── test_dataset.py
│   ├── test_features.py
│   ├── test_plots.py
│   ├── test_predict.py
│   └── test_train.py
├── .gitignore
├── .pre-commit-config.yaml
├── LICENSE
├── Makefile
├── pyproject.toml
├── README.md
├── requirements.txt
├── setup.cfg
└── .venv/   # ambiente local, não versionado
```

---

## 🐍 3. Requisitos e Pacotes Necessários

Para garantir a estabilidade do código, o projeto requer **Python 3.11 ou superior**.
O ambiente utilizado para validação deste projeto é o Python 3.12.

As dependências estão organizadas no `requirements.txt` sob três grandes pilares:

*   **Manipulação e Análise de Dados:** `pandas`, `numpy`, `scipy`
*   **Machine Learning & MLOps:** `scikit-learn`, `joblib`
*   **Visualização Científica:** `matplotlib`, `seaborn`
*   **Qualidade, Linting e Automação:** `flake8`, `black`, `pre-commit`, `pytest`

---

## ⚙️ 4. Instruções de Setup e Instalação

Siga o passo a passo abaixo no terminal do seu VS Code para configurar o ambiente virtual, instalar todas as dependências necessárias e habilitar os Git hooks automáticos antes de realizar qualquer commit.

### Passo 1: Atualizar o Sistema e Instalar o Venv do Python
Caso seu terminal Linux não possua as ferramentas do Python virtual environment habilitadas, instale-as usando:
```bash
sudo apt update
sudo apt install python3.12-venv
```

### Passo 2: Executar o Setup Automático do Ambiente
Para automatizar a criação da `.venv`, instalar as dependências e ativar os
hooks do **pre-commit**, rode simplesmente:
```bash
make setup
```
Este comando cria a `.venv`, instala as dependências e registra o `pre-commit`
no diretório local do Git.

### Passo 3: Ativar o Ambiente Virtual
Com o ambiente criado com sucesso pelo Makefile, ative a `.venv` no seu terminal:
*   **No Linux/macOS:**
    ```bash
    source .venv/bin/activate
    ```
*   **No Windows (Git Bash):**
    ```bash
    source .venv/Scripts/activate
    ```

### Dados e artefatos gerados

O arquivo bruto `data/raw/desafio_nps_fase_1.csv` é a entrada do pipeline.
Os arquivos em `data/processed/`, os relatórios gerados e o modelo serializado
em `models/` são artefatos produzidos localmente.

Se a base bruta não estiver disponível no clone, coloque-a em
`data/raw/desafio_nps_fase_1.csv` antes de executar `make data`.

---

## 🛠️ 5. Comandos Úteis do Makefile (Ciclo de Desenvolvimento)

Para manter o código alinhado às diretrizes estritas do **PEP 8** e garantir que nenhuma alteração quebre os padrões de formatação, utilize os seguintes comandos atalhos com a sua `.venv` ativada:

```bash
# 1. Formata automaticamente o código usando o Black de acordo com o pyproject.toml
make format

# 2. Executa a auditoria de estilo estática via Flake8 (setup.cfg)
make lint

# 3. Roda os testes unitários do projeto via Pytest
make test

# 4. Remove de forma recursiva os caches temporários e resíduos (__pycache__, .pytest_cache)
make clean

# 5. Executa o pipeline de preparação dos dados
make data

# 6. Treina o modelo e gera os relatórios
make train

# 7. Executa a inferência e gera data/processed/scored_orders.csv
make predict
```

### 🔒 Como o Pre-commit Trabalha no seu Commit:
Toda vez que você tentar consolidar alterações no Git (`git commit`), as seguintes checagens estáticas serão executadas automaticamente:
1. **Trim Trailing Whitespace:** Remove espaços inúteis ao final de linhas de código.
2. **Fix End of Files:** Garante que todo arquivo Python termine com uma quebra de linha padrão.
3. **Black:** Formata os arquivos modificados. Caso realize alterações estéticas necessárias, ele bloqueará o commit inicial para que você revise a alteração e realize o comando de commit novamente.
4. **Flake8:** Valida rigorosamente as regras do PEP 8, acusando inconsistências de estilo (como imports não utilizados ou nomes de variáveis em conflito) antes de consolidar o commit.

Para validar todos os arquivos manualmente antes do commit, execute:

```bash
.venv/bin/pre-commit run --all-files
```

Para validar somente os arquivos preparados para commit:

```bash
.venv/bin/pre-commit run
```

Caso um hook formate arquivos, adicione as alterações novamente com `git add`
antes de criar o commit.

---

## 📊 6. Pipeline de Dados

1. **Ingestão e Validação (`src/dataset.py`):** Carga do arquivo `desafio_nps_fase_1.csv` que você deve armazenar em `data/raw/` e binarização da target `is_detractor`.
2. **Exploratory Data Analysis (EDA):** Identificação de pontos de colapso de atendimento e atraso logístico, com testes de hipótese paramétricos e não paramétricos via SciPy (correlação de Spearman, Mann-Whitney U, Qui-Quadrado).
3. **Modelagem (`src/modeling/train.py`):** Treinamento com 80/20 train-test split, Stratified 5-Fold Cross Validation comparando algoritmos (Random Forest, Regressão Logística e Baselines).
4. **Escoragem (`src/modeling/predict.py`):** Motor de pontuação ordenando os clientes em faixas de risco operacional:
   * **Baixo Risco:** Probabilidade $\le 0.50$
   * **Alto Risco:** Probabilidade entre $0.50$ e $0.75$
   * **Risco Crítico:** Probabilidade $> 0.75$
### Momento da predição e disponibilidade das variáveis

O score deve ser gerado após a atualização dos dados operacionais do pedido e antes da aplicação da pesquisa de NPS. Para evitar o uso de informação futura, `nps_score` e `repeat_purchase_30d` são excluídos do modelo. A variável `csat_internal_score` também é excluída porque o momento de sua coleta não está definido. Variáveis de atendimento, como `complaints_count`, `customer_service_contacts` e `resolution_time_days`, só devem ser usadas na operação se já estiverem disponíveis no momento definido para a escoragem; caso contrário, devem permanecer restritas a análises retrospectivas.

## 📈 7. Resultados do Modelo

No conjunto de holdout de teste, o pipeline de Regressão Logística apresentou:

| Métrica | Resultado |
| --- | ---: |
| ROC-AUC | 0,8758 |
| Average Precision | 0,9463 |
| Accuracy | 0,8440 |
| F1-score | 0,8984 |
| Precisão | 0,8668 |
| Recall | 0,9324 |

Esses resultados são referências do artefato atualmente disponível. Um novo
treinamento pode produzir pequenas variações.
Os detalhes estão disponíveis em [reports/model_metrics.csv](reports/model_metrics.csv)
e [reports/model_cv_metrics.csv](reports/model_cv_metrics.csv).

---

## ⚙️ 8. Treinamento do Modelo e Predição de Novas Amostras

Para garantir a reprodutibilidade e a operacionalização do **NPS Preditivo** em ambientes de produção ou experimentação local, utilize as diretrizes abaixo.

### 🔄 8.1. Como Treinar o Modelo (Múltiplas Vias)

O ciclo de vida de treinamento do modelo preditivo foi estruturado em duas camadas complementares (Produção vs. Experimentação):

1. **Via Script de Produção (`src/modeling/train.py`):**
   * **Fluxo Oficial MLOps (Headless):** Este é o motor de produção automatizado. Ele carrega os dados processados e higienizados de `data/processed/processed_nps_data.csv`, faz o split de holdout estratificado 80/20 (para garantir o balanceamento crítico da classe detratora de **74,04%**), roda a Validação Cruzada Estratificada de 5 folds (Stratified 5-Fold CV) para auditar os classificadores e exporta o binário final consolidado com o pré-processador para `models/detractor_classifier.joblib`.
   * **Execução via CLI Direta:**
     ```bash
         .venv/bin/python src/modeling/train.py
     ```
   * **Execução via Automação do Makefile:**
     ```bash
     make train
     ```

2. **Via Jupyter Notebook de Experimentação (`notebooks/avaliacao_modelos.ipynb`):**
   * **Abordagem de Storytelling & Exploração:** Recomendado para analistas e para a banca avaliadora do Tech Challenge. Permite executar o ciclo de treino célula a célula de forma visual, gerando gráficos interativos como a Curva ROC, Matriz de Confusão e a Importância por Permutação baseada no SciPy.

---

### 🔮 8.2. Como Fazer a Predição de uma Nova Amostra (Single Sample Inference)

Para simular o uso do modelo em tempo real (por exemplo, quando um novo pedido é registrado no e-commerce e as variáveis logísticas e de atendimento são geradas), você pode carregar o pipeline serializado (.joblib) e passar a nova transação como uma amostra isolada.

O pipeline de inferência carrega conjuntamente o `ColumnTransformer` (StandardScaler para numéricas e OneHotEncoder para a região categórica) e o modelo de `LogisticRegression` campeão. Isso garante que a amostra passe exatamente pelas mesmas transformações do treino, **eliminando qualquer risco de vazamento de dados (data leakage)**.

Abaixo, está o script Python autônomo pronto para copiar, colar e rodar no seu terminal local:

```python
import joblib
import pandas as pd

# 1. Carregar o pipeline preditivo completo (preprocessor + classificador)
pipeline_path = "models/detractor_classifier.joblib"
try:
    pipeline = joblib.load(pipeline_path)
    print("✓ Pipeline preditivo carregado com sucesso!")
except FileNotFoundError:
    raise FileNotFoundError(f"Erro: O binário do modelo não foi encontrado em '{pipeline_path}'. Execute o 'make train' antes.")

Os limiares de 0,50 e 0,75 são regras iniciais de priorização, não parâmetros validados financeiramente. Em uma implantação, devem ser recalibrados com base nos custos de falsos positivos e falsos negativos, no custo das intervenções e no valor esperado de retenção.

# 2. Estruturar os dados operacionais da nova transação isolada
# (Respeitando rigorosamente o Dicionário de Dados do Tech Challenge)
nova_transacao = {
    "customer_age": 45,
    "customer_region": "Sudeste",
    "customer_tenure_months": 36,
    "order_value": 450.00,
    "items_quantity": 2,
    "discount_value": 15.00,
    "payment_installments": 3,
    "delivery_time_days": 10,
    "delivery_delay_days": 3,          # Ponto de colapso mapeado aos >=3 dias de atraso
    "freight_value": 25.00,
    "delivery_attempts": 1,
    "customer_service_contacts": 4,    # Alto volume de contatos (atrito operacional)
    "resolution_time_days": 5,
    "complaints_count": 2
}

# Converter a transação em DataFrame de uma única linha
df_amostra = pd.DataFrame([nova_transacao])

# 3. Computar a probabilidade exata de detração (Classe 1)
probabilidade_detracao = pipeline.predict_proba(df_amostra)[0][1]

# 4. Classificar a transação (0 = Não Detrator | 1 = Detrator)
predicao_classe = pipeline.predict(df_amostra)[0]

# 5. Enquadrar o cliente nas faixas de risco operacional da empresa
if probabilidade_detracao <= 0.50:
    faixa_risco = "Baixo Risco"
elif probabilidade_detracao <= 0.75:
    faixa_risco = "Alto Risco"
else:
    faixa_risco = "Risco Crítico"

print("\n=== RESULTADO DO NPS PREDITIVO ===")
print(f"-> Probabilidade Estimada de Detração: {probabilidade_detracao:.2%}")
print(f"-> Classe Predita: {predicao_classe} ({'Detrator (NPS 0-6)' if predicao_classe == 1 else 'Não Detrator (NPS 7-10)'})")
print(f"-> Faixa de Atendimento Recomendada: {faixa_risco}")

if faixa_risco == "Risco Crítico":
    print("🚨 AÇÃO RECOMENDADA: Acionar alerta logístico de prioridade máxima e triagem VIP de suporte!")
elif faixa_risco == "Alto Risco":
    print("⚠️ AÇÃO RECOMENDADA: Disparar e-mail preventivo e priorizar ticket de CS.")
else:
    print("🟢 AÇÃO RECOMENDADA: Fluxo de atendimento padrão (jornada estável).")
```
