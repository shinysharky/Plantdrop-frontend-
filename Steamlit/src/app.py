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
        df = pd.read_csv("data.csv")

        # Datum/Zeitspalte in datetime umwandeln
        df["timestamp_measurement"] = pd.to_datetime(df["timestamp_measurement"])

        if not df.empty:
            co2chart = alt.Chart(df).mark_area(
                opacity=0.5,
                color="#618B35"
            ).encode(
                x=alt.X('timestamp_measurement:T', axis=alt.Axis(title='Zeitpunkt')),
                y=alt.Y('feuchtigkeit:Q', axis=alt.Axis(title='Feuchtigkeit (%)'), scale=alt.Scale(domain=[0, 100]))
            )
            st.altair_chart(co2chart, use_container_width=True)
        else:
            st.info("Keine Messdaten gefunden.")
    except Exception as e:
        st.error(f"Fehler beim Laden der CSV-Datei: {e}")


    ############## Wasser Messung Chart ####################
    st.subheader("Wassergehalt")

    try:
        df = pd.read_csv("data.csv")
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
        df = pd.read_csv("data.csv")
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
        df = pd.read_csv("data.csv")
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
        df = pd.read_csv("data.csv")
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

# ---------------- Raum -----------------

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

# ---------------- Meldungen -----------------

elif main_page == "Meldungen":
    st.header("Meldungen")
    st.write("Hier erscheinen Benachrichtigungen, Warnungen oder Logs.")
