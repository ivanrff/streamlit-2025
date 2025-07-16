import streamlit as st
import pandas as pd

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

# Não tem arquivos . . .