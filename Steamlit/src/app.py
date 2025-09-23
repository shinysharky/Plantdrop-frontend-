import streamlit as st
import pandas as pd
import sqlite3
import altair as alt
import time

st.set_page_config(page_title = "Plantdrop", page_icon="src/styles/image-15.ico", layout = "wide")


def inject_css(file_path):
    with open(file_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

inject_css("src/styles/green_theme.css")

# Progressbar beim ersten Aufruf
if "progress_shown" not in st.session_state:
    progress_placeholder = st.empty()
    for i in range(101):
        progress = i / 100
        progress_placeholder.markdown(f"""
        <div style="width: 100%; background-color: transparent; border-radius: 10px;">
          <div style="width: {int(progress*100)}%; background: linear-gradient(90deg, white, #8AB162, black); height: 19px; border-radius: 10px;">
          </div>
        </div>
        """, unsafe_allow_html=True)
        time.sleep(0.01)
    progress_placeholder.empty()
    st.session_state["progress_shown"] = True

# ---------------- Navigation -----------------
st.sidebar.header("Navigation")
main_page = st.sidebar.selectbox("Seite wählen:", ["Startseite", "Meldungen", "Raumübersicht"],label_visibility="collapsed")

# Falls Raumübersicht gewählt wird → Räume auswählen
selected_room = None
if main_page == "Raumübersicht":
    selected_room = st.sidebar.selectbox("Raum auswählen:", ["Raum 1", "Raum 2", "Raum 3"])

# ---------------- Seiteninhalte -----------------
if main_page == "Startseite":
    st.title("Willkommen bei Plantdrop")
    st.header("Startseite")

    ############## CO2 Messung Chart ####################
    st.subheader("CO₂-Gehalt")
    try:
        conn = sqlite3.connect("co2_messungen.db")
        query = "SELECT zeitpunkt, co2_ppm FROM CO2Messung ORDER BY zeitpunkt"
        co2data = pd.read_sql_query(query, conn)
        conn.close()

        if not co2data.empty:
            co2chart = alt.Chart(co2data).mark_line(point=True, opacity=0.8).encode(
                x='zeitpunkt:T',
                y='co2_ppm:Q',
                color=alt.value('#618B35')
            )
            st.altair_chart(co2chart, use_container_width=True)
        else:
            st.info("Keine CO₂-Messdaten gefunden.")
    except Exception as e:
        st.error(f"Fehler beim Laden der CO₂-Datenbank: {e}")
    
    ############## Wasser Messung Chart ####################
    st.subheader("Wassergehalt") 
    try: 
        conn = sqlite3.connect("wasserverbrauch.db") 
        query = """ SELECT w.zeitpunkt, w.wasserstand_liter, b.name FROM Wasserverbrauch w JOIN Behaelter b ON w.behaelter_id = b.behaelter_id ORDER BY w.zeitpunkt """ 
        waterdata = pd.read_sql_query(query, conn) 
        conn.close() 

        if not waterdata.empty: 
            waterchart = alt.Chart(waterdata).mark_bar(opacity=0.7).encode(
                x='zeitpunkt:T', 
                y='wasserstand_liter:Q', 
                color=alt.value('#89AFD6') 
            ) 
            st.altair_chart(waterchart, use_container_width=True) 
        else: 
            st.info("Keine Wasserverbrauchsdaten gefunden.") 
    except Exception as e: 
        st.error(f"Fehler beim Laden der Datenbank: {e}")

elif main_page == "Raumübersicht":
    st.header("Raumübersicht")

    if selected_room:
        st.subheader(f"Daten für {selected_room}")

        # --- Pflanzenübersicht --------
        st.write("Pflanzenübersicht")
        if selected_room == "Raum 1":
            plants = pd.DataFrame({
                "Pflanze": ["Elium", "Rose", "Tuple", "Ficus", "Aloe Vera", "Kaktus"],
                "Ort": ["Fensterbank", "Regal", "Tisch", "Schrank", "Ecke", "Fenster"],
                "Status": ["OK", "!Braucht Wasser", "OK", "OK", "!Zu viel Wasser", "OK"],
                "CO₂ (ppm)": [420, 500, 430, 410, 480, 390],
                "Wasserstand (L)": [2.3, 1.1, 2.8, 2.5, 0.5, 3.0],
                "Wasser pro Tag (L)": [1.5, 2.0, 1.0, 1.2, 0.3, 0.1]
            })
        elif selected_room == "Raum 2":
            plants = pd.DataFrame({
                "Pflanze": ["Bonsai", "Lavendel", "Spinnen Lilie"],
                "Ort": ["Tisch B", "Ausbilderplatz", "Druckerraum"],
                "Status": ["OK", "OK", "Braucht Wasser"],
                "CO₂ (ppm)": [410, 425, 450],
                "Wasserstand (L)": [2.0, 2.5, 0.9],
                "Wasser pro Tag (L)": [1.2, 1.8, 0.7]
            })
        else:  # Raum 3
            plants = pd.DataFrame({
                "Pflanze": ["Orchidee", "Hyantinze", "Gänseblümchen"],
                "Ort": ["Topf 1", "Topf 2", "Topf 3"],
                "Status": ["OK", "OK", "OK"],
                "CO₂ (ppm)": [430, 440, 420],
                "Wasserstand (L)": [2.1, 2.4, 2.7],
                "Wasser pro Tag (L)": [1.0, 1.5, 0.8]
            })

        # Tabelle editierbar machen → nur bestimmte Spalten freigeben
        edited_plants = st.data_editor(
            plants,
            column_config={
                "Pflanze": st.column_config.TextColumn(disabled=False),
                "Ort": st.column_config.TextColumn(disabled=False),
                "Wasser pro Tag (L)": st.column_config.NumberColumn(disabled=False),
                "Status": st.column_config.TextColumn(disabled=True),
                "CO₂ (ppm)": st.column_config.NumberColumn(disabled=True),
                "Wasserstand (L)": st.column_config.NumberColumn(disabled=True),
            },
            disabled=False,  # wichtig, damit Config wirkt
            width="stretch"
        )

        if st.button("Änderungen speichern"):
            st.success("Änderungen übernommen (momentan nur im Speicher).")



elif main_page == "Meldungen":
    st.header("Meldungen")
    st.write("Hier erscheinen Benachrichtigungen, Warnungen oder Logs.")
