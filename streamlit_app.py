import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import json

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

# Tentar importar gspread
try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSHEETS_AVAILABLE = True
except ImportError:
    GSHEETS_AVAILABLE = False

# Configuração da página
st.set_page_config(
    page_title="Dashboard Analytics - Google Sheets",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main > div {
        padding-top: 2rem;
    }
    
    .header-container {
        background: linear-gradient(90deg, #34A853 0%, #4285F4 100%);
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
    
    .config-section {
        background-color: #e8f5e8;
        padding: 1.5rem;
        border-radius: 8px;
        margin-bottom: 2rem;
        border-left: 4px solid #34A853;
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
    
    .sheets-info {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #ffeaa7;
        margin-bottom: 1rem;
    }
    
    .success-box {
        background-color: #d1edff;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #0084ff;
        margin-bottom: 1rem;
    }
    
    .stDataFrame {
        border: 1px solid #e9ecef;
        border-radius: 8px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)

def configurar_google_sheets():
    """Interface para configurar conexão com Google Sheets"""
    st.markdown('<div class="config-section">', unsafe_allow_html=True)
    st.markdown("### 🔧 Configuração do Google Sheets")
    
    # Verificar se gspread está disponível
    if not GSHEETS_AVAILABLE:
        st.error("❌ Biblioteca gspread não está instalada.")
        st.code("pip install gspread google-auth")
        return None, None
    
    # Métodos de autenticação
    metodo_auth = st.radio(
        "Método de autenticação:",
        ["Credenciais JSON (Recomendado)", "URL Pública do Google Sheets"],
        help="Escolha como conectar ao Google Sheets"
    )
    
    if metodo_auth == "Credenciais JSON (Recomendado)":
        st.markdown("""
        **📋 Passo a passo para configurar:**
        1. Acesse [Google Cloud Console](https://console.cloud.google.com/)
        2. Crie um novo projeto ou selecione um existente
        3. Ative a API Google Sheets API e Google Drive API
        4. Crie uma conta de serviço (Service Account)
        5. Baixe o arquivo JSON de credenciais
        6. Compartilhe sua planilha com o email da conta de serviço
        """)
        
        # Upload do arquivo de credenciais
        credentials_file = st.file_uploader(
            "Faça upload do arquivo JSON de credenciais:",
            type=['json'],
            help="Arquivo JSON baixado do Google Cloud Console"
        )
        
        spreadsheet_url = st.text_input(
            "URL da planilha do Google Sheets:",
            placeholder="https://docs.google.com/spreadsheets/d/SEU_SPREADSHEET_ID/edit",
            help="Cole a URL completa da sua planilha"
        )
        
        sheet_name = st.text_input(
            "Nome da aba (opcional):",
            value="Sheet1",
            help="Nome da aba da planilha (deixe Sheet1 se for a primeira aba)"
        )
        
        if credentials_file and spreadsheet_url:
            try:
                # Carregar credenciais
                credentials_info = json.load(credentials_file)
                
                return {
                    'method': 'credentials',
                    'credentials': credentials_info,
                    'url': spreadsheet_url,
                    'sheet_name': sheet_name
                }
            except Exception as e:
                st.error(f"❌ Erro ao carregar credenciais: {str(e)}")
                return None
    
    else:  # URL Pública
        st.markdown("""
        **📋 Para usar URL pública:**
        1. Abra sua planilha no Google Sheets
        2. Clique em "Compartilhar" → "Alterar para qualquer pessoa com o link"
        3. Cole a URL abaixo
        """)
        
        spreadsheet_url = st.text_input(
            "URL pública da planilha:",
            placeholder="https://docs.google.com/spreadsheets/d/SEU_SPREADSHEET_ID/edit",
            help="A planilha deve estar pública (qualquer pessoa com o link pode visualizar)"
        )
        
        sheet_name = st.text_input(
            "Nome da aba:",
            value="Sheet1",
            help="Nome da aba da planilha"
        )
        
        if spreadsheet_url:
            return {
                'method': 'public',
                'url': spreadsheet_url,
                'sheet_name': sheet_name
            }
    
    st.markdown('</div>', unsafe_allow_html=True)
    return None

@st.cache_data(ttl=300)  # Cache por 5 minutos
def carregar_dados_sheets(config):
    """Carrega dados do Google Sheets"""
    try:
        if config['method'] == 'credentials':
            # Usar credenciais de conta de serviço
            scope = [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ]
            
            credentials = Credentials.from_service_account_info(
                config['credentials'], 
                scopes=scope
            )
            
            gc = gspread.authorize(credentials)
            
            # Extrair ID da planilha da URL
            if '/d/' in config['url']:
                sheet_id = config['url'].split('/d/')[1].split('/')[0]
            else:
                raise ValueError("URL inválida")
            
            # Abrir planilha
            spreadsheet = gc.open_by_key(sheet_id)
            worksheet = spreadsheet.worksheet(config['sheet_name'])
            
            # Converter para DataFrame
            data = worksheet.get_all_records()
            df = pd.DataFrame(data)
            
        else:  # Método público usando pandas
            # Converter URL para formato CSV
            if '/edit' in config['url']:
                csv_url = config['url'].replace('/edit', '/export?format=csv')
                if config['sheet_name'] != 'Sheet1':
                    csv_url += f"&gid=0"  # Para abas específicas, seria necessário o GID
            else:
                csv_url = config['url']
            
            # Ler como CSV
            df = pd.read_csv(csv_url)
        
        # Limpar dados
        df = df.dropna(how='all')  # Remove linhas completamente vazias
        df.columns = df.columns.str.strip()  # Remove espaços dos nomes das colunas
        
        return df
        
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados do Google Sheets: {str(e)}")
        return None

def gerar_dados_exemplo():
    """Gera dados de exemplo"""
    np.random.seed(42)
    data = []
    
    for i in range(500):
        data.append({
            'Data': (datetime.now() - timedelta(days=random.randint(0, 365))).strftime('%Y-%m-%d'),
            'Categoria': random.choice(['Vendas', 'Marketing', 'Suporte', 'Desenvolvimento', 'RH']),
            'Produto': random.choice(['Produto A', 'Produto B', 'Produto C', 'Produto D']),
            'Região': random.choice(['Norte', 'Sul', 'Leste', 'Oeste', 'Centro']),
            'Valor': round(random.uniform(100, 5000), 2),
            'Quantidade': random.randint(1, 50),
            'Responsável': random.choice(['Ana Silva', 'João Santos', 'Maria Oliveira', 'Pedro Costa'])
        })
    
    return pd.DataFrame(data)

def detectar_colunas(df):
    """Detecta tipos de colunas automaticamente"""
    colunas_numericas = df.select_dtypes(include=[np.number]).columns.tolist()
    colunas_data = []
    colunas_texto = df.select_dtypes(include=['object']).columns.tolist()
    
    # Tentar detectar colunas de data
    for col in colunas_texto.copy():
        try:
            pd.to_datetime(df[col].head(10))
            colunas_data.append(col)
            colunas_texto.remove(col)
        except:
            continue
    
    return colunas_numericas, colunas_data, colunas_texto

# Header principal
st.markdown("""
<div class="header-container">
    <h1 class="header-title">📊 Dashboard Analytics - Google Sheets</h1>
    <p class="header-subtitle">Conecte sua planilha do Google Sheets e crie visualizações em tempo real</p>
</div>
""", unsafe_allow_html=True)

# Configuração do Google Sheets
config = configurar_google_sheets()

# Carregar dados
df = None
if config:
    with st.spinner("🔄 Carregando dados do Google Sheets..."):
        df = carregar_dados_sheets(config)
        
    if df is not None:
        st.markdown('<div class="success-box">', unsafe_allow_html=True)
        st.success(f"✅ Dados carregados com sucesso! {len(df)} linhas e {len(df.columns)} colunas")
        
        # Botão para atualizar dados
        if st.button("🔄 Atualizar Dados", help="Recarrega os dados da planilha"):
            st.cache_data.clear()
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

# Se não conseguiu carregar do Sheets, usar dados de exemplo
if df is None:
    st.markdown('<div class="sheets-info">', unsafe_allow_html=True)
    st.warning("📋 Configure a conexão com Google Sheets acima ou veja os dados de exemplo abaixo")
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.checkbox("🔍 Mostrar dados de exemplo"):
        df = gerar_dados_exemplo()

if df is not None and not df.empty:
    # Detectar tipos de colunas
    cols_numericas, cols_data, cols_texto = detectar_colunas(df)
    
    # Mostrar preview dos dados
    with st.expander("👀 Visualizar dados carregados", expanded=False):
        st.dataframe(df.head(10), use_container_width=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write("**📊 Colunas Numéricas:**")
            for col in cols_numericas[:5]:  # Limitar a 5
                st.write(f"• {col}")
        
        with col2:
            st.write("**📅 Colunas de Data:**")
            for col in cols_data[:5]:
                st.write(f"• {col}")
        
        with col3:
            st.write("**📝 Colunas de Texto:**")
            for col in cols_texto[:5]:
                st.write(f"• {col}")

    # Sidebar com configurações
    st.sidebar.header("⚙️ Configurações de Análise")
    
    # Seleção de colunas principais
    if cols_numericas:
        coluna_valor = st.sidebar.selectbox(
            "💰 Coluna de Valor Principal",
            cols_numericas,
            help="Selecione a coluna numérica para análise"
        )
    else:
        coluna_valor = None
        st.sidebar.warning("⚠️ Nenhuma coluna numérica encontrada")
    
    if cols_texto:
        coluna_categoria = st.sidebar.selectbox(
            "📊 Coluna de Categoria",
            cols_texto,
            help="Coluna para agrupar os dados"
        )
    else:
        coluna_categoria = None
    
    if len(cols_texto) > 1:
        coluna_subcategoria = st.sidebar.selectbox(
            "🏷️ Subcategoria (Opcional)",
            ["Nenhuma"] + cols_texto,
            help="Segunda dimensão para análise"
        )
        if coluna_subcategoria == "Nenhuma":
            coluna_subcategoria = None
    else:
        coluna_subcategoria = None
    
    # Filtros dinâmicos
    st.sidebar.markdown("### 🔍 Filtros")
    
    filtros_ativos = {}
    for col in cols_texto[:3]:  # Primeiros 3 campos de texto
        valores_unicos = df[col].unique()
        if len(valores_unicos) <= 20:  # Só mostrar se não tiver muitas opções
            valores_selecionados = st.sidebar.multiselect(
                f"Filtrar por {col}",
                valores_unicos,
                default=valores_unicos
            )
            filtros_ativos[col] = valores_selecionados
    
    # Aplicar filtros
    df_filtrado = df.copy()
    for col, valores in filtros_ativos.items():
        if valores:
            df_filtrado = df_filtrado[df_filtrado[col].isin(valores)]
    
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
                <p class="metric-label">Registros</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Layout principal
    col_left, col_right = st.columns([1.5, 1])
    
    with col_left:
        if coluna_valor and coluna_categoria:
            st.markdown(f"### 📊 {coluna_valor} por {coluna_categoria}")
            
            # Preparar dados para gráfico
            if coluna_subcategoria:
                df_chart = df_filtrado.groupby([coluna_categoria, coluna_subcategoria])[coluna_valor].sum().reset_index()
                fig = px.bar(
                    df_chart.head(20),
                    x=coluna_categoria,
                    y=coluna_valor,
                    color=coluna_subcategoria,
                    title=f"{coluna_valor} por {coluna_categoria} e {coluna_subcategoria}"
                )
            else:
                df_chart = df_filtrado.groupby(coluna_categoria)[coluna_valor].sum().reset_index()
                df_chart = df_chart.sort_values(coluna_valor, ascending=False).head(10)
                fig = px.bar(
                    df_chart,
                    x=coluna_categoria,
                    y=coluna_valor,
                    title=f"Top 10 {coluna_categoria} por {coluna_valor}"
                )
            
            fig.update_layout(
                height=400,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("🔧 Configure as colunas na barra lateral para ver gráficos")
    
    with col_right:
        if coluna_categoria and coluna_valor:
            st.markdown(f"### 📋 Ranking {coluna_categoria}")
            
            df_ranking = df_filtrado.groupby(coluna_categoria)[coluna_valor].agg(['sum', 'count']).reset_index()
            df_ranking.columns = [coluna_categoria, 'Total', 'Quantidade']
            df_ranking = df_ranking.sort_values('Total', ascending=False).head(10)
            df_ranking['Pos'] = range(1, len(df_ranking) + 1)
            df_ranking['Total_fmt'] = df_ranking['Total'].apply(lambda x: f"{x:,.0f}")
            
            st.dataframe(
                df_ranking[['Pos', coluna_categoria, 'Total_fmt', 'Quantidade']].rename(columns={
                    'Pos': '#',
                    'Total_fmt': f'Total {coluna_valor}',
                    'Quantidade': 'Qtd'
                }),
                use_container_width=True,
                hide_index=True,
                height=400
            )
    
    # Dados detalhados
    st.markdown("### 📝 Dados Detalhados")
    
    # Configurações de exibição
    col_config1, col_config2 = st.columns([1, 3])
    with col_config1:
        num_linhas = st.selectbox(
            "Linhas a exibir:",
            [50, 100, 200, "Todas"],
            index=0
        )
    
    # Exibir tabela
    if num_linhas == "Todas":
        df_display = df_filtrado
    else:
        df_display = df_filtrado.head(num_linhas)
    
    st.dataframe(df_display, use_container_width=True, height=400)
    
    # Informações do rodapé
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"**📊 Total de registros:** {len(df_filtrado):,}")
    
    with col2:
        st.markdown(f"**🔄 Última atualização:** {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    
    with col3:
        if config and config.get('method') == 'credentials':
            st.markdown("**✅ Conectado via API**")
        else:
            st.markdown("**📋 Dados de exemplo**")

# Instruções de uso
with st.expander("📋 Como configurar Google Sheets"):
    st.markdown("""
    ## 🔧 **Configuração Completa - Passo a Passo**
    
    ### **Método 1: Credenciais JSON (Recomendado)**
    
    #### **1. Google Cloud Console:**
    1. Acesse [console.cloud.google.com](https://console.cloud.google.com/)
    2. Crie um projeto novo ou selecione existente
    3. No menu lateral: **APIs e serviços** → **Biblioteca**
    4. Ative as APIs:
       - **Google Sheets API**
       - **Google Drive API**
    
    #### **2. Criar Conta de Serviço:**
    1. **APIs e serviços** → **Credenciais**
    2. **Criar credenciais** → **Conta de serviço**
    3. Preencha nome e descrição
    4. Clique na conta criada
    5. **Chaves** → **Adicionar chave** → **JSON**
    6. Faça download do arquivo JSON
    
    #### **3. Configurar Planilha:**
    1. Abra sua planilha no Google Sheets
    2. Clique **Compartilhar**
    3. Adicione o email da conta de serviço (está no arquivo JSON)
    4. Dê permissão de **Editor** ou **Visualizador**
    
    #### **4. No Dashboard:**
    1. Faça upload do arquivo JSON
    2. Cole a URL da planilha
    3. Defina o nome da aba
    
    ---
    
    ### **Método 2: URL Pública (Mais Simples)**
    
    #### **1. Tornar Planilha Pública:**
    1. Abra sua planilha
    2. **Compartilhar** → **Alterar para qualquer pessoa com o link**
    3. Permissão: **Visualizador**
    4. Copie a URL
    
    #### **2. No Dashboard:**
    1. Cole a URL pública
    2. Defina o nome da aba
    
    ---
    
    ## 📊 **Estrutura Recomendada da Planilha**
    
    ```
    | Data       | Categoria | Produto   | Região | Valor | Quantidade | Responsável |
    |------------|-----------|-----------|--------|-------|------------|-------------|
    | 2024-01-15 | Vendas    | Produto A | Norte  | 1500  | 10         | João        |
    | 2024-01-16 | Marketing | Produto B | Sul    | 2000  | 15         | Maria       |
    ```
    
    ### **💡 Dicas importantes:**
    - **Primeira linha** deve conter os cabeçalhos
    - **Datas** em formato YYYY-MM-DD ou DD/MM/YYYY
    - **Números** sem texto (apenas números)
    - **Evite** células mescladas
    - **Use** nomes claros para as colunas
    
    ### **🔄 Atualização Automática:**
    - Os dados são atualizados automaticamente a cada 5 minutos
    - Use o botão **"Atualizar Dados"** para forçar atualização
    - Qualquer mudança na planilha aparece no dashboard
    """)
