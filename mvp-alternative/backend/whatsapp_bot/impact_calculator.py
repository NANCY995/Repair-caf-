"""
Calculateur d'impact environnemental BUTUS Repair.
CO₂ évité, déchets détournés, objets sauvés.
Basé sur les facteurs ADEME et données fabricants.
"""

from datetime import datetime
from typing import Optional

from knowledge_base import get_knowledge, DEVICE_KNOWLEDGE


# Facteurs d'émission CO₂ (kg équivalent CO₂ par appareil évité)
# Source : ADEME, Base Empreinte® — évitement fabrication + fin de vie
DEVICE_IMPACT_FACTORS = {
    "ventilateur": {
        "weight_kg": 3.5,
        "co2_avoided_kg": 12.0,
        "waste_avoided_kg": 3.0,
        "materials": ["plastique ABS", "cuivre", "acier", "aluminium"],
        "repair_success_rate": 0.78,
    },
    "climatiseur": {
        "weight_kg": 35.0,
        "co2_avoided_kg": 180.0,
        "waste_avoided_kg": 30.0,
        "materials": ["acier", "cuivre", "aluminium", "gaz R32"],
        "repair_success_rate": 0.65,
    },
    "refrigerateur": {
        "weight_kg": 45.0,
        "co2_avoided_kg": 210.0,
        "waste_avoided_kg": 40.0,
        "materials": ["acier", "polyuréthane", "cuivre", "gaz R600a"],
        "repair_success_rate": 0.62,
    },
    "machine_laver": {
        "weight_kg": 55.0,
        "co2_avoided_kg": 195.0,
        "waste_avoided_kg": 48.0,
        "materials": ["acier", "béton de lestage", "cuivre", "plastique PP"],
        "repair_success_rate": 0.70,
    },
    "television": {
        "weight_kg": 8.0,
        "co2_avoided_kg": 85.0,
        "waste_avoided_kg": 7.0,
        "materials": ["verre", "plastique ABS", "aluminium", "terres rares"],
        "repair_success_rate": 0.55,
    },
    "smartphone": {
        "weight_kg": 0.2,
        "co2_avoided_kg": 45.0,
        "waste_avoided_kg": 0.15,
        "materials": ["lithium", "verre", "cuivre", "terres rares"],
        "repair_success_rate": 0.60,
    },
    "ordinateur": {
        "weight_kg": 2.0,
        "co2_avoided_kg": 120.0,
        "waste_avoided_kg": 1.8,
        "materials": ["aluminium", "verre", "cuivre", "plastique PC/ABS"],
        "repair_success_rate": 0.58,
    },
    "audio": {
        "weight_kg": 1.5,
        "co2_avoided_kg": 20.0,
        "waste_avoided_kg": 1.2,
        "materials": ["plastique ABS", "cuivre", "aimants néodyme"],
        "repair_success_rate": 0.72,
    },
    "electromenager": {
        "weight_kg": 1.2,
        "co2_avoided_kg": 8.0,
        "waste_avoided_kg": 1.0,
        "materials": ["plastique PP", "acier inox", "cuivre"],
        "repair_success_rate": 0.75,
    },
    "autre": {
        "weight_kg": 5.0,
        "co2_avoided_kg": 25.0,
        "waste_avoided_kg": 4.0,
        "materials": ["divers"],
        "repair_success_rate": 0.50,
    },
}


# Facteurs par défaut pour les appareils non répertoriés
DEFAULT_FACTORS = {
    "weight_kg": 5.0,
    "co2_avoided_kg": 25.0,
    "waste_avoided_kg": 4.0,
    "materials": ["divers"],
    "repair_success_rate": 0.50,
}


def get_impact_factors(device_type: str) -> dict:
    """Retourne les facteurs d'impact pour un type d'appareil."""
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
        "electromenager": "electromenager", "mixeur": "electromenager",
    }
    key = mapping.get(device_type)
    if key and key in DEVICE_IMPACT_FACTORS:
        return DEVICE_IMPACT_FACTORS[key]

    for k, v in DEVICE_IMPACT_FACTORS.items():
        if device_type in k:
            return v
    return dict(DEFAULT_FACTORS)


def calculate_impact(device_type: str, repair_success: bool = True) -> dict:
    """Calcule l'impact d'une réparation."""
    factors = get_impact_factors(device_type)
    success_multiplier = 1.0 if repair_success else 0.0

    return {
        "device_type": device_type,
        "weight_kg": factors["weight_kg"],
        "co2_avoided_kg": round(factors["co2_avoided_kg"] * success_multiplier, 1),
        "waste_avoided_kg": round(factors["waste_avoided_kg"] * success_multiplier, 1),
        "materials_saved": factors["materials"],
        "repair_success": repair_success,
    }


def calculate_impact_batch(sessions: list[dict]) -> dict:
    """Calcule l'impact agrégé pour une liste de sessions de réparation."""
    total_co2 = 0.0
    total_waste = 0.0
    total_repaired = 0
    total_devices = len(sessions)
    devices_by_type = {}

    for session in sessions:
        device_type = session.get("device_type", "autre")
        success = session.get("status") in ("resolu", "reussi", "termine")

        factors = get_impact_factors(device_type)
        if success:
            total_co2 += factors["co2_avoided_kg"]
            total_waste += factors["waste_avoided_kg"]
            total_repaired += 1

        devices_by_type[device_type] = devices_by_type.get(device_type, 0) + 1

    return {
        "total_devices": total_devices,
        "total_repaired": total_repaired,
        "total_co2_avoided_kg": round(total_co2, 1),
        "total_waste_avoided_kg": round(total_waste, 1),
        "total_co2_avoided_tons": round(total_co2 / 1000, 2),
        "repair_rate": round(total_repaired / total_devices * 100, 1) if total_devices > 0 else 0,
        "devices_by_type": devices_by_type,
        "co2_by_device": {
            dt: get_impact_factors(dt)["co2_avoided_kg"]
            for dt in set(devices_by_type.keys())
        },
    }


def format_impact_text(impact: dict) -> str:
    """Formate l'impact en texte WhatsApp."""
    lines = [
        "🌍 *Impact BUTUS Repair*",
        "─" * 30,
        "",
        f"📦 Appareils traités : *{impact['total_devices']}*",
        f"✅ Réparés avec succès : *{impact['total_repaired']}*",
        f"📊 Taux de réparation : *{impact['repair_rate']}%*",
        "",
        f"🌱 CO₂ évité : *{impact['total_co2_avoided_kg']} kg*",
        f"   ({impact['total_co2_avoided_tons']} tonnes)",
        f"🗑️ Déchets détournés : *{impact['total_waste_avoided_kg']} kg*",
        "",
        "*Par type d'appareil :*",
    ]
    for dt, count in sorted(impact.get("devices_by_type", {}).items()):
        co2 = impact.get("co2_by_device", {}).get(dt, 0)
        lines.append(f"  • {dt} : {count} app. (~{co2} kg CO₂ évité chacun)")

    lines.append("")
    lines.append("💚 Merci de contribuer à réduire les déchets électroniques au Togo !")
    return "\n".join(lines)


def get_dashboard_stats(sessions: list[dict], tickets: list[dict]) -> dict:
    """Génère toutes les stats pour le dashboard."""
    # Impact CO₂
    impact = calculate_impact_batch(sessions)

    # Stats tickets
    total_tickets = len(tickets)
    tickets_by_status = {}
    for t in tickets:
        s = t.get("Statut", "ouvert").lower()
        tickets_by_status[s] = tickets_by_status.get(s, 0) + 1

    # Top pannes
    issue_counter = {}
    for t in tickets:
        desc = t.get("Description panne", "")
        if desc:
            for keyword in ["ne tourne", "ne chauffe", "ne refroidit", "ne s'allume",
                          "bruit", "fuit", "charge", "écran", "son", "lent"]:
                if keyword in desc.lower():
                    issue_counter[keyword] = issue_counter.get(keyword, 0) + 1
                    break
            else:
                issue_counter["autre"] = issue_counter.get("autre", 0) + 1

    top_issues = sorted(issue_counter.items(), key=lambda x: -x[1])[:10]

    return {
        "impact": impact,
        "tickets": {
            "total": total_tickets,
            "by_status": tickets_by_status,
        },
        "top_issues": [{"symptom": k, "count": v} for k, v in top_issues],
        "last_updated": datetime.now().isoformat(),
    }
