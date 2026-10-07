import streamlit as st
import pandas as pd
import requests
import random

WEB_APP_URL = "https://script.google.com/macros/s/AKfycbzXpg0gOGRWxnMFcozojnw5F-n8uZ_l0DUWw50lzUVzRmbxtEKQD-ytnCow_GpQLcc1/exec"
NUMMERS_CSV_URL = "https://docs.google.com/spreadsheets/d/1o8uxw9hUk9YMZ0eIRPCZ3_Lglt3CqV-Zu3xlmpu-Xnw/export?format=csv&gid=1454715385"
INSCHRIJVINGEN_CSV_URL = "https://docs.google.com/spreadsheets/d/1o8uxw9hUk9YMZ0eIRPCZ3_Lglt3CqV-Zu3xlmpu-Xnw/export?format=csv&gid=0"

st.set_page_config(page_title="Ultimate Jam Roulette", page_icon="🎸", layout="centered")

wachtwoord = st.sidebar.text_input("Wachtwoord voor beheer:", type="password")
is_admin = (wachtwoord == "jam2026")

if not is_admin:
    st.markdown("<h1 style='text-align: center;'>🎸 ULTIMATE JAM ROULETTE! 🎸</h1>", unsafe_allow_html=True)
    st.write("Welkom! Vul je naam in, kies je instrument en vink de nummers aan die je kent.")
    
    try:
        df_n = pd.read_csv(NUMMERS_CSV_URL)
        beschikbaar = df_n.iloc[:, 0].dropna().astype(str).tolist()
    except:
        beschikbaar = ["Rolling in the Deep", "Superstition"]
        
    with st.form("form"):
        naam = st.text_input("Naam (Voornaam + Achternaam)")
        instrument = st.selectbox("Instrument", ["Gitaar", "Bas", "Zang", "Drums", "Toetsen", "Saxofoon", "Anders"])
        nummers = st.multiselect("Kies nummers:", beschikbaar)
        nieuw = st.text_input("Nieuw nummer toevoegen (optioneel):")
        
        if st.form_submit_button("Inschrijven!", type="primary"):
            if not naam:
                st.warning("Vul je naam in.")
            else:
                lijst = list(nummers)
                if nieuw.strip():
                    lijst.extend([n.strip() for n in nieuw.split(',') if n.strip()])
                if not lijst:
                    st.warning("Kies minimaal één nummer.")
                else:
                    try:
                        res = requests.post(WEB_APP_URL, json={"naam": naam, "instrument": instrument, "nummers": lijst})
                        if res.status_code == 200:
                            st.success("Inschrijving gelukt!")
                            st.balloons()
                        else:
                            st.error("Fout bij opslaan.")
                    except Exception as e:
                        st.error(f"Fout: {e}")
else:
    st.markdown(
        "<style>header[data-testid='stHeader'] {visibility: hidden;} .stApp, .block-container {background-color: #000000 !important; color: #ffffff !important;} [data-testid='stSidebar'] {background-color: #111111 !important;} div.stButton > button:first-child {font-size: 2.5rem !important; padding: 22px !important; border-radius: 20px !important; font-weight: 900 !important; background: linear-gradient(135deg, #ff4b4b 0%, #ff6b6b 100%) !important; color: white !important; border: 4px solid #ffffff !important; text-transform: uppercase;}</style>",
        unsafe_allow_html=True
    )
    
    st.markdown("<h1 style='text-align: center; font-size: 2.8rem; font-weight: 800; margin-bottom: 0px;'>🎸 ULTIMATE JAM ROULETTE 🎸</h1>", unsafe_allow_html=True)
    
    try:
        df = pd.read_csv(INSCHRIJVINGEN_CSV_URL)
        if df.empty or 'html' in str(df.columns[0]).lower():
            st.warning("Kon Google Sheet niet laden.")
            if st.button("Verversen"): st.rerun()
        else:
            data = []
            for _, r in df.iterrows():
                if pd.isna(r.iloc[0]) or pd.isna(r.iloc[1]) or pd.isna(r.iloc[2]): continue
                for n in [x.strip() for x in str(r.iloc[2]).split(',') if x.strip() and x.strip() != 'nan']:
                    data.append({'Nummer': n, 'Naam': str(r.iloc[0]).strip(), 'Instrument': str(r.iloc[1]).strip()})
            
            df_bands = pd.DataFrame(data)
            if df_bands.empty:
                st.info("Nog geen inschrijvingen.")
            else:
                uniek = df_bands['Nummer'].unique().tolist()
                
                if 'geschiedenis' not in st.session_state: st.session_state['geschiedenis'] = []
                if 'huidig_nummer' not in st.session_state: st.session_state['huidig_nummer'] = None
                if 'huidige_band' not in st.session_state: st.session_state['huidige_band'] = None
                
                # Toon huidige band indien geloot
                if st.session_state['huidig_nummer']:
                    st.markdown(f"<h1 style='text-align: center; color: #ff4b4b; font-size: 2.8rem; margin-bottom: 5px;'>🎵 {st.session_state['huidig_nummer']} 🎵</h1>", unsafe_allow_html=True)
                    st.markdown("<h3 style='text-align: center; color: #ffffff; margin-top: 0px;'>🎸 De Band op het Podium:</h3>", unsafe_allow_html=True)
                    for _, row in st.session_state['huidige_band'].iterrows():
                        st.markdown(f"<div style='text-align: center; font-size: 1.4rem; padding: 12px; background-color: #121212; border-radius: 12px; margin: 8px 0; border: 2px solid #333333;'><b>{row['Naam']}</b> — <i style='color: #ff6b6b;'>{row['Instrument']}</i></div>", unsafe_allow_html=True)
                    st.markdown("<hr style='margin: 15px 0; border-color: #333333;'>", unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # CENTRAAL GEPLAATSTE GROTE JAM KNOP
                col1, col2, col3 = st.columns([1, 3, 1])
                with col2:
                    jam_geklikt = st.button("🔥  JAM!  🔥", type="primary", use_container_width=True)
                
                if jam_geklikt:
                    nog_te_spelen = [n for n in uniek if n not in st.session_state['geschiedenis']]
                    
                    volledig_geldig = []
                    gedeeltelijk_geldig = []
                    
                    for num in nog_te_spelen:
                        k = df_bands[df_bands['Nummer'] == num]
                        hz = any(k['Instrument'].str.lower().str.contains("zang|vocal|zanger", na=False))
                        hg = any(k['Instrument'].str.lower().str.contains("gitaar|guitar", na=False)) or any(k['Instrument'].str.lower().str.contains("toetsen|keys|keyboard|piano", na=False))
                        hd = any(k['Instrument'].str.lower().str.contains("drum", na=False))
                        hb = any(k['Instrument'].str.lower().str.contains("bas|bass", na=False))
                        
                        if hz and hg and hd and hb:
                            volledig_geldig.append(num)
                        elif hz and hg:
                            gedeeltelijk_geldig.append(num)
                    
                    aantal_gespeeld = len(st.session_state['geschiedenis'])
                    is_partieel_beurt = (aantal_gespeeld > 0 and aantal_gespeeld % 3 == 0)
                    
                    gekozen = None
                    is_partieel = False
                    
                    if is_partieel_beurt and gedeeltelijk_geldig:
                        gekozen = random.choice(gedeeltelijk_geldig)
                        is_partieel = True
                    elif volledig_geldig:
                        gekozen = random.choice(volledig_geldig)
                        is_partieel = False
                    elif gedeeltelijk_geldig:
                        gekozen = random.choice(gedeeltelijk_geldig)
                        is_partieel = True
                    
                    if gekozen:
                        st.session_state['geschiedenis'].append(gekozen)
                        kand = df_bands[df_bands['Nummer'] == gekozen]
                        
                        band = []
                        gekozen_namen = []
                        
                        # 1. Zang (max 1)
                        sub_zang = kand[kand['Instrument'].str.lower().str.contains("zang|vocal|zanger", na=False)]
                        if not sub_zang.empty:
                            r = sub_zang.sample(1).iloc[0]
                            band.append({'Naam': r['Naam'], 'Instrument': r['Instrument']})
                            gekozen_namen.append(r['Naam'])
                            
                        # 2. Gitaren (max 2)
                        sub_gitaar = kand[kand['Instrument'].str.lower().str.contains("gitaar|guitar", na=False)]
                        sub_gitaar = sub_gitaar[~sub_gitaar['Naam'].isin(gekozen_namen)]
                        aantal_gitaren_te_pakken = min(2, len(sub_gitaar))
                        if aantal_gitaren_te_pakken > 0:
                            gitaren_lijst = sub_gitaar.sample(aantal_gitaren_te_pakken)
                            for _, r in gitaren_lijst.iterrows():
                                band.append({'Naam': r['Naam'], 'Instrument': r['Instrument']})
                                gekozen_namen.append(r['Naam'])

                        # 3. Toetsen (max 1)
                        sub_toetsen = kand[kand['Instrument'].str.lower().str.contains("toetsen|keys|keyboard|piano", na=False)]
                        sub_toetsen = sub_toetsen[~sub_toetsen['Naam'].isin(gekozen_namen)]
                        if not sub_toetsen.empty:
                            r = sub_toetsen.sample(1).iloc[0]
                            band.append({'Naam': r['Naam'], 'Instrument': r['Instrument']})
                            gekozen_namen.append(r['Naam'])
                        
                        # 4. Bas (max 1, indien aanwezig)
                        sub_bas = kand[kand['Instrument'].str.lower().str.contains("bas|bass", na=False)]
                        sub_bas = sub_bas[~sub_bas['Naam'].isin(gekozen_namen)]
                        if not sub_bas.empty:
                            r = sub_bas.sample(1).iloc[0]
                            band.append({'Naam': r['Naam'], 'Instrument': r['Instrument']})
                            gekozen_namen.append(r['Naam'])

                        # 5. Saxofoon (max 1, indien aanwezig)
                        sub_sax = kand[kand['Instrument'].str.lower().str.contains("saxofoon|sax", na=False)]
                        sub_sax = sub_sax[~sub_sax['Naam'].isin(gekozen_namen)]
                        if not sub_sax.empty:
                            r = sub_sax.sample(1).iloc[0]
                            band.append({'Naam': r['Naam'], 'Instrument': r['Instrument']})
                            gekozen_namen.append(r['Naam'])

                        # 6. Anders (max 1, indien aanwezig)
                        sub_anders = kand[kand['Instrument'].str.lower().str.contains("anders", na=False)]
                        sub_anders = sub_anders[~sub_anders['Naam'].isin(gekozen_namen)]
                        if not sub_anders.empty:
                            r = sub_anders.sample(1).iloc[0]
                            band.append({'Naam': r['Naam'], 'Instrument': r['Instrument']})
                            gekozen_namen.append(r['Naam'])
                        
                        # 7. Drums (max 1, alleen bij volledige beurt)
                        if not is_partieel:
                            sub_drum = kand[kand['Instrument'].str.lower().str.contains("drum", na=False)]
                            sub_drum = sub_drum[~sub_drum['Naam'].isin(gekozen_namen)]
                            if not sub_drum.empty:
                                r = sub_drum.sample(1).iloc[0]
                                band.append({'Naam': r['Naam'], 'Instrument': r['Instrument']})
                                gekozen_namen.append(r['Naam'])
                                
                        st.session_state['huidig_nummer'] = gekozen
                        st.session_state['huidige_band'] = pd.DataFrame(band)
                        st.rerun()
                    else:
                        st.warning("Geen geschikte nummers beschikbaar om te loten!")
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # UITGEBREID OVERZICHT ONDER DE KNOP
                with st.expander("📋 Uitgebreid overzicht van alle nummers & status"):
                    st.write("Hier zie je welke nummers klaar zijn voor een volledige band, welke gedeeltelijk zijn, of welke essentiële bezetting ontbreekt.")
                    overzicht = []
                    for num in uniek:
                        k = df_bands[df_bands['Nummer'] == num]
                        hz = any(k['Instrument'].str.lower().str.contains("zang|vocal|zanger", na=False))
                        hg = any(k['Instrument'].str.lower().str.contains("gitaar|guitar", na=False)) or any(k['Instrument'].str.lower().str.contains("toetsen|keys|keyboard|piano", na=False))
                        hd = any(k['Instrument'].str.lower().str.contains("drum", na=False))
                        hb = any(k['Instrument'].str.lower().str.contains("bas|bass", na=False))
                        
                        if num in st.session_state['geschiedenis']:
                            status = "✅ Al gespeeld"
                        elif hz and hg and hd and hb:
                            status = "🟢 Volledige bezetting (Klaar)"
                        elif hz and hg:
                            status = "🟡 Gedeeltelijke bezetting (Zang + Melodisch OK)"
                        else:
                            status = "🔴 Niet in aanmerking (essentiële bezetting ontbreekt)"
                            
                        overzicht.append({
                            "Nummer": num, 
                            "Inschrijvingen": len(k), 
                            "Status": status,
                            "Zang": "✅" if hz else "❌",
                            "Melodisch/Gitaar": "✅" if hg else "❌",
                            "Drums": "✅" if hd else "❌",
                            "Bas": "✅" if hb else "❌"
                        })
                    st.dataframe(pd.DataFrame(overzicht), use_container_width=True)
                
                if st.session_state['geschiedenis']:
                    if st.button("↩️ Reset geschiedenis"):
                        st.session_state['geschiedenis'] = []
                        st.rerun()
    except Exception as e:
        st.error(f"Fout in admin paneel: {e}")