"""
Módulo de Geração de Métricas de Negócio para Apresentação e Storytelling.
Cria tabelas estruturadas de medidas operacionais agrupadas por faixas,
organizadas em 5 dimensões: Comprador, Pedido, Logística, Atendimento e Score.
Ideal para slides executivos e análise de negócio.
"""

import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import config

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def load_processed_data(raw_path: Path = None) -> pd.DataFrame:
    """
    Carrega a base bruta e aplica a preparação operacional necessária antes da geração
    das métricas. O projeto deve usar a base raw como fonte de verdade.
    """
    if raw_path is None:
        raw_path = config.DATA_DIR / "raw" / "desafio_nps_fase_1.csv"

    if not raw_path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {raw_path}")

    from src import dataset

    df = dataset.load_raw_data(raw_path)
    dataset.validate_data(df)
    df = dataset.winsorize_outlier_columns(
        df,
        columns=[
            "customer_service_contacts",
            "delivery_delay_days",
            "complaints_count",
        ],
    )
    df = dataset.binarize_target(df)
    df = dataset.create_business_risk_features(df)

    logger.info(
        f"Dados carregados da base raw: {df.shape[0]} linhas, {df.shape[1]} colunas"
    )
    return df


def create_buyer_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cria métricas da dimensão COMPRADOR com faixas de idade e tempo de relacionamento.

    Args:
        df (pd.DataFrame): DataFrame com dados.

    Returns:
        pd.DataFrame: Tabela com métricas de comprador.
    """
    logger.info("Gerando métricas de COMPRADOR...")

    metrics = []

    # Faixas de Idade
    age_bins = [0, 25, 35, 45, 55, 65, 100]
    age_labels = ["18-25", "26-35", "36-45", "46-55", "56-65", "65+"]
    df["age_group"] = pd.cut(
        df["customer_age"], bins=age_bins, labels=age_labels, right=False
    )

    age_groups = (
        df.groupby("age_group", observed=True)
        .agg({"customer_id": "count", "is_detractor": "mean", "nps_score": "mean"})
        .reset_index()
    )
    age_groups.columns = ["Faixa", "Qtd Clientes", "Taxa Detração", "NPS Médio"]
    age_groups["Dimensão"] = "Comprador"
    age_groups["Métrica"] = "Faixa Etária (anos)"

    metrics.append(age_groups)

    # Faixas de Tempo de Relacionamento
    tenure_bins = [0, 12, 24, 36, 48, 60, 120]
    tenure_labels = [
        "0-1 ano",
        "1-2 anos",
        "2-3 anos",
        "3-4 anos",
        "4-5 anos",
        "5+ anos",
    ]
    df["tenure_group"] = pd.cut(
        df["customer_tenure_months"],
        bins=tenure_bins,
        labels=tenure_labels,
        right=False,
    )

    tenure_groups = (
        df.groupby("tenure_group", observed=True)
        .agg({"customer_id": "count", "is_detractor": "mean", "nps_score": "mean"})
        .reset_index()
    )
    tenure_groups.columns = ["Faixa", "Qtd Clientes", "Taxa Detração", "NPS Médio"]
    tenure_groups["Dimensão"] = "Comprador"
    tenure_groups["Métrica"] = "Tempo de Relacionamento"

    metrics.append(tenure_groups)

    # Faixas por Região
    region_stats = (
        df.groupby("customer_region", observed=True)
        .agg({"customer_id": "count", "is_detractor": "mean", "nps_score": "mean"})
        .reset_index()
    )
    region_stats.columns = ["Faixa", "Qtd Clientes", "Taxa Detração", "NPS Médio"]
    region_stats["Dimensão"] = "Comprador"
    region_stats["Métrica"] = "Região Geográfica"

    metrics.append(region_stats)

    result = pd.concat(metrics, ignore_index=True)
    return result[
        ["Dimensão", "Métrica", "Faixa", "Qtd Clientes", "Taxa Detração", "NPS Médio"]
    ]


def create_order_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cria métricas da dimensão PEDIDO com faixas de valor e quantidade de itens.

    Args:
        df (pd.DataFrame): DataFrame com dados.

    Returns:
        pd.DataFrame: Tabela com métricas de pedido.
    """
    logger.info("Gerando métricas de PEDIDO...")

    metrics = []

    # Faixas de Valor do Pedido
    value_bins = [0, 100, 250, 500, 750, 1000, 2000]
    value_labels = [
        "R$ 0-100",
        "R$ 100-250",
        "R$ 250-500",
        "R$ 500-750",
        "R$ 750-1K",
        "R$ 1K+",
    ]
    df["order_value_group"] = pd.cut(
        df["order_value"], bins=value_bins, labels=value_labels, right=False
    )

    value_groups = (
        df.groupby("order_value_group", observed=True)
        .agg({"order_id": "count", "is_detractor": "mean", "nps_score": "mean"})
        .reset_index()
    )
    value_groups.columns = ["Faixa", "Qtd Pedidos", "Taxa Detração", "NPS Médio"]
    value_groups["Dimensão"] = "Pedido"
    value_groups["Métrica"] = "Faixa de Valor"

    metrics.append(value_groups)

    # Faixas de Quantidade de Itens
    qty_bins = [0, 1, 2, 3, 5, 10, 100]
    qty_labels = [
        "1 item",
        "2 items",
        "3 items",
        "4-5 items",
        "6-10 items",
        "10+ items",
    ]
    df["qty_group"] = pd.cut(
        df["items_quantity"], bins=qty_bins, labels=qty_labels, right=False
    )

    qty_groups = (
        df.groupby("qty_group", observed=True)
        .agg({"order_id": "count", "is_detractor": "mean", "nps_score": "mean"})
        .reset_index()
    )
    qty_groups.columns = ["Faixa", "Qtd Pedidos", "Taxa Detração", "NPS Médio"]
    qty_groups["Dimensão"] = "Pedido"
    qty_groups["Métrica"] = "Quantidade de Itens"

    metrics.append(qty_groups)

    # Faixas de Valor de Frete
    freight_bins = [0, 20, 35, 50, 65, 100]
    freight_labels = ["R$ 0-20", "R$ 20-35", "R$ 35-50", "R$ 50-65", "R$ 65+"]
    df["freight_group"] = pd.cut(
        df["freight_value"], bins=freight_bins, labels=freight_labels, right=False
    )

    freight_groups = (
        df.groupby("freight_group", observed=True)
        .agg({"order_id": "count", "is_detractor": "mean", "nps_score": "mean"})
        .reset_index()
    )
    freight_groups.columns = ["Faixa", "Qtd Pedidos", "Taxa Detração", "NPS Médio"]
    freight_groups["Dimensão"] = "Pedido"
    freight_groups["Métrica"] = "Faixa de Frete"

    metrics.append(freight_groups)

    result = pd.concat(metrics, ignore_index=True)
    return result[
        ["Dimensão", "Métrica", "Faixa", "Qtd Pedidos", "Taxa Detração", "NPS Médio"]
    ]


def create_logistics_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cria métricas da dimensão LOGÍSTICA com faixas de atraso e tentativas de entrega.

    Args:
        df (pd.DataFrame): DataFrame com dados.

    Returns:
        pd.DataFrame: Tabela com métricas de logística.
    """
    logger.info("Gerando métricas de LOGÍSTICA...")

    metrics = []

    # Faixas de Atraso na Entrega (CRÍTICA)
    delay_bins = [-1, 0, 1, 2, 3, 4, 10]
    delay_labels = ["Sem atraso", "1 dia", "2 dias", "3 dias", "4 dias", "5+ dias"]
    df["delay_group"] = pd.cut(
        df["delivery_delay_days"], bins=delay_bins, labels=delay_labels, right=False
    )

    delay_groups = (
        df.groupby("delay_group", observed=True)
        .agg({"order_id": "count", "is_detractor": "mean", "nps_score": "mean"})
        .reset_index()
    )
    delay_groups.columns = ["Faixa", "Qtd Pedidos", "Taxa Detração", "NPS Médio"]
    delay_groups["Dimensão"] = "Logística"
    delay_groups["Métrica"] = "Dias de Atraso"

    metrics.append(delay_groups)

    # Faixas de Tempo de Entrega
    delivery_time_bins = [0, 2, 4, 6, 8, 12]
    delivery_time_labels = ["0-2 dias", "2-4 dias", "4-6 dias", "6-8 dias", "8+ dias"]
    df["delivery_time_group"] = pd.cut(
        df["delivery_time_days"],
        bins=delivery_time_bins,
        labels=delivery_time_labels,
        right=False,
    )

    delivery_time_groups = (
        df.groupby("delivery_time_group", observed=True)
        .agg({"order_id": "count", "is_detractor": "mean", "nps_score": "mean"})
        .reset_index()
    )
    delivery_time_groups.columns = [
        "Faixa",
        "Qtd Pedidos",
        "Taxa Detração",
        "NPS Médio",
    ]
    delivery_time_groups["Dimensão"] = "Logística"
    delivery_time_groups["Métrica"] = "Tempo de Entrega"

    metrics.append(delivery_time_groups)

    # Faixas de Tentativas de Entrega
    attempts_bins = [0, 1, 2, 3, 4, 10]
    attempts_labels = [
        "1 tentativa",
        "2 tentativas",
        "3 tentativas",
        "4 tentativas",
        "5+ tentativas",
    ]
    df["attempts_group"] = pd.cut(
        df["delivery_attempts"], bins=attempts_bins, labels=attempts_labels, right=False
    )

    attempts_groups = (
        df.groupby("attempts_group", observed=True)
        .agg({"order_id": "count", "is_detractor": "mean", "nps_score": "mean"})
        .reset_index()
    )
    attempts_groups.columns = ["Faixa", "Qtd Pedidos", "Taxa Detração", "NPS Médio"]
    attempts_groups["Dimensão"] = "Logística"
    attempts_groups["Métrica"] = "Tentativas de Entrega"

    metrics.append(attempts_groups)

    result = pd.concat(metrics, ignore_index=True)
    return result[
        ["Dimensão", "Métrica", "Faixa", "Qtd Pedidos", "Taxa Detração", "NPS Médio"]
    ]


def create_support_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cria métricas da dimensão ATENDIMENTO com faixas de reclamações e
    tempo de resolução.

    Args:
        df (pd.DataFrame): DataFrame com dados.

    Returns:
        pd.DataFrame: Tabela com métricas de atendimento.
    """
    logger.info("Gerando métricas de ATENDIMENTO...")

    metrics = []

    # Faixas de Quantidade de Reclamações (CRÍTICA)
    complaints_bins = [-1, 0, 2, 4, 6, 8, 12]
    complaints_labels = [
        "0 reclamações",
        "1-2 reclamações",
        "3-4 reclamações",
        "5-6 reclamações",
        "7-8 reclamações",
        "9+ reclamações",
    ]
    df["complaints_group"] = pd.cut(
        df["complaints_count"],
        bins=complaints_bins,
        labels=complaints_labels,
        right=False,
    )

    complaints_groups = (
        df.groupby("complaints_group", observed=True)
        .agg({"order_id": "count", "is_detractor": "mean", "nps_score": "mean"})
        .reset_index()
    )
    complaints_groups.columns = ["Faixa", "Qtd Pedidos", "Taxa Detração", "NPS Médio"]
    complaints_groups["Dimensão"] = "Atendimento"
    complaints_groups["Métrica"] = "Qtd de Reclamações"

    metrics.append(complaints_groups)

    # Faixas de Tempo de Resolução
    resolution_bins = [0, 3, 6, 9, 12]
    resolution_labels = ["0-3 dias", "3-6 dias", "6-9 dias", "9+ dias"]
    df["resolution_group"] = pd.cut(
        df["resolution_time_days"],
        bins=resolution_bins,
        labels=resolution_labels,
        right=False,
    )

    resolution_groups = (
        df.groupby("resolution_group", observed=True)
        .agg({"order_id": "count", "is_detractor": "mean", "nps_score": "mean"})
        .reset_index()
    )
    resolution_groups.columns = ["Faixa", "Qtd Pedidos", "Taxa Detração", "NPS Médio"]
    resolution_groups["Dimensão"] = "Atendimento"
    resolution_groups["Métrica"] = "Tempo de Resolução"

    metrics.append(resolution_groups)

    # Faixas de Contatos com Atendimento
    contacts_bins = [0, 1, 2, 3, 5, 10]
    contacts_labels = [
        "1 contato",
        "2 contatos",
        "3 contatos",
        "4-5 contatos",
        "6+ contatos",
    ]
    df["contacts_group"] = pd.cut(
        df["customer_service_contacts"],
        bins=contacts_bins,
        labels=contacts_labels,
        right=False,
    )

    contacts_groups = (
        df.groupby("contacts_group", observed=True)
        .agg({"order_id": "count", "is_detractor": "mean", "nps_score": "mean"})
        .reset_index()
    )
    contacts_groups.columns = ["Faixa", "Qtd Pedidos", "Taxa Detração", "NPS Médio"]
    contacts_groups["Dimensão"] = "Atendimento"
    contacts_groups["Métrica"] = "Contatos com CS"

    metrics.append(contacts_groups)

    result = pd.concat(metrics, ignore_index=True)
    return result[
        ["Dimensão", "Métrica", "Faixa", "Qtd Pedidos", "Taxa Detração", "NPS Médio"]
    ]


def create_score_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cria métricas da dimensão SCORE com faixas de NPS, CSAT e recompra.

    Args:
        df (pd.DataFrame): DataFrame com dados.

    Returns:
        pd.DataFrame: Tabela com métricas de score.
    """
    logger.info("Gerando métricas de SCORE...")

    metrics = []

    # Faixas de NPS Score
    nps_bins = [-1, 6, 8, 10, 11]
    nps_labels = ["Detrator (0-6)", "Neutro (7-8)", "Promotor (9-10)", "Total"]
    df["nps_category"] = pd.cut(
        df["nps_score"], bins=nps_bins, labels=nps_labels, right=True
    )

    nps_groups = (
        df.groupby("nps_category", observed=True)
        .agg({"order_id": "count", "is_detractor": "mean", "nps_score": "mean"})
        .reset_index()
    )
    nps_groups.columns = ["Faixa", "Qtd Pedidos", "% da Base", "NPS Médio"]
    nps_groups["% da Base"] = (nps_groups["Qtd Pedidos"] / len(df) * 100).round(2)
    nps_groups["Dimensão"] = "Score"
    nps_groups["Métrica"] = "Categoria NPS"

    metrics.append(
        nps_groups[
            ["Dimensão", "Métrica", "Faixa", "Qtd Pedidos", "% da Base", "NPS Médio"]
        ]
    )

    # CSAT Interno
    csat_bins = [0, 4, 6, 8, 11]
    csat_labels = ["Baixo (0-4)", "Médio (5-6)", "Alto (7-8)", "Muito Alto (9-10)"]
    df["csat_category"] = pd.cut(
        df["csat_internal_score"], bins=csat_bins, labels=csat_labels, right=False
    )

    csat_groups = (
        df.groupby("csat_category", observed=True)
        .agg({"order_id": "count", "is_detractor": "mean", "nps_score": "mean"})
        .reset_index()
    )
    csat_groups.columns = ["Faixa", "Qtd Pedidos", "Taxa Detração", "NPS Médio"]
    csat_groups["Dimensão"] = "Score"
    csat_groups["Métrica"] = "CSAT Interno"

    metrics.append(csat_groups)

    # Recompra em 30 dias
    repeat_stats = (
        df.groupby("repeat_purchase_30d", observed=True)
        .agg({"order_id": "count", "is_detractor": "mean", "nps_score": "mean"})
        .reset_index()
    )
    repeat_stats["repeat_purchase_30d"] = repeat_stats["repeat_purchase_30d"].map(
        {0: "Sem recompra (30d)", 1: "Com recompra (30d)"}
    )
    repeat_stats.columns = ["Faixa", "Qtd Pedidos", "Taxa Detração", "NPS Médio"]
    repeat_stats["Dimensão"] = "Score"
    repeat_stats["Métrica"] = "Recompra 30 dias"

    metrics.append(repeat_stats)

    result = pd.concat(metrics, ignore_index=True)
    return result[
        ["Dimensão", "Métrica", "Faixa", "Qtd Pedidos", "Taxa Detração", "NPS Médio"]
    ]


def generate_business_metrics_report(output_path: Path = None) -> pd.DataFrame:
    """
    Gera relatório completo de métricas de negócio com todas as dimensões.

    Args:
        output_path (Path): Caminho para salvar o CSV gerado.

    Returns:
        pd.DataFrame: DataFrame consolidado com todas as métricas.
    """
    logger.info("=" * 70)
    logger.info("GERANDO RELATÓRIO DE MÉTRICAS DE NEGÓCIO")
    logger.info("=" * 70)

    # Carregar dados diretamente da base raw
    df = load_processed_data()

    # Gerar métricas por dimensão
    buyer_metrics = create_buyer_metrics(df)
    order_metrics = create_order_metrics(df)
    logistics_metrics = create_logistics_metrics(df)
    support_metrics = create_support_metrics(df)
    score_metrics = create_score_metrics(df)

    # Consolidar
    all_metrics = pd.concat(
        [
            buyer_metrics,
            order_metrics,
            logistics_metrics,
            support_metrics,
            score_metrics,
        ],
        ignore_index=True,
    )

    # Normalizar números para exibição
    all_metrics["Qtd Clientes"] = all_metrics["Qtd Clientes"].fillna(
        all_metrics["Qtd Pedidos"]
    )
    all_metrics["Taxa Detração"] = (all_metrics["Taxa Detração"] * 100).round(2).astype(
        str
    ) + "%"
    all_metrics["NPS Médio"] = all_metrics["NPS Médio"].round(2)

    # Remover colunas vazias
    all_metrics = all_metrics.dropna(axis=1, how="all")

    # Salvar CSV
    if output_path is None:
        output_path = config.REPORTS_DIR / "business_metrics.csv"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    all_metrics.to_csv(output_path, index=False, encoding="utf-8")
    logger.info(f"✓ Relatório salvo em: {output_path}")

    # Exibir resumo
    logger.info("\n" + "=" * 70)
    logger.info("RESUMO DO RELATÓRIO GERADO")
    logger.info("=" * 70)
    print(all_metrics.to_string(index=False))

    logger.info("\n" + "=" * 70)
    logger.info(f"Total de linhas no relatório: {len(all_metrics)}")
    logger.info(f"Dimensões cobertas: {all_metrics['Dimensão'].nunique()}")
    logger.info("=" * 70)

    return all_metrics


if __name__ == "__main__":
    # Executar geração de relatório
    metrics_df = generate_business_metrics_report()
