#! /bin/env python

import argparse
import csv
import re
import sys

import mechanicalsoup

PARSER = argparse.ArgumentParser("Récupère les offres ATER sur Galaxie "
                                 "et les écrit au format csv.")
PARSER.add_argument("-u", "--username", default=None,
                    help="Votre numéro de candidat Galaxie")
PARSER.add_argument("-p", "--password", default=None,
                    help="Votre mot de passe Galaxie")
ARGS = PARSER.parse_args()

URL_BASE = 'https://galaxie.enseignementsup-recherche.gouv.fr/'

FIELDS = {
    'etablissement': 'eta',
    'numero': 'numofr',
    'localisation': 'localofr',
    'section1': 'j_idt25',
    'quotite': 'j_idt76',
    'quotite_supp': 'j_idt77',
    'etat': 'j_idt80',
    'etat_supp': 'j_idt81',
    'profil_fr': 'profilofr',
    'profil_en': 'j_idt38',
    'euraxess': 'j_idt41_0_j_idt43',
    'mots_cles': 'j_idt108',
    'ufr': 'j_idt112',
    'ufr_ref': 'j_idt114',
    'labo1': 'j_idt118',
    'labo2': 'j_idt120',
    'labo3': 'j_idt122',
    'labo4': 'j_idt124',
    'labo5': 'j_idt126',
    'contact': 'j_idt48',
    'adresse_localisation': 'j_idt50',
    'codpost_localisation': 'j_idt52',
    'adresse_courrier': 'j_idt55',
    'codpost_courrier': 'j_idt59',
    'ville_courrier': 'j_idt61',
    'gestionnaire': 'j_idt63',
    'gestio_fonction': 'j_idt65',
    'gestio_tel1': 'j_idt67',
    'gestio_tel2': 'j_idt69',
    'gestio_fax': 'j_idt71',
    'gestio_mail': 'j_idt73',
    'date_prise_fonctions': 'j_idt83',
    'date_ouverture_cand': 'j_idt85',
    'date_cloture_cand': 'j_idt87',
    'date_decision': 'j_idt89',
    'date_maj': 'j_idt93',
    'dossier_papier': 'j_idt128_0_j_idt131',
    'dossier_application': 'j_idt128_1_j_idt131',
    'dossier_appli_url': 'j_idt128_1_j_idt135',
    'dossier_email': 'j_idt128_2_j_idt131',
    'dossier_email_adr': 'j_idt128_2_j_idt135',
    'dossier_num_phys': 'j_idt128_3_j_idt131',
    'dossier_aucun': 'j_idt128_4_j_idt131'
}

def get_position(browser):
    result = dict()
    for var_name, field_name in FIELDS.items():
        field = browser.get_current_page().find(attrs={'name': field_name})

        if not field:
            continue

        if field.get('value'):
            field_value = field.get('value')
        elif field.get('type') == "checkbox":
            field_value = 'oui' if field.get('checked') else 'non'
        elif field.name == 'textarea':
            field_value = field.text
        else:
            field_value = None

        result.update({var_name: field_value})
    return result

def get_url_from_onclick(elts):
    urls = []
    pattern = re.compile(r"openPopUp\(\\'(.*)\\'\)(;|',).*$")
    for elt in elts:
        match = pattern.search(elt.get('onclick'))
        if match:
            urls.append(URL_BASE + 'altaircand/' + match.group(1))
    return urls

def get_popup_id_from_onclick(elts):
    def extract_id(onclick):
        pattern = re.compile(r"\{'(.*)':.*\}")
        search = pattern.search(onclick)
        if search:
            return search.group(1)
        return None
    return [extract_id(e.get('onclick')) for e in elts]

if not ARGS.username or not ARGS.password:
    sys.exit("Veuillez donner vos identifiants Galaxie. "
             "Exécutez galaxie-scraper.py -h pour en savoir plus.")

print('Log into Galaxie...')
BROWSER = mechanicalsoup.StatefulBrowser()
BROWSER.open(URL_BASE + 'antares/can/astree/index.jsp')
BROWSER.select_form('form[name="connexion"]')
BROWSER['numecan'] = ARGS.username
BROWSER['pwd_RAW'] = ARGS.password
BROWSER.submit_selected()

if not BROWSER.get_current_page().find('span', 'textWarning'):
    sys.exit('La connexion à Galaxie a échoué. '
             'Vérifiez vos identifiants.')

print('Start Altair Session (getting CID)...')
BROWSER.open(URL_BASE + 'altaircand/home.seam')
BROWSER.open(URL_BASE + 'altaircand/ActureC021.seam?cid=' + BROWSER.get_url()[-5:])

print('Search for ATER positions...')
BROWSER.select_form('form[id="TdtCtuEdit"]')
BROWSER['TdtCtuEdit_section1'] = 3
BROWSER['TdtCtuEdit_section2'] = 18
BROWSER['TdtCtuEdit_section3'] = 48
BROWSER.submit_selected()

POSITIONS = list()

print('Get current open positions...')
CURRENT = BROWSER.links(title="Consulter l'appel à candidatures - nouvelle fenêtre")
CURRENT_URLS = get_url_from_onclick(CURRENT)
print(f'Found {len(CURRENT_URLS)} currently open positions.')

NEXT = BROWSER.links(id="choixAppel_lien_prochain_appel")
NEXT_URLS = get_url_from_onclick(NEXT)[0]

if CURRENT_URLS:
    for i, url in enumerate(CURRENT_URLS):
        print(f'Retrieving currently open position {i+1}/{len(CURRENT_URLS)}.')
        BROWSER.open(url)
        POSITIONS.append(get_position(BROWSER))

print('Get soon-to-be open positons...')
BROWSER.open(NEXT_URLS)
POPUP_LINKS = BROWSER.links(title="Consulter l'appel à candidatures - nouvelle fenêtre")
POPUP_IDS = get_popup_id_from_onclick(POPUP_LINKS)
print(f'Found {len(POPUP_LINKS)} soon-to-be open positions.')

for i, pop_id in enumerate(POPUP_IDS):
    if BROWSER.get_url() != NEXT_URLS:
        BROWSER.open(NEXT_URLS)

    print(f'Retrieving soon-to-be open position {i+1}/{len(POPUP_IDS)}.')
    BROWSER.select_form('form[id="j_idt20"]')
    BROWSER.new_control('hidden', pop_id, pop_id)
    BROWSER.submit_selected()

    POSITIONS.append(get_position(BROWSER))

print('Writing to file...')
with open('ater.csv', 'w') as csvfile:
    FIELDNAMES = FIELDS.keys()
    WRITER = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)

    WRITER.writeheader()
    for position in POSITIONS:
        WRITER.writerow(position)

print('All done!')
