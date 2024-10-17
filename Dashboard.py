"""Dashboard do projeto."""

import os
import random
import dotenv
import pandas as pd
import plotly.express as px  # type: ignore  # noqa: PGH003
import pymysql
import streamlit as st
from pyecharts.charts import Bar
from pyecharts import options as opts
from streamlit_echarts import st_pyecharts  # Importando o st_pyecharts para o novo gráfico

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
        # Executar a consulta SQL para citações
        cursor.execute(
            "SELECT * FROM ANDAMENTOS WHERE nome_procuradoria='PTB' AND natureza LIKE 'cit%' COLLATE utf8mb4_unicode_ci",
        )
        citacoes = cursor.fetchall()
        colunas = [desc[0] for desc in cursor.description]
        
        # Criar um DataFrame a partir dos resultados e nomes de colunas
        citacoes_dados = pd.DataFrame(citacoes, columns=colunas)
        citacoes_dados = citacoes_dados[citacoes_dados['name'].isin(names)]

        # Executar a consulta SQL para intimações
        cursor.execute(
            "SELECT * FROM ANDAMENTOS WHERE nome_procuradoria='PTB' AND natureza LIKE 'int%' COLLATE utf8mb4_unicode_ci",
        )
        intimacoes = cursor.fetchall()
        colunas = [desc[0] for desc in cursor.description]

        # Criar um DataFrame a partir dos resultados e nomes de colunas
        intimacoes_dados = pd.DataFrame(intimacoes, columns=colunas)
        intimacoes_dados = intimacoes_dados[intimacoes_dados['name'].isin(names)]

        # Fechar a conexão com o banco de dados
        conn.close()
        
        # Exibindo as informações da aba de citações
        with tabs[0]:
            dados = citacoes_dados
            # Calcular o total de publicações
            total_publicacoes = len(dados)
            st.metric(label="Quantidade Total", value=total_publicacoes)

            # Verifica se há uma coluna 'datapub' no formato adequado
            if "datapub" in dados.columns:
                dados["datapub"] = pd.to_datetime(dados["datapub"])
                dados["mes_ano"] = dados["datapub"].dt.to_period("M").astype(str)

                # Contar o número de publicações por mês e nome
                publicacoes_mensais = (
                    dados.groupby(["mes_ano", "name"]).size().reset_index(name="quantidade")
                )

                # Renomear colunas
                publicacoes_mensais.rename(
                    columns={"mes_ano": "Mês/Ano", "name": "Nome", "quantidade": "Quantidade"},
                    inplace=True,
                )

                # Criar gráfico de pizza com Plotly Express
                publicacoes_por_usuario = dados['name'].value_counts().reset_index()
                publicacoes_por_usuario.columns = ['Nome', 'Quantidade']

                fig_pizza = px.pie(
                    publicacoes_por_usuario,
                    names='Nome',
                    values='Quantidade',
                    title="Distribuição de Publicações por Usuário (Citações)",
                    hole=0.4,  # Isso cria o efeito de "rosca"
                )

                # Novo gráfico de colunas usando Pyecharts
                bar_chart = (
                    Bar()
                    .add_xaxis(publicacoes_mensais["Mês/Ano"].tolist())  # Adiciona os meses como eixos X
                    .add_yaxis("Quantidade de Publicações", publicacoes_mensais["Quantidade"].tolist())  # Adiciona as quantidades
                    .set_global_opts(
                        title_opts=opts.TitleOpts(
                            title="Publicações Mensais (Citações)", subtitle="Quantidade de Publicações"
                        ),
                        toolbox_opts=opts.ToolboxOpts(),
                    )
                )

                # Exibir os gráficos lado a lado
                col1, col2 = st.columns(2)
                with col1:
                    st.plotly_chart(fig_pizza, height=500)
                
                with col2:
                    st_pyecharts(bar_chart, key="echarts")  # Adiciona o novo gráfico de colunas

                # Exibir o resumo das publicações mensais
                st.subheader("Publicações Mensais Resumidas")
                
                # Ajustando a largura da tabela com CSS
                st.markdown(
                    """
                    <style>
                    .dataframe {
                        width: 100%;  /* Ajusta a largura da tabela */
                    }
                    </style>
                    """,
                    unsafe_allow_html=True,
                )
                st.table(publicacoes_mensais)

        # Exibindo as informações da aba de intimações
        with tabs[1]:
            dados = intimacoes_dados
            # Calcular o total de publicações
            total_publicacoes = len(dados)
            st.metric(label="Quantidade Total", value=total_publicacoes)

            # Verifica se há uma coluna 'datapub' no formato adequado
            if "datapub" in dados.columns:
                dados["datapub"] = pd.to_datetime(dados["datapub"])
                dados["mes_ano"] = dados["datapub"].dt.to_period("M").astype(str)

                # Contar o número de publicações por mês e nome
                publicacoes_mensais = (
                    dados.groupby(["mes_ano", "name"]).size().reset_index(name="quantidade")
                )

                # Renomear colunas
                publicacoes_mensais.rename(
                    columns={"mes_ano": "Mês/Ano", "name": "Nome", "quantidade": "Quantidade"},
                    inplace=True,
                )

                # Criar gráfico de pizza com Plotly Express
                publicacoes_por_usuario = dados['name'].value_counts().reset_index()
                publicacoes_por_usuario.columns = ['Nome', 'Quantidade']

                fig_pizza = px.pie(
                    publicacoes_por_usuario,
                    names='Nome',
                    values='Quantidade',
                    title="Distribuição de Publicações por Usuário (Intimações)",
                    hole=0.4,  # Isso cria o efeito de "rosca"
                )

                # Novo gráfico de colunas usando Pyecharts
                bar_chart = (
                    Bar()
                    .add_xaxis(publicacoes_mensais["Mês/Ano"].tolist())
                    .add_yaxis("Quantidade de Publicações", publicacoes_mensais["Quantidade"].tolist())
                    .set_global_opts(
                        title_opts=opts.TitleOpts(
                            title="Publicações Mensais (Intimações)", subtitle="Quantidade de Publicações"
                        ),
                        toolbox_opts=opts.ToolboxOpts(),
                    )
                )

                # Exibir os gráficos lado a lado
                col1, col2 = st.columns(2)
                with col1:
                    st.plotly_chart(fig_pizza, height=500)
                
                with col2:
                    st_pyecharts(bar_chart, key="echarts")  # Adiciona o novo gráfico de colunas

                # Exibir o resumo das publicações mensais
                st.subheader("Publicações Mensais Resumidas")
                
                # Ajustando a largura da tabela com CSS
                st.markdown(
                    """
                    <style>
                    .dataframe {
                        width: 100%;  /* Ajusta a largura da tabela */
                    }
                    </style>
                    """,
                    unsafe_allow_html=True,
                )
                st.table(publicacoes_mensais)

    except pymysql.MySQLError as e:
        st.error(f"Erro na conexão com o banco de dados: {e}")


main()
