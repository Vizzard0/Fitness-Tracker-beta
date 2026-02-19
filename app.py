import streamlit as st
import pandas as pd
import plotly.express as px
import requests

# 1. SETUP
st.set_page_config(page_title="Macro Pro 2026", page_icon="🥗", layout="wide")
st.title("🥗 My Daily Macro Goal Tracker")

# Replace this with your actual USDA API Key
API_KEY = "arQP3jO8ZKQpivl7SsTNWDB1chaxiNTdKf3tgw7h" 

if 'my_meals' not in st.session_state:
    st.session_state.my_meals = []

# 2. SIDEBAR GOALS
st.sidebar.header("🎯 Set Your Daily Goals")
g_cal = st.sidebar.number_input("Goal: Calories", value=2000)
g_p = st.sidebar.number_input("Goal: Protein (g)", value=150)
g_c = st.sidebar.number_input("Goal: Carbs (g)", value=200)
g_f = st.sidebar.number_input("Goal: Fats (g)", value=70)

# 3. USDA SEARCH BRAIN
def get_food_data(query):
    url = f"https://api.nal.usda.gov/fdc/v1/foods/search?api_key={API_KEY}&query={query}&pageSize=1"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data['foods']:
                food = data['foods'][0]
                nutrients = food.get('foodNutrients', [])
                results = {"p": 0, "c": 0, "f": 0, "name": food['description']}
                for n in nutrients:
                    n_name = n.get('nutrientName', '').lower()
                    val = n.get('value', 0)
                    if "protein" in n_name: results['p'] = val
                    elif "carbohydrate" in n_name: results['c'] = val
                    elif "lipid" in n_name or n_name == "fat": results['f'] = val
                return results
    except: return None
    return None

# 4. SEARCH INPUT
st.subheader("🔎 Find & Log Food")
user_query = st.text_input("Search USDA Database (e.g. Chicken)")

found_food = None 
if user_query:
    found_food = get_food_data(user_query)
    if found_food:
        st.success(f"Found: {found_food['name']}")

# 5. LOGGING FORM
with st.form("meal_form", clear_on_submit=True):
    name = st.text_input("Food Name", value=found_food['name'] if found_food else "")
    
    col_qty, col_unit = st.columns([1, 1])
    qty = col_qty.number_input("How much?", min_value=0.1, value=100.0)
    unit = col_unit.selectbox("Unit", ["grams (g)", "table spoons (tbsp)", "ounces (oz)"])

    # Conversion Logic
    multiplier = 1.0
    if unit == "table spoons (tbsp)": multiplier = qty * 15 / 100
    elif unit == "ounces (oz)": multiplier = qty * 28.35 / 100
    else: multiplier = qty / 100

    st.write("---")
    c1, c2, c3 = st.columns(3)
    
    # Calculate final numbers
    val_p = (float(found_food['p']) if found_food else 0.0) * multiplier
    val_c = (float(found_food['c']) if found_food else 0.0) * multiplier
    val_f = (float(found_food['f']) if found_food else 0.0) * multiplier
    
    p = c1.number_input("Protein", value=val_p)
    c = c2.number_input("Carbs", value=val_c)
    f = c3.number_input("Fats", value=val_f)
    
    if st.form_submit_button("Log Food"):
        if name:
            cal = (p*4) + (c*4) + (f*9)
            st.session_state.my_meals.append({
                "Food": f"{name} ({qty} {unit})", 
                "Protein": round(p, 1), 
                "Carbs": round(c, 1), 
                "Fats": round(f, 1), 
                "Calories": round(cal, 1)
            })
            st.rerun()

# 6. DASHBOARD & HISTORY
if st.session_state.my_meals:
    df = pd.DataFrame(st.session_state.my_meals)
    t_p, t_c, t_f, t_cal = df["Protein"].sum(), df["Carbs"].sum(), df["Fats"].sum(), df["Calories"].sum()
    r_cal, r_p, r_c, r_f = g_cal - t_cal, g_p - t_p, g_c - t_c, g_f - t_f

    st.divider()
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Calories", f"{t_cal:.0f}", f"{r_cal:.0f} Left", delta_color="inverse")
    m2.metric("Protein", f"{t_p:.0f}g", f"{r_p:.0f}g Left")
    m3.metric("Carbs", f
