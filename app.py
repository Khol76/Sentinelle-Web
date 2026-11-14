# Sentinelle Web — projet HackDécouverte
# Une mini application Flask qui analyse une URL et lui donne un score de risque.


import ipaddress
import os
import re
from datetime import datetime, timezone
from urllib.parse import urlparse

import requests
from flask import Flask, jsonify, render_template, request

from chargement import charger_liste, charger_marques


# ---------------------------------------------------------------------------
# 1. LISTES DE RÉFÉRENCE
#    Elles sont maintenant dans le dossier « donnees/ ».
#    Pour ajouter une marque, un mot ou une extension, modifie ces fichiers.
# ---------------------------------------------------------------------------

MARQUES = charger_marques("marques.json")
MOTS_SUSPECTS = charger_liste("mots_suspects.txt")
EXTENSIONS_SUSPECTES = charger_liste("extensions.txt")
RACCOURCISSEURS = charger_liste("raccourcisseurs.txt")
SUFFIXES_DOUBLES = charger_liste("suffixes.txt")


app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "cle-d-entrainement-sentinelle")

# --- Règle 4 : les marques qu'on surveille et leurs domaines OFFICIELS -------
# Si l'adresse contient le nom d'une marque mais n'est PAS son domaine
# officiel, c'est un signal classique d'hameçonnage (ex. « paypa1.com »,
# « desjardins-securite.com »).






# Les fraudeurs remplacent souvent des lettres par des chiffres
# (paypa1, faceb00k, g00gle). On « traduit » ces chiffres en lettres
# avant de comparer, pour attraper les imitations déguisées.
TRADUCTION_LEET = str.maketrans({"0": "o", "1": "l", "3": "e", "4": "a",
                                 "5": "s", "7": "t", "$": "s"})
