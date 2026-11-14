"""
Fonctions qui chargent les listes de référence depuis le dossier « donnees/ ».

- Les fichiers .txt contiennent une valeur par ligne.
  Les lignes vides et celles qui commencent par # sont ignorées.
- marques.json contient les marques, rangées par catégorie.
"""

import json
import os

# Chemin du dossier « donnees », trouvé à partir de l'emplacement de ce fichier.
# Ça marche peu importe d'où tu lances app.py.
DOSSIER_DONNEES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "donnees")


def chemin(nom_fichier: str) -> str:
    """Retourne le chemin complet d'un fichier du dossier « donnees »."""
    return os.path.join(DOSSIER_DONNEES, nom_fichier)


def charger_liste(nom_fichier: str) -> list[str]:
    """Lit un fichier texte et retourne la liste de ses valeurs.

    Exemple : charger_liste("extensions.txt") -> ["xyz", "top", "click", ...]
    """
    try:
        with open(chemin(nom_fichier), encoding="utf-8") as fichier:
            valeurs = []
            for ligne in fichier:
                ligne = ligne.strip().lower()
                if ligne and not ligne.startswith("#"):
                    valeurs.append(ligne.lstrip("."))  # « .xyz » devient « xyz »
            return valeurs
    except FileNotFoundError:
        print(f"⚠️  Fichier introuvable : {chemin(nom_fichier)} (liste vide utilisée)")
        return []


def charger_marques(nom_fichier: str = "marques.json") -> dict[str, list[str]]:
    """Lit le fichier JSON des marques et retourne un seul dictionnaire.

    Le fichier est rangé par catégorie :
        { "Banques": { "desjardins": ["desjardins.com"] }, "Livraison": {...} }
    La fonction fusionne tout :
        { "desjardins": ["desjardins.com"], "purolator": ["purolator.com"], ... }
    """
    try:
        with open(chemin(nom_fichier), encoding="utf-8") as fichier:
            donnees = json.load(fichier)
    except FileNotFoundError:
        print(f"⚠️  Fichier introuvable : {chemin(nom_fichier)} (aucune marque chargée)")
        return {}
    except json.JSONDecodeError as erreur:
        print(f"❌ Erreur dans {nom_fichier}, ligne {erreur.lineno} : {erreur.msg}")
        print("   (vérifie les virgules, les guillemets et les accolades)")
        return {}

    marques = {}
    for nom, valeur in donnees.items():
        if isinstance(valeur, dict):          # c'est une catégorie
            for marque, domaines in valeur.items():
                marques[marque.lower()] = [d.lower() for d in domaines]
        else:                                 # marque sans catégorie
            marques[nom.lower()] = [d.lower() for d in valeur]
    return marques


def charger_messages(nom_fichier: str = "messages.json") -> dict[str, dict[str, str]]:
    """Lit les messages traduits : { "fr": {cle: texte}, "en": {cle: texte} }."""
    try:
        with open(chemin(nom_fichier), encoding="utf-8") as fichier:
            return json.load(fichier)
    except FileNotFoundError:
        print(f"⚠️  Fichier introuvable : {chemin(nom_fichier)}")
    except json.JSONDecodeError as erreur:
        print(f"❌ Erreur dans {nom_fichier}, ligne {erreur.lineno} : {erreur.msg}")
    return {"fr": {}, "en": {}}


# Petit test : lance « python3 chargement.py » pour voir ce qui est chargé
if __name__ == "__main__":
    print("Marques         :", len(charger_marques()))
    print("Mots suspects   :", len(charger_liste("mots_suspects.txt")))
    print("Extensions      :", len(charger_liste("extensions.txt")))
    print("Raccourcisseurs :", len(charger_liste("raccourcisseurs.txt")))
    print("Suffixes        :", len(charger_liste("suffixes.txt")))
    m = charger_messages()
    print("Messages        :", {langue: len(textes) for langue, textes in m.items()})
