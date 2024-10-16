"""Dashboard do projeto."""

import os

import dotenv
import pandas as pd
import plotly.express as px  # type: ignore  # noqa: PGH003
import pymysql
import streamlit as st

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
            'Anamaria Barbosa Ebram Fernandes'
        ]
        
        
        tabs = st.tabs([ "Citações", "Intimações"])
        
        cursor = conn.cursor()
        # Executar a consulta SQL
        cursor.execute(
            "SELECT * FROM ANDAMENTOS WHERE nome_procuradoria='PTB' AND natureza LIKE 'int%' COLLATE utf8mb4_unicode_ci",
        )
        intimacoes = cursor.fetchall()
        colunas = [desc[0] for desc in cursor.description]
        
        
        
        # Criar um DataFrame a partir dos resultados e nomes de colunas
        intimacoes_dados = pd.DataFrame(intimacoes, columns=colunas)
        intimacoes_dados = intimacoes_dados[citacoes_dados['name'] in names]

        cursor = conn.cursor()
        # Executar a consulta SQL
        cursor.execute(
            "SELECT * FROM ANDAMENTOS WHERE nome_procuradoria='PTB' AND natureza LIKE 'cit%' COLLATE utf8mb4_unicode_ci",
        )
        citacoes = cursor.fetchall()
        colunas = [desc[0] for desc in cursor.description]

        # Criar um DataFrame a partir dos resultados e nomes de colunas
        citacoes_dados = pd.DataFrame(citacoes, columns=colunas)
        citacoes_dados = citacoes_dados['name' in names]

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

                # Contar o número de publicações por mês
                publicacoes_mensais = (  # type: ignore  # noqa: PGH003
                    dados.groupby("mes_ano").size().reset_index(name="quantidade")
                )

                # Renomear colunas
                publicacoes_mensais.rename(
                    columns={"mes_ano": "Mês/Ano", "quantidade": "Quantidade"},
                    inplace=True,
                )

                # Criar gráfico de barras com Plotly Express
                fig = px.bar(
                    publicacoes_mensais,
                    x="Mês/Ano",
                    y="Quantidade",
                    title="Publicações Mensais",
                    labels={
                        "Mês/Ano": "Mês/Ano",
                        "Quantidade": "Quantidade de Publicações",
                    },
                    height=400,
                )
                
                

                

                col1, col2 = st.columns(2)
                with col1:
                    # Exibir o gráfico no Streamlit
                    st.plotly_chart(fig)

                with col2:
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

                # Contar o número de publicações por mês
                publicacoes_mensais = (  # type: ignore  # noqa: PGH003
                    dados.groupby("mes_ano").size().reset_index(name="quantidade")
                )

                # Renomear colunas
                publicacoes_mensais.rename(
                    columns={"mes_ano": "Mês/Ano", "quantidade": "Quantidade"},
                    inplace=True,
                )

                # Criar gráfico de barras com Plotly Express
                fig = px.bar(
                    publicacoes_mensais,
                    x="Mês/Ano",
                    y="Quantidade",
                    title="Publicações Mensais",
                    labels={
                        "Mês/Ano": "Mês/Ano",
                        "Quantidade": "Quantidade de Publicações",
                    },
                    height=400,
                )
                
                

                

                col1, col2 = st.columns(2)
                with col1:
                    # Exibir o gráfico no Streamlit
                    st.plotly_chart(fig)

                with col2:
                    # Exibir o resumo das publicações mensais
                    st.subheader("Publicações Mensais Resumidas")
                    st.table(publicacoes_mensais)


    except pymysql.MySQLError as e:
        st.error(f"Erro na conexão com o banco de dados: {e}")


main()