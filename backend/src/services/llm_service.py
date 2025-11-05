"""LLM Service for OpenRouter API integration."""
import httpx
from typing import List, Dict, Optional
import os
from langfuse import Langfuse


class LLMService:
    """Service for interacting with LLMs via OpenRouter API."""
    
    def __init__(self, api_key: str):
        """Initialize LLM service with API key."""
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "https://github.com/dispatcher-agents",
            "X-Title": "Dispatcher Agents"
        }
        
        # Initialize Langfuse for observability
        langfuse_public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
        langfuse_secret_key = os.getenv("LANGFUSE_SECRET_KEY")
        langfuse_host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
        
        if langfuse_public_key and langfuse_secret_key:
            self.langfuse = Langfuse(
                public_key=langfuse_public_key,
                secret_key=langfuse_secret_key,
                host=langfuse_host
            )
            self.langfuse_enabled = True
        else:
            self.langfuse = None
            self.langfuse_enabled = False
            print("⚠ Langfuse not configured - observability disabled")
    
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        model: str = "openai/gpt-4o-mini",
        temperature: float = 0.7,
        trace_name: str = "llm_call"
    ) -> str:
        """
        Generate a response from the LLM.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Model to use for generation
            temperature: Temperature for generation (0.0 to 1.0)
            trace_name: Name for Langfuse trace
        
        Returns:
            Generated text response
        """
        # Create Langfuse trace if enabled
        trace = None
        generation = None
        
        if self.langfuse_enabled:
            try:
                trace = self.langfuse.trace(name=trace_name)
                generation = trace.generation(
                    name="openrouter_chat",
                    model=model,
                    input=messages,
                    metadata={"temperature": temperature}
                )
            except Exception as e:
                print(f"⚠ Langfuse trace creation failed: {e}")
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json={
                        "model": model,
                        "messages": messages,
                        "temperature": temperature
                    }
                )
                response.raise_for_status()
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                
                # Log successful response to Langfuse
                if generation:
                    try:
                        generation.end(
                            output=content,
                            metadata={
                                "usage": data.get("usage", {}),
                                "model": model
                            }
                        )
                    except Exception as e:
                        print(f"⚠ Langfuse logging failed: {e}")
                
                return content
                
            except httpx.HTTPStatusError as e:
                # Log error to Langfuse
                if generation:
                    try:
                        generation.end(
                            output=None,
                            level="ERROR",
                            status_message=f"HTTP {e.response.status_code}"
                        )
                    except:
                        pass
                raise Exception(f"HTTP error {e.response.status_code}: {e.response.text}")
            except httpx.TimeoutException:
                if generation:
                    try:
                        generation.end(output=None, level="ERROR", status_message="Timeout")
                    except:
                        pass
                raise Exception("Request timed out")
            except Exception as e:
                if generation:
                    try:
                        generation.end(output=None, level="ERROR", status_message=str(e))
                    except:
                        pass
                raise Exception(f"LLM generation error: {str(e)}")

