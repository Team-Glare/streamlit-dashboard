import datetime
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
    try:
        if not host or not user or not database:
            st.error("Erro! Faltam informações de conexão com o banco de dados.")
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

        # Verifique os nomes das colunas
        st.write("Colunas de Citações:", citacoes_dados.columns)

        # Consulta para intimações
        cursor.execute(
            "SELECT * FROM ANDAMENTOS WHERE nome_procuradoria='PTB' AND natureza LIKE 'int%' COLLATE utf8mb4_unicode_ci",
        )
        intimacoes = cursor.fetchall()
        colunas = [desc[0] for desc in cursor.description]
        intimacoes_dados = pd.DataFrame(intimacoes, columns=colunas)
        intimacoes_dados = intimacoes_dados[intimacoes_dados['name'].isin(names)]

        # Verifique os nomes das colunas
        st.write("Colunas de Intimações:", intimacoes_dados.columns)

        # Consulta para Assuntos
        cursor.execute("SELECT nome_assunto FROM assunto_especificos")  # Ajuste se a coluna tiver outro nome
        assuntos = cursor.fetchall()
        assuntos = [a[0] for a in assuntos]  # Converta para uma lista
        assuntos.insert(0, "Todos")  # Adiciona a opção "Todos"

        conn.close()

        # Filtro de data para citações
        # Dentro da aba "Citações"
        with tabs[0]:
            dados = citacoes_dados
            
            with st.sidebar:
                st.subheader("Filtro de Data (Citações)")
                start_date, end_date = st.date_input("Selecione o intervalo de datas:", [datetime.datetime(2024,5,15), datetime.datetime.today()], key='cit_date_input')
                
                st.subheader("Filtro de Nome (Citações)")
                selected_names = st.multiselect("Selecione o(s) nome(s):", options=names, default=names, key='cit_multiselect')

                st.subheader("Filtro de Assunto (Citações)")
                selected_assunto = st.selectbox("Selecione um assunto:", options=assuntos, key='cit_selectbox')

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

            # Aplicar o filtro de assunto
            if selected_assunto != "Todos":
                dados = dados[dados['nome_assunto'].str.contains(selected_assunto, na=False)]  # Altere 'assunto' para 'nome_assunto'

            total_publicacoes = len(dados)
            st.metric(label="Quantidade Total", value=total_publicacoes)

            # Gráficos e tabelas com dados filtrados por nome e data
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
                    title="Distribuição de Publicações por Usuário (Citações)",
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
                        title_opts=opts.TitleOpts(title="Publicações Mensais (Citações)", subtitle="Total por mês"),
                        toolbox_opts=opts.ToolboxOpts(),
                    )
                )

                col1, col2 = st.columns(2)
                with col1:
                    st.plotly_chart(fig_pizza, height=500)
                with col2:
                    st_pyecharts(bar, key="echarts_citacoes")

                fig_barras_plotly = px.bar(
                    publicacoes_mensais,
                    x="mes_ano",
                    y="quantidade",
                    color="name",
                    title="Publicações Mensais por Usuário (Citações)",
                    text_auto=True,
                    labels={"mes_ano": "Mês e Ano", "quantidade": "Quantidade", "name": "Nome"},
                )

                st.subheader("Gráfico de Barras (Citações)")
                st.plotly_chart(fig_barras_plotly, use_container_width=True)
                st.subheader("Tabela de Quantitativo Mensal (Citações)")
                st.dataframe(publicacoes_mensais)


        # Filtro de data para intimações
        with tabs[1]:
            dados = intimacoes_dados
            
            with st.sidebar:
                st.subheader("Filtro de Data (Intimações)")
                start_date, end_date = st.date_input("Selecione o intervalo de datas:", [datetime.datetime(2024,5,15), datetime.datetime.today()], key='int_date_input')
                
                st.subheader("Filtro de Nome (Intimações)")
                selected_names = st.multiselect("Selecione o(s) nome(s):", options=names, default=names, key='int_multiselect')

                st.subheader("Filtro de Assunto (Intimações)")
                selected_assunto = st.selectbox("Selecione um assunto:", options=assuntos, key='int_selectbox')

            if 'datapub' in dados.columns:
                dados["datapub"] = pd.to_datetime(dados["datapub"])
                if start_date and end_date:
                    dados = dados[(dados['datapub'] >= datetime.datetime(start_date.year, start_date.month, start_date.day)) &
                                  (dados['datapub'] <= datetime.datetime(end_date.year, end_date.month, end_date.day))]
            else:
                st.warning("A coluna 'datapub' não foi encontrada nos dados de intimações.")
                
            if selected_names:
                dados = dados[dados['name'].isin(selected_names)]
                
            # Aplicar o filtro de assunto
            if selected_assunto != "Todos":
                dados = dados[dados['nome_assunto'].str.contains(selected_assunto, na=False)]  # Altere 'assunto' para 'nome_assunto'
            
            total_publicacoes = len(dados)
            st.metric(label="Quantidade Total", value=total_publicacoes)

            if "datapub" in dados.columns:
                dados["datapub"] = pd.to_datetime(dados["datapub"])
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
                    title="Distribuição de Publicações por Usuário (Intimações)",
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
                        title_opts=opts.TitleOpts(title="Publicações Mensais (Intimações)", subtitle="Total por mês"),
                        toolbox_opts=opts.ToolboxOpts(),
                    )
                )

                col1, col2 = st.columns(2)
                with col1:
                    st.plotly_chart(fig_pizza, height=500)
                with col2:
                    st_pyecharts(bar, key="echarts_intimacoes")

                fig_barras_plotly = px.bar(
                    publicacoes_mensais,
                    x="mes_ano",
                    y="quantidade",
                    color="name",
                    title="Publicações Mensais por Usuário (Intimações)",
                    text_auto=True,
                    labels={"mes_ano": "Mês e Ano", "quantidade": "Quantidade", "name": "Nome"},
                )

                st.subheader("Gráfico de Barras (Intimações)")
                st.plotly_chart(fig_barras_plotly, use_container_width=True)
                st.subheader("Tabela de Quantitativo Mensal (Intimações)")
                st.dataframe(publicacoes_mensais)

    except Exception as e:
        st.error(f"Ocorreu um erro: {e}")

if __name__ == "__main__":
    main()
