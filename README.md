# 🛡️ Sentinelle Web

Mini application web en **Python + Flask** qui analyse une adresse web et lui attribue un **score de risque d'hameçonnage** (0 = très risqué, 100 = aucun signal détecté), avec les raisons expliquées en langage clair.

> ⚠️ L'analyse est purement textuelle : l'application ne visite jamais les liens analysés.

## 🔍 Les 12 règles de détection

| # | Règle | Pénalité |
|---|-------|----------|
| 1 | Connexion non chiffrée (absence de HTTPS) | −10 |
| 2 | Adresse IP au lieu d'un nom de domaine | −35 |
| 3 | Lien très long (plus de 100 caractères) | −10 |
| 4 | Imitation d'une marque connue ou faute de frappe | −40 |
| 5 | Présence de « @ » dans l'adresse | −30 |
| 6 | Extension suspecte | −20 |
| 7 | Trois sous-domaines ou plus | −15 |
| 8 | Plusieurs tirets dans le domaine principal | −15 |
| 9 | Mots typiques des arnaques | −30 |
| 10 | Caractères d'autres alphabets ou punycode | −35 |
| 11 | Lien raccourci | −15 |
| 12 | Domaine récemment enregistré (moins de 30 jours / moins de 180 jours) | −15 |

Le score commence à 100 et diminue lorsque des signaux suspects sont détectés. Un score élevé ne garantit pas qu'un site est légitime.

**Verdicts :** 80–100 → *Aucun signal majeur* 🟢 · 50–79 → *Prudence* 🟠 · 0–49 → *Risqué* 🔴

## ✨ Fonctionnalités

- **Historique de session** : chaque analyse s'ajoute à un historique personnel (10 dernières, la plus récente en premier), avec pastilles de couleur — parfait pour comparer plusieurs liens pendant une démo.
- **Bouton « Effacer l'historique »** pour repartir à zéro.
- **Présentation soignée** : bandeau bleu marine et accents dorés, mise en page adaptative (mobile et bureau).

## 🚀 Installation et lancement

Python 3 requis (`python --version` pour vérifier).

```bash
# 1. Aller dans le dossier du projet
cd sentinelle-pratique

# 2. Créer un environnement virtuel
python -m venv .venv

# 3. L'activer
#    Windows (PowerShell) :  .venv\Scripts\Activate.ps1
#    macOS / Linux :         source .venv/bin/activate

# 4. Installer les dépendances
pip install -r requirements.txt

# 5. Lancer l'application
python app.py
```

Ouvrir ensuite **http://127.0.0.1:5000** dans le navigateur.

## 🧪 Jeux de tests

Le fichier `jeux-de-tests.md` détaille 6 adresses avec le score et le verdict attendus pour chacune :

| Adresse | Score | Verdict |
|---|---|---|
| `https://www.google.com` | 100 | Aucun signal majeur|
| `http://banque-legitime.com@site-pirate.ru/connexion` | 40 | Risqué |
| `https://www.paypa1.com/connexion` | 75 | Prudence |
| `http://desjardins-securite.com` | 45 | Risqué |
| `https://connexion.banque.nationale.securite-verification.com/session/identifiant/client` | 60 | Prudence |
| `https://www.paypal.com/signin` | 100 | Aucun signal majeur |

## 🗂️ Structure du projet

```
sentinelle-pratique/
├── app.py               ← serveur Flask + logique d'analyse (6 règles)
├── requirements.txt     ← dépendances (Flask)
├── static/
│   └── style.css        ← feuille de style partagée (marine/or)
└── templates/
    ├── index.html       ← page du formulaire
    └── resultat.html    ← page de résultat (score, raisons, historique)
```

## 🛠️ Technologies

- Python 3 + Flask (routes, gabarits Jinja2, sessions)
- HTML / CSS maison (variables CSS, adaptatif)

## 👤 Contexte

Projet d'entraînement réalisé en vue d'**HackDécouverte 2026** (hackathon, 14 novembre 2026, Université Concordia, Montréal). La version du jour J sera reconstruite sur place avec l'équipe.

**Auteur :** Olivier Montpetit ([@khol76](https://github.com/khol76)) — AEC Infrastructure informatique et cybersécurité, Cégep Bois-de-Boulogne.

## 🔒 Limites honnêtes

- L'application détecte des *signaux* d'hameçonnage : elle ne garantit jamais qu'un site est légitime.
- L'historique vit dans un cookie de session : il disparaît si les cookies sont effacés et ne suit pas d'un appareil à l'autre. Un vrai produit le stockerait côté serveur, dans une base de données.
