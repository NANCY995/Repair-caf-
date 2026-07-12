import os
import json
from datetime import datetime
from typing import Optional

from config import get_settings

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# --- En-têtes des colonnes ---
TICKETS_HEADERS = [
    "ID Ticket", "Date", "Téléphone", "Nom client",
    "Type appareil", "Marque", "Modèle",
    "Description panne", "Diagnostic IA", "Statut",
    "Assigné à", "Notes"
]

CONTACTS_HEADERS = [
    "Date", "Téléphone", "Nom", "Raison contact", "Statut"
]

REPAIR_SESSIONS_HEADERS = [
    "Session ID", "Ticket ID", "Date", "Téléphone",
    "Type appareil", "Marque", "Modèle",
    "Pièces changées", "Coût pièces FCFA", "Main d'oeuvre FCFA",
    "Coût total FCFA", "Temps (min)", "Tests effectués",
    "Statut", "Technicien", "Notes"
]

RESERVATIONS_HEADERS = [
    "Date", "Téléphone", "Nom", "ID Pièce", "Nom Pièce",
    "Prix FCFA", "Lieu retrait", "Contact saisi", "Statut"
]


def _get_sheets_service():
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
    except ImportError:
        return None

    settings = get_settings()
    creds_path = settings.google_sheets_credentials_path

    if not os.path.exists(creds_path):
        return None

    creds = service_account.Credentials.from_service_account_file(
        creds_path, scopes=SCOPES
    )
    return build("sheets", "v4", credentials=creds)


def _ensure_sheet_exists(service, spreadsheet_id: str, sheet_name: str, headers: list[str]):
    try:
        sheet_metadata = service.spreadsheets().get(
            spreadsheetId=spreadsheet_id
        ).execute()
        existing = [s["properties"]["title"] for s in sheet_metadata.get("sheets", [])]

        if sheet_name not in existing:
            body = {
                "requests": [{
                    "addSheet": {
                        "properties": {"title": sheet_name}
                    }
                }]
            }
            service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id, body=body
            ).execute()
            # Écrire l'en-tête
            service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=f"{sheet_name}!A1:{chr(64 + len(headers))}1",
                valueInputOption="RAW",
                body={"values": [headers]}
            ).execute()
    except HttpError:
        pass


def add_ticket(ticket_data: dict) -> Optional[str]:
    service = _get_sheets_service()
    if not service:
        return None

    settings = get_settings()
    spreadsheet_id = settings.google_sheets_spreadsheet_id
    if not spreadsheet_id:
        return None

    sheet_name = "Tickets"
    _ensure_sheet_exists(service, spreadsheet_id, sheet_name, TICKETS_HEADERS)

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ticket_id = ticket_data.get("ticket_id", f"BUTUS-{datetime.now().strftime('%Y%m%d%H%M%S')}")

    row = [
        ticket_id,
        now,
        ticket_data.get("phone_number", ""),
        ticket_data.get("customer_name", ""),
        ticket_data.get("device_type", ""),
        ticket_data.get("device_brand", ""),
        ticket_data.get("device_model", ""),
        ticket_data.get("issue_description", ""),
        ticket_data.get("diagnosis_summary", ""),
        ticket_data.get("status", "ouvert"),
        ticket_data.get("assigned_to", ""),
        ticket_data.get("notes", ""),
    ]

    try:
        result = service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=f"{sheet_name}!A:L",
            valueInputOption="RAW",
            insertDataOption="INSERT_ROWS",
            body={"values": [row]}
        ).execute()
        return ticket_id
    except HttpError as e:
        print(f"Erreur Google Sheets: {e}")
        return None


def add_contact_request(contact_data: dict) -> bool:
    service = _get_sheets_service()
    if not service:
        return False

    settings = get_settings()
    spreadsheet_id = settings.google_sheets_spreadsheet_id
    if not spreadsheet_id:
        return False

    sheet_name = "Contacts"
    _ensure_sheet_exists(service, spreadsheet_id, sheet_name, CONTACTS_HEADERS)

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row = [
        now,
        contact_data.get("phone_number", ""),
        contact_data.get("name", ""),
        contact_data.get("reason", ""),
        "nouveau",
    ]

    try:
        service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=f"{sheet_name}!A:E",
            valueInputOption="RAW",
            insertDataOption="INSERT_ROWS",
            body={"values": [row]}
        ).execute()
        return True
    except HttpError:
        return False


def add_repair_session(session_data: dict) -> Optional[str]:
    """Enregistre une session de réparation dans Google Sheets."""
    service = _get_sheets_service()
    if not service:
        return None

    settings = get_settings()
    spreadsheet_id = settings.google_sheets_spreadsheet_id
    if not spreadsheet_id:
        return None

    sheet_name = "SessionsReparation"
    _ensure_sheet_exists(service, spreadsheet_id, sheet_name, REPAIR_SESSIONS_HEADERS)

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    session_id = session_data.get("session_id", f"SR-{datetime.now().strftime('%Y%m%d%H%M%S')}")

    parts_str = ", ".join(session_data.get("parts_changed", [])) if session_data.get("parts_changed") else ""

    row = [
        session_id,
        session_data.get("ticket_id", ""),
        now,
        session_data.get("phone_number", ""),
        session_data.get("device_type", ""),
        session_data.get("device_brand", ""),
        session_data.get("device_model", ""),
        parts_str,
        session_data.get("parts_cost_fcfa", 0),
        session_data.get("labor_cost_fcfa", 0),
        session_data.get("total_cost_fcfa", 0),
        session_data.get("time_spent_minutes", 0),
        session_data.get("test_results", ""),
        session_data.get("status", "en_cours"),
        session_data.get("technician_name", ""),
        session_data.get("notes", ""),
    ]

    try:
        service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=f"{sheet_name}!A:P",
            valueInputOption="RAW",
            insertDataOption="INSERT_ROWS",
            body={"values": [row]}
        ).execute()
        return session_id
    except HttpError as e:
        print(f"Erreur Google Sheets session: {e}")
        return None


def add_part_reservation(data: dict) -> Optional[str]:
    """Enregistre une réservation de pièce détachée dans Google Sheets."""
    service = _get_sheets_service()
    if not service:
        return None

    settings = get_settings()
    spreadsheet_id = settings.google_sheets_spreadsheet_id
    if not spreadsheet_id:
        return None

    sheet_name = "Reservations"
    _ensure_sheet_exists(service, spreadsheet_id, sheet_name, RESERVATIONS_HEADERS)

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row = [
        now,
        data.get("phone_number", ""),
        data.get("customer_name", ""),
        data.get("part_id", ""),
        data.get("part_name", ""),
        data.get("price_fcfa", 0),
        data.get("location", ""),
        data.get("contact_raw", ""),
        "nouvelle",
    ]

    try:
        service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=f"{sheet_name}!A:I",
            valueInputOption="RAW",
            insertDataOption="INSERT_ROWS",
            body={"values": [row]}
        ).execute()
        return "ok"
    except HttpError as e:
        print(f"Erreur Google Sheets réservation: {e}")
        return None


def get_all_tickets() -> list[dict]:
    """Récupère tous les tickets (pour le dashboard)."""
    service = _get_sheets_service()
    if not service:
        return []

    settings = get_settings()
    spreadsheet_id = settings.google_sheets_spreadsheet_id
    if not spreadsheet_id:
        return []

    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range="Tickets!A:L"
        ).execute()
        values = result.get("values", [])
        if not values or len(values) < 2:
            return []
        headers = values[0]
        tickets = []
        for row in values[1:]:
            ticket = dict(zip(headers, row + [""] * (len(headers) - len(row))))
            tickets.append(ticket)
        return tickets
    except HttpError:
        return []


def get_all_sessions() -> list[dict]:
    """Récupère toutes les sessions de réparation (pour le dashboard)."""
    service = _get_sheets_service()
    if not service:
        return []

    settings = get_settings()
    spreadsheet_id = settings.google_sheets_spreadsheet_id
    if not spreadsheet_id:
        return []

    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range="SessionsReparation!A:P"
        ).execute()
        values = result.get("values", [])
        if not values or len(values) < 2:
            return []
        headers = values[0]
        sessions = []
        for row in values[1:]:
            session = dict(zip(headers, row + [""] * (len(headers) - len(row))))
            sessions.append(session)
        return sessions
    except HttpError:
        return []


def get_tickets_by_phone(phone_number: str) -> list[dict]:
    service = _get_sheets_service()
    if not service:
        return []

    settings = get_settings()
    spreadsheet_id = settings.google_sheets_spreadsheet_id
    if not spreadsheet_id:
        return []

    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range="Tickets!A:L"
        ).execute()

        values = result.get("values", [])
        if not values or len(values) < 2:
            return []

        headers = values[0]
        tickets = []
        for row in values[1:]:
            if len(row) > 2 and row[2] == phone_number:
                ticket = dict(zip(headers, row + [""] * (len(headers) - len(row))))
                tickets.append(ticket)
        return tickets
    except HttpError:
        return []
