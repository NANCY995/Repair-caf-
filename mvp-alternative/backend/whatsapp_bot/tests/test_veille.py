import pytest
from unittest.mock import patch, MagicMock
from veille import search_web, do_veille

class TestVeilleUnit:
    @patch("veille.DDGS")
    def test_search_web_success(self, mock_ddgs):
        # Configuration du mock pour DDGS
        mock_instance = MagicMock()
        mock_instance.text.return_value = [
            {"title": "Actu 1", "body": "Snippet 1", "href": "http://link1"},
            {"title": "Actu 2", "body": "Snippet 2", "href": "http://link2"},
        ]
        mock_ddgs.return_value.__enter__.return_value = mock_instance

        results = search_web("test query")
        assert "Actu 1" in results
        assert "Snippet 2" in results
        assert "http://link1" in results

    @patch("veille.DDGS")
    def test_search_web_empty(self, mock_ddgs):
        mock_instance = MagicMock()
        mock_instance.text.return_value = []
        mock_ddgs.return_value.__enter__.return_value = mock_instance

        results = search_web("test query")
        assert results == "Aucun résultat trouvé."

    @patch("veille.DDGS")
    def test_search_web_exception(self, mock_ddgs):
        mock_ddgs.return_value.__enter__.side_effect = Exception("Network Error")
        results = search_web("test query")
        assert "Impossible de récupérer" in results

    @patch("veille.search_web")
    @patch("veille.get_text_completion")
    def test_do_veille_integration(self, mock_get_completion, mock_search):
        mock_search.return_value = "Résultat de recherche : Batterie pas cher à Lomé"
        mock_get_completion.return_value = "Rapport de veille : Les prix stagnent."

        result = do_veille("marche")
        mock_search.assert_called_once_with("prix pieces detachees reparation Afrique de l'Ouest")
        mock_get_completion.assert_called_once()
        assert result == "Rapport de veille : Les prix stagnent."


class TestVeilleAPI:
    def test_veille_topics(self, client):
        r = client.get("/api/veille/topics")
        assert r.status_code == 200
        data = r.json()
        assert "topics" in data
        assert any(t["key"] == "marche" for t in data["topics"])

    def test_veille_unauthorized(self, client):
        r = client.post("/api/veille", json={"topic": "marche"})
        assert r.status_code == 403

    @patch("veille.do_veille")
    def test_veille_authorized_success(self, mock_do_veille, client, admin_headers):
        mock_do_veille.return_value = "Veille générée avec succès."
        
        r = client.post(
            "/api/veille", 
            json={"topic": "marche", "custom_text": ""}, 
            headers=admin_headers
        )
        assert r.status_code == 200
        data = r.json()
        assert data["topic"] == "marche"
        assert data["result"] == "Veille générée avec succès."
