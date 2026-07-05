import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import sys
import os
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.data_loader import load_dataset, get_all_locations

st.set_page_config(page_title="Analyse Temporelle", page_icon="📅", layout="wide")

st.title("📅 Chapitre 2 : Analyse Temporelle et Impact Vaccinal")

st.markdown("""
Comment la vaccination a-t-elle influencé les courbes de mortalité ? 
Sélectionnez **un pays** pour analyser en détail la corrélation (et le décalage temporel) entre la montée de la couverture vaccinale et les vagues de mortalité.
""")

all_locations = get_all_locations()
country = st.selectbox("Choisissez un pays à analyser :", options=all_locations, index=all_locations.index("France") if "France" in all_locations else 0)

with st.spinner(f"Analyse des données pour {country}..."):
    vax_df = load_dataset("vaccination_monthly")
    mort_df = load_dataset("mortality_monthly")

if not vax_df.empty and not mort_df.empty:
    vax_country = vax_df[vax_df['location'] == country]
    mort_country = mort_df[mort_df['location'] == country]

    if not vax_country.empty and not mort_country.empty:
        # Fusion des données sur la date
        merged = pd.merge(vax_country[['date', 'max_fully_vaccinated']], 
                          mort_country[['date', 'total_new_deaths']], 
                          on='date', how='inner')
        merged = merged.sort_values('date')

        # Sélecteur de dates (Slider)
        min_date = merged['date'].min().to_pydatetime()
        max_date = merged['date'].max().to_pydatetime()
        
        st.markdown("### 🎚️ Filtrage Temporel")
        date_range = st.slider(
            "Sélectionnez la période à analyser :",
            min_value=min_date,
            max_value=max_date,
            value=(min_date, max_date),
            format="YYYY-MM"
        )
        
        merged = merged[(merged['date'] >= pd.to_datetime(date_range[0])) & (merged['date'] <= pd.to_datetime(date_range[1]))]
        
        # Lissage des courbes (Moyenne mobile)
        window = st.slider("Niveau de lissage (Moyenne mobile en mois) :", min_value=1, max_value=6, value=2)
        merged['smoothed_deaths'] = merged['total_new_deaths'].rolling(window=window, min_periods=1).mean()

        st.markdown(f"### L'Histoire de {country}")
        st.markdown(f"Ce graphique interactif montre deux axes Y. L'axe de gauche représente la couverture vaccinale (aire bleue), et celui de droite la mortalité mensuelle (ligne rouge).")

        fig = go.Figure()
        
        # Ajout de la vaccination en aire remplie
        fig.add_trace(go.Scatter(
            x=merged['date'], y=merged['max_fully_vaccinated'],
            fill='tozeroy',
            mode='lines',
            line=dict(color='royalblue', width=2),
            name="Totalement Vaccinés",
            yaxis="y1"
        ))
        
        # Ajout de la mortalité en ligne (brute)
        fig.add_trace(go.Scatter(
            x=merged['date'], y=merged['total_new_deaths'],
            mode='markers',
            marker=dict(color='lightcoral', size=5, opacity=0.5),
            name="Décès Bruts",
            yaxis="y2"
        ))
        
        # Ajout de la mortalité en ligne lissée
        fig.add_trace(go.Scatter(
            x=merged['date'], y=merged['smoothed_deaths'],
            mode='lines',
            line=dict(color='firebrick', width=3, shape='spline'), # shape spline = courbe lissée visuellement
            name="Décès Lissés (Tendance)",
            yaxis="y2"
        ))
        
        # Configuration des deux axes
        fig.update_layout(
            title_text=f"Impact de la Vaccination sur la Mortalité - {country}",
            xaxis_title="Date",
            yaxis=dict(
                title=dict(text="Personnes Totalement Vaccinées", font=dict(color="royalblue")),
                tickfont=dict(color="royalblue")
            ),
            yaxis2=dict(
                title=dict(text="Décès (Mensuel)", font=dict(color="firebrick")),
                tickfont=dict(color="firebrick"),
                overlaying="y",
                side="right"
            ),
            legend=dict(x=0.01, y=0.99, bgcolor='rgba(255,255,255,0.8)'),
            template="plotly_white"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Heatmap des corrélations
        st.markdown("### 🔍 Corrélations Temporelles")
        st.markdown("""
        La vaccination ne fait pas baisser la mortalité instantanément. Il y a un décalage.
        Voici la corrélation mathématique (Pearson) entre le nombre de décès d'un mois et les statistiques de vaccination.
        Plus la valeur est proche de -1, plus la vaccination est fortement corrélée à une *baisse* de la mortalité.
        """)
        
        corr_val = merged['max_fully_vaccinated'].corr(merged['total_new_deaths'])
        
        # Calcul du lag (décalage de 1 et 2 mois)
        merged['deaths_lag_1'] = merged['total_new_deaths'].shift(-1)
        merged['deaths_lag_2'] = merged['total_new_deaths'].shift(-2)
        
        corr_lag1 = merged['max_fully_vaccinated'].corr(merged['deaths_lag_1'])
        corr_lag2 = merged['max_fully_vaccinated'].corr(merged['deaths_lag_2'])
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Corrélation (Mois en cours)", f"{corr_val:.2f}")
        col2.metric("Corrélation (Décalage +1 Mois)", f"{corr_lag1:.2f}")
        col3.metric("Corrélation (Décalage +2 Mois)", f"{corr_lag2:.2f}")

    else:
        st.info("Données insuffisantes pour tracer ce graphique.")
