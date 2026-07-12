"""
Catalogue de pièces détachées BUTUS Pièces (Pilier 2).
Pièces issues d'invendus neufs, reconditionnées à Lomé.
Adapté au contexte togolais (prix FCFA, stock local).
"""


# Catalogue des pièces détachées disponibles
# Chaque pièce : nom, types d'appareils compatibles, prix FCFA, stock, lieu, tuto
PARTS_CATALOG = [
    # === VENTILATEURS ===
    {
        "id": "P-VENT-001",
        "name": "Condensateur de démarrage 2µF",
        "device_types": ["ventilateur", "ventilo"],
        "price_fcfa": 2000,
        "stock": 25,
        "location": "Atelier BUTUS — Akodesséwa",
        "tutorial": "https://www.youtube.com/results?search_query=changer+condensateur+ventilateur",
        "description": "Pour ventilateur qui ne démarre plus ou tourne lentement.",
    },
    {
        "id": "P-VENT-002",
        "name": "Condensateur 3.5µF",
        "device_types": ["ventilateur", "ventilo", "climatiseur", "clim"],
        "price_fcfa": 2500,
        "stock": 18,
        "location": "Atelier BUTUS — Akodesséwa",
        "tutorial": "https://www.youtube.com/results?search_query=condensateur+ventilateur+3.5uf",
        "description": "Condensateur standard pour gros ventilateurs et climatiseurs.",
    },
    {
        "id": "P-VENT-003",
        "name": "Roulement à billes 608ZZ",
        "device_types": ["ventilateur", "ventilo"],
        "price_fcfa": 1500,
        "stock": 40,
        "location": "Quincaillerie Moderne — Avenue République",
        "tutorial": "",
        "description": "Roulement pour axe moteur bruyant.",
    },
    {
        "id": "P-VENT-004",
        "name": "Interrupteur 3 vitesses",
        "device_types": ["ventilateur", "ventilo"],
        "price_fcfa": 1200,
        "stock": 30,
        "location": "Marché de Lomé — étage électricité",
        "tutorial": "",
        "description": "Commutateur de vitesse pour ventilateur sur pied.",
    },
    # === RÉFRIGÉRATEURS / CONGÉLATEURS ===
    {
        "id": "P-FRIG-001",
        "name": "Relais de démarrage (boîtier noir)",
        "device_types": ["refrigerateur", "frigo", "congelateur"],
        "price_fcfa": 3500,
        "stock": 15,
        "location": "Atelier BUTUS — Akodesséwa",
        "tutorial": "https://www.youtube.com/results?search_query=relais+demarrage+compresseur+frigo",
        "description": "Pour frigo qui ne démarre plus (compresseur silencieux).",
    },
    {
        "id": "P-FRIG-002",
        "name": "Thermostat réfrigérateur",
        "device_types": ["refrigerateur", "frigo", "congelateur"],
        "price_fcfa": 5500,
        "stock": 8,
        "location": "Pièces Frigo Togo — Rue de la Gare",
        "tutorial": "",
        "description": "Régulateur de température pour frigo/congélateur.",
    },
    {
        "id": "P-FRIG-003",
        "name": "Joint de porte frigorifique",
        "device_types": ["refrigerateur", "frigo", "congelateur"],
        "price_fcfa": 7000,
        "stock": 12,
        "location": "Pièces Frigo Togo — Rue de la Gare",
        "tutorial": "",
        "description": "Joint magnétique pour éviter les fuites de froid.",
    },
    {
        "id": "P-FRIG-004",
        "name": "Résistance de dégivrage",
        "device_types": ["refrigerateur", "frigo"],
        "price_fcfa": 4500,
        "stock": 10,
        "location": "Atelier BUTUS — Akodesséwa",
        "tutorial": "",
        "description": "Pour frigo qui givre trop (dégivrage défectueux).",
    },
    # === CLIMATISEURS ===
    {
        "id": "P-CLIM-001",
        "name": "Condensateur compresseur 35µF",
        "device_types": ["climatiseur", "clim"],
        "price_fcfa": 6000,
        "stock": 6,
        "location": "Clim Plus Togo — Rue de la Kozah",
        "tutorial": "",
        "description": "Pour climatiseur qui ne refroidit plus (compresseur HS).",
    },
    {
        "id": "P-CLIM-002",
        "name": "Filtre à air split (lavable)",
        "device_types": ["climatiseur", "clim"],
        "price_fcfa": 3500,
        "stock": 20,
        "location": "Marché de Lomé — étage électricité",
        "tutorial": "",
        "description": "Filtre de rechange pour entretien régulier.",
    },
    {
        "id": "P-CLIM-003",
        "name": "Carte d'alimentation intérieure",
        "device_types": ["climatiseur", "clim"],
        "price_fcfa": 12000,
        "stock": 4,
        "location": "Clim Plus Togo — Rue de la Kozah",
        "tutorial": "",
        "description": "Carte électronique pour unité intérieure défectueuse.",
    },
    # === MACHINES À LAVER ===
    {
        "id": "P-LAV-001",
        "name": "Courroie de transmission",
        "device_types": ["machine_laver", "lave-linge", "lave linge"],
        "price_fcfa": 5000,
        "stock": 14,
        "location": "Quincaillerie SONA — Lomé",
        "tutorial": "https://www.youtube.com/results?search_query=changer+courroie+machine+a+laver",
        "description": "Pour tambour qui ne tourne plus.",
    },
    {
        "id": "P-LAV-002",
        "name": "Pompe de vidange",
        "device_types": ["machine_laver", "lave-linge", "lave linge"],
        "price_fcfa": 9000,
        "stock": 7,
        "location": "Quincaillerie SONA — Lomé",
        "tutorial": "",
        "description": "Pour machine qui ne vide plus l'eau.",
    },
    {
        "id": "P-LAV-003",
        "name": "Charbons moteur (lot de 2)",
        "device_types": ["machine_laver", "lave-linge", "lave linge"],
        "price_fcfa": 3500,
        "stock": 16,
        "location": "Quincaillerie SONA — Lomé",
        "tutorial": "",
        "description": "Pour moteur qui étincelle ou ne démarre pas.",
    },
    {
        "id": "P-LAV-004",
        "name": "Électrovanne d'eau",
        "device_types": ["machine_laver", "lave-linge", "lave linge"],
        "price_fcfa": 6500,
        "stock": 9,
        "location": "Quincaillerie SONA — Lomé",
        "tutorial": "",
        "description": "Pour machine qui ne se remplit pas d'eau.",
    },
    # === TÉLÉVISEURS / ÉCRANS ===
    {
        "id": "P-TV-001",
        "name": "Kit LED backlight 32 pouces",
        "device_types": ["television", "tv", "ecran", "tele"],
        "price_fcfa": 9000,
        "stock": 5,
        "location": "TV Service Lomé — Marché Démocratie",
        "tutorial": "",
        "description": "Pour TV qui s'allume puis s'éteint (backlight mort).",
    },
    {
        "id": "P-TV-002",
        "name": "Carte d'alimentation TV 32\"",
        "device_types": ["television", "tv", "ecran", "tele"],
        "price_fcfa": 11000,
        "stock": 3,
        "location": "Électronique Lomé — Rue République",
        "tutorial": "",
        "description": "Carte d'alim pour TV écran noir (condensateurs gonflés).",
    },
    # === SMARTPHONES / TABLETTES ===
    {
        "id": "P-TEL-001",
        "name": "Batterie smartphone universelle",
        "device_types": ["smartphone", "telephone", "portable", "iphone", "tablette"],
        "price_fcfa": 6500,
        "stock": 22,
        "location": "Marché de Lomé — étage téléphonie",
        "tutorial": "https://www.youtube.com/results?search_query=changer+batterie+smartphone",
        "description": "Batterie de rechange (préciser modèle à la commande).",
    },
    {
        "id": "P-TEL-002",
        "name": "Câble chargeur USB-C",
        "device_types": ["smartphone", "telephone", "portable", "tablette"],
        "price_fcfa": 1500,
        "stock": 50,
        "location": "Marché de Lomé — étage téléphonie",
        "tutorial": "",
        "description": "Câble de recharge rapide.",
    },
    {
        "id": "P-TEL-003",
        "name": "Écran de rechange (par modèle)",
        "device_types": ["smartphone", "telephone", "portable", "iphone", "tablette"],
        "price_fcfa": 15000,
        "stock": 8,
        "location": "iPhone Service Lomé — Bd 13 Janvier",
        "tutorial": "",
        "description": "Écran complet (préciser modèle à la commande).",
    },
    {
        "id": "P-TEL-004",
        "name": "Connecteur de charge",
        "device_types": ["smartphone", "telephone", "portable", "tablette"],
        "price_fcfa": 3000,
        "stock": 12,
        "location": "Marché de Lomé — étage téléphonie",
        "tutorial": "",
        "description": "Pour téléphone qui ne charge plus (port abîmé).",
    },
    # === ORDINATEURS ===
    {
        "id": "P-ORD-001",
        "name": "SSD 240 Go",
        "device_types": ["ordinateur", "pc", "laptop", "macbook"],
        "price_fcfa": 18000,
        "stock": 10,
        "location": "Informatique Lomé — Bd République",
        "tutorial": "https://www.youtube.com/results?search_query=installer+ssd+ordinateur+portable",
        "description": "Pour accélérer un PC lent (remplace disque dur).",
    },
    {
        "id": "P-ORD-002",
        "name": "Batterie laptop (par modèle)",
        "device_types": ["ordinateur", "pc", "laptop", "macbook"],
        "price_fcfa": 22000,
        "stock": 6,
        "location": "PC Service Togo — Rue de la Gare",
        "tutorial": "",
        "description": "Batterie de rechange (préciser modèle).",
    },
    {
        "id": "P-ORD-003",
        "name": "Barrette RAM 8 Go DDR4",
        "device_types": ["ordinateur", "pc", "laptop", "macbook"],
        "price_fcfa": 15000,
        "stock": 8,
        "location": "Informatique Lomé — Bd République",
        "tutorial": "",
        "description": "Pour PC qui rame (mémoire insuffisante).",
    },
    # === PETIT ÉLECTROMÉNAGER ===
    {
        "id": "P-EM-001",
        "name": "Résistance chauffante (bouilloire/fer)",
        "device_types": ["electromenager", "mixeur", "fer a repasser", "grille pain", "bouilloire"],
        "price_fcfa": 3000,
        "stock": 14,
        "location": "Quincaillerie Moderne — Avenue République",
        "tutorial": "",
        "description": "Pour petit électroménager qui ne chauffe plus.",
    },
    {
        "id": "P-EM-002",
        "name": "Fusible thermique 10A",
        "device_types": ["electromenager", "mixeur", "fer a repasser", "grille pain"],
        "price_fcfa": 500,
        "stock": 100,
        "location": "Marché de Lomé — étage électricité",
        "tutorial": "",
        "description": "Sécurité thermique pour petit électroménager.",
    },
    {
        "id": "P-EM-003",
        "name": "Balais moteur (lot de 2)",
        "device_types": ["electromenager", "aspirateur", "mixeur"],
        "price_fcfa": 2000,
        "stock": 20,
        "location": "Quincaillerie Moderne — Avenue République",
        "tutorial": "",
        "description": "Pour moteur qui ne démarre plus (aspirateur, mixeur).",
    },
    # === SONORISATION / AUDIO ===
    {
        "id": "P-AUD-001",
        "name": "Haut-parleur de remplacement 4Ω",
        "device_types": ["audio", "enceinte", "sono"],
        "price_fcfa": 4000,
        "stock": 12,
        "location": "Sonorisation Lomé — Rue République",
        "tutorial": "",
        "description": "Pour enceinte portable qui ne diffuse plus le son.",
    },
    {
        "id": "P-AUD-002",
        "name": "Câble Jack 3.5mm",
        "device_types": ["audio", "enceinte", "sono"],
        "price_fcfa": 1000,
        "stock": 40,
        "location": "Marché de Lomé — étage électronique",
        "tutorial": "",
        "description": "Câble audio auxiliaire.",
    },
]


def get_all_parts() -> list[dict]:
    """Retourne tout le catalogue."""
    return PARTS_CATALOG


DEVICE_CATEGORIES = [
    ("ventilateur", "Ventilateur"),
    ("refrigerateur", "Réfrigérateur / Congélateur"),
    ("climatiseur", "Climatiseur"),
    ("machine_laver", "Machine à laver"),
    ("television", "Téléviseur / Écran"),
    ("smartphone", "Smartphone / Tablette"),
    ("ordinateur", "Ordinateur / PC"),
    ("electromenager", "Petit électroménager"),
    ("audio", "Audio / Sonorisation"),
]


def get_device_categories() -> list[tuple[str, str]]:
    """Retourne la liste canonique (clé, libellé) des catégories d'appareils."""
    return DEVICE_CATEGORIES


def get_parts_by_device(device_type: str) -> list[dict]:
    """Retourne les pièces compatibles avec un type d'appareil."""
    device_type = device_type.lower().replace("é", "e").replace("è", "e")
    mapping = {
        "ventilateur": "ventilateur", "ventilo": "ventilateur",
        "climatiseur": "climatiseur", "clim": "climatiseur",
        "refrigerateur": "refrigerateur", "frigo": "refrigerateur", "congelateur": "refrigerateur",
        "machine a laver": "machine_laver", "lave-linge": "machine_laver", "lave linge": "machine_laver",
        "television": "television", "tv": "television", "ecran": "television", "tele": "television",
        "smartphone": "smartphone", "telephone": "smartphone", "portable": "smartphone", "iphone": "smartphone", "tablette": "smartphone",
        "ordinateur": "ordinateur", "pc": "ordinateur", "laptop": "ordinateur", "macbook": "ordinateur",
        "audio": "audio", "enceinte": "audio", "sono": "audio",
        "electromenager": "electromenager", "mixeur": "electromenager", "fer a repasser": "electromenager",
    }
    key = mapping.get(device_type)
    if not key:
        # recherche par mot-clé
        results = [p for p in PARTS_CATALOG if device_type in " ".join(p["device_types"])]
        return results

    return [p for p in PARTS_CATALOG if key in p["device_types"]]


def search_parts(query: str) -> list[dict]:
    """Recherche libre dans le catalogue."""
    query = query.lower().strip()
    results = []
    for p in PARTS_CATALOG:
        if (query in p["name"].lower() or
            query in p["description"].lower() or
            any(query in dt for dt in p["device_types"])):
            results.append(p)
    return results


def get_part_by_id(part_id: str) -> dict | None:
    """Retourne une pièce par son ID."""
    for p in PARTS_CATALOG:
        if p["id"] == part_id.upper():
            return p
    return None


def format_part_detail(part: dict) -> str:
    """Formate le détail d'une pièce en texte WhatsApp."""
    emoji = "🟢" if part["stock"] > 0 else "🔴"
    lines = [
        f"🔩 *{part['name']}*",
        "",
        f"📦 Réf : `{part['id']}`",
        f"💰 Prix : *{part['price_fcfa']} FCFA*",
        f"{emoji} Stock : {part['stock']} unité(s)",
        f"📍 Dispo : {part['location']}",
        "",
        f"📝 {part['description']}",
    ]
    if part.get("tutorial"):
        lines.append(f"🎓 Tutoriel : {part['tutorial']}")
    lines.append("")
    lines.append("Réponse :")
    lines.append("1️⃣ Réserver cette pièce")
    lines.append("2️⃣ Autres pièces pour cet appareil")
    lines.append("0️⃣ Menu principal")
    return "\n".join(lines)
