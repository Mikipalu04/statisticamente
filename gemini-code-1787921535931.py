import streamlit as st
import numpy as np
from scipy.stats import poisson

# Configurazione della Pagina
st.set_page_config(page_title="STATISTICAMENTE - Ultimate Engine", page_icon="⚽", layout="wide")

# STILE CSS GLASSMORPHISM
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #0b0f19 0%, #111827 50%, #070a12 100%); color: #ffffff; }
    .brand-title { font-size: 46px; font-weight: 900; text-align: center; background: linear-gradient(90deg, #3b82f6, #60a5fa, #93c5fd); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0px; }
    .brand-subtitle { text-align: center; color: #9ca3af; font-size: 14px; margin-bottom: 20px; }
    .match-card { background: rgba(31, 41, 55, 0.6); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 16px; padding: 20px; margin-bottom: 20px; }
    .team-title { font-size: 22px; font-weight: 800; text-align: center; }
    .metric-container { background: rgba(17, 24, 39, 0.8); border-radius: 12px; padding: 14px; border-left: 4px solid #3b82f6; text-align: center; margin-bottom: 10px; }
    .metric-value { font-size: 24px; font-weight: 700; color: #60a5fa; }
    .metric-label { font-size: 11px; color: #9ca3af; text-transform: uppercase; }
    .value-box-success { background: rgba(16, 185, 129, 0.15); border: 1px solid #10b981; border-radius: 12px; padding: 16px; }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# DATABASE COMPLETO SERIE A (MEDIE & FACTOR RATINGS)
# ---------------------------------------------------------
AVG_HOME_SHOTS, AVG_AWAY_SHOTS = 13.2, 11.0
AVG_HOME_XG, AVG_AWAY_XG = 1.45, 1.15
AVG_HOME_CORNERS, AVG_AWAY_CORNERS = 5.4, 4.2
AVG_HOME_FOULS, AVG_AWAY_FOULS = 12.3, 12.8

TEAMS_DB = {
    'AC Milan': {'logo': 'https://ssl.gstatic.com/onebox/media/sports/logos/optimized/0E1JciuKLW0EbG48I5cFRQ_500x500.png', 'att': 1.25, 'def': 0.80, 'prec': 0.36, 'xg_att': 1.28, 'xg_def': 0.82, 'corner_att': 1.22, 'corner_def': 0.78, 'aggro': 0.92, 'cards': 1.8},
    'Venezia': {'logo': 'https://ssl.gstatic.com/onebox/media/sports/logos/optimized/3T56D6KGTM2XwaJpDVjIHw_500x500.png', 'att': 0.72, 'def': 1.32, 'prec': 0.28, 'xg_att': 0.70, 'xg_def': 1.35, 'corner_att': 0.68, 'corner_def': 1.28, 'aggro': 1.22, 'cards': 2.6},
    'Inter': {'logo': 'https://ssl.gstatic.com/onebox/media/sports/logos/optimized/l2-icwsMhIvsbRw8AwC1yg_500x500.png', 'att': 1.35, 'def': 0.68, 'prec': 0.38, 'xg_att': 1.38, 'xg_def': 0.70, 'corner_att': 1.30, 'corner_def': 0.70, 'aggro': 0.85, 'cards': 1.5},
    'Cagliari': {'logo': 'https://ssl.gstatic.com/onebox/media/sports/logos/optimized/e9XfySyGdfyJ4UzEkYwENw_500x500.png', 'att': 0.82, 'def': 1.18, 'prec': 0.30, 'xg_att': 0.80, 'xg_def': 1.20, 'corner_att': 0.82, 'corner_def': 1.15, 'aggro': 1.18, 'cards': 2.4},
    'Fiorentina': {'logo': 'https://ssl.gstatic.com/onebox/media/sports/logos/optimized/h-HS2cEVCwMJZFSlwYeWmA_500x500.png', 'att': 1.10, 'def': 0.92, 'prec': 0.33, 'xg_att': 1.12, 'xg_def': 0.90, 'corner_att': 1.15, 'corner_def': 0.88, 'aggro': 1.02, 'cards': 2.1},
    'Frosinone': {'logo': 'https://ssl.gstatic.com/onebox/media/sports/logos/optimized/_J6w-PL2RjW-fRR-D7Dl-w_500x500.png', 'att': 0.75, 'def': 1.28, 'prec': 0.28, 'xg_att': 0.76, 'xg_def': 1.30, 'corner_att': 0.72, 'corner_def': 1.25, 'aggro': 1.20, 'cards': 2.5},
    'Monza': {'logo': 'https://ssl.gstatic.com/onebox/media/sports/logos/optimized/g2S0HUWrWZX9hwKC87W11Q_500x500.png', 'att': 0.86, 'def': 1.08, 'prec': 0.30, 'xg_att': 0.84, 'xg_def': 1.10, 'corner_att': 0.85, 'corner_def': 1.08, 'aggro': 1.00, 'cards': 2.1},
    'Udinese': {'logo': 'https://ssl.gstatic.com/onebox/media/sports/logos/optimized/92Aw_iasBENKmzvdpbTpHQ_500x500.png', 'att': 0.90, 'def': 1.02, 'prec': 0.31, 'xg_att': 0.88, 'xg_def': 1.05, 'corner_att': 0.88, 'corner_def': 1.02, 'aggro': 1.12, 'cards': 2.3},
    'Sassuolo': {'logo': 'https://ssl.gstatic.com/onebox/media/sports/logos/optimized/GoeTFIVAZLA5JWk0-A6B0A_500x500.png', 'att': 0.95, 'def': 1.15, 'prec': 0.32, 'xg_att': 0.96, 'xg_def': 1.18, 'corner_att': 0.92, 'corner_def': 1.12, 'aggro': 0.98, 'cards': 2.0},
    'Torino': {'logo': 'https://ssl.gstatic.com/onebox/media/sports/logos/optimized/ovE3HSEx4GWXkW8GU7KVhA_500x500.png', 'att': 0.92, 'def': 0.90, 'prec': 0.31, 'xg_att': 0.90, 'xg_def': 0.88, 'corner_att': 0.90, 'corner_def': 0.92, 'aggro': 1.15, 'cards': 2.4},
    'Juventus': {'logo': 'https://ssl.gstatic.com/onebox/media/sports/logos/optimized/6lal-0xwWtos5HI99HRvuQ_500x500.png', 'att': 1.15, 'def': 0.72, 'prec': 0.35, 'xg_att': 1.18, 'xg_def': 0.75, 'corner_att': 1.10, 'corner_def': 0.78, 'aggro': 1.05, 'cards': 2.2},
    'Parma': {'logo': 'https://ssl.gstatic.com/onebox/media/sports/logos/optimized/Pr7ZXZlx34eEXdUMTkLvkw_500x500.png', 'att': 0.84, 'def': 1.15, 'prec': 0.30, 'xg_att': 0.82, 'xg_def': 1.16, 'corner_att': 0.80, 'corner_def': 1.12, 'aggro': 1.10, 'cards': 2.3},
    'Napoli': {'logo': 'https://ssl.gstatic.com/onebox/media/sports/logos/optimized/ueX_32AIja-hLmJSHpUuFg_500x500.png', 'att': 1.22, 'def': 0.75, 'prec': 0.35, 'xg_att': 1.25, 'xg_def': 0.78, 'corner_att': 1.25, 'corner_def': 0.74, 'aggro': 0.88, 'cards': 1.7},
    'Como': {'logo': 'https://ssl.gstatic.com/onebox/media/sports/logos/optimized/6InMYSIcwGvDV1SD3-cPGA_500x500.png', 'att': 0.85, 'def': 1.10, 'prec': 0.29, 'xg_att': 0.84, 'xg_def': 1.12, 'corner_att': 0.82, 'corner_def': 1.10, 'aggro': 1.08, 'cards': 2.2},
    'Lazio': {'logo': 'https://ssl.gstatic.com/onebox/media/sports/logos/optimized/VCmS5WyitnqY3ECAr0UYGw_500x500.png', 'att': 1.05, 'def': 0.95, 'prec': 0.33, 'xg_att': 1.06, 'xg_def': 0.94, 'corner_att': 1.02, 'corner_def': 0.92, 'aggro': 1.06, 'cards': 2.3},
    'Genoa': {'logo': 'https://ssl.gstatic.com/onebox/media/sports/logos/optimized/85QkdgIOpAt-_EuQ9mKTPg_500x500.png', 'att': 0.88, 'def': 1.05, 'prec': 0.30, 'xg_att': 0.86, 'xg_def': 1.02, 'corner_att': 0.82, 'corner_def': 1.05, 'aggro': 1.16, 'cards': 2.5},
    'Lecce': {'logo': 'https://ssl.gstatic.com/onebox/media/sports/logos/optimized/tIaC5FB7Gm8CIULc77qMjg_500x500.png', 'att': 0.85, 'def': 1.12, 'prec': 0.29, 'xg_att': 0.82, 'xg_def': 1.15, 'corner_att': 0.84, 'corner_def': 1.14, 'aggro': 1.14, 'cards': 2.4},
    'AS Roma': {'logo': 'https://ssl.gstatic.com/onebox/media/sports/logos/optimized/BQdP4jUBFJfG7U_JBsFIMg_500x500.png', 'att': 1.12, 'def': 0.88, 'prec': 0.34, 'xg_att': 1.15, 'xg_def': 0.86, 'corner_att': 1.12, 'corner_def': 0.85, 'aggro': 1.08, 'cards': 2.2},
    'Atalanta': {'logo': 'https://ssl.gstatic.com/onebox/media/sports/logos/aRlyKnUTdE3GoCZaofdwvg_500x500.png', 'att': 1.28, 'def': 0.85, 'prec': 0.36, 'xg_att': 1.32, 'xg_def': 0.86, 'corner_att': 1.26, 'corner_def': 0.80, 'aggro': 1.14, 'cards': 2.1},
    'Bologna': {'logo': 'https://ssl.gstatic.com/onebox/media/sports/logos/optimized/WnKdNmw06v2lz7HjhqPRPw_500x500.png', 'att': 1.02, 'def': 0.85, 'prec': 0.32, 'xg_att': 1.04, 'xg_def': 0.84, 'corner_att': 1.05, 'corner_def': 0.86, 'aggro': 1.04, 'cards': 2.0}
}

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

# INTERFACCIA WEB
st.markdown("<h1 class='brand-title'>STATISTICAMENTE</h1>", unsafe_allow_html=True)
st.markdown("<p class='brand-subtitle'>Engine Predittivo Omnicomprensivo • xG, Tiri, Corner, Falli & Cartellini</p>", unsafe_allow_html=True)

partite_labels = [f"🏟️ {m['casa']} vs {m['trasferta']} ({m['orario']})" for m in GIORNATA_2]
partita_scelta_idx = st.selectbox("Seleziona la Partita:", range(len(partite_labels)), format_func=lambda x: partite_labels[x])

match = GIORNATA_2[partita_scelta_idx]
team_c = TEAMS_DB[match['casa']].copy()
team_t = TEAMS_DB[match['trasferta']].copy()

# Card Partita
st.markdown('<div class="match-card">', unsafe_allow_html=True)
c_home, c_vs, c_away = st.columns([2, 1, 2])
with c_home:
    st.image(team_c['logo'], width=80)
    st.markdown(f'<div class="team-title">{match["casa"]}</div>', unsafe_allow_html=True)
with c_vs:
    st.markdown("<br><h3 style='text-align:center; color:#ef4444;'>VS</h3>", unsafe_allow_html=True)
    st.markdown(f'<p style="text-align:center; color:#9ca3af; font-size:12px;">{match["orario"]}</p>', unsafe_allow_html=True)
with c_away:
    st.image(team_t['logo'], width=80)
    st.markdown(f'<div class="team-title">{match["trasferta"]}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# SIDEBAR PARAMETRI DIVERSIFICATI
st.sidebar.header("⚙️ Variabili Match & Arbitro")
meteo = st.sidebar.selectbox("Condizioni Meteo:", ["Normale/Asciutto", "Pioggia / Campo Bagnato"])
severita_arbitro = st.sidebar.slider("Severità Arbitro (Cartellini %)", 80, 120, 100, step=5)
assenza_casa = st.sidebar.slider(f"Infortuni {match['casa']} (%)", 0, 30, 0, step=5)
assenza_trasferta = st.sidebar.slider(f"Infortuni {match['trasferta']} (%)", 0, 30, 0, step=5)

# CORREZIONI APPLICATE
att_c = team_c['att'] * (1 - (assenza_casa / 100))
att_t = team_t['att'] * (1 - (assenza_trasferta / 100))

# 1. TIRI
tiri_casa = AVG_HOME_SHOTS * att_c * team_t['def']
tiri_trasferta = AVG_AWAY_SHOTS * att_t * team_c['def']
if meteo == "Pioggia / Campo Bagnato":
    tiri_casa *= 1.05
    tiri_trasferta *= 1.05

tiri_totali = tiri_casa + tiri_trasferta
porta_casa = tiri_casa * team_c['prec']
porta_trasferta = tiri_trasferta * team_t['prec']
porta_totali = porta_casa + porta_trasferta

# 2. EXPECTED GOALS (xG) & GOL ATTESI
xg_casa = AVG_HOME_XG * team_c['xg_att'] * team_t['xg_def'] * (1 - (assenza_casa / 100))
xg_trasferta = AVG_AWAY_XG * team_t['xg_att'] * team_c['xg_def'] * (1 - (assenza_trasferta / 100))
xg_totali = xg_casa + xg_trasferta

# 3. CALCI D'ANGOLO
corner_casa = AVG_HOME_CORNERS * team_c['corner_att'] * team_t['corner_def']
corner_trasferta = AVG_AWAY_CORNERS * team_t['corner_att'] * team_c['corner_def']
corner_totali = corner_casa + corner_trasferta

# 4. FALLI E CARTELLINI
gap_tecnico = abs(att_c - att_t)
falli_casa = AVG_HOME_FOULS * team_c['aggro'] * (1 + (gap_tecnico * 0.1))
falli_trasferta = AVG_AWAY_FOULS * team_t['aggro'] * (1 + (gap_tecnico * 0.1))
falli_totali = falli_casa + falli_trasferta

cartellini_totali = (team_c['cards'] + team_t['cards']) * (severita_arbitro / 100) * (1 + (gap_tecnico * 0.15))

# DISPLAY RISULTATI AVANZATI
st.markdown("### 📊 Previsioni Statistiche Complete Match")

col_m1, col_m2, col_m3, col_m4 = st.columns(4)
with col_m1:
    st.markdown(f'<div class="metric-container"><div class="metric-value">{xg_totali:.2f}</div><div class="metric-label">Expected Goals (xG) Totali</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-container"><div class="metric-value">{tiri_totali:.1f}</div><div class="metric-label">Tiri Totali Match</div></div>', unsafe_allow_html=True)
with col_m2:
    st.markdown(f'<div class="metric-container"><div class="metric-value">{xg_casa:.2f} - {xg_trasferta:.2f}</div><div class="metric-label">xG Casa vs Trasferta</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-container"><div class="metric-value">{porta_totali:.1f}</div><div class="metric-label">Tiri nello Specchio</div></div>', unsafe_allow_html=True)
with col_m3:
    st.markdown(f'<div class="metric-container"><div class="metric-value">{corner_totali:.1f}</div><div class="metric-label">Calci d\'Angolo Totali</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-container"><div class="metric-value">{corner_casa:.1f} / {corner_trasferta:.1f}</div><div class="metric-label">Corner Casa / Trasferta</div></div>', unsafe_allow_html=True)
with col_m4:
    st.markdown(f'<div class="metric-container"><div class="metric-value">{falli_totali:.1f}</div><div class="metric-label">Falli Totali Attesi</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-container"><div class="metric-value">{cartellini_totali:.1f}</div><div class="metric-label">Cartellini Attesi</div></div>', unsafe_allow_html=True)

st.markdown("---")

# ENGINE VALUE BETTING MULTI-MERCATO
st.markdown("### 💰 Value Bet Finder (Distribuzione Stocastica Poisson)")

mercati_dict = {
    "Tiri Totali Match": tiri_totali,
    "Tiri in Porta Totali": porta_totali,
    "Expected Goals Totali": xg_totali,
    "Calci d'Angolo Totali": corner_totali,
    "Falli Totali Match": falli_totali,
    "Cartellini Totali": cartellini_totali
}

c_left, c_right = st.columns(2)
with c_left:
    mercato_sel = st.selectbox("Seleziona Mercato per Analisi EV:", list(mercati_dict.keys()))
    lambda_val = mercati_dict[mercato_sel]
    linea = st.number_input(f"Linea Bookmaker per {mercato_sel}", value=float(round(lambda_val * 2) / 2), step=0.5)

with c_right:
    quota_over = st.number_input("Quota Over Bookmaker", value=1.85, step=0.05)

k = int(np.floor(linea))
prob_under = poisson.cdf(k, lambda_val)
prob_over = 1 - prob_under
quota_reale_over = 1 / prob_over if prob_over > 0 else 999
ev_over = (prob_over * quota_over) - 1

st.markdown("<br>", unsafe_allow_html=True)
if ev_over > 0:
    st.markdown(f"""
        <div class="value-box-success">
            <h4 style="color: #10b981; margin:0;">🔥 VALUE BET INDIVIDUATA SU {mercato_sel.upper()} (OVER {linea})!</h4>
            <p style="margin: 4px 0 0 0;">Stima Algoritmo: <b>{lambda_val:.2f}</b> | Probabilità Over: <b>{prob_over*100:.1f}%</b> | Quota Reale: <b>{quota_reale_over:.2f}</b> | EV: <b>+{ev_over*100:.1f}%</b></p>
        </div>
    """, unsafe_allow_html=True)
else:
    st.info(f"Nessun valore identificato sull'OVER {linea} per {mercato_sel}. Probabilità: {prob_over*100:.1f}% (Quota minima sostenibile: {quota_reale_over:.2f})")