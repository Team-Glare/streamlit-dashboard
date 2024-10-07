import os
import dotenv
import pandas as pd
import plotly.express as px
import pymysql
import streamlit as st

st.set_page_config(layout="wide")

# Título da página
st.title("Estatística - PROCON :bar_chart:")

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
        cursor = conn.cursor()

        # Executar a consulta SQL com JOIN para obter o nome do procurador (coluna `name`)
        cursor.execute(
            """
            SELECT a.*, u.name 
            FROM ANDAMENTOS a
            JOIN users u ON a.user_id = u.id
            WHERE a.nome_procuradoria = 'PROCON'
            """
        )
        resultados = cursor.fetchall()
        colunas = [desc[0] for desc in cursor.description]

        # Criar um DataFrame a partir dos resultados e nomes de colunas
        dados = pd.DataFrame(resultados, columns=colunas)

        # Fechar a conexão com o banco de dados
        conn.close()

        # Calcular o total de publicações
        total_publicacoes = len(dados)
        st.metric(label="Quantidade Total", value=total_publicacoes)

        # Verifica se há uma coluna 'datapub' no formato adequado
        if "datapub" in dados.columns:
            dados["datapub"] = pd.to_datetime(dados["datapub"])
            dados["mes_ano"] = dados["datapub"].dt.to_period("M").astype(str)

            # Contar o número de publicações por mês
            publicacoes_mensais = (
                dados.groupby("mes_ano").size().reset_index(name="Quantidade")
            )

            # Criar gráfico de barras com Plotly Express
            fig = px.bar(
                publicacoes_mensais,
                x="mes_ano",
                y="Quantidade",
                title="Publicações Mensais",
                labels={
                    "mes_ano": "Mês/Ano",
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

        # Exibir tabela com nome do procurador (coluna `name`) e mês/ano
        st.table(dados[['name', 'mes_ano']])

    except pymysql.MySQLError as e:
        st.error(f"Erro na conexão com o banco de dados: {e}")


main()
