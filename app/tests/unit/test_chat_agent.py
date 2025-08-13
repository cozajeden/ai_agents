import pytest
from unittest.mock import Mock, patch
import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from agents.chat_agent import OllamaChatAgent, ChatState
from langchain_core.messages import HumanMessage, AIMessage

class TestOllamaChatAgent:
    """Unit tests for OllamaChatAgent"""
    
    @pytest.fixture
    def chat_agent(self):
        """Create a chat agent instance for testing"""
        with patch('agents.chat_agent.httpx.Client') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"models": [{"name": "llama3.1:8b"}]}
            mock_client.return_value.__enter__.return_value.get.return_value = mock_response
            
            agent = OllamaChatAgent()
            return agent
    
    def test_initialization(self, chat_agent):
        """Test chat agent initialization"""
        assert chat_agent.ollama_base_url == "http://ollama:11434"
        assert "llama3.1:8b" in chat_agent.available_models
    
    def test_get_available_models(self, chat_agent):
        """Test getting available models"""
        models = chat_agent.get_available_models()
        assert isinstance(models, list)
        assert "llama3.1:8b" in models
    
    def test_create_llm(self, chat_agent):
        """Test LLM creation"""
        with patch('agents.chat_agent.OllamaLLM') as mock_ollama:
            mock_llm = Mock()
            mock_ollama.return_value = mock_llm
            
            llm = chat_agent.create_llm("llama3.1:8b")
            
            mock_ollama.assert_called_once_with(
                base_url="http://ollama:11434",
                model="llama3.1:8b",
                temperature=0.7
            )
    
    def test_chat_node_valid_message(self, chat_agent):
        """Test chat node with valid message"""
        messages = [HumanMessage(content="Hello")]
        state = ChatState(
            messages=messages,
            model_name="llama3.1:8b",
            response="",
            error=""
        )
        
        with patch.object(chat_agent, 'create_llm') as mock_create_llm:
            mock_llm = Mock()
            mock_llm.invoke.return_value = "Hello! How can I help you?"
            mock_create_llm.return_value = mock_llm
            
            result = chat_agent.chat_node(state)
            
            assert result["response"] == "Hello! How can I help you?"
            assert result["error"] == ""
            assert len(result["messages"]) == 2  # Original + AI response
    
    def test_chat_node_no_message(self, chat_agent):
        """Test chat node with no valid message"""
        state = ChatState(
            messages=[],
            model_name="llama3.1:8b",
            response="",
            error=""
        )
        
        result = chat_agent.chat_node(state)
        
        assert result["error"] == "No valid human message found"
        assert result["response"] == ""
    
    def test_create_graph(self, chat_agent):
        """Test graph creation"""
        graph = chat_agent.create_graph()
        assert graph is not None
        # Verify graph structure
        assert hasattr(graph, 'nodes')
        assert 'chat' in graph.nodes
    
    def test_chat_invalid_model(self, chat_agent):
        """Test chat with invalid model"""
        result = chat_agent.chat("Hello", "invalid-model")
        
        assert "invalid-model not available" in result["error"]
        assert result["response"] == ""
    
    def test_chat_with_conversation_history(self, chat_agent):
        """Test chat with conversation history"""
        conversation_history = [
            {"role": "user", "content": "Hi"},
            {"role": "assistant", "content": "Hello!"}
        ]
        
        with patch.object(chat_agent, 'create_graph') as mock_create_graph:
            mock_graph = Mock()
            mock_graph.invoke.return_value = ChatState(
                messages=[HumanMessage(content="Hi"), AIMessage(content="Hello!")],
                model_name="llama3.1:8b",
                response="Hello! How are you?",
                error=""
            )
            mock_create_graph.return_value = mock_graph
            
            result = chat_agent.chat("How are you?", "llama3.1:8b", conversation_history)
            
            assert result["response"] == "Hello! How are you?"
            assert result["error"] == ""
            assert len(result["conversation_history"]) == 3  # 2 from history + 1 new
