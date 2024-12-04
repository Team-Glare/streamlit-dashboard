"""Dashboard do projeto."""

import os

import dotenv
import pandas as pd
import plotly.express as px  # type: ignore  # noqa: PGH003
import pymysql
import streamlit as st

st.set_page_config(layout="wide")

# Título da página
st.title("Estatística - Ministério Público - MP - 2024 :bar_chart:")


def main() -> None:
    """Start the Streamlit app."""
    try:
        conn = pymysql.connect(
            host='120.77.222.217',
            port=3306,
            user='root',
            password='123456',
            database='address',
        )
        cursor = conn.cursor()

        # Executar a consulta SQL
        cursor.execute(
            "SELECT id, name, email_address FROM contact",
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
