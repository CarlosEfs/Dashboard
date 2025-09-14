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
</style>
""", unsafe_allow_html=True)

def conectar_sheets_simples(url):
    """Método mais simples para conectar ao Google Sheets"""
    try:
        # Extrair ID da planilha
        if '/d/' in url:
            sheet_id = url.split('/d/')[1].split('/')[0]
        else:
            st.error("❌ URL inválida. Use o formato completo do Google Sheets")
            return None
        
        # URLs para tentar (diferentes formatos)
        urls_tentar = [
            f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0",
            f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv",
            f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&gid=0"
        ]
        
        for csv_url in urls_tentar:
            try:
                st.info(f"🔄 Tentando: {csv_url[:60]}...")
                df = pd.read_csv(csv_url)
                
                # Limpar dados
                df = df.dropna(how='all')
                df.columns = df.columns.str.strip()
                
                if not df.empty:
                    st.success(f"✅ Conectado com sucesso!")
                    return df
                    
            except Exception as e:
                st.warning(f"⚠️ Tentativa falhou: {str(e)[:50]}...")
                continue
        
        return None
        
    except Exception as e:
        st.error(f"❌ Erro: {str(e)}")
        return None

@st.cache_data(ttl=300)  # Cache 5 minutos
def carregar_dados_cached(url):
    """Versão com cache da função de conexão"""
    return conectar_sheets_simples(url)

def gerar_dados_exemplo():
    """Dados de exemplo"""
    np.random.seed(42)
    data = []
    
    categorias = ['Vendas', 'Marketing', 'Suporte', 'Desenvolvimento']
    produtos = ['Produto A', 'Produto B', 'Produto C', 'Produto D']
    regioes = ['Norte', 'Sul', 'Leste', 'Oeste']
    responsaveis = ['Ana Silva', 'João Santos', 'Maria Costa', 'Pedro Lima']
    
    for i in range(300):
        data.append({
            'Data': (datetime.now() - timedelta(days=random.randint(0, 90))).strftime('%Y-%m-%d'),
            'Categoria': random.choice(categorias),
            'Produto': random.choice(produtos),
            'Regiao': random.choice(regioes),
            'Valor': round(random.uniform(100, 5000), 2),
            'Quantidade': random.randint(1, 20),
            'Responsavel': random.choice(responsaveis)
        })
    
    return pd.DataFrame(data)

# Header
st.markdown("""
<div class="header">
    <h1>📊 Dashboard Analytics - Google Sheets</h1>
    <p>Conecte sua planilha em 3 cliques - Método Ultra Simples</p>
</div>
""", unsafe_allow_html=True)

# Configuração simplificada
st.markdown('<div class="config-box">', unsafe_allow_html=True)
st.markdown("### 🔗 Conectar Google Sheets")

col1, col2 = st.columns([2, 1])

with col1:
    sheets_url = st.text_input(
        "URL da sua planilha do Google Sheets:",
        placeholder="https://docs.google.com/spreadsheets/d/SEU_ID_AQUI/edit",
        help="Cole a URL completa da sua planilha"
    )

with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 Conectar", type="primary"):
        if sheets_url:
            st.cache_data.clear()
            st.rerun()

st.markdown("""
**📋 Passos rápidos:**
1. **Abra sua planilha** no Google Sheets
2. **Clique em Compartilhar** → "Qualquer pessoa com o link pode visualizar"
3. **Copie e cole** a URL acima
4. **Clique em Conectar**
""")

st.markdown('</div>', unsafe_allow_html=True)

# Tentar carregar dados
df = None
if sheets_url:
    with st.spinner("🔄 Conectando ao Google Sheets..."):
        df = carregar_dados_cached(sheets_url)

# Se não conseguir, mostrar dados de exemplo
if df is None:
    if sheets_url:
        st.error("❌ Não foi possível conectar. Verifique se a planilha está pública.")
    
    st.info("📋 Mostrando dados de exemplo. Configure a URL acima para usar seus dados reais.")
    
    if st.checkbox("🔍 Ver dados de exemplo", value=True):
        df = gerar_dados_exemplo()

# Se temos dados, mostrar dashboard
if df is not None and not df.empty:
    
    # Detectar colunas
    cols_numericas = df.select_dtypes(include=[np.number]).columns.tolist()
    cols_texto = df.select_dtypes(include=['object']).columns.tolist()
    
    # Preview dos dados
    with st.expander("👀 Preview dos dados", expanded=False):
        st.dataframe(df.head(), use_container_width=True)
        st.write(f"📊 **Shape:** {df.shape[0]} linhas × {df.shape[1]} colunas")
    
    # Configuração rápida na sidebar
    with st.sidebar:
        st.header("⚙️ Configurações")
        
        # Selecionar colunas principais
        if cols_numericas:
            coluna_valor = st.selectbox("💰 Coluna de Valores", cols_numericas)
        else:
            coluna_valor = None
            st.warning("Nenhuma coluna numérica encontrada")
        
        if cols_texto:
            coluna_categoria = st.selectbox("📊 Coluna de Categoria", cols_texto)
        else:
            coluna_categoria = None
        
        # Filtros simples
        if coluna_categoria and coluna_categoria in df.columns:
            valores_categoria = df[coluna_categoria].unique()
            if len(valores_categoria) <= 20:
                filtro_categoria = st.multiselect(
                    f"Filtrar {coluna_categoria}",
                    valores_categoria,
                    default=valores_categoria
                )
            else:
                filtro_categoria = valores_categoria
        else:
            filtro_categoria = []
    
    # Aplicar filtros
    df_filtrado = df.copy()
    if filtro_categoria and coluna_categoria:
        df_filtrado = df_filtrado[df_filtrado[coluna_categoria].isin(filtro_categoria)]
    
    # Métricas principais
    if coluna_valor and coluna_categoria:
        st.markdown("### 📈 Resumo Executivo")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total = df_filtrado[coluna_valor].sum()
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: #34A853; margin: 0;">{total:,.0f}</h3>
                <p style="color: #666; margin: 0.5rem 0;">Total {coluna_valor}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            media = df_filtrado[coluna_valor].mean()
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: #4285F4; margin: 0;">{media:,.0f}</h3>
                <p style="color: #666; margin: 0.5rem 0;">Média {coluna_valor}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            maximo = df_filtrado[coluna_valor].max()
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: #EA4335; margin: 0;">{maximo:,.0f}</h3>
                <p style="color: #666; margin: 0.5rem 0;">Máximo {coluna_valor}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            registros = len(df_filtrado)
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: #FBBC04; margin: 0;">{registros:,}</h3>
                <p style="color: #666; margin: 0.5rem 0;">Registros</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Gráfico principal
        col_graf, col_tabela = st.columns([2, 1])
        
        with col_graf:
            st.markdown(f"### 📊 {coluna_valor} por {coluna_categoria}")
            
            # Preparar dados para o gráfico
            df_graf = df_filtrado.groupby(coluna_categoria)[coluna_valor].sum().reset_index()
            df_graf = df_graf.sort_values(coluna_valor, ascending=False).head(10)
            
            fig = px.bar(
                df_graf,
                x=coluna_categoria,
                y=coluna_valor,
                title=f"Top 10 {coluna_categoria}",
                color=coluna_valor,
                color_continuous_scale="viridis"
            )
            
            fig.update_layout(
                height=400,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col_tabela:
            st.markdown(f"### 📋 Ranking {coluna_categoria}")
            
            df_ranking = df_filtrado.groupby(coluna_categoria)[coluna_valor].agg(['sum', 'count']).reset_index()
            df_ranking.columns = [coluna_categoria, 'Total', 'Qtd']
            df_ranking = df_ranking.sort_values('Total', ascending=False).head(10)
            df_ranking.index = range(1, len(df_ranking) + 1)
            df_ranking['Total'] = df_ranking['Total'].apply(lambda x: f"{x:,.0f}")
            
            st.dataframe(
                df_ranking[[coluna_categoria, 'Total', 'Qtd']],
                use_container_width=True,
                height=400
            )
    
    # Tabela de dados completos
    st.markdown("### 📝 Dados Completos")
    
    col_opt1, col_opt2 = st.columns([1, 3])
    with col_opt1:
        qtd_linhas = st.selectbox("Mostrar linhas:", [20, 50, 100, "Todas"])
    
    if qtd_linhas == "Todas":
        df_mostrar = df_filtrado
    else:
        df_mostrar = df_filtrado.head(qtd_linhas)
    
    st.dataframe(df_mostrar, use_container_width=True, height=400)
    
    # Informações finais
    st.markdown("---")
    col_info1, col_info2, col_info3 = st.columns(3)
    
    with col_info1:
        st.write(f"**📊 Total registros:** {len(df_filtrado):,}")
    
    with col_info2:
        st.write(f"**🔗 Fonte:** {'Google Sheets' if sheets_url else 'Dados exemplo'}")
    
    with col_info3:
        st.write(f"**🕒 Atualizado:** {datetime.now().strftime('%H:%M')}")

# Tutorial rápido
with st.expander("❓ Problemas de conexão? Clique aqui"):
    st.markdown("""
    ## 🔧 **Solução rápida para erros:**
    
    ### **1. Erro 400 - Bad Request**
    - ✅ Certifique-se que a planilha está **pública**
    - ✅ Use a URL completa (com `/edit` no final)
    - ✅ Verifique se há dados na planilha
    
    ### **2. Como tornar pública (SEM RISCOS):**
    1. Na sua planilha → **Compartilhar**
    2. **"Qualquer pessoa na internet com este link"**
    3. Permissão: **"Visualizador"** (não "Editor")
    4. Copiar link
    
    ### **3. Exemplo de URL correta:**
    ```
    https://docs.google.com/spreadsheets/d/1AbC123XyZ456/edit#gid=0
    ```
    
    ### **4. Estrutura da planilha:**
    - **Primeira linha:** Cabeçalhos (Data, Categoria, Valor, etc.)
    - **Sem células mescladas**
    - **Números sem texto** (ex: 1500 não "R$ 1.500")
    
    ### **5. Ainda não funciona?**
    - Teste com dados de exemplo primeiro
    - Verifique se a planilha não está vazia
    - Tente com uma planilha nova e simples
    """)
