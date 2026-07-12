"""Tests basiques : démarrage, health, statut."""


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "healthy"
    assert "environment" in data
    assert "whatsapp_configured" in data


def test_root(client):
    r = client.get("/")
    assert r.status_code == 200
    data = r.json()
    assert data["service"] == "BUTUS Repair WhatsApp Bot"
    assert data["version"] == "2.0.0"
    assert data["devices_in_knowledge_base"] == 9


def test_webhook_verify(client):
    r = client.get("/webhook/whatsapp", params={
        "hub.mode": "subscribe",
        "hub.verify_token": "test-verify",
        "hub.challenge": "12345",
    })
    assert r.status_code == 200


def test_webhook_verify_bad_token(client):
    r = client.get("/webhook/whatsapp", params={
        "hub.mode": "subscribe",
        "hub.verify_token": "wrong-token",
        "hub.challenge": "12345",
    })
    assert r.status_code == 403
