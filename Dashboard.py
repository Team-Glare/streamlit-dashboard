"""Dashboard do projeto."""

import os
import dotenv
import pandas as pd
import pymysql
import streamlit as st
from pyecharts.charts import Bar
from pyecharts import options as opts  # Importar as opções necessárias
import random  # Importar random para gerar dados aleatórios

# Verificação da versão do pyecharts
import pyecharts
print(pyecharts.__version__)

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
        
        tabs = st.tabs([ "Citações", "Intimações", "Gráfico de Pizza"])

        cursor = conn.cursor()
        # Executar a consulta SQL para intimações
        cursor.execute(
            "SELECT * FROM ANDAMENTOS WHERE nome_procuradoria='PTB' AND natureza LIKE 'int%' COLLATE utf8mb4_unicode_ci",
        )
        intimacoes = cursor.fetchall()
        colunas = [desc[0] for desc in cursor.description]
        
        # Criar um DataFrame a partir dos resultados e nomes de colunas
        intimacoes_dados = pd.DataFrame(intimacoes, columns=colunas)
        intimacoes_dados = intimacoes_dados[intimacoes_dados['name'].isin(names)]

        # Executar a consulta SQL para citações
        cursor.execute(
            "SELECT * FROM ANDAMENTOS WHERE nome_procuradoria='PTB' AND natureza LIKE 'cit%' COLLATE utf8mb4_unicode_ci",
        )
        citacoes = cursor.fetchall()
        colunas = [desc[0] for desc in cursor.description]

        # Criar um DataFrame a partir dos resultados e nomes de colunas
        citacoes_dados = pd.DataFrame(citacoes, columns=colunas)
        citacoes_dados = citacoes_dados[citacoes_dados['name'].isin(names)]

        # Fechar a conexão com o banco de dados
        conn.close()
        
        with tabs[0]:
            dados = citacoes_dados
            
            # Calcular o total de publicações
            total_publicacoes = len(dados)
            st.metric(label="Quantidade Total", value=total_publicacoes)

            # Verifica se há uma coluna 'datapub' no formato adequado
            if "datapub" in dados.columns:
                dados["datapub"] = pd.to_datetime(dados["datapub"])
                dados["mes_ano"] = dados["datapub"].dt.to_period("M").astype(str)

                # Contar o número de publicações por mês e por nome
                publicacoes_mensais = (
                    dados.groupby(["mes_ano", "name"]).size().reset_index(name="quantidade")
                )

                # Renomear colunas
                publicacoes_mensais.rename(
                    columns={"mes_ano": "Mês/Ano", "name": "Nome", "quantidade": "Quantidade"},
                    inplace=True,
                )

                # Criar gráfico de pizza
                pizza_data = [
                    {"value": row['Quantidade'], "name": row['Nome']}
                    for _, row in publicacoes_mensais.iterrows()
                ]

                options = {
                    "tooltip": {"trigger": "item"},
                    "legend": {"top": "5%", "left": "center"},
                    "series": [
                        {
                            "name": "Publicações",
                            "type": "pie",
                            "radius": ["40%", "70%"],
                            "avoidLabelOverlap": False,
                            "itemStyle": {
                                "borderRadius": 10,
                                "borderColor": "#fff",
                                "borderWidth": 2,
                            },
                            "label": {"show": False, "position": "center"},
                            "emphasis": {
                                "label": {"show": True, "fontSize": "40", "fontWeight": "bold"}
                            },
                            "labelLine": {"show": False},
                            "data": pizza_data,
                        }
                    ],
                }

                # Exibir gráfico de pizza
                col1, col2 = st.columns(2)
                with col1:
                    st_echarts(options=options, height="400px")

                # Criar gráfico de colunas (Bar Chart) com Pyecharts
                bar = (
                    Bar()
                    .add_xaxis(publicacoes_mensais["Mês/Ano"].tolist())
                    .add_yaxis("Quantidade", publicacoes_mensais["Quantidade"].tolist())
                    .set_global_opts(
                        title_opts=opts.TitleOpts(title="Publicações Mensais por Nome"),
                        toolbox_opts=opts.ToolboxOpts(),
                    )
                )

                with col2:
                    st_pyecharts(bar, key="echarts")  # Exibir o gráfico de colunas

                # Exibir o resumo das publicações mensais
                st.subheader("Publicações Mensais Resumidas")
                st.table(publicacoes_mensais)

        with tabs[1]:
            dados = intimacoes_dados

            # Calcular o total de publicações
            total_publicacoes = len(dados)
            st.metric(label="Quantidade Total", value=total_publicacoes)

            # Verifica se há uma coluna 'datapub' no formato adequado
            if "datapub" in dados.columns:
                dados["datapub"] = pd.to_datetime(dados["datapub"])
                dados["mes_ano"] = dados["datapub"].dt.to_period("M").astype(str)

                # Contar o número de publicações por mês e por nome
                publicacoes_mensais = (
                    dados.groupby(["mes_ano", "name"]).size().reset_index(name="quantidade")
                )

                # Renomear colunas
                publicacoes_mensais.rename(
                    columns={"mes_ano": "Mês/Ano", "name": "Nome", "quantidade": "Quantidade"},
                    inplace=True,
                )

                # Criar gráfico de pizza
                pizza_data = [
                    {"value": row['Quantidade'], "name": row['Nome']}
                    for _, row in publicacoes_mensais.iterrows()
                ]

                options = {
                    "tooltip": {"trigger": "item"},
                    "legend": {"top": "5%", "left": "center"},
                    "series": [
                        {
                            "name": "Publicações",
                            "type": "pie",
                            "radius": ["40%", "70%"],
                            "avoidLabelOverlap": False,
                            "itemStyle": {
                                "borderRadius": 10,
                                "borderColor": "#fff",
                                "borderWidth": 2,
                            },
                            "label": {"show": False, "position": "center"},
                            "emphasis": {
                                "label": {"show": True, "fontSize": "40", "fontWeight": "bold"}
                            },
                            "labelLine": {"show": False},
                            "data": pizza_data,
                        }
                    ],
                }

                # Exibir gráfico de pizza
                col1, col2 = st.columns(2)
                with col1:
                    st_echarts(options=options, height="400px")

                # Criar gráfico de colunas (Bar Chart) com Pyecharts
                bar = (
                    Bar()
                    .add_xaxis(publicacoes_mensais["Mês/Ano"].tolist())
                    .add_yaxis("Quantidade", publicacoes_mensais["Quantidade"].tolist())
                    .set_global_opts(
                        title_opts=opts.TitleOpts(title="Publicações Mensais por Nome"),
                        toolbox_opts=opts.ToolboxOpts(),
                    )
                )

                with col2:
                    st_pyecharts(bar, key="echarts")  # Exibir o gráfico de colunas

                # Exibir o resumo das publicações mensais
                st.subheader("Publicações Mensais Resumidas")
                st.table(publicacoes_mensais)

    except pymysql.MySQLError as e:
        st.error(f"Erro na conexão com o banco de dados: {e}")


main()
