# Import Python packages 
import streamlit as st
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col
import requests
import pandas as pd

# --- App title ---
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# --- Input for smoothie name ---
title = st.text_input("Name on Smoothie")
st.write("The name on your smoothie will be:", title)

# --- Get Snowflake session ---
sf_config = st.secrets["Snowflake"]
session = Session.builder.configs(sf_config).create()

# --- Load fruit options from Snowflake ---
my_dataframe = session.table("smoothies.public.fruit_options").select(
    col("FRUIT_NAME"), 
    col("SEARCH_ON")
)

# Convert the Snowpark DataFrame to a Pandas DataFrame
pd_df = my_dataframe.to_pandas()

# --- Convert DataFrame to Python list ---
fruit_options = pd_df["FRUIT_NAME"].tolist()

# --- Multiselect for ingredients ---
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_options,   # FIX: liste de strings
    max_selections=5
)

# --- Example external API call ---
smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

# --- Handle selected ingredients ---
if ingredients_list:
    # Construire une chaîne d’ingrédients propre
    ingredients_string = ", ".join(ingredients_list)

    for fruit_chosen in ingredients_list:
        # Récupérer la valeur SEARCH_ON pour l’API Fruityvice
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]

        st.subheader(fruit_chosen + " Nutrition Information")
        fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + search_on)
        fv_df = st.dataframe(data=fruityvice_response.json(), use_container_width=True)

    # SQL insert statement avec bind parameters
    my_insert_stmt = """
        INSERT INTO smoothies.public.orders(ingredients, name_on_order)
        VALUES (:ingredients, :title)
    """

    # Display SQL preview (optionnel)
    st.write("SQL preview:")
    st.code(f"INSERT INTO smoothies.public.orders(ingredients, name_on_order) VALUES ('{ingredients_string}', '{title}')")

    # Bouton pour soumettre la commande
    if st.button("Submit order"):
        session.sql(my_insert_stmt, {"ingredients": ingredients_string, "title": title}).collect()
        st.success(f"✅ Your Smoothie is ordered! {title}")
