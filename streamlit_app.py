import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Tentar importar plotly com tratamento de erro
try:
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    st.error("⚠️ Plotly não está instalado. Instale com: pip install plotly")
    st.stop()

# Configuração da página
st.set_page_config(
    page_title="Dashboard Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado para replicar o estilo Looker
st.markdown("""
<style>
    .main > div {
        padding-top: 2rem;
    }
    
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
    
    .filter-container {
        background-color: #f8f9fa;
        padding: 1rem 2rem;
        border-radius: 8px;
        margin-bottom: 2rem;
        border: 1px solid #e9ecef;
    }
    
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
    
    .upload-section {
        background-color: #e3f2fd;
        padding: 2rem;
        border-radius: 8px;
        margin-bottom: 2rem;
        border: 2px dashed #2196f3;
        text-align: center;
    }
    
    .stDataFrame {
        border: 1px solid #e9ecef;
        border-radius: 8px;
        overflow: hidden;
    }
    
    .chart-container {
        background-color: white;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e9ecef;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Função para carregar dados de exemplo
@st.cache_data
def gerar_dados_exemplo():
    """Gera dados de exemplo quando não há arquivo carregado"""
    np.random.seed(42)
    random.seed(42)
    
    data = []
    for i in range(1000):
        data.append({
            'data': datetime.now() - timedelta(days=random.randint(0, 365)),
            'categoria': random.choice(['Tecnologia', 'Vendas', 'Marketing', 'RH', 'Financeiro']),
            'produto': random.choice(['Produto A', 'Produto B', 'Produto C', 'Produto D']),
            'regiao': random.choice(['Norte', 'Sul', 'Leste', 'Oeste', 'Centro']),
            'valor': random.uniform(100, 10000),
            'quantidade': random.randint(1, 100),
            'responsavel': random.choice(['João', 'Maria', 'Pedro', 'Ana', 'Carlos'])
        })
    
    return pd.DataFrame(data)

# Função para processar arquivo carregado
def processar_arquivo(arquivo):
    """Processa arquivo CSV ou Excel carregado"""
    try:
        if arquivo.name.endswith('.csv'):
            df = pd.read_csv(arquivo, encoding='utf-8')
        elif arquivo.name.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(arquivo)
        else:
            st.error("⚠️ Formato não suportado. Use arquivos .csv, .xlsx ou .xls")
            return None
            
        return df
    except Exception as e:
        st.error(f"❌ Erro ao carregar arquivo: {str(e)}")
        return None

# Função para detectar colunas por tipo
def detectar_colunas(df):
    """Detecta automaticamente os tipos de colunas"""
    colunas_numericas = df.select_dtypes(include=[np.number]).columns.tolist()
    colunas_data = []
    colunas_texto = []
    
    for col in df.columns:
        # Tentar detectar colunas de data
        if df[col].dtype == 'object':
            try:
                pd.to_datetime(df[col].head(10))
                colunas_data.append(col)
            except:
                colunas_texto.append(col)
    
    return colunas_numericas, colunas_data, colunas_texto

# Header principal
st.markdown("""
<div class="header-container">
    <h1 class="header-title">📊 Dashboard Analytics Personalizado</h1>
    <p class="header-subtitle">Importe seus dados CSV/Excel e crie visualizações interativas</p>
</div>
""", unsafe_allow_html=True)

# Seção de upload de arquivo
st.markdown('<div class="upload-section">', unsafe_allow_html=True)
st.markdown("### 📁 Importar Dados")
st.markdown("Faça upload do seu arquivo CSV ou Excel para começar a análise")

uploaded_file = st.file_uploader(
    "Escolha seu arquivo",
    type=['csv', 'xlsx', 'xls'],
    help="Suporte para arquivos CSV, XLSX e XLS"
)
st.markdown('</div>', unsafe_allow_html=True)

# Carregar dados
if uploaded_file is not None:
    df = processar_arquivo(uploaded_file)
    if df is not None:
        st.success(f"✅ Arquivo '{uploaded_file.name}' carregado com sucesso!")
        st.info(f"📊 Dados carregados: {len(df)} linhas e {len(df.columns)} colunas")
else:
    df = gerar_dados_exemplo()
    st.info("📋 Usando dados de exemplo. Faça upload do seu arquivo para usar dados reais.")

if df is not None:
    # Detectar tipos de colunas
    cols_numericas, cols_data, cols_texto = detectar_colunas(df)
    
    # Mostrar preview dos dados
    with st.expander("👀 Visualizar dados carregados", expanded=False):
        st.dataframe(df.head(10), use_container_width=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write("**Colunas Numéricas:**")
            for col in cols_numericas:
                st.write(f"• {col}")
        
        with col2:
            st.write("**Colunas de Data:**")
            for col in cols_data:
                st.write(f"• {col}")
        
        with col3:
            st.write("**Colunas de Texto:**")
            for col in cols_texto:
                st.write(f"• {col}")

    # Sidebar com configurações
    st.sidebar.header("⚙️ Configurações do Dashboard")
    
    # Seleção de colunas para análise
    if cols_numericas:
        coluna_valor = st.sidebar.selectbox(
            "💰 Coluna de Valor Principal",
            cols_numericas,
            help="Selecione a coluna numérica principal para análise"
        )
    else:
        st.sidebar.warning("⚠️ Nenhuma coluna numérica encontrada")
        coluna_valor = None
    
    if cols_texto:
        coluna_categoria = st.sidebar.selectbox(
            "📊 Coluna de Categoria",
            cols_texto,
            help="Selecione a coluna para agrupar os dados"
        )
    else:
        coluna_categoria = None
    
    if len(cols_texto) > 1:
        coluna_subcategoria = st.sidebar.selectbox(
            "🏷️ Coluna de Subcategoria (Opcional)",
            ["Nenhuma"] + cols_texto,
            help="Selecione uma segunda dimensão para análise"
        )
        if coluna_subcategoria == "Nenhuma":
            coluna_subcategoria = None
    else:
        coluna_subcategoria = None
    
    # Filtros dinâmicos
    st.sidebar.markdown("### 🔍 Filtros")
    
    filtros_ativos = {}
    for col in cols_texto[:3]:  # Primeiras 3 colunas de texto para filtros
        valores_unicos = df[col].unique()
        if len(valores_unicos) <= 50:  # Só mostrar filtro se não tiver muitas opções
            valores_selecionados = st.sidebar.multiselect(
                f"Filtrar por {col}",
                valores_unicos,
                default=valores_unicos
            )
            filtros_ativos[col] = valores_selecionados

    # Aplicar filtros
    df_filtrado = df.copy()
    for col, valores in filtros_ativos.items():
        if valores:  # Se há valores selecionados
            df_filtrado = df_filtrado[df_filtrado[col].isin(valores)]
    
    # Verificar se há dados após filtros
    if df_filtrado.empty:
        st.warning("⚠️ Nenhum dado encontrado com os filtros selecionados.")
        st.stop()
    
    # Métricas principais
    if coluna_valor:
        st.markdown("### 📈 Métricas Principais")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total = df_filtrado[coluna_valor].sum()
            st.markdown(f"""
            <div class="metric-card">
                <p class="metric-value">{total:,.0f}</p>
                <p class="metric-label">Total {coluna_valor}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            media = df_filtrado[coluna_valor].mean()
            st.markdown(f"""
            <div class="metric-card">
                <p class="metric-value">{media:,.0f}</p>
                <p class="metric-label">Média {coluna_valor}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            maximo = df_filtrado[coluna_valor].max()
            st.markdown(f"""
            <div class="metric-card">
                <p class="metric-value">{maximo:,.0f}</p>
                <p class="metric-label">Máximo {coluna_valor}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            registros = len(df_filtrado)
            st.markdown(f"""
            <div class="metric-card">
                <p class="metric-value">{registros:,}</p>
                <p class="metric-label">Total de Registros</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Layout principal
    col_left, col_right = st.columns([1.5, 1])
    
    with col_left:
        if coluna_valor and coluna_categoria:
            st.markdown(f"### 📊 {coluna_valor} por {coluna_categoria}")
            
            # Agrupar dados por categoria
            df_grouped = df_filtrado.groupby(coluna_categoria)[coluna_valor].sum().reset_index()
            df_grouped = df_grouped.sort_values(coluna_valor, ascending=False).head(10)
            
            # Criar gráfico
            if coluna_subcategoria:
                # Gráfico agrupado por subcategoria
                df_grouped_sub = df_filtrado.groupby([coluna_categoria, coluna_subcategoria])[coluna_valor].sum().reset_index()
                fig = px.bar(
                    df_grouped_sub.head(20),
                    x=coluna_categoria,
                    y=coluna_valor,
                    color=coluna_subcategoria,
                    title=f"{coluna_valor} por {coluna_categoria} e {coluna_subcategoria}"
                )
            else:
                # Gráfico simples
                fig = px.bar(
                    df_grouped,
                    x=coluna_categoria,
                    y=coluna_valor,
                    title=f"Top 10 {coluna_categoria} por {coluna_valor}"
                )
            
            fig.update_layout(
                height=400,
                showlegend=True,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("🔧 Configure as colunas na barra lateral para ver os gráficos")
    
    with col_right:
        if coluna_categoria and coluna_valor:
            st.markdown(f"### 📋 Top {coluna_categoria}")
            
            # Criar tabela de ranking
            df_ranking = df_filtrado.groupby(coluna_categoria)[coluna_valor].agg(['sum', 'count']).reset_index()
            df_ranking.columns = [coluna_categoria, 'Total', 'Quantidade']
            df_ranking = df_ranking.sort_values('Total', ascending=False).head(15)
            df_ranking['Ranking'] = range(1, len(df_ranking) + 1)
            
            # Formatar valores
            df_ranking['Total Formatado'] = df_ranking['Total'].apply(lambda x: f"{x:,.0f}")
            
            st.dataframe(
                df_ranking[['Ranking', coluna_categoria, 'Total Formatado', 'Quantidade']].rename(columns={
                    'Total Formatado': f'Total {coluna_valor}',
                    'Quantidade': 'Qtd Registros'
                }),
                use_container_width=True,
                hide_index=True,
                height=400
            )
    
    # Tabela detalhada
    st.markdown("### 📝 Dados Detalhados")
    
    # Opções de exibição
    col_config1, col_config2 = st.columns([1, 3])
    
    with col_config1:
        num_registros = st.selectbox(
            "Registros para exibir:",
            [50, 100, 200, 500, "Todos"],
            index=0
        )
    
    # Mostrar dados
    if num_registros == "Todos":
        df_display = df_filtrado
    else:
        df_display = df_filtrado.head(num_registros)
    
    st.dataframe(
        df_display,
        use_container_width=True,
        height=400
    )
    
    # Informações adicionais
    st.markdown("---")
    col_info1, col_info2, col_info3 = st.columns(3)
    
    with col_info1:
        st.markdown(f"**📊 Registros filtrados:** {len(df_filtrado):,}")
    
    with col_info2:
        st.markdown(f"**📁 Arquivo:** {uploaded_file.name if uploaded_file else 'Dados de exemplo'}")
    
    with col_info3:
        st.markdown(f"**🔄 Última atualização:** {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    
    # Instruções
    with st.expander("ℹ️ Como usar este dashboard"):
        st.markdown("""
        ### 📋 **Como usar:**
        
        1. **📁 Upload de arquivo:**
           - Clique no botão de upload no topo da página
           - Selecione seu arquivo CSV ou Excel
           - O dashboard detectará automaticamente os tipos de colunas
        
        2. **⚙️ Configurações:**
           - Use a barra lateral para selecionar as colunas principais
           - **Coluna de Valor:** Dados numéricos para análise (ex: vendas, receita)
           - **Coluna de Categoria:** Dimensão para agrupar dados (ex: produto, região)
           - **Subcategoria:** Segunda dimensão opcional
        
        3. **🔍 Filtros:**
           - Use os filtros na barra lateral para segmentar os dados
           - Os gráficos e tabelas se atualizam automaticamente
        
        4. **📊 Visualizações:**
           - **Métricas principais:** Resumo dos dados filtrados
           - **Gráfico de barras:** Distribuição por categoria
           - **Tabela de ranking:** Top categorias ordenadas
           - **Dados detalhados:** Tabela completa com filtros aplicados
        
        ### 📝 **Formatos suportados:**
        - **CSV:** Separado por vírgula ou ponto-e-vírgula
        - **Excel:** Formatos .xlsx e .xls
        
        ### 💡 **Dicas:**
        - Para melhores resultados, organize seus dados com cabeçalhos claros
        - Dados numéricos devem estar em formato número (sem texto)
        - Datas devem estar em formato reconhecível (DD/MM/YYYY ou YYYY-MM-DD)
        """)

else:
    st.error("❌ Erro ao carregar dados. Tente novamente.")
