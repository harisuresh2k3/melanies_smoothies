# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd

# App Title
st.title(f":cup_with_straw: Customize Your Smoothie ! :cup_with_straw: {st.__version__}")
st.write("Choose the fruits you want in your Custom Smoothie!")

# Name input
name_on_order = st.text_input("Name on the Smoothie:")
st.write("The name on the smoothie will be:", name_on_order)

# Snowflake connection
cnx = st.connection("snowflake")
session = cnx.session()

# Load fruit options
fruit_df = (
    session.table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS")
    .select(col("FRUIT_NAME"))
    .to_pandas()
)

fruit_list = fruit_df["FRUIT_NAME"].tolist()

# Multiselect
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_list,
    max_selections=5
)

if ingredients_list:

    ingredients_string = " ".join(ingredients_list)

    for fruit_chosen in ingredients_list:
        st.subheader(f"{fruit_chosen} Nutrition Information")

        # Using fruit name directly for API
        response = requests.get(
            f"https://fruityvice.com/api/fruit/{fruit_chosen.lower()}"
        )

        if response.status_code == 200:
            nutrition_df = pd.json_normalize(response.json())
            st.dataframe(nutrition_df, use_container_width=True)
        else:
            st.warning("Nutrition data not found.")

    # Insert button
    if st.button("Submit Order"):

        session.sql(
            """
            INSERT INTO SMOOTHIES.PUBLIC.ORDERS (ingredients, name_on_order)
            VALUES (?, ?)
            """,
            params=[ingredients_string, name_on_order],
        ).collect()

        st.success(f"Your Smoothie is ordered, {name_on_order}! 🥤", icon="✅")
