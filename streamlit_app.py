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

# --- Connexion explicite à Snowflake ---
conn = st.connection(
    "",  # nom vide pour ne pas utiliser "snowflake" par défaut
    type="snowflake",
   account = "NSROXKC-QFB68358",
   user = "Nermine",
   password = "Leila12345678A",
   role = "SYSADMIN",
   warehouse = "COMPUTE_WH",
   database = "SMOOTHIES",
   schema = "PUBLIC",
)
session = conn.session()

# --- Input pour le nom ---
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# --- Récupération des fruits depuis Snowflake ---
my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"))
st.dataframe(my_dataframe, width="stretch")


# --- Sélection des ingrédients ---
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe,
    max_selections=5
)

# --- Si des ingrédients sont choisis, construire et insérer la commande ---
if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

    # st.write(ingredients_string)  # debug

    my_insert_stmt = f"""
        insert into smoothies.public.orders(ingredients, name_on_order)
        values ('{ingredients_string}', '{name_on_order}')
    """

  if st.button("Submit Order", type="primary"):
    if not name_on_order:
        st.error("Please enter your name before submitting!")
    elif not ingredients_list:
        st.error("Please choose at least one ingredient!")
    else:
        ingredients_string = " ".join(ingredients_list)

        my_insert_stmt = f"""
            insert into smoothies.public.orders(ingredients, name_on_order)
            values ('{ingredients_string}', '{name_on_order}')
        """
        session.sql(my_insert_stmt).collect()
        st.success(f"✅ Your Smoothie is ordered, {name_on_order}!")
