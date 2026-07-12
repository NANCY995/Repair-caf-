"""
BUTUS WhatsApp Bot — Script de configuration interactif.

Usage : python setup.py
"""

import os
import json
import secrets
import shutil
from pathlib import Path


BASE_DIR = Path(__file__).parent
ENV_FILE = BASE_DIR / ".env"
ENV_EXAMPLE = BASE_DIR / ".env.example"
CREDS_DIR = BASE_DIR / "credentials"


def check_dependencies():
    print("🔍 Vérification des dépendances...")
    try:
        import fastapi
        print(f"  ✅ FastAPI {fastapi.__version__}")
    except ImportError:
        print("  ❌ FastAPI non installé. Lancez : pip install -r requirements.txt")
        return False

    try:
        import openai
        print(f"  ✅ OpenAI {openai.__version__}")
    except ImportError:
        print("  ⚠️  OpenAI non installé. Le diagnostic IA ne fonctionnera pas.")
        print("     Lancez : pip install -r requirements.txt")

    return True


def configure_env():
    if ENV_FILE.exists():
        overwrite = input("⚠️  Le fichier .env existe déjà. Le réécrire ? (o/N) : ").lower()
        if overwrite != "o":
            print("  → Fichier .env conservé.")
            return

    print("\n📝 Configuration de l'environnement :\n")

    default_token = secrets.token_hex(32)
    config = {
        "WHATSAPP_TOKEN": input("WHATSAPP_TOKEN (token d'accès Meta) : ").strip(),
        "WHATSAPP_PHONE_NUMBER_ID": input("WHATSAPP_PHONE_NUMBER_ID : ").strip(),
        "WHATSAPP_VERIFY_TOKEN": input("WHATSAPP_VERIFY_TOKEN (votre choix, laissez vide pour auto) : ").strip() or default_token,
        "WHATSAPP_APP_SECRET": input("WHATSAPP_APP_SECRET (App Secret Meta, laissez vide pour auto) : ").strip() or secrets.token_hex(32),
        "WHATSAPP_API_VERSION": "v22.0",
        "GOOGLE_SHEETS_CREDENTIALS_PATH": str(CREDS_DIR / "google-sheets-creds.json"),
        "GOOGLE_SHEETS_SPREADSHEET_ID": input("GOOGLE_SHEETS_SPREADSHEET_ID (ID du Google Sheet) : ").strip(),
        "OPENAI_API_KEY": input("OPENAI_API_KEY (clé API OpenAI) : ").strip(),
        "OPENAI_MODEL": "gpt-4o-mini",
        "APP_ENV": "development",
        "APP_SECRET_KEY": secrets.token_hex(32),
        "ADMIN_API_TOKEN": secrets.token_hex(32),
        "BUTUS_NOTIFICATION_PHONE": input("BUTUS_NOTIFICATION_PHONE (numéro réparateur pour alertes, ex: +22890000000) : ").strip(),
    }

    with open(ENV_FILE, "w", encoding="utf-8") as f:
        for key, value in config.items():
            f.write(f'{key}="{value}"\n')

    print("  ✅ Fichier .env créé avec succès !")


def setup_credentials():
    print("\n📁 Configuration des credentials Google Sheets :")

    CREDS_DIR.mkdir(exist_ok=True)
    creds_file = CREDS_DIR / "google-sheets-creds.json"

    if creds_file.exists():
        overwrite = input("  ⚠️  Credentials existants. Remplacer ? (o/N) : ").lower()
        if overwrite != "o":
            print("  → Credentials conservés.")
            return

    print("""
  Pour obtenir vos credentials Google Sheets :
  1. Allez sur https://console.cloud.google.com/
  2. Créez un projet (ou sélectionnez-en un)
  3. Activez l'API Google Sheets
  4. Allez dans "Identifiants" → Créer un compte de service
  5. Téléchargez le fichier JSON
  6. Copiez le contenu ci-dessous
  """)

    print("  Collez le contenu du fichier JSON des credentials,")
    print("  puis tapez 'FIN' sur une ligne vide pour terminer :\n")

    lines = []
    while True:
        line = input()
        if line.strip().upper() == "FIN":
            break
        lines.append(line)

    if lines:
        try:
            json_content = json.loads("\n".join(lines))
            with open(creds_file, "w", encoding="utf-8") as f:
                json.dump(json_content, f, indent=2)
            print(f"  ✅ Credentials sauvegardés dans {creds_file}")
        except json.JSONDecodeError:
            print("  ❌ JSON invalide. Veuillez réessayer.")
    else:
        print("  ⏭️  Aucun credential fourni. Configurable plus tard.")


def final_guide():
    print("""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎉  BUTUS WhatsApp Bot — Prêt !

📋 Prochaines étapes :
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1️⃣  Lancement en développement :
    cd backend/whatsapp_bot
    python app.py
    
    Le serveur démarre sur http://localhost:8000

2️⃣  Tester le bot sans WhatsApp :
    curl -X POST http://localhost:8000/api/test/send \\
      -H "Content-Type: application/json" \\
      -d '{"from": "+22890000000", "text": "Bonjour"}'

3️⃣  Configurer le webhook WhatsApp :
    - URL : https://votre-domaine.com/webhook/whatsapp
    - Token : celui défini dans WHATSAPP_VERIFY_TOKEN

4️⃣  Exposer en ligne (pour le webhook) :
    Option A : ngrok http 8000 (test)
    Option B : Déployer sur Railway/Render (prod)

5️⃣  Déploiement production :
    git push
    → Railway déploie automatiquement (voir render.yaml)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔗  Liens utiles :
    • WhatsApp Cloud API Setup : https://developers.facebook.com/docs/whatsapp/cloud-api
    • Google Sheets API : https://console.cloud.google.com/
    • OpenAI API : https://platform.openai.com/api-keys
    • Railway : https://railway.app/
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")


if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("  🔧 BUTUS WhatsApp Bot — Configuration")
    print("=" * 50 + "\n")

    if not check_dependencies():
        exit(1)

    configure_env()
    setup_credentials()
    final_guide()
