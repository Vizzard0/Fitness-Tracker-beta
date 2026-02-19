import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Macro Tracker", page_icon="🥧")
st.title("🥧 My Macro Dashboard")

# Memory
if 'my_meals' not in st.session_state:
    st.session_state.my_meals = []

# Sidebar Goals
st.sidebar.header("🎯 Targets")
g_cal = st.sidebar.number_input("Calories", value=2000)
g_p = st.sidebar.number_input("Protein (g)", value=150)
g_c = st.sidebar.number_input("Carbs (g)", value=200)
g_f = st.sidebar.number_input("Fats (g)", value=70)

# Input
with st.expander("➕ Add Food", expanded=True):
    with st.form("meal_form"):
        name = st.text_input("Food Name")
        c1, c2, c3 = st.columns(3)
        p = c1.number_input("P", min_value=0)
        c = c2.number_input("C", min_value=0)
        f = c3.number_input("F", min_value=0)
        if st.form_submit_button("Log"):
            if name:
                cal = (p*4) + (c*4) + (f*9)
                st.session_state.my_meals.append({"Food": name, "Protein": p, "Carbs": c, "Fats": f, "Calories": cal})
                st.rerun()

# Dashboard
if st.session_state.my_meals:
    df = pd.DataFrame(st.session_state.my_meals)
    t_p, t_c, t_f, t_cal = df["Protein"].sum(), df["Carbs"].sum(), df["Fats"].sum(), df["Calories"].sum()

    # Pie Chart
    macro_data = pd.DataFrame({
        "Macro": ["Protein", "Carbs", "Fats"],
        "Grams": [t_p, t_c, t_f]
    })
    
    fig = px.pie(macro_data, values='Grams', names='Macro', title="Macro Split (Grams)",
                 color_discrete_sequence=['#FF4B4B', '#0068C9', '#FFAB00'])
    
    st.plotly_chart(fig, use_container_width=True)

    # Metrics
    st.subheader(f"Total: {t_cal} / {g_cal} kcal")
    st.progress(min(t_cal / g_cal, 1.0))
    
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Protein", f"{t_p}g")
    col_b.metric("Carbs", f"{t_c}g")
    col_c.metric("Fats", f"{t_f}g")

    st.divider()
    # USE_CONTAINER_WIDTH is the winner here
    st.dataframe(df, use_container_width=True)
    
    if st.button("🗑️ Reset Day"):
        st.session_state.my_meals = []
        st.rerun()