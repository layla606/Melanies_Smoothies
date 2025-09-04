# --- Handle selected ingredients ---
if ingredients_list:
    ingredients_string = ""
    nutrition_table = pd.DataFrame()  # Empty DataFrame to hold all fruits

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "

        # Get the search value from Snowflake
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]

        # Smoothiefroot API
        sf_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")
        if sf_response.status_code == 200:
            sf_json = sf_response.json()
            nutrition = sf_json.get("nutrition", {})

            # Dynamically convert nutrition dict to DataFrame row
            row_df = pd.DataFrame({**{"Fruit": fruit_chosen}, **nutrition}, index=[0])
            nutrition_table = pd.concat([nutrition_table, row_df], ignore_index=True)
        else:
            st.warning(f"No Smoothiefroot data found for {fruit_chosen}.")

    ingredients_string = ingredients_string.strip()

    # Display dynamic nutrition table
    st.subheader("Nutrition Info (Smoothiefroot)")
    st.dataframe(nutrition_table, use_container_width=True)
