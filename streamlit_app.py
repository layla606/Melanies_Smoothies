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
sf_config = st.secrets["snowflake"]
session = Session.builder.configs(sf_config).create()

# --- Load fruit options from Snowflake ---
my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"), col('SEARCH_ON'))

# Convert the Snowpark DataFrame to a Pandas DataFrame
pd_df = my_dataframe.to_pandas()
#st.dataframe(pd_df)
#st.stop() 

# --- Convert DataFrame to Python list ---
fruit_options = pd_df["FRUIT_NAME"].tolist()

# --- Multiselect for ingredients ---
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_options,  # Fixed: Use the fruit_options list instead of dataframe
    max_selections=5
)

# Fixed: Removed the problematic smoothiefroot API call
# smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
# sf_df= st.dataframe(data=smoothiefroot_response.json(),use_container_width= True)

# --- Handle selected ingredients ---
if ingredients_list:
    ingredients_string = ""  # Fixed: Initialize as empty string
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '    

        # Fixed: Added error handling for missing search terms
        search_result = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON']
        if not search_result.empty:
            search_on = search_result.iloc[0]
            
            st.subheader(fruit_chosen + ' Nutrition Information')
            try:
                fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + search_on)
                if fruityvice_response.status_code == 200:
                    fv_df = st.dataframe(data=fruityvice_response.json(), use_container_width=True)
                else:
                    st.warning(f"Could not fetch nutrition data for {fruit_chosen}")
            except requests.exceptions.RequestException:
                st.warning(f"Could not fetch nutrition data for {fruit_chosen}")

    # Create SQL insert statement using safe bind parameters
    my_insert_stmt = """
        INSERT INTO smoothies.public.orders(ingredients, name_on_order)
        VALUES (?, ?)
    """

    # Display SQL preview (optional)
    st.write("SQL preview:")
    st.code(f"INSERT INTO smoothies.public.orders(ingredients, name_on_order) VALUES ('{ingredients_string.strip()}', '{title}')")

    # Button to submit the order
    if st.button("Submit order"):
        if title:  # Fixed: Check if title is provided
            session.sql(my_insert_stmt, [ingredients_string.strip(), title]).collect()
            st.success(f"✅ Your Smoothie is ordered! {title}")
        else:
            st.error("Please enter a name for your smoothie!")
