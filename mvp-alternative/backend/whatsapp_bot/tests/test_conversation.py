"""Tests des flux de conversation : P1, P2, P3.
Chaque test utilise un numéro unique (son propre nom) pour la conversation."""

import pytest


def send_text(client, text, phone):
    """Helper : envoie un message sur une conversation."""
    resp = client.post("/api/test/send", json={"from": phone, "text": text},
                      headers={"X-Admin-Token": "test-admin-token"})
    return resp.json()


@pytest.fixture
def phone(request):
    """Un numéro unique par test."""
    name = request.node.name.replace("_", "-")
    return f"+228{name[:20]}"


class TestHomeMenu:
    def test_home_buffer(self, client, phone):
        # Consentement obligatoire avant toute interaction
        consent_resp = send_text(client, "Bonjour", phone)
        assert "protection des données" in consent_resp["responses"][0].lower()
        # Accepter le consentement
        send_text(client, "OUI", phone)
        # Maintenant le menu normal
        data = send_text(client, "Bonjour", phone)
        assert "BUTUS Repair" in data["responses"][0]
        assert data["responses_count"] == 1

    def test_mode_options(self, client, phone):
        # Consentement d'abord
        send_text(client, "Bonjour", phone)
        send_text(client, "OUI", phone)
        send_text(client, "Bonjour", "+228opt42")
        send_text(client, "OUI", "+228opt42")
        send_text(client, "Bonjour", "+228opt52")
        send_text(client, "OUI", "+228opt52")
        # "3" doit montrer le catalogue complet (shortcut direct)
        data = send_text(client, "3", phone)
        assert "Catalogue complet" in data["responses"][0]

        # "4" doit montrer le menu reconditionné
        data = send_text(client, "4", "+228opt42")

        # "5" → mes tickets
        data = send_text(client, "5", "+228opt52")
        responses = " ".join(data["responses"]).lower()
        assert "ticket" in responses or "réparation" in responses


class TestP2Parts:
    def test_parts_browse_and_reserve(self, client, phone):
        # Consentement d'abord
        send_text(client, "Bonjour", phone)
        send_text(client, "OUI", phone)
        # Menu pièces
        send_text(client, "3", phone)

        # Option 1 → choisir appareil
        data = send_text(client, "1", phone)
        assert "Choisir un appareil" in data["responses"][0]

        # Option 1 → Ventilateur
        data = send_text(client, "1", phone)
        assert "Ventilateur" in data["responses"][0]

        # ID de pièce → détail
        data = send_text(client, "P-VENT-001", phone)
        full = " ".join(data["responses"])
        assert "Condensateur" in full or "P-VENT-001" in full

        # commander
        data = send_text(client, "commander", phone)
        assert "Réserver" in data["responses"][0]

        # coordonnées → confirmation
        data = send_text(client, "Nancy test 90000000", phone)
        assert "Demande envoyée" in data["responses"][0]

    def test_part_search_from_home(self, client, phone):
        send_text(client, "Bonjour", phone)
        send_text(client, "OUI", phone)
        data = send_text(client, "batterie", phone)
        assert any("batterie" in r.lower() for r in data["responses"])


class TestConsent:
    def test_consent_required_before_menu(self, client):
        phone = "+228testconsent1"
        data = send_text(client, "Bonjour", phone)
        assert "protection des données" in data["responses"][0].lower()

    def test_consent_rejection(self, client):
        phone = "+228testconsent2"
        send_text(client, "Bonjour", phone)
        data = send_text(client, "Non", phone)
        assert "sans votre consentement" in data["responses"][0].lower() or "STOP" in data["responses"][0]

    def test_consent_acceptance_shows_menu(self, client):
        phone = "+228testconsent3"
        send_text(client, "Bonjour", phone)
        data = send_text(client, "OUI", phone)
        assert "BUTUS Repair" in data["responses"][0]


class TestP3Reconditioned:
    def test_reconditioned_browse(self, client, phone):
        send_text(client, "Bonjour", phone)
        send_text(client, "OUI", phone)
        send_text(client, "4", phone)
        data = send_text(client, "1", phone)
        assert "catégorie" in data["responses"][0].lower()

        data = send_text(client, "1", phone)
        assert "Smartphone" in data["responses"][0]

        data = send_text(client, "RC-SMARTPHONE-001", phone)
        assert "iPhone" in data["responses"][0]

        data = send_text(client, "contacter", phone)
        assert "Intéressé" in data["responses"][0]

        data = send_text(client, "Nancy test 90000000", phone)
        assert "Demande envoyée" in data["responses"][0]
