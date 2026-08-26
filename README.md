# NPS Preditivo: De Reativo ao Proativo na Experiência do Cliente no E-Commerce

Este repositório contém a solução completa para o desenvolvimento de um **modelo preditivo de Net Promoter Score (NPS)** voltado para e-commerce. O objetivo principal do projeto é transformar dados puramente operacionais (logística, pedidos e atendimento) em inteligência preditiva capaz de prever se um cliente se tornará um **Detrator** antes mesmo que a pesquisa de satisfação seja aplicada, permitindo que as áreas de negócios ajam de forma preventiva e proativa.

---

## 🗺️ 1. Descrição do Projeto

No ambiente dinâmico do varejo digital, o crescimento acelerado gera ganhos de escala substanciais, mas também traz grandes desafios à experiência de compra. O NPS é uma métrica clássica para mensurar essa experiência, porém possui duas grandes limitações:
1. **É reativo:** Só é coletado após o término da jornada.
2. **É parcial:** Depende da disposição voluntária do cliente para responder (gerando vieses de autoseleção).

Esta solução implementa um pipeline estruturado de Ciência de Dados para classificar e pontuar transações de e-commerce sob risco de detração. O modelo foca em **Classificação Binária** (variável alvo: `is_detractor`), priorizando a identificação de clientes sob Risco Crítico ou Alto Risco devido a gargalos como atrasos de entrega, problemas de atendimento ou atritos com o produto.

---

## 🗂️ 2. Estrutura de Pastas do Projeto

O repositório está organizado segundo os padrões mais consolidados de arquitetura de projetos Python e MLOps:

```text
├── LICENSE                 # Licença open-source do projeto
├── Makefile                # Automação de tarefas (ambiente, linter, testes, treino e inferência)
├── README.md               # Este arquivo de instruções gerais
├── pyproject.toml          # Metadados do projeto e configurações globais (ex: Black)
├── setup.cfg               # Configurações do linter de estilo Flake8
├── requirements.txt        # Dependências do ecossistema Python para execução
├── .gitignore              # Proteção para dados sensíveis, caches e binários locais
├── .pre-commit-config.yaml # Configuração de Git hooks contra commits fora de conformidade
│
├── data                    # Versionamento de dados de forma segura (ignorados no push)
│   ├── raw                 # Base de dados original e imutável (desafio_nps_fase_1.csv)
│   ├── interim             # Dados em estágios intermediários de tratamento
│   ├── processed           # Conjunto de dados finais e higienizados para o modelo
│   └── external            # Fontes de dados externas e complementares
│
├── docs                    # Documentação detalhada e relatórios do projeto
│
├── models                  # Pipelines serializados e binários do modelo treinado (*.joblib)
│
├── notebooks               # Jupyter Notebooks estruturados para prototipagem e análises
│
├── references              # Dicionários de dados, manuais e guias de negócio
│
├── reports                 # Relatórios gerenciais e técnicos finais emitidos
│   └── figures             # Gráficos gerados para subsidiar os relatórios de negócio
│
├── tests                   # Scripts de testes unitários para os módulos preditivos
│
└── src                     # Código-fonte modular e reutilizável do projeto
    ├── __init__.py         # Inicialização do diretório como pacote Python
    ├── config.py           # Configurações globais, mapeamento de caminhos e prevenção de leakage
    ├── dataset.py          # Scripts de ingestão, engenharia de target e validação
    ├── features.py         # Engenharia de recursos estruturada via ColumnTransformers
    ├── plots.py            # Módulos para geração consistente de gráficos analíticos
    └── modeling            # Scripts dedicados ao ciclo de vida preditivo
        ├── __init__.py     # Inicializador do subpacote de modelagem
        ├── train.py        # Pipeline de treinamento com validação cruzada estratificada
        └── predict.py      # Motor de pontuação/inferência de novos dados operacionais
```

---

## 🐍 3. Requisitos e Pacotes Necessários

Para garantir a estabilidade do código, o projeto exige a versão **Python 3.12** e utiliza bibliotecas específicas para engenharia de dados, modelagem preditiva, visualização, além de ferramentas de qualidade de software.

As dependências estão organizadas no `requirements.txt` sob três grandes pilares:

*   **Manipulação e Análise de Dados:** `pandas`, `numpy`, `scipy`
*   **Machine Learning & MLOps:** `scikit-learn`, `joblib`
*   **Visualização Científica:** `matplotlib`, `seaborn`
*   **Qualidade, Linting e Automação:** `flake8`, `black`, `pre-commit`, `pytest`

---

## ⚙️ 4. Instruções de Setup e Instalação

Siga o passo a passo abaixo no terminal do seu VS Code para configurar o ambiente virtual, instalar todas as dependências necessárias e habilitar os Git hooks automáticos antes de realizar qualquer commit.

### Passo 1: Atualizar o Sistema e Instalar o Venv do Python
Caso seu terminal não possua as ferramentas do Python virtual environment habilitadas, instale-as usando:
```bash
sudo apt update
sudo apt install python3.12-venv
```

### Passo 2: Executar o Setup Automático do Ambiente
Para automatizar a criação da `venv`, instalar as dependências corretas, atualizar o gerenciador de pacotes e ativar o **précompiler (Git hooks)** do projeto, rode simplesmente:
```bash
make setup
```
Este comando realizará todo o trabalho pesado por baixo dos panos e registrará o `pre-commit` no diretório local do Git.

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
```

### 🔒 Como o Précompiler (Pre-commit) Trabalha no seu Commit:
Toda vez que você tentar consolidar alterações no Git (`git commit`), as seguintes checagens estáticas serão executadas automaticamente:
1. **Trim Trailing Whitespace:** Remove espaços inúteis ao final de linhas de código.
2. **Fix End of Files:** Garante que todo arquivo Python termine com uma quebra de linha padrão.
3. **Black:** Formata os arquivos modificados. Caso realize alterações estéticas necessárias, ele bloqueará o commit inicial para que você revise a alteração e realize o comando de commit novamente.
4. **Flake8:** Valida rigorosamente as regras do PEP 8, acusando inconsistências de estilo (como imports não utilizados ou nomes de variáveis em conflito) antes de consolidar o commit.

---

## 📊 6. Metodologia do Pipeline de Dados e Próximos Passos

1. **Ingestão e Validação (`src/dataset.py`):** Carga do arquivo `desafio_nps_fase_1.csv` que você deve armazenar em `data/raw/` e binarização da target `is_detractor`.
2. **Exploratory Data Analysis (EDA):** Identificação de pontos de colapso de atendimento e atraso logístico, com testes de hipótese paramétricos e não paramétricos via SciPy (correlação de Spearman, Mann-Whitney U, Qui-Quadrado).
3. **Modelagem (`src/modeling/train.py`):** Treinamento com 80/20 train-test split, Stratified 5-Fold Cross Validation comparando algoritmos (Random Forest, Regressão Logística e Baselines).
4. **Escoragem (`src/modeling/predict.py`):** Motor de pontuação ordenando os clientes em faixas de risco operacional:
   * **Baixo Risco:** Probabilidade $\le 0.50$
   * **Alto Risco:** Probabilidade entre $0.50$ e $0.75$
   * **Risco Crítico:** Probabilidade $> 0.75$
