import os
import dotenv
import pandas as pd
import plotly.express as px
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
        
        # Obter os IDs e nomes da tabela 'users'
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM users")
        ids_nomes = cursor.fetchall()
        ids_nomes_df = pd.DataFrame(ids_nomes, columns=["id", "name"])

        # Lista de IDs de interesse
        ids = ids_nomes_df["id"].tolist()
        
        tabs = st.tabs([ "Citações", "Intimações"])
        
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM ANDAMENTOS WHERE nome_procuradoria='PTB' AND natureza LIKE 'int%' COLLATE utf8mb4_unicode_ci",
        )
        intimacoes = cursor.fetchall()
        colunas = [desc[0] for desc in cursor.description]

        intimacoes_dados = pd.DataFrame(intimacoes, columns=colunas)
        intimacoes_dados = intimacoes_dados[intimacoes_dados['id'].isin(ids)]

        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM ANDAMENTOS WHERE nome_procuradoria='PTB' AND natureza LIKE 'cit%' COLLATE utf8mb4_unicode_ci",
        )
        citacoes = cursor.fetchall()
        colunas = [desc[0] for desc in cursor.description]

        citacoes_dados = pd.DataFrame(citacoes, columns=colunas)
        citacoes_dados = citacoes_dados[citacoes_dados['id'].isin(ids)]

        conn.close()
        
        with tabs[0]:
            dados = citacoes_dados
            total_publicacoes = len(dados)
            st.metric(label="Quantidade Total", value=total_publicacoes)

            if "datapub" in dados.columns:
                dados["datapub"] = pd.to_datetime(dados["datapub"])
                dados["mes_ano"] = dados["datapub"].dt.to_period("M").astype(str)

                # Agrupar por 'id' e 'mes_ano' para contar as publicações por pessoa e mês
                publicacoes_mensais = dados.groupby(["mes_ano", "id"]).size().reset_index(name="quantidade")

                # Unir com a tabela de nomes para exibir o nome correto no gráfico
                publicacoes_mensais = publicacoes_mensais.merge(ids_nomes_df, on="id")

                fig = px.bar(
                    publicacoes_mensais,
                    x="mes_ano",
                    y="quantidade",
                    color="name",  # Adiciona cores por nome
                    title="Publicações Mensais por Pessoa",
                    labels={
                        "mes_ano": "Mês/Ano",
                        "quantidade": "Quantidade de Publicações",
                        "name": "Pessoa"
                    },
                    height=400,
                )

                col1, col2 = st.columns(2)
                with col1:
                    st.plotly_chart(fig)

                with col2:
                    st.subheader("Publicações Mensais por Pessoa")
                    st.table(publicacoes_mensais)

        with tabs[1]:
            dados = intimacoes_dados
            total_publicacoes = len(dados)
            st.metric(label="Quantidade Total", value=total_publicacoes)

            if "datapub" in dados.columns:
                dados["datapub"] = pd.to_datetime(dados["datapub"])
                dados["mes_ano"] = dados["datapub"].dt.to_period("M").astype(str)

                publicacoes_mensais = dados.groupby(["mes_ano", "id"]).size().reset_index(name="quantidade")

                # Unir com a tabela de nomes para exibir o nome correto
                publicacoes_mensais = publicacoes_mensais.merge(ids_nomes_df, on="id")

                fig = px.bar(
                    publicacoes_mensais,
                    x="mes_ano",
                    y="quantidade",
                    color="name",
                    title="Intimações Mensais por Pessoa",
                    labels={
                        "mes_ano": "Mês/Ano",
                        "quantidade": "Quantidade de Intimações",
                        "name": "Pessoa"
                    },
                    height=400,
                )

                col1, col2 = st.columns(2)
                with col1:
                    st.plotly_chart(fig)

                with col2:
                    st.subheader("Intimações Mensais por Pessoa")
                    st.table(publicacoes_mensais)

    except pymysql.MySQLError as e:
        st.error(f"Erro na conexão com o banco de dados: {e}")

main()
