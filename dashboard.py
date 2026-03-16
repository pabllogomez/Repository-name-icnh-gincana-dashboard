import streamlit as st
import pandas as pd
import plotly.express as px

# CONFIGURAÇÃO
st.set_page_config(
    page_title="Gincana ICNH",
    page_icon="🏆",
    layout="wide"
)

# ID da planilha
SHEET_ID = "1baQ45Hd6-4BYLP6dDx7KX8zOknbPO2td5Y37KFbBWjw"

url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

# CARREGAR DADOS
df = pd.read_csv(url)

df["Data"] = pd.to_datetime(df["Data"], dayfirst=True)

df["Trimestre"] = df["Data"].dt.quarter

df["TrimestreNome"] = df["Trimestre"].map({
    1: "1° Trimestre",
    2: "2° Trimestre",
    3: "3° Trimestre",
    4: "4° Trimestre"
})

TRIMESTRE_ATUAL = pd.Timestamp.now().quarter

# TÍTULO
st.title("🏆 Gincana ICNH")

# ABAS
tab1, tab2, tab3, tab4 = st.tabs([
    "🏅 Ranking Atual",
    "📜 Histórico",
    "📊 Gráficos",
    "🎯 Tipos de Pontos"
])

# -----------------------------
# TAB 1 - RANKING GERAL
# -----------------------------
with tab1:

    col1, col2, col3 = st.columns(3)

    col1.metric("🎯 Pontos Totais", int(df["Pontos"].sum()))
    col2.metric("👥 Participantes", df["Nome"].nunique())
    col3.metric("🏳️ Grupos", df["Grupo"].nunique())

    st.divider()

    st.subheader("👤 Ranking Individual (Ano)")

    ranking_individual = df.groupby(
        ["Nome","Grupo"]
    )["Pontos"].sum().reset_index()

    ranking_individual = ranking_individual.sort_values(
        "Pontos",
        ascending=False
    )

    st.dataframe(ranking_individual, use_container_width=True)

    st.subheader("🏆 Pódio")

    top3 = ranking_individual.head(3)

    col1, col2, col3 = st.columns(3)

    if len(top3) > 0:
        col1.metric("🥇 1º Lugar", top3.iloc[0]["Nome"], int(top3.iloc[0]["Pontos"]))

    if len(top3) > 1:
        col2.metric("🥈 2º Lugar", top3.iloc[1]["Nome"], int(top3.iloc[1]["Pontos"]))

    if len(top3) > 2:
        col3.metric("🥉 3º Lugar", top3.iloc[2]["Nome"], int(top3.iloc[2]["Pontos"]))

    st.divider()

    st.subheader("👥 Ranking de Grupos")

    ranking_grupos = df.groupby(
        "Grupo"
    )["Pontos"].sum().reset_index()

    ranking_grupos = ranking_grupos.sort_values(
        "Pontos",
        ascending=False
    )

    st.dataframe(ranking_grupos, use_container_width=True)

# -----------------------------
# TAB 2 - HISTÓRICO
# -----------------------------
with tab2:

    st.subheader("📜 Resultados por Trimestre")

    historico = df.groupby(
        ["TrimestreNome","Grupo"]
    )["Pontos"].sum().reset_index()

    trimestres = historico["TrimestreNome"].unique()

    for trimestre in sorted(trimestres):

        bloco = historico[historico["TrimestreNome"] == trimestre]

        bloco = bloco.sort_values("Pontos", ascending=False)

        st.markdown(f"### 🏆 {trimestre}")

        campeao = bloco.iloc[0]

        st.success(
            f"🥇 Campeão: {campeao['Grupo']} — {campeao['Pontos']} pontos"
        )

        for i, row in bloco.iterrows():

            grupo = row["Grupo"]
            pontos = row["Pontos"]

            st.write(f"{grupo} — {pontos} pontos")

        st.divider()

# -----------------------------
# TAB 3 - GRÁFICOS
# -----------------------------
with tab3:

    st.subheader("📊 Comparação entre Grupos")

    grupo_total = df.groupby(
        "Grupo"
    )["Pontos"].sum().reset_index()

    fig = px.bar(
        grupo_total,
        x="Grupo",
        y="Pontos",
        color="Grupo",
        text="Pontos"
    )

    fig.update_traces(textposition="outside")

    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    st.subheader("📈 Evolução por Trimestre")

    trimestre_grupo = df.groupby(
        ["TrimestreNome","Grupo"]
    )["Pontos"].sum().reset_index()

    fig2 = px.line(
        trimestre_grupo,
        x="TrimestreNome",
        y="Pontos",
        color="Grupo",
        markers=True
    )

    st.plotly_chart(fig2, use_container_width=True)

# -----------------------------
# TAB 4 - RANKING POR TIPO DE PONTO
# -----------------------------
with tab4:

    st.subheader("🎯 Ranking por Tipo de Pontos")

    if "Descricao" in df.columns:

        tipos_pontos = sorted(df["Descricao"].dropna().unique())

        tipo_selecionado = st.selectbox(
            "Escolha o tipo de pontuação",
            tipos_pontos
        )

        df_tipo = df[df["Descricao"] == tipo_selecionado]

        ranking_tipo = df_tipo.groupby("Nome")["Pontos"].sum().reset_index()

        ranking_tipo = ranking_tipo.sort_values(
            "Pontos",
            ascending=False
        )

        ranking_tipo["Posição"] = range(1, len(ranking_tipo) + 1)

        col1, col2 = st.columns([3,1])

        with col1:

            st.dataframe(
                ranking_tipo,
                use_container_width=True
            )

        with col2:

            st.subheader("🏆 Top 3")

            top3 = ranking_tipo.head(3)

            if len(top3) > 0:
                st.success(f"🥇 {top3.iloc[0]['Nome']} — {top3.iloc[0]['Pontos']} pts")

            if len(top3) > 1:
                st.info(f"🥈 {top3.iloc[1]['Nome']} — {top3.iloc[1]['Pontos']} pts")

            if len(top3) > 2:
                st.warning(f"🥉 {top3.iloc[2]['Nome']} — {top3.iloc[2]['Pontos']} pts")

    else:

        st.warning("Coluna 'Descricao' não encontrada na planilha.")
