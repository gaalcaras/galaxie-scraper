Ce script permet d'obtenir au format `.csv` (tableur) les postes d'ATER publiés
sur [la plateforme
Galaxie](https://galaxie.enseignementsup-recherche.gouv.fr/antares/can/astree/index.jsp).

# Installation

Le script est écrit en Python et utilise
[MechanicalSoup](https://mechanicalsoup.readthedocs.io/en/stable/index.html)
qu'il vous faudra peut-être
[installer](https://mechanicalsoup.readthedocs.io/en/stable/introduction.html#installation).

Exemple de processus d'installation :

```bash
git clone https://github.com/gaalcaras/galaxie-scraper.git
cd galaxie-scraper
chmod +x galaxie-scraper
pip install requirements.txt
```

# Utilisation

Le script s'utilise en ligne de commande :

```bash
./galaxie-scraper -u NUMÉRO_CANDIDAT -p MOTDEPASSE -s 4,19
```

Les deux premiers arguments correspondent à vos identifiants Galaxie,
l'argument `-s` aux sections qui vous intéressent (utilisez `./galaxie-scraper
-ls` pour obtenir une liste des sections disponibles).

Utilisez `./galaxie-scraper -h` pour obtenir l'aide de la commande.

# Remarques

Le but de ce script est simplement de fournir un document complémentaire
à Galaxie. Il est fourni sans aucune garantie, mais n'hésitez pas à ouvrir une
issue ou soumettre une *pull request* pour améliorer son fonctionnement.
