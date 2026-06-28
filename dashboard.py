"""
Dashboard Interativo — Desempenho de Estudantes
================================================
Projeto Final de Estatística — Etapa 3 (Visualização Interativa)

Ferramenta escolhida: Python + Streamlit + Plotly
Base de dados: StudentsPerformance.csv (Kaggle - Students Performance in Exams)

Como executar:
    pip install streamlit plotly pandas
    streamlit run dashboard.py
"""

import importlib.util

import pandas as pd
import plotly.express as px
import streamlit as st

# Linha de tendência (OLS) só é possível se statsmodels estiver instalado
TEM_STATSMODELS = importlib.util.find_spec("statsmodels") is not None

# ----------------------------------------------------------------------------
# Configuração da página
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="Dashboard — Desempenho de Estudantes",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

QUANTITATIVAS = ["Nota Matemática", "Nota Leitura", "Nota Escrita"]


# ----------------------------------------------------------------------------
# Carregamento e tradução dos dados (em cache para performance)
# ----------------------------------------------------------------------------
@st.cache_data
def carregar_dados(caminho: str = "StudentsPerformance.csv") -> pd.DataFrame:
    df = pd.read_csv(caminho)

    # Renomeia colunas para português
    df = df.rename(columns={
        "gender": "Gênero",
        "race/ethnicity": "Etnia",
        "parental level of education": "Escolaridade dos Pais",
        "lunch": "Merenda",
        "test preparation course": "Curso Preparatório",
        "math score": "Nota Matemática",
        "reading score": "Nota Leitura",
        "writing score": "Nota Escrita",
    })

    # Traduz valores das variáveis qualitativas
    df["Gênero"] = df["Gênero"].map({"female": "Feminino", "male": "Masculino"})
    df["Etnia"] = df["Etnia"].map({
        "group A": "Grupo A", "group B": "Grupo B", "group C": "Grupo C",
        "group D": "Grupo D", "group E": "Grupo E"})
    df["Escolaridade dos Pais"] = df["Escolaridade dos Pais"].map({
        "some high school": "Ensino médio incompleto",
        "high school": "Ensino médio",
        "some college": "Superior incompleto",
        "associate's degree": "Tecnólogo",
        "bachelor's degree": "Bacharelado",
        "master's degree": "Mestrado"})
    df["Merenda"] = df["Merenda"].map({
        "standard": "Padrão", "free/reduced": "Gratuita/reduzida"})
    df["Curso Preparatório"] = df["Curso Preparatório"].map({
        "none": "Não fez", "completed": "Concluiu"})

    df["Média Geral"] = df[QUANTITATIVAS].mean(axis=1).round(2)
    return df


df = carregar_dados()

# ----------------------------------------------------------------------------
# Cabeçalho
# ----------------------------------------------------------------------------
st.title("🎓 Dashboard de Desempenho de Estudantes")
st.markdown(
    "Dashboard interativo do projeto de Estatística — base *Students Performance "
    "in Exams* (Kaggle). Use os **filtros na barra lateral** para segmentar a análise."
)

# ----------------------------------------------------------------------------
# Barra lateral — Filtros e segmentações
# ----------------------------------------------------------------------------
st.sidebar.header("🔎 Filtros e Segmentações")

generos = st.sidebar.multiselect(
    "Gênero", options=sorted(df["Gênero"].unique()),
    default=sorted(df["Gênero"].unique()))

etnias = st.sidebar.multiselect(
    "Etnia", options=sorted(df["Etnia"].unique()),
    default=sorted(df["Etnia"].unique()))

escolaridades = st.sidebar.multiselect(
    "Escolaridade dos Pais", options=list(df["Escolaridade dos Pais"].unique()),
    default=list(df["Escolaridade dos Pais"].unique()))

merendas = st.sidebar.multiselect(
    "Merenda", options=sorted(df["Merenda"].unique()),
    default=sorted(df["Merenda"].unique()))

cursos = st.sidebar.multiselect(
    "Curso Preparatório", options=sorted(df["Curso Preparatório"].unique()),
    default=sorted(df["Curso Preparatório"].unique()))

faixa_nota = st.sidebar.slider(
    "Faixa de Média Geral", min_value=0, max_value=100, value=(0, 100), step=1)

st.sidebar.markdown("---")
materia = st.sidebar.selectbox(
    "Matéria em destaque (histograma e rankings)", options=QUANTITATIVAS, index=0)

# Aplicação dos filtros
df_filtrado = df[
    df["Gênero"].isin(generos)
    & df["Etnia"].isin(etnias)
    & df["Escolaridade dos Pais"].isin(escolaridades)
    & df["Merenda"].isin(merendas)
    & df["Curso Preparatório"].isin(cursos)
    & df["Média Geral"].between(faixa_nota[0], faixa_nota[1])
]

if df_filtrado.empty:
    st.warning("⚠️ Nenhum registro corresponde aos filtros selecionados. Ajuste os filtros.")
    st.stop()

# ----------------------------------------------------------------------------
# Indicadores-chave (KPIs)
# ----------------------------------------------------------------------------
st.subheader("📊 Indicadores-Chave (KPIs)")

c1, c2, c3, c4, c5 = st.columns(5)
total = len(df_filtrado)
pct_base = total / len(df) * 100

c1.metric("Alunos (filtro)", f"{total}", f"{pct_base:.0f}% da base")
c2.metric("Média Matemática", f"{df_filtrado['Nota Matemática'].mean():.1f}",
          f"{df_filtrado['Nota Matemática'].mean() - df['Nota Matemática'].mean():+.1f} vs geral")
c3.metric("Média Leitura", f"{df_filtrado['Nota Leitura'].mean():.1f}",
          f"{df_filtrado['Nota Leitura'].mean() - df['Nota Leitura'].mean():+.1f} vs geral")
c4.metric("Média Escrita", f"{df_filtrado['Nota Escrita'].mean():.1f}",
          f"{df_filtrado['Nota Escrita'].mean() - df['Nota Escrita'].mean():+.1f} vs geral")
taxa_aprov = (df_filtrado["Média Geral"] >= 60).mean() * 100
c5.metric("% com Média ≥ 60", f"{taxa_aprov:.1f}%")

st.markdown("---")

# ----------------------------------------------------------------------------
# Linha 1 de gráficos: histograma + pizza
# ----------------------------------------------------------------------------
col_a, col_b = st.columns([3, 2])

with col_a:
    st.markdown(f"#### Distribuição de **{materia}**")
    fig_hist = px.histogram(
        df_filtrado, x=materia, nbins=20, color="Gênero",
        barmode="overlay", opacity=0.7,
        color_discrete_map={"Feminino": "#FF9999", "Masculino": "#66B3FF"})
    fig_hist.add_vline(
        x=df_filtrado[materia].mean(), line_dash="dash", line_color="black",
        annotation_text=f"Média {df_filtrado[materia].mean():.1f}")
    fig_hist.update_layout(yaxis_title="Frequência", bargap=0.05, height=400)
    st.plotly_chart(fig_hist, use_container_width=True)

with col_b:
    st.markdown("#### Composição por Curso Preparatório")
    cont_curso = df_filtrado["Curso Preparatório"].value_counts().reset_index()
    cont_curso.columns = ["Curso Preparatório", "Quantidade"]
    fig_pie = px.pie(
        cont_curso, names="Curso Preparatório", values="Quantidade", hole=0.4,
        color_discrete_sequence=["#99FF99", "#FFCC99"])
    fig_pie.update_traces(textposition="inside", textinfo="percent+label")
    fig_pie.update_layout(height=400)
    st.plotly_chart(fig_pie, use_container_width=True)

# ----------------------------------------------------------------------------
# Linha 2 de gráficos: barras por grupo + dispersão
# ----------------------------------------------------------------------------
col_c, col_d = st.columns(2)

with col_c:
    st.markdown("#### Média das Notas por Segmento")
    segmento = st.selectbox(
        "Segmentar por:",
        ["Gênero", "Curso Preparatório", "Escolaridade dos Pais", "Etnia", "Merenda"],
        key="segmento_barras")
    medias_seg = (
        df_filtrado.groupby(segmento, observed=True)[QUANTITATIVAS]
        .mean().round(2).reset_index()
        .melt(id_vars=segmento, var_name="Prova", value_name="Nota Média"))
    fig_bar = px.bar(
        medias_seg, x=segmento, y="Nota Média", color="Prova",
        barmode="group", text_auto=".1f",
        color_discrete_sequence=["#4C72B0", "#55A868", "#C44E52"])
    fig_bar.update_layout(height=420, xaxis_title="")
    st.plotly_chart(fig_bar, use_container_width=True)

with col_d:
    st.markdown("#### Relação entre duas Notas (dispersão)")
    cx, cy = st.columns(2)
    eixo_x = cx.selectbox("Eixo X", QUANTITATIVAS, index=1, key="disp_x")
    eixo_y = cy.selectbox("Eixo Y", QUANTITATIVAS, index=2, key="disp_y")
    fig_disp = px.scatter(
        df_filtrado, x=eixo_x, y=eixo_y, color="Curso Preparatório",
        opacity=0.6, trendline="ols" if TEM_STATSMODELS else None,
        color_discrete_map={"Concluiu": "#55A868", "Não fez": "#C44E52"})
    if not TEM_STATSMODELS:
        st.caption("💡 Instale `statsmodels` para exibir a linha de tendência.")
    fig_disp.update_layout(height=420)
    st.plotly_chart(fig_disp, use_container_width=True)

# ----------------------------------------------------------------------------
# Tabela de distribuição de frequência + dados brutos
# ----------------------------------------------------------------------------
st.markdown("---")
st.subheader("📋 Tabela de Distribuição de Frequência")

classes = pd.cut(df_filtrado[materia], bins=range(0, 101, 10),
                 right=True, include_lowest=True)
tab = classes.value_counts().sort_index()
tabela_freq = pd.DataFrame({
    "Classe": [str(i) for i in tab.index],
    "Freq. Absoluta (fi)": tab.values,
    "Freq. Relativa (%)": (tab.values / len(df_filtrado) * 100).round(2),
})
tabela_freq["Freq. Acumulada"] = tabela_freq["Freq. Absoluta (fi)"].cumsum()
st.dataframe(tabela_freq, use_container_width=True, hide_index=True)

with st.expander("🔬 Ver dados brutos filtrados"):
    st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
    st.download_button(
        "⬇️ Baixar dados filtrados (CSV)",
        data=df_filtrado.to_csv(index=False).encode("utf-8"),
        file_name="dados_filtrados.csv", mime="text/csv")

st.caption("Projeto Final de Estatística • Dashboard em Python + Streamlit + Plotly")
