# Sentinelle Web — projet HackDécouverte
# Une mini application Flask qui analyse une URL et lui donne un score de risque.


from flask import Flask, redirect, render_template, request, session, url_for
from urllib.parse import urlparse
import ipaddress
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "cle-d-entrainement-sentinelle")

# --- Règle 4 : les marques qu'on surveille et leurs domaines OFFICIELS -------
# Si l'adresse contient le nom d'une marque mais n'est PAS son domaine
# officiel, c'est un signal classique d'hameçonnage (ex. « paypa1.com »,
# « desjardins-securite.com »).

MARQUES = 