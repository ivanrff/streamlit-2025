import streamlit as st
import pandas as pd


def calc_general_stats(df):
    df_data = df.groupby(by="Data")[["Valor"]].sum()
    df_data["lag_1"] = df_data["Valor"].shift(1)
    df_data["Diferença Mensal Abs."] = df_data["Valor"] - df_data["lag_1"]
    df_data["Média 6M Diferença Mensal Abs."] = df_data["Diferença Mensal Abs."].rolling(6).mean()
    df_data["Média 12M Diferença Mensal Abs."] = df_data["Diferença Mensal Abs."].rolling(12).mean()
    df_data["Média 24M Diferença Mensal Abs."] = df_data["Diferença Mensal Abs."].rolling(24).mean()

    df_data["Diferença Mensal Rel."] = df_data["Valor"] / df_data["lag_1"] - 1

    df_data["Evolução 6M Total"] = df_data["Valor"].rolling(6).apply(lambda x: x[-1] - x[0])
    df_data["Evolução 12M Total"] = df_data["Valor"].rolling(12).apply(lambda x: x[-1] - x[0])
    df_data["Evolução 24M Total"] = df_data["Valor"].rolling(24).apply(lambda x: x[-1] - x[0])

    df_data["Evolução 6M Relativa"] = df_data["Valor"].rolling(6).apply(lambda x: x[-1] / x[0] - 1)
    df_data["Evolução 12M Relativa"] = df_data["Valor"].rolling(12).apply(lambda x: x[-1] / x[0] - 1)
    df_data["Evolução 24M Relativa"] = df_data["Valor"].rolling(24).apply(lambda x: x[-1] / x[0] - 1)

    df_data.drop("lag_1", axis=1)

    return df_data

# emojis para icones https://streamlit-emoji-shortcodes-streamlit-app-gwckff.streamlit.app/
st.set_page_config(page_title="Finanças", page_icon="💰")

st.markdown("""
# Boas vindas!
            
## Nosso APP Financeiro

Espero que você curta a experiência da nossa solução para organização financeira

""")

# Widget de upload de arquivo
file_upload = st.file_uploader(label="Faça upload dos dados aqui", type=['csv'])

# Verifica se algum arquivo foi feito upload
if file_upload:

    # Leitura dos dados
    df = pd.read_csv(file_upload)
    df["Data"] = pd.to_datetime(df["Data"], format="%d/%m/%Y").dt.date

    # Exibição dos dados no App
    exp1 = st.expander("Dados Brutos")
    columns_fmt = {"Valor": st.column_config.NumberColumn("Valor", format="R$ %.2f")}
    exp1.dataframe(df, hide_index=True, column_config=columns_fmt)

    # Visão Instituição
    exp2 = st.expander("Instituições")
    df_instituicao = df.pivot_table(index="Data", columns="Instituição", values="Valor")

    tab_data, tab_history, tab_share = exp2.tabs(["Dados", "Histórico", "Distribuição"])

    with tab_data:
        st.dataframe(df_instituicao)

    with tab_history:
        st.line_chart(df_instituicao)

    with tab_share:

        date = st.date_input("Data para Distribuição", min_value=df_instituicao.index.min(), max_value=df_instituicao.index.max())

        if date not in df_instituicao.index:
            st.warning("Entre com uma data válida")
        else:
            st.bar_chart(df_instituicao.loc[date])


    exp3 = st.expander("Estatísticas Gerais")

    df_stats = calc_general_stats(df)
    columns_config = {
        "Valor": st.column_config.NumberColumn("Valor", format="R$ %.2f"),
        "Diferença Mensal Abs.": st.column_config.NumberColumn("Diferença Mensal Abs.", format="R$ %.2f"),
        "Média 6M Diferença Mensal Abs.": st.column_config.NumberColumn("Média 6M Diferença Mensal Abs.", format="R$ %.2f"),
        "Média 12M Diferença Mensal Abs.": st.column_config.NumberColumn("Média 12M Diferença Mensal Abs.", format="R$ %.2f"),
        "Média 24M Diferença Mensal Abs.": st.column_config.NumberColumn("Média 24M Diferença Mensal Abs.", format="R$ %.2f"),
        "Evolução 6M Total": st.column_config.NumberColumn("Evolução 6M Total", format="R$ %.2f"),
        "Evolução 12M Total": st.column_config.NumberColumn("Evolução 12M Total", format="R$ %.2f"),
        "Evolução 24M Total": st.column_config.NumberColumn("Evolução 24M Total", format="R$ %.2f"),
        "Diferença Mensal Rel.": st.column_config.NumberColumn("Diferença Mensal Rel.", format='percent'),
        "Evolução 6M Relativa": st.column_config.NumberColumn("Evolução 6M Relativa", format='percent'),
        "Evolução 12M Relativa": st.column_config.NumberColumn("Evolução 12M Relativa", format='percent'),
        "Evolução 24M Relativa": st.column_config.NumberColumn("Evolução 24M Relativa", format='percent')
    }

    tab_stats, tab_abs, tab_rel = exp3.tabs(tabs=["Dados", "Histórico de Evolução", "Crescimento Relativo"])

   
    with tab_stats:
        st.dataframe(df_stats, column_config=columns_config)

    with tab_abs:
        abs_cols = [
            "Diferença Mensal Abs.",
            "Média 6M Diferença Mensal Abs.",
            "Média 12M Diferença Mensal Abs.",
            "Média 24M Diferença Mensal Abs."
        ]
        st.line_chart(df_stats[abs_cols])

    with tab_rel:
        rel_cols = [
            "Diferença Mensal Rel.",
            "Evolução 6M Relativa",
            "Evolução 12M Relativa",
            "Evolução 24M Relativa"
        ]
        st.line_chart(df_stats[rel_cols])

    with st.expander("Metas"):
        col1, col2 = st.columns(2)

        data_inicio_meta = col1.date_input("Início de Meta", max_value=df_stats.index.max()) # a data só pode ser no máximo a ultima data dos dados
        data_filtrada = df_stats.index[df_stats.index <= data_inicio_meta][-1]

        custos_fixos = col1.number_input("Custos Fixos", min_value=0., format="%.2f")
        salario_bruto = col2.number_input("Salário Bruto", min_value=0., format="%.2f")
        salario_liq = col2.number_input("Salário Líquido", min_value=0., format="%.2f")

        valor_inicio = df_stats.loc[data_filtrada]["Valor"]
        col1.markdown(f"**Valor do Início da Meta**: R$ {valor_inicio:.2f}")

        col1_pot, col2_pot = st.columns(2)
        mensal = salario_liq - custos_fixos
        anual = mensal * 12
        
        with col1_pot.container(border=True):
            st.markdown(f"**Potencial Arrecadação Mês**:\n\n R$ {mensal:.2f}")
        with col2_pot.container(border=True):
            st.markdown(f"**Potencial Arrecadação Ano**:\n\n R$ {anual:.2f}")

        col1_meta, col2_meta = st.columns(2)
        with col1_meta:
            meta_estipulada = st.number_input("Meta Estipulada", min_value=0., format="%.2f", value=anual)

        with col2_meta:
            patrimonio_final = meta_estipulada + valor_inicio
            st.markdown(f"Patrimônio Estimado pós meta: \n\n R$ {patrimonio_final:.2f}")


# Não tem arquivos . . .