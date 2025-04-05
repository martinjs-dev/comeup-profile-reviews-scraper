# ComeUp Reviews Scraper

Un outil en Python pour extraire automatiquement les avis clients de votre profil ComeUp ainsi que les réponses du vendeur.

## 🌟 Fonctionnalités

- Extraction automatique de tous les services d'un profil ComeUp
- Récupération de tous les avis clients pour chaque service
- Capture des réponses du vendeur pour chaque avis
- Export des données en JSON et CSV
- Traitement intelligent des pages avec pagination ("Plus de commentaires")
- Dédoublonnage des services

## 📋 Prérequis

- Python 3.8+
- pip (gestionnaire de paquets Python)

## 🚀 Installation

1. Clonez ce dépôt :
```bash
git clone https://github.com/votre-username/comeup-scraper.git
cd comeup-scraper
```

2. Créez un environnement virtuel :
```bash
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

3. Installez les dépendances :
```bash
pip install -r requirements.txt
playwright install
```

## 💡 Utilisation

1. Exécutez le script en spécifiant l'URL du profil ComeUp à scraper :
```bash
python scraper.py
```

2. Le script va automatiquement :
   - Visiter la page du profil spécifié
   - Identifier tous les services proposés
   - Parcourir chaque service pour collecter les avis
   - Sauvegarder les résultats dans le dossier `data/`

## 📊 Format des données

Exemple d'un avis dans le JSON généré :
```json
{
  "service_url": "https://comeup.com/fr/service/221336/creer-votre-site-wordpress-optimise-seo-avec-un-design-premium",
  "service_name": "Je vais créer votre site WordPress optimisé SEO avec un design premium",
  "client": "Ayoubouilali",
  "commentaire": "Rendu nickel comme d'habitude, merci.",
  "date": "24 sept. 2024 à 21:41",
  "positive": true,
  "seller_response": "Merci à vous aussi pour la confiance. Je reste à votre disposition."
}
```

## 🔧 Personnalisation

Vous pouvez modifier le script selon vos besoins :

- Pour changer l'URL du profil, modifiez la variable `profile_url` dans la fonction `main()`.
- Pour ajuster le délai d'attente entre les clics, modifiez la valeur du `page.wait_for_timeout()`.
- Pour changer le mode headless, modifiez `headless=False` à `headless=True` pour exécuter sans interface visuelle.

## 📁 Structure du projet

```
comeup-scraper/
├── scraper.py          # Script principal
├── requirements.txt    # Dépendances du projet
├── README.md           # Documentation
└── data/               # Dossier généré pour stocker les données extraites
    ├── avis_comeup_YYYYMMDD_HHMMSS.json  # Format JSON
    └── avis_comeup_YYYYMMDD_HHMMSS.csv   # Format CSV (si pandas est installé)
```

## 📑 Dépendances

- [Playwright](https://playwright.dev/) - Pour l'automatisation du navigateur
- [Pandas](https://pandas.pydata.org/) - Pour l'export CSV (optionnel)

## ⚠️ Avertissement

Ce script est destiné à un usage personnel pour récupérer vos propres avis. Respectez les conditions d'utilisation de ComeUp et n'utilisez pas cet outil pour scraper des profils qui ne vous appartiennent pas sans autorisation. Une utilisation excessive peut entraîner une limitation de votre accès à la plateforme.

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou à proposer une pull request.

## 📜 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.