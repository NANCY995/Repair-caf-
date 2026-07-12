import httpx
from typing import Optional

from config import get_settings


async def send_text(to: str, text: str) -> bool:
    settings = get_settings()
    if not settings.whatsapp_token or not settings.whatsapp_phone_number_id:
        return False

    url = settings.whatsapp_api_base
    headers = {
        "Authorization": f"Bearer {settings.whatsapp_token}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "text",
        "text": {"body": text},
    }

    async with httpx.AsyncClient(timeout=15) as client:
        try:
            response = await client.post(url, json=payload, headers=headers)
            return response.status_code == 200
        except httpx.HTTPError as e:
            print(f"Erreur envoi WhatsApp: {e}")
            return False


async def send_interactive_list(to: str, header: str, body: str, button_text: str, sections: list[dict]) -> bool:
    """Envoie une liste interactive WhatsApp (pour les menus)."""
    settings = get_settings()
    if not settings.whatsapp_token or not settings.whatsapp_phone_number_id:
        return False

    url = settings.whatsapp_api_base
    headers = {
        "Authorization": f"Bearer {settings.whatsapp_token}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "header": {"type": "text", "text": header},
            "body": {"text": body},
            "footer": {"text": "BUTUS Repair 🇹🇬"},
            "action": {
                "button": button_text,
                "sections": sections,
            },
        },
    }

    async with httpx.AsyncClient(timeout=15) as client:
        try:
            response = await client.post(url, json=payload, headers=headers)
            return response.status_code == 200
        except httpx.HTTPError as e:
            print(f"Erreur envoi liste interactive: {e}")
            return False


async def send_buttons(to: str, body: str, buttons: list[tuple[str, str] | dict]) -> bool:
    """Envoie des boutons interactifs (max 3 boutons)."""
    settings = get_settings()
    if not settings.whatsapp_token or not settings.whatsapp_phone_number_id:
        return False

    url = settings.whatsapp_api_base
    headers = {
        "Authorization": f"Bearer {settings.whatsapp_token}",
        "Content-Type": "application/json",
    }

    rows = []
    for i, btn in enumerate(buttons[:3]):
        if isinstance(btn, dict):
            btn_id = btn.get("id", f"b{i}")
            btn_title = btn.get("title", f"Option {i+1}")[:20]
        else:
            btn_id = f"btn_{i}_{btn[0][:20]}"
            btn_title = btn[0][:20]
        rows.append({
            "type": "reply",
            "reply": {
                "id": btn_id,
                "title": btn_title,
            },
        })

    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": body},
            "action": {"buttons": rows},
        },
    }

    async with httpx.AsyncClient(timeout=15) as client:
        try:
            response = await client.post(url, json=payload, headers=headers)
            return response.status_code == 200
        except httpx.HTTPError as e:
            print(f"Erreur envoi boutons: {e}")
            return False
