from typing import Dict, List, Any, TypedDict
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain_ollama import OllamaLLM
import json
import os

class ChatState(TypedDict):
    messages: List[BaseMessage]
    model_name: str
    response: str
    error: str

class OllamaChatAgent:
    def __init__(self):
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
        self.available_models = []
        self._load_available_models()
    
    def _load_available_models(self):
        """Load available Ollama models"""
        try:
            import httpx
            with httpx.Client() as client:
                response = client.get(f"{self.ollama_base_url}/api/tags")
                if response.status_code == 200:
                    data = response.json()
                    self.available_models = [model["name"] for model in data.get("models", [])]
                else:
                    self.available_models = ["llama3.1:8b", "gpt-oss:20b", "mistral:7b"]
        except Exception:
            self.available_models = ["llama3.1:8b", "gpt-oss:20b", "mistral:7b"]
    
    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        return self.available_models
    
    def create_llm(self, model_name: str) -> OllamaLLM:
        """Create Ollama LLM instance"""
        return OllamaLLM(
            base_url=self.ollama_base_url,
            model=model_name,
            temperature=0.7
        )
    
    def chat_node(self, state: ChatState) -> ChatState:
        """Main chat processing node"""
        try:
            messages = state["messages"]
            if not messages or not isinstance(messages[-1], HumanMessage):
                state["error"] = "No valid human message found"
                return state
            
            llm = self.create_llm(state["model_name"])
            
            response = llm.invoke(messages)
            
            ai_message = AIMessage(content=response)
            messages.append(ai_message)
            
            state["messages"] = messages
            state["response"] = response
            state["error"] = ""
            
        except Exception as e:
            state["error"] = str(e)
            state["response"] = ""
        
        return state
    
    def create_graph(self) -> StateGraph:
        """Create the LangGraph workflow"""
        workflow = StateGraph(ChatState)
        
        workflow.add_node("chat", self.chat_node)
        
        workflow.set_entry_point("chat")
        
        workflow.add_edge("chat", END)
        
        return workflow.compile()
    
    def chat(self, message: str, model_name: str, conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """Process a chat message and return response"""
        if model_name not in self.available_models:
            return {
                "error": f"Model {model_name} not available. Available models: {self.available_models}",
                "response": "",
                "model_name": model_name
            }
        
        messages = []
        if conversation_history:
            for msg in conversation_history:
                if not isinstance(msg, dict):
                    continue
                    
                role = msg.get("role")
                content = msg.get("content")
                
                if role == "user" and content:
                    messages.append(HumanMessage(content=content))
                elif role == "assistant" and content:
                    messages.append(AIMessage(content=content))
                else:
                    continue
        
        messages.append(HumanMessage(content=message))
        
        initial_state = ChatState(
            messages=messages,
            model_name=model_name,
            response="",
            error=""
        )
        
        try:
            graph = self.create_graph()
            final_state = graph.invoke(initial_state)
            
            return {
                "response": final_state["response"],
                "error": final_state["error"],
                "model_name": model_name,
                "conversation_history": [
                    {
                        "role": "user" if isinstance(msg, HumanMessage) else "assistant",
                        "content": msg.content
                    }
                    for msg in final_state["messages"]
                ]
            }
            
        except Exception as e:
            return {
                "error": f"Graph execution failed: {str(e)}",
                "response": "",
                "model_name": model_name
            }
