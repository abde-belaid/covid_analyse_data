# Démarrage du projet

## 1. Configurer l'environnement

```bash
cp .env-example .env
```

## 2. Installer les dépendances locales

```bash
pip install -r requirements.txt
```

## 3. Démarrer les services Docker (Spark + MinIO)

```bash
docker compose -f docker/docker-compose.yml up -d
```

## 4. Accéder aux interfaces

- **Spark Master UI** : http://localhost:8080
- **MinIO Console** : http://localhost:9001 (user: `minioadmin`, password: `minioadmin`)
- **Spark Master** : spark://spark-master:7077 (depuis scripts Python)

## 5. Développer et tester localement

Vous pouvez maintenant :
- Exécuter `python scripts/main.py` sur votre machine locale
- Utiliser Jupyter : `jupyter lab`
- Les connexions Docker utilisent le réseau `covid-net`

## 6. Arrêter les services

```bash
docker compose -f docker/docker-compose.yml down
```

## Notes

- Le projet n'a pas encore de service applicatif Docker. Les scripts s'exécutent en local.
- Une fois votre application développée et testée, vous pouvez ajouter un service `app` au docker-compose.yml.
