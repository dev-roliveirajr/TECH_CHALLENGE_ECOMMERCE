"""
Gerador de Visualização HTML para Slide de Métricas de Negócio.
Cria uma tabela interativa e visualmente atraente para apresentação.
"""

import sys
from pathlib import Path

import pandas as pd

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import config


def generate_html_metrics_table(csv_path: Path = None, output_path: Path = None) -> str:
    """
    Gera HTML com tabelas elegantes por dimensão.

    Args:
        csv_path (Path): Caminho para o CSV de métricas
        output_path (Path): Caminho para salvar o HTML

    Returns:
        str: HTML gerado
    """
    if csv_path is None:
        csv_path = config.REPORTS_DIR / "business_metrics.csv"

    if output_path is None:
        output_path = config.REPORTS_DIR / "business_metrics.html"

    df = pd.read_csv(csv_path)

    css = """
    <style>
        :root {
            --bg: #f5f7fa;
            --panel: #ffffff;
            --text: #2c3e50;
            --muted: #7f8c8d;
            --border: #e0e0e0;
            --shadow: rgba(0, 0, 0, 0.1);
        }

        * {
            margin: 0;
            padding: 0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        body {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 40px;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: var(--panel);
            border-radius: 12px;
            box-shadow: 0 10px 40px var(--shadow);
            padding: 40px;
        }

        h1 {
            text-align: center;
            color: var(--text);
            margin-bottom: 10px;
            font-size: 32px;
        }

        .subtitle {
            text-align: center;
            color: var(--muted);
            margin-bottom: 40px;
            font-size: 14px;
        }

        .dimension-section {
            margin-bottom: 50px;
        }

        .dimension-title {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 20px;
            border-radius: 8px 8px 0 0;
            font-size: 18px;
            font-weight: bold;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .dimension-title.comprador {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .dimension-title.pedido {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }
        .dimension-title.logistica {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        }
        .dimension-title.atendimento {
            background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        }
        .dimension-title.score {
            background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        }

        .dimension-icon {
            font-size: 20px;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            border-radius: 8px;
            overflow: hidden;
            background: white;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        }

        thead {
            background: #f8f9fa;
        }

        th {
            padding: 14px;
            text-align: left;
            font-weight: 600;
            color: var(--text);
            border-bottom: 2px solid var(--border);
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        td {
            padding: 12px 14px;
            border-bottom: 1px solid #f0f0f0;
            font-size: 13px;
            color: #34495e;
        }

        tbody tr:hover {
            background: #f8f9fa;
            transition: background 0.2s ease;
        }

        tbody tr:last-child td {
            border-bottom: none;
        }

        .metric-name {
            font-weight: 500;
            color: var(--text);
        }

        .faixa {
            color: #555;
            background: #f9f9f9;
            padding: 4px 8px;
            border-radius: 4px;
        }

        .number {
            text-align: right;
            font-family: 'Monaco', 'Courier New', monospace;
            font-weight: 500;
        }

        .detration {
            font-weight: 600;
        }

        .nps {
            font-weight: 600;
            color: #27ae60;
        }

        .low {
            color: #e74c3c;
            font-weight: 600;
        }

        .medium {
            color: #f39c12;
            font-weight: 600;
        }

        .high {
            color: #27ae60;
            font-weight: 600;
        }

        .footer {
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid var(--border);
            color: var(--muted);
            font-size: 12px;
        }
    </style>
    """

    html = (
        "<!DOCTYPE html>\n"
        '<html lang="pt-BR">\n'
        "<head>\n"
        '    <meta charset="UTF-8">\n'
        '    <meta name="viewport" content="width=device-width,\n'
        '        initial-scale=1.0">\n'
        "    <title>Métricas de Negócio - E-commerce NPS</title>\n"
        f"{css}\n"
        "</head>\n"
        "<body>\n"
        '    <div class="container">\n'
        "        <h1>📊 Métricas de Negócio - Base de Dados E-commerce</h1>\n"
        '        <p class="subtitle">\n'
        "            Análise estruturada em 5 dimensões: Comprador, Pedido,\n"
        "            Logística, Atendimento e Score\n"
        "        </p>\n"
    )

    dimensions = {
        "Comprador": ("comprador", "👤"),
        "Pedido": ("pedido", "📦"),
        "Logística": ("logistica", "🚚"),
        "Atendimento": ("atendimento", "💬"),
        "Score": ("score", "⭐"),
    }

    for dim_name, (dim_class, icon) in dimensions.items():
        dim_data = df[df["Dimensão"] == dim_name].copy()

        if dim_data.empty:
            continue

        html += (
            '<div class="dimension-section">\n'
            f'    <div class="dimension-title {dim_class}">\n'
            f'        <span class="dimension-icon">{icon}</span>\n'
            f"        <span>{dim_name.upper()}</span>\n"
            "    </div>\n"
            "    <table>\n"
            "        <thead>\n"
            "            <tr>\n"
            "                <th>Métrica</th>\n"
            "                <th>Faixa</th>\n"
            '                <th class="number">Qtd</th>\n'
            '                <th class="number">Taxa Detração</th>\n'
            '                <th class="number">NPS Médio</th>\n'
            "            </tr>\n"
            "        </thead>\n"
            "        <tbody>\n"
        )

        for metric in dim_data["Métrica"].unique():
            metric_data = dim_data[dim_data["Métrica"] == metric]

            for idx, row in metric_data.iterrows():
                metric_display = row["Métrica"] if idx == metric_data.index[0] else ""

                if pd.notna(row["Taxa Detração"]):
                    taxa_str = str(row["Taxa Detração"]).replace("%", "")
                    try:
                        taxa_float = float(taxa_str)
                    except (TypeError, ValueError):
                        detration_class = "medium"
                    else:
                        if taxa_float > 85:
                            detration_class = "low"
                        elif taxa_float > 70:
                            detration_class = "medium"
                        else:
                            detration_class = "high"
                    detration_value = (
                        f'<span class="{detration_class}">'
                        f'{row["Taxa Detração"]}</span>'
                    )
                else:
                    detration_value = "-"

                if pd.notna(row["NPS Médio"]):
                    nps_value = f'<span class="nps">{row["NPS Médio"]:.2f}' "</span>"
                else:
                    nps_value = "-"

                qtd = (
                    int(row["Qtd Clientes"])
                    if pd.notna(row["Qtd Clientes"])
                    else (
                        int(row["Qtd Pedidos"]) if pd.notna(row["Qtd Pedidos"]) else 0
                    )
                )

                html += (
                    "                    <tr>\n"
                    '                        <td class="metric-name">'
                    f"{metric_display}</td>\n"
                    '                        <td><span class="faixa">'
                    f"{row['Faixa']}</span></td>\n"
                    '                        <td class="number">'
                    f"{format(qtd, ',')}</td>\n"
                    '                        <td class="number">'
                    f"{detration_value}</td>\n"
                    '                        <td class="number">'
                    f"{nps_value}</td>\n"
                    "                    </tr>\n"
                )

        html += "        </tbody>\n" "    </table>\n" "</div>\n"

    html += (
        '    <div class="footer">\n'
        "        <p>Relatório gerado automaticamente a partir dos "
        "dados processados.</p>\n"
        "        <p>Base: 2.500 transações | Período: 2024-2025 | "
        "Fonte: E-commerce</p>\n"
        "    </div>\n"
        "    </div>\n"
        "</body>\n"
        "</html>\n"
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✓ HTML gerado com sucesso: {output_path}")
    return html


if __name__ == "__main__":
    print("🎨 Gerando visualizações de métricas...")
    print()
    generate_html_metrics_table()
    print()
    print("✓ Visualização gerada com sucesso!")
    print("  → HTML: reports/business_metrics.html")
