# 🛡️ Sentinelle Web

Mini application web en **Python + Flask** qui analyse une adresse web et lui attribue un **score de risque d'hameçonnage** (0 = très risqué, 100 = aucun signal détecté), avec les raisons expliquées en langage clair. Interface bilingue Français / Anglais.

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
| 9 | Mots typiques des arnaques | -8 par mot, max −30 |
| 10 | Caractères d'autres alphabets ou punycode | −35 |
| 11 | Lien raccourci | −30 |
| 12 | Domaine récemment enregistré (moins de 30 jours / moins de 180 jours) | −35 / -15 |

Le score commence à 100 et diminue lorsque des signaux suspects sont détectés. Un score élevé ne garantit pas qu'un site est légitime.

**Verdicts :** 80–100 → *Probablement sûr* 🟢 · 50–79 → *Prudence* 🟠 · 0–49 → *Risqué* 🔴

## ✨ Fonctionnalités

- **Historique de session** : chaque analyse s'ajoute à un historique personnel (10 dernières, la plus récente en premier), avec pastilles de couleur — parfait pour comparer plusieurs liens pendant une démo.
- **Bouton « Effacer l'historique »** pour repartir à zéro.
- **Présentation soignée** : bandeau bleu marine et accents dorés, mise en page adaptative (mobile et bureau).
- **Interface bilingue** Français / Anglais 

## 🚀 Installation et lancement

Python 3 requis (`python --version` pour vérifier).

```bash
# 1. Aller dans le dossier du projet
cd sentinelle-web

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

Ouvrir ensuite **http://127.0.0.1:5001** dans le navigateur.

## 🧪 Jeux de tests


| Adresse | Score | Verdict |
|---|---|---|
| `https://www.google.com` | 100 | Probablement sûr|
| `https://paypa1.com` | 60 | Prudence |
| `http://google.com@192.168.0.25` | 25 | Risqué |
| `login.secure.update.paypa1-secure-verify.xyz/verify-colis-remboursement-urgent-connexion-securisee-1234567890` | 0 | Risqué |
| `https://bit.ly/3xYz12` | 70 | Prudence |
| `https://xn--pple-43d.com` | 50 | Prudence |

## 🗂️ Structure du projet

```
sentinelle-web/
├── app.py                       ← serveur Flask + logique d'analyse (12 règles)
├── chargement.py                ← chargement des listes de référence
├── requirements.txt             ← dépendances (Flask, requests)
├── donnees/
│   └── extensions.txt           ← extensions souvent abusées, ex .xyz (règle 6)
│   └── marques.json             ← marques connues et leurs domaines officiels (règle 4)
│   └── marques_mot_entier.txt   ← marques aussi mais mots courants, mot entier seulement
│   └── messages.json            ← textes de l'interface en Français et Anglais
│   └── mots_suspects.txt        ← mots typiques des arnaques (règle 9) 
│   └── raccourcisseurs.txt      ← raccourcisseurs connus, ex. bit.ly (règle 11)
│   └── sites_confiance.txt      ← base de données pour sites de confiance
│   └── suffixes.txt             ← suffixes doubles, ex. co.uk
├── static/
│   └── style.css                ← feuille de style partagée (marine/or)
└── templates/
    ├── index.html               ← page du formulaire + resultat

```

## 🛠️ Technologies

- Python 3 + Flask (routes, gabarits Jinja2, sessions)
- HTML / CSS maison (variables CSS, adaptatif)

## 👤 Contexte

Projet réalisé en vue d'**HackDécouverte 2026** (hackathon, 14 novembre 2026, Université Concordia, Montréal).

**Auteur :** 
Olivier Montpetit, Walid Guetaf, Alex Jandali, Allassane Kamara

## 🔒 Limites honnêtes

- L'application détecte des *signaux* d'hameçonnage : elle ne garantit jamais qu'un site est légitime.
- L'historique vit dans un cookie de session : il disparaît si les cookies sont effacés et ne suit pas d'un appareil à l'autre. Un vrai produit le stockerait côté serveur, dans une base de données.
