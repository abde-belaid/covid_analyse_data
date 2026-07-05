import streamlit as st
import plotly.express as px
import pandas as pd
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.data_loader import load_dataset

st.set_page_config(page_title="Bilan et Classements", page_icon="🏆", layout="wide")

st.title("🏆 Chapitre 3 : Bilan Macro et Cartographie Globale")

st.markdown("""
Découvrez ici un bilan consolidé de l'impact de la pandémie à travers le monde.
L'objectif est d'identifier les pays les plus affectés et d'évaluer visuellement la corrélation macroéconomique entre l'effort de vaccination et le bilan humain.
""")

with st.spinner("Chargement du bilan consolidé (Couche Gold)..."):
    cases_df = load_dataset("cases_by_location")
    mort_df = load_dataset("mortality_by_location")
    vax_df = load_dataset("vaccination_by_location")

# Nettoyage : retirer les agrégats de régions (Europe, World, etc.)
continents = ['World', 'Europe', 'North America', 'South America', 'Asia', 'Africa', 
              'European Union', 'High income', 'Upper middle income', 'Lower middle income', 'Low income']

if not mort_df.empty and not vax_df.empty and not cases_df.empty:
    
    # 1. Cartographie
    st.header("🗺️ Cartographie de la Mortalité")
    st.markdown("Visualisation mondiale du volume total de décès recensés par pays.")
    map_df = mort_df[~mort_df['location'].isin(continents)].copy()
    
    fig_map = px.choropleth(
        map_df,
        locations="location",
        locationmode="country names",
        color="total_deaths",
        hover_name="location",
        color_continuous_scale="Reds",
        title="Bilan Total des Décès par Pays",
        template="plotly_white"
    )
    fig_map.update_layout(margin={"r":0,"t":40,"l":0,"b":0})
    st.plotly_chart(fig_map, use_container_width=True)

    # Fusion des données pour le classement et scatter plot
    merged_macro = pd.merge(cases_df, mort_df, on='location', how='inner')
    merged_macro = pd.merge(merged_macro, vax_df, on='location', how='inner')
    merged_macro = merged_macro[~merged_macro['location'].isin(continents)]

    # 2. Classements (Top 10)
    st.header("📊 Le Palmarès (Top 10)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Pays les plus impactés (Décès)")
        top_deaths = merged_macro.nlargest(10, 'total_deaths').sort_values('total_deaths', ascending=True)
        fig_bar_deaths = px.bar(top_deaths, x='total_deaths', y='location', orientation='h',
                                title="Top 10 des décès absolus", color='total_deaths', color_continuous_scale="Reds")
        st.plotly_chart(fig_bar_deaths, use_container_width=True)
        
    with col2:
        st.subheader("Effort Vaccinal (Volume de personnes)")
        top_vax = merged_macro.nlargest(10, 'max_fully_vaccinated').sort_values('max_fully_vaccinated', ascending=True)
        fig_bar_vax = px.bar(top_vax, x='max_fully_vaccinated', y='location', orientation='h',
                             title="Top 10 de l'immunisation", color='max_fully_vaccinated', color_continuous_scale="Greens")
        st.plotly_chart(fig_bar_vax, use_container_width=True)

    # 3. Scatter Plot macro : Vaccination vs Mortalité
    st.header("⚖️ Macro-Analyse : L'Immunisation a-t-elle protégé la population ?")
    st.markdown("""
    Chaque point représente un pays. Observez la relation entre le volume de personnes complètement vaccinées et le bilan final de mortalité.
    (*L'axe est logarithmique pour mieux voir l'ensemble des pays, indépendamment de leur taille*).
    """)
    
    fig_scatter = px.scatter(
        merged_macro,
        x="max_fully_vaccinated",
        y="total_deaths",
        size="total_cases",
        color="location",
        hover_name="location",
        log_x=True, log_y=True,
        title="Relation globale : Personnes Vaccinées vs Total des Décès",
        labels={"max_fully_vaccinated": "Personnes Totalement Vaccinées (Log)", "total_deaths": "Total Décès (Log)"},
        template="plotly_white",
        size_max=40
    )
    # Ajouter une ligne de tendance (tendances générales)
    st.plotly_chart(fig_scatter, use_container_width=True)
    
else:
    st.error("Données Gold inaccessibles ou vides. Veuillez vérifier l'ingestion.")
