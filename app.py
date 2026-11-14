# Sentinelle Web — projet HackDécouverte
# Une mini application Flask qui analyse une URL et lui donne un score de risque.
#
# Lancer :  python3 app.py   puis ouvrir http://127.0.0.1:5001

import ipaddress
import os
import re
from datetime import datetime, timezone
from urllib.parse import urlparse

import requests
from flask import Flask, jsonify, redirect, render_template, request, session, url_for

from chargement import charger_liste, charger_marques, charger_messages


<<<<<<< HEAD
from chargement import charger_liste, charger_marques, charger_messages

=======
>>>>>>> 2dfed7065c32aa43c21230dafb312a0d11f8a3cb
# ---------------------------------------------------------------------------
# 1. LISTES DE RÉFÉRENCE
#    Elles sont dans le dossier « donnees/ ».
#    Pour ajouter une marque, un mot ou une extension, modifie ces fichiers.
# ---------------------------------------------------------------------------

MARQUES = charger_marques("marques.json")
MOTS_SUSPECTS = charger_liste("mots_suspects.txt")
EXTENSIONS_SUSPECTES = charger_liste("extensions.txt")
RACCOURCISSEURS = charger_liste("raccourcisseurs.txt")
SUFFIXES_DOUBLES = charger_liste("suffixes.txt")
<<<<<<< HEAD
MESSAGES = charger_messages("messages.json")   # textes en français et en anglais
=======
MARQUES_MOT_ENTIER = set(charger_liste("marques_mot_entier.txt"))
MESSAGES = charger_messages("messages.json")   # textes en français et en anglais

# --- BASE DE DONNÉES DES SITES DE CONFIANCE ---------------------------------
# = les sites de sites_confiance.txt + les domaines officiels de marques.json
SITES_CONFIANCE = set(charger_liste("sites_confiance.txt"))
for domaines_officiels in MARQUES.values():
    SITES_CONFIANCE.update(domaines_officiels)

# MODE_STRICT = True  : un site ABSENT de la base est considéré comme une FRAUDE.
# MODE_STRICT = False : un site absent est seulement analysé avec les règles.
MODE_STRICT = True

# Vérification au démarrage : si 0 marque est chargée, marques.json a un problème
print(f"  ✔ {len(MARQUES)} marques chargées")
print(f"  ✔ {len(SITES_CONFIANCE)} sites dans la base de confiance (mode strict : {'oui' if MODE_STRICT else 'non'})")
if not MARQUES:
    print("  ❌ AUCUNE marque chargée : vérifie donnees/marques.json (virgules, guillemets, accolades)")
>>>>>>> 2dfed7065c32aa43c21230dafb312a0d11f8a3cb

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "cle-d-entrainement-sentinelle")


def traduire(langue, cle, **valeurs):
    """Retourne un message dans la bonne langue (« fr » ou « en »).
    Ex. : traduire("en", "long", n=120) -> "The link is very long (120 characters)."
    """
    textes = MESSAGES.get(langue) or MESSAGES.get("fr", {})
    modele = textes.get(cle) or MESSAGES.get("fr", {}).get(cle, cle)
    return modele.format(**valeurs)


# ---------------------------------------------------------------------------
# 2. OUTILS
# ---------------------------------------------------------------------------

# Les fraudeurs remplacent souvent des lettres par des chiffres
# (paypa1, faceb00k, g00gle). On « traduit » ces chiffres en lettres
# avant de comparer, pour attraper les imitations déguisées.
TRADUCTION_LEET = str.maketrans({"0": "o", "1": "l", "3": "e", "4": "a",
                                 "5": "s", "7": "t", "$": "s"})


def site_de_confiance(domaine):
    """Retourne le site de la base qui correspond au domaine, ou None.
    Ex. : « mail.google.com » -> « google.com » ; « google.com.faux.xyz » -> None
    """
    for site in SITES_CONFIANCE:
        if domaine == site or domaine.endswith("." + site):
            return site
    return None


def domaine_est_officiel(domaine, officiels):
    """Vrai si le domaine EST un domaine officiel de la marque,
    ou un de ses sous-domaines légitimes (ex. www.paypal.com)."""
    for officiel in officiels:
        if domaine == officiel or domaine.endswith("." + officiel):
            return True
    return False


def marque_imitee(domaine):
    """Retourne le nom de la marque imitée, ou None si tout est beau."""
    # D'abord : si c'est le site officiel d'UNE des marques, ce n'est pas une imitation
    if any(domaine_est_officiel(domaine, officiels) for officiels in MARQUES.values()):
        return None

    domaine_traduit = domaine.translate(TRADUCTION_LEET)
    morceaux = re.split(r"[.-]", domaine_traduit)          # « paypal-securite.com » -> ["paypal", "securite", "com"]
    # On teste les noms les plus longs d'abord (« canadiantire » avant « canada »)
    for marque in sorted(MARQUES, key=len, reverse=True):
        if len(marque) <= 4 or marque in MARQUES_MOT_ENTIER:
            trouve = marque in morceaux                     # marque courte : mot entier seulement (évite « bell » dans « isabelle »)
        else:
            trouve = marque in domaine_traduit.replace("-", "")
        if trouve:
            return marque
    return None


def distance_levenshtein(a, b):
    """Nombre de lettres à changer/ajouter/enlever pour passer de a à b.
    Ex. : distance_levenshtein("desjardlns", "desjardins") = 1
    """
    if len(a) < len(b):
        a, b = b, a
    precedente = list(range(len(b) + 1))
    for i, ca in enumerate(a, start=1):
        ligne = [i]
        for j, cb in enumerate(b, start=1):
            ligne.append(min(precedente[j] + 1, ligne[j - 1] + 1,
                             precedente[j - 1] + (ca != cb)))
        precedente = ligne
    return precedente[-1]


def faute_de_frappe(domaine):
    """Repère les imitations par faute de frappe (ex. « desjardlns »).
    Retourne (morceau, marque) ou None."""
    for morceau in re.split(r"[.-]", domaine):
        for marque in MARQUES:
            if len(marque) >= 6 and marque not in MARQUES_MOT_ENTIER and morceau != marque \
                    and abs(len(morceau) - len(marque)) <= 1 \
                    and distance_levenshtein(morceau, marque) == 1:
                return morceau, marque
    return None


def domaine_principal(hote):
    """« login.secure.paypal.com » -> « paypal.com »"""
    for suffixe in sorted(SUFFIXES_DOUBLES, key=len, reverse=True):
        if hote.endswith("." + suffixe):
            reste = hote[: -(len(suffixe) + 1)]
            return reste.split(".")[-1] + "." + suffixe
    parties = hote.split(".")
    return ".".join(parties[-2:]) if len(parties) >= 2 else hote


def est_adresse_ip(hote):
    try:
        ipaddress.ip_address(hote.strip("[]"))
        return True
    except ValueError:
        return False


def age_du_domaine(domaine):
    """Âge du domaine en jours (service public RDAP), ou None si inconnu."""
    try:
        r = requests.get(f"https://rdap.org/domain/{domaine}", timeout=6)
        if r.status_code != 200:
            return None
        for evenement in r.json().get("events", []):
            if evenement.get("eventAction") == "registration":
                date = datetime.fromisoformat(evenement["eventDate"].replace("Z", "+00:00"))
                return (datetime.now(timezone.utc) - date).days
    except (requests.RequestException, ValueError, KeyError):
        pass
    return None


# ---------------------------------------------------------------------------
# 3. L'ANALYSE
# ---------------------------------------------------------------------------

def analyser_url(url, langue="fr"):
    """Retourne (score, raisons, infos, dans_la_base) :
    - score de 0 (très risqué) à 100 (sûr)
    - raisons : liste de {"points", "niveau", "message"} en langage clair
    - infos : renseignements neutres (domaine, âge…)
    - dans_la_base : True si le site est dans la base de confiance
    """
    score = 100
    raisons = []
    infos = []

    def t(cle, **valeurs):
        return traduire(langue, cle, **valeurs)

    def retirer(points, message):
        """Enlève des points au score et note la raison."""
        nonlocal score
        score -= points
        niveau = "danger" if points >= 25 else "attention"
        raisons.append({"points": points, "niveau": niveau, "message": message})

    # Si l'utilisateur n'a pas mis de schéma (http/https), on en ajoute un
    # pour que urlparse puisse bien découper l'adresse.
    url_analysee = url if "://" in url else "http://" + url
    morceaux = urlparse(url_analysee)
    domaine = (morceaux.hostname or "").lower()  # ex. "www.paypa1.com" (sans le chemin)

    if not domaine or ("." not in domaine and not est_adresse_ip(domaine)):
        return 0, [{"points": 100, "niveau": "danger", "message": t("invalide")}], [], False

    principal = domaine_principal(domaine)

    # --- ÉTAPE 0 : le site est-il dans la base de données de confiance ?
    site = site_de_confiance(domaine)
    # Un lien raccourci (bit.ly/abc, tinyurl.com/xyz) cache sa vraie destination :
    # même si le raccourcisseur est connu, on ne fait pas confiance au lien.
    est_raccourcisseur = (domaine in RACCOURCISSEURS or principal in RACCOURCISSEURS
                          or site in ("bitly.com", "tinyurl.com")) \
        and morceaux.path not in ("", "/")
    if site and not est_raccourcisseur:
        infos.append(t("domaine", domaine=principal))
        infos.append(t("confiance", site=site))
        return 100, [], infos, True
    if est_raccourcisseur:
        retirer(30, t("raccourci_confiance"))
    extension = domaine.rsplit(".", 1)[-1]
    infos.append(t("domaine", domaine=principal))

    # --- Règle 1 : connexion non chiffrée
    if morceaux.scheme != "https":
        retirer(10, t("https"))

    # --- Règle 2 : adresse IP au lieu d'un nom
    if est_adresse_ip(domaine):
        retirer(35, t("ip"))

    # --- Règle 3 : lien très long
    if len(url_analysee) > 100:
        retirer(10, t("long", n=len(url_analysee)))

    # --- Règle 4 : imitation d'une marque
    marque = marque_imitee(domaine)
    if marque:
        retirer(40, t("contient_marque", marque=marque))
    else:
        typo = faute_de_frappe(domaine)
        if typo:
            retirer(40, t("typo", imitation=typo[0], marque=typo[1]))
    est_officiel = any(domaine_est_officiel(domaine, off) for off in MARQUES.values())
    if est_officiel:
        infos.append(t("officiel"))

    # --- Règle 4 bis : marque cachée dans le CHEMIN du lien
    # ex. « secure-login.com/paypal/verify » : le site n'est pas PayPal,
    # mais le lien essaie de le faire croire.
    if not marque and not est_officiel:
        chemin = (morceaux.path + " " + morceaux.query).lower().translate(TRADUCTION_LEET)
        mots_chemin = re.split(r"[^a-z0-9]+", chemin)
        for nom_marque in MARQUES:
            mot_entier = len(nom_marque) <= 4 or nom_marque in MARQUES_MOT_ENTIER
            if (mot_entier and nom_marque in mots_chemin) or \
               (not mot_entier and nom_marque in chemin.replace("-", "")):
                retirer(25, t("mentionne_marque", marque=nom_marque))
                break

    # --- Règle 5 : « @ » dans l'adresse (cache la vraie destination)
    if "@" in url_analysee.split("://", 1)[1]:
        retirer(30, t("arobase"))

    # --- Règle 6 : extension souvent utilisée par les fraudeurs
    if extension in EXTENSIONS_SUSPECTES:
        retirer(20, t("extension", ext=extension))

    # --- Règle 7 : trop de sous-domaines
    nb_sous_domaines = domaine.count(".") - principal.count(".")
    if nb_sous_domaines >= 3:
        retirer(15, t("sous_domaines", n=nb_sous_domaines))

    # --- Règle 8 : plusieurs tirets
    if principal.count("-") >= 2:
        retirer(15, t("tirets"))

    # --- Règle 9 : mots typiques des arnaques
    url_minuscule = url_analysee.lower()
    mots = [m for m in MOTS_SUSPECTS if m in url_minuscule]
    if mots:
        retirer(min(30, 8 * len(mots)), t("mots", mots=", ".join(mots)))

    # --- Règle 10 : lettres d'autres alphabets (punycode)
    if "xn--" in domaine or any(ord(c) > 127 for c in domaine):
        retirer(35, t("caracteres"))

    # --- Règle 12 : domaine tout neuf
    if not est_adresse_ip(domaine):
        jours = age_du_domaine(principal)
        if jours is None:
            infos.append(t("age_inconnu"))
        else:
            infos.append(t("age", jours=jours, ans=jours // 365))
            if jours < 30:
                retirer(35, t("age_tres_recent", jours=jours))
            elif jours < 180:
                retirer(15, t("age_recent"))

    # --- Site absent de la base de confiance
    if MODE_STRICT:
        raisons.append({"points": 100, "niveau": "danger", "message": t("inconnu")})
        score = min(score, 20)            # toujours dans le rouge

    score = max(0, score)
    raisons.sort(key=lambda r: -r["points"])
    return score, raisons, infos, False


def verdict_pour(score, langue="fr", dans_la_base=True):
    """Traduit le score en verdict + couleur d'affichage."""
    if MODE_STRICT and not dans_la_base:
        return traduire(langue, "verdict_fraude"), "rouge"
    if score >= 80:
        couleur = "vert"
    elif score >= 50:
        couleur = "orange"
    else:
        couleur = "rouge"
    return traduire(langue, "verdict_" + couleur), couleur


def ajouter_historique(url, score, verdict, couleur):
    """Mission 3 — la nouvelle analyse va EN PREMIER, max 10 entrées,
    et on RÉASSIGNE la liste complète (sinon Flask ne voit pas le changement)."""
    historique = session.get("historique", [])
    historique = [{"url": url, "score": score, "verdict": verdict,
                   "couleur": couleur}] + historique
    session["historique"] = historique[:10]
    return session["historique"]


# ---------------------------------------------------------------------------
# 4. LES ROUTES
# ---------------------------------------------------------------------------

@app.after_request
def autoriser_page_locale(reponse):
    """Permet à index.html de parler au serveur même s'il est ouvert
    autrement (double-clic, Live Server…)."""
    # On renvoie l'origine exacte de la page (et non « * ») : c'est obligatoire
    # pour que le navigateur accepte d'envoyer le cookie de session (historique).
    origine = request.headers.get("Origin")
    if origine:
        reponse.headers["Access-Control-Allow-Origin"] = origine
        reponse.headers["Access-Control-Allow-Credentials"] = "true"
        reponse.headers["Vary"] = "Origin"
    reponse.headers["Access-Control-Allow-Headers"] = "Content-Type"
    reponse.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    return reponse


# Route 1 : la page d'accueil
@app.route("/")
def accueil():
    return render_template("index1.html")


# Route 2 : l'API utilisée par index.html (reçoit et renvoie du JSON)
@app.route("/api/analyser", methods=["POST", "OPTIONS"])
def api_analyser():
    if request.method == "OPTIONS":
        return "", 204
    donnees = request.get_json(silent=True) or {}
    url = (donnees.get("url") or "").strip()
    langue = donnees.get("langue", "fr")
    if langue not in MESSAGES:
        langue = "fr"
    enregistrer = donnees.get("historique", True)

    if not url:
        return jsonify({"erreur": traduire(langue, "vide")}), 400
    if len(url) > 2000:
        return jsonify({"erreur": traduire(langue, "trop_long")}), 400

    score, raisons, infos, dans_la_base = analyser_url(url, langue)
    verdict, couleur = verdict_pour(score, langue, dans_la_base)
    historique = ajouter_historique(url, score, verdict, couleur) if enregistrer \
        else session.get("historique", [])

    return jsonify({
        "url": url if "://" in url else "http://" + url,
        "score": score,
        "verdict": verdict,
        "couleur": couleur,
        "raisons": raisons,
        "infos": infos,
        "historique": historique,
    })


# Route 3 : lire l'historique (au chargement de la page)
@app.route("/api/historique")
def api_historique():
    return jsonify(session.get("historique", []))


# Route 4 : effacer l'historique
@app.route("/api/effacer-historique", methods=["POST"])
def api_effacer_historique():
    session.pop("historique", None)
    return jsonify([])


# Ancienne version (formulaire classique + resultat.html), gardée au cas où
@app.route("/analyser", methods=["POST"])
def analyser():
    url = request.form["url"]
    score, raisons, _, dans_la_base = analyser_url(url)
    verdict, couleur = verdict_pour(score, "fr", dans_la_base)
    historique = ajouter_historique(url, score, verdict, couleur)
    return render_template("resultat.html", url=url, score=score,
                           raisons=[r["message"] for r in raisons],
                           verdict=verdict, couleur=couleur,
                           historique=historique)


@app.route("/effacer-historique")
def effacer_historique():
    session.pop("historique", None)
    return redirect(url_for("accueil"))


# Point d'entrée : « python3 app.py » démarre le serveur de développement
PORT = 5001  # 5001 au lieu de 5000 : sur Mac, AirPlay occupe déjà le port 5000

if __name__ == "__main__":
    print(f"\n  ➜  Ouvre ce lien dans ton navigateur : http://127.0.0.1:{PORT}\n")
    app.run(debug=True, port=PORT)
