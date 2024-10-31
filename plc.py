"""Dashboard do projeto."""

import os
import datetime
import dotenv
import pandas as pd
import plotly.express as px  # type: ignore  # noqa: PGH003
import pymysql
import streamlit as st
from pyecharts.charts import Bar
from pyecharts import options as opts
from streamlit_echarts import st_pyecharts

st.set_page_config(layout="wide")

# Título da página
st.title("Estatística da procuradoria Licitações e Contratos - PLC - 2024 :bar_chart:")

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
            'Luís Fernando da Costa',
            'Glaucus Cerqueira Barreto',
            'Gabriela Abramides',
            'Jean Almeida do Vale',
            'João Paulo Gregório Canelas'
        ]
        
        cursor = conn.cursor()

        # Executar a consulta SQL
        cursor.execute(
            "SELECT * FROM ANDAMENTOS WHERE nome_procuradoria='PLC'",
        )
        resultados = cursor.fetchall()
        colunas = [desc[0] for desc in cursor.description]
        dados = pd.DataFrame(resultados, columns=colunas)
        dados = dados[dados['name'].isin(names)]

        # Fechar a conexão com o banco de dados
        conn.close()
        
        with st.sidebar:
            st.subheader("Filtro de Data")
            start_date, end_date = st.date_input("Selecione o intervalo de datas:", [datetime.datetime(2024,5,15), datetime.datetime.today()])
                
            st.subheader("Filtro de Nome")
            selected_names = st.multiselect("Selecione o(s) nome(s):", options=names, default=names)
            
            # Aplicar o filtro de data
        if 'datapub' in dados.columns:
            dados["datapub"] = pd.to_datetime(dados["datapub"])
            if start_date and end_date:
                dados = dados[(dados['datapub'] >= datetime.datetime(start_date.year, start_date.month, start_date.day)) &
                            (dados['datapub'] <= datetime.datetime(end_date.year, end_date.month, end_date.day))]
        else:
            st.warning("A coluna 'datapub' não foi encontrada nos dados de citações.")
            
        # Aplicar o filtro de nome
        if selected_names:
            dados = dados[dados['name'].isin(selected_names)]

        # Calcular o total de publicações
        total_publicacoes = len(dados)
        st.metric(label="Quantidade Total", value=total_publicacoes)

        # Verifica se há uma coluna 'datapub' no formato adequado
        if "datapub" in dados.columns:
                dados["mes_ano"] = dados["datapub"].dt.to_period("M").astype(str)
                
                publicacoes_mensais = (
                    dados.groupby(["mes_ano", "name"]).size().reset_index(name="quantidade")
                )
                
                publicacoes_por_usuario = dados['name'].value_counts().reset_index()
                publicacoes_por_usuario.columns = ['Nome', 'Quantidade']
                
                fig_pizza = px.pie(
                    publicacoes_por_usuario,
                    names='Nome',
                    values='Quantidade',
                    title="Distribuição de Publicações por Usuário",
                    hole=0.4,
                )

                bar = (
                    Bar()
                    .add_xaxis(list(publicacoes_mensais["mes_ano"].unique()))
                    .add_yaxis(
                        "Quantidade de Publicações",
                        publicacoes_mensais.groupby("mes_ano")["quantidade"].sum().tolist()
                    )
                    .set_global_opts(
                        title_opts=opts.TitleOpts(title="Publicações Mensais", subtitle="Total por mês"),
                        toolbox_opts=opts.ToolboxOpts(),
                    )
                )

                col1, col2 = st.columns(2)
                with col1:
                    st.plotly_chart(fig_pizza, height=500)
                with col2:
                    st_pyecharts(bar)

                fig_barras_plotly = px.bar(
                    publicacoes_mensais,
                    x="mes_ano",
                    y="quantidade",
                    color="name",
                    title="Publicações Mensais por Usuário",
                    text_auto=True,
                    labels={"mes_ano": "Mês e Ano", "quantidade": "Quantidade", "name": "Nome"},
                )

                st.subheader("Gráfico de Barras")
                st.plotly_chart(fig_barras_plotly, use_container_width=True)
                st.subheader("Tabela de Quantitativo Mensal")
                st.dataframe(publicacoes_mensais)

    except pymysql.MySQLError as e:
        st.error(f"Erro na conexão com o banco de dados: {e}")


main()