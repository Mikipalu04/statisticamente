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
    .metric-container { background: rgba(17, 24, 39, 0.8); border-radius: 12px; padding: 14px; border-left: 4px solid #3b82f6; text-align: center; }
    .metric-value { font-size: 24px; font-weight: 700; color: #60a5fa; }
    .metric-label { font-size: 11px; color: #9ca3af; text-transform: uppercase; }
    .value-box-success { background: rgba(16, 185, 129, 0.15); border: 1px solid #10b981; border-radius: 12px; padding: 16px; }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# CONSTANTI BASE SERIE A
# ---------------------------------------------------------
AVG_HOME_SHOTS = 13.2
AVG_AWAY_SHOTS = 11.0

TEAMS_DB = {
    'AC Milan': {'logo': 'https://ssl.gstatic.com/onebox/media/sports/logos/optimized/0E1JciuKLW0EbG48I5cFRQ_500x500.png', 'att': 1.25, 'def': 0.80, 'prec': 0.36},
    'Venezia': {'logo': 'https://ssl.gstatic.com/onebox/media/sports/logos/optimized/3T56D6KGTM2XwaJpDVjIHw_500x500.png', 'att': 0.72, 'def': 1.32, 'prec': 0.28},
    'Inter': {'logo': 'https://ssl.gstatic.com/onebox/media/sports/logos/optimized/l2-icwsMhIvsbRw8AwC1yg_500x500.png', 'att': 1.35, 'def': 0.68, 'prec': 0.38},
    'Cagliari': {'logo': 'https://ssl.gstatic.com/onebox/media/sports/logos/optimized/e9XfySyGdfyJ4UzEkYwENw_500x500.png', 'att': 0.82, 'def': 1.18, 'prec': 0.30},
    'Fiorentina': {'logo': 'https://ssl.gstatic.com/onebox/media/sports/logos/optimized/h-HS2cEVCwMJZFSlwYeWmA_500x500.png', 'att': 1.10, 'def': 0.92, 'prec': 0.33},
    'Frosinone': {'logo': 'https://ssl.gstatic.com/onebox/media/sports/logos/optimized/_J6w-PL2RjW-fRR-D7Dl-w_500x500.png', 'att': 0.75, 'def': 1.28, 'prec': 0.28},
    'Monza': {'logo': 'https://ssl.gstatic.com/onebox/media/sports/logos/optimized/g2S0HUWrWZX9hwKC87W11Q_500x500.png', 'att': 0.86, 'def': 1.08, 'prec': 0.30},
    'Udinese': {'logo': 'https://ssl.gstatic.com/onebox/media/sports/logos/optimized/92Aw_iasBENKmzvdpbTpHQ_500x500.png', 'att': 0.90, 'def': 1.02, 'prec': 0.31},
    'Sassuolo': {'logo': 'https://ssl.gstatic.com/onebox/media/sports/logos/optimized/GoeTFIVAZLA5JWk0-A6B0A_500x500.png', 'att': 0.95, 'def': 1.15, 'prec': 0.32},
    'Torino': {'logo': 'https://ssl.gstatic.com/onebox/media/sports/logos/optimized/ovE3HSEx4GWXkW8GU7KVhA_500x500.png', 'att': 0.92, 'def': 0.90, 'prec': 0.31},
    'Juventus': {'logo': 'https://ssl.gstatic.com/onebox/media/sports/logos/optimized/6lal-0xwWtos5HI99HRvuQ_500x500.png', 'att': 1.15, 'def': 0.72, 'prec': 0.35},
    'Parma': {'logo': 'https://ssl.gstatic.com/onebox/media/sports/logos/optimized/Pr7ZXZlx34eEXdUMTkLvkw_500x500.png', 'att': 0.84, 'def': 1.15, 'prec': 0.30},
    'Napoli': {'logo': 'https://ssl.gstatic.com/onebox/media/sports/logos/optimized/ueX_32AIja-hLmJSHpUuFg_500x500.png', 'att': 1.22, 'def': 0.75, 'prec': 0.35},
    'Como': {'logo': 'https://ssl.gstatic.com/onebox/media/sports/logos/optimized/6InMYSIcwGvDV1SD3-cPGA_500x500.png', 'att': 0.85, 'def': 1.10, 'prec': 0.29},
    'Lazio': {'logo': 'https://ssl.gstatic.com/onebox/media/sports/logos/optimized/VCmS5WyitnqY3ECAr0UYGw_500x500.png', 'att': 1.05, 'def': 0.95, 'prec': 0.33},
    'Genoa': {'logo': 'https://ssl.gstatic.com/onebox/media/sports/logos/optimized/85QkdgIOpAt-_EuQ9mKTPg_500x500.png', 'att': 0.88, 'def': 1.05, 'prec': 0.30},
    'Lecce': {'logo': 'https://ssl.gstatic.com/onebox/media/sports/logos/optimized/tIaC5FB7Gm8CIULc77qMjg_500x500.png', 'att': 0.85, 'def': 1.12, 'prec': 0.29},
    'AS Roma': {'logo': 'https://ssl.gstatic.com/onebox/media/sports/logos/optimized/BQdP4jUBFJfG7U_JBsFIMg_500x500.png', 'att': 1.12, 'def': 0.88, 'prec': 0.34},
    'Atalanta': {'logo': 'https://ssl.gstatic.com/onebox/media/sports/logos/aRlyKnUTdE3GoCZaofdwvg_500x500.png', 'att': 1.28, 'def': 0.85, 'prec': 0.36},
    'Bologna': {'logo': 'https://ssl.gstatic.com/onebox/media/sports/logos/optimized/WnKdNmw06v2lz7HjhqPRPw_500x500.png', 'att': 1.02, 'def': 0.85, 'prec': 0.32}
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

# ---------------------------------------------------------
# INTERFACCIA WEB
# ---------------------------------------------------------
st.markdown("<h1 class='brand-title'>STATISTICAMENTE</h1>", unsafe_allow_html=True)
st.markdown("<p class='brand-subtitle'>Algoritmo Predittivo Avanzato • Game State & Weather Impact Integrated</p>", unsafe_allow_html=True)

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

# ---------------------------------------------------------
# PARAMETRI CONDIZIONALI AVANZATI (SIDEBAR E MODIFICATORI)
# ---------------------------------------------------------
st.sidebar.header("⚙️ Variabili Tattiche & Ambientali")

meteo = st.sidebar.selectbox("Condizioni Meteo/Campo:", ["Normale/Asciutto", "Pioggia / Campo Bagnato (+5% tiri)"])
assenza_casa = st.sidebar.slider(f"Infortuni Top Scorer {match['casa']} (%)", 0, 30, 0, step=5)
assenza_trasferta = st.sidebar.slider(f"Infortuni Top Scorer {match['trasferta']} (%)", 0, 30, 0, step=5)

# Applicazione Correttivi Infortuni
att_c_effective = team_c['att'] * (1 - (assenza_casa / 100))
att_t_effective = team_t['att'] * (1 - (assenza_trasferta / 100))

# ---------------------------------------------------------
# CALCOLO MATEMATICO AVANZATO
# ---------------------------------------------------------
# 1. Base Ponderata
tiri_casa_raw = AVG_HOME_SHOTS * att_c_effective * team_t['def']
tiri_trasferta_raw = AVG_AWAY_SHOTS * att_t_effective * team_c['def']

# 2. Game State Modifier (Aggiustamento inerzia match)
# Se c'è grande divario, la favorita abbassa l'intensità in vantaggio, la sfavorita calcia di più disperatamente
gap = att_c_effective - att_t_effective
game_state_factor_c = 1.0 - (gap * 0.04) if gap > 0.3 else 1.0
game_state_factor_t = 1.0 + (gap * 0.05) if gap > 0.3 else 1.0

tiri_casa = tiri_casa_raw * game_state_factor_c
tiri_trasferta = tiri_trasferta_raw * game_state_factor_t

# 3. Weather Modifier
if meteo == "Pioggia / Campo Bagnato (+5% tiri)":
    tiri_casa *= 1.05
    tiri_trasferta *= 1.05

tiri_totali = tiri_casa + tiri_trasferta
porta_casa = tiri_casa * team_c['prec']
porta_trasferta = tiri_trasferta * team_t['prec']
porta_totali = porta_casa + porta_trasferta

# ---------------------------------------------------------
# VISUALIZZAZIONE RISULTATI
# ---------------------------------------------------------
st.markdown("### 📊 Previsioni Ricalibrate (Stima Avanzata)")
t1, t2, t3, t4 = st.columns(4)
with t1:
    st.markdown(f'<div class="metric-container"><div class="metric-value">{tiri_totali:.1f}</div><div class="metric-label">Tiri Totali Attesi</div></div>', unsafe_allow_html=True)
with t2:
    st.markdown(f'<div class="metric-container"><div class="metric-value">{porta_totali:.1f}</div><div class="metric-label">Tiri in Porta Attesi</div></div>', unsafe_allow_html=True)
with t3:
    st.markdown(f'<div class="metric-container"><div class="metric-value">{tiri_casa:.1f}</div><div class="metric-label">Tiri {match["casa"]}</div></div>', unsafe_allow_html=True)
with t4:
    st.markdown(f'<div class="metric-container"><div class="metric-value">{tiri_trasferta:.1f}</div><div class="metric-label">Tiri {match["trasferta"]}</div></div>', unsafe_allow_html=True)

st.markdown("---")

# ---------------------------------------------------------
# ENGINE VALUE BETTING (POISSON)
# ---------------------------------------------------------
st.markdown("### 💰 Analisi Valore Quota Bookmaker")
c_left, c_right = st.columns(2)
with c_left:
    linea = st.number_input("Linea Tiri Bookmaker", value=float(int(tiri_totali)) + 0.5, step=0.5)
with c_right:
    quota_over = st.number_input("Quota Over Offerta", value=1.85, step=0.05)

k = int(np.floor(linea))
prob_under = poisson.cdf(k, tiri_totali)
prob_over = 1 - prob_under
quota_reale_over = 1 / prob_over if prob_over > 0 else 999
ev_over = (prob_over * quota_over) - 1

if ev_over > 0:
    st.markdown(f"""
        <div class="value-box-success">
            <h4 style="color: #10b981; margin:0;">🔥 VALUE BET INDIVIDUATA (OVER {linea})!</h4>
            <p style="margin: 4px 0 0 0;">Probabilità Algoritmo: <b>{prob_over*100:.1f}%</b> | Quota Reale Equa: <b>{quota_reale_over:.2f}</b> | Valore Atteso (EV): <b>+{ev_over*100:.1f}%</b></p>
        </div>
    """, unsafe_allow_html=True)
else:
    st.info(f"Nessun valore sull'OVER {linea}. Probabilità stimata: {prob_over*100:.1f}% (Quota minima consigliata: {quota_reale_over:.2f})")