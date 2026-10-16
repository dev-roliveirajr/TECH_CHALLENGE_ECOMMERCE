# Análise de Negócio: Oportunidade de Ação Proativa no NPS Preditivo

Este documento apresenta a análise de negócio do projeto e conecta a satisfação do cliente aos sinais operacionais disponíveis no e-commerce. O objetivo é identificar fatores associados à detração e avaliar como um score preditivo poderia apoiar a priorização de ações antes da pesquisa de NPS.

## 1. Problema de negócio

O e-commerce observa a satisfação principalmente após o encerramento da jornada, quando o cliente responde à pesquisa. Esse processo é útil para medir a experiência, mas limita a capacidade de antecipar problemas. A proposta deste projeto é transformar informações de pedidos, logística e atendimento em uma estimativa de risco que apoie decisões preventivas.

## 2. A importância do NPS

O NPS pode ser acompanhado em conjunto com indicadores de recompra, retenção, LTV, reclamações, entrega no prazo, SLA e custo de atendimento.

Para o negócio, ele não representa apenas uma avaliação da experiência ao final da jornada; pode funcionar como um indicador antecedente de relacionamento e receita. Clientes satisfeitos tendem a ter maior potencial de retenção e recompra, contribuindo para a redução da dependência de novas aquisições e, consequentemente, do CAC.

A confiança também pode favorecer o boca a boca e a expansão orgânica, enquanto experiências negativas podem enfraquecer o relacionamento e a participação da empresa em um mercado de baixa barreira de entrada.

Por essa razão, o NPS conecta a experiência do cliente a três dimensões estratégicas: **recompra e retenção**, **boca a boca e expansão** e **participação de mercado e vantagem competitiva**. Essas relações são hipóteses de negócio a serem acompanhadas com indicadores próprios; não foram medidas integralmente nesta base.

Nesta base, a recompra em 30 dias foi tratada como informação posterior à jornada e não foi usada como variável de entrada do modelo. Relações com CAC, participação de mercado e reputação externa exigiriam dados adicionais, não disponíveis neste projeto.

## 3. Stakeholders e possíveis usos

O NPS e os sinais operacionais analisados podem apoiar diferentes áreas da empresa. Cada stakeholder pode usar os insights para uma decisão específica:

| Área | Como pode se beneficiar dos insights |
| --- | --- |
| **Logística** | Mapear o impacto real dos atrasos na satisfação e identificar etapas da entrega que precisam de atenção. |
| **Atendimento** | Identificar clientes potencialmente frustrados antes que realizem um novo contato, permitindo organizar a prioridade dos casos. |
| **Pricing** | Avaliar a sensibilidade do cliente ao valor do frete e ao preço do pedido, desde que essas hipóteses sejam complementadas por dados comerciais. |
| **Produto** | Relacionar padrões de detração a possíveis falhas ou defeitos dos itens, caso essas informações sejam incorporadas à base. |
| **Marketing** | Evitar o direcionamento de campanhas ou novas pesquisas a clientes que estejam passando por uma experiência insatisfatória. |
| **Finanças** | Relacionar o NPS à retenção e ao LTV, além de comparar o valor potencial da recuperação com o custo das ações. |

Esses são possíveis usos de negócio derivados da análise. O repositório atual não possui integração com CRM, canais de comunicação, pricing, produto, marketing ou sistemas logísticos; a implementação existente gera o score e a fila de risco para avaliação.

## 4. Definição da target

A variável original de satisfação é `nps_score`, coletada após a experiência de compra ou o encerramento do atendimento. Ela foi escolhida por sintetizar a percepção geral do cliente em uma escala de 0 a 10 e por permitir acompanhar a disposição de recomendação da empresa. **2.075 das 2.500 notas são não inteiras**; por isso, neste projeto a classificação usa limites contínuos:

- **score < 7:** detrator;
- **7 <= score < 9:** neutro;
- **9 <= score <= 10:** promotor.

O projeto adotou uma classificação binária para responder a uma decisão operacional específica: identificar risco de detração. A variável `is_detractor` é criada assim:

- `1`: `nps_score < 7`;
- `0`: `nps_score >= 7`, reunindo neutros e promotores.

Assim, uma nota como 6,9 é detratora; não se deve arredondar a nota antes de classificá-la. Essa escolha simplifica a priorização de casos, mas não substitui a leitura do NPS em suas três categorias. Usar `nps_score` como entrada causaria vazamento, pois a própria target é derivada dessa variável. `repeat_purchase_30d` também é posterior à jornada, e `csat_internal_score` foi excluída porque seu momento de coleta não está documentado. Portanto, o score deve ser gerado após a atualização dos dados operacionais disponíveis e antes da aplicação da pesquisa de NPS; variáveis de atendimento só devem ser usadas se já existirem nesse momento.

## 5. Diagnóstico

A amostra contém **2.500 pedidos** e **19 variáveis originais**. Na validação realizada, não foram encontrados valores ausentes nem duplicidades. Com a classificação por limites contínuos, o NPS observado é **-79,96%**, com **84,36% de detratores (2.109)**, **11,24% de neutros (281)** e **4,40% de promotores (110)**. A nota média é **4,379**. A regra anterior (`score <= 6`) deixava 258 notas entre 6 e 7 fora da classe detratora; todos os indicadores de detração e os artefatos derivados precisam ser recalculados.

### 5.1. Atraso na entrega do pedido

| Faixa de atraso | Pedidos | NPS médio | Detratores |
| --- | ---: | ---: | ---: |
| Sem atraso | 277 | 6,86 | 51,62% |
| 1 a 2 dias | 1.261 | 5,05 | 81,13% |
| 3 a 4 dias | 795 | 3,10 | 97,61% |
| 5 dias ou mais | 167 | 1,28 | 100,00% |

Nesta amostra, a faixa a partir de 3 dias representa um ponto de atenção operacional relevante. O detalhamento estatístico e as visualizações estão em [docs/analise_exploratoria_dados.md](analise_exploratoria_dados.md).

### 5.2. Reclamações recorrentes

| Faixa de reclamações | Pedidos | NPS médio | Detratores |
| --- | ---: | ---: | ---: |
| 0 a 1 | 145 | 7,89 | 28,28% |
| 2 a 3 | 784 | 5,31 | 75,89% |
| 4 a 5 | 1.044 | 3,98 | 91,86% |
| 6 ou mais | 527 | 2,82 | 97,53% |

O aumento da quantidade de reclamações esteve associado a menor NPS e maior proporção de detratores. Essa associação não deve ser interpretada isoladamente como causalidade.

### 5.3. Tempo de resolução do atendimento

| Tempo de resolução | Pedidos | NPS médio | Detratores |
| --- | ---: | ---: | ---: |
| 0 a 2 dias | 629 | 5,04 | 77,74% |
| 3 a 5 dias | 619 | 4,51 | 82,55% |
| 6 a 8 dias | 637 | 4,18 | 86,81% |
| 9 dias ou mais | 615 | 3,78 | 90,41% |

Também foi observada uma elevação gradual da proporção de detratores conforme aumentou o tempo de resolução.

### 5.4. Estrutura do Pedido

| Variável | Faixa observada | Pedidos | NPS médio | Detratores |
| --- | --- | ---: | ---: | ---: |
| Valor do frete | 2,62 a 29,93 | 625 | 4,42 | 84,32% |
| Valor do frete | 46,27 a 76,13 | 624 | 4,21 | 85,42% |
| Valor do pedido | 7,76 a 220,25 | 625 | 4,22 | 86,56% |
| Valor do pedido | 577,29 a 1.983,81 | 625 | 4,56 | 82,40% |
| Parcelas | 1 parcela | 206 | 4,31 | 83,98% |
| Parcelas | 8 parcelas | 209 | 4,50 | 84,21% |

Na estrutura do pedido, os valores apresentaram pouca variação no NPS entre as faixas analisadas.

### 5.5. Perfil demográfico por região

| Região | Pedidos | NPS médio | Detratores |
| --- | ---: | ---: | ---: |
| Sul | 521 | 4,49 | 83,30% |
| Nordeste | 485 | 4,42 | 85,57% |
| Norte | 506 | 4,38 | 85,18% |
| Sudeste | 520 | 4,37 | 83,65% |
| Centro-Oeste | 468 | 4,21 | 84,19% |

A comparação regional mostrou que a média de NPS e a proporção de detratores são muito semelhantes entre as regiões.

🔍 Para uma visualização mais detalhada dessas medidas, consulte o relatório em `reports/business_metrics.html`.

## 6. Indicadores complementares

Para posicionar os resultados em relação ao mercado, recomenda-se acompanhar:

- **NPS médio do setor:** comparação com benchmarks de e-commerce e varejo digital nacional;
- **SLA logístico da concorrência:** prazos médios praticados por concorrentes diretos na mesma região;
- **OTIF (On-Time In-Full):** proporção de entregas realizadas no prazo e sem avarias;
- **Índices em plataformas públicas:** reputação e resolução em canais externos de atendimento, como o Reclame Aqui.

Também são úteis indicadores internos de recompra, retenção, devoluções, cancelamentos, CSAT, taxa de resposta e custo de atendimento. Esses benchmarks externos não foram incorporados à base atual.

## 7. Ações sugeridas

As ações abaixo são propostas para uma futura implantação e usam os limiares observados ou já definidos no projeto como ponto de partida:

1. **Alertas logísticos:** gerar um alerta quando o atraso observado ou previsto atingir **3 dias**; nessa faixa, a detração observada foi de **96,76%**. A comunicação deve atualizar o prazo e registrar a tratativa.

2. **Priorização de entrega:** encaminhar para avaliação operacional pedidos com **2 ou mais tentativas** de entrega ou atraso previsto, respeitando a capacidade da operação. Esse número é uma regra inicial a ser validada.

3. **Triagem de atendimento:** usar o score para organizar uma fila de recuperação, tratando como prioridade inicial os casos de **Alto Risco (probabilidade > 0,50)** e **Risco Crítico (probabilidade > 0,75)**.

4. **Autonomia do atendimento:** avaliar a autorização para que analistas de atendimento ofereçam descontos ou compensações quando o atraso atingir **3 dias**, sempre com critérios de elegibilidade, limite de custo e aprovação definidos pela empresa.

5. **Monitoramento:** acompanhar a taxa de detratores, o tempo de resolução e o custo das ações por faixa de risco. A efetividade deve ser comparada com um grupo de controle em um teste controlado.

Essas ações são recomendações para investigação e teste. O projeto não implementa integrações com CRM, alertas, compensações ou logística, e a análise histórica não demonstra que essas intervenções causarão aumento do NPS.

## 8. Limitações

- A base não contém datas, SLA prometido, transportadora, categoria de produto, motivo do contato, devolução, cancelamento, taxa de resposta ou custo de intervenção.
- Há um pedido por cliente, o que limita análises de comportamento recorrente individual.
- O estudo não possui validação temporal nem teste prospectivo.
- As probabilidades e os limiares de risco ainda não passaram por calibração específica de custo-benefício.
- O viés de autoseleção da pesquisa pode limitar a generalização para clientes que não responderam ao NPS.

## 9. Conclusão

Na amostra analisada, atrasos, reclamações e tempo de resolução apresentaram relação mais evidente com a detração do que as variáveis demográficas avaliadas. A classificação binária pode apoiar uma fila de priorização, desde que seja validada com dados novos, supervisão humana e experimento controlado.
