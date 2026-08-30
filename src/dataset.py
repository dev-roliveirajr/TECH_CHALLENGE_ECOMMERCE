"""
Módulo de Ingestão, Validação e Engenharia de Target do Projeto NPS Preditivo.
Contém funções para carregar os dados brutos, validar a integridade da base,
binarizar a variável target (NPS) e criar variáveis categóricas de risco operacional.
"""

import logging
from pathlib import Path
import pandas as pd
import numpy as np

# Configuração de logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def load_raw_data(file_path: Path = None) -> pd.DataFrame:
    """
    Carrega a base de dados original de e-commerce.

    Args:
        file_path (Path, opcional): Caminho completo para o arquivo CSV.
            Se não fornecido, busca no caminho padrão src/config.py.

    Returns:
        pd.DataFrame: DataFrame com os dados brutos carregados.
    """
    if file_path is None:
        # Importação tardia para evitar dependência circular se importado em
        # outros contextos
        from src import config

        file_path = config.DATA_DIR / "raw" / "desafio_nps_fase_1.csv"

    logger.info(f"Carregando dados originais de: {file_path}")
    if not file_path.exists():
        raise FileNotFoundError(
            f"Arquivo de dados brutos não localizado em: {file_path}"
        )

    df = pd.read_csv(file_path)
    logger.info(
        f"Dados carregados com sucesso! Linhas: {df.shape[0]}, Colunas: {df.shape[1]}"
    )
    return df


def validate_data(df: pd.DataFrame) -> None:
    """
    Realiza validações rigorosas de integridade e qualidade de dados na base.
    Lança ValueError se houver violação de consistência.

    Args:
        df (pd.DataFrame): DataFrame a ser validado.
    """
    logger.info("Iniciando validação de consistência e integridade dos dados...")

    # 1. Validação de chaves primárias e unicidade
    if "customer_id" not in df.columns or "order_id" not in df.columns:
        raise ValueError(
            "Colunas essenciais de identificação ('customer_id', 'order_id') ausentes."
        )

    if df["customer_id"].nunique() != len(df):
        raise ValueError(
            "Violação de unicidade: 'customer_id' possui valores duplicados."
        )

    if df["order_id"].nunique() != len(df):
        raise ValueError("Violação de unicidade: 'order_id' possui valores duplicados.")

    # 2. Validação da nota de NPS (nps_score)
    if "nps_score" not in df.columns:
        raise ValueError("Coluna 'nps_score' essencial para a target está ausente.")

    if not df["nps_score"].between(0, 10).all():
        out_of_bounds = df[~df["nps_score"].between(0, 10)]["nps_score"].unique()
        raise ValueError(
            "Violação de limites: 'nps_score' possui valores fora do intervalo "
            f"[0, 10]: {out_of_bounds}"
        )

    # 3. Validação de outras variáveis numéricas contra valores negativos incoerentes
    non_negative_cols = [
        "customer_age",
        "customer_tenure_months",
        "order_value",
        "items_quantity",
        "discount_value",
        "payment_installments",
        "delivery_time_days",
        "delivery_delay_days",
        "freight_value",
        "delivery_attempts",
        "customer_service_contacts",
        "resolution_time_days",
        "complaints_count",
        "csat_internal_score",
    ]

    for col in non_negative_cols:
        if col in df.columns:
            if (df[col] < 0).any():
                neg_count = (df[col] < 0).sum()
                raise ValueError(
                    f"Inconsistência de dados: coluna '{col}' possui "
                    f"{neg_count} valores negativos."
                )

    # 4. Validação da variável binária de recompra
    if "repeat_purchase_30d" in df.columns:
        invalid_binary = df[~df["repeat_purchase_30d"].isin([0, 1])]
        if len(invalid_binary) > 0:
            raise ValueError(
                "Coluna 'repeat_purchase_30d' contém valores inválidos "
                "(esperado apenas 0 ou 1)."
            )

    logger.info(
        "Validação de integridade concluída com sucesso! Todos os testes de "
        "qualidade passaram."
    )


def winsorize_outlier_columns(
    df: pd.DataFrame,
    columns: list[str] | None = None,
    factor: float = 1.5,
) -> pd.DataFrame:
    """
    Aplica winsorização por regra IQR para limitar valores extremos em colunas
    selecionadas, preservando a linha no DataFrame e reduzindo a influência de
    outliers na modelagem e na análise exploratória.

    Args:
        df (pd.DataFrame): DataFrame a ser tratado.
        columns (list[str] | None): Colunas alvo. Se None, aplica às colunas mais
            sensíveis ao problema de negócio.
        factor (float): Multiplicador do IQR para definição dos limites.

    Returns:
        pd.DataFrame: DataFrame com as colunas winsorizadas.
    """
    df = df.copy()

    if columns is None:
        columns = [
            "customer_service_contacts",
            "delivery_delay_days",
            "complaints_count",
        ]

    for col in columns:
        if col not in df.columns:
            continue

        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - factor * iqr
        upper_bound = q3 + factor * iqr

        df[col] = df[col].clip(lower=lower_bound, upper=upper_bound)
        logger.info(
            "Winsorização aplicada em '%s': limites [%.2f, %.2f] usando IQR*%.1f.",
            col,
            lower_bound,
            upper_bound,
            factor,
        )

    return df


def binarize_target(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cria a variável alvo binária 'is_detractor' de acordo com a regra do NPS.
    Detratores (notas de 0 a 6) recebem 1, outros (notas de 7 a 10) recebem 0.

    Args:
        df (pd.DataFrame): DataFrame original.

    Returns:
        pd.DataFrame: DataFrame com a nova coluna 'is_detractor'.
    """
    logger.info("Aplicando engenharia de target (binarização do NPS)...")
    df = df.copy()

    # 1 se nps_score <= 6 (Detrator) e 0 se nps_score > 6 (Não Detrator)
    df["is_detractor"] = (df["nps_score"] <= 6).astype(int)

    prop_detractors = df["is_detractor"].mean() * 100
    logger.info(
        "Binarização concluída. Proporção de Detratores (classe positiva):"
        "{}%".format(prop_detractors)
    )
    return df


def group_delivery_delay(days: float) -> str:
    """Classifica a quantidade de dias de atraso logístico em faixas de risco."""
    if days == 0:
        return "Sem Atraso"
    elif 1 <= days <= 2:
        return "Atraso Baixo (1-2 dias)"
    elif 3 <= days <= 4:
        return "Atraso Médio (3-4 dias)"
    else:
        return "Atraso Crítico (5+ dias)"


def group_contacts(contacts: float) -> str:
    """Classifica contatos com o atendimento em faixas de risco."""
    if contacts == 0:
        return "Sem Contato"
    elif 1 <= contacts <= 2:
        return "Contato Baixo (1-2 contatos)"
    elif 3 <= contacts <= 4:
        return "Contato Médio (3-4 contatos)"
    else:
        return "Contato Alto (5+ contatos)"


def group_support(days: float) -> str:
    """Classifica o tempo de resolução de problemas do suporte em faixas de risco."""
    if days <= 2:
        return "Rápido (0-2 dias)"
    elif 3 <= days <= 5:
        return "Médio (3-5 dias)"
    elif 6 <= days <= 8:
        return "Lento (6-8 dias)"
    else:
        return "Crítico (9+ dias)"


def create_business_risk_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cria variáveis categóricas de risco baseadas nos limites e comportamentos
    operacionais, facilitando análises exploratórias e oferecendo recursos
    adicionais para inteligência de negócios.

    Args:
        df (pd.DataFrame): DataFrame a ser processado.

    Returns:
        pd.DataFrame: DataFrame com as novas colunas de faixas de risco operacional.
    """
    logger.info("Criando faixas categóricas de risco operacional...")
    df = df.copy()

    # Criação das faixas de atraso logístico
    if "delivery_delay_days" in df.columns:
        df["delay_group"] = df["delivery_delay_days"].apply(group_delivery_delay)

    # Criação das faixas de volume de contatos
    if "customer_service_contacts" in df.columns:
        df["contacts_group"] = df["customer_service_contacts"].apply(group_contacts)

    # Criação das faixas de tempo de suporte/resolução
    if "resolution_time_days" in df.columns:
        df["support_group"] = df["resolution_time_days"].apply(group_support)

    logger.info("Novas colunas de faixas criadas com sucesso!")
    return df


if __name__ == "__main__":
    # Testando a execução pontual das funções de ingestão e engenharia de target
    import sys

    sys.path.append(str(Path(__file__).resolve().parent.parent))
    from src import config

    # Cria diretórios processed e interim caso não existam
    (config.DATA_DIR / "processed").mkdir(parents=True, exist_ok=True)
    (config.DATA_DIR / "interim").mkdir(parents=True, exist_ok=True)

    try:
        # Executa o pipeline do dataset
        raw_df = load_raw_data()
        validate_data(raw_df)

        # Tratamento de outliers sensíveis antes de salvar a versão processada
        raw_df = winsorize_outlier_columns(
            raw_df,
            columns=[
                "customer_service_contacts",
                "delivery_delay_days",
                "complaints_count",
            ],
        )

        # Engenharia de Target e Risco
        processed_df = binarize_target(raw_df)
        processed_df = create_business_risk_features(processed_df)

        # Salva em processed/
        output_path = config.DATA_DIR / "processed" / "processed_nps_data.csv"
        processed_df.to_csv(output_path, index=False)
        logger.info(
            f"Pipeline de dados do dataset concluído! Arquivo gerado em: {output_path}"
        )

    except Exception as e:
        logger.error(f"Falha no pipeline de ingestão e validação: {e}")
        sys.exit(1)
