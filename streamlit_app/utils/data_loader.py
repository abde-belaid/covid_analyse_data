import os
import pandas as pd
import streamlit as st
import s3fs
from dotenv import load_dotenv

# Charger les variables d'environnement (depuis le .env à la racine)
load_dotenv()

MINIO_ENDPOINT = os.getenv("MINIO_HOST", "localhost")
MINIO_PORT = os.getenv("MINIO_PORT", "9000")
MINIO_URL = f"http://{MINIO_ENDPOINT}:{MINIO_PORT}"

MINIO_USER = os.getenv("MINIO_ROOT_USER", "minioadmin")
MINIO_PASSWORD = os.getenv("MINIO_ROOT_PASSWORD", "minioadmin")
GOLD_BUCKET = os.getenv("MINIO_BUCKET_GOLD", "gold")

@st.cache_resource
def get_s3_fs():
    """Initialise la connexion à MinIO via s3fs"""
    return s3fs.S3FileSystem(
        key=MINIO_USER,
        secret=MINIO_PASSWORD,
        client_kwargs={'endpoint_url': MINIO_URL}
    )

@st.cache_data(ttl=3600)
def load_dataset(dataset_name: str) -> pd.DataFrame:
    """
    Charge un dataset Parquet depuis la couche Gold de MinIO.
    Utilise le cache de Streamlit pour optimiser les performances.
    """
    fs = get_s3_fs()
    path = f"{GOLD_BUCKET}/{dataset_name}"
    
    try:
        # Liste les fichiers parquet dans le dossier
        files = fs.glob(f"{path}/*.parquet")
        if not files:
            st.error(f"Aucun fichier trouvé pour {dataset_name} dans la couche Gold.")
            return pd.DataFrame()
        
        # Lit le dataset complet via pyarrow et s3fs
        df = pd.read_parquet(f"s3://{path}", storage_options={
            "key": MINIO_USER,
            "secret": MINIO_PASSWORD,
            "client_kwargs": {"endpoint_url": MINIO_URL}
        })
        
        # S'assurer que les colonnes temporelles soient bien typées si elles existent
        if 'year' in df.columns and 'month' in df.columns:
            # Créer une colonne Date pour faciliter les graphes
            df['date'] = pd.to_datetime(
                df['year'].astype(str) + '-' + df['month'].astype(str).str.zfill(2) + '-01',
                errors='coerce'
            )
            df = df.sort_values(by=['location', 'date'])
            
        return df
    except Exception as e:
        st.error(f"Erreur lors du chargement de {dataset_name}: {str(e)}")
        return pd.DataFrame()

@st.cache_data
def get_all_locations():
    """Récupère la liste de tous les pays disponibles (basé sur vaccination_by_location)"""
    df = load_dataset("vaccination_by_location")
    if not df.empty and 'location' in df.columns:
        return sorted(df['location'].unique().tolist())
    return []
