"""
Módulo de Treinamento, Seleção e Auditoria do Modelo Preditor de Detratores.
Realiza divisão estratificada (80/20), executa Validação Cruzada Estratificada
(5-Fold) para comparar Dummy, Regressão Logística e Random Forest, avalia o
melhor modelo no conjunto de teste, calcula Importância por Permutação das
variáveis e salva o pipeline preditivo serializado (.joblib).
"""

import logging
import sys
from pathlib import Path
import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_validate
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.dummy import DummyClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    roc_auc_score,
    average_precision_score,
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.inspection import permutation_importance

# Garantir que o diretório pai esteja no PATH para importações locais
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from src import config  # noqa: E402
from src.dataset import load_raw_data  # noqa: E402
from src.features import (  # noqa: E402
    split_features_target,
    get_feature_lists,
    build_preprocessing_pipeline,
)

# Configuração de logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def train_and_evaluate():
    """
    Função principal que executa todo o fluxo de treinamento e auditoria.
    """
    # 1. Carregar dados processados
    processed_path = config.DATA_DIR / "processed" / "processed_nps_data.csv"
    if not processed_path.exists():
        logger.error(
            f"Arquivo de dados processados não encontrado em: {processed_path}. "
            "Executando dataset.py..."
        )
        from src import dataset

        # Executar dataset.py para gerar a base se não existir
        df = dataset.load_raw_data()
        dataset.validate_data(df)
        df_target = dataset.binarize_target(df)
        df_risk = dataset.create_business_risk_features(df_target)
        processed_path.parent.mkdir(parents=True, exist_ok=True)
        df_risk.to_csv(processed_path, index=False)

    df = pd.read_csv(processed_path)
    logger.info(f"Dados carregados para modelagem. Shape: {df.shape}")

    # 2. Divisão X/y e Holdout estratificado (80/20)
    X, y = split_features_target(df)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, stratify=y, random_state=config.RANDOM_STATE
    )
    logger.info(f"Treino - X: {X_train.shape}, y: {y_train.shape}")
    logger.info(f"Holdout (Teste) - X: {X_test.shape}, y: {y_test.shape}")

    # 3. Engenharia de Features e Pré-processamento
    num_features, cat_features = get_feature_lists(X_train)
    preprocessor = build_preprocessing_pipeline(num_features, cat_features)

    # 4. Configurar Modelos Concorrentes
    models = {
        "DummyClassifier": DummyClassifier(
            strategy="most_frequent", random_state=config.RANDOM_STATE
        ),
        "LogisticRegression": LogisticRegression(
            random_state=config.RANDOM_STATE, max_iter=1000
        ),
        "RandomForestClassifier": RandomForestClassifier(
            random_state=config.RANDOM_STATE, max_depth=6
        ),
    }

    # 5. Validação Cruzada Estratificada (5-Fold)
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=config.RANDOM_STATE)
    cv_records = []

    logger.info("Iniciando Validação Cruzada Estratificada de 5 Folds...")
    for name, model in models.items():
        pipe = Pipeline([("preprocessor", preprocessor), ("model", model)])

        cv_results = cross_validate(
            pipe,
            X_train,
            y_train,
            cv=skf,
            scoring=["roc_auc", "average_precision", "accuracy", "f1"],
            return_train_score=False,
        )

        # Guardar métricas médias e desvios padrões
        for metric in ["roc_auc", "average_precision", "accuracy", "f1"]:
            test_scores = cv_results[f"test_{metric}"]
            cv_records.append(
                {
                    "model": name,
                    "metric": metric.upper(),
                    "mean_score": np.mean(test_scores),
                    "std_score": np.std(test_scores),
                }
            )
            logger.info(
                "[%s] %s: %.4f (+/- %.4f)",
                name,
                metric.upper(),
                np.mean(test_scores),
                np.std(test_scores),
            )

    # Salvar métricas de CV
    cv_metrics_df = pd.DataFrame(cv_records)
    config.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    cv_metrics_path = config.REPORTS_DIR / "model_cv_metrics.csv"
    cv_metrics_df.to_csv(cv_metrics_path, index=False)
    logger.info(f"Métricas de Validação Cruzada salvas em: {cv_metrics_path}")

    # 6. Escolha e Treinamento do Modelo Final (Regressão Logística)
    logger.info(
        "Selecionando Regressão Logística como o melhor modelo interpretável..."
    )
    best_model_name = "LogisticRegression"
    best_model = models[best_model_name]

    final_pipeline = Pipeline([("preprocessor", preprocessor), ("model", best_model)])

    logger.info(
        "Treinando o pipeline preditivo final em toda a base de treinamento (80%)..."
    )
    final_pipeline.fit(X_train, y_train)

    # 7. Avaliação Final Única no Holdout (Teste - 20%)
    logger.info("Executando avaliação única no conjunto de holdout (Teste)...")
    y_pred_proba = final_pipeline.predict_proba(X_test)[:, 1]
    y_pred = final_pipeline.predict(X_test)

    holdout_metrics = {
        "model": [best_model_name],
        "roc_auc": [roc_auc_score(y_test, y_pred_proba)],
        "average_precision": [average_precision_score(y_test, y_pred_proba)],
        "accuracy": [accuracy_score(y_test, y_pred)],
        "f1_score": [f1_score(y_test, y_pred)],
        "precision": [precision_score(y_test, y_pred)],
        "recall": [recall_score(y_test, y_pred)],
    }

    holdout_metrics_df = pd.DataFrame(holdout_metrics)
    metrics_path = config.REPORTS_DIR / "model_metrics.csv"
    holdout_metrics_df.to_csv(metrics_path, index=False)

    logger.info("--- MÉTRICAS FINAIS NO HOLDOUT (TESTE) ---")
    for col in holdout_metrics_df.columns:
        if col != "model":
            logger.info("%s: %.4f", col.upper(), holdout_metrics_df[col].values[0])

    # 8. Cálculo de Importância por Permutação (ROC-AUC Holdout)
    logger.info(
        "Calculando a Importância por Permutação com base na ROC-AUC de Holdout..."
    )
    perm_importance = permutation_importance(
        final_pipeline,
        X_test,
        y_test,
        scoring="roc_auc",
        n_repeats=10,
        random_state=config.RANDOM_STATE,
    )

    importance_df = pd.DataFrame(
        {
            "feature": X_test.columns,
            "importance_mean": perm_importance.importances_mean,
            "importance_std": perm_importance.importances_std,
        }
    ).sort_values(by="importance_mean", ascending=False)

    importance_path = config.REPORTS_DIR / "model_feature_importance.csv"
    importance_df.to_csv(importance_path, index=False)
    logger.info(f"Tabela de importância por permutação salva em: {importance_path}")

    # 9. Serialização do Pipeline de Produção
    config.MODELS_DIR.mkdir(parents=True, exist_ok=True)
    model_export_path = config.MODELS_DIR / "detractor_classifier.joblib"
    joblib.dump(final_pipeline, model_export_path)
    logger.info(f"Pipeline final serializado com sucesso em: {model_export_path}")
    logger.info(
        "Ciclo de vida do Passo 6 de Modelagem preditiva concluído com sucesso!"
    )


if __name__ == "__main__":
    train_and_evaluate()
