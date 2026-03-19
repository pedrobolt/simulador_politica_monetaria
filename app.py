import math
from dataclasses import dataclass

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(
    page_title="Simulador de Política Monetária",
    page_icon="📈",
    layout="wide",
)


@dataclass
class ParametrosSimulacao:
    taxa_neutra: float
    inflacao_meta: float
    inflacao_inicial: float
    juros_inicial: float
    hiato_inicial: float
    choque_demanda: float
    choque_oferta: float
    peso_inflacao: float
    peso_hiato: float
    persistencia_inflacao: float
    sensibilidade_juros: float
    periodos: int


def simular_politica_monetaria(parametros: ParametrosSimulacao) -> pd.DataFrame:
    inflacao = parametros.inflacao_inicial
    juros = parametros.juros_inicial
    hiato = parametros.hiato_inicial

    registros: list[dict] = []

    for periodo in range(1, parametros.periodos + 1):
        desvio_inflacao = inflacao - parametros.inflacao_meta
        juros_recomendado = (
            parametros.taxa_neutra
            + parametros.peso_inflacao * desvio_inflacao
            + parametros.peso_hiato * hiato
        )

        juros = 0.65 * juros + 0.35 * juros_recomendado
        hiato = (
            0.55 * hiato
            - parametros.sensibilidade_juros * (juros - parametros.taxa_neutra)
            + parametros.choque_demanda * math.exp(-periodo / 6)
        )
        inflacao = (
            parametros.persistencia_inflacao * inflacao
            + (1 - parametros.persistencia_inflacao) * parametros.inflacao_meta
            + 0.30 * hiato
            + parametros.choque_oferta * math.exp(-periodo / 5)
        )

        registros.append(
            {
                "Período": periodo,
                "Inflação (%)": round(inflacao, 2),
                "Juros Selic (%)": round(juros, 2),
                "Hiato do Produto (%)": round(hiato, 2),
                "Desvio da Meta (%)": round(inflacao - parametros.inflacao_meta, 2),
            }
        )

    return pd.DataFrame(registros)


def grafico_linhas(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    series = [
        ("Inflação (%)", "#ef4444"),
        ("Juros Selic (%)", "#2563eb"),
        ("Hiato do Produto (%)", "#16a34a"),
    ]

    for coluna, cor in series:
        fig.add_trace(
            go.Scatter(
                x=df["Período"],
                y=df[coluna],
                mode="lines+markers",
                name=coluna,
                line={"width": 3, "color": cor},
                hovertemplate="Período %{x}<br>" + coluna + ": %{y:.2f}<extra></extra>",
            )
        )

    fig.update_layout(
        title="Evolução da política monetária ao longo do tempo",
        hovermode="x unified",
        legend_title="Indicadores",
        template="plotly_white",
        height=460,
    )
    return fig


def grafico_comparativo(df: pd.DataFrame, meta: float) -> go.Figure:
    fig = px.bar(
        df,
        x="Período",
        y=["Inflação (%)", "Juros Selic (%)"],
        barmode="group",
        template="plotly_white",
        title="Comparativo entre inflação e juros por período",
    )
    fig.add_hline(
        y=meta,
        line_dash="dash",
        line_color="#dc2626",
        annotation_text=f"Meta de inflação ({meta:.2f}%)",
        annotation_position="top left",
    )
    fig.update_layout(height=430, legend_title="Séries")
    return fig


def grafico_dispersao(df: pd.DataFrame) -> go.Figure:
    df_plot = df.assign(
        **{
            "Tamanho Juros Selic": df["Juros Selic (%)"].clip(lower=0),
        }
    )

    fig = px.scatter(
        df_plot,
        x="Hiato do Produto (%)",
        y="Inflação (%)",
        size="Tamanho Juros Selic",
        color="Desvio da Meta (%)",
        color_continuous_scale="RdYlGn_r",
        hover_data={
            "Período": True,
            "Juros Selic (%)": ':.2f',
            "Tamanho Juros Selic": False,
        },
        template="plotly_white",
        title="Relação entre hiato do produto, inflação e juros",
    )
    fig.update_layout(height=430)
    return fig


st.title("📊 Simulador de Política Monetária")
st.caption(
    "Simule diferentes cenários de juros, inflação e hiato do produto com visualizações interativas no final da análise."
)

with st.sidebar:
    st.header("Parâmetros do cenário")
    taxa_neutra = st.slider("Taxa neutra (%)", 2.0, 12.0, 5.0, 0.25)
    inflacao_meta = st.slider("Meta de inflação (%)", 2.0, 8.0, 3.0, 0.25)
    inflacao_inicial = st.slider("Inflação inicial (%)", 0.0, 15.0, 5.5, 0.25)
    juros_inicial = st.slider("Juros iniciais (%)", 0.0, 18.0, 9.5, 0.25)
    hiato_inicial = st.slider("Hiato do produto inicial (%)", -6.0, 6.0, -0.5, 0.1)

    st.divider()
    st.subheader("Choques e sensibilidades")
    choque_demanda = st.slider("Choque de demanda", -3.0, 3.0, 0.5, 0.1)
    choque_oferta = st.slider("Choque de oferta", -3.0, 3.0, 0.2, 0.1)
    peso_inflacao = st.slider("Peso da inflação na regra de Taylor", 0.5, 3.0, 1.8, 0.1)
    peso_hiato = st.slider("Peso do hiato na regra de Taylor", 0.0, 2.0, 0.8, 0.1)
    persistencia_inflacao = st.slider("Persistência inflacionária", 0.1, 0.95, 0.65, 0.05)
    sensibilidade_juros = st.slider("Sensibilidade do hiato aos juros", 0.05, 0.8, 0.25, 0.05)
    periodos = st.slider("Número de períodos", 4, 24, 12, 1)

parametros = ParametrosSimulacao(
    taxa_neutra=taxa_neutra,
    inflacao_meta=inflacao_meta,
    inflacao_inicial=inflacao_inicial,
    juros_inicial=juros_inicial,
    hiato_inicial=hiato_inicial,
    choque_demanda=choque_demanda,
    choque_oferta=choque_oferta,
    peso_inflacao=peso_inflacao,
    peso_hiato=peso_hiato,
    persistencia_inflacao=persistencia_inflacao,
    sensibilidade_juros=sensibilidade_juros,
    periodos=periodos,
)

df_resultado = simular_politica_monetaria(parametros)

ultimo = df_resultado.iloc[-1]
col1, col2, col3, col4 = st.columns(4)
col1.metric("Inflação final", f"{ultimo['Inflação (%)']:.2f}%", f"{ultimo['Desvio da Meta (%)']:.2f} p.p.")
col2.metric("Juros finais", f"{ultimo['Juros Selic (%)']:.2f}%")
col3.metric("Hiato final", f"{ultimo['Hiato do Produto (%)']:.2f}%")
col4.metric("Períodos simulados", f"{periodos}")

st.subheader("Tabela de resultados")
st.dataframe(df_resultado, use_container_width=True, hide_index=True)

csv = df_resultado.to_csv(index=False).encode("utf-8")
st.download_button(
    "Baixar resultados em CSV",
    data=csv,
    file_name="simulacao_politica_monetaria.csv",
    mime="text/csv",
)

st.subheader("Gráficos interativos")
aba1, aba2, aba3 = st.tabs([
    "Linhas",
    "Comparativo",
    "Dispersão",
])

with aba1:
    st.plotly_chart(grafico_linhas(df_resultado), use_container_width=True)

with aba2:
    st.plotly_chart(grafico_comparativo(df_resultado, inflacao_meta), use_container_width=True)

with aba3:
    st.plotly_chart(grafico_dispersao(df_resultado), use_container_width=True)

with st.expander("Como interpretar a simulação"):
    st.markdown(
        """
        - **Inflação** mostra a trajetória estimada dos preços em resposta aos choques e à política monetária.
        - **Juros Selic** representa a resposta do Banco Central usando uma regra inspirada em Taylor.
        - **Hiato do produto** indica o nível de aquecimento ou ociosidade da atividade econômica.
        - Use os gráficos para explorar os pontos no tempo, comparar séries e identificar cenários de convergência ou persistência inflacionária.
        """
    )
