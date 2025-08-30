# Import Python packages
import streamlit as st
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col

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
my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"))
fruit_list = my_dataframe.collect()
fruit_options = [row["FRUIT_NAME"] for row in fruit_list]  # Convert DataFrame to Python list

# --- Multiselect for ingredients ---
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_options,  # Use Python list, not DataFrame
    max_selections=5
)

# --- Handle selected ingredients ---
if ingredients_list:
    # Join fruits into one string
    ingredients_string = " ".join(ingredients_list)

    # Create SQL insert statement
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders(ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{title}')
    """

    st.write("SQL preview:")
    st.code(my_insert_stmt)

    # Button to submit the order
    if st.button("Submit order"):
        session.sql(my_insert_stmt).collect()
        st.success(f"✅ Your Smoothie is ordered! {title}")
