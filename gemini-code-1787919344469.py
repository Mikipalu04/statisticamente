import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson

# Configurazione della Pagina
st.set_page_config(
    page_title="Serie A Shot Value Dashboard",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# STILE CSS PERSONALIZZATO (UI/UX Moderna & Dark Theme)
# ---------------------------------------------------------
st.markdown("""
    <style>
    /* Background e Font */
    .main {
        background-color: #0e1117;
        color: #ffffff;
    }
    
    /* Card Partita */
    .match-card {
        background: linear-gradient(135deg, #1e2640 0%, #111827 100%);
        border: 1px solid #374151;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 25px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
    }
    
    /* Stemmi e Nomi Squadre */
    .team-logo {
        width: 90px;
        height: 90px;
        object-fit: contain;
        filter: drop-shadow(0 4px 6px rgba(0,0,0,0.3));
    }
    .team-name {
        font-size: 24px;
        font-weight: 800;
        margin-top: 8px;
        letter-spacing: 0.5px;
    }
    .vs-badge {
        background: #ef4444;
        color: white;
        font-weight: 900;
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 14px;
        letter-spacing: 1px;
    }
    
    /* Box Metriche */
    .metric-container {
        background: #1f2937;
        border-radius: 12px;
        padding: 16px;
        border-left: 4px solid #3b82f6;
        text-align: center;
    }
    .metric-value {
        font-size: 28px;
        font-weight: 700;
        color: #60a5fa;
    }
    .metric-label {
        font-size: 13px;
        color: #9ca3af;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Value Bet Card Highlight */
    .value-box-success {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(6, 78, 59, 0.3) 100%);
        border: 1px solid #10b981;
        border-radius: 12px;
        padding: 18px;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# DATABASE SERIE A: STEMMI E METRICHE STORICHE TIRI
# ---------------------------------------------------------
TEAMS_DB = {
    'AC Milan': {
        'logo': 'https://upload.wikimedia.org/wikipedia/commons/d/d0/AC-Milan-logo.svg',
        'tiri_fatti': 15.6, 'tiri_concessi': 9.2, 'porta_fatti': 5.4, 'porta_concessi': 3.1
    },
    'Venezia': {
        'logo': 'https://upload.wikimedia.org/wikipedia/it/c/c8/Venezia_FC_logo_2022.png',
        'tiri_fatti': 10.1, 'tiri_concessi': 16.2, 'porta_fatti': 3.2, 'porta_concessi': 5.8
    },
    'Inter': {
        'logo': 'https://upload.wikimedia.org/wikipedia/commons/0/05/FC_Internazionale_Milano_2021.svg',
        'tiri_fatti': 16.8, 'tiri_concessi': 8.3, 'porta_fatti': 6.1, 'porta_concessi': 2.4
    },
    'Lecce': {
        'logo': 'https://upload.wikimedia.org/wikipedia/it/a/a7/US_Lecce_2001.png',
        'tiri_fatti': 11.5, 'tiri_concessi': 14.2, 'porta_fatti': 3.6, 'porta_concessi': 4.5
    },
    'Juventus': {
        'logo': 'https://upload.wikimedia.org/wikipedia/commons/b/bc/Juventus_FC_2017_icon_%28black%29.svg',
        'tiri_fatti': 14.5, 'tiri_concessi': 9.0, 'porta_fatti': 5.0, 'porta_concessi': 2.9
    },
    'AS Roma': {
        'logo': 'https://upload.wikimedia.org/wikipedia/en/f/f7/AS_Roma_logo_%282017%29.svg',
        'tiri_fatti': 14.1, 'tiri_concessi': 11.0, 'porta_fatti': 4.6, 'porta_concessi': 3.5
    },
    'Napoli': {
        'logo': 'https://upload.wikimedia.org/wikipedia/commons/b/b5/SSC_Neapel.svg',
        'tiri_fatti': 15.4, 'tiri_concessi': 8.9, 'porta_fatti': 5.3, 'porta_concessi': 2.7
    },
    'Bologna': {
        'logo': 'https://upload.wikimedia.org/wikipedia/commons/5/5b/Bologna_fc_logo.svg',
        'tiri_fatti': 12.8, 'tiri_concessi': 10.5, 'porta_fatti': 4.1, 'porta_concessi': 3.3
    },
    'Atalanta': {
        'logo': 'https://upload.wikimedia.org/wikipedia/it/2/28/Atalanta_BC_logo.svg',
        'tiri_fatti': 15.8, 'tiri_concessi': 10.4, 'porta_fatti': 5.7, 'porta_concessi': 3.4
    },
    'Fiorentina': {
        'logo': 'https://upload.wikimedia.org/wikipedia/commons/7/79/ACF_Fiorentina_2022.svg',
        'tiri_fatti': 14.0, 'tiri_concessi': 10.2, 'porta_fatti': 4.7, 'porta_concessi': 3.3
    },
    'Lazio': {
        'logo': 'https://upload.wikimedia.org/wikipedia/it/3/36/SS_Lazio_logo.svg',
        'tiri_fatti': 13.5, 'tiri_concessi': 11.2, 'porta_fatti': 4.4, 'porta_concessi': 3.6
    },
    'Verona': {
        'logo': 'https://upload.wikimedia.org/wikipedia/it/9/92/Hellas_Verona_FC_logo_2020.svg',
        'tiri_fatti': 10.8, 'tiri_concessi': 14.5, 'porta_fatti': 3.3, 'porta_concessi': 4.7
    }
}

# ---------------------------------------------------------
# CALENDARIO UFFICIALE: 2ª GIORNATA SERIE A
# ---------------------------------------------------------
GIORNATA_2 = [
    {"casa": "AC Milan", "trasferta": "Venezia", "orario": "Oggi, 20:45"},
    {"casa": "Inter", "trasferta": "Lecce", "orario": "Domani, 18:30"},
    {"casa": "Juventus", "trasferta": "AS Roma", "orario": "Domani, 20:45"},
    {"casa": "Napoli", "trasferta": "Bologna", "orario": "Domenica, 18:30"},
    {"casa": "Atalanta", "trasferta": "Fiorentina", "orario": "Domenica, 20:45"},
    {"casa": "Lazio", "trasferta": "Verona", "orario": "Lunedì, 20:45"}
]

# ---------------------------------------------------------
# UI HEADER & SELEZIONE MATCH
# ---------------------------------------------------------
st.markdown("<h1 style='text-align: center; color: #60a5fa;'>⚽ SERIE A SHOT PREDICTOR</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #9ca3af; font-size: 16px;'>Modulo Analisi Tiri & Value Bet • <b>2ª Giornata di Campionato</b></p>", unsafe_allow_html=True)
st.markdown("---")

# Selettore Partite della 2ª Giornata
partite_labels = [f"🏟️ {m['casa']} vs {m['trasferta']} ({m['orario']})" for m in GIORNATA_2]
partita_scelta_idx = st.selectbox("Seleziona la partita da analizzare:", range(len(partite_labels)), format_func=lambda x: partite_labels[x])

match = GIORNATA_2[partita_scelta_idx]
team_c = TEAMS_DB[match['casa']]
team_t = TEAMS_DB[match['trasferta']]

# ---------------------------------------------------------
# CARD MATCH WITH LOGOS
# ---------------------------------------------------------
st.markdown(f"""
    <div class="match-card">
        <div style="display: flex; justify-content: space-around; align-items: center; text-align: center;">
            <div style="flex: 1;">
                <img src="{team_c['logo']}" class="team-logo"><br>
                <div class="team-name">{match['casa']}</div>
                <span style="color: #9ca3af; font-size: 14px;">Casa</span>
            </div>
            <div>
                <span class="vs-badge">VS</span>
                <div style="color: #9ca3af; font-size: 13px; margin-top: 8px;">{match['orario']}</div>
            </div>
            <div style="flex: 1;">
                <img src="{team_t['logo']}" class="team-logo"><br>
                <div class="team-name">{match['trasferta']}</div>
                <span style="color: #9ca3af; font-size: 14px;">Trasferta</span>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# ENGINE DI CALCOLO PREVISIONI TIRI
# ---------------------------------------------------------
tiri_attesi_casa = (team_c['tiri_fatti'] + team_t['tiri_concessi']) / 2
tiri_attesi_trasferta = (team_t['tiri_fatti'] + team_c['tiri_concessi']) / 2
tiri_totali_attesi = tiri_attesi_casa + tiri_attesi_trasferta

porta_attesi_casa = (team_c['porta_fatti'] + team_t['porta_concessi']) / 2
porta_attesi_trasferta = (team_t['porta_fatti'] + team_c['porta_concessi']) / 2
porta_totali_attesi = porta_attesi_casa + porta_attesi_trasferta

# Dashboard Previsioni
st.markdown("### 🎯 Previsione Tiri Attesi Match")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f'<div class="metric-container"><div class="metric-value">{tiri_totali_attesi:.1f}</div><div class="metric-label">Tiri Totali Match</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="metric-container"><div class="metric-value">{porta_totali_attesi:.1f}</div><div class="metric-label">Tiri in Porta Totali</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="metric-container"><div class="metric-value">{tiri_attesi_casa:.1f} / {porta_attesi_casa:.1f}</div><div class="metric-label">Tiri Tot / Porta {match["casa"]}</div></div>', unsafe_allow_html=True)
with col4:
    st.markdown(f'<div class="metric-container"><div class="metric-value">{tiri_attesi_trasferta:.1f} / {porta_attesi_trasferta:.1f}</div><div class="metric-label">Tiri Tot / Porta {match["trasferta"]}</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------
# MODULO VALUE BETTING (BOOKMAKER COMPARISON)
# ---------------------------------------------------------
st.markdown("### 💰 Trova Valore nelle Quote (Value Bet Finder)")

c_left, c_right = st.columns(2)

with c_left:
    mercato = st.radio("Seleziona Mercato Tiri", ["Tiri Totali Match", "Tiri in Porta Totali"], horizontal=True)
    linea_default = 25.5 if mercato == "Tiri Totali Match" else 8.5
    linea = st.number_input("Linea Under/Over del Bookmaker", value=linea_default, step=0.5)

with c_right:
    quota_over = st.number_input("Quota Over del Bookmaker", value=1.85, step=0.05)
    quota_under = st.number_input("Quota Under del Bookmaker", value=1.85, step=0.05)

# Calcolo Probabilità tramite Poisson
lambda_ref = tiri_totali_attesi if mercato == "Tiri Totali Match" else porta_totali_attesi
k = int(np.floor(linea))

prob_under = poisson.cdf(k, lambda_ref)
prob_over = 1 - prob_under

quota_reale_over = 1 / prob_over if prob_over > 0 else 999
quota_reale_under = 1 / prob_under if prob_under > 0 else 999

ev_over = (prob_over * quota_over) - 1
ev_under = (prob_under * quota_under) - 1

st.markdown("---")

# Visualizzazione Risultati Value Bet
res_col1, res_col2 = st.columns(2)

with res_col1:
    st.markdown(f"**Probabilità Stimata Over {linea}:** `{prob_over*100:.1f}%` (Quota Reale: **{quota_reale_over:.2f}**)")
    if ev_over > 0:
        st.markdown(f"""
            <div class="value-box-success">
                <h4 style="color: #10b981; margin:0;">🔥 VALUE BET DETECTED (OVER)!</h4>
                <p style="margin: 4px 0 0 0;">Valore Atteso (EV): <b>+{ev_over*100:.2f}%</b><br>La quota del bookmaker ({quota_over}) è più alta del valore reale.</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.info(f"Nessun valore sull'OVER. Expected Value: {ev_over*100:.2f}%")

with res_col2:
    st.markdown(f"**Probabilità Stimata Under {linea}:** `{prob_under*100:.1f}%` (Quota Reale: **{quota_reale_under:.2f}**)")
    if ev_under > 0:
        st.markdown(f"""
            <div class="value-box-success">
                <h4 style="color: #10b981; margin:0;">🔥 VALUE BET DETECTED (UNDER)!</h4>
                <p style="margin: 4px 0 0 0;">Valore Atteso (EV): <b>+{ev_under*100:.2f}%</b><br>La quota del bookmaker ({quota_under}) è più alta del valore reale.</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.info(f"Nessun valore sull'UNDER. Expected Value: {ev_under*100:.2f}%")