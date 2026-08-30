"""
Módulo de Inferência e Classificação de Risco do Projeto NPS Preditivo.
Carrega o pipeline preditivo treinado e escorre novos dados operacionais,
segmentando-os em faixas de risco proativas para tomada de decisão.
"""

import argparse
import logging
from pathlib import Path
import pandas as pd
import joblib

# Configuração de logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def load_trained_pipeline(model_path: Path) -> joblib.compressor:
    """
    Carrega o pipeline completo de pré-processamento e modelagem serializado (.joblib).
    """
    logger.info(f"Carregando pipeline de modelagem de: {model_path}")
    if not model_path.exists():
        raise FileNotFoundError(f"Pipeline serializado não localizado em: {model_path}")

    pipeline = joblib.load(model_path)
    logger.info("Pipeline preditivo carregado com sucesso!")
    return pipeline


def categorize_risk_band(probability: float) -> str:
    """
    Categoriza a probabilidade de detração nas faixas de risco operacionais
    (Risk Bands):
    - Baixo Risco: Probabilidade <= 0.50
    - Alto Risco: Probabilidade entre 0.50 e 0.75 (inclusive)
    - Risco Crítico: Probabilidade > 0.75
    """
    if probability <= 0.50:
        return "Baixo Risco"
    elif 0.50 < probability <= 0.75:
        return "Alto Risco"
    else:
        return "Risco Crítico"


def run_inference(data_path: Path, model_path: Path, output_path: Path) -> pd.DataFrame:
    """
    Executa a escoragem preditiva sobre uma nova carga de dados operacionais.
    """
    # 1. Carregar os dados de entrada
    logger.info(f"Carregando novos dados operacionais para inferência de: {data_path}")
    if not data_path.exists():
        raise FileNotFoundError(
            f"Arquivo de dados para inferência não encontrado em: {data_path}"
        )

    df = pd.read_csv(data_path)
    logger.info(f"Dados carregados. Linhas: {df.shape[0]}, Colunas: {df.shape[1]}")

    # Preservar o DataFrame original para anexar os resultados
    df_scored = df.copy()

    # 2. Carregar o modelo
    pipeline = load_trained_pipeline(model_path)

    # 3. Gerar previsões de probabilidade para a classe positiva (1 - Detrator)
    logger.info("Executando inferência preditiva...")

    # predict_proba retorna [prob_classe_0, prob_classe_1]
    probabilities = pipeline.predict_proba(df)
    detractor_probs = probabilities[:, 1]

    # 4. Acoplar resultados e faixas de risco
    df_scored["detractor_probability"] = detractor_probs
    df_scored["risk_band"] = df_scored["detractor_probability"].apply(
        categorize_risk_band
    )

    # 5. Ordenar por prioridade de risco e maior probabilidade.
    logger.info("Segmentando e priorizando a fila de risco operacional...")
    risk_order = {"Risco Crítico": 0, "Alto Risco": 1, "Baixo Risco": 2}
    df_scored["risk_priority"] = df_scored["risk_band"].map(risk_order)

    df_scored = df_scored.sort_values(
        by=["risk_priority", "detractor_probability"], ascending=[True, False]
    ).drop(columns=["risk_priority"])

    # Exibir resumo das faixas de risco geradas
    risk_summary = df_scored["risk_band"].value_counts()
    logger.info("Distribuição de Faixas de Risco geradas:", risk_summary)

    # 6. Salvar base pontuada
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df_scored.to_csv(output_path, index=False)
    logger.info(f"Base escorada e priorizada salva com sucesso em: {output_path}")

    return df_scored


if __name__ == "__main__":
    import sys

    # Ajustar o path para que localize src se executado direto
    sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
    from src import config

    # Configuração dos caminhos padrão
    default_input = config.DATA_DIR / "raw" / "desafio_nps_fase_1.csv"
    default_model = config.MODELS_DIR / "detractor_classifier.joblib"
    default_output = config.DATA_DIR / "processed" / "scored_orders.csv"

    # Permite execução via CLI ou chamada direta padrão
    parser = argparse.ArgumentParser(
        description="Motor de Escoragem e Classificação de Risco NPS."
    )
    parser.add_argument(
        "--input",
        type=str,
        default=str(default_input),
        help="Caminho do arquivo de entrada.",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=str(default_model),
        help="Caminho do arquivo do modelo serializado.",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=str(default_output),
        help="Caminho do arquivo de saída.",
    )
    args = parser.parse_args()

    try:
        run_inference(
            data_path=Path(args.input),
            model_path=Path(args.model),
            output_path=Path(args.output),
        )
    except Exception as e:
        logger.error(f"Falha na execução do motor de inferência: {e}")
        sys.exit(1)
