import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson

st.set_page_config(page_title="Serie A Shot Value Finder", layout="wide")

st.title("⚽ Serie A - Value Bet Finder sui Tiri")
st.markdown("Analisi delle linee dei bookmaker su **Tiri Totali** e **Tiri in Porta** per giornata.")

# 1. Database di esempio (Sostituibile con API o scraping)
stats_squadre = {
    'Inter': {'tiri_fatti_casa': 16.2, 'tiri_concessi_casa': 8.1, 'in_porta_fatti': 5.8, 'in_porta_concessi': 2.4},
    'Milan': {'tiri_fatti_casa': 14.5, 'tiri_concessi_casa': 10.2, 'in_porta_fatti': 4.9, 'in_porta_concessi': 3.1},
    'Juventus': {'tiri_fatti_casa': 13.8, 'tiri_concessi_casa': 9.0, 'in_porta_fatti': 4.5, 'in_porta_concessi': 2.8},
    'Napoli': {'tiri_fatti_casa': 15.1, 'tiri_concessi_casa': 8.8, 'in_porta_fatti': 5.2, 'in_porta_concessi': 2.9},
    'Atalanta': {'tiri_fatti_casa': 15.8, 'tiri_concessi_casa': 10.5, 'in_porta_fatti': 5.5, 'in_porta_concessi': 3.5},
    'Roma': {'tiri_fatti_casa': 13.2, 'tiri_concessi_casa': 11.0, 'in_porta_fatti': 4.2, 'in_porta_concessi': 3.6}
}

# 2. Sidebar parametri
st.sidebar.header("Parametri Partita")
squadra_casa = st.sidebar.selectbox("Squadra in Casa", list(stats_squadre.keys()), index=0)
squadra_ospite = st.sidebar.selectbox("Squadra Ospite", list(stats_squadre.keys()), index=1)
tipo_tiro = st.sidebar.radio("Tipo di Dati", ["Tiri Totali", "Tiri in Porta"])

col1, col2 = st.columns(2)

with col1:
    linea_bookmaker = st.number_input("Linea proposta dal Bookmaker (es. 24.5 o 8.5)", value=24.5, step=0.5)
with col2:
    quota_over = st.number_input("Quota Over Bookmaker", value=1.85, step=0.05)

if squadra_casa == squadra_ospite:
    st.error("Seleziona due squadre diverse.")
else:
    # 3. Calcolo media attesa (Lambda)
    if tipo_tiro == "Tiri Totali":
        lambda_casa = (stats_squadre[squadra_casa]['tiri_fatti_casa'] + stats_squadre[squadra_ospite]['tiri_concessi_casa']) / 2
        lambda_ospite = (stats_squadre[squadra_ospite]['tiri_fatti_casa'] + stats_squadre[squadra_casa]['tiri_concessi_casa']) / 2
    else:
        lambda_casa = (stats_squadre[squadra_casa]['in_porta_fatti'] + stats_squadre[squadra_ospite]['in_porta_concessi']) / 2
        lambda_ospite = (stats_squadre[squadra_ospite]['in_porta_fatti'] + stats_squadre[squadra_casa]['in_porta_concessi']) / 2

    lambda_totale = lambda_casa + lambda_ospite

    # 4. Calcolo probabilità Poisson
    # Probabilità che i tiri siano minor o uguali alla linea (troncata)
    k = int(np.floor(linea_bookmaker))
    prob_under = poisson.cdf(k, lambda_totale)
    prob_over = 1 - prob_under

    quota_reale_over = 1 / prob_over if prob_over > 0 else 0
    expected_value = (prob_over * quota_over) - 1

    # 5. Output Risultati
    st.subheader(f"Analisi: {squadra_casa} vs {squadra_ospite}")
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Media Tiri Attesi Totali", f"{lambda_totale:.2f}")
    m2.metric("Probabilità Stimata Over", f"{prob_over * 100:.1f}%")
    m3.metric("Quota Reale Calcolata", f"{quota_reale_over:.2f}")

    st.markdown("---")
    
    if expected_value > 0:
        st.success(f"🔥 **VALUE BET TROVATA!** Expected Value: **+{expected_value * 100:.2f}%**\n"
                   f"La quota bookmaker ({quota_over}) è più alta della quota reale ({quota_reale_over:.2f}).")
    else:
        st.warning(f"❌ **NESSUN VALORE.** Expected Value: **{expected_value * 100:.2f}%**\n"
                   f"La quota del bookmaker non rispecchia un margine di vantaggio.")