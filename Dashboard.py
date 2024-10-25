# ... código de importação e configuração permanece o mesmo ...

def main() -> None:
    # Conexão e outras configurações
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

                # Filtro por mês e ano
                meses_disponiveis = sorted(dados["mes_ano"].unique())
                mes_selecionado = st.selectbox("Selecione o Mês/Ano", meses_disponiveis)

                # Filtrar os dados com base no mês selecionado
                dados_filtrados = dados[dados["mes_ano"] == mes_selecionado]

                publicacoes_mensais = (
                    dados_filtrados.groupby(["mes_ano", "name"]).size().reset_index(name="quantidade")
                )

                # Gráfico de pizza com Plotly
                publicacoes_por_usuario = dados_filtrados['name'].value_counts().reset_index()
                publicacoes_por_usuario.columns = ['Nome', 'Quantidade']

                fig_pizza = px.pie(
                    publicacoes_por_usuario,
                    names='Nome',
                    values='Quantidade',
                    title=f"Distribuição de Publicações por Usuário (Citações - {mes_selecionado})",
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
                        title_opts=opts.TitleOpts(title=f"Publicações Mensais (Citações) - {mes_selecionado}", subtitle="Total por mês"),
                        toolbox_opts=opts.ToolboxOpts(),
                    )
                )
                
                # Exibir gráficos lado a lado
                col1, col2 = st.columns(2)
                with col1:
                    st.plotly_chart(fig_pizza, height=500)
                with col2:
                    st_pyecharts(bar, key="echarts_citacoes")

                # Gráfico de barras com Plotly
                fig_barras_plotly = px.bar(
                    publicacoes_mensais,
                    x="mes_ano",
                    y="quantidade",
                    color="name",
                    title=f"Publicações Mensais por Usuário (Citações - {mes_selecionado})",
                    text_auto=True,
                    labels={"mes_ano": "Mês e Ano",
                            "quantidade": "Quantidade",
                            "name": "Nome"},  
                )

                st.subheader(f"Gráfico de Barras (Citações - {mes_selecionado})")
                st.plotly_chart(fig_barras_plotly, use_container_width=True)
                st.subheader(f"Tabela de Quantitativo Mensal (Citações - {mes_selecionado})")
                st.dataframe(publicacoes_mensais)

        # Repita o mesmo processo para a aba de intimações
        with tabs[1]:
            dados = intimacoes_dados
            total_publicacoes = len(dados)
            st.metric(label="Quantidade Total", value=total_publicacoes)

            if "datapub" in dados.columns:
                dados["datapub"] = pd.to_datetime(dados["datapub"])
                dados["mes_ano"] = dados["datapub"].dt.to_period("M").astype(str)

                meses_disponiveis = sorted(dados["mes_ano"].unique())
                mes_selecionado = st.selectbox("Selecione o Mês/Ano", meses_disponiveis, key="intimacoes_mes")

                dados_filtrados = dados[dados["mes_ano"] == mes_selecionado]

                publicacoes_mensais = (
                    dados_filtrados.groupby(["mes_ano", "name"]).size().reset_index(name="quantidade")
                )

                publicacoes_por_usuario = dados_filtrados['name'].value_counts().reset_index()
                publicacoes_por_usuario.columns = ['Nome', 'Quantidade']

                fig_pizza = px.pie(
                    publicacoes_por_usuario,
                    names='Nome',
                    values='Quantidade',
                    title=f"Distribuição de Publicações por Usuário (Intimações - {mes_selecionado})",
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
                        title_opts=opts.TitleOpts(title=f"Publicações Mensais (Intimações) - {mes_selecionado}", subtitle="Total por mês"),
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
                    title=f"Publicações Mensais por Usuário (Intimações - {mes_selecionado})",
                    text_auto=True,
                    labels={"mes_ano": "Mês e Ano",
                            "quantidade": "Quantidade",
                            "name": "Nome"}, 
                )

                st.subheader(f"Gráfico de Barras (Intimações - {mes_selecionado})")
                st.plotly_chart(fig_barras_plotly, use_container_width=True)
                st.subheader(f"Tabela de Quantitativo Mensal (Intimações - {mes_selecionado})")
                st.dataframe(publicacoes_mensais)

    except pymysql.MySQLError as e:
        st.error(f"Erro na conexão com o banco de dados: {e}")

main()
