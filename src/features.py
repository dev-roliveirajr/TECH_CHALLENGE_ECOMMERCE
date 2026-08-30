"""
Módulo de Engenharia de Features e Pré-processamento do Projeto NPS Preditivo.
    Unifica as transformações de variáveis usando o ColumnTransformer do
    Scikit-Learn, garantindo o isolamento estatístico completo para evitar
    vazamento de dados (data leakage).
"""

import logging
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from src import config

logger = logging.getLogger(__name__)


def get_feature_lists(df: pd.DataFrame):
    """
    Identifica dinamicamente as colunas numéricas e categóricas que serão usadas
    como features no modelo preditivo, excluindo as variáveis listadas em
    config.EXCLUDED_FROM_MODEL
    e a própria target 'is_detractor'.
    """
    # Lista de exclusões, target e grupos categóricos auxiliares.
    exclusions = config.EXCLUDED_FROM_MODEL.copy()
    if "is_detractor" not in exclusions:
        exclusions.append("is_detractor")

    # Excluir grupos categóricos auxiliares criados para AED.
    for col in ["delay_group", "contacts_group", "support_group"]:
        if col not in exclusions:
            exclusions.append(col)

    # Filtrar colunas que realmente existem no DataFrame
    available_exclusions = [col for col in exclusions if col in df.columns]

    # Features candidatas (tudo menos as exclusões)
    feature_cols = [col for col in df.columns if col not in available_exclusions]

    # Separar numéricas e categóricas
    num_features = []
    cat_features = []

    for col in feature_cols:
        if pd.api.types.is_numeric_dtype(df[col]):
            num_features.append(col)
        else:
            cat_features.append(col)

    logger.info(
        f"Features Numéricas identificadas ({len(num_features)}): {num_features}"
    )
    logger.info(
        f"Features Categóricas identificadas ({len(cat_features)}): {cat_features}"
    )

    return num_features, cat_features


def build_preprocessing_pipeline(
    num_features: list, cat_features: list
) -> ColumnTransformer:
    """
    Constrói o ColumnTransformer do Scikit-Learn para unificar o
    pré-processamento.
    - Numéricas: Imputação de nulos pela mediana + Padronização (StandardScaler)
        - Categóricas: Imputação de nulos por valor constante + Codificação
            One-Hot (OneHotEncoder)
    """
    logger.info("Construindo pipeline de pré-processamento (ColumnTransformer)...")

    # Pipeline para variáveis numéricas
    num_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    # Pipeline para variáveis categóricas
    cat_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="constant", fill_value="missing")),
            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
    )

    # Unificação com ColumnTransformer
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", num_transformer, num_features),
            ("cat", cat_transformer, cat_features),
        ],
        remainder="drop",  # Descarta qualquer outra coluna não listada
    )

    return preprocessor


def split_features_target(df: pd.DataFrame, target_col: str = "is_detractor"):
    """
    Divide o DataFrame em matriz de features (X) e vetor da variável alvo (y),
    removendo todas as colunas que não devem ir para o modelo preditivo.
    """
    if target_col not in df.columns:
        raise ValueError(
            f"A coluna target '{target_col}' não foi encontrada no DataFrame."
        )

    y = df[target_col].copy()

    # Lista de colunas a remover de X
    drop_cols = config.EXCLUDED_FROM_MODEL.copy()
    if target_col not in drop_cols:
        drop_cols.append(target_col)

    # Remover também colunas de faixas categóricas auxiliares se existirem
    for col in ["delay_group", "contacts_group", "support_group"]:
        if col not in drop_cols:
            drop_cols.append(col)

    # Garantir que só removemos colunas que existem no df
    cols_to_drop = [col for col in drop_cols if col in df.columns]
    X = df.drop(columns=cols_to_drop).copy()

    logger.info(f"Divisão X/y concluída. Shape de X: {X.shape}, Shape de y: {y.shape}")
    return X, y


if __name__ == "__main__":
    # Teste rápido do módulo de features
    import sys
    from pathlib import Path

    sys.path.append(str(Path(__file__).resolve().parent.parent))
    from src.dataset import (
        load_raw_data,
        binarize_target,
        create_business_risk_features,
    )

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    try:
        # Carregar dados e simular preparação
        raw_df = load_raw_data()
        df_processed = binarize_target(raw_df)
        df_processed = create_business_risk_features(df_processed)

        # Testar split X/y
        X, y = split_features_target(df_processed)

        # Obter listas de features
        num_cols, cat_cols = get_feature_lists(X)

        # Construir e testar pipeline de pré-processamento
        preprocessor = build_preprocessing_pipeline(num_cols, cat_cols)

        # Fit_transform para verificar funcionamento
        X_trans = preprocessor.fit_transform(X)
        logger.info(
            "Pipeline testado com sucesso! Shape dos dados transformados: "
            f"{X_trans.shape}"
        )

    except Exception as e:
        logger.error(f"Erro ao testar o módulo de features: {e}")
        sys.exit(1)
