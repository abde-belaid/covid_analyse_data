import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.data_loader import load_dataset

st.set_page_config(page_title="Focus Maroc", page_icon="🇲🇦", layout="wide")

st.title("🇲🇦 Chapitre 3 : L'Histoire du Maroc face au COVID-19")

st.markdown("""
Le Maroc a été l'un des pionniers en Afrique concernant la gestion de la crise sanitaire et l'acquisition précoce de vaccins.
À travers ces données, nous allons raconter l'histoire de cette riposte, de la montée des tests au lancement de la vaste campagne de vaccination.
""")

with st.spinner("Récupération des archives marocaines..."):
    cases_df = load_dataset("cases_monthly")
    vax_df = load_dataset("vaccination_monthly")
    mort_df = load_dataset("mortality_monthly")
    test_df = load_dataset("testing_monthly")

# Extraction stricte pour le Maroc
ma_cases = cases_df[cases_df['location'] == 'Morocco'].sort_values('date') if not cases_df.empty else None
ma_vax = vax_df[vax_df['location'] == 'Morocco'].sort_values('date') if not vax_df.empty else None
ma_mort = mort_df[mort_df['location'] == 'Morocco'].sort_values('date') if not mort_df.empty else None
ma_test = test_df[test_df['location'] == 'Morocco'].sort_values('date') if not test_df.empty else None

if ma_cases is None or ma_cases.empty:
    st.warning("Données marocaines introuvables dans le Dataset actuel.")
else:
    # 1. Première vague et capacité de dépistage
    st.header("1️⃣ Le Dépistage : Première Ligne de Défense")
    st.markdown("""
    Dès les premiers mois de la pandémie (Mars 2020), le Maroc a rapidement dû accroître sa capacité de dépistage (PCR puis Antigénique).
    Voici l'évolution du volume de tests par rapport au nombre de cas confirmés.
    """)
    if ma_test is not None and not ma_test.empty:
        fig1 = go.Figure()
        fig1.add_trace(go.Bar(x=ma_test['date'], y=ma_test['total_new_tests'], name="Tests Réalisés", marker_color='lightgray'))
        fig1.add_trace(go.Scatter(x=ma_cases['date'], y=ma_cases['total_new_cases'], mode='lines', name="Nouveaux Cas", line=dict(color='orange', width=3)))
        fig1.update_layout(title="Capacité de Dépistage vs Vagues de Contamination", template="plotly_white", barmode='overlay')
        st.plotly_chart(fig1, use_container_width=True)

    # 2. La Campagne de Vaccination
    st.header("2️⃣ La Riposte Vaccinale")
    st.markdown("""
    Début 2021, le Maroc lance une campagne nationale massive. Contrairement à de nombreux pays de la région, la courbe d'adoption grimpe en flèche grâce à l'acquisition rapide de doses (Sinopharm, AstraZeneca, etc.).
    """)
    
    if ma_vax is not None and not ma_vax.empty:
        fig2 = px.area(
            ma_vax, x="date", y=["max_people_vaccinated", "max_fully_vaccinated"],
            labels={"value": "Population Vaccinée", "variable": "Statut", "date": "Date"},
            title="L'ascension fulgurante de l'immunité collective",
            color_discrete_map={"max_people_vaccinated": "lightblue", "max_fully_vaccinated": "darkblue"},
            template="plotly_white"
        )
        st.plotly_chart(fig2, use_container_width=True)
        
    # 3. L'Impact sur la Mortalité
    st.header("3️⃣ Sauver des Vies : L'Impact de la Vaccination")
    st.markdown("""
    Le but ultime de toute cette logistique était d'aplatir la courbe de la mortalité. 
    En observant le graphique ci-dessous, repérez les vagues tardives de cas (fin 2021/début 2022) : grâce à l'immunité acquise (plus de 23 millions de vaccinés), la proportion de cas sévères et de décès a considérablement diminué par rapport à la vague de l'été 2021.
    """)
    
    if ma_mort is not None and not ma_mort.empty:
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(x=ma_cases['date'], y=ma_cases['total_new_cases'], fill='tozeroy', mode='none', name="Volume des Cas", fillcolor='rgba(255, 165, 0, 0.2)', yaxis='y1'))
        fig3.add_trace(go.Scatter(x=ma_mort['date'], y=ma_mort['total_new_deaths'], mode='lines', name="Décès", line=dict(color='red', width=3), yaxis='y2'))
        
        fig3.update_layout(
            title="Cas Confirmés vs Mortalité (Le découplage post-vaccination)",
            yaxis=dict(title="Volume de Cas (Fond Orange)", showgrid=False),
            yaxis2=dict(title="Décès (Ligne Rouge)", overlaying="y", side="right"),
            template="plotly_white"
        )
        st.plotly_chart(fig3, use_container_width=True)

    st.success("🇲🇦 Le Royaume a démontré une résilience exceptionnelle, transformant une gestion de crise sanitaire en une leçon d'agilité logistique.")
