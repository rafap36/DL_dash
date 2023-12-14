import streamlit as st
import altair as alt
import pandas as pd
from PIL import Image
import streamlit_authenticator as stauth


import yaml
from yaml.loader import SafeLoader
with open('./config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

#CONFIGURAÇÕES DE PÁGINA
st.set_page_config(
  page_title = 'DASHBOARD MAERSK',
  page_icon = ':globe_with_meridians:',
  layout = 'wide',
  initial_sidebar_state = 'expanded',
  menu_items = {
    'About': 'Rec36 property'
  }
)



authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

name, authentication_status, username = authenticator.login('Login', 'main')


if authentication_status:

  cor_grafico = '#33b3ca'




  # criar o dataframe
  @st.cache_resource
  def busca_df():
    df = pd.read_excel(
      io = './Datasets/base.xlsx',
      engine = 'openpyxl',
      sheet_name = 'base1',
      usecols = 'A:I',
      nrows = 93
    )
    return df

  df = busca_df()

  # criar o sidebar
  with st.sidebar:
    logo_teste = Image.open('./Mídia/Logo_DeLuna.png')
    st.image(logo_teste, width=300)
    st.subheader('MENU - DASHBOARD MAERSK')

    fUnidade = st.selectbox(
      'Selecione a unidade:',
      options=df['unidade'].unique()
      )

    fSetor = st.selectbox(
      'Selecione o setor:',
      options=df['setor'].unique()
      )

    # Defina o local para português do Brasil
    #locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')

    # Supondo que 'data' seja a coluna com as datas no DataFrame df
    #df['data'] = pd.to_datetime(df['data']) # Garanta que 'data' seja do tipo datetime
    df['mês'] = df['data'].dt.strftime('%m/%Y')
    # Extrai o nome do mês da coluna 'data'
    #df['mes'] = df['data'].dt.strftime('%B').str.capitalize() # %B formata para o nome completo do mês

    fData = st.selectbox(
      'Selecione a data:',
      options=df['mês'].unique()
      )


  #Cria a tabela 'dataframe que será usada na construção da evolução da quantidade de produtos
  tabela_qtd_produtos = df.loc[
    #(df['data'] == fData)
    #&
    (df['unidade'] == fUnidade)
    &
    (df['setor'] == fSetor)
    ]

  df['mês'] = df['data'].dt.strftime('%m/%Y')
  tabela_qtd_produtos = tabela_qtd_produtos.groupby(['mês'])[['quantidade_produtos', 'setor', 'unidade']].sum().reset_index()


  #Criação do gráfico da quantidade de produtos
  grafico_qtd_produtos = alt.Chart(tabela_qtd_produtos).mark_bar(
    color = cor_grafico,
    cornerRadiusTopLeft = 9,
    cornerRadiusTopRight= 9,
  ).encode(
    x = 'mês',
    y = 'quantidade_produtos',
    tooltip = ['mês', 'quantidade_produtos']
  ).properties(
    title = 'QUANTIDADE SKUS'
    ).configure_axis(
    grid = False
  ).configure_view(
    strokeWidth = 0
  )



  #criação tabela de diferenças
  tabela_diferenca = df.loc[
    #(df['data'] == fData)
    #&
    (df['unidade'] == fUnidade)
    &
    (df['setor'] == fSetor)
    ]

  tabela_diferenca = tabela_diferenca.groupby(['mês'])[['diferença', 'setor', 'unidade', 'produtos_diferença']].sum().reset_index()



  grafico_diferenca = alt.Chart(tabela_diferenca).mark_line(
    color = cor_grafico
  ).encode(
    x = 'mês',
    y = 'diferença',
    tooltip = ['mês', 'diferença']
  ).properties(
    title = 'DIFERENÇA'
  ).configure_axis(
    grid = True
  ).configure_view(
    strokeWidth = 0
  )




  tabela_percentual = df.loc[
    #(df['data'] == fData)
    #&
    (df['unidade'] == fUnidade)
    &
    (df['setor'] == fSetor)
    ]

  tabela_percentual = tabela_percentual.groupby(['mês'])[['percentual']].sum().reset_index()

  grafico_percentual = alt.Chart(tabela_percentual).mark_line(
    color = cor_grafico
  ).encode(
    x = 'mês',
    y = 'percentual',
    tooltip = ['mês', 'percentual']
  ).properties(
    title = 'DIFERENÇA PERCENTUAL'
  ).configure_axis(
    grid = True
  ).configure_view(
    strokeWidth = 0
  )


















  ######  PÁGINA PRINCIPAL ########

  # Faz a filtragem dos dados com base nas variáveis fData, fUnidade e fSetor
  info_home = df[(df['data'] == fData) & (df['unidade'] == fUnidade) & (df['setor'] == fSetor)]

  # Agrupa os dados filtrados por data e realiza a soma das colunas específicas
  info_home = info_home.groupby('data')[['unidades_contadas', 'unidades_fisicas', 'percentual', 'diferença', 'quantidade_produtos', 'produtos_diferença']].sum().reset_index()

  # Calcula a soma total das unidades contadas e unidades físicas, arredondando para duas casas decimais
  unidades_contadas = round(info_home['unidades_contadas'].sum(), 2)
  unidades_fisicas = round(info_home['unidades_fisicas'].sum(), 2)
  diferença = round(info_home['diferença'].sum(), 2)
  quantidade_produtos = round(info_home['quantidade_produtos'].sum(), 2)
  produtos_diferença = round(info_home['produtos_diferença'].sum(), 2)
  # Calcula a soma total da coluna percentual e converte para um número inteiro multiplicando por 100
  diferenca_em_porcentagem = round(info_home['percentual'].sum() * 100, 2)
  st.header("- Inventários Maersk")

  dst1, dst2, dst3 = st.columns([1,1,1])

  with dst1:
    st.write('**UNIDADES CONTADAS:**')
    st.info(f' {unidades_contadas} UN')
    st.write('**SKUS:**')
    st.info(f' {quantidade_produtos} UN')

  with dst2:
    st.write('**UNIDADES FÍSICAS:**')
    st.info(f' {unidades_fisicas} UN')
    st.write('**SKUS COM DIVERGÊNCIA:**')
    st.info(f' {produtos_diferença} UN')

  with dst3:
    st.write('**DIFERENÇA:**')
    st.info(f'{diferença} UN')
    st.write('**DIFERENÇA %:**')
    st.info(f'{diferenca_em_porcentagem}%')

  st.markdown('---')


  col1, col2, col3 = st.columns([1,1,1])

  #with col1:


  #with col2:



  #with col3:
    #st.altair_chart(graf2_vendas_vendedor + rot2Ve + rot2Vp)
  st.altair_chart(grafico_qtd_produtos, use_container_width=True)
  st.altair_chart(grafico_diferenca, use_container_width=True)
  st.altair_chart(grafico_percentual, use_container_width=True)

  st.markdown('---')

  st.markdown(
      """
      <h4 style='text-align: center;'>DB preview</h4>
      """,
      unsafe_allow_html=True
  )

  st.dataframe(df, use_container_width=True)

  st.markdown('---')
  authenticator.logout('Logout', 'sidebar')
elif authentication_status == False:
    st.error('Username/password is incorrect')
elif authentication_status == None:
    st.warning('Please enter your username and password')
