"""
Configurações Globais do Projeto NPS Preditivo.
Centralização de parâmetros, caminhos e variáveis para garantir reprodutibilidade,
consistência e prevenir vazamentos de dados (data leakage).
"""

import os
from pathlib import Path

# Raiz do repositório (diretório pai de src/)
BASE_DIR = Path(__file__).resolve().parent.parent

# Caminhos lógicos do projeto
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
REPORTS_DIR = BASE_DIR / "reports"
REPORTS_FIGURES_DIR = REPORTS_DIR / "figures"

# Parâmetro de repetibilidade / reprodutibilidade do modelo
RANDOM_STATE = 42

# Variáveis a serem excluídas do modelo para evitar vazamento de dados (data leakage)
# ou por representarem informações redundantes/futuras:
# - customer_id, order_id: identificadores únicos sem poder preditivo.
# - nps_score: nota original de onde é derivada a target.
# - repeat_purchase_30d: variável coletada 30 dias após o pedido (informação futura).
# - csat_internal_score: pontuação de satisfação interna coletada em momento incerto.
EXCLUDED_FROM_MODEL = [
    "customer_id",
    "order_id",
    "nps_score",
    "repeat_purchase_30d",
    "csat_internal_score",
]
