"""
Moteur de diagnostic BUTUS Repair.
Utilise la base de connaissance locale d'abord, puis le LLM en renfort.
"""

import json
from typing import Optional

from config import get_settings
from models import DiagnosisRequest, DiagnosisResponse
from knowledge_base import get_knowledge, get_symptom_diagnosis, format_issue_response
from ai_client import get_completion


SYSTEM_PROMPT = """Tu es le **Copilote IA de BUTUS Repair**, un assistant de diagnostic pour réparateurs et bénévoles d'un Repair Café à Lomé, Togo.

## CONTEXTE
- Tu aides des gens au Togo à réparer leurs appareils électroménagers et électroniques.
- Les pièces de rechange doivent être disponibles localement (Lomé, marchés, quincailleries).
- Le courant peut être instable (variations de tension, coupures fréquentes).
- Beaucoup d'appareils sont de marques asiatiques et européennes courantes en Afrique de l'Ouest.
- Les gens ont des outils de base (tournevis, multimètre, fer à souder).

## RÈGLES DE RÉPONSE
1. Sois pédagogique et patient — explique *pourquoi* faire chaque étape.
2. Propose d'abord les solutions gratuites ou low-cost avant de suggérer de changer des pièces.
3. Si le problème implique le 220V, de l'eau, du gaz ou des hautes tensions → préviens du DANGER.
4. Cite les prix en FCFA quand tu proposes des pièces.
5. Indique où trouver les pièces à Lomé si possible (marchés, quincailleries).
6. Si le diagnostic est complexe : recommande de contacter un réparateur BUTUS.
7. N'invente PAS de diagnostic — si tu n'es pas sûr, dis-le.

## FORMAT DE RÉPONSE
Retourne UNIQUEMENT un objet JSON valide :

{
  "possible_causes": ["cause courte 1", "cause courte 2"],
  "steps_to_try": ["1. Étape détaillée", "2. Étape détaillée"],
  "parts_needed": ["pièce ~ prix FCFA"] ou null,
  "local_shops": ["boutique 1", "boutique 2"] ou null,
  "urgency": "faible" | "moyenne" | "urgente" | "dangereux",
  "can_self_repair": true | false,
  "recommendation": "Paragraphe complet en français avec explications claires",
  "follow_up_questions": ["Question pour préciser le diagnostic"] ou null
}

Ne retourne RIEN d'autre que ce JSON."""


# ===================== MOTEUR DE DIAGNOSTIC =====================


def diagnose(req: DiagnosisRequest) -> Optional[DiagnosisResponse]:
    """
    Diagnostic en 3 couches :
    1. Base de connaissance locale (KB) — rapide et gratuit
    2. LLM (OpenAI) — si KB insuffisante
    3. Fallback — si tout échoue
    """
    # --- Couche 1 : Base de connaissance locale ---
    kb_result = _diagnose_from_knowledge_base(req)
    if kb_result:
        return kb_result

    # --- Couche 2 : LLM ---
    llm_result = _diagnose_with_llm(req)
    if llm_result:
        return llm_result

    # --- Couche 3 : Fallback ---
    return _fallback_diagnosis(req)


def _diagnose_from_knowledge_base(req: DiagnosisRequest) -> Optional[DiagnosisResponse]:
    """Cherche dans la base de connaissance locale."""
    kb = get_knowledge(req.device_type)
    if not kb:
        return None

    # Extraire des mots-clés de la description de panne
    issue_lower = req.issue_description.lower()
    keywords = issue_lower.split()[:10]  # premiers mots significatifs

    matches = get_symptom_diagnosis(req.device_type, [req.issue_description] + keywords)

    if matches:
        best = matches[0]
        parts = best.get("parts")
        local_shops = kb.get("local_shops", [])

        return DiagnosisResponse(
            possible_causes=best.get("causes", ["Cause non identifiée"]),
            steps_to_try=best.get("steps", ["Consultez un réparateur"]),
            parts_needed=parts if parts else None,
            urgency="dangereux" if best.get("danger") else ("moyenne" if not best.get("self_repair") else "faible"),
            can_self_repair=best.get("self_repair", False),
            recommendation=f"Diagnostic basé sur notre base de connaissance pour {kb['emoji']} {kb['name']}.\n\n→ {best['symptom']}\n\nSuivez les étapes ci-dessus. {'⚠️ Attention danger !' if best.get('danger') else ''}",
        )

    # Pas de correspondance exacte → retourne les infos générales de l'appareil
    return DiagnosisResponse(
        possible_causes=[f"Panne non spécifique sur {kb['name']}"],
        steps_to_try=[
            "1. Vérifiez l'alimentation électrique (prise, câble, fusible)",
            "2. Inspectez visuellement : composants brûlés ? Odeur ? Bruit ?",
            "3. Consultez les symptômes courants dans notre base",
        ],
        parts_needed=None,
        urgency="moyenne",
        can_self_repair=True,
        recommendation=f"Votre {kb['emoji']} {kb['name']} présente des symptômes que nous n'avons pas encore dans notre base. Voici les vérifications de base à faire. Contactez un réparateur BUTUS si le problème persiste.",
    )


def _diagnose_with_llm(req: DiagnosisRequest) -> Optional[DiagnosisResponse]:
    """Utilise le LLM (OpenAI ou Gemini) pour le diagnostic. Silently fails si non configuré."""
    if not _is_llm_configured():
        return None

    # Enrichir le prompt avec la base de connaissance si disponible
    kb = get_knowledge(req.device_type)
    kb_context = ""
    if kb:
        issues_text = []
        for issue in kb.get("common_issues", []):
            issues_text.append(f"- {issue['symptom']} : causes={issue['causes'][:2]}")
        kb_context = "\n".join([
            f"Appareil reconnu : {kb['emoji']} {kb['name']}",
            "Symptômes connus dans notre base :",
            *issues_text,
            "",
            "Utilise ces info si la panne correspond, sinon fais appel à tes connaissances générales.",
        ])

    user_prompt = f"""Appareil : {req.device_type}
Marque : {req.device_brand}
Modèle : {req.device_model}
Description de la panne : {req.issue_description}
Langue : {req.language}

{kb_context if kb_context else "Appareil non référencé dans notre base. Utilise tes connaissances générales."}"""

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]

    try:
        data = get_completion(messages, temperature=0.3, max_tokens=1000)
        if not data:
            return None

        return DiagnosisResponse(
            possible_causes=data.get("possible_causes", ["Cause non identifiée"]),
            steps_to_try=data.get("steps_to_try", ["Consultez un réparateur"]),
            parts_needed=data.get("parts_needed"),
            urgency=data.get("urgency", "moyenne"),
            can_self_repair=data.get("can_self_repair", True),
            recommendation=data.get("recommendation", "Pas de diagnostic disponible."),
        )
    except Exception as e:
        print(f"Erreur LLM: {e}")
        return None


def _is_llm_configured() -> bool:
    """Vérifie si un LLM (OpenAI ou Gemini) est configuré."""
    settings = get_settings()
    if settings.ai_provider == "gemini":
        return bool(settings.gemini_api_key)
    return bool(settings.openai_api_key)


def _fallback_diagnosis(req: DiagnosisRequest) -> DiagnosisResponse:
    """Diagnostic de dernier recours quand KB + LLM échouent."""
    return DiagnosisResponse(
        possible_causes=[
            "Problème d'alimentation électrique (courant instable, coupure)",
            "Composant interne fatigué ou grillé",
            "Connexion desserrée ou oxydée",
            "Pièce d'usure en fin de vie",
        ],
        steps_to_try=[
            "1. Débranchez l'appareil 5 minutes puis rebranchez-le",
            "2. Vérifiez la prise avec une autre lampe ou appareil",
            "3. Inspectez le câble d'alimentation : coupure ? brûlure ?",
            "4. Cherchez des odeurs de brûlé, des composants noircis",
            "5. Si rien n'a fonctionné, contactez un réparateur BUTUS",
        ],
        parts_needed=None,
        urgency="moyenne",
        can_self_repair=False,
        recommendation=(
            f"Votre **{req.device_type} {req.device_brand}** ({req.device_model}) "
            f"a le problème suivant : _{req.issue_description[:100]}_.\n\n"
            "Je n'ai pas pu identifier la cause exacte avec les informations actuelles.\n\n"
            "**Prochaine étape :** Je vous recommande de créer un ticket pour qu'un "
            "réparateur BUTUS examine l'appareil en personne. C'est gratuit et sans engagement.\n\n"
            "👉 Répondez **OUI** pour créer un ticket maintenant."
        ),
    )


# ===================== UTILITAIRES =====================


def get_device_info(device_type: str) -> dict | None:
    """Retourne les infos générales d'un appareil (pour la rubrique 'Fiches techniques')."""
    return get_knowledge(device_type)


def get_device_impact(device_type: str) -> dict:
    """Retourne les données d'impact CO₂ pour un appareil."""
    kb = get_knowledge(device_type)
    if not kb:
        return {"weight_kg": 5.0, "co2_per_unit_kg": 25.0}
    return {
        "weight_kg": kb.get("weight_kg", 5.0),
        "co2_per_unit_kg": kb.get("co2_per_unit_kg", 25.0),
    }


def get_all_device_names() -> list[str]:
    """Retourne la liste de tous les appareils connus."""
    from knowledge_base import DEVICE_KNOWLEDGE
    return [v["name"] for v in DEVICE_KNOWLEDGE.values() if v["name"] != "Autre appareil"]
