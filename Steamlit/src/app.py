import streamlit as st
import pandas as pd
import altair as alt
import time
import sys
import os

# Add the parent folder (project root) to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# Add Scripts folder to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Scripts')))

from Scripts.frontend_connection import Frontend_connector

st.set_page_config(page_title = "Plantdrop", page_icon="src/styles/image-15.ico", layout = "wide")

db = Frontend_connector()

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
    rooms = db.show_rooms()
    selected_room = st.sidebar.selectbox("Raum auswählen:", rooms)

# ---------------- Seiteninhalte -----------------
if main_page == "Startseite":
    st.title("Willkommen bei Plantdrop")
    st.header("Startseite")


    df = db.select_all_measurements()
    #df = pd.read_csv("data.csv") #testing_database


############## Wasser Messung Chart ####################
    st.subheader("Wassergehalt")

    try:
        df["timestamp_measurement"] = pd.to_datetime(df["timestamp_measurement"])

        if not df.empty:
            waterchart = alt.Chart(df).mark_bar(opacity=0.7).encode(
                x=alt.X('timestamp_measurement:T', axis=alt.Axis(title='Zeitpunkt')),
                y=alt.Y('wasserstand:Q', axis=alt.Axis(title='Wasserstand (mL)'), scale=alt.Scale(domain=[0, 100])),
                color=alt.value('#89AFD6')
            )
            st.altair_chart(waterchart, use_container_width=True)
        else:
            st.info("Keine Wasserverbrauchsdaten gefunden.")
    except Exception as e:
        st.error(f"Fehler beim Laden der CSV-Datei: {e}")

    
    ############## Licht Messung Chart ####################
    st.subheader("Lichtintensität")

    try:
        df["timestamp_measurement"] = pd.to_datetime(df["timestamp_measurement"])
        if not df.empty:
            line = alt.Chart(df).mark_line(color="#8b8a35").encode(
                x=alt.X('timestamp_measurement:T', axis=alt.Axis(title='Zeitpunkt')),
                y=alt.Y('lux:Q', axis=alt.Axis(title='Lichtintensität (Lux)'))
            )
            points = alt.Chart(df).mark_point(opacity=0.5, color="#8b8a35").encode(
                x=alt.X('timestamp_measurement:T'),
                y=alt.Y('lux:Q')
            )
            lightchart = line + points
            st.altair_chart(lightchart, use_container_width=True)
        else:
            st.info("Keine Messdaten gefunden.")
    except Exception as e:
        st.error(f"Fehler beim Laden der CSV-Datei: {e}")

    ############## Luft ####################
    st.subheader("Luftfeuchtigkeit & Lufttemperatur")

    try:
        df["timestamp_measurement"] = pd.to_datetime(df["timestamp_measurement"])

        if not df.empty:
            # Farbdefinition
            color_scale = alt.Scale(domain=["Luftfeuchtigkeit", "Lufttemperatur"],
                                    range=["#1F77B4", "#D95F02"])

            # Luftfeuchtigkeit
            humidity_line = alt.Chart(df).mark_line().encode(
                x=alt.X('timestamp_measurement:T', axis=alt.Axis(title='Zeitpunkt')),
                y=alt.Y('luftfeuchtigkeit:Q', axis=alt.Axis(title='Luftfeuchtigkeit (%)')),
                color=alt.value("#1F77B4")
            )
            humidity_points = alt.Chart(df).mark_point(opacity=0.5).encode(
                x='timestamp_measurement:T',
                y='luftfeuchtigkeit:Q',
                color=alt.value("#1F77B4")
            )

            # Lufttemperatur
            temperature_line = alt.Chart(df).mark_line().encode(
                x='timestamp_measurement:T',
                y=alt.Y('lufttemperatur:Q', axis=alt.Axis(title='Lufttemperatur (°C)')),
                color=alt.value("#D95F02")
            )
            temperature_points = alt.Chart(df).mark_point(opacity=0.5).encode(
                x='timestamp_measurement:T',
                y='lufttemperatur:Q',
                color=alt.value("#D95F02")
            )

            humidity_chart = humidity_line + humidity_points
            temperature_chart = temperature_line + temperature_points

            combined_chart = alt.layer(
                humidity_chart,
                temperature_chart
            ).resolve_scale(
                y='independent'
            )

            legend = alt.Chart(pd.DataFrame({
                'Variable': ["Luftfeuchtigkeit", "Lufttemperatur"],
                'color': ["#1F77B4", "#D95F02"]
            })).mark_point(size=0).encode(
                color=alt.Color('Werte:N', scale=color_scale, legend=alt.Legend(orient="bottom"))
            )

            final_chart = combined_chart & legend

            st.altair_chart(final_chart, use_container_width=True)
        else:
            st.info("Keine Messdaten gefunden.")

    except Exception as e:
        st.error(f"Fehler beim Laden der CSV-Datei: {e}")

    ############## Bodenfeuchtigkeit ####################
    st.subheader("Bodenfeuchtigkeit")

    try:
        df["timestamp_measurement"] = pd.to_datetime(df["timestamp_measurement"])

        if not df.empty:
            groundchart = alt.Chart(df).mark_area(opacity=0.5).encode(
                x=alt.X('timestamp_measurement:T', axis=alt.Axis(title='Zeitpunkt')),
                y=alt.Y('feuchtigkeit:Q', axis=alt.Axis(title='Bodenfeuchtigkeit (%)'), scale=alt.Scale(domain=[0, 100])),
                color=alt.value('#89AFD6')
            )
            st.altair_chart(groundchart, use_container_width=True)
        else:
            st.info("Keine Wasserverbrauchsdaten gefunden.")
    except Exception as e:
        st.error(f"Fehler beim Laden der CSV-Datei: {e}")




elif main_page == "Raumübersicht":
    st.header("Raumübersicht")

    if selected_room:
        st.subheader(f"Daten für {selected_room}")

        # --- Pflanzenübersicht --------
        st.write("Pflanzenübersicht")
        rooms = db.show_rooms()
        for room in rooms:
            if selected_room == room:
                plants = db.roomquerry(room)
                plants = plants.rename(columns={
                    "plantid": "id",
                    "plant_name": "Pflanze",
                    "plant_type": "Pflanzenart",
                    "minimum_water": "Gießung_Schwellwert (%)",
                    "feuchtigkeit": "Bodenfeuchtigkeit (%)",  
                    "kohlenstoffdioxid": "CO₂ (ppm)",
                    "wasserstand": "Wasserstand (L)",
                    "luftfeuchtigkeit": "Luftfeuchtigkeit",
                    "lux": "Helligkeit(lux)",
                    "lufttemperatur": "Lufttemperatur (°C)",
                    "error_msg": "Status"  
                    })

        # Tabelle editierbar machen → nur bestimmte Spalten freigeben
        edited_plants = st.data_editor(
            plants,
            column_config={
                "id": st.column_config.NumberColumn(disabled=True),
                "Pflanze": st.column_config.TextColumn(disabled=False),
                "Pflanzenart": st.column_config.TextColumn(disabled=False),
                "Bodenfeuchtigkeit": st.column_config.NumberColumn(disabled=True),
                "Gießung_Schwellwert (%)": st.column_config.NumberColumn(disabled=False),
                "Status": st.column_config.TextColumn(disabled=True),
                "CO₂ (ppm)": st.column_config.NumberColumn(disabled=True),
                "Luftfeuchtigkeit": st.column_config.NumberColumn(disabled=True),
                "Lufttemperatur (°C)": st.column_config.NumberColumn(disabled=True),
                "Helligkeit(lux)": st.column_config.NumberColumn(disabled=True),
                "Wasserstand (L)": st.column_config.NumberColumn(disabled=True),
            },
            disabled=False,  # wichtig, damit Config wirkt
            width="stretch"
        )

        if st.button("Änderungen speichern"):
            db.update_raumuebersicht(edited_plants)

            
            st.success("Änderungen übernommen.")
            



elif main_page == "Meldungen":
    st.header("Meldungen")
    st.write("Hier erscheinen Benachrichtigungen, Warnungen oder Logs.")
