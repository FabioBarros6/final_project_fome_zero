import pandas as pd
import inflection
import streamlit as st
import folium
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

st.set_page_config(page_title="Home", page_icon="📊", layout="wide")

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

st.markdown('# Fome Zero!')
st.markdown('## O Melhor lugar para encontrar seu mais novo restaurante favorito!')
st.markdown('### Temos as seguintes marcas dentro da nossa plataforma:')

restaurants, countries, cities, ratings, cuisines = st.columns(5)

restaurants.metric(
    "Restaurantes Cadastrados",
    len(df1.loc[:, 'restaurant'].unique())
)

countries.metric(
    "Países Cadastrados",
    df1.loc[:, 'country'].nunique()
)

cities.metric(
    "Cidades Cadastrados",
    df1.loc[:, 'city'].nunique()
)

ratings.metric(
    "Avaliações Feitas na Plataforma",
    df1.loc[:, 'votes'].sum()
)

cuisines.metric(
    "Tipos de Culinárias Oferecidas",
    df1.loc[:, 'cuisines'].nunique()
)


### MAPA

f = folium.Figure(width=1920, height=1080)

m = folium.Map(max_bounds=True).add_to(f)

marker_cluster = MarkerCluster().add_to(m)

for _, line in df1.iterrows():

    name = line["restaurant_name"]
    price_for_two = line["average_cost_for_two"]
    cuisine = line["cuisines"]
    currency = line["currency"]
    rating = line["aggregate_rating"]
    color = f'{line["color_name"]}'

    html = "<p><strong>{}</strong></p>"
    html += "<p>Price: {},00 ({}) para dois"
    html += "<br />Type: {}"
    html += "<br />Aggragate Rating: {}/5.0"
    html = html.format(name, price_for_two, currency, cuisine, rating)

    popup = folium.Popup(
        folium.Html(html, script=True),
        max_width=500,
    )

    folium.Marker(
        [line["latitude"], line["longitude"]],
        popup=popup,
        icon=folium.Icon(color=color, icon="home", prefix="fa"),
    ).add_to(marker_cluster)

folium_static(m, width=1024, height=768)