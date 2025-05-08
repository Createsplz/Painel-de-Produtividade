import json
import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime
import subprocess

# Layout e título
st.set_page_config(page_title="Painel de Produtividade", layout="wide")

with open("custom_style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown("""
    <style>
    .title { font-size: 36px; font-weight: 700; margin-bottom: 10px; }
    .sub { font-size: 22px; color: #888; margin-top: -10px; }
    .top-box {
        border-radius: 16px;
        padding: 16px;
        background: #f9f9f9;
        margin-bottom: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    .metric-box {
        border: 1px solid #e6e6e6;
        border-radius: 10px;
        padding: 15px;
        background-color: #ffffff;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">📊 Painel de Produtividade Gamificado</div>', unsafe_allow_html=True)
st.markdown('<div class="sub">Sistema de pontos baseado em entregas no ClickUp</div>', unsafe_allow_html=True)

# Botão para atualizar dados
if st.button("🔄 Atualizar Dados Agora"):
    with st.spinner("Atualizando tarefas do ClickUp..."):
        subprocess.run(["python3", "clickup_fetcher.py"])
        subprocess.run(["python3", "scoring_logic.py"])
        st.success("✅ Dados atualizados com sucesso!")
        st.rerun()


# Carregar dados
with open("processed_tasks.json") as f:
    data = json.load(f)

df = pd.DataFrame(data)
df["data"] = pd.to_datetime(df["data"])

# Ranking
ranking = df.groupby("responsavel").agg({
    "pontos": "sum",
    "titulo": "count"
}).reset_index().rename(columns={"titulo": "tarefas"})
ranking = ranking.sort_values(by="pontos", ascending=False)

# Tabs
aba = st.tabs(["🏆 Painel Geral", "👤 Painel Individual"])

# ---------------------- GERAL ----------------------
with aba[0]:
    st.markdown("### 🥇 Destaques do Mês")

    col1, col2, col3 = st.columns(3)
    for i, col in zip(range(3), [col1, col2, col3]):
        if i < len(ranking):
            row = ranking.iloc[i]
            emoji = ["🥇", "🥈", "🥉"][i]
            col.markdown(f"""
                <div class="top-box">
                <h4>{emoji} {row['responsavel']}</h4>
                <p><strong>{row['pontos']}</strong> pontos • {row['tarefas']} tarefas</p>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("### 📊 Ranking Completo")
    fig = px.bar(ranking, x="responsavel", y="pontos", text="pontos",
                 title="Pontuação por Colaborador",
                 labels={"responsavel": "Colaborador", "pontos": "Pontos"},
                 color_discrete_sequence=["#66c2a5"])
    fig.update_layout(showlegend=False, height=400)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 📋 Detalhamento em Tabela")
    st.dataframe(ranking.reset_index(drop=True), use_container_width=True)

# ---------------------- INDIVIDUAL ----------------------
with aba[1]:
    colaboradores = sorted(df["responsavel"].unique())
    selecionado = st.selectbox("👤 Selecione o colaborador", colaboradores)

    dados = df[df["responsavel"] == selecionado]
    total_pontos = dados["pontos"].sum()
    total_tarefas = dados.shape[0]
    meta_mensal = 100
    progresso = min(total_pontos / meta_mensal, 1.0)

    st.markdown(f"## 👤 {selecionado}")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f'<div class="metric-box"><h4>🎯 Pontos</h4><h2>{total_pontos}</h2></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-box"><h4>📌 Tarefas</h4><h2>{total_tarefas}</h2></div>', unsafe_allow_html=True)

    st.markdown("### 📈 Progresso até a meta mensal (100 pts)")
    st.progress(progresso)

    st.markdown("### 📋 Tarefas Concluídas")
    st.dataframe(dados[["data", "titulo", "tags", "pontos"]].sort_values(by="data", ascending=False), use_container_width=True)