"""
Catalogue d'appareils reconditionnés BUTUS (Pilier 3).
Appareils testés, reconditionnés à Lomé, garantis.
"""

RECONDITIONED_CATALOG = [
    # === SMARTPHONES ===
    {
        "id": "RC-SMARTPHONE-001",
        "name": "iPhone XR 64 Go",
        "category": "smartphone",
        "price_fcfa": 85000,
        "original_price_fcfa": 180000,
        "warranty": "6 mois",
        "condition": "Très bon état",
        "description": "iPhone XR reconditionné, batterie >85%, écran d'origine.",
        "stock": 5,
        "location": "Atelier BUTUS — Akodesséwa",
    },
    {
        "id": "RC-SMARTPHONE-002",
        "name": "iPhone 11 128 Go",
        "category": "smartphone",
        "price_fcfa": 120000,
        "original_price_fcfa": 250000,
        "warranty": "6 mois",
        "condition": "Très bon état",
        "description": "iPhone 11 reconditionné, batterie >90%. Face ID OK.",
        "stock": 3,
        "location": "Atelier BUTUS — Akodesséwa",
    },
    {
        "id": "RC-SMARTPHONE-003",
        "name": "Samsung Galaxy A52 128 Go",
        "category": "smartphone",
        "price_fcfa": 65000,
        "original_price_fcfa": 150000,
        "warranty": "6 mois",
        "condition": "Bon état",
        "description": "Galaxy A52 reconditionné, écran légèrement rayé, fonctionne parfaitement.",
        "stock": 8,
        "location": "Atelier BUTUS — Akodesséwa",
    },
    {
        "id": "RC-SMARTPHONE-004",
        "name": "Tecno Camon 18 64 Go",
        "category": "smartphone",
        "price_fcfa": 45000,
        "original_price_fcfa": 90000,
        "warranty": "3 mois",
        "condition": "Bon état",
        "description": "Tecno Camon 18 reconditionné, batterie neuve installée.",
        "stock": 10,
        "location": "Atelier BUTUS — Akodesséwa",
    },
    {
        "id": "RC-SMARTPHONE-005",
        "name": "Infinix Hot 12 64 Go",
        "category": "smartphone",
        "price_fcfa": 38000,
        "original_price_fcfa": 75000,
        "warranty": "3 mois",
        "condition": "Bon état",
        "description": "Infinix Hot 12 reconditionné, écran et batterie d'origine, bon fonctionnement.",
        "stock": 12,
        "location": "Atelier BUTUS — Akodesséwa",
    },
    # === ORDINATEURS ===
    {
        "id": "RC-ORDINATEUR-001",
        "name": "HP EliteBook 840 G6 i5 8Go SSD256",
        "category": "ordinateur",
        "price_fcfa": 175000,
        "original_price_fcfa": 350000,
        "warranty": "12 mois",
        "condition": "Très bon état",
        "description": "PC portable professionnel reconditionné. Windows 11, SSD rapide.",
        "stock": 4,
        "location": "Informatique Lomé — Bd République",
    },
    {
        "id": "RC-ORDINATEUR-002",
        "name": "Lenovo ThinkPad T480 i5 8Go SSD256",
        "category": "ordinateur",
        "price_fcfa": 150000,
        "original_price_fcfa": 300000,
        "warranty": "12 mois",
        "condition": "Très bon état",
        "description": "ThinkPad reconditionné, clavier AZERTY, batterie 85%.",
        "stock": 6,
        "location": "Informatique Lomé — Bd République",
    },
    {
        "id": "RC-ORDINATEUR-003",
        "name": "Dell Latitude 5490 i5 8Go SSD256",
        "category": "ordinateur",
        "price_fcfa": 140000,
        "original_price_fcfa": 280000,
        "warranty": "6 mois",
        "condition": "Bon état",
        "description": "Dell Latitude reconditionné, léger, idéal pour le taf.",
        "stock": 5,
        "location": "Informatique Lomé — Bd République",
    },
    # === TÉLÉVISEURS ===
    {
        "id": "RC-TV-001",
        "name": "TV Samsung 32\" Smart LED",
        "category": "television",
        "price_fcfa": 85000,
        "original_price_fcfa": 170000,
        "warranty": "6 mois",
        "condition": "Bon état",
        "description": "TV Samsung Smart 32 pouces reconditionnée. Télécommande incluse.",
        "stock": 3,
        "location": "TV Service Lomé — Marché Démocratie",
    },
    {
        "id": "RC-TV-002",
        "name": "TV LG 43\" UHD 4K Smart",
        "category": "television",
        "price_fcfa": 150000,
        "original_price_fcfa": 300000,
        "warranty": "6 mois",
        "condition": "Très bon état",
        "description": "TV LG 43 pouces 4K reconditionnée. Parfait pour le salon.",
        "stock": 2,
        "location": "TV Service Lomé — Marché Démocratie",
    },
    # === ÉLECTROMÉNAGER ===
    {
        "id": "RC-EM-001",
        "name": "Réfrigérateur Samsung 230L",
        "category": "electromenager",
        "price_fcfa": 150000,
        "original_price_fcfa": 350000,
        "warranty": "12 mois",
        "condition": "Bon état",
        "description": "Réfrigérateur reconditionné, compresseur neuf, garanti 1 an.",
        "stock": 2,
        "location": "Pièces Frigo Togo — Rue de la Gare",
    },
    {
        "id": "RC-EM-002",
        "name": "Machine à laver Samsung 7kg",
        "category": "electromenager",
        "price_fcfa": 120000,
        "original_price_fcfa": 280000,
        "warranty": "6 mois",
        "condition": "Bon état",
        "description": "Lave-linge avant reconditionné, courroie et pompe neuves.",
        "stock": 1,
        "location": "Quincaillerie SONA — Lomé",
    },
]

CATEGORIES = [
    ("smartphone", "Smartphone / Tablette"),
    ("ordinateur", "Ordinateur / PC"),
    ("television", "Téléviseur / Écran"),
    ("electromenager", "Électroménager"),
]


def get_all_reconditioned() -> list[dict]:
    return RECONDITIONED_CATALOG


def get_by_category(category: str) -> list[dict]:
    category = category.lower().replace("é", "e")
    return [d for d in RECONDITIONED_CATALOG if d["category"] == category]


def search_reconditioned(query: str) -> list[dict]:
    query = query.lower().strip()
    results = []
    for d in RECONDITIONED_CATALOG:
        if (query in d["name"].lower() or
            query in d["description"].lower() or
            query in d["category"]):
            results.append(d)
    return results


def get_by_id(device_id: str) -> dict | None:
    for d in RECONDITIONED_CATALOG:
        if d["id"] == device_id.upper():
            return d
    return None


def format_detail(device: dict) -> str:
    savings = device["original_price_fcfa"] - device["price_fcfa"]
    savings_pct = int(savings / device["original_price_fcfa"] * 100)
    lines = [
        f"📱 *{device['name']}*",
        "",
        f"📦 Réf : `{device['id']}`",
        f"💰 Prix : *{device['price_fcfa']:,} FCFA*",
        f"🏷️ Prix neuf : ~~{device['original_price_fcfa']:,} FCFA~~ (−{savings_pct}%)",
        f"🎁 Économie : *{savings:,} FCFA*",
        f"🛡️ Garantie : {device['warranty']}",
        f"📊 État : {device['condition']}",
        f"📍 {device['location']}",
        "",
        f"📝 {device['description']}",
        "",
        "👉 *Contacter BUTUS* pour acheter ou réserver (tapez **contacter**).",
        "0️⃣ Menu principal",
    ]
    return "\n".join(lines)


def format_category_list(devices: list[dict], title: str) -> str:
    lines = [f"{title} ({len(devices)})\n"]
    for d in devices:
        lines.append(f"• *{d['name']}* — {d['price_fcfa']:,} FCFA")
        lines.append(f"  ID: `{d['id']}` | Garantie: {d['warranty']} | Stock: {d['stock']}")
    lines.append("\n👉 Envoyez l'*ID* d'un appareil pour voir le détail.")
    return "\n".join(lines)


def get_categories() -> list[tuple[str, str]]:
    return CATEGORIES
