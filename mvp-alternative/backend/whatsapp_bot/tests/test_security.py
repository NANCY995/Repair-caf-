"""Tests de sécurité : webhook signature, admin auth."""

import json
import hashlib
import hmac


def test_webhook_post_valid_signature(client):
    body = json.dumps({"entry": [{}]}).encode()
    sig = "sha256=" + hmac.new(b"test-app-secret", body, hashlib.sha256).hexdigest()
    r = client.post("/webhook/whatsapp", content=body, headers={"X-Hub-Signature-256": sig})
    assert r.status_code == 200


def test_webhook_post_bad_signature(client):
    body = json.dumps({"entry": [{}]}).encode()
    r = client.post("/webhook/whatsapp", content=body, headers={"X-Hub-Signature-256": "sha256=bad"})
    assert r.status_code == 403


def test_webhook_post_missing_signature(client):
    body = json.dumps({"entry": [{}]}).encode()
    r = client.post("/webhook/whatsapp", content=body)
    assert r.status_code == 403


def test_admin_endpoints_require_token(client):
    for url in ["/api/stats", "/api/sessions", "/api/conversations/active",
                 "/api/dashboard"]:
        r = client.get(url)
        assert r.status_code == 403, f"{url} should be 403 without token"


def test_admin_endpoints_with_token(client, admin_headers):
    for url in ["/api/stats", "/api/sessions", "/api/conversations/active",
                 "/api/dashboard"]:
        r = client.get(url, headers=admin_headers)
        assert r.status_code == 200, f"{url} should be 200 with token"


def test_dashboard_html_requires_auth(client):
    r = client.get("/dashboard")
    assert r.status_code == 401
    assert r.headers.get("www-authenticate", "").startswith("Basic realm=")


def test_dashboard_html_with_basic_auth(client):
    import base64
    basic = "Basic " + base64.b64encode(b"admin:test-admin-token").decode()
    r = client.get("/dashboard", headers={"Authorization": basic})
    assert r.status_code == 200


def test_admin_endpoints_with_bearer(client):
    r = client.get("/api/stats", headers={"Authorization": "Bearer test-admin-token"})
    assert r.status_code == 200


def test_admin_endpoints_with_query_token(client):
    r = client.get("/api/dashboard?token=test-admin-token")
    assert r.status_code == 200
