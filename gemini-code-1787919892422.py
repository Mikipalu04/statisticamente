import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson

# Configurazione della Pagina
st.set_page_config(
    page_title="Serie A Full Match Predictor",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# STILE CSS PERSONALIZZATO (UI/UX Moderna & Dark Theme)
# ---------------------------------------------------------
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
        color: #ffffff;
    }
    .match-card {
        background: linear-gradient(135deg, #1e2640 0%, #111827 100%);
        border: 1px solid #374151;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 25px;
    }
    .team-title {
        font-size: 24px;
        font-weight: 800;
        text-align: center;
        color: #ffffff;
    }
    .vs-text {
        font-size: 20px;
        font-weight: 900;
        color: #ef4444;
        text-align: center;
    }
    .metric-container {
        background: #1f2937;
        border-radius: 12px;
        padding: 16px;
        border-left: 4px solid #3b82f6;
        text-align: center;
        margin-bottom: 10px;
    }
    .metric-value {
        font-size: 26px;
        font-weight: 700;
        color: #60a5fa;
    }
    .metric-label {
        font-size: 12px;
        color: #9ca3af;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .value-box-success {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(6, 78, 59, 0.3) 100%);
        border: 1px solid #10b981;
        border-radius: 12px;
        padding: 18px;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# DATABASE SERIE A: LOGHI AFFIDABILI E METRICHE
# ---------------------------------------------------------
TEAMS_DB = {
    'AC Milan': {
        'logo': 'https://raw.githubusercontent.com/luuksten/football-logos/main/logos/AC%20Milan.png',
        'tiri_fatti': 15.6, 'tiri_concessi': 9.2, 'porta_fatti': 5.4, 'porta_concessi': 3.1,
        'corner_fatti': 5.8, 'corner_concessi': 3.5, 'falli_fatti': 11.2, 'falli_subiti': 12.5, 'cartellini': 1.8
    },
    'Venezia': {
        'logo': 'https://raw.githubusercontent.com/luuksten/football-logos/main/logos/Venezia.png',
        'tiri_fatti': 10.1, 'tiri_concessi': 16.2, 'porta_fatti': 3.2, 'porta_concessi': 5.8,
        'corner_fatti': 3.4, 'corner_concessi': 6.2, 'falli_fatti': 13.8, 'falli_subiti': 10.5, 'cartellini': 2.4
    },
    'Inter': {
        'logo': 'https://raw.githubusercontent.com/luuksten/football-logos/main/logos/Inter%20Milan.png',
        'tiri_fatti': 16.8, 'tiri_concessi': 8.3, 'porta_fatti': 6.1, 'porta_concessi': 2.4,
        'corner_fatti': 6.2, 'corner_concessi': 3.1, 'falli_fatti': 10.8, 'falli_subiti': 11.8, 'cartellini': 1.6
    },
    'Lecce': {
        'logo': 'https://raw.githubusercontent.com/luuksten/football-logos/main/logos/Lecce.png',
        'tiri_fatti': 11.5, 'tiri_concessi': 14.2, 'porta_fatti': 3.6, 'porta_concessi': 4.5,
        'corner_fatti': 4.1, 'corner_concessi': 5.4, 'falli_fatti': 13.1, 'falli_subiti': 11.2, 'cartellini': 2.3
    },
    'Juventus': {
        'logo': 'https://raw.githubusercontent.com/luuksten/football-logos/main/logos/Juventus.png',
        'tiri_fatti': 14.5, 'tiri_concessi': 9.0, 'porta_fatti': 5.0, 'porta_concessi': 2.9,
        'corner_fatti': 5.2, 'corner_concessi': 3.8, 'falli_fatti': 12.0, 'falli_subiti': 12.0, 'cartellini': 2.1
    },
    'AS Roma': {
        'logo': 'https://raw.githubusercontent.com/luuksten/football-logos/main/logos/AS%20Roma.png',
        'tiri_fatti': 14.1, 'tiri_concessi': 11.0, 'porta_fatti': 4.6, 'porta_concessi': 3.5,
        'corner_fatti': 5.5, 'corner_concessi': 4.2, 'falli_fatti': 12.5, 'falli_subiti': 12.8, 'cartellini': 2.2
    },
    'Napoli': {
        'logo': 'https://raw.githubusercontent.com/luuksten/football-logos/main/logos/Napoli.png',
        'tiri_fatti': 15.4, 'tiri_concessi': 8.9, 'porta_fatti': 5.3, 'porta_concessi': 2.7,
        'corner_fatti': 6.0, 'corner_concessi': 3.3, 'falli_fatti': 10.5, 'falli_subiti': 13.0, 'cartellini': 1.7
    },
    'Bologna': {
        'logo': 'https://raw.githubusercontent.com/luuksten/football-logos/main/logos/Bologna.png',
        'tiri_fatti': 12.8, 'tiri_concessi': 10.5, 'porta_fatti': 4.1, 'porta_concessi': 3.3,
        'corner_fatti': 4.8, 'corner_concessi': 4.0, 'falli_fatti': 12.2, 'falli_subiti': 11.5, 'cartellini': 2.0
    },
    'Atalanta': {
        'logo': 'https://raw.githubusercontent.com/luuksten/football-logos/main/logos/Atalanta.png',
        'tiri_fatti': 15.8, 'tiri_concessi': 10.4, 'porta_fatti': 5.7, 'porta_concessi': 3.4,
        'corner_fatti': 5.9, 'corner_concessi': 3.9, 'falli_fatti': 13.5, 'falli_subiti': 12.2, 'cartellini': 2.2
    },
    'Fiorentina': {
        'logo': 'https://raw.githubusercontent.com/luuksten/football-logos/main/logos/Fiorentina.png',
        'tiri_fatti': 14.0, 'tiri_concessi': 10.2, 'porta_fatti': 4.7, 'porta_concessi': 3.3,
        'corner_fatti': 5.3, 'corner_concessi': 4.1, 'falli_fatti': 11.8, 'falli_subiti': 12.4, 'cartellini': 1.9
    },
    'Lazio': {
        'logo': 'https://raw.githubusercontent.com/luuksten/football-logos/main/logos/Lazio.png',
        'tiri_fatti': 13.5, 'tiri_concessi': 11.2, 'porta_fatti': 4.4, 'porta_concessi': 3.6,
        'corner_fatti': 5.0, 'corner_concessi': 4.3, 'falli_fatti': 11.9, 'falli_subiti': 11.7, 'cartellini': 2.3
    },
    'Verona': {
        'logo': 'https://raw.githubusercontent.com/luuksten/football-logos/main/logos/Hellas%20Verona.png',
        'tiri_fatti': 10.8, 'tiri_concessi': 14.5, 'porta_fatti': 3.3, 'porta_concessi': 4.7,
        'corner_fatti': 3.6, 'corner_concessi': 5.8, 'falli_fatti': 14.2, 'falli_subiti': 10.8, 'cartellini': 2.5
    }
}

# ---------------------------------------------------------
# CALENDARIO SERIE A - 2ª GIORNATA
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
# INTERFACCIA WEB & SELEZIONE MATCH
# ---------------------------------------------------------
st.markdown("<h1 style='text-align: center; color: #60a5fa;'>⚽ SERIE A MATCH STATS PREDICTOR</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #9ca3af; font-size: 15px;'>Modello Predittivo Integrato: <b>Tiri, Angoli, Cartellini & Falli</b></p>", unsafe_allow_html=True)
st.markdown("---")

partite_labels = [f"🏟️ {m['casa']} vs {m['trasferta']} ({m['orario']})" for m in GIORNATA_2]
partita_scelta_idx = st.selectbox("Seleziona la partita da analizzare:", range(len(partite_labels)), format_func=lambda x: partite_labels[x])

match = GIORNATA_2[partita_scelta_idx]
team_c = TEAMS_DB[match['casa']]
team_t = TEAMS_DB[match['trasferta']]

# ---------------------------------------------------------
# CARD PARTITA NATIVA STREAMLIT CON LOGHI CORRETTI
# ---------------------------------------------------------
st.markdown('<div class="match-card">', unsafe_allow_html=True)
c_home, c_vs, c_away = st.columns([2, 1, 2])

with c_home:
    st.image(team_c['logo'], width=100)
    st.markdown(f'<div class="team-title">{match["casa"]}</div>', unsafe_allow_html=True)

with c_vs:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown('<div class="vs-text">VS</div>', unsafe_allow_html=True)
    st.markdown(f'<p style="text-align:center; color:#9ca3af;">{match["orario"]}</p>', unsafe_allow_html=True)

with c_away:
    st.image(team_t['logo'], width=100)
    st.markdown(f'<div class="team-title">{match["trasferta"]}</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# ALGORITMO PREVISIONI MULTI-METRICA
# ---------------------------------------------------------
tiri_casa = (team_c['tiri_fatti'] + team_t['tiri_concessi']) / 2
tiri_trasferta = (team_t['tiri_fatti'] + team_c['tiri_concessi']) / 2
tiri_totali = tiri_casa + tiri_trasferta

porta_casa = (team_c['porta_fatti'] + team_t['porta_concessi']) / 2
porta_trasferta = (team_t['porta_fatti'] + team_c['porta_concessi']) / 2
porta_totali = porta_casa + porta_trasferta

corner_casa = (team_c['corner_fatti'] + team_t['corner_concessi']) / 2
corner_trasferta = (team_t['corner_fatti'] + team_c['corner_concessi']) / 2
corner_totali = corner_casa + corner_trasferta

falli_casa = (team_c['falli_fatti'] + team_t['falli_subiti']) / 2
falli_trasferta = (team_t['falli_fatti'] + team_c['falli_subiti']) / 2
falli_totali = falli_casa + falli_trasferta

cartellini_totali = team_c['cartellini'] + team_t['cartellini']

# ---------------------------------------------------------
# DISPLAY PREVISIONI MATCH
# ---------------------------------------------------------
st.markdown("### 📊 Previsioni Statistiche Complete del Match")

t1, t2, t3, t4 = st.columns(4)
with t1:
    st.markdown(f'<div class="metric-container"><div class="metric-value">{tiri_totali:.1f}</div><div class="metric-label">Tiri Totali</div></div>', unsafe_allow_html=True)
with t2:
    st.markdown(f'<div class="metric-container"><div class="metric-value">{porta_totali:.1f}</div><div class="metric-label">Tiri in Porta</div></div>', unsafe_allow_html=True)
with t3:
    st.markdown(f'<div class="metric-container"><div class="metric-value">{corner_totali:.1f}</div><div class="metric-label">Calci d\'Angolo</div></div>', unsafe_allow_html=True)
with t4:
    st.markdown(f'<div class="metric-container"><div class="metric-value">{falli_totali:.1f} / {cartellini_totali:.1f}</div><div class="metric-label">Falli / Cartellini</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown(f"#### 🔍 Dettaglio Squadre: **{match['casa']}** vs **{match['trasferta']}**")

d1, d2, d3 = st.columns(3)
with d1:
    st.markdown(f"**⚽ Tiri Totali (Porta):**")
    st.write(f"• {match['casa']}: **{tiri_casa:.1f}** ({porta_casa:.1f} in porta)")
    st.write(f"• {match['trasferta']}: **{tiri_trasferta:.1f}** ({porta_trasferta:.1f} in porta)")

with d2:
    st.markdown(f"**🚩 Calci d'Angolo:**")
    st.write(f"• {match['casa']}: **{corner_casa:.1f}** corner")
    st.write(f"• {match['trasferta']}: **{corner_trasferta:.1f}** corner")

with d3:
    st.markdown(f"**🟨 Falli Commessi:**")
    st.write(f"• {match['casa']}: **{falli_casa:.1f}** falli")
    st.write(f"• {match['trasferta']}: **{falli_trasferta:.1f}** falli")

st.markdown("---")

# ---------------------------------------------------------
# VALUE BET CALCULATOR SUL METRIC SCELTO
# ---------------------------------------------------------
st.markdown("### 💰 Calcolatore Value Bet")

c_left, c_right = st.columns(2)

dict_metriche = {
    "Tiri Totali Match": tiri_totali,
    "Tiri in Porta Totali": porta_totali,
    "Calci d'Angolo Totali": corner_totali,
    "Falli Totali Match": falli_totali,
    "Cartellini Totali": cartellini_totali
}

with c_left:
    mercato = st.selectbox("Mercato su cui scommettere", list(dict_metriche.keys()))
    lambda_ref = dict_metriche[mercato]
    linea = st.number_input(f"Linea Under/Over proposta dal Bookmaker per {mercato}", value=float(int(lambda_ref)) + 0.5, step=0.5)

with c_right:
    quota_over = st.number_input("Quota Over del Bookmaker", value=1.85, step=0.05)
    quota_under = st.number_input("Quota Under del Bookmaker", value=1.85, step=0.05)

# Calcolo Poisson per trovare il valore
k = int(np.floor(linea))
prob_under = poisson.cdf(k, lambda_ref)
prob_over = 1 - prob_under

quota_reale_over = 1 / prob_over if prob_over > 0 else 999
quota_reale_under = 1 / prob_under if prob_under > 0 else 999

ev_over = (prob_over * quota_over) - 1
ev_under = (prob_under * quota_under) - 1

st.markdown("<br>", unsafe_allow_html=True)
res_col1, res_col2 = st.columns(2)

with res_col1:
    st.markdown(f"**Probabilità Stimata Over {linea}:** `{prob_over*100:.1f}%` (Quota Reale: **{quota_reale_over:.2f}**)")
    if ev_over > 0:
        st.markdown(f"""
            <div class="value-box-success">
                <h4 style="color: #10b981; margin:0;">🔥 VALUE BET TROVATA (OVER)!</h4>
                <p style="margin: 4px 0 0 0;">EV+: <b>+{ev_over*100:.2f}%</b><br>Quota bookmaker ({quota_over}) > Quota Reale ({quota_reale_over:.2f})</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.info(f"Nessun valore sull'OVER per {linea}. EV: {ev_over*100:.2f}%")

with res_col2:
    st.markdown(f"**Probabilità Stimata Under {linea}:** `{prob_under*100:.1f}%` (Quota Reale: **{quota_reale_under:.2f}**)")
    if ev_under > 0:
        st.markdown(f"""
            <div class="value-box-success">
                <h4 style="color: #10b981; margin:0;">🔥 VALUE BET TROVATA (UNDER)!</h4>
                <p style="margin: 4px 0 0 0;">EV+: <b>+{ev_under*100:.2f}%</b><br>Quota bookmaker ({quota_under}) > Quota Reale ({quota_reale_under:.2f})</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.info(f"Nessun valore sull'UNDER per {linea}. EV: {ev_under*100:.2f}%")