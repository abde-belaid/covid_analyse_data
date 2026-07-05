import streamlit as st

# Configuration de la page principale (doit être la première commande Streamlit)
st.set_page_config(
    page_title="COVID-19 Data Story",
    page_icon="🦠",
    layout="wide",
    initial_sidebar_state="expanded",
)

from utils.data_loader import load_dataset

def main():
    st.title("🦠 COVID-19 : L'Histoire d'une Pandémie Mondiale")
    
    st.markdown("""
    Bienvenue dans ce Dashboard interactif dédié à l'analyse de l'impact du **COVID-19** à travers le monde.
    
    À partir de données massives collectées quotidiennement, nettoyées et agrégées dans notre *Data Lake (Architecture Medallion)*, cette application vous propose de plonger au cœur des chiffres pour comprendre :
    - Comment le virus s'est propagé à l'échelle planétaire.
    - Quel a été l'impact réel de la campagne de vaccination mondiale sur la mortalité.
    - Quel est le lien crucial entre la capacité de dépistage d'un pays et le bilan humain.
    
    ### 📖 Sommaire (Navigation dans la barre latérale)
    1. **🌍 Comparaison Pays** : Analysez et comparez les stratégies et les impacts entre différentes nations (Heatmaps, Tendances).
    2. **📅 Analyse Temporelle** : Plongez dans la chronologie de la pandémie pour un pays donné (Saisonnalité, Lissage, Time-lag).
    3. **🏆 Bilan et Classements** : Découvrez le classement des pays les plus touchés et une macro-analyse globale Vaccination vs Mortalité.
    4. **🧪 Dynamique de Dépistage** : Comprenez pourquoi le taux de positivité a été l'indicateur d'alerte numéro 1 durant la pandémie.
    
    ---
    """)

    # Vue d'ensemble (Aperçu des données globales)
    st.subheader("📊 Aperçu des Données Mondiales (Statistiques Aggregées)")
    
    # Chargement rapide des données (en cache)
    with st.spinner("Chargement des données depuis la couche Gold..."):
        vax_df = load_dataset("vaccination_by_location")
        mort_df = load_dataset("mortality_by_location")
        cases_df = load_dataset("cases_by_location")
    
    if vax_df.empty or mort_df.empty or cases_df.empty:
        st.warning("⚠️ Les données ne sont pas encore disponibles. Assurez-vous que le pipeline PySpark a bien généré la couche Gold dans MinIO.")
        return

    # Nettoyage des agrégats mondiaux si existants (ex: 'World', 'Europe') 
    # pour garder un aperçu approximatif des totaux
    world_cases = cases_df[cases_df['location'] == 'World']['total_cases'].max() if 'World' in cases_df['location'].values else cases_df['total_cases'].sum()
    world_deaths = mort_df[mort_df['location'] == 'World']['total_deaths'].max() if 'World' in mort_df['location'].values else mort_df['total_deaths'].sum()
    world_vax = vax_df[vax_df['location'] == 'World']['max_fully_vaccinated'].max() if 'World' in vax_df['location'].values else vax_df['max_fully_vaccinated'].sum()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="🦠 Total Cas", value=f"{world_cases:,.0f}".replace(",", " "))
    with col2:
        st.metric(label="☠️ Total Décès", value=f"{world_deaths:,.0f}".replace(",", " "))
    with col3:
        st.metric(label="💉 Personnes Totalement Vaccinées", value=f"{world_vax:,.0f}".replace(",", " "))
        
    st.markdown("---")
    st.subheader("🗺️ Cartographie Mondiale de la Vaccination")
    
    # Préparer les données pour la carte (exclure les aggrégats)
    import plotly.express as px
    continents = ['World', 'Europe', 'North America', 'South America', 'Asia', 'Africa', 'European Union', 'High income', 'Upper middle income', 'Lower middle income', 'Low income']
    map_df = vax_df[~vax_df['location'].isin(continents)]
    
    if not map_df.empty and 'max_fully_vaccinated' in map_df.columns:
        fig_map = px.choropleth(
            map_df,
            locations="location",
            locationmode="country names",
            color="max_fully_vaccinated",
            hover_name="location",
            color_continuous_scale="Blues",
            title="Personnes Totalement Vaccinées par Pays",
            template="plotly_white"
        )
        fig_map.update_layout(margin={"r":0,"t":40,"l":0,"b":0})
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.info("Données géographiques insuffisantes pour la carte.")
        
    st.info("👈 **Commencez l'exploration détaillée en sélectionnant un chapitre dans la barre latérale !**")

if __name__ == "__main__":
    main()
