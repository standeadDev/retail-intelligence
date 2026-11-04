import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. Configuração da página
st.set_page_config(
    page_title="Retail Intelligence Dashboard",
    page_icon="📊",
    layout="wide"
)

# 2. Função com cache para carregar os dados via CSV (Compatível com Streamlit Cloud)
@st.cache_data
def carregar_dados():
    # Caminhos relativos a partir da raiz do repositório
    caminho_vendas = os.path.join('data', 'processed', 'online_retail_cleaned.csv')
    caminho_rfm = os.path.join('data', 'processed', 'rfm_clientes_segmentados.csv')
    
    df_vendas = pd.read_csv(caminho_vendas, dtype={'InvoiceNo': str, 'StockCode': str})
    df_rfm = pd.read_csv(caminho_rfm)
    
    df_vendas['InvoiceDate'] = pd.to_datetime(df_vendas['InvoiceDate'])
    df_vendas['Ano_Mes'] = df_vendas['InvoiceDate'].dt.to_period('M').astype(str)
    return df_vendas, df_rfm

# Carregar bases de dados
try:
    df_vendas, df_rfm = carregar_dados()
except Exception as e:
    st.error(f"Erro ao carregar os dados. Verifique se os arquivos CSV estão na pasta data/processed/. Detalhes: {e}")
    st.stop()

# 3. Barra Lateral — Filtros Interativos
st.sidebar.header("🔍 Filtros Executivos")

# Filtro de País
paises = ["Todos"] + sorted(df_vendas['Country'].dropna().unique().tolist())
pais_selecionado = st.sidebar.selectbox("Selecione o País:", paises)

# Aplicar Filtro de País
if pais_selecionado != "Todos":
    df_vendas_filtrado = df_vendas[df_vendas['Country'] == pais_selecionado]
else:
    df_vendas_filtrado = df_vendas.copy()

# 4. Título Principal
st.title("📊 Retail Intelligence — Painel Executivo de Vendas e RFM")
st.markdown("---")

# 5. Módulos / Abas do Dashboard
aba1, aba2 = st.tabs(["📈 Visão Geral de Vendas", "👥 Segmentação de Clientes (RFM)"])

# ABA 1: VISÃO GERAL DE VENDAS
with aba1:
    st.subheader("Indicadores Chave de Desempenho (KPIs)")
    
    col1, col2, col3, col4 = st.columns(4)
    total_receita = df_vendas_filtrado['TotalSales'].sum()
    total_pedidos = df_vendas_filtrado['InvoiceNo'].nunique()
    total_clientes = df_vendas_filtrado['CustomerID'].dropna().nunique()
    ticket_medio = total_receita / total_pedidos if total_pedidos > 0 else 0
    
    col1.metric("Receita Total", f"£ {total_receita:,.2f}")
    col2.metric("Total de Pedidos", f"{total_pedidos:,}")
    col3.metric("Clientes Únicos", f"{total_clientes:,}")
    col4.metric("Ticket Médio", f"£ {ticket_medio:,.2f}")
    
    st.markdown("---")
    
    col_left, col_right = st.columns(2)
    
    # Gráfico 1: Evolução Mensal de Vendas
    faturamento_mensal = df_vendas_filtrado.groupby('Ano_Mes')['TotalSales'].sum().reset_index()
    fig_linha = px.line(
        faturamento_mensal, 
        x='Ano_Mes', 
        y='TotalSales',
        title='Evolução do Faturamento Mensal (£)',
        labels={'Ano_Mes': 'Ano-Mês', 'TotalSales': 'Receita (£)'},
        markers=True
    )
    col_left.plotly_chart(fig_linha, use_container_width=True)
    
    # Gráfico 2: Top 5 Países por Faturamento
    top_paises = df_vendas.groupby('Country')['TotalSales'].sum().nlargest(5).reset_index()
    fig_paises = px.bar(
        top_paises,
        x='TotalSales',
        y='Country',
        orientation='h',
        title='Top 5 Países por Receita (£)',
        labels={'TotalSales': 'Receita (£)', 'Country': 'País'},
        color='TotalSales',
        color_continuous_scale='Blues'
    )
    fig_paises.update_layout(yaxis={'categoryorder':'total ascending'})
    col_right.plotly_chart(fig_paises, use_container_width=True)

# ABA 2: SEGMENTAÇÃO RFM
with aba2:
    st.subheader("Análise de Segmentos de Clientes")
    
    col_rfm1, col_rfm2 = st.columns(2)
    
    # Gráfico 3: Distribuição por Segmento RFM
    df_seg_count = df_rfm['Segment'].value_counts().reset_index()
    df_seg_count.columns = ['Segmento', 'Clientes']
    fig_seg = px.bar(
        df_seg_count,
        x='Clientes',
        y='Segmento',
        orientation='h',
        title='Distribuição de Clientes por Segmento',
        color='Clientes',
        color_continuous_scale='Greens'
    )
    fig_seg.update_layout(yaxis={'categoryorder':'total ascending'})
    col_rfm1.plotly_chart(fig_seg, use_container_width=True)
    
    # Gráfico 4: Receita por Segmento RFM
    receita_segmento = df_rfm.groupby('Segment')['Monetary'].sum().reset_index()
    fig_rec_seg = px.pie(
        receita_segmento,
        values='Monetary',
        names='Segment',
        title='Representatividade da Receita por Segmento',
        hole=0.4
    )
    col_rfm2.plotly_chart(fig_rec_seg, use_container_width=True)

st.markdown("---")
st.caption("Desenvolvido por Leonardo Silva | Projeto 001/500 — Retail Intelligence")