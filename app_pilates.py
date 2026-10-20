import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da página
st.set_page_config(
    page_title="Stúdio de Pilates e Fisioterapia Ítalo e Letícia Sampaio",
    page_icon="🧘‍♀️",
    layout="wide"
)

# Título personalizado da Clínica
st.title("🧘‍♀️ Stúdio de Pilates e Fisioterapia Ítalo e Letícia Sampaio")
st.subheader("Painel de Planejamento e Controle Financeiro")
st.markdown("Ajuste os parâmetros na barra lateral para simular faturamento, custos com professores e margens de lucro.")

# ==============================================================================
# 1. BARRA LATERAL - INPUT DE DADOS VARIÁVEIS
# ==============================================================================
st.sidebar.header("⚙️ Parâmetros do Estúdio")

# Capacidade Física
st.sidebar.subheader("1. Estrutura e Capacidade")
vagas_por_turma = st.sidebar.number_input("Alunos/Vagas por Turma", min_value=1, max_value=10, value=4)
horas_por_dia = st.sidebar.number_input("Horas de Aula por Dia", min_value=1, max_value=18, value=10)
dias_por_semana = st.sidebar.number_input("Dias de Funcionamento/Semana", min_value=1, max_value=7, value=5)

# Custos e Equipe
st.sidebar.subheader("2. Custos e Comissão de Professores")
comissao_prof_hora = st.sidebar.number_input("Comissão do Professor (R$/hora de aula)", min_value=0.0, value=45.0, step=5.0)
custos_fixos = st.sidebar.number_input("Custos Fixos Mensais (Aluguel, Luz, Mkt, etc.) (R$)", min_value=0.0, value=8000.0, step=500.0)
imposto_pct = st.sidebar.slider("Imposto / Simples Nacional (%)", min_value=0.0, max_value=20.0, value=6.0) / 100

# Preços dos Planos
st.sidebar.subheader("3. Preços dos Planos (Mensalidade/Aluno)")
preco_1x = st.sidebar.number_input("Plano 1x por semana (R$)", value=250.0, step=10.0)
preco_2x = st.sidebar.number_input("Plano 2x por semana (R$)", value=380.0, step=10.0)
preco_3x = st.sidebar.number_input("Plano 3x por semana (R$)", value=480.0, step=10.0)

# ==============================================================================
# 2. CÁLCULOS BASE E CENÁRIOS DINÂMICOS
# ==============================================================================
aulas_semanais = horas_por_dia * dias_por_semana
aulas_mensais = aulas_semanais * 4.33  # Média de semanas no mês
capacidade_slots_semanais = aulas_semanais * vagas_por_turma

# Custo total da hora/aula do professor no mês
custo_professores_mes = aulas_mensais * comissao_prof_hora

# Cenários proporcionais à capacidade de vagas do estúdio (Reação dinâmica)
cenarios = [
    {
        "Nome": "1. Baixa Ocupação (~30%)", 
        "Alunos_1x": int(capacidade_slots_semanais * 0.1), 
        "Alunos_2x": int(capacidade_slots_semanais * 0.15), 
        "Alunos_3x": int(capacidade_slots_semanais * 0.05)
    },
    {
        "Nome": "2. Ponto de Equilíbrio (~55%)", 
        "Alunos_1x": int(capacidade_slots_semanais * 0.15), 
        "Alunos_2x": int(capacidade_slots_semanais * 0.25), 
        "Alunos_3x": int(capacidade_slots_semanais * 0.15)
    },
    {
        "Nome": "3. Alta Ocupação (~85%)", 
        "Alunos_1x": int(capacidade_slots_semanais * 0.2), 
        "Alunos_2x": int(capacidade_slots_semanais * 0.4), 
        "Alunos_3x": int(capacidade_slots_semanais * 0.25)
    },
    {
        "Nome": "4. Capacidade Máxima (100%)", 
        "Alunos_1x": int(capacidade_slots_semanais * 0.2), 
        "Alunos_2x": int(capacidade_slots_semanais * 0.5), 
        "Alunos_3x": int(capacidade_slots_semanais * 0.3)
    }
]

dados_resultados = []

for c in cenarios:
    total_alunos = c["Alunos_1x"] + c["Alunos_2x"] + c["Alunos_3x"]
    slots_ocupados = (c["Alunos_1x"] * 1) + (c["Alunos_2x"] * 2) + (c["Alunos_3x"] * 3)
    taxa_ocupacao = (slots_ocupados / capacidade_slots_semanais) * 100 if capacidade_slots_semanais > 0 else 0
    
    # Faturamento Bruto
    fat_bruto = (c["Alunos_1x"] * preco_1x) + (c["Alunos_2x"] * preco_2x) + (c["Alunos_3x"] * preco_3x)
    impostos = fat_bruto * imposto_pct
    
    # Custo Total = Custos Fixos + Impostos + Comissão dos Professores
    custo_total = custos_fixos + impostos + custo_professores_mes
    lucro_liquido = fat_bruto - custo_total
    
    dados_resultados.append({
        "Cenário": c["Nome"],
        "Total Alunos": total_alunos,
        "Ocupação (%)": round(taxa_ocupacao, 1),
        "Faturamento Bruto": fat_bruto,
        "Impostos": impostos,
        "Custo Fixos": custos_fixos,
        "Comissão Professores": custo_professores_mes,
        "Custo Total": custo_total,
        "Lucro Líquido": lucro_liquido,
        "Margem Líquida (%)": round((lucro_liquido / fat_bruto * 100) if fat_bruto > 0 else 0, 1)
    })

df = pd.DataFrame(dados_resultados)

# ==============================================================================
# 3. EXIBIÇÃO DAS MÉTRICAS EM CARDS
# ==============================================================================
m1, m2, m3, m4 = st.columns(4)
m1.metric("Capacidade Máxima de Vagas", f"{capacidade_slots_semanais} vagas/sem")
m2.metric("Custo Mensal Professores", f"R$ {custo_professores_mes:,.2f}")
m3.metric("Faturamento Máximo (100%)", f"R$ {df.iloc[-1]['Faturamento Bruto']:,.2f}")
m4.metric("Lucro Líquido Máximo (100%)", f"R$ {df.iloc[-1]['Lucro Líquido']:,.2f}", 
          delta=f"{df.iloc[-1]['Margem Líquida (%)']}% Margem")

st.divider()

# ==============================================================================
# 4. GRÁFICOS INTERATIVOS
# ==============================================================================
col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    st.subheader("📊 Faturamento Bruto vs. Lucro Líquido por Cenário")
    fig_bar = px.bar(
        df, 
        x="Cenário", 
        y=["Faturamento Bruto", "Lucro Líquido"],
        barmode="group",
        labels={"value": "Valor (R$)", "variable": "Métrica"},
        color_discrete_map={"Faturamento Bruto": "#2b5c8f", "Lucro Líquido": "#2ca02c"}
    )
    st.plotly_chart(fig_bar, width='stretch')

with col_graf2:
    st.subheader("🍩 Composição das Despesas e Custos (Capacidade Máxima)")
    cenario_max = df.iloc[-1]
    labels_custos = ['Custos Fixos', 'Comissão Professores', 'Impostos', 'Lucro Líquido']
    valores_custos = [cenario_max['Custo Fixos'], cenario_max['Comissão Professores'], cenario_max['Impostos'], max(0, cenario_max['Lucro Líquido'])]
    
    fig_pie = px.pie(
        names=labels_custos, 
        values=valores_custos, 
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    st.plotly_chart(fig_pie, width='stretch')

st.divider()

# ==============================================================================
# 5. TABELA DETALHADA
# ==============================================================================
st.subheader("📋 Detalhamento Numérico dos Cenários")

df_display = df.copy()
colunas_moeda = ["Faturamento Bruto", "Impostos", "Custo Fixos", "Comissão Professores", "Custo Total", "Lucro Líquido"]
for col in colunas_moeda:
    df_display[col] = df_display[col].apply(lambda x: f"R$ {x:,.2f}")

df_display["Ocupação (%)"] = df_display["Ocupação (%)"].apply(lambda x: f"{x}%")
df_display["Margem Líquida (%)"] = df_display["Margem Líquida (%)"].apply(lambda x: f"{x}%")

st.dataframe(df_display, width='stretch')