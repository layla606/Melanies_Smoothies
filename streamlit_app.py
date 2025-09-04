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
my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"),col('SEARCH_ON'))
#st.dataframe(data=my_dataframe,use_container_width= True)
#st.stop()
#convert the snowpark dataframe to a pandas dataframe so we can use the loc function
pd_df=my_dataframe.to_pandas()
st.dataframe(pd_df)
st.stop() 
#fruit_list = my_dataframe.collect()
#fruit_options = [row["FRUIT_NAME"] for row in fruit_list]  # Convert DataFrame to Python list

# --- Multiselect for ingredients ---
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    my_dataframe,  # Use Python list, not DataFrame
    max_selections=5
)

# --- Handle selected ingredients ---
if ingredients_list:
    ingredients_string = " "
    for fruit_chosen in ingredients_list:
        ingredients_string+=fruit_chosen+' '    

        search_on=pd_df.loc[pd_df['FRUIT_NAME']==fruit_chosen,'SEARCH_ON'].iloc[0]
        st.write('The search value for',fruit_chosen,'is ',search_on,'.')
        
        st.subheader(fruit_chosen+ 'Nutrition Information')
        fruityvice_response=requests.get("https://fruityvice.com/api/fruit/"+ fruit_chosen)
        
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
        sf_df = st.dataframe(smoothiefroot_response.json(), use_container_width=True)


    # Create SQL insert statement using safe bind parameters
    my_insert_stmt = """
        INSERT INTO smoothies.public.orders(ingredients, name_on_order)
        VALUES (:ingredients, :title)
    """

    # Display SQL preview (optional)
    st.write("SQL preview:")
    st.code(f"INSERT INTO smoothies.public.orders(ingredients, name_on_order) VALUES ('{ingredients_string}', '{title}')")

    # Button to submit the order
    if st.button("Submit order"):
        session.sql(my_insert_stmt, {"ingredients": ingredients_string, "title": title}).collect()
        st.success(f"✅ Your Smoothie is ordered! {title}")
