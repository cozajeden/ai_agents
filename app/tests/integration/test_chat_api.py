import pytest
from unittest.mock import patch

class TestChatAPI:
    """Integration tests for Chat API endpoints"""
    
    def test_chat_endpoint_success(self, client, sample_chat_request):
        """Test successful chat request"""
        with patch('routers.chat.chat_agent') as mock_agent:
            mock_agent.chat.return_value = {
                "response": "Hello! How can I help you?",
                "error": "",
                "model_name": "llama3.1:8b",
                "conversation_history": [
                    {"role": "user", "content": "Hello, how are you?"},
                    {"role": "assistant", "content": "Hello! How can I help you?"}
                ]
            }
            
            response = client.post("/api/v1/ollama/chat/", json=sample_chat_request)
            
            assert response.status_code == 200
            data = response.json()
            assert data["response"] == "Hello! How can I help you?"
            assert data["model_name"] == "llama3.1:8b"
            assert "session_id" in data
    
    def test_chat_endpoint_empty_message(self, client):
        """Test chat request with empty message"""
        request_data = {"message": "", "model_name": "llama3.1:8b"}
        
        response = client.post("/api/v1/ollama/chat/", json=request_data)
        
        assert response.status_code == 400
        assert "Message cannot be empty" in response.json()["detail"]
    
    def test_chat_endpoint_missing_model(self, client):
        """Test chat request without model name"""
        request_data = {"message": "Hello"}
        
        response = client.post("/api/v1/ollama/chat/", json=request_data)
        
        assert response.status_code == 400
        assert "Model name is required" in response.json()["detail"]
    
    def test_chat_endpoint_with_session_id(self, client, sample_chat_request):
        """Test chat request with existing session ID"""
        sample_chat_request["session_id"] = "test-session-123"
        
        with patch('routers.chat.chat_agent') as mock_agent:
            mock_agent.chat.return_value = {
                "response": "I remember you!",
                "error": "",
                "model_name": "llama3.1:8b",
                "conversation_history": [
                    {"role": "user", "content": "Hello, how are you?"},
                    {"role": "assistant", "content": "Hello! How can I help you?"},
                    {"role": "user", "content": "Hello, how are you?"},
                    {"role": "assistant", "content": "I remember you!"}
                ]
            }
            
            response = client.post("/api/v1/ollama/chat/", json=sample_chat_request)
            
            assert response.status_code == 200
            data = response.json()
            assert data["session_id"] == "test-session-123"
            assert len(data["conversation_history"]) == 4
    
    def test_chat_health_check(self, client):
        """Test chat health check endpoint"""
        with patch('routers.chat.chat_agent') as mock_agent:
            mock_agent.get_available_models.return_value = ["llama3.1:8b", "gpt-oss:20b"]
            mock_agent.ollama_base_url = "http://ollama:11434"
            
            response = client.get("/api/v1/ollama/chat/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert data["available_models"] == 2
            assert data["ollama_url"] == "http://ollama:11434"
