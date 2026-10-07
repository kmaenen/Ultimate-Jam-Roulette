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
        transform: scale(1.02);
    }
    </style>
    """, unsafe_allow_html=True)

    st.sidebar.success("Ingelogd als organisator! ✅")
    
    st.markdown("<h1 style='text-align: center; font-size: 2.8rem; font-weight: 800; margin-bottom: 0px; color: #ffffff;'>🎸 ULTIMATE JAM ROULETTE 🎸</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #aaaaaa; font-size: 1.1rem; margin-bottom: 15px;'>De live band machine</p>", unsafe_allow_html=True)
    
    try:
        df_inschrijvingen = pd.read_csv(INSCHRIJVINGEN_CSV_URL)
        
        if df_inschrijvingen.empty or 'html' in str(df_inschrijvingen.columns[0]).lower():
            st.warning("⚠️ Kon de Google Sheet niet goed laden. Klik hieronder op de knop om te verversen.")
            if st.button("🔄 Data verversen"):
                st.rerun()
            st.stop()
        
        if len(df_inschrijvingen) > 0 and len(df_inschrijvingen.columns) >= 3:
            uitgeklapt = []
            for _, row in df_inschrijvingen.iterrows():
                val_naam = row.iloc[0]
                val_inst = row.iloc[1]
                val_nums = row.iloc[2]
                
                if pd.isna(val_naam) or pd.isna(val_inst) or pd.isna(val_nums):
                    continue
                    
                naam = str(val_naam).strip()
                instrument = str(val_inst).strip()
                nummers_str = str(val_nums)
                
                nummers_lijst = [n.strip() for n in nummers_str.split(',') if n.strip() and n.strip() != 'nan']
                
                for num in nummers_lijst:
                    uitgeklapt.append({
                        'Nummer': num,
                        'Naam': naam,
                        'Instrument': instrument
                    })
            
            df_raw_bands = pd.DataFrame(uitgeklapt)
            
            if not df_raw_bands.empty:
                unieke_nummers = df_raw_bands['Nummer'].unique().tolist()
                
                if 'loting_teller' not in st.session_state:
                    st.session_state['loting_teller'] = 0
                if 'vorige_bezetting_dict' not in st.session_state:
                    st.session_state['vorige_bezetting_dict'] = {}
                if 'geschiedenis_nummers' not in st.session_state:
                    st.session_state['geschiedenis_nummers'] = []
                
                # --- RESULTATENWEERGAVE ---
                resultaat_container = st.container()
                
                with resultaat_container:
                    if st.session_state.get('geen_geldige_band', False):
                        st.warning("⚠️ Geen enkel overgebleven nummer heeft momenteel de minimale bezetting (of alle nummers zijn al gespeeld!).")
                    elif 'huidig_nummer' in st.session_state:
                        st.markdown(f"<h1 style='text-align: center; color: #ff4b4b; font-size: 2.8rem; margin-bottom: 5px;'>🎵 {st.session_state['huidig_nummer']} 🎵</h1>", unsafe_allow_html=True)
                        st.markdown("<h3 style='text-align: center; color: #ffffff; margin-top: 0px; margin-bottom: 10px;'>🎸 De Band op het Podium:</h3>", unsafe_allow_html=True)
                        
                        for _, row in st.session_state['huidige_band'].iterrows():
                            st.markdown(f"<div style='text-align: center; font-size: 1.4rem; padding: 12px; background-color: #121212; border-radius: 12px; margin: 8px 0; border: 2px solid #333333; color: #ffffff;'><b>{row['Naam']}</b> — <i style='color: #ff6b6b;'>{row['Instrument']}</i></div>", unsafe_allow_html=True)
                        st.markdown("<hr style='margin: 15px 0; border-color: #333333;'>", unsafe_allow_html=True)
                
                # --- DE ABSURD GROTE JAM KNOP ---
                st.markdown("<br>", unsafe_allow_html=True)
                jam_knop = st.button("🔥  JAM!  🔥", type="primary", use_container_width=True)
                
                # Snelle knop om de geschiedenis te resetten direct onder de jam-knop
                if st.session_state['geschiedenis_nummers']:
                    aantal_reeds_gehad = len(st.session_state['geschiedenis_nummers'])
                    if st.button(f"↩️ Reset geschiedenis ({aantal_reeds_gehad} nummers gespeeld - klik om opnieuw te beginnen)"):
                        st.session_state['geschiedenis_nummers'] = []
                        st.success("Geschiedenis gereset! Alle nummers kunnen weer geloot worden.")
                        st.rerun()
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                if jam_knop:
                    st.session_state['loting_teller'] += 1
                    is_flexibel_moment = (st.session_state['loting_teller'] % 4 == 0)
                    
                    volledig_bezet_nummers = []
                    geldige_nummers = []
                    
                    # FILTER: Neem enkel nummers mee die nog NIET zijn gespeeld
                    nog_te_spelen_nummers = [n for n in unieke_nummers if n not in st.session_state['geschiedenis_nummers']]
                    
                    for num in nog_te_spelen_nummers:
                        kandidaten_check = df_raw_bands[df_raw_bands['Nummer'] == num]
                        
                        heeft_zang = any(kandidaten_check['Instrument'].str.lower().str.contains("zang|vocal|zanger", na=False))
                        heeft_gitaar_keys = any(kandidaten_check['Instrument'].str.lower().str.contains("gitaar|guitar|toetsen|keys|keyboard|piano", na=False))
                        heeft_drum = any(kandidaten_check['Instrument'].str.lower().str.contains("drum", na=False))
                        heeft_bas = any(kandidaten_check['Instrument'].str.lower().str.contains("bas|bass", na=False))
                        
                        if heeft_zang and heeft_gitaar_keys:
                            geldige_nummers.append(num)
                            if heeft_drum and heeft_bas:
                                volledig_bezet_nummers.append(num)
                    
                    gekozen_nummer = None
                    if volledig_bezet_nummers and (not is_flexibel_moment or not geldige_nummers):
                        gekozen_nummer = random.choice(volledig_bezet_nummers)
                    elif geldige_nummers:
                        gekozen_nummer = random.choice(geldige_nummers)
                    
                    if gekozen_nummer:
                        # Voeg toe aan geschiedenis zodat het niet meer gekozen kan worden
                        st.session_state['geschiedenis_nummers'].append(gekozen_nummer)
                        
                        kandidaten = df_raw_bands[df_raw_bands['Nummer'] == gekozen_nummer].copy()
                        kandidaten['Inst_Lower'] = kandidaten['Instrument'].str.lower()
                        
                        vorige_dict = st.session_state['vorige_bezetting_dict']
                        
                        def filter_optimaal(subset_df, instrument_zoekwoord, reeds_gekozen_namen):
                            beschikbaar = []
                            noodoplossing = []
                            
                            for _, row in subset_df.iterrows():
                                naam = row['Naam']
                                if naam in reeds_gekozen_namen:
                                    continue
                                
                                noodoplossing.append(row)
                                if vorige_dict.get(naam) == instrument_zoekwoord:
                                    continue
                                
                                beschikbaar.append(row)
                            
                            if beschikbaar:
                                return pd.DataFrame(beschikbaar)
                            elif noodoplossing:
                                return pd.DataFrame(noodoplossing)
                            else:
                                return pd.DataFrame()

                        toegevoegde_rollen = []
                        reeds_gekozen_namen = []
                        
                        # STAP 1: Kies een Zanger
                        zang_mensen = kandidaten[kandidaten['Inst_Lower'].str.contains("zang|vocal|zanger", na=False)]
                        zang_filter = filter_optimaal(zang_mensen, "Zang", reeds_gekozen_namen)
                        
                        gekozen_zanger_naam = None
                        if not zang_filter.empty:
                            z = zang_filter.sample(1).iloc[0]
                            gekozen_zanger_naam = z['Naam']
                            toegevoegde_rollen.append({'Naam': gekozen_zanger_naam, 'Instrument': z['Instrument']})
                            reeds_gekozen_namen.append(gekozen_zanger_naam)
                        
                        # STAP 2: Kies Gitaar/Toetsen
                        extra_instrument_van_zanger = None
                        if gekozen_zanger_naam:
                            check_dubbel = kandidaten[
                                (kandidaten['Naam'] == gekozen_zanger_naam) & 
                                (kandidaten['Inst_Lower'].str.contains("gitaar|guitar|toetsen|keys|keyboard|piano", na=False))
                            ]
                            if not check_dubbel.empty:
                                kand_inst = check_dubbel.iloc[0]['Instrument']
                                if vorige_dict.get(gekozen_zanger_naam) != kand_inst:
                                    extra_instrument_van_zanger = kand_inst
                        
                        if extra_instrument_van_zanger:
                            toegevoegde_rollen[0]['Instrument'] = f"{toegevoegde_rollen[0]['Instrument']}, {extra_instrument_van_zanger}"
                        else:
                            gitaar_mensen = kandidaten[kandidaten['Inst_Lower'].str.contains("gitaar|guitar", na=False)]
                            keys_mensen = kandidaten[kandidaten['Inst_Lower'].str.contains("toetsen|keys|keyboard|piano", na=False)]
                            
                            gitaar_filter = filter_optimaal(gitaar_mensen, "Gitaar", reeds_gekozen_namen)
                            keys_filter = filter_optimaal(keys_mensen, "Toetsen", reeds_gekozen_namen)
                            
                            beschikbare_mk = pd.concat([gitaar_filter, keys_filter])
                            if not beschikbare_mk.empty:
                                mk = beschikbare_mk.sample(1).iloc[0]
                                toegevoegde_rollen.append({'Naam': mk['Naam'], 'Instrument': mk['Instrument']})
                                reeds_gekozen_namen.append(mk['Naam'])