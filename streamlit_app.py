# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write(
    """
    Choose the fruits you want in your custom Smoothie!
    """
)

import streamlit as st

name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

cnx= st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"))
st.dataframe(my_dataframe, use_container_width=True)

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe,
    max_selections=5
)

if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

    #st.write(ingredients_string)

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
                         values ('""" + ingredients_string + """','""" + name_on_order + """')"""


    # Display SQL preview (optional)
    st.write("SQL preview:")
    st.code(f"INSERT INTO SMOOTHIES.PUBLIC.ORDERS(INGREDIENTS, NAME_ON_ORDER) VALUES ('{ingredients_string}', '{title}')")

    # Button to submit the order
  # --- Button to submit the order ---
if st.button("Submit order"):
    try:
        my_insert_stmt = """
            INSERT INTO SMOOTHIES.PUBLIC.ORDERS (NAME_ON_ORDER, INGREDIENTS)
            VALUES (?, ?)
        """
        session.sql(my_insert_stmt, [title, ingredients_string]).collect()
        st.success(f"✅ Your Smoothie is ordered! {title}")
    except Exception as e:
        st.error(f"❌ Error: {e}")


