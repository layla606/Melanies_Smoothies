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
if title:
    st.write("The name on your smoothie will be:", title)

# --- Get Snowflake session ---
sf_config = st.secrets["Snowflake"]
session = Session.builder.configs(sf_config).create()

# --- Load fruit options from Snowflake ---
my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"), col('SEARCH_ON'))

# Convert Snowpark DataFrame to Pandas
pd_df = my_dataframe.to_pandas()
st.subheader("Available Fruits")
st.dataframe(pd_df, use_container_width=True)

# --- Convert DataFrame to list for multiselect ---
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

        st.subheader(fruit_chosen + ' Nutrition Information (Smoothiefroot)')
        smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")
        if smoothiefroot_response.status_code == 200:
            st.dataframe(smoothiefroot_response.json(), use_container_width=True)
        else:
            st.warning(f"No Smoothiefroot data found for {fruit_chosen}.")

    ingredients_string = ingredients_string.strip()

# Create SQL insert statement
my_insert_stmt = """
    INSERT INTO smoothies.public.orders(ingredients, name_on_order)
    VALUES (:ingredients, :title)
"""

# Button to submit the order
if st.button("Submit order"):
    if not ingredients_string or not title:
        st.error("Please select ingredients and enter a name before submitting!")
    else:
        # Correct way to bind parameters in Snowpark
        session.sql(my_insert_stmt).bind({"ingredients": ingredients_string, "title": title}).collect()
        st.success(f"✅ Your Smoothie is ordered! {title}")

