import streamlit as st
import pandas as pd
import requests
import random

# --- JOUW URL'S MET DE JUISTE GID'S ---
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbzXpg0gOGRWxnMFcozojnw5F-n8uZ_l0DUWw50lzUVzRmbxtEKQD-ytnCow_GpQLcc1/exec"

NUMMERS_CSV_URL = "https://docs.google.com/spreadsheets/d/1o8uxw9hUk9YMZ0eIRPCZ3_Lglt3CqV-Zu3xlmpu-Xnw/export?format=csv&gid=1454715385"
INSCHRIJVINGEN_CSV_URL = "https://docs.google.com/spreadsheets/d/1o8uxw9hUk9YMZ0eIRPCZ3_Lglt3CqV-Zu3xlmpu-Xnw/export?format=csv&gid=0"

st.set_page_config(page_title="Ultimate Jam Roulette", page_icon="🎸", layout="centered")

# --- ZIJKANT VOOR BEHEERDER (ORGANISATOR) ---
st.sidebar.header("🔐 Organisator Login")
wachtwoord_input = st.sidebar.text_input("Wachtwoord voor beheer:", type="password")

ADMIN_WACHTWOORD = "jam2026" 
is_admin = (wachtwoord_input == ADMIN_WACHTWOORD)

# --- WEERGAVE ALS JE GEEN ADMIN BENT (DEELNEMERS VIEW) ---
if not is_admin:
    st.markdown("<h1 style='text-align: center;'>🎸 ULTIMATE JAM ROULETTE! 🎸</h1>", unsafe_allow_html=True)
    st.write("")
    st.write("Fijn dat je zaterdag naar ons feest komt! Om de avond nog wat muzikaler te maken, nodigen we je uit voor de ultieme jamsessie. Vul hieronder je naam in, het instrument dat je speelt, en selecteer alle nummers waarvan je de partij op dat instrument kent. Staat je favoriete nummer er niet tussen? Voeg het onderaan toe. Dit nummer wordt automatisch aan de lijst toegevoegd zodat iedereen kan meespelen.")
    st.write("Speel je meerdere instrumenten? Geen probleem! Je kan gerust een volledige keuze opgeven voor bijvoorbeeld gitaar, daarna een volledig andere keuze voor zang, enzovoort. Zorg er zeker voor dat je je voornaam en achternaam invult!")
    st.write("Let wel op: je keuze is pas bevestigd wanneer je de ballonnen over het scherm ziet stijgen.")
    st.write("Bezoek de link zeker later op de week, of op de avond van het feest zelf, nog even terug om te kijken of er interessante nummers zijn toegevoegd waar je misschien zelf niet aan gedacht had.")
    st.write("Wij kijken nu al uit naar de meest chaotische, doch legendarische jam allertijden!")
    st.write("**Tot zaterdag!**")
    st.markdown("---")
    
    try:
        df_nummers = pd.read_csv(NUMMERS_CSV_URL)
        beschikbare_nummers = df_nummers.iloc[:, 0].dropna().astype(str).tolist()
    except Exception:
        beschikbare_nummers = ["Rolling in the Deep", "Superstition", "Purple Haze"]
        
    with st.form("inschrijf_form"):
        naam = st.text_input("Jouw Naam (Voornaam + Achternaam)")
        instrument = st.selectbox("Jouw Instrument / Rol", ["Gitaar", "Bas", "Zang", "Drums", "Toetsen", "Saxofoon", "Anders"])
        
        gekozen_bestaand = st.multiselect(
            "Vink hier jouw nummers aan (je kunt er meerdere kiezen of erop zoeken door te typen):", 
            beschikbare_nummers
        )
        
        nieuw_nummer = st.text_input("Staat jouw nummer er echt niet bij? Typ het hier in (optioneel):")
        
        submitted = st.form_submit_button("Inschrijven!", type="primary")
        
        if submitted:
            if not naam:
                st.warning("Vul alsjeblieft je naam in.")
            else:
                final_nummers = list(gekozen_bestaand)
                
                if nieuw_nummer and nieuw_nummer.strip():
                    getypte_nummers = [n.strip() for n in nieuw_nummer.split(',') if n.strip()]
                    for num in getypte_nummers:
                        if num not in final_nummers:
                            final_nummers.append(num)
                
                if not final_nummers:
                    st.warning("Kies minimaal één nummer uit de lijst of vul een nieuw nummer in.")
                else:
                    payload = {
                        "naam": naam,
                        "instrument": instrument,
                        "nummers": final_nummers
                    }
                    
                    try:
                        response = requests.post(WEB_APP_URL, json=payload)
                        if response.status_code == 200:
                            st.success(f"Top {naam}! Je inschrijving voor **{instrument}** is opgeslagen voor {len(final_nummers)} nummer(s).")
                            st.balloons()
                        else:
                            st.error("Er ging iets mis bij het opslaan naar de Google Sheet.")
                    except Exception as e:
                        st.error(f"Verbindingsfout: {e}")

# --- WEERGAVE ALS JE WEL ADMIN BENT (GROOT SCHERM / PUBLIEK VIEW) ---
else:
    st.markdown("""
    <style>
    header[data-testid="stHeader"] {
        background-color: rgba(0, 0, 0, 0) !important;
        visibility: hidden;
    }
    .stApp, .block-container {
        background-color: #000000 !important;
        color: #ffffff !important;
    }
    [data-testid="stSidebar"] {
        background-color: #111111 !important;
    }
    div.stButton > button:first-child {
        font-size: 3.5rem !important;
        padding: 30px 40px !important;
        height: auto !important;
        width: 100% !important;
        border-radius: 25px !important;
        font-weight: 900 !important;
        letter-spacing: 2px !important;
        background: linear-gradient(135deg, #ff4b4b 0%, #ff6b6b 100%) !important;
        color: white !important;
        border: 4px solid #ffffff !important;
        box-shadow: 0px 15px 35px rgba(255, 75, 75, 0.7) !important;
        text-transform: uppercase;
    }
    div.stButton > button:first-child:hover {
        background: linear-gradient(135deg, #ff2a2a 0%, #ff4b4b 100%) !important;
        border-color: #ffeb3b !important;
        box-shadow: 0px 20px 45px rgba(255, 75, 75, 0.9) !important;
        transform: scale(