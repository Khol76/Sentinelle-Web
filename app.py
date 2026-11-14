# Sentinelle Web — projet HackDécouverte
# Une mini application Flask qui analyse une URL et lui donne un score de risque.


from flask import Flask, redirect, render_template, request, session, url_for
from urllib.parse import urlparse
import ipaddress
import os
import extentions
import marque
import suffixe

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
=======
>>>>>>> 0e6f12a0db4bac0a9e294e28891391c0328eb744

