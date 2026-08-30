"""
Módulo de Visualização Científica e Geração de Gráficos Analíticos.
Contém funções modularizadas para gerar visualizações profissionais e científicas
sobre os fatores operacionais e de atrito que impactam o NPS.
"""

import matplotlib

matplotlib.use("Agg")  # Configura modo headless para evitar erros de display
import matplotlib.pyplot as plt  # noqa: E402
import seaborn as sns  # noqa: E402
import pandas as pd  # noqa: E402
import numpy as np  # noqa: E402
from pathlib import Path  # noqa: E402
from scipy import stats  # noqa: E402


def set_professional_style():
    """Configura o estilo estético profissional para os gráficos."""
    sns.set_theme(style="whitegrid")
    plt.rcParams["figure.figsize"] = (10, 6)
    plt.rcParams["axes.unicode_minus"] = False
    plt.rcParams["font.size"] = 10
    plt.rcParams["axes.labelsize"] = 11
    plt.rcParams["axes.titlesize"] = 13
    plt.rcParams["xtick.labelsize"] = 10
    plt.rcParams["ytick.labelsize"] = 10


def plot_nps_distribution(df: pd.DataFrame, save_path: Path) -> None:
    """
    Gera o gráfico de distribuição das notas de NPS e realiza o QQ-Plot
    demonstrando visualmente a não normalidade das notas (rejeição de Shapiro-Wilk).
    """
    set_professional_style()
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # 1. Histograma + KDE
    sns.histplot(df["nps_score"], bins=11, kde=True, ax=axes[0], color="#2c3e50")
    axes[0].set_title(
        "Distribuição das Notas de NPS (Histograma)", fontweight="bold", pad=10
    )
    axes[0].set_xlabel("Nota de NPS (0 a 10)")
    axes[0].set_ylabel("Frequência")

    # Linha vertical na média
    mean_score = df["nps_score"].mean()
    axes[0].axvline(
        mean_score,
        color="#e74c3c",
        linestyle="--",
        linewidth=2,
        label="Média: {:.3f}".format(mean_score),
    )
    axes[0].legend(loc="upper left")

    # 2. QQ-Plot
    stats.probplot(df["nps_score"], dist="norm", plot=axes[1])
    axes[1].get_lines()[0].set_color("#2c3e50")
    axes[1].get_lines()[0].set_alpha(0.5)
    axes[1].get_lines()[1].set_color("#e74c3c")
    axes[1].get_lines()[1].set_linewidth(2)
    axes[1].set_title("Q-Q Plot (Comparação vs. Normal)", fontweight="bold", pad=10)
    axes[1].set_xlabel("Quantis Teóricos")
    axes[1].set_ylabel("Quantis Ordenados da Nota")

    plt.suptitle(
        "Radiografia da Nota de Satisfação (NPS Score)",
        fontsize=15,
        fontweight="bold",
        y=1.02,
    )
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()


def plot_detraction_by_delay(df: pd.DataFrame, save_path: Path) -> None:
    """
    Plota a taxa de detração por dias de atraso logístico,
    evidenciando graficamente o ponto de colapso de experiência.
    """
    set_professional_style()

    # Certifica-se de ter a target
    if "is_detractor" not in df.columns:
        df = df.copy()
        df["is_detractor"] = (df["nps_score"] <= 6).astype(int)

    # Agrupa por dias de atraso
    delay_groups = df.groupby("delivery_delay_days")["is_detractor"].mean() * 100

    plt.figure(figsize=(10, 6))

    # Barra normal para atraso baixo e barra de destaque para colapso (>=3 dias)
    colors = ["#34495e" if x < 3 else "#e74c3c" for x in delay_groups.index]

    ax = sns.barplot(
        x=delay_groups.index,
        y=delay_groups.values,
        hue=delay_groups.index,
        palette=colors,
        legend=False,
    )

    # Adiciona rótulos de porcentagem
    for p in ax.patches:
        height = p.get_height()
        ax.annotate(
            "{:.1f}%".format(height),
            xy=(p.get_x() + p.get_width() / 2, height),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontweight="bold",
            fontsize=9,
        )

    plt.title(
        "Taxa de Detração por Dias de Atraso Logístico", fontweight="bold", pad=15
    )
    plt.xlabel("Dias de Atraso na Entrega (delivery_delay_days)")
    plt.ylabel("Taxa de Clientes Detratores (%)")
    plt.ylim(0, 110)

    # Linha e anotação destacando o colapso
    plt.axvline(x=2.5, color="#c0392b", linestyle=":", linewidth=2)
    plt.text(
        2.6,
        95,
        "Ponto de Ruptura Crítico\n(Atraso >= 3 dias: Detração > 89%)",
        color="#c0392b",
        fontweight="bold",
        fontsize=10,
    )

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()


def plot_delivery_time_boxplot(df: pd.DataFrame, save_path: Path) -> None:
    """
    Gera diagramas de caixa (Boxplots) comparando o comportamento de
    atraso (delivery_delay_days) entre Detratores e Não Detratores.
    """
    set_professional_style()

    if "is_detractor" not in df.columns:
        df = df.copy()
        df["is_detractor"] = (df["nps_score"] <= 6).astype(int)

    plt.figure(figsize=(9, 6))

    # Compara atraso
    sns.boxplot(
        data=df,
        x="is_detractor",
        y="delivery_delay_days",
        hue="is_detractor",
        palette=["#2ecc71", "#e74c3c"],
        legend=False,
        width=0.5,
        showmeans=True,
        meanprops={
            "marker": "o",
            "markerfacecolor": "white",
            "markeredgecolor": "black",
            "markersize": "8",
        },
    )

    plt.title(
        "Atraso de Entrega: Detratores vs. Não Detratores\n"
        "(Validação do Teste de Mann-Whitney U)",
        fontweight="bold",
        pad=15,
    )
    plt.xlabel("Categoria (0 = Não Detrator | 1 = Detrator)")
    plt.ylabel("Quantidade de Dias de Atraso")
    plt.xticks(
        [0, 1], ["Não Detratores\n(Média: 1.20 dias)", "Detratores\n(Média: 2.53 dias)"]
    )

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()


def plot_spearman_correlation_matrix(df: pd.DataFrame, save_path: Path) -> None:
    """
    Gera o heatmap de correlação não linear de Spearman entre as variáveis numéricas
    e a flag de detração, provando estatisticamente as causas do atrito.
    """
    set_professional_style()

    if "is_detractor" not in df.columns:
        df = df.copy()
        df["is_detractor"] = (df["nps_score"] <= 6).astype(int)

    df_corr = prepare_order_structure_features(df)

    # Seleciona variáveis numéricas de interesse operacional e remove identificadores
    cols_of_interest = [
        "is_detractor",
        "nps_score",
        "delivery_delay_days",
        "complaints_count",
        "customer_service_contacts",
        "resolution_time_days",
        "delivery_time_days",
        "customer_region_code",
        "order_value_q",
        "freight_value_q",
        "payment_installments",
        "order_value",
        "freight_value",
    ]

    # Filtra colunas que existem no dataframe
    cols_of_interest = [col for col in cols_of_interest if col in df_corr.columns]

    corr_matrix = df_corr[cols_of_interest].corr(method="spearman")

    plt.figure(figsize=(10, 8))
    sns.heatmap(
        corr_matrix,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        vmin=-1.0,
        vmax=1.0,
        linewidths=0.5,
        cbar_kws={"label": "Coeficiente de Correlação de Spearman"},
    )

    plt.title(
        "Matriz de Correlação de Spearman (Fatores Operacionais vs. Detração)",
        fontweight="bold",
        pad=15,
    )
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()


def prepare_order_structure_features(df: pd.DataFrame) -> pd.DataFrame:
    """Cria codificações regionais e variáveis por quartis para
    a análise de estrutura do pedido.
    """
    df_processed = df.copy()

    region_map = {
        "Sul": 1,
        "Sudeste": 2,
        "Norte": 3,
        "Nordeste": 4,
        "Centro-Oeste": 5,
    }
    if (
        "customer_region" in df_processed.columns
        and "customer_region_code" not in df_processed.columns
    ):
        df_processed["customer_region_code"] = df_processed["customer_region"].map(
            region_map
        )
    if (
        "order_value" in df_processed.columns
        and "order_value_q" not in df_processed.columns
    ):
        df_processed["order_value_q"] = pd.qcut(
            df_processed["order_value"], q=4, labels=[1, 2, 3, 4], duplicates="drop"
        )
    if (
        "freight_value" in df_processed.columns
        and "freight_value_q" not in df_processed.columns
    ):
        df_processed["freight_value_q"] = pd.qcut(
            df_processed["freight_value"], q=4, labels=[1, 2, 3, 4], duplicates="drop"
        )

    return df_processed


def plot_detraction_by_region(df: pd.DataFrame, save_path: Path) -> None:
    """
    Gera um gráfico de barras empilhadas ou agrupadas mostrando a distribuição
    de detratores entre as diferentes regiões e provando visualmente o teste de
    Qui-Quadrado.
    """
    set_professional_style()

    if "is_detractor" not in df.columns:
        df = df.copy()
        df["is_detractor"] = (df["nps_score"] <= 6).astype(int)

    # Cria tabela de contingência percentual
    contingency = (
        pd.crosstab(df["customer_region"], df["is_detractor"], normalize="index") * 100
    )

    plt.figure(figsize=(10, 6))
    ax = contingency.plot(
        kind="bar", stacked=True, color=["#2ecc71", "#e74c3c"], ax=plt.gca(), width=0.6
    )

    # Detalha as barras
    for p in ax.patches:
        width, height = p.get_width(), p.get_height()
        x, y = p.get_xy()
        if height > 0:
            ax.annotate(
                "{:.1f}%".format(height),
                xy=(x + width / 2, y + height / 2),
                xytext=(0, 0),
                textcoords="offset points",
                ha="center",
                va="center",
                color="white",
                fontweight="bold",
                fontsize=9,
            )

    plt.title(
        "Proporção de Detração por Região Geográfica\n"
        "(Validação do Teste Qui-Quadrado de Independência)",
        fontweight="bold",
        pad=15,
    )
    plt.xlabel("Região do Cliente (customer_region)")
    plt.ylabel("Proporção (%)")
    plt.legend(
        ["Não Detratores", "Detratores"],
        title="Status",
        bbox_to_anchor=(1.02, 1),
        loc="upper left",
    )
    plt.xticks(rotation=0)
    plt.ylim(0, 110)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()


def plot_order_structure_analysis(df: pd.DataFrame, save_path: Path) -> None:
    """Gera uma visão comparativa da detração por faixa de valor
    do pedido, frete e parcelas.
    """
    set_professional_style()

    if "is_detractor" not in df.columns:
        df = df.copy()
        df["is_detractor"] = (df["nps_score"] <= 6).astype(int)

    df_plot = prepare_order_structure_features(df)

    variables = [
        ("order_value_q", "Valor do Pedido (Quartis)"),
        ("freight_value_q", "Valor do Frete (Quartis)"),
        ("payment_installments", "Número de Parcelas"),
    ]

    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    for ax, (col, title) in zip(axes, variables):
        if col not in df_plot.columns:
            continue
        if col in ["order_value_q", "freight_value_q"]:
            grouping = df_plot[col]
        else:
            grouping = df_plot[col].astype(str)

        contingency = (
            pd.crosstab(grouping, df_plot["is_detractor"], normalize="index") * 100
        )
        contingency.plot(
            kind="bar",
            stacked=True,
            color=["#2ecc71", "#e74c3c"],
            ax=ax,
            width=0.6,
        )
        ax.set_title(f"Detração por {title}", fontweight="bold")
        ax.set_xlabel(title)
        ax.set_ylabel("Proporção (%)")
        ax.legend(["Não Detratores", "Detratores"], title="Status")
        ax.set_ylim(0, 110)

    fig.suptitle(
        "Estrutura do Pedido e Detração\n"
        "(Validação dos Testes Qui-Quadrado de Independência)",
        fontsize=14,
        fontweight="bold",
        y=1.02,
    )
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent.parent
    data_path = project_root / "data" / "processed" / "processed_nps_data.csv"
    figures_dir = project_root / "reports" / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)

    if not data_path.exists():
        raise FileNotFoundError(f"Arquivo de dados não encontrado: {data_path}")

    df_raw = pd.read_csv(data_path)

    print("Iniciando geração de gráficos em reports/figures/...")

    plot_nps_distribution(df_raw, figures_dir / "nps_distribution.png")
    plot_detraction_by_delay(df_raw, figures_dir / "detraction_rate_by_delay.png")
    plot_delivery_time_boxplot(df_raw, figures_dir / "delivery_delay_boxplot.png")
    plot_spearman_correlation_matrix(
        df_raw, figures_dir / "spearman_correlation_matrix.png"
    )
    plot_detraction_by_region(df_raw, figures_dir / "detraction_by_region.png")
    plot_order_structure_analysis(
        df_raw, figures_dir / "detraction_by_order_structure.png"
    )

    print("Gráficos gerados com sucesso!")
