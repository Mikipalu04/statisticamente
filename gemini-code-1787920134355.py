import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson

# Configurazione della Pagina
st.set_page_config(
    page_title="STATISTICAMENTE - Serie A Predictive Dashboard",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# STILE CSS PERSONALIZZATO (UX Moderna, Glassmorphism & Background)
# ---------------------------------------------------------
st.markdown("""
    <style>
    /* Background del sito con pattern e sfumatura dark moderna */
    .stApp {
        background: linear-gradient(135deg, #0b0f19 0%, #111827 50%, #070a12 100%);
        color: #ffffff;
    }
    
    /* Intestazione Brand */
    .brand-title {
        font-size: 46px;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(90deg, #3b82f6, #60a5fa, #93c5fd);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: 2px;
        margin-bottom: 0px;
    }
    .brand-subtitle {
        text-align: center;
        color: #9ca3af;
        font-size: 16px;
        margin-bottom: 25px;
    }

    /* Card Partita Glassmorphism */
    .match-card {
        background: rgba(31, 41, 55, 0.6);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 25px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }
    .team-title {
        font-size: 22px;
        font-weight: 800;
        text-align: center;
        color: #ffffff;
    }
    .vs-text {
        font-size: 22px;
        font-weight: 900;
        color: #ef4444;
        text-align: center;
    }
    
    /* Visualizzatori Metriche */
    .metric-container {
        background: rgba(17, 24, 39, 0.8);
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

    /* Value Bet Highlight Box */
    .value-box-success {
        background: rgba(16, 185, 129, 0.15);
        border: 1px solid #10b981;
        border-radius: 12px;
        padding: 18px;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# DATABASE SERIE A: METRICHE REALISTICHE DIFFERENZIATE & LOGHI
# ---------------------------------------------------------
TEAMS_DB = {
    'AC Milan': {
        'logo': 'https://ssl.gstatic.com/onebox/media/sports/logos/optimized/0E1JciuKLW0EbG48I5cFRQ_500x500.png',
        'tiri_fatti': 16.2, 'tiri_concessi': 9.8, 'porta_fatti': 5.8, 'porta_concessi': 3.2,
        'corner_fatti': 6.2, 'corner_concessi': 3.6, 'falli_fatti': 11.2, 'falli_subiti': 12.8, 'cartellini': 1.8
    },
    'Venezia': {
        'logo': 'https://ssl.gstatic.com/onebox/media/sports/logos/optimized/3T56D6KGTM2XwaJpDVjIHw_500x500.png',
        'tiri_fatti': 9.4, 'tiri_concessi': 16.8, 'porta_fatti': 2.9, 'porta_concessi': 5.9,
        'corner_fatti': 3.2, 'corner_concessi': 6.5, 'falli_fatti': 14.2, 'falli_subiti': 10.1, 'cartellini': 2.5
    },
    'Inter': {
        'logo': 'https://ssl.gstatic.com/onebox/media/sports/logos/optimized/l2-icwsMhIvsbRw8AwC1yg_500x500.png',
        'tiri_fatti': 17.5, 'tiri_concessi': 8.2, 'porta_fatti': 6.4, 'porta_concessi': 2.5,
        'corner_fatti': 6.8, 'corner_concessi': 3.1, 'falli_fatti': 10.5, 'falli_subiti': 12.2, 'cartellini': 1.5
    },
    'Cagliari': {
        'logo': 'https://ssl.gstatic.com/onebox/media/sports/logos/optimized/e9XfySyGdfyJ4UzEkYwENw_500x500.png',
        'tiri_fatti': 10.8, 'tiri_concessi': 14.9, 'porta_fatti': 3.4, 'porta_concessi': 4.8,
        'corner_fatti': 4.2, 'corner_concessi': 5.8, 'falli_fatti': 13.5, 'falli_subiti': 11.0, 'cartellini': 2.3
    },
    'Fiorentina': {
        'logo': 'https://ssl.gstatic.com/onebox/media/sports/logos/optimized/h-HS2cEVCwMJZFSlwYeWmA_500x500.png',
        'tiri_fatti': 14.8, 'tiri_concessi': 11.1, 'porta_fatti': 4.9, 'porta_concessi': 3.6,
        'corner_fatti': 5.6, 'corner_concessi': 4.2, 'falli_fatti': 12.1, 'falli_subiti': 12.5, 'cartellini': 2.0
    },
    'Frosinone': {
        'logo': 'https://ssl.gstatic.com/onebox/media/sports/logos/optimized/_J6w-PL2RjW-fRR-D7Dl-w_500x500.png',
        'tiri_fatti': 10.2, 'tiri_concessi': 15.6, 'porta_fatti': 3.2, 'porta_concessi': 5.2,
        'corner_fatti': 3.8, 'corner_concessi': 6.0, 'falli_fatti': 13.8, 'falli_subiti': 10.8, 'cartellini': 2.4
    },
    'Juventus': {
        'logo': 'https://ssl.gstatic.com/onebox/media/sports/logos/optimized/6lal-0xwWtos5HI99HRvuQ_500x500.png',
        'tiri_fatti': 15.1, 'tiri_concessi': 8.9, 'porta_fatti': 5.2, 'porta_concessi': 2.8,
        'corner_fatti': 5.5, 'corner_concessi': 3.7, 'falli_fatti': 12.2, 'falli_subiti': 12.0, 'cartellini': 2.1
    },
    'Parma': {
        'logo': 'https://ssl.gstatic.com/onebox/media/sports/logos/optimized/Pr7ZXZlx34eEXdUMTkLvkw_500x500.png',
        'tiri_fatti': 11.2, 'tiri_concessi': 14.2, 'porta_fatti': 3.6, 'porta_concessi': 4.6,
        'corner_fatti': 4.0, 'corner_concessi': 5.3, 'falli_fatti': 12.8, 'falli_subiti': 11.2, 'cartellini': 2.2
    },
    'Napoli': {
        'logo': 'https://ssl.gstatic.com/onebox/media/sports/logos/optimized/ueX_32AIja-hLmJSHpUuFg_500x500.png',
        'tiri_fatti': 16.5, 'tiri_concessi': 9.0, 'porta_fatti': 5.6, 'porta_concessi': 2.9,
        'corner_fatti': 6.4, 'corner_concessi': 3.2, 'falli_fatti': 10.9, 'falli_subiti': 13.2, 'cartellini': 1.6
    },
    'Como': {
        'logo': 'https://ssl.gstatic.com/onebox/media/sports/logos/optimized/6InMYSIcwGvDV1SD3-cPGA_500x500.png',
        'tiri_fatti': 11.5, 'tiri_concessi': 13.8, 'porta_fatti': 3.7, 'porta_concessi': 4.4,
        'corner_fatti': 4.4, 'corner_concessi': 5.1, 'falli_fatti': 12.5, 'falli_subiti': 11.5, 'cartellini': 2.1
    },
    'Lazio': {
        'logo': 'https://ssl.gstatic.com/onebox/media/sports/logos/optimized/VCmS5WyitnqY3ECAr0UYGw_500x500.png',
        'tiri_fatti': 13.9, 'tiri_concessi': 10.8, 'porta_fatti': 4.6, 'porta_concessi': 3.5,
        'corner_fatti': 5.1, 'corner_concessi': 4.2, 'falli_fatti': 12.0, 'falli_subiti': 12.1, 'cartellini': 2.2
    },
    'Genoa': {
        'logo': 'https://ssl.gstatic.com/onebox/media/sports/logos/optimized/85QkdgIOpAt-_EuQ9mKTPg_500x500.png',
        'tiri_fatti': 10.5, 'tiri_concessi': 13.2, 'porta_fatti': 3.3, 'porta_concessi': 4.1,
        'corner_fatti': 3.9, 'corner_concessi': 5.2, 'falli_fatti': 13.6, 'falli_subiti': 11.4, 'cartellini': 2.4
    },
    'Lecce': {
        'logo': 'https://ssl.gstatic.com/onebox/media/sports/logos/optimized/tIaC5FB7Gm8CIULc77qMjg_500x500.png',
        'tiri_fatti': 11.8, 'tiri_concessi': 14.5, 'porta_fatti': 3.7, 'porta_concessi': 4.7,
        'corner_fatti': 4.3, 'corner_concessi': 5.5, 'falli_fatti': 13.2, 'falli_subiti': 10.9, 'cartellini': 2.3
    },
    'AS Roma': {
        'logo': 'https://ssl.gstatic.com/onebox/media/sports/logos/optimized/BQdP4jUBFJfG7U_JBsFIMg_500x500.png',
        'tiri_fatti': 15.0, 'tiri_concessi': 10.6, 'porta_fatti': 5.1, 'porta_concessi': 3.4,
        'corner_fatti': 5.7, 'corner_concessi': 4.1, 'falli_fatti': 12.6, 'falli_subiti': 12.9, 'cartellini': 2.2
    },
    'Atalanta': {
        'logo': 'https://ssl.gstatic.com/onebox/media/sports/logos/aRlyKnUTdE3GoCZaofdwvg_500x500.png',
        'tiri_fatti': 16.4, 'tiri_concessi': 10.1, 'porta_fatti': 5.9, 'porta_concessi': 3.3,
        'corner_fatti': 6.1, 'corner_concessi': 3.8, 'falli_fatti': 13.8, 'falli_subiti': 12.0, 'cartellini': 2.1
    },
    'Bologna': {
        'logo': 'https://ssl.gstatic.com/onebox/media/sports/logos/optimized/WnKdNmw06v2lz7HjhqPRPw_500x500.png',
        'tiri_fatti': 13.2, 'tiri_concessi': 10.2, 'porta_fatti': 4.3, 'porta_concessi': 3.2,
        'corner_fatti': 5.0, 'corner_concessi': 3.9, 'falli_fatti': 12.4, 'falli_subiti': 11.8, 'cartellini': 2.0
    },
    'Monza': {
        'logo': 'https://ssl.gstatic.com/onebox/media/sports/logos/optimized/g2S0HUWrWZX9hwKC87W11Q_500x500.png',
        'tiri_fatti': 10.9, 'tiri_concessi': 14.6, 'porta_fatti': 3.4, 'porta_concessi': 4.7,
        'corner_fatti': 4.1, 'corner_concessi': 5.4, 'falli_fatti': 12.1, 'falli_subiti': 11.2, 'cartellini': 2.1
    },
    'Udinese': {
        'logo': 'https://ssl.gstatic.com/onebox/media/sports/logos/optimized/92Aw_iasBENKmzvdpbTpHQ_500x500.png',
        'tiri_fatti': 11.4, 'tiri_concessi': 13.5, 'porta_fatti': 3.6, 'porta_concessi': 4.3,
        'corner_fatti': 4.3, 'corner_concessi': 5.0, 'falli_fatti': 13.0, 'falli_subiti': 11.7, 'cartellini': 2.2
    },
    'Sassuolo': {
        'logo': 'https://ssl.gstatic.com/onebox/media/sports/logos/optimized/GoeTFIVAZLA5JWk0-A6B0A_500x500.png',
        'tiri_fatti': 12.4, 'tiri_concessi': 14.0, 'porta_fatti': 4.0, 'porta_concessi': 4.5,
        'corner_fatti': 4.6, 'corner_concessi': 5.2, 'falli_fatti': 11.8, 'falli_subiti': 11.0, 'cartellini': 1.9
    },
    'Torino': {
        'logo': 'https://ssl.gstatic.com/onebox/media/sports/logos/optimized/ovE3HSEx4GWXkW8GU7KVhA_500x500.png',
        'tiri_fatti': 11.6, 'tiri_concessi': 11.9, 'porta_fatti': 3.8, 'porta_concessi': 3.7,
        'corner_fatti': 4.4, 'corner_concessi': 4.5, 'falli_fatti': 13.4, 'falli_subiti': 11.6, 'cartellini': 2.3
    }
}

# ---------------------------------------------------------
# CALENDARIO UFFICIALE: 2ª GIORNATA SERIE A 2026/2027
# ---------------------------------------------------------
GIORNATA_2 = [
    {"casa": "AC Milan", "trasferta": "Venezia", "orario": "Venerdì, 20:45"},
    {"casa": "Fiorentina", "trasferta": "Frosinone", "orario": "Sabato, 18:30"},
    {"casa": "Monza", "trasferta": "Udinese", "orario": "Sabato, 18:30"},
    {"casa": "Sassuolo", "trasferta": "Torino", "orario": "Sabato, 18:30"},
    {"casa": "Juventus", "trasferta": "Parma", "orario": "Sabato, 20:45"},
    {"casa": "Napoli", "trasferta": "Como", "orario": "Domenica, 18:30"},
    {"casa": "Cagliari", "trasferta": "Inter", "orario": "Domenica, 20:45"},
    {"casa": "Lazio", "trasferta": "Genoa", "orario": "Domenica, 20:45"},
    {"casa": "Lecce", "trasferta": "AS Roma", "orario": "Lunedì, 18:30"},
    {"casa": "Atalanta", "trasferta": "Bologna", "orario": "Lunedì, 20:45"}
]

# ---------------------------------------------------------
# INTERFACCIA WEB & BRANDING "STATISTICAMENTE"
# ---------------------------------------------------------
st.markdown("<h1 class='brand-title'>STATISTICAMENTE</h1>", unsafe_allow_html=True)
st.markdown("<p class='brand-subtitle'>Serie A Predictive Analytics • <b>2ª Giornata di Campionato</b></p>", unsafe_allow_html=True)

partite_labels = [f"🏟️ {m['casa']} vs {m['trasferta']} ({m['orario']})" for m in GIORNATA_2]
partita_scelta_idx = st.selectbox("Seleziona il Match da Analizzare:", range(len(partite_labels)), format_func=lambda x: partite_labels[x])

match = GIORNATA_2[partita_scelta_idx]
team_c = TEAMS_DB[match['casa']]
team_t = TEAMS_DB[match['trasferta']]

# ---------------------------------------------------------
# MATCH CARD CON LOGHI OFFICIAL GOOGLE SPORTS
# ---------------------------------------------------------
st.markdown('<div class="match-card">', unsafe_allow_html=True)
c_home, c_vs, c_away = st.columns([2, 1, 2])

with c_home:
    st.image(team_c['logo'], width=90)
    st.markdown(f'<div class="team-title">{match["casa"]}</div>', unsafe_allow_html=True)

with c_vs:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="vs-text">VS</div>', unsafe_allow_html=True)
    st.markdown(f'<p style="text-align:center; color:#9ca3af; font-size:13px;">{match["orario"]}</p>', unsafe_allow_html=True)

with c_away:
    st.image(team_t['logo'], width=90)
    st.markdown(f'<div class="team-title">{match["trasferta"]}</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# CALCOLO METRICHE INCROCIATE (ATTESE DEL MATCH)
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
st.markdown("### 📊 Previsioni Statistiche Match")

t1, t2, t3, t4 = st.columns(4)
with t1:
    st.markdown(f'<div class="metric-container"><div class="metric-value">{tiri_totali:.1f}</div><div class="metric-label">Tiri Totali Match</div></div>', unsafe_allow_html=True)
with t2:
    st.markdown(f'<div class="metric-container"><div class="metric-value">{porta_totali:.1f}</div><div class="metric-label">Tiri in Porta Totali</div></div>', unsafe_allow_html=True)
with t3:
    st.markdown(f'<div class="metric-container"><div class="metric-value">{corner_totali:.1f}</div><div class="metric-label">Calci d\'Angolo</div></div>', unsafe_allow_html=True)
with t4:
    st.markdown(f'<div class="metric-container"><div class="metric-value">{falli_totali:.1f} / {cartellini_totali:.1f}</div><div class="metric-label">Falli / Cartellini</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown(f"#### 🔍 Dettaglio Squadre: **{match['casa']}** vs **{match['trasferta']}**")

d1, d2, d3 = st.columns(3)
with d1:
    st.markdown(f"**⚽ Tiri Totali (In Porta):**")
    st.write(f"• {match['casa']}: **{tiri_casa:.1f}** tiri ({porta_casa:.1f} in porta)")
    st.write(f"• {match['trasferta']}: **{tiri_trasferta:.1f}** tiri ({porta_trasferta:.1f} in porta)")

with d2:
    st.markdown(f"**🚩 Calci d'Angolo Attesi:**")
    st.write(f"• {match['casa']}: **{corner_casa:.1f}** corner")
    st.write(f"• {match['trasferta']}: **{corner_trasferta:.1f}** corner")

with d3:
    st.markdown(f"**🟨 Aggressività & Falli:**")
    st.write(f"• {match['casa']}: **{falli_casa:.1f}** falli commessi")
    st.write(f"• {match['trasferta']}: **{falli_trasferta:.1f}** falli commessi")

st.markdown("---")

# ---------------------------------------------------------
# ENGINE VALUE BETTING (STIMA PROBABILITÀ POISSON)
# ---------------------------------------------------------
st.markdown("### 💰 Valutazione Value Bet (Quote vs Stime Realistiche)")

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
    quota_over = st.number_input("Quota Over Bookmaker", value=1.85, step=0.05)
    quota_under = st.number_input("Quota Under Bookmaker", value=1.85, step=0.05)

# Algoritmo Poisson
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
                <h4 style="color: #10b981; margin:0;">🔥 VALUE BET DETECTED (OVER)!</h4>
                <p style="margin: 4px 0 0 0;">Valore Atteso (EV): <b>+{ev_over*100:.2f}%</b><br>La quota del bookmaker ({quota_over}) è più alta del valore reale ({quota_reale_over:.2f}).</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.info(f"Nessun valore sull'OVER per la linea {linea}. EV: {ev_over*100:.2f}%")

with res_col2:
    st.markdown(f"**Probabilità Stimata Under {linea}:** `{prob_under*100:.1f}%` (Quota Reale: **{quota_reale_under:.2f}**)")
    if ev_under > 0:
        st.markdown(f"""
            <div class="value-box-success">
                <h4 style="color: #10b981; margin:0;">🔥 VALUE BET DETECTED (UNDER)!</h4>
                <p style="margin: 4px 0 0 0;">Valore Atteso (EV): <b>+{ev_under*100:.2f}%</b><br>La quota del bookmaker ({quota_under}) è più alta del valore reale ({quota_reale_under:.2f}).</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.info(f"Nessun valore sull'UNDER per la linea {linea}. EV: {ev_under*100:.2f}%")