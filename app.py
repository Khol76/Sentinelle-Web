# Sentinelle Web — projet HackDécouverte
# Une mini application Flask qui analyse une URL et lui donne un score de risque.


from flask import Flask, redirect, render_template, request, session, url_for
from urllib.parse import urlparse
import ipaddress
import os
<<<<<<< HEAD
=======
import marque
>>>>>>> d5f14f56d307e545374dcbad659134ec904b190f


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



def domaine_est_officiel(domaine, officiels):
    """Vrai si le domaine EST un domaine officiel de la marque,
    ou un de ses sous-domaines légitimes (ex. www.paypal.com)."""
    for officiel in officiels:
        if domaine == officiel or domaine.endswith("." + officiel):
            return True
    return False


def marque_imitee(domaine):
    """Retourne le nom de la marque imitée, ou None si tout est beau."""
    domaine_traduit = domaine.translate(TRADUCTION_LEET)
    for marque, officiels in MARQUES.items():
        if marque in domaine_traduit and not domaine_est_officiel(domaine, officiels):
            return marque
    return None


def analyser_url(url):
    """Retourne (score, raisons) : score de 0 (très risqué) à 100 (sûr),
    et la liste des raisons en langage clair."""
    score = 100
    raisons = []

 """a mettre ici les regles"""



def verdict_pour(score):
    """Traduit le score en verdict + couleur d'affichage."""
    if score >= 80:
        return "Probablement sûr", "vert"
    if score >= 50:
        return "Prudence", "orange"
    return "Risqué", "rouge"



# Route 1 : la page d'accueil, qui affiche le formulaire
@app.route("/")
def accueil():
    return render_template("index.html")


# Route 2 : reçoit le formulaire (méthode POST) et affiche le résultat
@app.route("/analyser", methods=["POST"])
def analyser():
    url = request.form["url"]          # le champ nommé "url" du formulaire
    score, raisons = analyser_url(url)  # notre logique Python ordinaire
    verdict, couleur = verdict_pour(score)
    # Mission 3 — la nouvelle analyse va EN PREMIER, max 10 entrées,
    # et on RÉASSIGNE la liste complète (le piège expliqué plus haut).
    historique = session.get("historique", [])
    historique = [{"url": url, "score": score, "verdict": verdict,
                   "couleur": couleur}] + historique
    session["historique"] = historique[:10]

    return render_template("resultat.html", url=url, score=score,
                           raisons=raisons, verdict=verdict, couleur=couleur,
                           historique=session["historique"])

@app.route("/effacer-historique")
def effacer_historique():
    session.pop("historique", None)
    return redirect(url_for("accueil"))

# Point d'entrée : « python app.py » démarre le serveur de développement
if __name__ == "__main__":
    app.run(debug=True)
