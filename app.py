import streamlit as st
import pandas as pd
import requests
import random
import time

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
        """
        <style>
        header[data-testid='stHeader'] {visibility: hidden;}
        .stApp, .block-container {background-color: #000000 !important; color: #ffffff !important;}
        [data-testid='stSidebar'] {background-color: #111111 !important;}
        div.stButton > button:first-child {font-size: 2.5rem !important; padding: 22px !important; border-radius: 20px !important; font-weight: 900 !important; background: linear-gradient(135deg, #ff4b4b 0%, #ff6b6b 100%) !important; color: white !important; border: 4px solid #ffffff !important; text-transform: uppercase;}
        .reroll-container { display: flex; align-items: center; justify-content: center; position: relative; }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown("<h1 style='text-align: center; font-size: 2.8rem; font-weight: 800; margin-bottom: 0px;'>🎸 ULTIMATE JAM ROULETTE 🎸</h1>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
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
                if 'vorige_muzikanten' not in st.session_state: st.session_state['vorige_muzikanten'] = []
                if 'fase' not in st.session_state: st.session_state['fase'] = 'idle'
                if 'cached_winnende_rollen' not in st.session_state: st.session_state['cached_winnende_rollen'] = []
                if 'cached_person_instruments' not in st.session_state: st.session_state['cached_person_instruments'] = {}
                
                podium_slot = st.empty()
                
                def bouw_podium_html(nummer, band_lijst, rol_bezig=None, slot_naam=""):
                    html = f"<h1 style='text-align: center; color: #ff4b4b; font-size: 2.8rem; margin-bottom: 5px;'>🎵 {nummer} 🎵</h1>"
                    html += "<h3 style='text-align: center; color: #ffffff; margin-top: 0px;'>🎸 De Band op het Podium:</h3>"
                    
                    for item in band_lijst:
                        r, n, ins = item[0], item[1], item[2]
                        # De rol tussen haakjes wordt hier weggelaten uit de weergave
                        html += f"<div style='text-align: center; font-size: 1.4rem; padding: 12px; background-color: #121212; border-radius: 12px; margin: 8px 0; border: 2px solid #333333;'><b>{n}</b> — <i style='color: #ff6b6b;'>{ins}</i></div>"
                    
                    if rol_bezig:
                        # Tijdens de animatie tonen we ook alleen de instrumentnaam of rol in het groot
                        scherm_rol = "Gitaar" if "gitaar" in rol_bezig.lower() else rol_bezig
                        html += f"<div style='text-align: center; font-size: 1.4rem; padding: 12px; background-color: #1a1a1a; border-radius: 12px; margin: 8px 0; border: 2px dashed #ff4b4b;'><b style='color: #ff4b4b;'>{scherm_rol.upper()} DECODING...</b> <br><span style='font-size: 1.8rem; font-family: monospace; letter-spacing: 2px; color: #00ffcc;'>{slot_naam}</span></div>"
                    
                    html += "<hr style='margin: 15px 0; border-color: #333333;'>"
                    return html

                # --- RENDER LOGICA IN DE PODIUM CONTAINER ---
                if st.session_state['fase'] == 'wacht_op_onthulling':
                    podium_slot.markdown(
                        f"<h1 style='text-align: center; color: #ff4b4b; font-size: 2.8rem; margin-bottom: 5px;'>🎵 {st.session_state['huidig_nummer']} 🎵</h1>"
                        f"<h3 style='text-align: center; color: #ffffff; margin-top: 0px;'>🎸 Klaar voor de band... Klik op 'Onthul Band'!</h3>"
                        f"<hr style='margin: 15px 0; border-color: #333333;'>",
                        unsafe_allow_html=True
                    )
                elif st.session_state['fase'] == 'klaar' and st.session_state['huidig_nummer'] and st.session_state['huidige_band'] is not None:
                    with podium_slot.container():
                        st.markdown(f"<h1 style='text-align: center; color: #ff4b4b; font-size: 2.8rem; margin-bottom: 5px;'>🎵 {st.session_state['huidig_nummer']} 🎵</h1>", unsafe_allow_html=True)
                        st.markdown("<h3 style='text-align: center; color: #ffffff; margin-top: 0px;'>🎸 De Band op het Podium:</h3>", unsafe_allow_html=True)
                        
                        band_df = st.session_state['huidige_band']
                        for idx, row in band_df.iterrows():
                            cols = st.columns([11, 1])
                            with cols[0]:
                                # Ook hier is de rol tussen haakjes weggelaten
                                st.markdown(f"<div style='text-align: center; font-size: 1.4rem; padding: 12px; background-color: #121212; border-radius: 12px; margin: 8px 0; border: 2px solid #333333;'><b>{row['Naam']}</b> — <i style='color: #ff6b6b;'>{row['Instrument']}</i></div>", unsafe_allow_html=True)
                            with cols[1]:
                                st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)
                                if st.button("🔄", key=f"reroll_{idx}", help=f"Vervang {row['Instrument']}"):
                                    gekozen_nummer = st.session_state['huidig_nummer']
                                    doel_rol = row['Rol']
                                    zoek_rol = "gitaar" if "gitaar" in doel_rol.lower() else doel_rol
                                    kand = df_bands[df_bands['Nummer'] == gekozen_nummer]
                                    
                                    if zoek_rol.lower() == 'zang':
                                        sub = kand[kand['Instrument'].str.lower().str.contains("zang|vocal|zanger", na=False)]
                                    elif zoek_rol.lower() == 'gitaar':
                                        sub = kand[kand['Instrument'].str.lower().str.contains("gitaar|guitar", na=False)]
                                    elif zoek_rol.lower() == 'toetsen':
                                        sub = kand[kand['Instrument'].str.lower().str.contains("toetsen|keys|keyboard|piano", na=False)]
                                    elif zoek_rol.lower() == 'bas':
                                        sub = kand[kand['Instrument'].str.lower().str.contains("bas|bass", na=False)]
                                    elif zoek_rol.lower() == 'saxofoon':
                                        sub = kand[kand['Instrument'].str.lower().str.contains("saxofoon|sax", na=False)]
                                    elif zoek_rol.lower() == 'anders':
                                        sub = kand[kand['Instrument'].str.lower().str.contains("anders", na=False)]
                                    elif zoek_rol.lower() == 'drums':
                                        sub = kand[kand['Instrument'].str.lower().str.contains("drum", na=False)]
                                    else:
                                        sub = pd.DataFrame()

                                    beschikbare_kandidaten = sub[~sub['Naam'].isin([row['Naam']])]
                                    if not beschikbare_kandidaten.empty:
                                        nieuwe_keuze = beschikbare_kandidaten.sample(1).iloc[0]
                                        band_df.at[idx, 'Naam'] = nieuwe_keuze['Naam']
                                        band_df.at[idx, 'Instrument'] = nieuwe_keuze['Instrument']
                                        st.session_state['huidige_band'] = band_df
                                        st.rerun()
                                    else:
                                        st.toast(f"Geen andere reservekandidaten voor dit instrument!", icon="⚠️")
                        st.markdown("<hr style='margin: 15px 0; border-color: #333333;'>", unsafe_allow_html=True)
                else:
                    podium_slot.empty()

                st.markdown("<br>", unsafe_allow_html=True)

                # --- HOOFDKNOPPEN ---
                if st.session_state['fase'] == 'wacht_op_onthulling':
                    col1, col2, col3 = st.columns([1, 3, 1])
                    with col2:
                        onthul_geklikt = st.button("🔥  ONTHUL BAND!  🔥", type="primary", use_container_width=True)
                    
                    if onthul_geklikt:
                        raw_winnende_rollen = st.session_state['cached_winnende_rollen']
                        person_instruments = st.session_state['cached_person_instruments']
                        gekozen = st.session_state['huidig_nummer']
                        
                        winnende_rollen = []
                        for item in raw_winnende_rollen:
                            if isinstance(item, (list, tuple)) and len(item) >= 3:
                                winnende_rollen.append((item[0], item[1], item[2]))

                        huidige_bouw_band = []
                        chars_pool = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz "
                        
                        for rol_type, winnaar_naam, winnaar_inst in winnende_rollen:
                            target_length = len(winnaar_naam)
                            frames = 50
                            
                            for frame in range(frames):
                                locked_count = int((frame / (frames - 1)) * target_length) if frames > 1 else target_length
                                display_naam = ""
                                for i, char in enumerate(winnaar_naam):
                                    if char == " ":
                                        display_naam += " "
                                    elif i < locked_count:
                                        display_naam += char
                                    else:
                                        display_naam += random.choice(chars_pool)
                                        
                                animatie_html = bouw_podium_html(gekozen, huidige_bouw_band, rol_bezig=rol_type, slot_naam=display_naam)
                                podium_slot.markdown(animatie_html, unsafe_allow_html=True)
                                time.sleep(0.05)
                            
                            huidige_bouw_band.append((rol_type, winnaar_naam, winnaar_inst))
                            vaste_html = bouw_podium_html(gekozen, huidige_bouw_band)
                            podium_slot.markdown(vaste_html, unsafe_allow_html=True)
                            time.sleep(0.2)
                        
                        st.session_state['huidige_band'] = pd.DataFrame(huidige_bouw_band, columns=['Rol', 'Naam', 'Instrument'])
                        st.session_state['vorige_muzikanten'] = list(person_instruments.keys())
                        st.session_state['fase'] = 'klaar'
                        st.rerun()
                else:
                    col1, col2, col3 = st.columns([1, 3, 1])
                    with col2:
                        jam_geklikt = st.button("🔥  JAM!  🔥", type="primary", use_container_width=True)
                    
                    if jam_geklikt:
                        st.session_state['huidige_band'] = None
                        st.session_state['fase'] = 'idle'
                        
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
                            
                            # --- NUMMER ROULETTE ANIMATIE ---
                            alle_mogelijke_nummers = uniek
                            willekeurige_loop_nummers = random.choices(alle_mogelijke_nummers, k=25)
                            animatie_nummers = willekeurige_loop_nummers + [gekozen]
                            
                            for idx, dummy_num in enumerate(animatie_nummers):
                                is_laatste = (idx == len(animatie_nummers) - 1)
                                kleur = "#ff4b4b" if is_laatste else "#ffffff"
                                titel = "🎵 WINNEND NUMMER! 🎵" if is_laatste else "🎰 NUMMER ROULETTE... 🎰"
                                
                                podium_slot.markdown(
                                    f"<h1 style='text-align: center; color: #ff4b4b; font-size: 2.8rem; margin-bottom: 5px;'>{titel}</h1>"
                                    f"<h1 style='text-align: center; color: {kleur}; font-size: 2.5rem; margin: 10px 0;'>🎵 {dummy_num} 🎵</h1>"
                                    f"<hr style='margin: 15px 0; border-color: #333333;'>",
                                    unsafe_allow_html=True
                                )
                                delay = 0.08 if idx < 18 else (0.15 if idx < 23 else 0.25)
                                time.sleep(delay if not is_laatste else 0.5)

                            # Bereken de band achter de schermen
                            kand = df_bands[df_bands['Nummer'] == gekozen]
                            person_instruments = {} 
                            temp_vorige = list(st.session_state['vorige_muzikanten'])
                            
                            def kan_persoon_instrument_krijgen(naam, inst_groep):
                                huidige_insts = person_instruments.get(naam, set())
                                heeft_zang = any("zang" in i.lower() for i in huidige_insts)
                                heeft_ander = any("zang" not in i.lower() for i in huidige_insts)
                                is_zang = "zang" in inst_groep.lower()
                                
                                if is_zang:
                                    return not heeft_zang
                                else:
                                    return not heeft_ander
                            
                            def kies_muzikant_voor_rol(sub_df, rol_naam):
                                if sub_df.empty: return None
                                geldige_rijen = []
                                for _, r in sub_df.iterrows():
                                    if kan_persoon_instrument_krijgen(r['Naam'], rol_naam):
                                        geldige_rijen.append(r)
                                if not geldige_rijen: return None
                                
                                geldig_df = pd.DataFrame(geldige_rijen)
                                vrij = geldig_df[~geldig_df['Naam'].isin(temp_vorige)]
                                if not vrij.empty:
                                    return vrij.sample(1).iloc[0]
                                else:
                                    return geldig_df.sample(1).iloc[0]

                            winnende_rollen = []
                            
                            # 1. Zang
                            sub_zang = kand[kand['Instrument'].str.lower().str.contains("zang|vocal|zanger", na=False)]
                            r_zang = kies_muzikant_voor_rol(sub_zang, "zang")
                            if r_zang is not None:
                                winnende_rollen.append(('Zang', r_zang['Naam'], r_zang['Instrument']))
                                person_instruments.setdefault(r_zang['Naam'], set()).add(r_zang['Instrument'])
                                
                            # 2. Gitaren
                            sub_gitaar = kand[kand['Instrument'].str.lower().str.contains("gitaar|guitar", na=False)]
                            gitaren_gekozen = 0
                            while gitaren_gekozen < 2:
                                r_git = kies_muzikant_voor_rol(sub_gitaar, "gitaar")
                                if r_git is None: break
                                rol_label = "Gitaar" if gitaren_gekozen == 0 else "Tweede Gitaar"
                                winnende_rollen.append((rol_label, r_git['Naam'], r_git['Instrument']))
                                person_instruments.setdefault(r_git['Naam'], set()).add(r_git['Instrument'])
                                sub_gitaar = sub_gitaar[~((sub_gitaar['Naam'] == r_git['Naam']) & (sub_gitaar['Instrument'] == r_git['Instrument']))]
                                gitaren_gekozen += 1

                            # 3. Toetsen
                            sub_toetsen = kand[kand['Instrument'].str.lower().str.contains("toetsen|keys|keyboard|piano", na=False)]
                            r_toetsen = kies_muzikant_voor_rol(sub_toetsen, "toetsen")
                            if r_toetsen is not None:
                                winnende_rollen.append(('Toetsen', r_toetsen['Naam'], r_toetsen['Instrument']))
                                person_instruments.setdefault(r_toetsen['Naam'], set()).add(r_toetsen['Instrument'])
                            
                            melodische_rollen = []
                            for item in winnende_rollen:
                                if len(item) >= 3:
                                    melodische_rollen.append(item[0].lower())
                            
                            heeft_melodisch = any('gitaar' in rol or 'toetsen' in rol for rol in melodische_rollen) or any(any(inst.lower() in ['gitaar', 'guitar', 'toetsen', 'keys', 'keyboard', 'piano'] for inst in item) for item in winnende_rollen)
                            
                            if not winnende_rollen or not heeft_melodisch:
                                st.warning(f"Nummer '{gekozen}' heeft onvoldoende melodische bezetting en wordt overgeslagen.")
                                st.session_state['geschiedenis'].pop()
                            else:
                                # 4. Bas
                                sub_bas = kand[kand['Instrument'].str.lower().str.contains("bas|bass", na=False)]
                                r_bas = kies_muzikant_voor_rol(sub_bas, "bas")
                                if r_bas is not None:
                                    winnende_rollen.append(('Bas', r_bas['Naam'], r_bas['Instrument']))
                                    person_instruments.setdefault(r_bas['Naam'], set()).add(r_bas['Instrument'])

                                # 5. Saxofoon
                                sub_sax = kand[kand['Instrument'].str.lower().str.contains("saxofoon|sax", na=False)]
                                r_sax = kies_muzikant_voor_rol(sub_sax, "saxofoon")
                                if r_sax is not None:
                                    winnende_rollen.append(('Saxofoon', r_sax['Naam'], r_sax['Instrument']))
                                    person_instruments.setdefault(r_sax['Naam'], set()).add(r_sax['Instrument'])

                                # 6. Anders
                                sub_anders = kand[kand['Instrument'].str.lower().str.contains("anders", na=False)]
                                r_anders = kies_muzikant_voor_rol(sub_anders, "anders")
                                if r_anders is not None:
                                    winnende_rollen.append(('Anders', r_anders['Naam'], r_anders['Instrument']))
                                    person_instruments.setdefault(r_anders['Naam'], set()).add(r_anders['Instrument'])
                                
                                # 7. Drums
                                if not is_partieel:
                                    sub_drum = kand[kand['Instrument'].str.lower().str.contains("drum", na=False)]
                                    r_drum = kies_muzikant_voor_rol(sub_drum, "drum")
                                    if r_drum is not None:
                                        winnende_rollen.append(('Drums', r_drum['Naam'], r_drum['Instrument']))
                                        person_instruments.setdefault(r_drum['Naam'], set()).add(r_drum['Instrument'])

                                schone_rollen = []
                                for item in winnende_rollen:
                                    if len(item) >= 3:
                                        schone_rollen.append((item[0], item[1], item[2]))

                                st.session_state['huidig_nummer'] = gekozen
                                st.session_state['cached_winnende_rollen'] = schone_rollen
                                st.session_state['cached_person_instruments'] = person_instruments
                                st.session_state['fase'] = 'wacht_op_onthulling'
                                st.rerun()
                        else:
                            st.warning("Geen geschikte nummers beschikbaar om te loten!")
                
                st.markdown("<br>", unsafe_allow_html=True)
                
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
                        st.session_state['vorige_muzikanten'] = []
                        st.session_state['huidig_nummer'] = None
                        st.session_state['huidige_band'] = None
                        st.session_state['fase'] = 'idle'
                        st.rerun()
    except Exception as e:
        st.error(f"Fout in admin paneel: {e}")