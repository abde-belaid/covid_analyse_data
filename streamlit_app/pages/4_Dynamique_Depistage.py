import streamlit as st
import plotly.express as px
import pandas as pd
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.data_loader import load_dataset, get_all_locations

st.set_page_config(page_title="Dynamique de Dépistage", page_icon="🧪", layout="wide")

st.title("🧪 Chapitre 4 : La Dynamique du Dépistage")

st.markdown("""
Tester massivement la population a été l'un des enjeux majeurs du début de la pandémie. 
Cette page explore la relation entre le volume de tests effectués, le taux de positivité, et la détection réelle des cas.
**L'hypothèse :** Un taux de positivité très élevé indique généralement que le pays ne teste que les cas graves (sous-évaluation de l'épidémie), ce qui précède souvent une vague de mortalité sévère.
""")

with st.spinner("Chargement des historiques de dépistage..."):
    cases_df = load_dataset("cases_monthly")
    test_df = load_dataset("testing_monthly")
    mort_df = load_dataset("mortality_monthly")

all_locations = get_all_locations()
country = st.selectbox("Sélectionnez un pays pour analyser sa stratégie de dépistage :", 
                       options=all_locations, 
                       index=all_locations.index("United States") if "United States" in all_locations else 0)

if not cases_df.empty and not test_df.empty and not mort_df.empty:
    country_cases = cases_df[cases_df['location'] == country]
    country_tests = test_df[test_df['location'] == country]
    country_mort = mort_df[mort_df['location'] == country]
    
    if country_tests.empty:
        st.warning(f"Aucune donnée de dépistage (tests) disponible pour : {country}.")
    else:
        # Fusionner sur la date
        merged = pd.merge(country_cases[['date', 'total_new_cases']], 
                          country_tests[['date', 'total_new_tests', 'avg_positive_rate']], 
                          on='date', how='inner')
        merged = pd.merge(merged, country_mort[['date', 'total_new_deaths']], on='date', how='left')
        merged = merged.sort_values('date')
        
        # 1. Tests vs Cas Détectés
        st.header("1️⃣ L'effort de dépistage vs Contaminations détectées")
        st.markdown("Si le volume de tests n'augmente pas au même rythme que l'épidémie, de nombreux cas passent sous les radars.")
        
        fig1 = px.area(
            merged, x="date", y=["total_new_tests", "total_new_cases"],
            labels={"value": "Volume mensuel", "variable": "Indicateur", "date": "Date"},
            title=f"Volume de Tests vs Cas Positifs ({country})",
            color_discrete_map={"total_new_tests": "lightgray", "total_new_cases": "orange"},
            template="plotly_white"
        )
        st.plotly_chart(fig1, use_container_width=True)
        
        # 2. Taux de positivité comme indicateur d'alerte
        st.header("2️⃣ Le Taux de Positivité : Signal d'Alarme")
        st.markdown("""
        L'OMS considérait qu'un taux de positivité supérieur à 5% signifiait que l'épidémie n'était pas sous contrôle.
        Le graphique ci-dessous superpose ce **taux de positivité** avec la **mortalité**. Observez comment les pics de positivité (ligne rouge) précèdent souvent les vagues de décès (barres noires).
        """)
        
        import plotly.graph_objects as go
        fig2 = go.Figure()
        
        fig2.add_trace(go.Bar(
            x=merged['date'], y=merged['total_new_deaths'],
            name="Décès (Mensuel)",
            marker_color='black',
            yaxis='y1',
            opacity=0.6
        ))
        
        fig2.add_trace(go.Scatter(
            x=merged['date'], y=merged['avg_positive_rate'],
            mode='lines+markers',
            name="Taux de Positivité",
            line=dict(color='firebrick', width=3),
            yaxis='y2'
        ))
        
        fig2.update_layout(
            title=f"Taux de Positivité vs Mortalité - {country}",
            yaxis=dict(title="Volume de Décès", showgrid=False),
            yaxis2=dict(
                title=dict(text="Taux de Positivité (0 à 1)", font=dict(color="firebrick")),
                tickfont=dict(color="firebrick"),
                overlaying="y", side="right",
                range=[0, max(merged['avg_positive_rate'].max() * 1.2, 0.1)]
            ),
            template="plotly_white",
            legend=dict(x=0.01, y=0.99, bgcolor='rgba(255,255,255,0.8)')
        )
        st.plotly_chart(fig2, use_container_width=True)
else:
    st.error("Les données mensuelles nécessaires ne sont pas disponibles.")
