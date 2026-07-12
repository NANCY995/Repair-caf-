"""
Utilitaires de sécurité BUTUS Repair.

- Vérification de la signature des webhooks WhatsApp (X-Hub-Signature-256)
- Protection des endpoints d'administration par token
  (en-tête X-Admin-Token / Bearer / Basic, ou query ?token=)
"""

import base64
import hashlib
import hmac
import logging

from config import get_settings
from fastapi import HTTPException, Request
from fastapi.responses import Response

logger = logging.getLogger("butus-security")


def verify_webhook_signature(raw_body: bytes, signature_header: str | None) -> bool:
    """
    Vérifie la signature X-Hub-Signature-256 envoyée par Meta.

    La signature est un HMAC-SHA256 du corps brut de la requête, calculé
    avec le *App Secret* de l'application Meta (pas le verify_token).
    """
    settings = get_settings()
    secret = settings.whatsapp_app_secret

    if not secret:
        if settings.is_production:
            logger.error("❌ whatsapp_app_secret manquant — webhook NON sécurisé en production")
            return False
        logger.warning("⚠️ whatsapp_app_secret non configuré — signature webhook désactivée (DEV)")
        return True

    if not signature_header or not signature_header.startswith("sha256="):
        logger.warning("⚠️ En-tête X-Hub-Signature-256 absent ou invalide")
        return False

    expected = hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
    provided = signature_header[len("sha256="):]

    if not hmac.compare_digest(provided, expected):
        logger.warning("⚠️ Signature webhook invalide")
        return False

    return True


def _extract_token(request: Request) -> str | None:
    """Récupère le token depuis X-Admin-Token, Bearer, Basic ou ?token=."""
    provided = request.headers.get("X-Admin-Token")
    if provided:
        return provided

    auth = request.headers.get("Authorization", "")
    if auth.lower().startswith("bearer "):
        return auth[7:]
    if auth.lower().startswith("basic "):
        try:
            decoded = base64.b64decode(auth[6:]).decode("utf-8")
            _, password = decoded.split(":", 1)
            return password
        except Exception:
            return None

    return request.query_params.get("token")


def verify_admin_token(request: Request, html: bool = False) -> None:
    """
    Protège un endpoint d'administration.

    - API (html=False) : 403 si token manquant/invalide.
    - Page HTML (html=True) : 401 + WWW-Authenticate Basic pour que le
      navigateur affiche la boîte de dialogue native (les requêtes
      same-origin suivantes incluent alors l'en-tête automatiquement).

    En DEV sans token configuré, l'accès reste ouvert (avertissement log).
    """
    settings = get_settings()
    token = settings.admin_api_token

    if not token:
        if settings.is_production:
            logger.error("❌ admin_api_token manquant — endpoints admin NON sécurisés en production")
            if html:
                raise _unauthorized()
            raise HTTPException(status_code=403, detail="Configuration sécurité manquante")
        logger.warning("⚠️ admin_api_token non configuré — accès admin ouvert (DEV)")
        return

    provided = _extract_token(request)
    if not provided or not hmac.compare_digest(provided, token):
        logger.warning("⚠️ Tentative d'accès admin sans token valide")
        if html:
            raise _unauthorized()
        raise HTTPException(status_code=403, detail="Accès refusé")


def _unauthorized() -> HTTPException:
    return HTTPException(
        status_code=401,
        detail="Accès refusé",
        headers={"WWW-Authenticate": 'Basic realm="BUTUS Admin"'},
    )


# --- Rate limiting simple (in-memory) ---
import time
from collections import defaultdict

_rate_store: dict[str, list[float]] = defaultdict(list)


def check_rate_limit(request: Request, max_requests: int = 30, window_seconds: int = 60) -> None:
    """
    Limite le nombre de requêtes par IP sur une fenêtre glissante.
    Lève HTTPException 429 si le quota est dépassé.
    """
    key = request.client.host if request.client else "unknown"
    now = time.time()
    cutoff = now - window_seconds
    _rate_store[key] = [t for t in _rate_store[key] if t > cutoff]
    if len(_rate_store[key]) >= max_requests:
        logger.warning(f"⚠️ Rate limit atteint pour {key}")
        raise HTTPException(
            status_code=429,
            detail="Trop de requêtes. Réessayez dans une minute.",
        )
    _rate_store[key].append(now)
