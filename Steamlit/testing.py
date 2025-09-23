import streamlit as st
import numpy as np
import pandas as pd
import altair as alt
import matplotlib.pyplot as plt
import time

def set_page(new_page):
    st.session_state["page"] = new_page

# Initialize page in session_state
if "page" not in st.session_state:
    st.session_state["page"] = "Home"

# Render navbar and update page if navbar is used
st.sidebar.title("Navigation")
selected_page = st.sidebar.radio("", ["Startseite", "Raumübersicht", "Meldungen"])
if selected_page != st.session_state["page"]:
    st.session_state["page"] = selected_page

page = st.session_state["page"]

if page == "Startseite":
    if st.button("Willkommen bei Plantdrop (Zur Startseite)", key="home_btn"):
        set_page("Home")
    st.header("Startseite")
    st.subheader("CO² Gehalt")
    st.subheader("Zufallsdaten Chart (Pink)")
    data = pd.DataFrame(
        np.random.randn(20, 3),
        columns=["A", "B", "C"]
    )
    chart = alt.Chart(data.reset_index()).transform_fold(
        ['A', 'B', 'C'],
        as_=['Spalte', 'Wert']
    ).mark_bar(opacity=0.7).encode(
        x='index:O',
        y='Wert:Q',
        color=alt.value('#406931')
    )
    st.altair_chart(chart, use_container_width=True)
    # Example clickable header to go to Documentation
    if st.button("Zur Dokumentation"):
        set_page("Documentation")

elif page == "Raumübersicht":
    if st.button("Zurück zur Startseite"):
        set_page("Home")
    st.title("Dokumentation")
    st.write("Hier findest du die Dokumentation zu Plantdrop.")
    if st.button("Zu Beispielen"):
        set_page("Examples")

elif page == "Meldungen":
    if st.button("Zurück zur Startseite"):
        set_page("Home")
    st.title("Beispiele")
    st.write("Hier findest du Beispielanwendungen und Code-Snippets.")

#elif page == "Community":
    #if st.button("Zurück zur Startseite"):
        #set_page("Home")
    #st.title("Community")
    #st.write("Tritt der Plantdrop Community bei und tausche dich aus!")

#elif page == "About":
    #if st.button("Zurück zur Startseite"):
        #set_page("Home")
    #st.title("Über Plantdrop")
    #st.write("Plantdrop ist ein Beispielprojekt für Streamlit mit Navigation.")