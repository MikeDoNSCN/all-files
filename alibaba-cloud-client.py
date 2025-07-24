"""
ALIBABA-CLOUD-CLIENT.PY - Direct Alibaba Cloud Model Studio API Client
Created: 23/7/2025
"""

import requests
import json
import tiktoken
import os
from typing import Tuple, Optional, Dict, Any

class AlibabCloudClient:
    """Client for direct Alibaba Cloud Model Studio API access"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://dashscope-intl.aliyuncs.com"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Model configurations
        self.models = {
            "qwen-max": {
                "name": "Qwen-Max",
                "model_id": "qwen-max-2025-01-25",
                "max_tokens": 32768,
                "supports_thinking": False
            },
            "qwen-plus": {
                "name": "Qwen-Plus",
                "model_id": "qwen-plus-2025-04-28",
                "max_tokens": 131072,
                "supports_thinking": True
            },
            "qwen-turbo": {
                "name": "Qwen-Turbo",
                "model_id": "qwen-turbo-2025-04-28",
                "max_tokens": 131072,
                "supports_thinking": True
            },
            # Add new models here:
            "qwen3-coder-480b-a35b-instruct": {
                "name": "Qwen3-Coder-480B",
                "model_id": "qwen3-coder-480b-a35b-instruct",
                "max_tokens": 131072,
                "supports_thinking": True
            },
            "qwen3-turbo": {
                "name": "Qwen3-Turbo",
                "model_id": "qwen3-turbo",
                "max_tokens": 131072,
                "supports_thinking": True
            },
            "qwen-long": {
                "name": "Qwen-Long",
                "model_id": "qwen-long",
                "max_tokens": 1000000,
                "supports_thinking": False
            }
        }
        
        # Default model
        self.model = "qwen-plus"
        self.temperature = 0.6
        self.enable_thinking = False
        
        # Initialize tokenizer
        try:
            self.tokenizer = tiktoken.encoding_for_model("gpt-4")
        except:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for text"""
        return len(self.tokenizer.encode(text))
    
    def set_model(self, model_key: str):
        """Set the active model"""
        if model_key in self.models:
            self.model = model_key
            print(f"Model set to: {self.models[model_key]['name']}")
        else:
            print(f"Unknown model: {model_key}")
    
    def send_completion(self, messages: list, max_tokens: int = 4000, 
                       enable_thinking: Optional[bool] = None) -> Tuple[Optional[str], Dict[str, Any]]:
        """Send completion request to Alibaba Cloud"""
        
        model_config = self.models.get(self.model, self.models["qwen-plus"])
        model_id = model_config["model_id"]
        
        # Use model's thinking capability if supported
        use_thinking = enable_thinking if enable_thinking is not None else self.enable_thinking
        if use_thinking and not model_config["supports_thinking"]:
            print(f"Warning: {model_config['name']} doesn't support thinking mode")
            use_thinking = False
        
        # OpenAI-compatible endpoint
        url = f"{self.base_url}/compatible-mode/v1/chat/completions"
        
        data = {
            "model": model_id,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": min(max_tokens, model_config["max_tokens"]),
            "stream": False
        }
        
        # Add thinking parameter if supported
        if use_thinking and model_config["supports_thinking"]:
            # For newer Qwen models, enable_thinking is in extra_body
            data["extra_body"] = {"enable_thinking": True}
            print("🧠 Thinking mode enabled")
        
        try:
            print(f"Sending request to {model_config['name']} ({model_id})...")
            response = requests.post(url, headers=self.headers, json=data, timeout=120)
            
            if response.status_code == 200:
                result = response.json()
                
                # Extract content
                content = result['choices'][0]['message']['content']
                
                # Token usage
                usage = result.get('usage', {})
                token_info = {
                    'input_tokens': usage.get('prompt_tokens', 0),
                    'output_tokens': usage.get('completion_tokens', 0),
                    'total_tokens': usage.get('total_tokens', 0),
                    'model': model_id,
                    'thinking_enabled': use_thinking
                }
                
                return content, token_info
            else:
                print(f"Error: {response.status_code}")
                print(response.text)
                return None, {'error': response.text}
                
        except Exception as e:
            print(f"Exception: {str(e)}")
            return None, {'error': str(e)}
    
    def send_prd_request(self, prd_content: str, project_name: str, 
                        output_dir: str, max_tokens: int = 100000) -> Tuple[Optional[str], Dict[str, Any]]:
        """Send PRD to model for code generation"""
        
        model_config = self.models.get(self.model, self.models["qwen-plus"])
        
        # Enhanced system prompt for Alibaba Cloud models
        system_prompt = f"""You are an expert full-stack developer using {model_config['name']} from Alibaba Cloud.
Convert the PRD (Product Requirements Document) into a complete, working codebase.

CRITICAL INSTRUCTIONS:
1. Generate COMPLETE, PRODUCTION-READY code
2. Create ALL necessary files with FULL implementation
3. NO placeholders, NO TODOs, NO comments like "implement later"
4. Include proper error handling and validation
5. Follow modern best practices and design patterns

Project Structure Requirements:
- Create a well-organized directory structure
- Include all configuration files (package.json, requirements.txt, etc.)
- Add a comprehensive README.md with setup instructions
- Include example .env files where needed

Output Format:
For each file, use this EXACT format:

### Path: <relative/path/to/file>
```<language>
<complete file content>
```

Start with the directory structure overview, then generate each file."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Project Name: {project_name}\n\nPRD Content:\n{prd_content}\n\nGenerate the complete codebase."}
        ]
        
        # Enable thinking mode for complex code generation if supported
        use_thinking = model_config["supports_thinking"] and self.enable_thinking
        
        return self.send_completion(messages, max_tokens, use_thinking)
    
    def test_connection(self) -> bool:
        """Test API connection"""
        messages = [{"role": "user", "content": "Say 'Hello from Alibaba Cloud!'"}]
        response, _ = self.send_completion(messages, max_tokens=20)
        return response is not None
