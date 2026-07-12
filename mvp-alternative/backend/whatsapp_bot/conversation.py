import re
from datetime import datetime
from typing import Optional

from config import get_settings
from models import (
    ConversationState, ConversationData, DEVICE_CATEGORIES,
    DiagnosisRequest,
)
from whatsapp import send_text, send_interactive_list, send_buttons
from diagnostic import diagnose, get_device_info, get_all_device_names, get_device_impact
from knowledge_base import format_issue_response, get_knowledge
from sheets import add_ticket, add_contact_request, add_repair_session, add_part_reservation
from impact_calculator import calculate_impact, format_impact_text, calculate_impact_batch
from parts_catalog import get_parts_by_device, get_all_parts, search_parts, get_part_by_id, format_part_detail, get_device_categories
from reconditioned_catalog import get_all_reconditioned, get_by_category, search_reconditioned, get_by_id, format_detail, format_category_list, get_categories
from veille import do_veille, build_veille_menu, build_perso_instruction, VEILLE_TOPICS


conversations: dict[str, ConversationData] = {}


def _get_or_create(phone: str) -> ConversationData:
    if phone not in conversations:
        conversations[phone] = ConversationData(phone_number=phone)
    return conversations[phone]


def _update_state(phone: str, state: ConversationState):
    conv = _get_or_create(phone)
    conv.state = state
    conv.updated_at = datetime.now()


def _clean_text(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"^\d+\s*[\)\.]\s*", "", text)
    text = re.sub(r"^[•\-*]\s*", "", text)
    return text.strip()


async def handle_message(phone: str, text: str) -> list[str]:
    conv = _get_or_create(phone)
    cleaned = _clean_text(text)
    state = conv.state

    # Commande universelle : retour au menu
    if cleaned in ["menu", "retour", "accueil", "0", "🏠", "quitter"]:
        _update_state(phone, ConversationState.HOME)
        _set_home_interactive(phone)
        return [build_home_menu()]

    handlers = {
        ConversationState.HOME: _handle_home,
        ConversationState.DIAGNOSE_DEVICE_TYPE: _handle_diagnose_device_type,
        ConversationState.DIAGNOSE_BRAND: _handle_diagnose_brand,
        ConversationState.DIAGNOSE_MODEL: _handle_diagnose_model,
        ConversationState.DIAGNOSE_ISSUE: _handle_diagnose_issue,
        ConversationState.DIAGNOSE_CONFIRM: _handle_diagnose_confirm,
        ConversationState.DIAGNOSE_RESULT: _handle_diagnose_result,
        ConversationState.MY_TICKETS: _handle_my_tickets,
        ConversationState.CONTACT_REPAIRER: _handle_contact_repairer,
        ConversationState.CONTACT_REPAIRER_NAME: _handle_contact_name,
        ConversationState.CONTACT_REPAIRER_PHONE: _handle_contact_phone,
        ConversationState.CONTACT_REPAIRER_REASON: _handle_contact_reason,
        ConversationState.ABOUT_BUTUS: _handle_about,
        ConversationState.FICHES_TECHNIQUES: _handle_fiches_menu,
        ConversationState.FICHES_DEVICE_SELECT: _handle_fiches_device,
        ConversationState.FICHES_ISSUE_SELECT: _handle_fiches_issue,
        ConversationState.TIPS: _handle_tips,
        ConversationState.LOG_REPAIR: _handle_log_repair,
        ConversationState.LOG_REPAIR_TICKET: _handle_log_repair_ticket,
        ConversationState.LOG_REPAIR_PARTS: _handle_log_repair_parts,
        ConversationState.LOG_REPAIR_COST: _handle_log_repair_cost,
        ConversationState.LOG_REPAIR_TIME: _handle_log_repair_time,
        ConversationState.LOG_REPAIR_STATUS: _handle_log_repair_status,
        ConversationState.LOG_REPAIR_CONFIRM: _handle_log_repair_confirm,
        ConversationState.SHOW_IMPACT: _handle_show_impact,
        ConversationState.BROWSE_PARTS: _handle_browse_parts,
        ConversationState.BROWSE_PARTS_DEVICE: _handle_browse_parts_device,
        ConversationState.PART_DETAIL: _handle_part_detail,
        ConversationState.PART_RESERVE: _handle_part_reserve,
        ConversationState.PART_RESERVE_CONFIRM: _handle_part_reserve_confirm,
        ConversationState.BROWSE_RECONDITIONED: _handle_reconditioned_menu,
        ConversationState.RECONDITIONED_CATEGORY: _handle_reconditioned_category,
        ConversationState.RECONDITIONED_DETAIL: _handle_reconditioned_detail,
        ConversationState.RECONDITIONED_CONTACT: _handle_reconditioned_contact,
        ConversationState.CONSENT_PENDING: _handle_consent,
        ConversationState.VEILLE_MENU: _handle_veille_menu,
        ConversationState.VEILLE_TOPIC: _handle_veille_topic,
        ConversationState.VEILLE_RESULTS: _handle_veille_results,
        ConversationState.VEILLE_PERSO: _handle_veille_perso,
    }

    handler = handlers.get(state, _handle_home)
    responses = await handler(phone, cleaned, conv)

    # Auto-registrer les menus interactifs selon l'état après traitement
    new_state = conv.state
    if new_state == ConversationState.HOME:
        _set_home_interactive(phone)
    elif new_state == ConversationState.DIAGNOSE_DEVICE_TYPE:
        _set_device_interactive(phone)
    elif new_state == ConversationState.BROWSE_PARTS:
        _set_parts_buttons(phone)
    elif new_state == ConversationState.BROWSE_RECONDITIONED:
        _set_reconditioned_buttons(phone)

    return responses


# =================== MENU PRINCIPAL ===================

def build_home_menu() -> str:
    return (
        "🌀 *BUTUS Repair — Assistant Diagnostic*\n\n"
        "Je suis votre copilote réparation. Besoin d'aide ?\n\n"
        "1️⃣ *Diagnostiquer* un appareil en panne\n"
        "2️⃣ *Fiches techniques* — guides par appareil\n"
        "3️⃣ *Pièces détachées* — trouver & commander 🔩\n"
        "4️⃣ *Appareils reconditionnés* — acheter garanti 📱\n"
        "5️⃣ *Mes tickets* — suivi de mes réparations\n"
        "6️⃣ *Contacter* un réparateur BUTUS\n"
        "7️⃣ *Astuces & infos* — prévention, contacts\n"
        "8️⃣ *Impact* — CO₂ évité, stats\n"
        "9️⃣ *Enregistrer* une réparation (technicien)\n"
        "🔟 *Veille stratégique* — marché, concurrents 📡\n\n"
        "👉 Répondez avec le numéro de votre choix.\n"
        "💡 *À propos* de BUTUS → tapez \"butus\""
    )


# =================== MENUS INTERACTIFS ===================


def _set_home_interactive(phone: str):
    rows = [
        {"id": "1", "title": "Diagnostiquer", "description": "un appareil en panne"},
        {"id": "2", "title": "Fiches techniques", "description": "guides par appareil"},
        {"id": "3", "title": "Pièces détachées", "description": "trouver & commander"},
        {"id": "4", "title": "Reconditionnés", "description": "acheter garanti"},
        {"id": "5", "title": "Mes tickets", "description": "suivi réparations"},
        {"id": "6", "title": "Contacter", "description": "un réparateur BUTUS"},
        {"id": "7", "title": "Astuces & infos", "description": "prévention, contacts"},
        {"id": "8", "title": "Impact CO₂", "description": "stats environnement"},
        {"id": "9", "title": "Enregistrer", "description": "une réparation (technicien)"},
        {"id": "10", "title": "Veille stratégique", "description": "marché, concurrents"},
    ]
    register_interactive(phone, {
        "type": "list",
        "header": "🌀 BUTUS Repair",
        "body": "Je suis votre copilote réparation. Besoin d'aide ?\n\n💡 \"butus\" = À propos",
        "footer": "BUTUS Repair — Lomé 🇹🇬",
        "button": "Menu principal",
        "sections": [{"title": "Options", "rows": rows}],
    })


def _set_device_interactive(phone: str):
    from models import DEVICE_CATEGORIES
    rows = [
        {"id": str(i), "title": cat.label, "description": None}
        for i, cat in enumerate(DEVICE_CATEGORIES, 1)
    ]
    register_interactive(phone, {
        "type": "list",
        "header": "🔍 Diagnostiquer",
        "body": "Quel appareil est en panne ?",
        "button": "Choisir un appareil",
        "sections": [{"title": "Appareils", "rows": rows}],
    })


def _set_parts_buttons(phone: str):
    register_interactive(phone, {
        "type": "button",
        "body": "🔩 Pièces détachées",
        "buttons": [
            {"id": "1", "title": "Par appareil"},
            {"id": "2", "title": "Rechercher"},
            {"id": "3", "title": "Catalogue complet"},
        ],
    })


def _set_reconditioned_buttons(phone: str):
    register_interactive(phone, {
        "type": "button",
        "body": "📱 Reconditionnés",
        "buttons": [
            {"id": "1", "title": "Par catégorie"},
            {"id": "2", "title": "Rechercher"},
            {"id": "3", "title": "Tout le catalogue"},
        ],
    })


# --- Consentement RGPD / protection des données ---
_consented: set[str] = set()
_interactive_payloads: dict[str, dict] = {}


def register_interactive(phone: str, payload: dict):
    """Stocke un payload interactif (liste/buttons) à envoyer avec la prochaine réponse."""
    _interactive_payloads[phone] = payload


def pop_interactive(phone: str) -> dict | None:
    """Récupère et supprime le payload interactif en attente."""
    return _interactive_payloads.pop(phone, None)

CONSENT_TEXT = (
    "🔒 *BUTUS Repair — Protection des données*\n\n"
    "BUTUS collecte les données suivantes pour vous assister :\n"
    "• Numéro WhatsApp\n"
    "• Type d'appareil, marque et description de la panne\n"
    "• Informations de contact (si réservation ou demande)\n\n"
    "Ces données sont strictement internes à BUTUS Repair (Lomé, Togo) "
    "et ne sont jamais partagées ni revendues.\n"
    "Conformément à la loi togolaise 2019-004.\n\n"
    "👉 Tapez *OUI* ou *Commencer* pour accepter.\n"
    "Tapez *STOP* pour annuler."
)


async def _handle_home(phone: str, text: str, conv: ConversationData) -> list[str]:
    # Vérifier le consentement (1ère utilisation)
    if phone not in _consented:
        _update_state(phone, ConversationState.CONSENT_PENDING)
        return [CONSENT_TEXT]

    # Salutations → menu
    if text in ["bonjour", "hello", "salut", "bonsoir", "hi", "hey", "yo", "cc", "merci"]:
        _set_home_interactive(phone)
        return [build_home_menu()]

    intent_map = {
        "1": "diagnostiquer", "diagnostiquer": "diagnostiquer",
        "diagnostic": "diagnostiquer", "dépanner": "diagnostiquer",
        "reparer": "diagnostiquer", "réparer": "diagnostiquer",
        "panne": "diagnostiquer", "aider": "diagnostiquer",

        "2": "fiches", "fiches": "fiches",
        "fiche technique": "fiches", "fiches techniques": "fiches",
        "guide": "fiches", "tutoriel": "fiches",

        "3": "parts", "pieces": "parts", "pièce": "parts",
        "pièces": "parts", "piece": "parts",
        "boutique": "parts", "catalogue": "parts", "commander": "parts",

        "4": "reconditioned", "reconditionne": "reconditioned",
        "reconditionné": "reconditioned", "occase": "reconditioned",
        "occasion": "reconditioned", "acheter": "reconditioned",

        "5": "tickets", "ticket": "tickets", "mes tickets": "tickets",
        "mes réparations": "tickets", "suivi": "tickets",

        "6": "contact", "contacter": "contact",
        "réparateur": "contact", "reparateur": "contact",
        "aide": "contact", "assistance": "contact",
        "humain": "contact",

        "7": "tips", "astuces": "tips", "conseils": "tips",
        "prévention": "tips", "prevention": "tips",

        "8": "impact", "impact": "impact",
        "stats": "impact", "co2": "impact", "statistiques": "impact",

        "9": "log", "enregistrer": "log",
        "réparation": "log", "reparation": "log",
        "technicien": "log", "réparateur": "log",

        "10": "veille", "veille": "veille",
        "veille stratégique": "veille", "stratégique": "veille",
        "strategique": "veille", "marché": "veille",
        "concurrents": "veille", "concurrence": "veille",
        "tendance": "veille", "tendances": "veille",

        "butus": "about", "info": "about",
        "présentation": "about", "à propos": "about",
    }

    intent = intent_map.get(text, text)

    if intent == "diagnostiquer":
        _set_device_interactive(phone)
        _update_state(phone, ConversationState.DIAGNOSE_DEVICE_TYPE)
        return [build_device_type_menu()]
    elif intent == "fiches":
        _update_state(phone, ConversationState.FICHES_TECHNIQUES)
        return [build_fiches_menu()]
    elif intent == "parts":
        _update_state(phone, ConversationState.BROWSE_PARTS)
        return await _handle_browse_parts(phone, text, conv)
    elif intent == "reconditioned":
        _update_state(phone, ConversationState.BROWSE_RECONDITIONED)
        return await _handle_reconditioned_menu(phone, text, conv)
    elif intent == "tickets":
        return await _handle_my_tickets(phone, text, conv)
    elif intent == "contact":
        _update_state(phone, ConversationState.CONTACT_REPAIRER)
        return ["📞 *Contacter un réparateur BUTUS*\n\nUn réparateur vous rappelle sous 24h.\n\n👉 Quel est votre *prénom et nom* ?"]
    elif intent == "tips":
        _update_state(phone, ConversationState.TIPS)
        return await _handle_tips(phone, text, conv)
    elif intent == "impact":
        _update_state(phone, ConversationState.SHOW_IMPACT)
        return await _handle_show_impact(phone, text, conv)
    elif intent == "log":
        _update_state(phone, ConversationState.LOG_REPAIR)
        return ["🔧 *Enregistrer une réparation*\n\nRéservé aux techniciens BUTUS.\n\n📝 *Numéro du ticket ?* (ex: BUTUS-20260710123456)\n\n💡 Vous le trouvez dans le message de confirmation reçu par le client."]
    elif intent == "veille":
        _update_state(phone, ConversationState.VEILLE_MENU)
        return [build_veille_menu()]
    elif intent == "about":
        _update_state(phone, ConversationState.ABOUT_BUTUS)
        return await _handle_about(phone, text, conv)
    else:
        # Tentative de recherche directe dans le catalogue de pièces
        results = search_parts(text)
        if len(text) >= 3 and results:
            _update_state(phone, ConversationState.BROWSE_PARTS)
            return [_format_parts_list(results, f"🔎 Résultats pour « {text} »")]
        return [
            "Je n'ai pas compris. Voici les options :\n\n"
            "1️⃣ Diagnostiquer un appareil\n"
            "2️⃣ Fiches techniques\n"
            "3️⃣ Pièces détachées\n"
            "4️⃣ Appareils reconditionnés\n"
            "5️⃣ Mes tickets\n"
            "6️⃣ Contacter un réparateur\n"
            "7️⃣ Astuces & infos\n"
            "8️⃣ Impact\n"
            "9️⃣ Enregistrer une réparation\n"
            "🔟 Veille stratégique"
        ]


async def _handle_consent(phone: str, text: str, conv: ConversationData) -> list[str]:
    text_clean = text.strip().lower()
    if text_clean in ("oui", "ouai", "ok", "commencer", "yes", "y", "go", "start", "accepter"):
        _consented.add(phone)
        _update_state(phone, ConversationState.HOME)
        _set_home_interactive(phone)
        return [build_home_menu()]
    elif text_clean in ("non", "no", "stop", "annuler", "n"):
        return [
            "⚠️ Sans votre consentement, BUTUS ne peut pas collecter les "
            "informations nécessaires pour vous assister.\n\n"
            "Répondez *OUI* si vous changez d'avis, ou tapez *STOP* pour arrêter."
        ]
    else:
        return [
            "🔒 Pour utiliser BUTUS Repair, vous devez accepter la collecte "
            "de vos données (numéro, type d'appareil et panne).\n\n"
            "👉 Tapez *OUI* pour accepter\n👉 Tapez *STOP* pour annuler"
        ]


# =================== DIAGNOSTIC AMÉLIORÉ ===================

def build_device_type_menu() -> str:
    lines = ["🔍 *Quel appareil est en panne ?*\n"]
    for i, cat in enumerate(DEVICE_CATEGORIES, 1):
        lines.append(f"{i}. {cat.emoji} {cat.label}")
    lines.append("\n0️⃣ Menu principal")
    return "\n".join(lines)


async def _handle_diagnose_device_type(phone: str, text: str, conv: ConversationData) -> list[str]:
    if text == "0":
        _update_state(phone, ConversationState.HOME)
        return [build_home_menu()]

    if text.isdigit():
        idx = int(text) - 1
        if 0 <= idx < len(DEVICE_CATEGORIES):
            selected = DEVICE_CATEGORIES[idx]
            conv.device_type = selected.label
            _update_state(phone, ConversationState.DIAGNOSE_BRAND)
            return [
                f"✅ *{selected.emoji} {selected.label}* — bien reçu !\n\n"
                f"📝 *Marque ?* (Samsung, LG, Philips, Brandt, ou la marque de l'appareil)\n\n"
                f"💡 Si vous ne savez pas, dites \"Je ne sais pas\""
            ]
        return ["❌ Numéro invalide. Choisissez un chiffre entre 1 et 10, ou 0 pour le menu."]

    cleaned = _clean_text(text)
    for cat in DEVICE_CATEGORIES:
        if cleaned in cat.label.lower() or cleaned in cat.id.lower():
            conv.device_type = cat.label
            _update_state(phone, ConversationState.DIAGNOSE_BRAND)
            return [
                f"✅ *{cat.emoji} {cat.label}* — bien reçu !\n\n"
                f"📝 *Marque ?* (Samsung, LG, Philips, Brandt...)"
            ]

    names = ", ".join(c.label.lower() for c in DEVICE_CATEGORIES)
    return [f"❌ Type non reconnu. Choisissez :\n{names}\n\nOu envoyez 0 pour le menu."]


async def _handle_diagnose_brand(phone: str, text: str, conv: ConversationData) -> list[str]:
    if _clean_text(text) in ["je ne sais pas", "jsp", "inconnu", "?", "non"]:
        conv.device_brand = "Marque inconnue"
    else:
        conv.device_brand = text.strip().title()

    _update_state(phone, ConversationState.DIAGNOSE_MODEL)
    return [
        f"✅ Marque : *{conv.device_brand}*\n\n"
        f"📝 *Modèle exact ?* (souvent sur une étiquette à l'arrière)\n\n"
        f"💡 Si inconnu, dites \"Je ne sais pas\""
    ]


async def _handle_diagnose_model(phone: str, text: str, conv: ConversationData) -> list[str]:
    model = text.strip()
    if _clean_text(text) in ["je ne sais pas", "jsp", "inconnu", "?", "non"]:
        model = "Modèle non spécifié"
    conv.device_model = model

    _update_state(phone, ConversationState.DIAGNOSE_ISSUE)
    return [
        f"✅ Modèle : *{conv.device_model}*\n\n"
        f"📝 *Quel est le problème exact ?* Décrivez en quelques phrases :\n\n"
        f"  → Que se passe-t-il ?\n"
        f"  → Depuis quand ?\n"
        f"  → Bruit ? Odeur ? Voyant ?\n"
        f"  → Y a-t-il eu une coupure de courant récemment ?"
    ]


async def _handle_diagnose_issue(phone: str, text: str, conv: ConversationData) -> list[str]:
    conv.issue_description = text.strip()
    _update_state(phone, ConversationState.DIAGNOSE_CONFIRM)

    summary = (
        "📋 *Récapitulatif :*\n\n"
        f"🔧 *Appareil :* {conv.device_type}\n"
        f"🏷️ *Marque :* {conv.device_brand}\n"
        f"📦 *Modèle :* {conv.device_model}\n"
        f"🔴 *Panne :* {conv.issue_description[:100]}{'...' if len(conv.issue_description) > 100 else ''}\n\n"
        "Que voulez-vous faire ?\n"
        "✅ *1* — Lancer le diagnostic IA\n"
        "📖 *2* — Voir la fiche technique de cet appareil\n"
        "📞 *3* — Créer un ticket pour un réparateur\n"
        "❌ *0* — Menu principal"
    )
    return [summary]


async def _handle_diagnose_confirm(phone: str, text: str, conv: ConversationData) -> list[str]:
    cleaned = _clean_text(text)

    if cleaned in ["1", "oui", "yes", "ok", "go", "diagnostiquer", "lancer", "démarrer", "✅"]:
        # → Diagnostic
        _update_state(phone, ConversationState.DIAGNOSE_RESULT)
        return await _run_diagnosis(phone, conv)

    elif cleaned in ["2", "fiche", "fiche technique"]:
        # → Fiche technique de l'appareil
        return await _show_device_fiche(phone, conv)

    elif cleaned in ["3", "ticket", "créer ticket", "contacter", "📞"]:
        # → Créer ticket directement
        return await _create_ticket_from_diagnosis(phone, conv)

    elif cleaned in ["0", "non", "menu", "retour"]:
        _update_state(phone, ConversationState.HOME)
        return [build_home_menu()]

    else:
        return ["Répondez :\n✅ *1* = Diagnostic\n📖 *2* = Fiche technique\n📞 *3* = Ticket réparateur\n❌ *0* = Menu"]


async def _run_diagnosis(phone: str, conv: ConversationData) -> list[str]:
    req = DiagnosisRequest(
        device_type=conv.device_type or "",
        device_brand=conv.device_brand or "",
        device_model=conv.device_model or "",
        issue_description=conv.issue_description or "",
    )

    messages = ["⏳ *Diagnostic en cours...* Patientez quelques secondes.\n"]

    result = diagnose(req)
    if result:
        lines = [
            "🔍 *RÉSULTAT DU DIAGNOSTIC*",
            "─" * 30,
            "",
            f"⚠️ *Urgence :* {result.urgency}",
            f"🛠️ *Réparable par vous-même :* {'Oui ✅' if result.can_self_repair else 'Non ❌ — préférez un professionnel'}",
            "",
            "*Causes possibles :*",
        ]
        for c in result.possible_causes:
            lines.append(f"  • {c}")

        lines.append("")
        lines.append("*Étapes recommandées :*")
        for s in result.steps_to_try:
            lines.append(f"  {s}")

        if result.parts_needed:
            lines.append("")
            lines.append("*Pièces nécessaires (prix FCFA indicatifs) :*")
            for p in result.parts_needed:
                lines.append(f"  • {p}")

        lines.append("")
        lines.append(f"💬 *Recommandation :*")
        lines.append(result.recommendation)

        # Créer ticket dans Google Sheets
        ticket_id = f"BUTUS-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        conv.ticket_id = ticket_id
        add_ticket({
            "ticket_id": ticket_id,
            "phone_number": phone,
            "device_type": conv.device_type or "",
            "device_brand": conv.device_brand or "",
            "device_model": conv.device_model or "",
            "issue_description": conv.issue_description or "",
            "diagnosis_summary": result.recommendation[:200],
            "status": "en_cours",
        })

        lines.append("")
        lines.append(f"📌 *Ticket créé :* `{ticket_id}`")
        lines.append("")
        lines.append("─" * 30)
        lines.append("Prochaine étape ?")
        lines.append("1️⃣ Contacter un réparateur BUTUS")
        lines.append("2️⃣ Nouveau diagnostic")
        lines.append("0️⃣ Menu principal")

        messages.append("\n".join(lines))
    else:
        messages.append(
            "❌ Diagnostic impossible. Voulez-vous créer un ticket pour "
            "qu'un réparateur vous contacte ?\n\n"
            "1️⃣ Oui, créer un ticket\n"
            "0️⃣ Menu principal"
        )

    return messages


async def _handle_diagnose_result(phone: str, text: str, conv: ConversationData) -> list[str]:
    cleaned = _clean_text(text)

    if cleaned in ["1", "contacter", "réparateur", "reparateur"]:
        _update_state(phone, ConversationState.CONTACT_REPAIRER_NAME)
        return ["📞 *Contact réparateur*\n\nQuel est votre *nom et prénom* ?"]

    elif cleaned in ["2", "nouveau", "recommencer"]:
        _update_state(phone, ConversationState.DIAGNOSE_DEVICE_TYPE)
        return ["🔄 *Nouveau diagnostic*\n\n" + build_device_type_menu()]

    elif cleaned in ["0", "menu", "retour"]:
        _update_state(phone, ConversationState.HOME)
        return [build_home_menu()]

    else:
        return ["Choisissez :\n1️⃣ Contacter un réparateur\n2️⃣ Nouveau diagnostic\n0️⃣ Menu principal"]


async def _show_device_fiche(phone: str, conv: ConversationData) -> list[str]:
    """Affiche la fiche technique de l'appareil en cours de diagnostic."""
    device_type = conv.device_type or ""
    kb = get_knowledge(device_type)
    if not kb:
        return ["Aucune fiche technique disponible pour cet appareil."]

    lines = [
        f"📖 *Fiche technique — {kb['emoji']} {kb['name']}*",
        "─" * 30,
        "",
    ]
    for issue in kb.get("common_issues", []):
        lines.append(f"🔴 *{issue['symptom']}*")
        for c in issue.get("causes", [])[:2]:
            lines.append(f"  • {c}")
        lines.append(f"  ✅ Rép. {'possible ✅' if issue.get('self_repair') else 'difficile ❌'}")
        lines.append("")

    shops = kb.get("local_shops", [])
    if shops:
        lines.append("*Où réparer à Lomé :*")
        for s in shops:
            lines.append(f"  📍 {s}")

    lines.append("")
    lines.append("─" * 30)
    lines.append("1️⃣ Lancer le diagnostic")
    lines.append("0️⃣ Menu principal")

    return ["\n".join(lines)]


async def _create_ticket_from_diagnosis(phone: str, conv: ConversationData) -> list[str]:
    ticket_id = f"BUTUS-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    conv.ticket_id = ticket_id

    add_ticket({
        "ticket_id": ticket_id,
        "phone_number": phone,
        "device_type": conv.device_type or "Non spécifié",
        "device_brand": conv.device_brand or "Non spécifié",
        "device_model": conv.device_model or "Non spécifié",
        "issue_description": conv.issue_description or "Non spécifié",
        "status": "ouvert",
    })

    _update_state(phone, ConversationState.HOME)

    return [
        f"✅ *Ticket créé !*\n\n"
        f"📌 Référence : `{ticket_id}`\n\n"
        f"Un réparateur BUTUS vous contactera sous 24h.\n"
        f"Conservez ce numéro pour le suivi.\n\n"
        "---\n" + build_home_menu()
    ]


# =================== FICHES TECHNIQUES ===================

def build_fiches_menu() -> str:
    lines = ["📖 *Fiches techniques BUTUS*\n\nChoisissez un appareil :\n"]
    devices = get_all_device_names()
    for i, name in enumerate(devices, 1):
        kb = get_knowledge(name)
        emoji = kb["emoji"] if kb else "📖"
        lines.append(f"{i}. {emoji} {name}")
    lines.append("\n0️⃣ Menu principal")
    return "\n".join(lines)


async def _handle_fiches_menu(phone: str, text: str, conv: ConversationData) -> list[str]:
    if text == "0":
        _update_state(phone, ConversationState.HOME)
        return [build_home_menu()]

    devices = get_all_device_names()
    if text.isdigit():
        idx = int(text) - 1
        if 0 <= idx < len(devices):
            conv.device_type = devices[idx]
            _update_state(phone, ConversationState.FICHES_DEVICE_SELECT)
            return await _show_fiche_detail(phone, conv, devices[idx])

    return [f"Choisissez un numéro d'appareil (1-{len(devices)}), ou 0 pour le menu."]


async def _handle_fiches_device(phone: str, text: str, conv: ConversationData) -> list[str]:
    if text == "0":
        _update_state(phone, ConversationState.HOME)
        return [build_home_menu()]

    if text in ["1", "menu", "retour"]:
        _update_state(phone, ConversationState.FICHES_TECHNIQUES)
        return [build_fiches_menu()]

    return [build_fiches_menu()]


async def _handle_fiches_issue(phone: str, text: str, conv: ConversationData) -> list[str]:
    _update_state(phone, ConversationState.HOME)
    return [build_home_menu()]


async def _show_fiche_detail(phone: str, conv: ConversationData, device_name: str) -> list[str]:
    kb = get_knowledge(device_name)
    if not kb:
        return ["Fiche non disponible."]

    lines = [
        f"📖 *{kb['emoji']} {kb['name']} — Pannes fréquentes*",
        "─" * 30,
        "",
    ]
    for idx, issue in enumerate(kb.get("common_issues", []), 1):
        lines.append(f"{idx}. *{issue['symptom']}*")
        lines.append(f"   Causes : {issue['causes'][0]}")
        lines.append(f"   ✅ {'Réparable' if issue.get('self_repair') else '→ Réparateur'}")
        lines.append("")

    lines.append("─" * 30)
    lines.append("1️⃣ Lancer un diagnostic")
    lines.append("0️⃣ Menu principal")

    return ["\n".join(lines)]


# =================== ASTUCES ===================

async def _handle_tips(phone: str, text: str, conv: ConversationData) -> list[str]:
    _update_state(phone, ConversationState.HOME)
    tips = (
        "💡 *Astuces BUTUS pour prolonger la vie de vos appareils*\n\n"
        "🔌 *Protection électrique*\n"
        "  • Utilisez un régulateur de tension (stabilisateur) — ~15 000 FCFA\n"
        "  • Débranchez les appareils sensibles pendant les orages\n"
        "  • Un parafoudre sur le tableau électrique protège toute la maison\n\n"
        "🧹 *Entretien régulier*\n"
        "  • Nettoyez les filtres (clim, ventilateur, machine à laver) tous les mois\n"
        "  • Dépoussiérez l'arrière du frigo tous les 6 mois\n"
        "  • Graissez les charnières et axes des ventilateurs 2×/an\n\n"
        "💧 *Évitez l'humidité*\n"
        "  • Ne posez pas d'appareils électroniques près des fenêtres\n"
        "  • Utilisez des housses de protection pour la saison des pluies\n\n"
        "🛠️ *Avant de jeter*\n"
        "  • 80% des pannes sont réparables ! Consultez nos fiches techniques\n"
        "  • Une panne est souvent due à un simple condensateur à 1 000 FCFA\n"
        "  • Apportez votre appareil à un Repair Café BUTUS avant de le jeter\n\n"
        "📞 *Urgence réparateur ?* Choisissez l'option 4 dans le menu.\n"
        "---\n" + build_home_menu()
    )
    return [tips]


# =================== MES TICKETS ===================

async def _handle_my_tickets(phone: str, text: str, conv: ConversationData) -> list[str]:
    try:
        from sheets import get_tickets_by_phone
        tickets = get_tickets_by_phone(phone)
    except Exception:
        tickets = []

    if not tickets:
        _update_state(phone, ConversationState.HOME)
        return [
            "📋 *Vos tickets*\n\n"
            "Vous n'avez pas encore de ticket.\n\n"
            "Pour créer un ticket : choisissez *1. Diagnostiquer* depuis le menu.\n"
            "---\n" + build_home_menu()
        ]

    lines = ["📋 *Vos tickets de réparation :*\n"]
    for t in tickets[-5:]:
        status = t.get("Statut", "").lower()
        status_emoji = {"ouvert": "🟢", "en_cours": "🟡", "resolu": "✅", "ferme": "⚪"}
        emoji = status_emoji.get(status, "⚪")
        lines.append(
            f"{emoji} `{t.get('ID Ticket', '?')}`\n"
            f"   {t.get('Type appareil', '?')} — {t.get('Date', '?')}\n"
            f"   Statut : *{status}*\n"
        )

    lines.append("---\n1️⃣ Nouveau diagnostic\n0️⃣ Menu principal")
    _update_state(phone, ConversationState.HOME)
    return ["\n".join(lines)]


# =================== CONTACT RÉPARATEUR ===================

async def _handle_contact_repairer(phone: str, text: str, conv: ConversationData) -> list[str]:
    conv.customer_name = text.strip().title()
    _update_state(phone, ConversationState.CONTACT_REPAIRER_PHONE)
    return [
        f"👤 Merci *{conv.customer_name}* !\n\n"
        f"📞 *Numéro pour le rappel ?*\n"
        f"(si c'est le même, dites \"Même numéro\")"
    ]


async def _handle_contact_name(phone: str, text: str, conv: ConversationData) -> list[str]:
    conv.customer_name = text.strip().title()
    _update_state(phone, ConversationState.CONTACT_REPAIRER_PHONE)
    return [
        f"👤 Merci *{conv.customer_name}* !\n\n"
        f"📞 *Numéro pour le rappel ?*"
    ]


async def _handle_contact_phone(phone: str, text: str, conv: ConversationData) -> list[str]:
    cleaned = _clean_text(text)
    if cleaned in ["même numéro", "meme", "oui", "le même", "meme numero"]:
        contact_phone = phone
    else:
        contact_phone = text.strip()

    conv.customer_phone = contact_phone
    _update_state(phone, ConversationState.CONTACT_REPAIRER_REASON)
    return [
        f"📞 Rappel au *{contact_phone}*\n\n"
        f"📝 *Motif du contact ?*\n"
        f"(diagnostic complexe, pièces, devis, autre...)"
    ]


async def _handle_contact_reason(phone: str, text: str, conv: ConversationData) -> list[str]:
    reason = text.strip()

    add_contact_request({
        "phone_number": phone,
        "name": getattr(conv, "customer_name", "Non spécifié"),
        "reason": reason,
    })

    _update_state(phone, ConversationState.HOME)
    return [
        "✅ *Demande envoyée !*\n\n"
        "Un réparateur BUTUS vous rappellera sous 24h (hors week-end).\n\n"
        "En attendant :\n"
        "• Essayez le *diagnostic* automatique (option 1)\n"
        "• Consultez les *fiches techniques* (option 2)\n"
        "---\n" + build_home_menu()
    ]


# =================== À PROPOS ===================

async def _handle_about(phone: str, text: str, conv: ConversationData) -> list[str]:
    _update_state(phone, ConversationState.HOME)
    return [
        "🌍 *BUTUS Repair — Lomé, Togo*\n\n"
        "BUTUS est un Repair Café et une communauté de réparateurs "
        "passionnés pour réduire les déchets électroniques au Togo.\n\n"
        "🎯 *Mission :*\n"
        "  • Réduire les déchets électroniques\n"
        "  • Former aux métiers de la réparation\n"
        "  • Rendre la réparation accessible à tous\n\n"
        "🔧 *Services :*\n"
        "  • Diagnostic gratuit via ce bot 🤖\n"
        "  • Réparation à prix solidaire 💰\n"
        "  • Pièces détachées d'occasion 🔄\n"
        "  • Ateliers de formation 👨‍🔧\n\n"
        "📍 *Lomé* — Atelier physique à venir !\n\n"
        "💰 *Faire un don* pour soutenir BUTUS :\n"
        "  • Mobile Money (T-Money, Flooz) : +228 XX XX XX XX\n"
        "  • Compte bancaire : à venir\n\n"
        "---\n" + build_home_menu()
    ]


# =================== IMPACT ENVIRONNEMENTAL ===================

async def _handle_show_impact(phone: str, text: str, conv: ConversationData) -> list[str]:
    """Affiche l'impact BUTUS (CO₂ évité, stats)."""
    try:
        from sheets import get_all_tickets, get_all_sessions
        tickets = get_all_tickets() or []
        sessions = get_all_sessions() or []
    except Exception:
        tickets = []
        sessions = []

    _update_state(phone, ConversationState.HOME)

    if not sessions and not tickets:
        # Pas encore de données → montrer les facteurs d'impact potentiels
        impact_msg = (
            "🌍 *Impact BUTUS Repair*\n\n"
            "Pas encore de données de réparation enregistrées.\n\n"
            "*Facteurs d'impact par appareil (CO₂ évité par réparation) :*\n"
            "  • 🌀 Ventilateur : 12 kg\n"
            "  • ❄️ Climatiseur : 180 kg\n"
            "  • 🧊 Réfrigérateur : 210 kg\n"
            "  • 👕 Machine à laver : 195 kg\n"
            "  • 📺 Téléviseur : 85 kg\n"
            "  • 📱 Smartphone : 45 kg\n"
            "  • 💻 Ordinateur : 120 kg\n\n"
            "💡 Astuce : les techniciens peuvent enregistrer chaque réparation "
            "via l'option *7. Enregistrer* pour générer automatiquement les stats d'impact.\n"
            "---\n" + build_home_menu()
        )
        return [impact_msg]

    # Calculer l'impact réel
    impact = calculate_impact_batch(sessions)
    impact_text = format_impact_text(impact)

    # Ajouter un sous-ensemble de stats tickets
    total_tickets = len(tickets)
    impact_text += f"\n📋 Tickets créés : {total_tickets}\n"
    impact_text += "\n---\n" + build_home_menu()

    return [impact_text]


# =================== ENREGISTRER UNE RÉPARATION (TECHNICIEN) ===================

# Stockage temporaire pour la session en cours d'enregistrement
_repair_logs: dict[str, dict] = {}


async def _handle_log_repair(phone: str, text: str, conv: ConversationData) -> list[str]:
    """État LOG_REPAIR : demande du numéro de ticket."""
    if text == "0":
        _update_state(phone, ConversationState.HOME)
        return [build_home_menu()]

    ticket_id = text.strip().upper()
    _repair_logs[phone] = {
        "ticket_id": ticket_id,
        "phone_number": phone,
        "parts_changed": [],
        "parts_cost_fcfa": 0,
        "labor_cost_fcfa": 0,
        "time_spent_minutes": 30,
        "test_results": "",
        "technician_name": "",
        "notes": "",
        "device_type": conv.device_type or "",
        "device_brand": conv.device_brand or "",
        "device_model": conv.device_model or "",
    }
    _update_state(phone, ConversationState.LOG_REPAIR_TICKET)
    return [
        f"✅ Ticket *{ticket_id}*\n\n"
        f"🧰 *Pièces changées ?* (séparez par des virgules)\n"
        f"Exemple : *Condensateur 2µF, interrupteur*\n"
        f"Si aucune pièce, dites \"Aucune\" ou tapez 0 pour passer."
    ]


async def _handle_log_repair_ticket(phone: str, text: str, conv: ConversationData) -> list[str]:
    """État LOG_REPAIR_TICKET : enregistre les pièces changées."""
    if text in ["0", "aucune", "non", "rien", "pas de pièces"]:
        _repair_logs[phone]["parts_changed"] = []
    else:
        parts = [p.strip() for p in text.split(",") if p.strip()]
        _repair_logs[phone]["parts_changed"] = parts

    _update_state(phone, ConversationState.LOG_REPAIR_PARTS)
    return [
        "💰 *Coût des pièces (FCFA) ?*\n"
        "Exemple : *3500* (pour 3 500 FCFA)\n"
        "Si gratuit, dites *0*."
    ]


async def _handle_log_repair_parts(phone: str, text: str, conv: ConversationData) -> list[str]:
    try:
        cost = int(text.strip().replace(" ", ""))
    except ValueError:
        cost = 0
    _repair_logs[phone]["parts_cost_fcfa"] = cost

    _update_state(phone, ConversationState.LOG_REPAIR_COST)
    return [
        f"💵 Pièces : *{cost} FCFA*\n\n"
        "🔧 *Main-d'œuvre (FCFA) ?*\n"
        "Exemple : *5000* (pour 5 000 FCFA)"
    ]


async def _handle_log_repair_cost(phone: str, text: str, conv: ConversationData) -> list[str]:
    try:
        labor = int(text.strip().replace(" ", ""))
    except ValueError:
        labor = 0
    _repair_logs[phone]["labor_cost_fcfa"] = labor

    _update_state(phone, ConversationState.LOG_REPAIR_TIME)
    return [
        f"🔧 Main-d'œuvre : *{labor} FCFA*\n\n"
        "⏱️ *Temps passé (minutes) ?*\n"
        "Exemple : *45* (pour 45 minutes)"
    ]


async def _handle_log_repair_time(phone: str, text: str, conv: ConversationData) -> list[str]:
    try:
        minutes = int(text.strip())
    except ValueError:
        minutes = 30
    _repair_logs[phone]["time_spent_minutes"] = minutes

    _update_state(phone, ConversationState.LOG_REPAIR_STATUS)
    return [
        f"⏱️ Temps : *{minutes} min*\n\n"
        "✅ *Résultat de la réparation ?*\n"
        "1️⃣ *Réussi* — l'appareil fonctionne\n"
        "2️⃣ *Échec* — pas réparable\n"
        "3️⃣ *Partiel* — fonctionne avec limitations"
    ]


async def _handle_log_repair_status(phone: str, text: str, conv: ConversationData) -> list[str]:
    status_map = {
        "1": "reussi", "réussi": "reussi", "reussi": "reussi",
        "oui": "reussi", "ok": "reussi", "marche": "reussi",
        "2": "echec", "échec": "echec", "echec": "echec",
        "non": "echec", "pas réparable": "echec",
        "3": "partiel", "partiel": "partiel",
        "limité": "partiel", "limite": "partiel",
    }
    status = status_map.get(text.strip().lower(), "reussi")
    _repair_logs[phone]["status"] = status

    _update_state(phone, ConversationState.LOG_REPAIR_CONFIRM)

    log = _repair_logs[phone]
    total = log["parts_cost_fcfa"] + log["labor_cost_fcfa"]
    parts_str = ", ".join(log["parts_changed"]) or "Aucune"

    imp = calculate_impact(log.get("device_type", "autre"), status == "reussi")

    confirm = (
        "📋 *Récapitulatif réparation*\n"
        "─" * 30 + "\n"
        f"📌 Ticket : `{log['ticket_id']}`\n"
        f"🧰 Pièces : {parts_str}\n"
        f"💰 Coût pièces : {log['parts_cost_fcfa']} FCFA\n"
        f"🔧 Main-d'œuvre : {log['labor_cost_fcfa']} FCFA\n"
        f"💵 *Total : {total} FCFA*\n"
        f"⏱️ Temps : {log['time_spent_minutes']} min\n"
        f"✅ Statut : {status}\n\n"
        f"🌱 *Impact :* {imp['co2_avoided_kg']} kg CO₂ évités\n"
        f"🗑️ {imp['waste_avoided_kg']} kg déchets détournés\n\n"
        "Confirmer l'enregistrement ?\n"
        "1️⃣ *Oui*, enregistrer\n"
        "2️⃣ *Non*, recommencer\n"
        "0️⃣ Annuler → menu"
    )
    return [confirm]


async def _handle_log_repair_confirm(phone: str, text: str, conv: ConversationData) -> list[str]:
    cleaned = _clean_text(text)

    if cleaned in ["1", "oui", "yes", "ok", "enregistrer"]:
        log = _repair_logs.get(phone, {})
        session_id = add_repair_session(log)

        _update_state(phone, ConversationState.HOME)
        imp = calculate_impact(log.get("device_type", "autre"), log.get("status") == "reussi")

        if session_id:
            msg = (
                "✅ *Réparation enregistrée !*\n\n"
                f"📌 Session : `{session_id}`\n"
                f"📌 Ticket : `{log.get('ticket_id', '?')}`\n\n"
                f"🌱 *Impact climat :* {imp['co2_avoided_kg']} kg CO₂ évités\n"
                f"🗑️ *Déchets sauvés :* {imp['waste_avoided_kg']} kg\n\n"
                "Chaque réparation comptabilisée renforce l'impact de BUTUS ! 💚\n"
                "---\n" + build_home_menu()
            )
        else:
            msg = (
                "⚠️ Enregistrement local (Google Sheets non configuré).\n"
                "Les données sont sauvegardées en mémoire pour la session.\n"
                "---\n" + build_home_menu()
            )

        # Nettoyer les données temporaires
        _repair_logs.pop(phone, None)
        return [msg]

    elif cleaned in ["2", "non", "recommencer"]:
        _update_state(phone, ConversationState.LOG_REPAIR_TICKET)
        _repair_logs.pop(phone, None)
        return ["🔄 *Nouvel enregistrement*\n\n🧰 *Pièces changées ?* (séparez par des virgules)"]

    else:
        _update_state(phone, ConversationState.HOME)
        _repair_logs.pop(phone, None)
        return [build_home_menu()]


# ---------------------------------------------------------------------------
# Pilier 2 — Pièces détachées (catalogue & commande)
# ---------------------------------------------------------------------------

_parts_session: dict[str, dict] = {}


def build_parts_menu() -> str:
    return (
        "🔩 *BUTUS Repair — Pièces détachées*\n\n"
        "Trouvez la pièce qu'il vous faut, available à Lomé 🇹🇬\n\n"
        "1️⃣ *Par appareil* — voir les pièces d'un type\n"
        "2️⃣ *Rechercher* — taper un mot-clé (ex: batterie, écran)\n"
        "3️⃣ *Tout le catalogue* — liste complète\n\n"
        "👉 Répondez avec le numéro, ou écrivez directement votre recherche."
    )


def build_parts_device_menu() -> str:
    cats = get_device_categories()
    lines = ["📱 *Choisir un appareil :*\n"]
    for i, (_, label) in enumerate(cats, 1):
        lines.append(f"{i}️⃣ {label}")
    lines.append("\n👉 Répondez avec le numéro de l'appareil.")
    return "\n".join(lines)


async def _handle_browse_parts(phone: str, text: str, conv: ConversationData) -> list[str]:
    if get_part_by_id(text):
        return await _handle_part_detail(phone, text, conv)

    if text in ["1", "appareil", "par appareil"]:
        _update_state(phone, ConversationState.BROWSE_PARTS_DEVICE)
        return [build_parts_device_menu()]
    if text in ["2", "rechercher", "search"]:
        _update_state(phone, ConversationState.BROWSE_PARTS)
        return ["🔎 *Recherche de pièce*\n\nÉcrivez un mot-clé (ex: *batterie*, *écran*, *chargeur*) :"]
    if text in ["3", "catalogue", "tout", "tous"]:
        parts = get_all_parts()
        return [_format_parts_list(parts, "📦 Catalogue complet")]

    # Recherche directe par mot-clé
    results = search_parts(text)
    if results:
        return [_format_parts_list(results, f"🔎 Résultats pour « {text} »")]
    _update_state(phone, ConversationState.BROWSE_PARTS)
    return [build_parts_menu()]


async def _handle_browse_parts_device(phone: str, text: str, conv: ConversationData) -> list[str]:
    # Si l'utilisateur envoie un ID de pièce, on affiche le détail
    if get_part_by_id(text):
        return await _handle_part_detail(phone, text, conv)

    cats = get_device_categories()
    try:
        idx = int(text) - 1
        key, _ = cats[idx]
    except (ValueError, IndexError):
        return [build_parts_device_menu()]

    _parts_session[phone] = {"device": key}
    parts = get_parts_by_device(key)
    return [_format_parts_list(parts, f"🔩 Pièces pour {cats[idx][1]}")]


def _format_parts_list(parts: list[dict], title: str) -> str:
    lines = [f"{title} ({len(parts)})\n"]
    for p in parts:
        price = f"{p['price_fcfa']:,} FCFA" if p.get("price_fcfa") else "Sur devis"
        lines.append(f"• *{p['name']}* — {price}")
        lines.append(f"  ID: `{p['id']}` | Stock: {p.get('stock', '?')} | {p.get('location', '')}")
    lines.append("\n👉 Envoyez l'*ID* d'une pièce pour voir le détail & commander.")
    return "\n".join(lines)


async def _handle_part_detail(phone: str, text: str, conv: ConversationData) -> list[str]:
    part = get_part_by_id(text)
    if not part:
        return ["❌ Pièce introuvable. Envoyez un ID valide (ex: `BAT-PH-001`)."]
    _parts_session[phone] = {"part_id": part["id"]}
    _update_state(phone, ConversationState.PART_RESERVE)
    return [format_part_detail(part) + "\n\n👉 Tapez *commander* pour réserver, ou *retour* pour le catalogue."]


async def _handle_part_reserve(phone: str, text: str, conv: ConversationData) -> list[str]:
    if text in ["retour", "menu", "annuler"]:
        _update_state(phone, ConversationState.BROWSE_PARTS)
        return [build_parts_menu()]
    if text in ["commander", "reserver", "réserver", "order", "acheter", "oui"]:
        _update_state(phone, ConversationState.PART_RESERVE_CONFIRM)
        return [
            "📝 *Réserver cette pièce*\n\n"
            "Indiquez votre *prénom et numéro WhatsApp* pour confirmation :\n"
            "_(ex: Nancy 90 12 34 56)_"
        ]
    return ["👉 Tapez *commander* pour réserver, ou *retour* pour le catalogue."]


async def _handle_part_reserve_confirm(phone: str, text: str, conv: ConversationData) -> list[str]:
    session = _parts_session.get(phone, {})
    part = get_part_by_id(session.get("part_id", ""))
    extras = []
    if part:
        # Persister dans Google Sheets
        reservation_data = {
            "phone_number": phone,
            "customer_name": conv.customer_name or text.split()[0] if text else "",
            "part_id": part["id"],
            "part_name": part["name"],
            "price_fcfa": part["price_fcfa"],
            "location": part.get("location", ""),
            "contact_raw": text,
        }
        sheet_ok = add_part_reservation(reservation_data)
        if not sheet_ok:
            extras.append("_(sauvegarde locale — Sheets non configuré)_")

        # Notifier le réparateur BUTUS si configuré
        settings = get_settings()
        if settings.butus_notification_phone and sheet_ok:
            notif = (
                f"🛒 *Nouvelle réservation pièce*\n\n"
                f"🔩 {part['name']} ({part['id']})\n"
                f"💰 {part['price_fcfa']:,} FCFA\n"
                f"📞 Client: {phone}\n"
                f"📝 Infos: {text}\n"
                f"📍 Retrait: {part.get('location', '?')}"
            )
            await send_text(settings.butus_notification_phone, notif)

        msg = (
            f"✅ *Demande envoyée !*\n\n"
            f"🔩 {part['name']} ({part['id']})\n"
            f"💰 {part['price_fcfa']:,} FCFA\n"
            f"📍 Retrait: {part.get('location', 'BUTUS Repair, Lomé')}\n\n"
            f"Un réparateur BUTUS vous confirmera la disponibilité sous 24h.\n"
            f"Coordonnées reçues: {text}\n\n"
            "Merci de faire durer vos appareils ! 💚"
        )
    else:
        msg = "❌ Réservation impossible (pièce introuvable)."
    _update_state(phone, ConversationState.HOME)
    _parts_session.pop(phone, None)
    return [msg + "\n\n".join(extras + [""]) + build_home_menu()]


# ---------------------------------------------------------------------------
# Pilier 3 — Appareils reconditionnés
# ---------------------------------------------------------------------------

_recond_store: dict[str, dict] = {}


def build_reconditioned_menu() -> str:
    return (
        "📱 *BUTUS Repair — Appareils reconditionnés*\n\n"
        "Des appareils testés et garantis, économiques et écologiques 🇹🇬\n\n"
        "1️⃣ *Par catégorie* — parcourir par type\n"
        "2️⃣ *Rechercher* — taper un mot-clé (ex: iPhone, TV)\n"
        "3️⃣ *Tout le catalogue* — liste complète\n\n"
        "👉 Répondez avec le numéro, ou écrivez directement votre recherche."
    )


def build_reconditioned_category_menu() -> str:
    cats = get_categories()
    lines = ["📱 *Choisir une catégorie :*\n"]
    for i, (_, label) in enumerate(cats, 1):
        lines.append(f"{i}️⃣ {label}")
    lines.append("\n👉 Répondez avec le numéro de la catégorie.")
    return "\n".join(lines)


async def _handle_reconditioned_menu(phone: str, text: str, conv: ConversationData) -> list[str]:
    if get_by_id(text):
        return await _handle_reconditioned_detail(phone, text, conv)

    if text in ["1", "categorie", "catégorie", "par catégorie"]:
        _update_state(phone, ConversationState.RECONDITIONED_CATEGORY)
        return [build_reconditioned_category_menu()]
    if text in ["2", "rechercher"]:
        _update_state(phone, ConversationState.BROWSE_RECONDITIONED)
        return ["🔎 *Recherche appareil reconditionné*\n\nÉcrivez un mot-clé (ex: *iPhone*, *Samsung*, *TV*) :"]
    if text in ["3", "catalogue", "tout", "tous"]:
        devices = get_all_reconditioned()
        return [format_category_list(devices, "📦 Tous les reconditionnés")]

    # Recherche directe (mots-clés longs uniquement)
    if len(text) >= 3:
        results = search_reconditioned(text)
        if results:
            return [format_category_list(results, f"🔎 Résultats pour « {text} »")]
    return [build_reconditioned_menu()]


async def _handle_reconditioned_category(phone: str, text: str, conv: ConversationData) -> list[str]:
    if get_by_id(text):
        return await _handle_reconditioned_detail(phone, text, conv)

    cats = get_categories()
    try:
        idx = int(text) - 1
        key, label = cats[idx]
    except (ValueError, IndexError):
        return [build_reconditioned_category_menu()]

    _recond_store[phone] = {"category": key}
    devices = get_by_category(key)
    return [format_category_list(devices, f"📱 {label}")]


async def _handle_reconditioned_detail(phone: str, text: str, conv: ConversationData) -> list[str]:
    device = get_by_id(text)
    if not device:
        return ["❌ Appareil introuvable. Envoyez un ID valide (ex: `RC-SMARTPHONE-001`)."]
    _recond_store[phone] = {"device_id": device["id"]}
    _update_state(phone, ConversationState.RECONDITIONED_CONTACT)
    return [format_detail(device)]


async def _handle_reconditioned_contact(phone: str, text: str, conv: ConversationData) -> list[str]:
    if text in ["retour", "menu", "annuler", "0"]:
        _update_state(phone, ConversationState.BROWSE_RECONDITIONED)
        return [build_reconditioned_menu()]

    if text in ["contacter", "acheter", "reserver", "réserver", "oui"]:
        return [
            "📝 *Intéressé par cet appareil ?*\n\n"
            "Indiquez votre *prénom et numéro WhatsApp* :\n"
            "_(ex: Nancy 90 12 34 56)_\n\n"
            "Un conseiller BUTUS vous recontactera sous 24h."
        ]
    if len(text) >= 5:
        device = get_by_id(_recond_store.get(phone, {}).get("device_id", ""))
        extra = ""
        if device:
            settings = get_settings()
            if settings.butus_notification_phone:
                notif = (
                    f"🛒 *Nouveau lead reconditionné*\n\n"
                    f"📱 {device['name']} ({device['id']})\n"
                    f"💰 {device['price_fcfa']:,} FCFA\n"
                    f"📞 Client: {phone}\n"
                    f"📝 Infos: {text}"
                )
                await send_text(settings.butus_notification_phone, notif)
            extra = "_(contact enregistré)_"
        _update_state(phone, ConversationState.HOME)
        _recond_store.pop(phone, None)
        return [
            f"✅ *Demande envoyée !*\n\n"
            f"Un conseiller BUTUS vous recontactera sous 24h.\n"
            f"Coordonnées reçues: {text}\n\n{extra}"
            + "\n\n" + build_home_menu()
        ]
    return ["👉 Tapez *contacter* pour qu'on vous rappelle, ou donnez vos coordonnées."]


# =================== VEILLE STRATÉGIQUE ===================

async def _handle_veille_menu(phone: str, text: str, conv: ConversationData) -> list[str]:
    if text == "0":
        _update_state(phone, ConversationState.HOME)
        return [build_home_menu()]

    topic_info = VEILLE_TOPICS.get(text)
    if topic_info:
        topic_key, topic_label = topic_info
        if topic_key == "personnalisé":
            _update_state(phone, ConversationState.VEILLE_PERSO)
            return [build_perso_instruction()]
        _update_state(phone, ConversationState.VEILLE_TOPIC)
        conv.veille_topic = topic_key
        return ["⏳ *Recherche en cours...* Génération de la synthèse.\n"]
    return [build_veille_menu()]


async def _handle_veille_topic(phone: str, text: str, conv: ConversationData) -> list[str]:
    result = do_veille(conv.veille_topic or "marche")
    if not result:
        _update_state(phone, ConversationState.HOME)
        return [
            "❌ Impossible de générer la veille pour le moment. Réessayez plus tard.\n\n"
            + build_home_menu()
        ]

    parts = _split_long_message(result)
    _update_state(phone, ConversationState.VEILLE_RESULTS)
    parts.append(
        "📡 *Que faire ensuite ?*\n"
        "1️⃣ Nouvelle recherche sur ce sujet\n"
        "2️⃣ Autre sujet de veille\n"
        "0️⃣ Menu principal"
    )
    return parts


async def _handle_veille_results(phone: str, text: str, conv: ConversationData) -> list[str]:
    if text in ["1", "recommencer", "nouveau", "encore"]:
        _update_state(phone, ConversationState.VEILLE_TOPIC)
        return ["⏳ *Génération d'une nouvelle synthèse...*\n"]
    if text in ["2", "autre", "menu veille"]:
        _update_state(phone, ConversationState.VEILLE_MENU)
        return [build_veille_menu()]
    _update_state(phone, ConversationState.HOME)
    return [build_home_menu()]


async def _handle_veille_perso(phone: str, text: str, conv: ConversationData) -> list[str]:
    if text == "0":
        _update_state(phone, ConversationState.HOME)
        return [build_home_menu()]
    if len(text.strip()) < 5:
        return ["Votre question est trop courte. Donnez plus de détails (min 5 caractères).\n\n0️⃣ Menu principal"]

    _update_state(phone, ConversationState.VEILLE_TOPIC)
    conv.veille_topic = "personnalisé"
    conv.veille_custom_question = text.strip()
    return ["⏳ *Analyse de votre question en cours...* Génération de la réponse.\n"]


def _split_long_message(text: str, max_len: int = 1500) -> list[str]:
    if len(text) <= max_len:
        return [text]

    parts = []
    current = ""
    for line in text.split("\n"):
        if len(current) + len(line) + 1 > max_len and current:
            parts.append(current.strip())
            current = line + "\n"
        else:
            current += line + "\n"
    if current.strip():
        parts.append(current.strip())
    return parts
