import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Tentar importar plotly
try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    st.error("⚠️ Plotly não está instalado")
    st.stop()

# Configuração da página
st.set_page_config(
    page_title="Dashboard - Google Sheets",
    page_icon="📊",
    layout="wide"
)

# CSS
st.markdown("""
<style>
    .header {
        background: linear-gradient(90deg, #34A853 0%, #4285F4 100%);
        padding: 2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        text-align: center;
    }
    
    .config-box {
        background: #f0f8ff;
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid #0084ff;
        margin-bottom: 2rem;
    }
    
    .filter-success {
        background: #d4edda;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #c3e6cb;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

def conectar_sheets_simples(url):
    """Método mais simples para conectar ao Google Sheets"""
    try:
        if '/d/' in url:
            sheet_id = url.split('/d/')[1].split('/')[0]
        else:
            st.error("❌ URL inválida. Use o formato completo do Google Sheets")
            return None
        
        urls_tentar = [
            f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0",
            f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv",
        ]
        
        for csv_url in urls_tentar:
            try:
                df = pd.read_csv(csv_url)
                df = df.dropna(how='all')
                df.columns = df.columns.str.strip()
                
                if not df.empty:
                    st.success(f"✅ Conectado com sucesso!")
                    return df
                    
            except Exception as e:
                continue
        
        return None
        
    except Exception as e:
        st.error(f"❌ Erro: {str(e)}")
        return None

@st.cache_data(ttl=300)
def carregar_dados_cached(url):
    return conectar_sheets_simples(url)

def gerar_dados_exemplo():
    """Dados de exemplo"""
    np.random.seed(42)
    data = []
    
    categorias = ['Lei', 'Cidades', 'Notícias', 'Saúde/Bem Estar', 'Carros/Motos']
    sites = ['Terra Brasil', 'Em Foco', 'CB Radar', 'Uni Not']
    gerentes = ['Vanessa', 'Gabriel', 'Núbia', 'Guilherme']
    
    # Criar dados similares ao que você mostrou na imagem
    for i in range(300):
        data.append({
            'Gerentes': random.choice(gerentes),
            'Site': random.choice(sites),
            'Link do Post': f"/2025/02/{random.choice(['mudancas-e-novidades', 'muro-de-pontal', 'lei-das-placas'])}-{i}",
            'Pageviews': random.randint(5000, 50000),
            'Categoria': random.choice(categorias),
            'Palavra-chave': 'None',
            'Mês': random.choice(['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio']),
            'Período': random.choice(['S1', 'S2', 'S3', 'S4'])
        })
    
    return pd.DataFrame(data)

# Header
st.markdown("""
<div class="header">
    <h1>📊 Dashboard Analytics - FILTROS SIMPLES</h1>
    <p>Conecte sua planilha e filtre os dados facilmente</p>
</div>
""", unsafe_allow_html=True)

# Configuração do Google Sheets
st.markdown('<div class="config-box">', unsafe_allow_html=True)
st.markdown("### 🔗 Conectar Google Sheets")

col1, col2 = st.columns([2, 1])

with col1:
    sheets_url = st.text_input(
        "URL da sua planilha:",
        placeholder="https://docs.google.com/spreadsheets/d/SEU_ID_AQUI/edit",
        help="Cole a URL completa da sua planilha pública"
    )

with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 Conectar", type="primary"):
        if sheets_url:
            st.cache_data.clear()
            st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# Tentar carregar dados
df = None
if sheets_url:
    with st.spinner("🔄 Conectando..."):
        df = carregar_dados_cached(sheets_url)

# Se não conseguir, mostrar dados de exemplo
if df is None:
    if sheets_url:
        st.error("Não foi possível conectar. Verifique se a planilha está pública.")
    
    st.info("📋 Usando dados de exemplo (similar aos seus dados)")
    df = gerar_dados_exemplo()

if df is not None and not df.empty:
    
    # FILTROS MUITO SIMPLES NA SIDEBAR
    st.sidebar.markdown("# 🔍 FILTROS")
    
    # Detectar colunas
    colunas = df.columns.tolist()
    
    # FILTRO 1: MÊS (se existir)
    if 'Mês' in df.columns:
        st.sidebar.markdown("### 📅 Filtrar por Mês")
        meses_disponíveis = df['Mês'].unique().tolist()
        meses_selecionados = st.sidebar.multiselect(
            "Escolha os meses:",
            meses_disponíveis,
            default=meses_disponíveis,
            key="filtro_mes"
        )
    else:
        meses_selecionados = []
    
    # FILTRO 2: CATEGORIA (se existir)  
    if 'Categoria' in df.columns:
        st.sidebar.markdown("### 📊 Filtrar por Categoria")
        categorias_disponíveis = df['Categoria'].unique().tolist()
        categorias_selecionadas = st.sidebar.multiselect(
            "Escolha as categorias:",
            categorias_disponíveis,
            default=categorias_disponíveis,
            key="filtro_categoria"
        )
    else:
        categorias_selecionadas = []
    
    # FILTRO 3: GERENTES (se existir)
    if 'Gerentes' in df.columns:
        st.sidebar.markdown("### 👤 Filtrar por Gerente")
        gerentes_disponíveis = df['Gerentes'].unique().tolist()
        gerentes_selecionados = st.sidebar.multiselect(
            "Escolha os gerentes:",
            gerentes_disponíveis,
            default=gerentes_disponíveis,
            key="filtro_gerente"
        )
    else:
        gerentes_selecionados = []
    
    # FILTRO 4: SITE (se existir)
    if 'Site' in df.columns:
        st.sidebar.markdown("### 🌐 Filtrar por Site")
        sites_disponíveis = df['Site'].unique().tolist()
        sites_selecionados = st.sidebar.multiselect(
            "Escolha os sites:",
            sites_disponíveis,
            default=sites_disponíveis,
            key="filtro_site"
        )
    else:
        sites_selecionados = []
        
    # FILTRO 5: PERÍODO (se existir coluna Período)
    if 'Período' in df.columns:
        st.sidebar.markdown("### ⏰ Filtrar por Período")
        periodos_disponíveis = df['Período'].unique().tolist()
        periodos_selecionados = st.sidebar.multiselect(
            "Escolha os períodos:",
            periodos_disponíveis,
            default=periodos_disponíveis,
            key="filtro_periodo",
            help="S1, S2, S3, S4 representam semanas/quinzenas do mês"
        )
    else:
        periodos_selecionados = []
    
    # APLICAR FILTROS DE FORMA SIMPLES
    df_filtrado = df.copy()
    
    # Aplicar cada filtro se tiver dados selecionados
    if meses_selecionados and 'Mês' in df.columns:
        df_filtrado = df_filtrado[df_filtrado['Mês'].isin(meses_selecionados)]
    
    if categorias_selecionadas and 'Categoria' in df.columns:
        df_filtrado = df_filtrado[df_filtrado['Categoria'].isin(categorias_selecionadas)]
        
    if gerentes_selecionados and 'Gerentes' in df.columns:
        df_filtrado = df_filtrado[df_filtrado['Gerentes'].isin(gerentes_selecionados)]
        
    if sites_selecionados and 'Site' in df.columns:
        df_filtrado = df_filtrado[df_filtrado['Site'].isin(sites_selecionados)]

    if periodos_selecionados and 'Período' in df.columns:
    df_filtrado = df_filtrado[df_filtrado['Período'].isin(periodos_selecionados)]
    
    # MOSTRAR STATUS DOS FILTROS
    if len(df_filtrado) != len(df):
        st.markdown(f"""
        <div class="filter-success">
            <strong>✅ FILTROS APLICADOS!</strong><br>
            Mostrando <strong>{len(df_filtrado):,}</strong> de <strong>{len(df):,}</strong> registros
            ({len(df_filtrado)/len(df)*100:.1f}%)
        </div>
        """, unsafe_allow_html=True)
    
    # MÉTRICAS SIMPLES
    if 'Pageviews' in df_filtrado.columns:
        st.markdown("### 📈 Resumo")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total = df_filtrado['Pageviews'].sum()
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: #34A853; margin: 0;">{total:,.0f}</h3>
                <p style="color: #666; margin: 0.5rem 0;">Total Pageviews</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            media = df_filtrado['Pageviews'].mean()
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: #4285F4; margin: 0;">{media:,.0f}</h3>
                <p style="color: #666; margin: 0.5rem 0;">Média</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            maximo = df_filtrado['Pageviews'].max()
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: #EA4335; margin: 0;">{maximo:,.0f}</h3>
                <p style="color: #666; margin: 0.5rem 0;">Máximo</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            registros = len(df_filtrado)
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: #FBBC04; margin: 0;">{registros:,}</h3>
                <p style="color: #666; margin: 0.5rem 0;">Posts</p>
            </div>
            """, unsafe_allow_html=True)
    
    # GRÁFICO SIMPLES
    if 'Categoria' in df_filtrado.columns and 'Pageviews' in df_filtrado.columns:
        st.markdown("### 📊 Pageviews por Categoria")
        
        # Agrupar dados
        df_graf = df_filtrado.groupby('Categoria')['Pageviews'].sum().reset_index()
        df_graf = df_graf.sort_values('Pageviews', ascending=False).head(10)
        
        fig = px.bar(
            df_graf,
            x='Categoria',
            y='Pageviews',
            title="Top 10 Categorias",
            color='Pageviews',
            color_continuous_scale="viridis"
        )
        
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # TABELA DE DADOS
    st.markdown("### 📝 Dados Filtrados")
    
    # Controles de exibição e download
    col_ctrl1, col_ctrl2, col_ctrl3 = st.columns([1, 1, 2])
    
    with col_ctrl1:
        qtd_mostrar = st.selectbox("Mostrar:", [20, 50, 100, "Todos"])
    
    with col_ctrl2:
        # DOWNLOAD CSV
        csv_data = df_filtrado.to_csv(index=False, encoding='utf-8-sig')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Nome inteligente baseado nos filtros
        nome_arquivo = f"dados_filtrados_{timestamp}.csv"
        if meses_selecionados and len(meses_selecionados) < len(df['Mês'].unique() if 'Mês' in df.columns else []):
            meses_str = '_'.join(meses_selecionados)
            nome_arquivo = f"dados_{meses_str}_{timestamp}.csv"
        
        st.download_button(
            label="📥 Baixar CSV",
            data=csv_data,
            file_name=nome_arquivo,
            mime="text/csv",
            help=f"Baixar {len(df_filtrado)} registros filtrados"
        )
    
    with col_ctrl3:
        # Info sobre os filtros aplicados
        filtros_ativos = []
        if meses_selecionados and len(meses_selecionados) < len(df['Mês'].unique() if 'Mês' in df.columns else []):
            filtros_ativos.append(f"Mês: {', '.join(meses_selecionados)}")
        if categorias_selecionadas and len(categorias_selecionadas) < len(df['Categoria'].unique() if 'Categoria' in df.columns else []):
            filtros_ativos.append(f"Categoria: {len(categorias_selecionadas)} selecionadas")
        
        if filtros_ativos:
            st.info(f"🔍 Filtros: {' | '.join(filtros_ativos)}")
    
    # Mostrar tabela
    if qtd_mostrar == "Todos":
        df_mostrar = df_filtrado
    else:
        df_mostrar = df_filtrado.head(qtd_mostrar)
    
    st.dataframe(df_mostrar, use_container_width=True, height=400)
    
    # Footer
    st.markdown("---")
    col_footer1, col_footer2, col_footer3 = st.columns(3)
    
    with col_footer1:
        st.write(f"**📊 Total filtrado:** {len(df_filtrado):,} registros")
    
    with col_footer2:
        st.write(f"**🔗 Fonte:** {'Google Sheets' if sheets_url else 'Dados exemplo'}")
    
    with col_footer3:
        st.write(f"**🕒 Atualizado:** {datetime.now().strftime('%H:%M')}")
