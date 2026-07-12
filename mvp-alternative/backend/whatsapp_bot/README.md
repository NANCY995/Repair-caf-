# 🤖 BUTUS Repair — WhatsApp Bot MVP

Assistant diagnostic WhatsApp + catalogue pièces + reconditionnés pour le Repair Café BUTUS (Lomé, Togo).

**3 piliers :** Diagnostic IA (P1) · Pièces détachées (P2) · Appareils reconditionnés (P3)

---

## Architecture

```
Utilisateur WhatsApp → WhatsApp Cloud API → Webhook → FastAPI → Google Sheets
                                   ↕                    ↕
                                                   OpenAI (diagnostic IA)
                                              + Base de connaissance locale
```

**Stack :** Python 3.13 · FastAPI · WhatsApp Cloud API · Google Sheets API · OpenAI API

---

## Prérequis

- Python 3.10+
- Compte développeur Meta (WhatsApp Cloud API) — [gratuit](https://developers.facebook.com/docs/whatsapp/cloud-api)
- Clé API OpenAI (optionnel, sans → fallback KB locale)
- Compte Google Cloud avec API Sheets activée (optionnel, fallback mémoire)

---

## Installation rapide

```bash
# 1. Dépendances
pip install -r requirements.txt

# 2. Configuration interactive
python setup.py

# 3. Démarrer
uvicorn app:app --host 0.0.0.0 --port 8000
```

Le setup génère automatiquement les tokens `WHATSAPP_APP_SECRET`, `ADMIN_API_TOKEN` et `APP_SECRET_KEY`.

---

## Endpoints

### Webhook WhatsApp

| Méthode | URL | Description |
|---------|-----|-------------|
| GET | `/webhook/whatsapp?hub.mode=subscribe&hub.verify_token=...&hub.challenge=...` | Vérification Meta |
| POST | `/webhook/whatsapp` | Messages entrants (signé `X-Hub-Signature-256`) |

### API publique (catalogue)

| Méthode | URL | Description |
|---------|-----|-------------|
| GET | `/api/fiches` | Liste des fiches techniques |
| GET | `/api/fiches/{device}` | Détail d'une fiche |
| GET | `/api/fiches/{device}/search?q=` | Recherche dans une fiche |
| GET | `/api/parts` | Catalogue pièces détachées |
| GET | `/api/parts/search?q=` | Recherche pièces |
| GET | `/api/parts/{id}` | Détail d'une pièce |
| GET | `/api/reconditioned` | Catalogue reconditionnés |
| GET | `/api/reconditioned/search?q=` | Recherche reconditionnés |
| GET | `/api/reconditioned/{id}` | Détail appareil |
| GET | `/health` | Santé du service |

### API admin (token requis — voir sécurisation)

| Méthode | URL | Description |
|---------|-----|-------------|
| POST | `/api/test/send` | Simuler un message WhatsApp |
| POST | `/api/sessions` | Créer une session réparation |
| GET | `/api/sessions` | Lister les sessions |
| GET | `/api/dashboard` | Données du tableau de bord |
| GET | `/dashboard` | Page HTML du tableau de bord |
| GET | `/api/conversations/active` | Conversations actives |
| POST | `/api/conversations/reset` | Réinitialiser une conversation |

---

## Menu utilisateur

```
1  → Diagnostiquer un appareil
2  → Fiches techniques
3  → Pièces détachées 🔩
4  → Appareils reconditionnés 📱
5  → Mes tickets
6  → Contacter un réparateur
7  → Astuces & infos
8  → Impact CO₂
9  → Enregistrer une réparation (technicien)
10 → À propos
```

Recherche directe : tapez un mot-clé (ex: « batterie », « iPhone ») depuis l'accueil.

---

## Sécurité

| Mesure | Statut |
|--------|--------|
| Signature webhook `X-Hub-Signature-256` | ✅ Obligatoire en prod |
| Token admin sur endpoints sensibles | ✅ (X-Admin-Token / Bearer / Basic Auth) |
| Page `/dashboard` protégée par Basic Auth | ✅ (boîte de dialogue navigateur) |
| Rate limiting webhook (30 requêtes/min/IP) | ✅ |
| Rate limiting `/api/test/send` (15/min, bypass admin) | ✅ |
| CORS configurable via `CORS_ORIGINS` | ✅ |
| Headers sécurité (X-Content-Type-Options, HSTS) | ✅ |
| Logs sans PII (numéros masqués) | ✅ |

> **En production** : les variables `WHATSAPP_APP_SECRET`, `ADMIN_API_TOKEN`,
> `WHATSAPP_VERIFY_TOKEN` et `APP_SECRET_KEY` doivent être des valeurs
> aléatoires (générées par `setup.py` ou `secrets.token_hex(32)`).

---

## Variables d'environnement (`.env`)

```
WHATSAPP_TOKEN         → Token d'accès Meta
WHATSAPP_PHONE_NUMBER_ID  → ID du numéro WhatsApp
WHATSAPP_VERIFY_TOKEN  → Token de vérification webhook
WHATSAPP_APP_SECRET    → App Secret Meta (signature webhook)
ADMIN_API_TOKEN        → Token d'accès aux endpoints admin
BUTUS_NOTIFICATION_PHONE → Numéro réparateur pour alertes réservations
GOOGLE_SHEETS_SPREADSHEET_ID → ID du Google Sheet
OPENAI_API_KEY         → Clé API OpenAI
APP_ENV                → "development" | "production"
CORS_ORIGINS           → Origines CORS (défaut: *)
```

---

## Structure du code

```
backend/whatsapp_bot/
├── app.py                    # Serveur FastAPI
├── config.py                 # Configuration (.env)
├── models.py                 # États de conversation + modèles
├── conversation.py           # Machine à états (5 000+ lignes)
├── security.py               # Signature webhook, auth admin, rate limit
├── whatsapp.py               # Envoi messages WhatsApp
├── diagnostic.py             # Moteur diagnostic IA (KB + LLM + fallback)
├── sheets.py                 # Google Sheets (tickets, sessions, réservations)
├── impact_calculator.py      # Calcul CO₂ et stats
├── knowledge_base.py         # Base de connaissance (36 pannes, 9 devices)
├── parts_catalog.py          # Catalogue pièces (30 pièces, 9 catégories)
├── reconditioned_catalog.py  # Catalogue reconditionnés (12 appareils)
├── setup.py                  # Configuration interactive
├── security.py               # Sécurité (signature, auth, rate limit)
├── tests/                    # Suite pytest (36 tests)
└── .github/workflows/test.yml  # CI GitHub Actions
```

---

## Coûts estimés (MVP)

| Service | Coût |
|---------|------|
| WhatsApp Cloud API | Gratuit (1 000 conversations/mois) |
| OpenAI GPT-4o-mini | ~1-5 $/mois |
| Google Sheets API | Gratuit |
| Hébergement (Railway Free / Render Free) | Gratuit |
| **Total** | **~1-5 $/mois** |

---

## Licence

MIT — BUTUS Repair 🇹🇬
