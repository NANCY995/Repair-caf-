"""Module de veille stratégique — concurrents, marché, réglementation, personnalisé."""

import logging
from typing import Optional
from ai_client import get_text_completion
from duckduckgo_search import DDGS

logger = logging.getLogger("butus-veille")

VEILLE_PROMPTS: dict[str, str] = {
    "concurrents": (
        "Tu es un analyste veille stratégique pour BUTUS Repair, un Repair Café à Lomé, Togo. "
        "Sujet : CONCURRENTS ET ACTEURS LOCAUX\n\n"
        "Génère une synthèse structurée (300-500 mots) sur :\n"
        "• Qui sont les autres réparateurs à Lomé ? (marchands de pièces, "
        "techniciens indépendants, Repair Cafés)\n"
        "• Quels services proposent-ils que BUTUS n'a pas encore ?\n"
        "• Forces et faiblesses perçues\n"
        "• Opportunités pour BUTUS de se différencier\n\n"
        "Structure la réponse en sections claires. Utilise des données plausibles "
        "basées sur le contexte ouest-africain."
    ),
    "marche": (
        "Tu es un analyste veille stratégique pour BUTUS Repair, Lomé, Togo. "
        "Sujet : TENDANCES DU MARCHÉ DE LA RÉPARATION\n\n"
        "Génère une synthèse structurée (300-500 mots) sur :\n"
        "• Tendances des prix des pièces détachées en Afrique de l'Ouest\n"
        "• Disponibilité et délais d'approvisionnement\n"
        "• Marques les plus réparées vs les plus jetées\n"
        "• Évolution du marché des reconditionnés en Afrique francophone\n\n"
        "Donne des ordres de prix en FCFA. Structure en sections claires."
    ),
    "reglementation": (
        "Tu es un conseiller juridique spécialisé économie circulaire en Afrique. "
        "Sujet : RÉGLEMENTATION ET NORMES\n\n"
        "Génère une synthèse structurée (300-500 mots) sur :\n"
        "• Loi togolaise 2019-004 protection des données : implications pour un Repair Café\n"
        "• Réglementation des déchets électroniques (DEEE) au Togo et UEMOA\n"
        "• Normes de qualité pour appareils reconditionnés\n"
        "• Incitations fiscales possibles pour l'économie circulaire\n\n"
        "Structure en sections claires."
    ),
}

VEILLE_TOPICS = {
    "1": ("concurrents", "Concurrents & acteurs locaux"),
    "2": ("marche", "Tendances du marché"),
    "3": ("reglementation", "Réglementation & normes"),
    "4": ("personnalisé", "Personnalisé — votre question"),
}


def build_veille_menu() -> str:
    return (
        "📡 *BUTUS Repair — Veille Stratégique*\n\n"
        "Restez informé des tendances du marché de la réparation à Lomé et en Afrique.\n\n"
        "1️⃣ *Concurrents & acteurs locaux*\n"
        "2️⃣ *Tendances du marché*\n"
        "3️⃣ *Réglementation & normes*\n"
        "4️⃣ *Personnalisé* — posez votre question\n\n"
        "0️⃣ Menu principal\n\n"
        "👉 Répondez avec le numéro de votre choix."
    )


def build_perso_instruction() -> str:
    return (
        "📡 *Veille personnalisée*\n\n"
        "Posez votre question de veille stratégique. Exemples :\n"
        "• *Quelles sont les dernières innovations en réparation smartphone ?*\n"
        "• *Quel est l'impact du Bitcoin sur l'approvisionnement en cartes graphiques à Lomé ?*\n"
        "• *Comment se développe le marché des batteries solaires au Togo ?*\n\n"
        "👉 Écrivez votre question ci-dessous :"
    )


def build_topic_prompt(topic: str, custom_text: str = "") -> str:
    if topic == "personnalisé" and custom_text:
        return (
            "Tu es un analyste veille stratégique pour BUTUS Repair, Lomé, Togo. "
            "Réponds de façon structurée, concise (400-600 mots), avec des insights "
            "actionnables pour un petit réparateur local.\n\n"
            f"Question de l'utilisateur : {custom_text}"
        )
    return VEILLE_PROMPTS.get(topic, VEILLE_PROMPTS["marche"])


def search_web(query: str) -> str:
    """Effectue une recherche web via DuckDuckGo et renvoie les résultats formatés."""
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=5)
            if not results:
                return "Aucun résultat trouvé."
            formatted = []
            for r in results:
                formatted.append(f"- Title: {r.get('title')}\n  Snippet: {r.get('body')}\n  URL: {r.get('href')}")
            return "\n\n".join(formatted)
    except Exception as e:
        logger.warning(f"⚠️ Échec de la recherche web DuckDuckGo: {e}")
        return "Impossible de récupérer des résultats de recherche récents pour le moment."


def do_veille(topic: str, custom_text: str = "") -> Optional[str]:
    # Déterminer la requête de recherche web appropriée
    search_query = ""
    if topic == "concurrents":
        search_query = "reparateur telephone informatique Lomé Togo"
    elif topic == "marche":
        search_query = "prix pieces detachees reparation Afrique de l'Ouest"
    elif topic == "reglementation":
        search_query = "loi protection donnees Togo 2019-004 dechets electroniques UEMOA"
    elif topic == "personnalisé" and custom_text:
        search_query = custom_text

    web_context = ""
    if search_query:
        logger.info(f"🔍 Recherche web pour la veille: {search_query}")
        web_context = search_web(search_query)

    prompt = build_topic_prompt(topic, custom_text)
    
    if web_context:
        prompt = (
            f"Voici des informations récentes trouvées sur le web pour t'aider :\n"
            f"```\n{web_context}\n```\n\n"
            f"En utilisant ces informations récentes ainsi que tes connaissances, réponds au sujet suivant :\n"
            f"{prompt}"
        )

    messages = [
        {"role": "system", "content": "Tu es un analyste veille stratégique. Réponds toujours en français, de façon structurée et professionnelle. Utilise des titres de sections (ex: **Titre**) et des listes à puces. Cite brièvement tes sources si tu utilises les informations web."},
        {"role": "user", "content": prompt},
    ]
    response = get_text_completion(messages, temperature=0.4, max_tokens=1500)
    return response
