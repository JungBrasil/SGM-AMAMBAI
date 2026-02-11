import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px

# --- CONFIGURAÇÃO DA PÁGINA (Deve ser a primeira linha do Streamlit) ---
st.set_page_config(
    page_title="SGC Amambai - Gestão de Contratos",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS PERSONALIZADO (Para dar um visual de Sistema Governamental) ---
st.markdown("""
    <style>
    .main {background-color: #f8f9fa;}
    .stMetric {background-color: white; padding: 15px; border-radius: 10px; box-shadow: 2px 2px 10px rgba(0,0,0,0.1);}
    h1, h2, h3 {color: #2c3e50;}
    .status-ok {color: green; font-weight: bold;}
    .status-atencao {color: orange; font-weight: bold;}
    .status-critico {color: red; font-weight: bold;}
    div[data-testid="stMetricValue"] {font-size: 24px; color: #1f77b4;}
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES AUXILIARES ---
def calcular_status(data_fim):
    if isinstance(data_fim, str):
        data_fim = datetime.strptime(data_fim, "%Y-%m-%d").date()
        
    hoje = datetime.now().date()
    delta = (data_fim - hoje).days
    
    if delta < 0:
        return "VENCIDO", "critico"
    elif delta <= 30:
        return f"CRÍTICO ({delta} dias)", "critico"
    elif delta <= 90:
        return f"ATENÇÃO ({delta} dias)", "atencao"
    else:
        return "VIGENTE", "ok"

# --- SIMULAÇÃO DE BANCO DE DADOS (Persistência na Sessão) ---
if 'contratos' not in st.session_state:
    # Dados iniciais para demonstração
    st.session_state.contratos = pd.DataFrame([
        {
            "id": 1, 
            "objeto": "Pavimentação Asfáltica Vila Limeira", 
            "contratada": "Construtora MS Ltda", 
            "valor": 1500000.00, 
            "data_inicio": datetime(2023, 1, 10).date(), 
            "data_fim": datetime(2024, 5, 15).date(), # Data próxima para gerar alerta
            "tipo": "Obras",
            "fiscal": "João Silva"
        },
        {
            "id": 2, 
            "objeto": "Fornecimento de Merenda Escolar", 
            "contratada": "Alimentos S.A.", 
            "valor": 800000.00, 
            "data_inicio": datetime(2023, 5, 1).date(), 
            "data_fim": datetime(2026, 2, 28).date(), 
            "tipo": "Compras",
            "fiscal": "Maria Oliveira"
        },
        {
            "id": 3, 
            "objeto": "Locação de Impressoras", 
            "contratada": "Tech Print", 
            "valor": 50000.00, 
            "data_inicio": datetime(2022, 1, 1).date(), 
            "data_fim": datetime(2024, 3, 20).date(), # Data crítica
            "tipo": "Serviços",
            "fiscal": "Carlos Souza"
        },
    ])

# --- BARRA LATERAL (MENU) ---
with st.sidebar:
    st.title("🏛️ SGC Amambai")
    st.markdown("### Controladoria Geral")
    menu = st.radio("Navegação", ["Dashboard", "Cadastrar Contrato", "Gestão de Aditivos", "Relatórios"])
    st.divider()
    st.info("Sistema em conformidade com a Lei 14.133/2021")

# --- PÁGINA: DASHBOARD ---
if menu == "Dashboard":
    st.title("📊 Painel de Controle - Obras e Serviços")
    st.markdown("Visão geral da carteira de contratos do município.")
    
    df = st.session_state.contratos.copy()
    
    # Processando status
    status_list = []
    cor_list = []
    for dt in df['data_fim']:
        s, c = calcular_status(dt)
        status_list.append(s)
        cor_list.append(c)
    
    df['Status'] = status_list
    df['Cor'] = cor_list
    
    # Métricas de Topo
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total de Contratos", len(df))
    col2.metric("Valor Total Gerido", f"R$ {df['valor'].sum():,.2f}")
    
    criticos = df[df['Cor'] == 'critico'].shape[0]
    atencao = df[df['Cor'] == 'atencao'].shape[0]
    
    col3.metric("Contratos Críticos (<30 dias)", criticos, delta=-criticos, delta_color="inverse")
    col4.metric("Contratos em Atenção (30-90 dias)", atencao, delta=-atencao, delta_color="inverse")
    
    st.divider()
    
    # Gráficos
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Distribuição por Tipo")
        fig_pizza = px.pie(df, names='tipo', values='valor', title='Valor por Modalidade')
        st.plotly_chart(fig_pizza, use_container_width=True)
        
    with c2:
        st.subheader("Vencimentos por Mês")
        df['Mes_Vencimento'] = pd.to_datetime(df['data_fim']).dt.strftime('%Y-%m')
        vencimentos = df.groupby('Mes_Vencimento').size().reset_index(name='Contagem')
        fig_bar = px.bar(vencimentos, x='Mes_Vencimento', y='Contagem', title='Cronograma de Vencimentos')
        st.plotly_chart(fig_bar, use_container_width=True)

    # Semáforo de Prazos (Tabela)
    st.subheader("🚦 Semáforo de Vencimentos Detalhado")
    st.info("Atenção: Contratos com menos de 90 dias exigem ação imediata (Aditivo ou Nova Licitação).")
    
    # Estilizando a tabela
    def highlight_rows(row):
        if "CRÍTICO" in row['Status'] or "VENCIDO" in row['Status']:
            return ['background-color: #ffcccc; color: black'] * len(row)
        elif "ATENÇÃO" in row['Status']:
            return ['background-color: #fff4cc; color: black'] * len(row)
        return [''] * len(row)

    st.dataframe(
        df[['objeto', 'contratada', 'data_fim', 'Status', 'valor', 'fiscal']].style.apply(highlight_rows, axis=1).format({"valor": "R$ {:,.2f}"}),
        use_container_width=True,
        height=400
    )

# --- PÁGINA: CADASTRAR CONTRATO ---
elif menu == "Cadastrar Contrato":
    st.title("📝 Novo Instrumento Contratual")
    st.markdown("Cadastro de novos contratos, atas ou convênios.")
    
    with st.form("form_contrato", clear_on_submit=True):
        col1, col2 = st.columns(2)
        objeto = col1.text_input("Objeto do Contrato *")
        contratada = col2.text_input("Empresa Contratada *")
        
        col3, col4, col5 = st.columns(3)
        valor = col3.number_input("Valor Global (R$)", min_value=0.0, step=1000.0)
        dt_inicio = col4.date_input("Data Início")
        dt_fim = col5.date_input("Data Fim (Vigência) *")
        
        col6, col7 = st.columns(2)
        tipo = col6.selectbox("Tipo de Instrumento", ["Obras", "Serviços", "Compras", "Locação", "Credenciamento"])
        fiscal = col7.text_input("Fiscal do Contrato")
        
        submitted =
