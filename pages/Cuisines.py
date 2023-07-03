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
RAW_DATA_PATH = r"dataset/zomato.csv"

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

################
# FUNÇÕES
################

def top_cuisines(df1):
    cuisines = {
        "Italian": "",
        "American": "",
        "Arabian": "",
        "Japanese": "",
        "Brazilian": "",
    }

    cols = [
        "restaurant",
        "restaurant_name",
        "country",
        "city",
        "cuisines",
        "average_cost_for_two",
        "currency",
        "aggregate_rating",
        "votes",
    ]

    for key in cuisines.keys():

        lines = df1["cuisines"] == key

        cuisines[key] = (
            df1.loc[lines, cols]
            .sort_values(["aggregate_rating", "restaurant"], ascending=[False, True])
            .iloc[0, :]
            .to_dict()
        )

    return cuisines

def write_metrics():

    cuisines = top_cuisines(df1)

    italian, american, arabian, japonese, brazilian = st.columns(len(cuisines))

    with italian:
        st.metric(
            label=f'Italiana: {cuisines["Italian"]["restaurant_name"]}',
            value=f'{cuisines["Italian"]["aggregate_rating"]}/5.0',
            help=f"""
            País: {cuisines["Italian"]['country']}\n
            Cidade: {cuisines["Italian"]['city']}\n
            Média Prato para dois: {cuisines["Italian"]['average_cost_for_two']} ({cuisines["Italian"]['currency']})
            """,
        )

    with american:
        st.metric(
            label=f'Italiana: {cuisines["American"]["restaurant_name"]}',
            value=f'{cuisines["American"]["aggregate_rating"]}/5.0',
            help=f"""
            País: {cuisines["American"]['country']}\n
            Cidade: {cuisines["American"]['city']}\n
            Média Prato para dois: {cuisines["American"]['average_cost_for_two']} ({cuisines["American"]['currency']})
            """,
        )

    with arabian:
        st.metric(
            label=f'Italiana: {cuisines["Arabian"]["restaurant_name"]}',
            value=f'{cuisines["Arabian"]["aggregate_rating"]}/5.0',
            help=f"""
            País: {cuisines["Arabian"]['country']}\n
            Cidade: {cuisines["Arabian"]['city']}\n
            Média Prato para dois: {cuisines["Arabian"]['average_cost_for_two']} ({cuisines["Arabian"]['currency']})
            """,
        )

    with japonese:
        st.metric(
            label=f'Italiana: {cuisines["Japanese"]["restaurant_name"]}',
            value=f'{cuisines["Japanese"]["aggregate_rating"]}/5.0',
            help=f"""
            País: {cuisines["Japanese"]['country']}\n
            Cidade: {cuisines["Japanese"]['city']}\n
            Média Prato para dois: {cuisines["Japanese"]['average_cost_for_two']} ({cuisines["Japanese"]['currency']})
            """,
        )

    with brazilian:
        st.metric(
            label=f'Italiana: {cuisines["Brazilian"]["restaurant_name"]}',
            value=f'{cuisines["Brazilian"]["aggregate_rating"]}/5.0',
            help=f"""
            País: {cuisines["Brazilian"]['country']}\n
            Cidade: {cuisines["Brazilian"]['city']}\n
            Média Prato para dois: {cuisines["Brazilian"]['average_cost_for_two']} ({cuisines["Brazilian"]['currency']})
            """,
        )

    return None
    
def top_restaurants(df1, countries, cuisines, top_n):

    cols = [
        "restaurant",
        "restaurant_name",
        "country",
        "city",
        "cuisines",
        "average_cost_for_two",
        "aggregate_rating",
        "votes",
    ]

    lines = (df1["cuisines"].isin(cuisines)) & (df1["country"].isin(countries))

    dataframe = df1.loc[lines, cols].sort_values(
        ["aggregate_rating", "restaurant"], ascending=[False, True]
    )

    return dataframe.head(top_n)

def melhores_cozinhas(df1, countries, top_n):

    lines = df1["country"].isin(countries)

    grouped_df = (
        df1.loc[lines, ["aggregate_rating", "cuisines"]]
        .groupby("cuisines")
        .mean()
        .sort_values("aggregate_rating", ascending=False)
        .reset_index()
        .head(top_n)
    )

    fig = px.bar(
        grouped_df.head(top_n),
        x="cuisines",
        y="aggregate_rating",
        text="aggregate_rating",
        text_auto=".2f",
        title=f"Top {top_n} Melhores Tipos de Culinárias",
        labels={
            "cuisines": "Tipo de Culinária",
            "aggregate_rating": "Média da Avaliação Média",
        },
    )

    return fig

def piores_cozinhas(df1, countries, top_n):

    lines = df1["country"].isin(countries)

    grouped_df = (
        df1.loc[lines, ["aggregate_rating", "cuisines"]]
        .groupby("cuisines")
        .mean()
        .sort_values("aggregate_rating")
        .reset_index()
        .head(top_n)
    )

    fig = px.bar(
        grouped_df.head(top_n),
        x="cuisines",
        y="aggregate_rating",
        text="aggregate_rating",
        text_auto=".2f",
        title=f"Top {top_n} Piores Tipos de Culinárias",
        labels={
            "cuisines": "Tipo de Culinária",
            "aggregate_rating": "Média da Avaliação Média",
        },
    )

    return fig


#### FIM DAS FUNÇÔES

st.set_page_config(page_title="Cuisines", page_icon="🍽️", layout="wide")

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


top_n = st.sidebar.slider(
    "Selecione a quantidade de Restaurantes que deseja visualizar", 1, 20, 10
)

cuisines = st.sidebar.multiselect(
    "Escolha os Tipos de Culinária ",
    df1.loc[:, "cuisines"].unique().tolist(),
    default=[
        "Home-made",
        "BBQ",
        "Japanese",
        "Brazilian",
        "Arabian",
        "American",
        "Italian",
    ],
)

### LAYOUT STREAMLIT

st.markdown('# :knife_fork_plate: Visão Tipos de Cozinhas')
st.markdown('## Melhores Restaurantes dos Principais tipos Culinários')

df_restaurantes = top_restaurants(df1, countries, cuisines, top_n)

write_metrics()

# Dataframe personalizado top restaurantes
st.markdown(f'## Top {top_n} Restaurantes')
st.dataframe(df_restaurantes)

#Gráficos TOP melhores e piores tipos de cozinhas
melhores, piores = st.columns(2)
with melhores:
    fig = melhores_cozinhas(df1, countries, top_n)
    st.plotly_chart(fig, use_container_width=True)

with piores:
    fig = piores_cozinhas(df1, countries, top_n)
    st.plotly_chart(fig, use_container_width=True)

