from enum import Enum
from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class ConversationState(str, Enum):
    HOME = "HOME"
    DIAGNOSE_DEVICE_TYPE = "DIAGNOSE_DEVICE_TYPE"
    DIAGNOSE_BRAND = "DIAGNOSE_BRAND"
    DIAGNOSE_MODEL = "DIAGNOSE_MODEL"
    DIAGNOSE_ISSUE = "DIAGNOSE_ISSUE"
    DIAGNOSE_CONFIRM = "DIAGNOSE_CONFIRM"
    DIAGNOSE_RESULT = "DIAGNOSE_RESULT"
    MY_TICKETS = "MY_TICKETS"
    CONTACT_REPAIRER = "CONTACT_REPAIRER"
    CONTACT_REPAIRER_NAME = "CONTACT_REPAIRER_NAME"
    CONTACT_REPAIRER_PHONE = "CONTACT_REPAIRER_PHONE"
    CONTACT_REPAIRER_REASON = "CONTACT_REPAIRER_REASON"
    ABOUT_BUTUS = "ABOUT_BUTUS"
    FICHES_TECHNIQUES = "FICHES_TECHNIQUES"
    FICHES_DEVICE_SELECT = "FICHES_DEVICE_SELECT"
    FICHES_ISSUE_SELECT = "FICHES_ISSUE_SELECT"
    TROUBLESHOOTING = "TROUBLESHOOTING"
    TROUBLESHOOTING_QUESTION = "TROUBLESHOOTING_QUESTION"
    TIPS = "TIPS"
    LOG_REPAIR = "LOG_REPAIR"
    LOG_REPAIR_TICKET = "LOG_REPAIR_TICKET"
    LOG_REPAIR_PARTS = "LOG_REPAIR_PARTS"
    LOG_REPAIR_COST = "LOG_REPAIR_COST"
    LOG_REPAIR_TIME = "LOG_REPAIR_TIME"
    LOG_REPAIR_STATUS = "LOG_REPAIR_STATUS"
    LOG_REPAIR_CONFIRM = "LOG_REPAIR_CONFIRM"
    SHOW_IMPACT = "SHOW_IMPACT"
    BROWSE_PARTS = "BROWSE_PARTS"
    BROWSE_PARTS_DEVICE = "BROWSE_PARTS_DEVICE"
    PART_DETAIL = "PART_DETAIL"
    PART_RESERVE = "PART_RESERVE"
    PART_RESERVE_CONFIRM = "PART_RESERVE_CONFIRM"

    BROWSE_RECONDITIONED = "BROWSE_RECONDITIONED"
    RECONDITIONED_CATEGORY = "RECONDITIONED_CATEGORY"
    RECONDITIONED_DETAIL = "RECONDITIONED_DETAIL"
    RECONDITIONED_CONTACT = "RECONDITIONED_CONTACT"
    CONSENT_PENDING = "CONSENT_PENDING"

    VEILLE_MENU = "VEILLE_MENU"
    VEILLE_TOPIC = "VEILLE_TOPIC"
    VEILLE_RESULTS = "VEILLE_RESULTS"
    VEILLE_PERSO = "VEILLE_PERSO"


class DeviceCategory(BaseModel):
    id: str
    label: str
    emoji: str
    examples: list[str]


DEVICE_CATEGORIES: list[DeviceCategory] = [
    DeviceCategory(id="ventilateur", label="Ventilateur", emoji="🌀", examples=["plafonnier", "sur pied", "brasseur d'air"]),
    DeviceCategory(id="climatiseur", label="Climatiseur", emoji="❄️", examples=["split", "mobile", "mural"]),
    DeviceCategory(id="refrigerateur", label="Réfrigérateur / Congélateur", emoji="🧊", examples=["réfrigérateur", "congélateur", "combi"]),
    DeviceCategory(id="machine_laver", label="Machine à laver", emoji="👕", examples=["top", "frontale", "sèche-linge"]),
    DeviceCategory(id="television", label="Téléviseur / Écran", emoji="📺", examples=["LED", "LCD", "smart TV"]),
    DeviceCategory(id="smartphone", label="Smartphone / Tablette", emoji="📱", examples=["smartphone", "tablette", "iPhone"]),
    DeviceCategory(id="ordinateur", label="Ordinateur / Laptop", emoji="💻", examples=["PC", "MacBook", "imprimante"]),
    DeviceCategory(id="audio", label="Sonorisation / Audio", emoji="🔊", examples=["enceinte", "chaîne hi-fi", "micro"]),
    DeviceCategory(id="electromenager", label="Petit électroménager", emoji="🔌", examples=["mixeur", "fer à repasser", "grille-pain"]),
    DeviceCategory(id="autre", label="Autre appareil", emoji="🔧", examples=["groupe électrogène", "panneau solaire", "autre"]),
]


class ConversationData(BaseModel):
    phone_number: str
    state: ConversationState = ConversationState.HOME
    device_type: Optional[str] = None
    device_brand: Optional[str] = None
    device_model: Optional[str] = None
    issue_description: Optional[str] = None
    ticket_id: Optional[str] = None
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    language: str = "fr"
    veille_topic: Optional[str] = None
    veille_custom_question: Optional[str] = None


class DiagnosisRequest(BaseModel):
    device_type: str
    device_brand: str
    device_model: str
    issue_description: str
    language: str = "fr"


class DiagnosisResponse(BaseModel):
    possible_causes: list[str]
    steps_to_try: list[str]
    parts_needed: Optional[list[str]] = None
    urgency: str  # "faible", "moyenne", "urgente"
    can_self_repair: bool
    recommendation: str


class Ticket(BaseModel):
    ticket_id: str
    phone_number: str
    customer_name: Optional[str] = None
    device_type: str
    device_brand: str
    device_model: str
    issue_description: str
    diagnosis_summary: Optional[str] = None
    status: str = "ouvert"  # ouvert, en_cours, resolu, ferme
    assigned_to: Optional[str] = None
    created_at: str = ""
    updated_at: str = ""


class ReparationSession(BaseModel):
    session_id: str
    ticket_id: str
    phone_number: str
    device_type: str
    device_brand: str = ""
    device_model: str = ""
    parts_changed: list[str] = []
    parts_cost_fcfa: float = 0.0
    labor_cost_fcfa: float = 0.0
    total_cost_fcfa: float = 0.0
    time_spent_minutes: int = 0
    test_results: str = ""
    status: str = "en_cours"  # en_cours, reussi, echec
    notes: str = ""
    technician_name: str = ""
    created_at: str = ""
    updated_at: str = ""


class WhatsAppMessage(BaseModel):
    from_number: str
    text: str
    message_id: str
    timestamp: str
