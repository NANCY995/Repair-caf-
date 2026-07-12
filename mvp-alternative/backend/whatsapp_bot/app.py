import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import json
import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel

from config import get_settings
from conversation import handle_message, pop_interactive
from knowledge_base import get_knowledge, DEVICE_KNOWLEDGE
from diagnostic import get_all_device_names
from parts_catalog import get_all_parts, get_parts_by_device, search_parts, get_part_by_id

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("butus-whatsapp")
from datetime import datetime
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler

VEILLE_FILE = "latest_veille.json"

def get_latest_veille() -> dict:
    if os.path.exists(VEILLE_FILE):
        try:
            with open(VEILLE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"date": None, "content": "Aucune veille hebdomadaire disponible pour le moment."}

def save_latest_veille(content: str):
    data = {
        "date": datetime.now().strftime("%d/%m/%Y à %H:%M"),
        "content": content
    }
    try:
        with open(VEILLE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde de la veille: {e}")

async def run_weekly_veille():
    logger.info("📡 Lancement de la veille hebdomadaire automatique...")
    try:
        from veille import do_veille
        prompt_custom = (
            "Réalise une veille complète et hebdomadaire de la réparation en Afrique de l'Ouest (Lomé, Togo).\n"
            "Aborde en 3 sections :\n"
            "1. Prix et disponibilité des pièces (écrans, batteries, ventilateurs)\n"
            "2. Actualités des concurrents et réparateurs à Lomé\n"
            "3. Nouvelles réglementations ou initiatives écologiques locales au Togo."
        )
        # do_veille uses search_web internally so it will be up to date
        result = do_veille("personnalisé", prompt_custom)
        if result:
            save_latest_veille(result)
            logger.info("✅ Veille hebdomadaire sauvegardée avec succès.")
        else:
            logger.error("❌ Échec de la génération de la veille hebdomadaire (résultat vide).")
    except Exception as e:
        logger.error(f"❌ Erreur lors de la génération de la veille hebdomadaire: {e}", exc_info=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 BUTUS WhatsApp Bot démarré")
    logger.info(f"📚 {len(get_all_device_names())} fiches techniques chargées")
    
    # Démarrage du planificateur de tâches
    scheduler = AsyncIOScheduler()
    # Planification hebdomadaire (chaque lundi à 08:00)
    scheduler.add_job(run_weekly_veille, "cron", day_of_week="mon", hour=8, minute=0)
    scheduler.start()
    logger.info("⏰ Planificateur APScheduler démarré (veille programmée le lundi à 08h00)")
    
    # Lancement d'une veille initiale asynchrone si aucune n'a encore été générée
    if not os.path.exists(VEILLE_FILE):
        logger.info("📡 Première veille manquante, génération en arrière-plan...")
        asyncio.create_task(run_weekly_veille())
        
    yield
    scheduler.shutdown()
    logger.info("🛑 BUTUS WhatsApp Bot arrêté")


app = FastAPI(
    title="BUTUS Repair — API WhatsApp Bot",
    description="Assistant diagnostic IA pour BUTUS Repair (Lomé, Togo)",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS — allowlist configurable via CORS_ORIGINS
_cors_origins = get_settings().cors_origins.split(",") if get_settings().cors_origins else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# Headers de sécurité de base
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    if get_settings().is_production:
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response


@app.get("/")
async def root():
    return {
        "service": "BUTUS Repair WhatsApp Bot",
        "version": "2.0.0",
        "status": "running",
        "devices_in_knowledge_base": len(get_all_device_names()),
    }


@app.get("/health")
async def health():
    settings = get_settings()
    return {
        "status": "healthy",
        "environment": settings.app_env,
        "whatsapp_configured": bool(settings.whatsapp_token and settings.whatsapp_phone_number_id),
        "sheets_configured": bool(settings.google_sheets_spreadsheet_id),
        "ia_configured": bool(settings.openai_api_key) or bool(settings.gemini_api_key),
        "ai_provider": settings.ai_provider,
    }


# ==================== WEBHOOK WHATSAPP ====================

@app.get("/webhook/whatsapp")
async def verify_webhook(request: Request):
    settings = get_settings()

    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == settings.whatsapp_verify_token:
        logger.info("✅ Webhook WhatsApp vérifié")
        return int(challenge) if challenge else 200

    raise HTTPException(status_code=403, detail="Échec vérification webhook")


@app.post("/webhook/whatsapp")
async def webhook_receive(request: Request):
    from security import check_rate_limit, verify_webhook_signature

    # Rate limiting WhatsApp : 30 requêtes / min / IP
    check_rate_limit(request, max_requests=30, window_seconds=60)

    raw_body = await request.body()

    # Vérification de la signature Meta (anti-spoofing)
    signature = request.headers.get("X-Hub-Signature-256")
    if not verify_webhook_signature(raw_body, signature):
        raise HTTPException(status_code=403, detail="Signature webhook invalide")

    try:
        body = json.loads(raw_body.decode("utf-8"))
    except Exception:
        raise HTTPException(status_code=400, detail="Corps invalide")

    logger.info("📩 Webhook WhatsApp reçu (signature OK)")

    entry = body.get("entry", [{}])[0]
    changes = entry.get("changes", [{}])[0]
    value = changes.get("value", {})

    if "messages" in value:
        for msg in value["messages"]:
            if msg.get("type") == "text":
                from_number = msg["from"]
                text = msg["text"]["body"]

                logger.info(f"💬 Message de {from_number[-4:]}: {text[:100]}")

                try:
                    responses = await handle_message(from_number, text)
                except Exception as e:
                    logger.error(f"❌ Erreur: {e}", exc_info=True)
                    responses = [
                        "❌ Erreur technique. Veuillez réessayer.\n\n0️⃣ Menu principal"
                    ]

                # Envoyer chaque réponse via WhatsApp
                from whatsapp import send_text, send_interactive_list, send_buttons
                interactive = pop_interactive(from_number)
                if interactive:
                    if interactive["type"] == "list":
                        await send_interactive_list(from_number, interactive)
                    elif interactive["type"] == "button":
                        await send_buttons(from_number, interactive["body"], interactive["buttons"])
                    # Ne pas envoyer le 1er texte (remplacé par l'interactif)
                    for response_text in responses[1:]:
                        await send_text(from_number, response_text)
                else:
                    for response_text in responses:
                        await send_text(from_number, response_text)

    return {"status": "ok"}


# ==================== FICHES TECHNIQUES API ====================

@app.get("/api/fiches")
async def list_fiches():
    """Liste toutes les fiches techniques disponibles."""
    return {
        "count": len(get_all_device_names()),
        "devices": [
            {
                "name": name,
                "emoji": get_knowledge(name).get("emoji", "📖") if get_knowledge(name) else "📖",
                "issues_count": len(get_knowledge(name).get("common_issues", [])) if get_knowledge(name) else 0,
            }
            for name in get_all_device_names()
        ],
    }


@app.get("/api/fiches/{device_name}")
async def get_fiche(device_name: str):
    """Fiche technique détaillée pour un appareil."""
    kb = get_knowledge(device_name)
    if not kb:
        raise HTTPException(status_code=404, detail=f"Fiche '{device_name}' non trouvée")

    return {
        "name": kb["name"],
        "emoji": kb["emoji"],
        "issues": [
            {
                "symptom": issue["symptom"],
                "causes": issue["causes"],
                "steps": issue["steps"],
                "parts": issue.get("parts"),
                "self_repair": issue.get("self_repair", False),
                "danger": issue.get("danger", False),
            }
            for issue in kb.get("common_issues", [])
        ],
        "local_shops": kb.get("local_shops", []),
    }


@app.get("/api/fiches/{device_name}/search")
async def search_in_fiche(device_name: str, q: str = Query(..., description="Terme de recherche")):
    """Cherche un symptôme dans une fiche technique."""
    kb = get_knowledge(device_name)
    if not kb:
        raise HTTPException(status_code=404, detail="Fiche non trouvée")

    results = []
    query = q.lower()
    for issue in kb.get("common_issues", []):
        if (query in issue["symptom"].lower() or
            any(query in c.lower() for c in issue["causes"]) or
            any(query in s.lower() for s in issue["steps"])):
            results.append({
                "symptom": issue["symptom"],
                "causes": issue["causes"],
                "steps": issue["steps"],
            })

    return {
        "query": q,
        "results_count": len(results),
        "results": results,
    }


@app.get("/api/parts")
async def get_parts(device: str = Query(None, description="Filtrer par type d'appareil")):
    """Retourne le catalogue de pièces détachées (Pilier 2)."""
    if device:
        parts = get_parts_by_device(device)
    else:
        parts = get_all_parts()
    return {
        "count": len(parts),
        "device_filter": device,
        "parts": parts,
    }


@app.get("/api/parts/search")
async def search_parts_endpoint(q: str = Query(..., description="Mot-clé de recherche")):
    """Recherche une pièce par mot-clé."""
    results = search_parts(q)
    return {
        "query": q,
        "count": len(results),
        "parts": results,
    }


@app.get("/api/parts/{part_id}")
async def get_part_endpoint(part_id: str):
    """Détail d'une pièce par son ID."""
    part = get_part_by_id(part_id)
    if not part:
        raise HTTPException(status_code=404, detail="Pièce non trouvée")
    return part


# ==================== APPAREILS RECONDITIONNÉS (Pilier 3) ====================

@app.get("/api/reconditioned")
async def get_reconditioned(category: str = Query(None, description="Filtrer par catégorie (smartphone, ordinateur, television, electromenager)")):
    from reconditioned_catalog import get_all_reconditioned, get_by_category
    if category:
        devices = get_by_category(category)
    else:
        devices = get_all_reconditioned()
    return {"count": len(devices), "category_filter": category, "devices": devices}


@app.get("/api/reconditioned/search")
async def search_reconditioned_endpoint(q: str = Query(..., description="Mot-clé")):
    from reconditioned_catalog import search_reconditioned
    results = search_reconditioned(q)
    return {"query": q, "count": len(results), "devices": results}


@app.get("/api/reconditioned/{device_id}")
async def get_reconditioned_detail(device_id: str):
    from reconditioned_catalog import get_by_id
    device = get_by_id(device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Appareil non trouvé")
    return device


# ==================== ENDPOINTS DE TEST ====================

class TestSendPayload(BaseModel):
    from_: str = "test-user"
    text: str

    model_config = {
        "populate_by_name": True,
        "alias_generator": lambda s: "from" if s == "from_" else s,
    }


@app.post("/api/test/send")
async def test_send_message(request: Request, payload: TestSendPayload):
    """Simule un message WhatsApp (test)."""
    from security import check_rate_limit, verify_admin_token

    # Pas de rate limit si admin authentifié
    is_admin = False
    try:
        verify_admin_token(request)
        is_admin = True
    except HTTPException:
        pass

    if not is_admin:
        check_rate_limit(request, max_requests=15, window_seconds=60)
        verify_admin_token(request)

    from_number = payload.from_
    text = payload.text

    if not text:
        raise HTTPException(status_code=400, detail="Le champ 'text' est requis")

    responses = await handle_message(from_number, text)
    interactive = pop_interactive(from_number)
    result = {
        "from": from_number,
        "received": text,
        "responses": responses,
        "responses_count": len(responses),
    }
    if interactive:
        result["interactive"] = {
            "type": interactive["type"],
            "rows": len(interactive.get("sections", [{}])[0].get("rows", [])),
            "buttons": len(interactive.get("buttons", [])),
        }
    return result


@app.get("/api/conversations/active")
async def list_active_conversations(request: Request):
    """Conversations actives en mémoire."""
    from security import verify_admin_token
    verify_admin_token(request)

    from conversation import conversations
    return {
        "count": len(conversations),
        "conversations": [
            {
                "phone": phone[-4:],  # masqué
                "state": conv.state.value,
                "device_type": conv.device_type,
                "updated_at": conv.updated_at.isoformat(),
            }
            for phone, conv in conversations.items()
        ],
    }


@app.post("/api/conversations/reset")
async def reset_conversation(request: Request, payload: dict):
    """Réinitialise une conversation (debug)."""
    from security import verify_admin_token
    verify_admin_token(request)

    phone = payload.get("phone", "")
    if phone:
        from conversation import conversations
        if phone in conversations:
            del conversations[phone]
            return {"status": "reset", "phone": phone}
    return {"status": "not_found"}


# ==================== DASHBOARD MINIMAL ====================

@app.get("/api/stats")
async def get_stats(request: Request):
    """Statistiques d'utilisation."""
    from security import verify_admin_token
    verify_admin_token(request)

    from conversation import conversations
    active = len(conversations)
    states = {}
    for conv in conversations.values():
        s = conv.state.value
        states[s] = states.get(s, 0) + 1

    return {
        "active_conversations": active,
        "states_distribution": states,
        "knowledge_base_devices": len(get_all_device_names()),
        "total_issues_in_kb": sum(
            len(kb.get("common_issues", []))
            for name, kb in DEVICE_KNOWLEDGE.items()
        ),
    }

# ==================== VEILLE STRATÉGIQUE API ====================

class VeilleRequest(BaseModel):
    topic: str = "marche"
    custom_text: str = ""

class VeilleResponse(BaseModel):
    topic: str
    result: str


@app.post("/api/veille", response_model=VeilleResponse)
async def api_veille(request: Request, payload: VeilleRequest):
    """Génère une synthèse de veille stratégique via Gemini."""
    from security import verify_admin_token
    verify_admin_token(request)

    from veille import do_veille
    result = do_veille(payload.topic, payload.custom_text)
    if not result:
        raise HTTPException(status_code=500, detail="Erreur génération veille")

    return VeilleResponse(topic=payload.topic, result=result)


@app.get("/api/veille/topics")
async def api_veille_topics():
    """Liste les sujets de veille disponibles."""
    from veille import VEILLE_TOPICS
    return {
        "topics": [
            {"id": k, "key": v[0], "label": v[1]}
            for k, v in VEILLE_TOPICS.items()
        ]
    }

# ==================== SESSIONS DE RÉPARATION API ====================

SESSION_STORE: dict[str, dict] = {}  # stockage mémoire fallback


class RepairSessionIn(BaseModel):
    ticket_id: str
    phone_number: str = ""
    device_type: str = ""
    device_brand: str = ""
    device_model: str = ""
    parts_changed: list[str] = []
    parts_cost_fcfa: float = 0
    labor_cost_fcfa: float = 0
    total_cost_fcfa: float = 0
    time_spent_minutes: int = 0
    test_results: str = ""
    status: str = "en_cours"
    technician_name: str = ""
    notes: str = ""


@app.post("/api/sessions")
async def create_session(request: Request, session: RepairSessionIn):
    """Enregistre une session de réparation."""
    from security import verify_admin_token
    verify_admin_token(request)

    from sheets import add_repair_session
    from datetime import datetime
    data = session.model_dump()

    # Calculer le total
    data["total_cost_fcfa"] = session.parts_cost_fcfa + session.labor_cost_fcfa

    session_id = add_repair_session(data)

    if not session_id:
        # Fallback mémoire
        session_id = f"SR-{datetime.now().strftime('%Y%m%d%H%M%S')}-mem"
        data["session_id"] = session_id
        SESSION_STORE[session_id] = data

    # Calculer l'impact
    from impact_calculator import calculate_impact
    impact = calculate_impact(session.device_type or "autre", session.status == "reussi")

    return {
        "session_id": session_id,
        "impact": impact,
        "message": "Session de réparation enregistrée",
    }


@app.get("/api/sessions")
async def list_sessions(request: Request, limit: int = 50):
    """Liste les dernières sessions de réparation."""
    from security import verify_admin_token
    verify_admin_token(request)

    from sheets import get_all_sessions
    sessions = get_all_sessions() or []

    # Ajouter les sessions mémoire
    for sid, s in SESSION_STORE.items():
        sessions.append(s)

    return {
        "total": len(sessions),
        "sessions": sessions[-limit:],
    }


# ==================== DASHBOARD ====================

@app.get("/api/dashboard")
async def get_dashboard(request: Request):
    """Tableau de bord complet avec indicateurs d'impact."""
    from security import verify_admin_token
    verify_admin_token(request)

    from sheets import get_all_tickets, get_all_sessions
    from impact_calculator import get_dashboard_stats

    tickets = get_all_tickets() or []
    sessions = get_all_sessions() or []

    # Ajouter sessions mémoire
    for sid, s in SESSION_STORE.items():
        sessions.append(s)

    stats = get_dashboard_stats(sessions, tickets)
    stats["latest_veille"] = get_latest_veille()
    return stats


@app.get("/dashboard")
async def dashboard_page(request: Request):
    """Page HTML du tableau de bord d'impact."""
    from security import verify_admin_token
    verify_admin_token(request, html=True)

    return """
<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>BUTUS Repair — Dashboard Impact</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: system-ui, sans-serif; background: #f0fdf4; padding: 20px; }
    .container { max-width: 1100px; margin: 0 auto; }
    h1 { font-size: 28px; color: #1a1a2e; margin-bottom: 8px; display: flex; align-items: center; gap: 10px; }
    .subtitle { color: #666; margin-bottom: 24px; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; margin-bottom: 24px; }
    .card { background: white; border-radius: 12px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
    .card h3 { font-size: 14px; color: #666; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; }
    .card .value { font-size: 32px; font-weight: 700; color: #1a1a2e; }
    .card .unit { font-size: 14px; color: #888; }
    .card.green { border-left: 4px solid #2ecc71; }
    .card.blue { border-left: 4px solid #3498db; }
    .card.orange { border-left: 4px solid #e67e22; }
    .card.purple { border-left: 4px solid #9b59b6; }
    .chart-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 24px; }
    table { width: 100%; border-collapse: collapse; font-size: 14px; }
    th, td { text-align: left; padding: 10px 12px; border-bottom: 1px solid #eee; }
    th { background: #f8faf8; font-weight: 600; color: #555; }
    .badge { display: inline-block; padding: 2px 10px; border-radius: 20px; font-size: 12px; font-weight: 600; }
    .badge-success { background: #d4edda; color: #155724; }
    .badge-warning { background: #fff3cd; color: #856404; }
    .badge-danger { background: #f8d7da; color: #721c24; }
    .badge-info { background: #d1ecf1; color: #0c5460; }
    @media (max-width: 700px) { .chart-row { grid-template-columns: 1fr; } }
    .loading { text-align: center; padding: 60px; color: #999; }
    .footer { text-align: center; color: #aaa; font-size: 12px; margin-top: 40px; }
    .veille-text { font-family: inherit; font-size: 14px; line-height: 1.6; background: #fafafa; border: 1px solid #eee; border-radius: 8px; padding: 15px; max-height: 350px; overflow-y: auto; white-space: pre-wrap; margin-top: 10px; }
  </style>
</head>
<body>
  <div class="container">
    <h1>🌍 BUTUS Repair — Impact Dashboard</h1>
    <p class="subtitle">Tableau de bord automatique des indicateurs d'impact</p>
    <div id="loading" class="loading">⏳ Chargement...</div>

    <div id="content" style="display:none;">
      <div class="grid" id="kpiGrid"></div>
      <div class="chart-row">
        <div class="card"><h3>CO₂ évité par type d'appareil</h3><canvas id="co2Chart"></canvas></div>
        <div class="card"><h3>Répartition des réparations</h3><canvas id="repairChart"></canvas></div>
      </div>
      <div class="card"><h3>Top pannes les plus fréquentes</h3><div id="topIssues"></div></div>
      <div class="card" style="margin-top:16px;"><h3>📡 Dernière Veille Hebdomadaire <span id="veilleDate" style="font-size:12px;color:#888;text-transform:none;"></span></h3><div id="veilleContent" class="veille-text"></div></div>
      <div class="card" style="margin-top:16px;"><h3>Sessions de réparation récentes</h3><table id="sessionsTable"><thead><tr><th>Session</th><th>Appareil</th><th>Pièces</th><th>Coût</th><th>Statut</th><th>CO₂ évité</th></tr></thead><tbody id="sessionsBody"></tbody></table></div>
    </div>
    <p class="footer">BUTUS Repair 🇹🇬 — Lomé, Togo — Données mises à jour en temps réel</p>
  </div>

  <script>
    async function loadDashboard() {
      try {
        const res = await fetch('/api/dashboard');
        const data = await res.json();
        document.getElementById('loading').style.display = 'none';
        document.getElementById('content').style.display = 'block';

        // KPI cards
        const impact = data.impact || {};
        document.getElementById('kpiGrid').innerHTML = `
          <div class="card green"><h3>✅ Appareils réparés</h3><div class="value">${impact.total_repaired || 0}</div><div class="unit">sur ${impact.total_devices || 0} traités</div></div>
          <div class="card blue"><h3>🌱 CO₂ évité</h3><div class="value">${impact.total_co2_avoided_kg || 0}</div><div class="unit">kg (${impact.total_co2_avoided_tons || 0} tonnes)</div></div>
          <div class="card orange"><h3>🗑️ Déchets détournés</h3><div class="value">${impact.total_waste_avoided_kg || 0}</div><div class="unit">kg</div></div>
          <div class="card purple"><h3>📊 Taux de succès</h3><div class="value">${impact.repair_rate || 0}%</div><div class="unit">des réparations</div></div>
        `;

        // CO2 chart
        const co2Data = impact.co2_by_device || {};
        new Chart(document.getElementById('co2Chart'), {
          type: 'bar', data: {
            labels: Object.keys(co2Data),
            datasets: [{ label: 'kg CO₂ évité par appareil', data: Object.values(co2Data), backgroundColor: '#2ecc71' }]
          },
          options: { responsive: true, plugins: { legend: { display: false } } }
        });

        // Repair pie chart
        const byType = impact.devices_by_type || {};
        new Chart(document.getElementById('repairChart'), {
          type: 'pie', data: {
            labels: Object.keys(byType),
            datasets: [{ data: Object.values(byType), backgroundColor: ['#2ecc71','#3498db','#e67e22','#9b59b6','#e74c3c','#1abc9c','#f39c12'] }]
          },
          options: { responsive: true }
        });

        // Top issues
        const issues = data.top_issues || [];
        document.getElementById('topIssues').innerHTML = issues.length ? `
          <table><thead><tr><th>Symptôme</th><th>Occurrences</th></tr></thead><tbody>
          ${issues.map(i => `<tr><td>${i.symptom}</td><td><strong>${i.count}</strong></td></tr>`).join('')}
          </tbody></table>` : '<p style="color:#999;padding:12px;">Aucune donnée suffisante</p>';

        // Veille
        const veille = data.latest_veille || {};
        document.getElementById('veilleDate').textContent = veille.date ? `(Générée le ${veille.date})` : "(Génération en cours...)";
        document.getElementById('veilleContent').textContent = veille.content || "Aucune veille disponible.";
      } catch(e) {
        document.getElementById('loading').innerHTML = '❌ Erreur chargement: ' + e.message;
      }
    }
    loadDashboard();
  </script>
</body>
</html>
""".strip()


# ==================== FICHIER STATIQUE (PAGE DE TEST) ====================

@app.get("/test")
async def test_page(request: Request):
    """Page HTML simple pour tester le bot."""
    from security import verify_admin_token
    verify_admin_token(request, html=True)

    return """
<!DOCTYPE html>
<html>
<head>
  <title>BUTUS Bot — Test</title>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    * { box-sizing: border-box; }
    body { font-family: system-ui, sans-serif; max-width: 600px; margin: 0 auto; padding: 16px; background: #f5f5f5; }
    .card { background: white; border-radius: 12px; padding: 20px; margin: 12px 0; box-shadow: 0 1px 8px rgba(0,0,0,0.08); }
    h1 { font-size: 22px; color: #1a1a2e; }
    input { width: 100%; padding: 12px; border: 2px solid #ddd; border-radius: 8px; font-size: 16px; }
    button { background: #2ecc71; color: white; border: none; padding: 12px 24px; border-radius: 8px; font-size: 16px; font-weight: 600; cursor: pointer; width: 100%; margin-top: 8px; }
    .response { background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 12px; margin: 8px 0; white-space: pre-wrap; }
    .chat { display: flex; flex-direction: column; gap: 8px; max-height: 400px; overflow-y: auto; }
    .msg-user { background: #dbeafe; align-self: flex-end; padding: 8px 12px; border-radius: 12px 12px 4px 12px; }
    .msg-bot { background: white; align-self: flex-start; padding: 8px 12px; border-radius: 12px 12px 12px 4px; border: 1px solid #eee; white-space: pre-wrap; }
  </style>
</head>
<body>
  <div class="card">
    <h1>🧪 BUTUS Bot — Simulateur</h1>
    <p style="color: #666; font-size: 14px;">Testez le bot sans WhatsApp</p>
  </div>

  <div class="card">
    <div id="chat" class="chat" style="margin-bottom: 12px;">
      <div class="msg-bot">💬 Envoyez un message pour tester</div>
    </div>
    <input type="text" id="msgInput" placeholder="Votre message..." />
    <button onclick="send()">Envoyer</button>
  </div>

  <div class="card" style="font-size: 13px; color: #666;">
    <strong>Messages rapides :</strong><br>
    <a href="#" onclick="quick('Bonjour')">Bonjour</a> ·
    <a href="#" onclick="quick('1')">1 (Diagnostic)</a> ·
    <a href="#" onclick="quick('2')">2 (Fiches)</a> ·
    <a href="#" onclick="quick('5')">5 (Astuces)</a> ·
    <a href="#" onclick="quick('6')">6 (À propos)</a>
  </div>

  <script>
    async function send(msg) {
      const text = msg || document.getElementById('msgInput').value;
      if (!text) return;
      document.getElementById('msgInput').value = '';
      addMsg('user', text);
      try {
        const res = await fetch('/api/test/send', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({ from: 'test-user', text })
        });
        const data = await res.json();
        data.responses.forEach(r => addMsg('bot', r));
      } catch(e) {
        addMsg('bot', '❌ Erreur: ' + e.message);
      }
    }

    function addMsg(role, text) {
      const chat = document.getElementById('chat');
      const div = document.createElement('div');
      div.className = role === 'user' ? 'msg-user' : 'msg-bot';
      div.textContent = text;
      chat.appendChild(div);
      chat.scrollTop = chat.scrollHeight;
    }

    function quick(text) {
      document.getElementById('msgInput').value = text;
      send(text);
      return false;
    }

    document.getElementById('msgInput').addEventListener('keydown', e => {
      if (e.key === 'Enter') send();
    });
  </script>
</body>
</html>
""".strip()


# ==================== LANCEMENT ====================

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    reload_mode = not get_settings().is_production
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=reload_mode)
