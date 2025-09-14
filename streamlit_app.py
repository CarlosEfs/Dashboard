
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import random

# Configuração da página
st.set_page_config(
    page_title="Relatório Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS personalizado para replicar o estilo Looker
st.markdown("""
<style>
    /* Estilo geral */
    .main > div {
        padding-top: 2rem;
    }
    
    /* Header estilo Looker */
    .header-container {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem 2rem;
        border-radius: 8px;
        margin-bottom: 2rem;
        color: white;
    }
    
    .header-title {
        font-size: 2rem;
        font-weight: 600;
        margin: 0;
        color: white;
    }
    
    .header-subtitle {
        font-size: 1rem;
        opacity: 0.9;
        margin: 0;
        color: white;
    }
    
    /* Filtros estilo dropdown */
    .filter-container {
        background-color: #f8f9fa;
        padding: 1rem 2rem;
        border-radius: 8px;
        margin-bottom: 2rem;
        border: 1px solid #e9ecef;
    }
    
    /* Cartões de métricas */
    .metric-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid #e9ecef;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #495057;
        margin: 0;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #6c757d;
        margin: 0.5rem 0 0 0;
    }
    
    /* Estilo das tabelas */
    .stDataFrame {
        border: 1px solid #e9ecef;
        border-radius: 8px;
        overflow: hidden;
    }
    
    .stDataFrame > div {
        border-radius: 8px;
    }
    
    /* Gráficos */
    .chart-container {
        background-color: white;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e9ecef;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Remover padding extra */
    .element-container {
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Função para gerar dados de exemplo (similar ao dashboard mostrado)
@st.cache_data
def gerar_dados_analytics():
    """Gera dados de exemplo para dashboard analytics"""
    np.random.seed(42)
    
    # Categorias (similar ao mostrado na imagem)
    categorias = [
        'Cidades', 'Curiosidades Gerais', 'Notícias', 'Saúde/Bem Estar',
        'Carros/Motos', 'Jardinagem', 'Filmes/Séries/TV', 'Astrologia',
        'Esportes', 'Tecnologia', 'Economia', 'Política', 'Entretenimento'
    ]
    
    sites = [
        'Em Foco', 'Terra Br', 'CB Radar', 'Uni Not', 'Tupi FM',
        'G1 Notícias', 'UOL', 'R7', 'Globo', 'Band'
    ]
    
    gerentes = ['Gabriel', 'Vanessa', 'Núbia', 'Guilherme', 'Ana', 'Carlos']
    
    # Dados de pageviews por categoria
    dados_categoria = []
    for i, categoria in enumerate(categorias):
        pageviews = random.randint(1000000, 100000000)
        dados_categoria.append({
            'rank': i + 1,
            'categoria': categoria,
            'pageviews': pageviews
        })
    
    df_categorias = pd.DataFrame(dados_categoria)
    
    # Dados detalhados de posts
    dados_posts = []
    for i in range(200):  # 200 posts de exemplo
        site = random.choice(sites)
        categoria = random.choice(categorias)
        gerente = random.choice(gerentes)
        
        # Simular título de post
        titulos = [
            f"economia/2025/05/03/fim-de-linha-de-almoco-com-nova-lei-trabalhista",
            f"noticias/2025/brasil-se-despede-de-fabio-de-mello-aos-61-anos",
            f"curiosidades/2025/06/02/grande-rede-de-varejo-falida-fecha-todas-lojas",
            f"saude/2025/o-que-significa-quando-lagartixa-estao-aparecendo-em-casa",
            f"entretenimento/2025/12-nomes-femininos-vintage-dos-anos-50",
            f"tecnologia/2025/05/11/escala-de-trabalho-4x3-foi-aprovada"
        ]
        
        link_post = random.choice(titulos) + f"-{i}"
        pageviews = random.randint(100000, 10000000)
        
        dados_posts.append({
            'link_post': link_post,
            'categoria': categoria,
            'site': site,
            'gerente': gerente,
            'pageviews': pageviews,
            'data': datetime.now() - timedelta(days=random.randint(1, 365))
        })
    
    df_posts = pd.DataFrame(dados_posts)
    
    # Dados para o gráfico de barras (Pageviews por Site e Gerente)
    dados_grafico = []
    for site in sites[:4]:  # Top 4 sites
        for gerente in gerentes[:4]:  # Top 4 gerentes
            pageviews = random.randint(10000000, 100000000)
            dados_grafico.append({
                'site': site,
                'gerente': gerente,
                'pageviews': pageviews
            })
    
    df_grafico = pd.DataFrame(dados_grafico)
    
    return df_categorias, df_posts, df_grafico

# Header principal
st.markdown("""
<div class="header-container">
    <h1 class="header-title">📊 Relatório Analytics</h1>
    <p class="header-subtitle">Dashboard de Performance - Pageviews e Engajamento</p>
</div>
""", unsafe_allow_html=True)

# Carregar dados
df_categorias, df_posts, df_grafico = gerar_dados_analytics()

# Filtros no topo (estilo Looker)
st.markdown('<div class="filter-container">', unsafe_allow_html=True)
col_filtro1, col_filtro2, col_filtro3, col_filtro4 = st.columns([2, 2, 2, 6])

with col_filtro1:
    periodo_selecionado = st.selectbox(
        "📅 Período",
        ["Últimos 7 dias", "Últimos 30 dias", "Últimos 90 dias", "Último ano"],
        index=2
    )

with col_filtro2:
    sites_unicos = df_posts['site'].unique()
    site_selecionado = st.selectbox(
        "🌐 Site",
        ["Todos os sites"] + list(sites_unicos)
    )

with col_filtro3:
    gerentes_unicos = df_posts['gerente'].unique()
    gerente_selecionado = st.selectbox(
        "👤 Gerentes",
        ["Todos os gerentes"] + list(gerentes_unicos)
    )

st.markdown('</div>', unsafe_allow_html=True)

# Métricas principais
total_pageviews = df_posts['pageviews'].sum()
total_posts = len(df_posts)
media_pageviews = df_posts['pageviews'].mean()

col_metric1, col_metric2, col_metric3, col_metric4 = st.columns(4)

with col_metric1:
    st.markdown(f"""
    <div class="metric-card">
        <p class="metric-value">{total_pageviews:,}</p>
        <p class="metric-label">Total Pageviews</p>
    </div>
    """, unsafe_allow_html=True)

with col_metric2:
    st.markdown(f"""
    <div class="metric-card">
        <p class="metric-value">{total_posts:,}</p>
        <p class="metric-label">Total de Posts</p>
    </div>
    """, unsafe_allow_html=True)

with col_metric3:
    st.markdown(f"""
    <div class="metric-card">
        <p class="metric-value">{media_pageviews:,.0f}</p>
        <p class="metric-label">Média por Post</p>
    </div>
    """, unsafe_allow_html=True)

with col_metric4:
    st.markdown(f"""
    <div class="metric-card">
        <p class="metric-value">{len(df_posts['categoria'].unique())}</p>
        <p class="metric-label">Categorias Ativas</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Layout principal com duas colunas
col_left, col_right = st.columns([1.5, 1])

with col_left:
    # Gráfico de Pageviews por Site e Gerente
    st.markdown("### 📊 Pageviews por Site e Gerente")
    
    # Preparar dados para o gráfico
    df_grouped = df_grafico.groupby(['gerente', 'site'])['pageviews'].sum().reset_index()
    
    # Cores para diferentes gerentes
    cores = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD']
    
    fig = go.Figure()
    
    gerentes_graf = df_grouped['gerente'].unique()
    for i, gerente in enumerate(gerentes_graf):
        df_gerente = df_grouped[df_grouped['gerente'] == gerente]
        fig.add_trace(go.Bar(
            name=gerente,
            x=df_gerente['site'],
            y=df_gerente['pageviews'],
            marker_color=cores[i % len(cores)],
            hovertemplate=f"<b>{gerente}</b><br>%{{x}}<br>%{{y:,.0f}} pageviews<extra></extra>"
        ))
    
    fig.update_layout(
        barmode='group',
        height=400,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis_title="Sites",
        yaxis_title="Pageviews",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12)
        yaxis=dict(tickformat=".2s")
    )
    
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    # Tabela de Categorias (estilo da imagem)
    st.markdown("### 📈 Top Categorias por Pageviews")
    
    # Preparar dados da tabela
    df_cat_display = df_categorias.copy()
    df_cat_display['Pageviews'] = df_cat_display['pageviews'].apply(lambda x: f"{x:,}")
    
    # Mostrar tabela estilizada
    st.dataframe(
        df_cat_display[['rank', 'categoria', 'Pageviews']].rename(columns={
            'rank': '#',
            'categoria': 'Categoria',
            'Pageviews': 'Pageviews'
        }),
        use_container_width=True,
        hide_index=True,
        height=400
    )

# Tabela detalhada de posts (parte inferior)
st.markdown("### 📝 Detalhamento de Posts")

# Filtrar dados baseado nas seleções
df_posts_filtrado = df_posts.copy()

if site_selecionado != "Todos os sites":
    df_posts_filtrado = df_posts_filtrado[df_posts_filtrado['site'] == site_selecionado]

if gerente_selecionado != "Todos os gerentes":
    df_posts_filtrado = df_posts_filtrado[df_posts_filtrado['gerente'] == gerente_selecionado]

# Ordenar por pageviews (descendente)
df_posts_filtrado = df_posts_filtrado.sort_values('pageviews', ascending=False)

# Preparar dados para exibição
df_display = df_posts_filtrado.head(50).copy()  # Top 50 posts
df_display['Pageviews'] = df_display['pageviews'].apply(lambda x: f"{x:,}")
df_display['Data'] = df_display['data'].dt.strftime('%d/%m/%Y')

# Adicionar numeração
df_display.reset_index(drop=True, inplace=True)
df_display.index = df_display.index + 1

# Mostrar tabela
st.dataframe(
    df_display[['link_post', 'categoria', 'site', 'Pageviews']].rename(columns={
        'link_post': 'Link do Post',
        'categoria': 'Categoria',
        'site': 'Site',
        'Pageviews': 'Pageviews'
    }),
    use_container_width=True,
    height=400
)

# Footer com informações adicionais
st.markdown("---")
col_footer1, col_footer2, col_footer3 = st.columns(3)

with col_footer1:
    st.markdown(f"**📊 Total de registros:** {len(df_posts_filtrado):,}")

with col_footer2:
    st.markdown(f"**🔥 Maior pageview:** {df_posts_filtrado['pageviews'].max():,}")

with col_footer3:
    st.markdown(f"**📅 Última atualização:** {datetime.now().strftime('%d/%m/%Y %H:%M')}")

# Instruções para uso
with st.expander("ℹ️ Como usar este dashboard"):
    st.markdown("""
    **Filtros disponíveis:**
    - **Período:** Filtra os dados por intervalo de tempo
    - **Site:** Filtra por site específico ou todos os sites
    - **Gerentes:** Filtra por gerente específico ou todos os gerentes
    
    **Visualizações:**
    - **Gráfico de barras:** Mostra pageviews agrupados por site e gerente
    - **Tabela de categorias:** Ranking das categorias mais acessadas
    - **Tabela de posts:** Lista detalhada dos posts com maior engajamento
    
    **Métricas principais:**
    - Total de pageviews, posts, média por post e categorias ativas
    """)
