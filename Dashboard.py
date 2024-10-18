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

        # Exibindo as informações da aba de citações
        with tabs[0]:
            dados = citacoes_dados
            total_publicacoes = len(dados)
            st.metric(label="Quantidade Total", value=total_publicacoes)

            if "datapub" in dados.columns:
                dados["datapub"] = pd.to_datetime(dados["datapub"])
                dados["mes_ano"] = dados["datapub"].dt.to_period("M").astype(str)

                publicacoes_mensais = (
                    dados.groupby(["mes_ano", "name"]).size().reset_index(name="quantidade")
                )

                # Preparação do gráfico de barras com Pyecharts
                bar = Bar()
                meses = sorted(publicacoes_mensais["mes_ano"].unique())

                # Adicionar os dados para cada usuário individualmente
                for usuario in names:
                    dados_usuario = publicacoes_mensais[publicacoes_mensais["name"] == usuario]
                    # Garantir que os valores de cada mês sejam correspondentes ao eixo x
                    quantidade_por_mes = [dados_usuario[dados_usuario["mes_ano"] == mes]["quantidade"].sum() if not dados_usuario[dados_usuario["mes_ano"] == mes].empty else 0 for mes in meses]
                    bar.add_yaxis(usuario, quantidade_por_mes)

                bar.add_xaxis(meses)
                bar.set_global_opts(
                    title_opts=opts.TitleOpts(title="Publicações Mensais (Citações)", subtitle="Total por mês e por usuário"),
                    toolbox_opts=opts.ToolboxOpts(),
                    xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-45)),
                    yaxis_opts=opts.AxisOpts(name="Quantidade")
                )

                # Exibir o gráfico de barras no Streamlit
                st_pyecharts(bar, key="echarts_citacoes")

        # Exibindo as informações da aba de intimações
        with tabs[1]:
            dados = intimacoes_dados
            total_publicacoes = len(dados)
            st.metric(label="Quantidade Total", value=total_publicacoes)

            if "datapub" in dados.columns:
                dados["datapub"] = pd.to_datetime(dados["datapub"])
                dados["mes_ano"] = dados["datapub"].dt.to_period("M").astype(str)

                publicacoes_mensais = (
                    dados.groupby(["mes_ano", "name"]).size().reset_index(name="quantidade")
                )

                # Preparação do gráfico de barras com Pyecharts
                bar = Bar()
                meses = sorted(publicacoes_mensais["mes_ano"].unique())

                # Adicionar os dados para cada usuário individualmente
                for usuario in names:
                    dados_usuario = publicacoes_mensais[publicacoes_mensais["name"] == usuario]
                    quantidade_por_mes = [dados_usuario[dados_usuario["mes_ano"] == mes]["quantidade"].sum() if not dados_usuario[dados_usuario["mes_ano"] == mes].empty else 0 for mes in meses]
                    bar.add_yaxis(usuario, quantidade_por_mes)

                bar.add_xaxis(meses)
                bar.set_global_opts(
                    title_opts=opts.TitleOpts(title="Publicações Mensais (Intimações)", subtitle="Total por mês e por usuário"),
                    toolbox_opts=opts.ToolboxOpts(),
                    xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-45)),
                    yaxis_opts=opts.AxisOpts(name="Quantidade")
                )

                # Exibir o gráfico de barras no Streamlit
                st_pyecharts(bar, key="echarts_intimacoes")

    except pymysql.MySQLError as e:
        st.error(f"Erro na conexão com o banco de dados: {e}")


main()
