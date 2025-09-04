# Import Python packages
import streamlit as st
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col
import requests

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
my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"), col("SEARCH_ON"))
pd_df = my_dataframe.to_pandas()

# Display available fruits
st.subheader("Available Fruits")
st.dataframe(pd_df, use_container_width=True)

# --- Convert to list for multiselect ---
fruit_options = pd_df["FRUIT_NAME"].tolist()

# --- Multiselect for ingredients ---
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_options,
    max_selections=5
)

# --- Handle selected ingredients ---
if ingredients_list:
    ingredients_string = ""
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "

        # Get the search value from Snowflake
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]

        # Display nutrition info from Fruityvice API
        st.subheader(f"{fruit_chosen} Nutrition Information (Fruityvice)")
        fruityvice_response = requests.get(f"https://fruityvice.com/api/fruit/{fruit_chosen.lower()}")
        if fruityvice_response.status_code == 200:
            st.json(fruityvice_response.json())
        else:
            st.warning(f"No Fruityvice data found for {fruit_chosen}.")

        # Display nutrition info from Smoothiefroot API
        st.subheader(f"{fruit_chosen} Nutrition Information (Smoothiefroot)")
        smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")
        if smoothiefroot_response.status_code == 200:
            st.json(smoothiefroot_response.json())
        else:
            st.warning(f"No Smoothiefroot data found for {fruit_chosen}.")

    # Strip trailing space
    ingredients_string = ingredients_string.strip()

    # SQL insert statement using safe bind parameters
    my_insert_stmt = """
        INSERT INTO smoothies.public.orders(ingredients, name_on_order)
        VALUES (:ingredients, :title)
    """

    # Display SQL preview
    st.write("SQL preview:")
    st.code(f"INSERT INTO smoothies.public.orders(ingredients, name_on_order) VALUES ('{ingredients_string}', '{title}')")

    # Button to submit the order
    if st.button("Submit order"):
        session.sql(my_insert_stmt, {"ingredients": ingredients_string, "title": title}).collect()
        st.success(f"✅ Your Smoothie is ordered! {title}")
