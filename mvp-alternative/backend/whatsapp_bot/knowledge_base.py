"""
Base de connaissance technique BUTUS Repair.
Diagnostics, pièces, astuces pour chaque type d'appareil.
Adapté au contexte togolais (pièces disponibles à Lomé, solutions low-cost).
"""


DEVICE_KNOWLEDGE = {
    "ventilateur": {
        "name": "Ventilateur",
        "emoji": "🌀",
        "weight_kg": 3.5,
        "co2_per_unit_kg": 12.0,
        "common_issues": [
            {
                "symptom": "Ne tourne plus du tout",
                "causes": [
                    "Condensateur de démarrage HS (très courant au Togo à cause des variations de tension)",
                    "Moteur grillé (bobinage fondu)",
                    "Interrupteur de vitesse cassé",
                    "Fusible thermique interne claqué",
                ],
                "steps": [
                    "1. Vérifiez la prise et le câble d'alimentation avec un multimètre",
                    "2. Testez le condensateur (généralement 1.2µF à 3.5µF) — il doit faire 'bip' au testeur",
                    "3. Tournez l'hélice à la main : si elle bloque, le roulement est grippé",
                    "4. Si rien, le bobinage moteur est probablement mort → réparateur",
                ],
                "parts": [
                    "Condensateur ~ 1 500-3 000 FCFA (Quincaillerie Lomé, Avenue de la République)",
                    "Interrupteur 3 vitesses ~ 1 000 FCFA (marché de Lomé)",
                    "Roulement à billes ~ 1 000-2 000 FCFA (pièces auto détournées)",
                ],
                "self_repair": True,
            },
            {
                "symptom": "Tourne lentement ou par à-coups",
                "causes": [
                    "Condensateur fatigué (perte de capacité)",
                    "Palier du moteur sec (manque de graisse)",
                    "Vitesse mal réglée",
                ],
                "steps": [
                    "1. Nettoyez et graissez l'axe du moteur (huile de moteur ou WD-40)",
                    "2. Remplacez le condensateur (même valeur en µF)",
                    "3. Vérifiez que l'hélice n'est pas déformée",
                ],
                "parts": ["Condensateur ~ 2 000 FCFA", "Huile légère ~ 500 FCFA"],
                "self_repair": True,
            },
            {
                "symptom": "Bruit anormal (grincement, claquement)",
                "causes": ["Roulement usé", "Hélice desserrée ou déformée", "Objet étranger dans le moteur"],
                "steps": [
                    "1. Arrêtez immédiatement et débranchez",
                    "2. Vérifiez l'hélice : serrez la vis centrale",
                    "3. Si le bruit persiste, le roulement est à changer",
                ],
                "parts": ["Roulement ~ 1 500 FCFA", "Graisse silicone ~ 1 000 FCFA"],
                "self_repair": True,
            },
        ],
        "local_shops": [
            "Quincaillerie Moderne — Avenue de la République, Lomé",
            "Marché de Lomé — étage électricité",
            "Magasin SONA — Rue du Commerce",
        ],
        "tutorial_url": "https://www.youtube.com/results?search_query=r%C3%A9parer+ventilateur+%C3%A9lectrique",
    },
    "climatiseur": {
        "name": "Climatiseur",
        "emoji": "❄️",
        "weight_kg": 35.0,
        "co2_per_unit_kg": 180.0,
        "common_issues": [
            {
                "symptom": "Ne refroidit pas / ventile seulement",
                "causes": [
                    "Manque de gaz frigorigène (R32 ou R410A) — fuite lente",
                    "Condensateur du compresseur HS",
                    "Filtre à air obstrué",
                    "Thermostat défectueux",
                ],
                "steps": [
                    "⚠️ ATTENTION : Le gaz frigorigène et le compresseur 220V sont DANGEREUX",
                    "1. Éteignez et débranchez l'appareil",
                    "2. Nettoyez le filtre à l'eau savonneuse",
                    "3. Vérifiez que l'unité extérieure est propre et dégagée",
                    "4. Si rien, appelez un frigoriste — ne percez jamais les tubes de gaz",
                ],
                "parts": [
                    "Filtre neuf ~ 3 000-5 000 FCFA",
                    "Gaz R32 recharge ~ 15 000-25 000 FCFA (frigoriste)",
                    "Condensateur compresseur ~ 4 000-6 000 FCFA",
                ],
                "self_repair": False,
                "danger": True,
            },
            {
                "symptom": "Fuit de l'eau à l'intérieur",
                "causes": [
                    "Bac d'égouttement bouché",
                    "Tuyau d'évacuation plié ou obstrué",
                    "Filtre sale (gèle puis dégèle)",
                ],
                "steps": [
                    "1. Nettoyez le bac et le tuyau d'évacuation avec un fil de fer",
                    "2. Vérifiez que le tuyau d'évacuation est en pente vers l'extérieur",
                    "3. Nettoyez le filtre à air",
                ],
                "parts": ["Tuyau d'évacuation ~ 1 000 FCFA"],
                "self_repair": True,
            },
        ],
        "local_shops": [
            "Frigo Services Lomé — Boulevard du 13 Janvier",
            "Clim Plus Togo — Rue de la Kozah",
        ],
        "tutorial_url": None,
    },
    "refrigerateur": {
        "name": "Réfrigérateur / Congélateur",
        "emoji": "🧊",
        "weight_kg": 45.0,
        "co2_per_unit_kg": 210.0,
        "common_issues": [
            {
                "symptom": "Ne refroidit plus (moteur arrêté)",
                "causes": [
                    "Relais de démarrage HS (pièce la plus courante)",
                    "Thermostat défectueux",
                    "Compresseur grillé",
                    "Câble d'alimentation coupé",
                ],
                "steps": [
                    "⚠️ DANGER : débranchez toujours avant d'intervenir",
                    "1. Testez la prise avec une lampe pour confirmer le courant",
                    "2. Localisez le relais de démarrage (boîtier noir sur le compresseur)",
                    "3. Secouez le relais : si ça cliquette, il est probablement mort",
                    "4. Remplacez le relais (identique, disponible en boutique pièces frigo)",
                ],
                "parts": [
                    "Relais de démarrage ~ 3 000-5 000 FCFA",
                    "Thermostat ~ 4 000-7 000 FCFA",
                    "Gaz R600a recharge ~ 10 000-20 000 FCFA (frigoriste)",
                ],
                "self_repair": True,
            },
            {
                "symptom": "Fait du bruit mais ne refroidit pas",
                "causes": ["Compresseur qui tourne mais pas de gaz", "Gaz insuffisant (fuite)", "Évaporateur obstrué"],
                "steps": [
                    "1. Écoutez : si le compresseur tourne mais frigo chaud → gaz manquant",
                    "2. Regardez derrière : si givre excessif → dégivrez 24h puis réessayez",
                    "3. Si toujours chaud → appelez un frigoriste (recharge de gaz nécessaire)",
                ],
                "parts": ["Gaz R600a ~ 15 000 FCFA", "Dégivrage manuel : gratuit"],
                "self_repair": False,
                "danger": True,
            },
            {
                "symptom": "Givre excessif",
                "causes": ["Joint de porte abîmé", "Thermostat trop haut", "Porte mal fermée"],
                "steps": [
                    "1. Vérifiez le joint : fermez la porte sur un billet, s'il se retire facilement → joint HS",
                    "2. Nettoyez le joint à l'eau savonneuse",
                    "3. Dégivrez complètement 24h",
                ],
                "parts": ["Joint de porte ~ 5 000-10 000 FCFA", "Mastic silicone ~ 1 500 FCFA"],
                "self_repair": True,
            },
        ],
        "local_shops": [
            "Frigo Services Lomé",
            "Pièces Frigo Togo — Rue de la Gare",
        ],
        "tutorial_url": None,
    },
    "machine_laver": {
        "name": "Machine à laver",
        "emoji": "👕",
        "weight_kg": 55.0,
        "co2_per_unit_kg": 195.0,
        "common_issues": [
            {
                "symptom": "Ne s'allume pas / pas de courant",
                "causes": ["Carte électronique HS", "Fusible interne claqué", "Filtre anti-parasite brûlé", "Programmateur bloqué"],
                "steps": [
                    "⚠️ DANGER : condensation + 220V",
                    "1. Vérifiez la prise et le disjoncteur",
                    "2. Débranchez 10 minutes puis rebranchez (reset carte)",
                    "3. Si rien, la carte électronique est probablement morte → réparateur",
                ],
                "parts": ["Carte électronique ~ 15 000-40 000 FCFA", "Fusible ~ 500 FCFA"],
                "self_repair": False,
            },
            {
                "symptom": "Ne vidange pas / reste en eau",
                "causes": ["Filtre de vidange bouché", "Pompe de vidange HS", "Tuyau d'évacuation plié"],
                "steps": [
                    "1. Ouvrez le filtre (en bas à droite) — vidangez l'eau d'abord",
                    "2. Nettoyez le filtre : pièces, cheveux, pièces de monnaie",
                    "3. Vérifiez que la pompe tourne (écoutez un bourdonnement en cycle vidange)",
                ],
                "parts": ["Pompe de vidange ~ 8 000-15 000 FCFA"],
                "self_repair": True,
            },
            {
                "symptom": "Le tambour ne tourne pas",
                "causes": ["Courroie de traction cassée", "Charbons moteur usés", "Moteur grillé"],
                "steps": [
                    "1. Débranchez la machine",
                    "2. Retirez le panneau arrière",
                    "3. Vérifiez la courroie : si elle est détendue ou cassée → remplacez",
                    "4. Vérifiez les charbons : sortez-les du moteur, s'ils font <5mm → changez",
                ],
                "parts": [
                    "Courroie ~ 4 000-7 000 FCFA",
                    "Charbons moteur ~ 3 000-5 000 FCFA",
                    "Disponibles Quincaillerie SONA Lomé",
                ],
                "self_repair": True,
            },
        ],
        "local_shops": [
            "Quincaillerie SONA — Lomé",
            "Pièces Électro Togo — Boulevard Élective",
        ],
        "tutorial_url": None,
    },
    "television": {
        "name": "Téléviseur / Écran",
        "emoji": "📺",
        "weight_kg": 8.0,
        "co2_per_unit_kg": 85.0,
        "common_issues": [
            {
                "symptom": "Écran noir mais voyant allumé",
                "causes": ["Carte d'alimentation HS (condensateurs gonflés)", "Backlight (LED) mort", "Carte T-Con défectueuse"],
                "steps": [
                    "⚠️ DANGER : hautes tensions (condensateurs >300V)",
                    "1. Écoutez : y a-t-il du son ? Si oui → problème d'écran uniquement",
                    "2. Regardez avec une lampe de près : voyez-vous une image fantôme ?",
                    "3. Si oui : backlight HS (les LED ne s'allument pas)",
                ],
                "parts": [
                    "Condensateurs (lot de 10) ~ 2 000 FCFA",
                    "Kit LED backlight ~ 8 000-15 000 FCFA",
                    "Carte d'alimentation ~ 10 000-20 000 FCFA",
                ],
                "self_repair": False,
                "danger": True,
            },
            {
                "symptom": "S'allume puis s'éteint",
                "causes": ["Condensateurs fatigués (carte alim)", "Court-circuit sur une LED backlight", "Surchauffe"],
                "steps": [
                    "1. Débranchez 30 minutes (refroidissement)",
                    "2. Si le problème persiste : ouvrez (si vous êtes équipé) et vérifiez les condos",
                    "3. Condos bombés = à remplacer (c'est réparable)",
                ],
                "parts": ["Condensateurs ~ 2 000 FCFA"],
                "self_repair": False,
                "danger": True,
            },
        ],
        "local_shops": [
            "Électronique Lomé — Rue de la République",
            "TV Service Lomé — Marché de la Démocratie",
        ],
        "tutorial_url": "https://www.youtube.com/results?search_query=reparer+tv+led+noir+son",
    },
    "smartphone": {
        "name": "Smartphone / Tablette",
        "emoji": "📱",
        "weight_kg": 0.2,
        "co2_per_unit_kg": 45.0,
        "common_issues": [
            {
                "symptom": "Ne charge plus / charge lentement",
                "causes": ["Port de charge sale", "Câble ou chargeur HS", "Batterie dégradée", "Connecteur interne dessoudé"],
                "steps": [
                    "1. Nettoyez le port de charge avec un cure-dent (pas de métal !)",
                    "2. Essayez un autre câble et chargeur",
                    "3. Vérifiez : la batterie gonfle-t-elle ? Si oui, remplacez-la URGENCE (risque incendie)",
                ],
                "parts": [
                    "Batterie ~ 5 000-15 000 FCFA selon modèle",
                    "Câble USB ~ 1 000-2 500 FCFA",
                    "Chargeur mural ~ 2 500-5 000 FCFA",
                ],
                "self_repair": True,
            },
            {
                "symptom": "Écran cassé / ne s'affiche pas",
                "causes": ["Écran brisé (chute)", "Nappe de connexion desserrée", "LCD mort"],
                "steps": [
                    "1. Si l'écran est fissuré → remplacement nécessaire",
                    "2. Si écran noir mais téléphone vibre/ sonne → nappe ou LCD",
                    "3. Vous pouvez commander un écran de rechange sur AliExpress ou Marché de Lomé",
                ],
                "parts": [
                    "Écran de rechange ~ 8 000-50 000 FCFA selon modèle",
                    "Kit outillage ~ 3 000 FCFA",
                ],
                "self_repair": True,
            },
            {
                "symptom": "Ne s'allume plus du tout",
                "causes": ["Batterie complètement vide", "Bouton power HS", "Carte mère morte (chute ou eau)", "Eau dans le téléphone"],
                "steps": [
                    "1. Forcez le redémarrage : volume haut + power 10 secondes",
                    "2. Branchez 30 minutes sur chargeur mural (pas PC)",
                    "3. Si rien : probablement carte mère → réparateur smartphone",
                ],
                "parts": ["Batterie ~ 8 000 FCFA", "Nappe bouton power ~ 2 000 FCFA"],
                "self_repair": True,
            },
        ],
        "local_shops": [
            "Marché de Lomé — étage téléphonie",
            "iPhone Service Lomé — Boulevard du 13 Janvier",
            "Petit Marché de Bè — réparateurs smartphone",
        ],
        "tutorial_url": "https://www.youtube.com/results?search_query=r%C3%A9parer+smartphone+%C3%A9cran+noir",
    },
    "ordinateur": {
        "name": "Ordinateur / Laptop",
        "emoji": "💻",
        "weight_kg": 2.0,
        "co2_per_unit_kg": 120.0,
        "common_issues": [
            {
                "symptom": "Ne s'allume pas (pas de voyant)",
                "causes": ["Chargeur HS", "Batterie complètement vide", "Carte mère grillée", "Connecteur d'alimentation dessoudé"],
                "steps": [
                    "1. Testez le chargeur : une lumière sur le bloc ? Sinon, chargeur mort",
                    "2. Débranchez la batterie et branchez sur secteur uniquement",
                    "3. Essayez un autre chargeur compatible (même voltage)",
                    "4. Si toujours rien : carte mère probablement → réparateur",
                ],
                "parts": ["Chargeur universel ~ 7 000-12 000 FCFA", "Batterie ~ 15 000-30 000 FCFA"],
                "self_repair": True,
            },
            {
                "symptom": "Lent, plante, s'éteint tout seul",
                "causes": ["Disque dur défectueux", "RAM insuffisante", "Surchauffe (ventilateur poussiéreux)", "Virus"],
                "steps": [
                    "1. Nettoyez le ventilateur avec une bombe à air comprimé",
                    "2. Utilisez CrystalDiskInfo pour vérifier l'état du disque dur",
                    "3. Passez un antivirus (Windows Defender ou Malwarebytes gratuit)",
                    "4. Remplacez le disque dur par un SSD (la meilleure amélioration possible !)",
                ],
                "parts": [
                    "SSD 240 Go ~ 15 000-20 000 FCFA",
                    "RAM 8 Go ~ 12 000-18 000 FCFA",
                    "Pâte thermique ~ 2 000 FCFA",
                ],
                "self_repair": True,
            },
        ],
        "local_shops": [
            "Informatique Lomé — Boulevard de la République",
            "PC Service Togo — Rue de la Gare",
            "Marché de Lomé — étage informatique",
        ],
        "tutorial_url": "https://www.youtube.com/results?search_query=r%C3%A9parer+pc+portable+ne+s+allume+pas",
    },
    "audio": {
        "name": "Sonorisation / Audio",
        "emoji": "🔊",
        "weight_kg": 1.5,
        "co2_per_unit_kg": 20.0,
        "common_issues": [
            {
                "symptom": "Pas de son / son hachuré",
                "causes": ["Fil de haut-parleur coupé", "Cône du haut-parleur déchiré", "Amplificateur en protection", "Batterie faible (enceinte portable)"],
                "steps": [
                    "1. Vérifiez le câble Jack ou Bluetooth",
                    "2. Montez le volume progressivement",
                    "3. Si son hachuré : l'enceinte est probablement en fin de vie",
                    "4. Cône déchiré : colle à caoutchouc ou remplacement haut-parleur",
                ],
                "parts": [
                    "Haut-parleur de rechange ~ 5 000-20 000 FCFA",
                    "Colle néoprène ~ 1 000 FCFA",
                    "Câble Jack ~ 1 500 FCFA",
                ],
                "self_repair": True,
            },
            {
                "symptom": "S'allume mais pas de son (ampli)",
                "causes": ["Fusible interne claqué", "Transistors de sortie HS", "Relais de protection bloqué"],
                "steps": [
                    "⚠️ DANGER : hautes tensions >50V dans les amplis",
                    "1. Vérifiez le fusible (sur le panneau arrière ou à l'intérieur)",
                    "2. Si fusible fondu → remplacez par un identique",
                    "3. Si le nouveau fusible fond aussi → transistor de sortie HS → réparateur",
                ],
                "parts": ["Fusible ~ 500 FCFA", "Transistor de puissance ~ 2 000-5 000 FCFA"],
                "self_repair": False,
                "danger": True,
            },
        ],
        "local_shops": [
            "Sonorisation Lomé — Rue de la République",
            "Marché de Lomé — étage électronique",
        ],
        "tutorial_url": "https://www.youtube.com/results?search_query=r%C3%A9parer+enceinte+bluetooth+pas+de+son",
    },
    "electromenager": {
        "name": "Petit électroménager",
        "emoji": "🔌",
        "weight_kg": 1.2,
        "co2_per_unit_kg": 8.0,
        "common_issues": [
            {
                "symptom": "Ne chauffe plus (fer, grille-pain, bouilloire)",
                "causes": ["Résistance chauffante coupée", "Thermostat HS", "Fusible thermique claqué", "Câble interne cassé"],
                "steps": [
                    "1. Vérifiez le câble et la prise",
                    "2. Ouvrez l'appareil et testez la résistance au multimètre",
                    "3. Résistance coupée → remplacez-la (pièce standard)",
                    "4. Fusible thermique → testez au multimètre",
                ],
                "parts": [
                    "Résistance chauffante ~ 2 000-5 000 FCFA",
                    "Fusible thermique ~ 500 FCFA",
                    "Thermostat ~ 2 000-4 000 FCFA",
                ],
                "self_repair": True,
            },
            {
                "symptom": "Moteur ne tourne plus (mixeur, aspirateur)",
                "causes": ["Balais moteur usés", "Roulement grippé", "Interrupteur de sécurité bloqué", "Électronique de puissance HS"],
                "steps": [
                    "1. Vérifiez que l'interrupteur de sécurité est bien enfoncé (mixeurs)",
                    "2. Nettoyez les pièces mobiles",
                    "3. Si le moteur bourdonne sans tourner → roulement ou condensateur",
                ],
                "parts": ["Condensateur ~ 1 500 FCFA", "Balais moteur ~ 1 000-2 000 FCFA"],
                "self_repair": True,
            },
        ],
        "local_shops": [
            "Quincaillerie Moderne Lomé",
            "Marché de Lomé — étage électricité",
        ],
        "tutorial_url": None,
    },
    "autre": {
        "name": "Autre appareil",
        "emoji": "🔧",
        "weight_kg": 5.0,
        "co2_per_unit_kg": 25.0,
        "common_issues": [
            {
                "symptom": "Panne générale",
                "causes": ["Alimentation électrique instable", "Pièce électronique grillée", "Câble ou connecteur oxydé", "Usure normale"],
                "steps": [
                    "1. Vérifiez la source d'alimentation (prise, batterie)",
                    "2. Inspectez visuellement : composants brûlés, condensateurs gonflés",
                    "3. Cherchez des pièces de rechange compatibles",
                    "4. Si pas de diagnostic clair → contactez un réparateur BUTUS",
                ],
                "parts": None,
                "self_repair": False,
            }
        ],
        "local_shops": [],
        "tutorial_url": None,
    },
}


def get_knowledge(device_type: str) -> dict | None:
    """Retourne la fiche technique pour un type d'appareil."""
    device_type = device_type.lower().replace("é", "e").replace("è", "e")
    mapping = {
        "ventilateur": "ventilateur",
        "ventilo": "ventilateur",
        "climatiseur": "climatiseur",
        "clim": "climatiseur",
        "refrigerateur": "refrigerateur",
        "frigo": "refrigerateur",
        "congelateur": "refrigerateur",
        "machine a laver": "machine_laver",
        "lave-linge": "machine_laver",
        "lave linge": "machine_laver",
        "television": "television",
        "tv": "television",
        "ecran": "television",
        "tele": "television",
        "smartphone": "smartphone",
        "telephone": "smartphone",
        "portable": "smartphone",
        "iphone": "smartphone",
        "tablette": "smartphone",
        "ordinateur": "ordinateur",
        "pc": "ordinateur",
        "laptop": "ordinateur",
        "macbook": "ordinateur",
        "audio": "audio",
        "enceinte": "audio",
        "sono": "audio",
        "haut parleur": "audio",
        "haut-parleur": "audio",
        "electromenager": "electromenager",
        "mixeur": "electromenager",
        "fer a repasser": "electromenager",
        "grille pain": "electromenager",
        "aspirateur": "electromenager",
        "bouilloire": "electromenager",
    }
    key = mapping.get(device_type)
    if key and key in DEVICE_KNOWLEDGE:
        return DEVICE_KNOWLEDGE[key]
    # Fallback : chercher par mot-clé
    for k, v in DEVICE_KNOWLEDGE.items():
        if device_type in v["name"].lower():
            return v
    return None


def get_symptom_diagnosis(device_key: str, symptom_keywords: list[str]) -> list[dict]:
    """Trouve les diagnostiques correspondant aux symptômes décrits."""
    kb = get_knowledge(device_key)
    if not kb:
        return []

    matches = []
    for issue in kb.get("common_issues", []):
        symptom = issue.get("symptom", "").lower()
        # Chercher des mots-clés dans le symptôme
        for kw in symptom_keywords:
            if kw.lower() in symptom:
                matches.append(issue)
                break

    return matches


def format_issue_response(issue: dict, device_name: str, emoji: str) -> str:
    """Formate une réponse de diagnostic en texte WhatsApp."""
    lines = [
        f"{emoji} *{device_name}* — {issue['symptom']}",
        "",
        "*Causes possibles :*",
    ]
    for c in issue.get("causes", []):
        lines.append(f"  • {c}")

    lines.append("")
    lines.append("*À faire :*")
    for s in issue.get("steps", []):
        lines.append(f"  {s}")

    parts = issue.get("parts")
    if parts:
        lines.append("")
        lines.append("*Pièces nécessaires (prix indicatifs) :*")
        for p in parts:
            lines.append(f"  • {p}")

    lines.append("")
    if issue.get("danger"):
        lines.append("⚠️ *ATTENTION : intervention dangereuse* — préférez un réparateur")
    elif issue.get("self_repair"):
        lines.append("✅ *Réparable par vous-même* avec des outils de base")
    else:
        lines.append("🔧 *Faites appel à un réparateur BUTUS*")

    return "\n".join(lines)
