from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # WhatsApp Cloud API
    whatsapp_token: str = ""
    whatsapp_phone_number_id: str = ""
    whatsapp_verify_token: str = "butus_verify_2026"
    whatsapp_app_secret: str = ""
    whatsapp_api_version: str = "v22.0"

    # Google Sheets
    google_sheets_credentials_path: str = "credentials/google-sheets-creds.json"
    google_sheets_spreadsheet_id: str = ""

    # OpenAI / LLM
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    # Google Gemini (fallback/open source alternatif)
    ai_provider: str = "openai"  # "openai" | "gemini"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"

    # Notification réparateur (WhatsApp)
    butus_notification_phone: str = ""

    # Sécurité / CORS
    cors_origins: str = "*"

    # App
    app_env: str = "development"
    app_secret_key: str = "changez_moi_en_production"
    admin_api_token: str = ""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def whatsapp_api_base(self) -> str:
        return (
            f"https://graph.facebook.com/{self.whatsapp_api_version}"
            f"/{self.whatsapp_phone_number_id}/messages"
        )


@lru_cache()
def get_settings() -> Settings:
    return Settings()
