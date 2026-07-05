import streamlit as st
import plotly.express as px
import sys
import os

# Permet d'importer depuis le dossier parent
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.data_loader import load_dataset, get_all_locations

st.set_page_config(page_title="Comparaison Pays", page_icon="🌍", layout="wide")

st.title("🌍 Chapitre 1 : Comparaison Mondiale")

st.markdown("""
Dans cette première partie de notre analyse, nous observons comment différents pays ont fait face à la pandémie. 
Sélectionnez plusieurs pays ci-dessous pour comparer l'évolution des **cas déclarés**, de la **mortalité** et du **taux de positivité** au fil des mois.
""")

# Chargement des données
with st.spinner("Chargement des données..."):
    cases_df = load_dataset("cases_monthly")
    mort_df = load_dataset("mortality_monthly")
    test_df = load_dataset("testing_monthly")

all_locations = get_all_locations()
# Exclure les agrégats de continents générés par OWID pour une comparaison juste
continents = ['World', 'Europe', 'North America', 'South America', 'Asia', 'Africa', 'European Union', 'High income', 'Upper middle income', 'Lower middle income', 'Low income']
filtered_locations = [loc for loc in all_locations if loc not in continents]

# Widgets de sélection
default_countries = ["France", "United States", "Brazil", "India"]
selected_countries = st.multiselect(
    "Sélectionnez les pays à comparer :", 
    options=filtered_locations, 
    default=[c for c in default_countries if c in filtered_locations]
)

if not selected_countries:
    st.warning("Veuillez sélectionner au moins un pays.")
else:
    # Filtrer les données
    filtered_cases = cases_df[cases_df['location'].isin(selected_countries)]
    filtered_mort = mort_df[mort_df['location'].isin(selected_countries)]
    
    st.markdown("### 📈 Évolution Mensuelle des Nouveaux Cas")
    if not filtered_cases.empty and 'date' in filtered_cases.columns:
        fig_cases = px.line(
            filtered_cases, x="date", y="total_new_cases", color="location",
            labels={"total_new_cases": "Nouveaux Cas", "date": "Date", "location": "Pays"},
            template="plotly_white"
        )
        st.plotly_chart(fig_cases, use_container_width=True)
    else:
        st.info("Données insuffisantes pour les cas.")

    st.markdown("### 📉 Évolution Mensuelle des Décès")
    st.markdown("*On observe souvent un décalage (lag) entre le pic des cas et le pic des décès.*")
    if not filtered_mort.empty and 'date' in filtered_mort.columns:
        fig_mort = px.line(
            filtered_mort, x="date", y="total_new_deaths", color="location",
            labels={"total_new_deaths": "Nouveaux Décès", "date": "Date", "location": "Pays"},
            template="plotly_white"
        )
        st.plotly_chart(fig_mort, use_container_width=True)
    else:
        st.info("Données insuffisantes pour les décès.")
        
    st.markdown("### 🧪 Capacité de Dépistage (Taux de Positivité Moyen)")
    filtered_test = test_df[test_df['location'].isin(selected_countries)]
    if not filtered_test.empty and 'date' in filtered_test.columns:
        fig_test = px.bar(
            filtered_test, x="location", y="avg_positive_rate", color="location",
            animation_frame=filtered_test["date"].dt.strftime('%Y-%m'), # Format string pour l'animation
            range_y=[0, filtered_test['avg_positive_rate'].max() * 1.2],
            labels={"avg_positive_rate": "Taux de Positivité", "location": "Pays"},
            title="Évolution du Taux de Positivité par Mois",
            template="plotly_white"
        )
        st.plotly_chart(fig_test, use_container_width=True)
    else:
        st.info("Les données de dépistage ne sont pas assez denses pour ces pays.")
        
    st.markdown("---")
    st.markdown("### 🔍 Heatmap des Corrélations entre Variables")
    st.markdown("Pour les pays sélectionnés, comment les différentes variables interagissent-elles ?")
    
    # Préparer les données pour la corrélation
    if not filtered_cases.empty and not filtered_mort.empty:
        # Fusionner les datasets sur location et date
        import pandas as pd
        merged_corr = pd.merge(filtered_cases[['location', 'date', 'total_new_cases']], 
                               filtered_mort[['location', 'date', 'total_new_deaths']], 
                               on=['location', 'date'], how='inner')
        if not filtered_test.empty:
            merged_corr = pd.merge(merged_corr, filtered_test[['location', 'date', 'avg_positive_rate', 'total_new_tests']], 
                                   on=['location', 'date'], how='left')
            
        # Sélectionner les colonnes numériques
        num_cols = merged_corr.select_dtypes(include=['float64', 'int64']).columns
        if len(num_cols) > 1:
            corr_matrix = merged_corr[num_cols].corr()
            
            import plotly.graph_objects as go
            fig_corr = go.Figure(data=go.Heatmap(
                z=corr_matrix.values,
                x=corr_matrix.columns,
                y=corr_matrix.index,
                colorscale='RdBu',
                zmin=-1, zmax=1,
                text=corr_matrix.values.round(2),
                texttemplate="%{text}",
                showscale=True
            ))
            fig_corr.update_layout(
                title="Corrélation de Pearson (Nouveaux Cas, Décès, Tests, Positivité)",
                template="plotly_white",
                height=500
            )
            st.plotly_chart(fig_corr, use_container_width=True)
        else:
            st.info("Variables numériques insuffisantes pour générer la Heatmap.")
