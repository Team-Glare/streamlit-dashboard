import os
import dotenv
import pandas as pd
import plotly.express as px
import pymysql
import streamlit as st
from pyecharts.charts import Bar
from pyecharts import options as opts
from streamlit_echarts import st_pyecharts

st.set_page_config(layout="wide")

# Título da página
st.title("Estatísticas da Procuradoria Trabalhista - PTB :bar_chart:")

dotenv.load_dotenv()

# Informações de conexão com o banco de dados
host = os.getenv("DB_HOST")
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD") or ""
database = os.getenv("DB_DATABASE")

def main() -> None:
    """Start the Streamlit app."""
    try:
        if not host or not user or not database:
            st.error("Faltam informações de conexão com o banco de dados.")
            return

        conn = pymysql.connect(
            host=host,
            port=3306,
            user=user,
            password=password,
            database=database,
        )

        names = [
            'Natália Franco Massuia e Marcondes',
            'Anamaria Barbosa Ebram Fernandes',
            'Leonardo Tokuda Pereira',
            'Leonardo Warmling Candido da Silva',
            'Marcelo Moura da Silva',
            'Pedro Carvalho Mitre Chaves',
            'Kelly Cristina Majima'
        ]

        tabs = st.tabs(["Citações", "Intimações"])

        cursor = conn.cursor()

        # Consulta para citações
        cursor.execute(
            "SELECT * FROM ANDAMENTOS WHERE nome_procuradoria='PTB' AND natureza LIKE 'cit%' COLLATE utf8mb4_unicode_ci",
        )
        citacoes = cursor.fetchall()
        colunas = [desc[0] for desc in cursor.description]
        citacoes_dados = pd.DataFrame(citacoes, columns=colunas)
        citacoes_dados = citacoes_dados[citacoes_dados['name'].isin(names)]

        # Consulta para intimações
        cursor.execute(
            "SELECT * FROM ANDAMENTOS WHERE nome_procuradoria='PTB' AND natureza LIKE 'int%' COLLATE utf8mb4_unicode_ci",
        )
        intimacoes = cursor.fetchall()
        colunas = [desc[0] for desc in cursor.description]
        intimacoes_dados = pd.DataFrame(intimacoes, columns=colunas)
        intimacoes_dados = intimacoes_dados[intimacoes_dados['name'].isin(names)]

        conn.close()

        # Filtro de mês e ano
        with st.sidebar:
            st.header("Filtro de Data")
            meses_disponiveis = pd.to_datetime(citacoes_dados["datapub"].append(intimacoes_dados["datapub"])).dt.to_period("M").unique()
            mes_selecionado = st.selectbox("Selecione o Mês e Ano", sorted(meses_disponiveis.astype(str)))

        # Exibindo as informações da aba de citações
        with tabs[0]:
            dados = citacoes_dados
            dados["datapub"] = pd.to_datetime(dados["datapub"])
            dados["mes_ano"] = dados["datapub"].dt.to_period("M").astype(str)
            dados = dados[dados["mes_ano"] == mes_selecionado]  # Aplicando o filtro

            total_publicacoes = len(dados)
            st.metric(label="Quantidade Total", value=total_publicacoes)

            # Gráficos e Tabela (Citações)
            gerar_graficos(dados, "Citações")

        # Exibindo as informações da aba de intimações
        with tabs[1]:
            dados = intimacoes_dados
            dados["datapub"] = pd.to_datetime(dados["datapub"])
            dados["mes_ano"] = dados["datapub"].dt.to_period("M").astype(str)
            dados = dados[dados["mes_ano"] == mes_selecionado]  # Aplicando o filtro

            total_publicacoes = len(dados)
            st.metric(label="Quantidade Total", value=total_publicacoes)

            # Gráficos e Tabela (Intimações)
            gerar_graficos(dados, "Intimações")

    except pymysql.MySQLError as e:
        st.error(f"Erro na conexão com o banco de dados: {e}")

def gerar_graficos(dados, titulo):
    """Função para gerar gráficos e tabela com base nos dados."""
    if "datapub" in dados.columns:
        # Dados de publicações mensais
        publicacoes_mensais = (
            dados.groupby(["mes_ano", "name"]).size().reset_index(name="quantidade")
        )

        # Gráfico de pizza com Plotly
        publicacoes_por_usuario = dados['name'].value_counts().reset_index()
        publicacoes_por_usuario.columns = ['Nome', 'Quantidade']
        fig_pizza = px.pie(
            publicacoes_por_usuario,
            names='Nome',
            values='Quantidade',
            title=f"Distribuição de Publicações por Usuário ({titulo})",
            hole=0.4,
        )

        # Gráfico de barras com Pyecharts
        bar = (
            Bar()
            .add_xaxis(list(publicacoes_mensais["mes_ano"].unique()))
            .add_yaxis(
                "Quantidade de Publicações",
                publicacoes_mensais.groupby("mes_ano")["quantidade"].sum().tolist()
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title=f"Publicações Mensais ({titulo})", subtitle="Total por mês"),
                toolbox_opts=opts.ToolboxOpts(),
            )
        )

        # Exibir gráficos lado a lado
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(fig_pizza, height=500)
        with col2:
            st_pyecharts(bar, key=f"echarts_{titulo}")

        # Gráfico de barras com Plotly
        fig_barras_plotly = px.bar(
            publicacoes_mensais,
            x="mes_ano",
            y="quantidade",
            color="name",
            title=f"Publicações Mensais por Usuário ({titulo})",
            text_auto=True,
            labels={"mes_ano": "Mês e Ano", "quantidade": "Quantidade", "name": "Nome"},
        )
        
        # Exibir gráfico de barras do Plotly
        st.subheader(f"Gráfico de Barras ({titulo})")
        st.plotly_chart(fig_barras_plotly, use_container_width=True)

        # Tabela com o quantitativo mensal
        st.subheader(f"Tabela de Quantitativo Mensal ({titulo})")
        st.dataframe(publicacoes_mensais)

main()
