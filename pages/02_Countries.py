import pandas as pd
import inflection
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from folium.plugins import MarkerCluster
from streamlit_folium import folium_static

from PIL import Image

### -------------------------
### TRATAMENTO DOS DADOS 
### -------------------------
RAW_DATA_PATH = r"C:/Users/fabio/OneDrive/Estudos/Data Science - Comunidade DS/Analisando Dados com Python/Ciclo 8 - Projeto do Aluno/dataset/zomato.csv"

COUNTRIES = {
    1: "India",
    14: "Australia",
    30: "Brazil",
    37: "Canada",
    94: "Indonesia",
    148: "New Zeland",
    162: "Philippines",
    166: "Qatar",
    184: "Singapure",
    189: "South Africa",
    191: "Sri Lanka",
    208: "Turkey",
    214: "United Arab Emirates",
    215: "England",
    216: "United States of America",
}


COLORS = {
    "3F7E00": "darkgreen",
    "5BA829": "green",
    "9ACD32": "lightgreen",
    "CDD614": "orange",
    "FFBA00": "red",
    "CBCBC8": "darkred",
    "FF7800": "darkred",
}

#Renomear colunas
def rename_columns(df):
    df1 = df.copy()
    title = lambda x: inflection.titleize(x)
    snakecase = lambda x: inflection.underscore(x)
    spaces = lambda x: x.replace(" ", "")
    cols_old = list(df.columns)
    cols_old = list(map(title, cols_old))
    cols_old = list(map(spaces, cols_old))
    cols_new = list(map(snakecase, cols_old))
    df1.columns = cols_new
    return df1

def country_name(country_id):
    return COUNTRIES[country_id]

def color_name(color_code):
    return COLORS[color_code]

#Criação do Tipo de Categoria de Comida
def create_price_tye(price_range):
    if price_range == 1:
        return "cheap"
    elif price_range == 2:
        return "normal"
    elif price_range == 3:
        return "expensive"
    else:
        return "gourmet"

def adjust_columns_order(df):
    df1 = df.copy()

    new_cols_order = [
        "restaurant_id",
        "restaurant_name",
        "country",
        "city",
        "address",
        "locality",
        "locality_verbose",
        "longitude",
        "latitude",
        "cuisines",
        "price_type",
        "average_cost_for_two",
        "currency",
        "has_table_booking",
        "has_online_delivery",
        "is_delivering_now",
        "aggregate_rating",
        "rating_color",
        "color_name",
        "rating_text",
        "votes",
    ]

    return df1.loc[:, new_cols_order]

def process_data(file_path):
    df1 = pd.read_csv(file_path)

    df1 = df1.dropna()

    df1 = rename_columns(df1)

    df1["price_type"] = df1.loc[:, "price_range"].apply(lambda x: create_price_tye(x))

    df1["country"] = df1.loc[:, "country_code"].apply(lambda x: country_name(x))

    df1["color_name"] = df1.loc[:, "rating_color"].apply(lambda x: color_name(x))

    df1["cuisines"] = df1.loc[:, "cuisines"].astype(str).apply(lambda x: x.split(",")[0])
        
    df1 = df1.drop_duplicates()

    df1 = adjust_columns_order(df1)

    df1.to_csv(r"C:/Users/fabio/OneDrive/Estudos/Data Science - Comunidade DS/Analisando Dados com Python/Ciclo 8 - Projeto do Aluno/dataset/zomato.csv", index=False)

    return df1

df_raw = pd.read_csv(RAW_DATA_PATH)
df_raw.head()

df1 = df_raw.copy()

df1 = rename_columns(df1)

### -------------------------
### FIM TRATAMENTO DOS DADOS 
### -------------------------

################
# FUNÇÕES
################

def quant_restaurantes_pais(df1):
    grouped_df = (
        df1.loc[df1["country"].isin(countries), ["restaurant", "country"]]
        .groupby("country")
        .count()
        .sort_values("restaurant", ascending=False)
        .reset_index()
    )

    fig = px.bar(
        grouped_df,
        x="country",
        y="restaurant",
        text="restaurant",
        title="Quantidade de Restaurantes Registrados por País",
        labels={
            "country": "Paises",
            "restaurant": "Quantidade de Restaurantes",
        },
    )
    
    return fig

def quant_cidade_pais(df1):
    grouped_df = (
        df1.loc[df1["country"].isin(countries), ["city", "country"]]
        .groupby("country")
        .nunique()
        .sort_values("city", ascending=False)
        .reset_index()
    )

    fig = px.bar(
        grouped_df,
        x="country",
        y="city",
        text="city",
        title="Quantidade de Cidade Registrados por País",
        labels={
            "country": "Paises",
            "city": "Quantidade de Cidades",
        },
    )
    
    return fig

def media_votos(df1):
    grouped_df = (
        df1.loc[df1["country"].isin(countries), ["votes", "country"]]
        .groupby("country")
        .mean()
        .sort_values("votes", ascending=False)
        .reset_index()
    )
    
    fig = px.bar(
        grouped_df,
        x="country",
        y="votes",
        text="votes",
        text_auto=".2f",
        title="Média de Avaliações feitas por País",
        labels={
            "country": "Paises",
            "votes": "Quantidade de Avaliações",
        },
    )
    
    return fig

def media_preco_para_dois(df1):
    grouped_df = (
        df1.loc[df1["country"].isin(countries), ["average_cost_for_two", "country"]]
        .groupby("country")
        .mean()
        .sort_values("average_cost_for_two", ascending=False)
        .reset_index()
    )

    fig = px.bar(
        grouped_df,
        x="country",
        y="average_cost_for_two",
        text="average_cost_for_two",
        text_auto=".2f",
        title="Média de Preço de um prato para duas pessoas por País",
        labels={
            "country": "Paises",
            "average_cost_for_two": "Preço de prato para duas Pessoas",
        },
    )

    return fig

#### FIM DAS FUNÇÔES

st.set_page_config(page_title="Countries", page_icon="🌍", layout="wide")

### BARRA LATERAL STREAMLIT

image_path = "./img/"
image = Image.open(image_path + "logo.png")

col1, col2 = st.sidebar.columns([1, 4], gap="small")
col1.image(image, width=35)
col2.markdown("# Fome Zero")

st.sidebar.markdown("## Filtros")

countries = st.sidebar.multiselect(
    "Escolha os Paises que Deseja visualizar os Restaurantes",
    df1.loc[:, "country"].unique().tolist(),
    default=["Brazil", "England", "Qatar", "South Africa", "Canada", "Australia"],
)


### LAYOUT STREAMLIT

st.markdown('# :earth_americas: Visão Países')

#Gráfico 1
fig = quant_restaurantes_pais(df1)
st.plotly_chart(fig, use_container_width=True)

#Gráfico 2
fig = quant_cidade_pais(df1)
st.plotly_chart(fig, use_container_width=True)

#Gráficos 3 e 4
col1, col2 = st.columns(2)

with col1:
    fig = media_votos(df1)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = media_preco_para_dois(df1)
    st.plotly_chart(fig, use_container_width=True)

