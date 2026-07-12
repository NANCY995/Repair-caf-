"""Tests des endpoints API : fiches, pièces, sessions, catalogue reconditionné."""


class TestFiches:
    def test_list_fiches(self, client):
        r = client.get("/api/fiches")
        assert r.status_code == 200
        data = r.json()
        assert data["count"] == 9
        assert any(d["name"] == "Ventilateur" for d in data["devices"])

    def test_fiche_device(self, client):
        r = client.get("/api/fiches/ventilateur")
        assert r.status_code == 200
        data = r.json()
        assert data["name"] == "Ventilateur"
        assert len(data["issues"]) > 0

    def test_fiche_not_found(self, client):
        r = client.get("/api/fiches/inconnu")
        assert r.status_code == 404

    def test_fiche_search(self, client):
        r = client.get("/api/fiches/ventilateur/search?q=bruit")
        assert r.status_code == 200
        data = r.json()
        assert data["results_count"] > 0


class TestParts:
    def test_list_all_parts(self, client):
        r = client.get("/api/parts")
        assert r.status_code == 200
        data = r.json()
        assert data["count"] >= 25

    def test_parts_by_device(self, client):
        r = client.get("/api/parts?device=ventilateur")
        assert r.status_code == 200
        data = r.json()
        assert data["count"] >= 4
        assert data["device_filter"] == "ventilateur"

    def test_parts_search(self, client):
        r = client.get("/api/parts/search?q=batterie")
        assert r.status_code == 200
        assert r.json()["count"] >= 2

    def test_part_detail(self, client):
        r = client.get("/api/parts/P-VENT-001")
        assert r.status_code == 200
        assert r.json()["name"] == "Condensateur de démarrage 2µF"

    def test_part_not_found(self, client):
        r = client.get("/api/parts/INVALID")
        assert r.status_code == 404


class TestReconditioned:
    def test_list_all(self, client):
        r = client.get("/api/reconditioned")
        assert r.status_code == 200
        data = r.json()
        assert data["count"] == 12

    def test_by_category(self, client):
        r = client.get("/api/reconditioned?category=smartphone")
        assert r.status_code == 200
        assert r.json()["count"] == 5

    def test_search(self, client):
        r = client.get("/api/reconditioned/search?q=iphone")
        assert r.status_code == 200
        assert r.json()["count"] == 2

    def test_detail(self, client):
        r = client.get("/api/reconditioned/RC-SMARTPHONE-001")
        assert r.status_code == 200
        assert r.json()["name"] == "iPhone XR 64 Go"


class TestSessions:
    def test_create_session(self, client, admin_headers):
        r = client.post("/api/sessions", json={
            "ticket_id": "TEST-001",
            "device_type": "ventilateur",
            "status": "reussi",
            "parts_changed": ["condensateur"],
        }, headers=admin_headers)
        assert r.status_code == 200
        data = r.json()
        assert "session_id" in data
        assert "impact" in data

    def test_list_sessions(self, client, admin_headers):
        r = client.get("/api/sessions", headers=admin_headers)
        assert r.status_code == 200
        assert "sessions" in r.json()

    def test_sessions_require_auth(self, client):
        r = client.post("/api/sessions", json={"ticket_id": "X"})
        assert r.status_code == 403


class TestDashboard:
    def test_dashboard_data(self, client, admin_headers):
        r = client.get("/api/dashboard", headers=admin_headers)
        assert r.status_code == 200

    def test_dashboard_requires_auth(self, client):
        r = client.get("/api/dashboard")
        assert r.status_code == 403
