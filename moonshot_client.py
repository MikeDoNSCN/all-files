import requests
import json
import os
from datetime import datetime
try:
    import tiktoken
    HAS_TIKTOKEN = True
except ImportError:
    HAS_TIKTOKEN = False
    print("Warning: tiktoken not installed. Token estimation will be approximate.")

class MoonshotClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.moonshot.cn/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        # Kimi K2 specific settings
        self.model = "kimi"  # Kimi K2 API model identifier
        self.temperature = 0.6  # Recommended temperature for Kimi K2
        self.max_context = 128000  # 128k context window
        
        # Initialize tokenizer for estimation
        self.tokenizer = None
        if HAS_TIKTOKEN:
            try:
                self.tokenizer = tiktoken.get_encoding("cl100k_base")
            except:
                self.tokenizer = None
    
    def estimate_tokens(self, text):
        """Estimate token count for text"""
        if self.tokenizer:
            return len(self.tokenizer.encode(text))
        else:
            # Rough estimation: 1 token ≈ 4 characters
            return len(text) // 4
    
    def send_prd_request(self, prd_content, project_name="MyProject", output_dir="output", max_tokens=None):
        """Send PRD to Kimi K2 and get code response"""
        
        if max_tokens is None:
            max_tokens = 100000  # Default for Kimi K2
        
        # Ensure max_tokens doesn't exceed model limit
        max_tokens = min(max_tokens, self.max_context - self.estimate_tokens(prd_content) - 1000)
        
        prompt = f"""Based on the following PRD (Product Requirements Document), 
        create a complete, production-ready project with all necessary code files.
        
        PRD Content:
        {prd_content}
        
        Please provide a COMPLETE implementation including:
        1. Full file structure with all directories
        2. ALL necessary code files with complete implementations (no placeholders)
        3. Configuration files (package.json, requirements.txt, etc.)
        4. Environment files (.env.example)
        5. Comprehensive README.md with:
           - Project overview
           - Installation instructions
           - Usage examples
           - API documentation (if applicable)
           - Deployment guide
        6. Unit tests for core functionality
        7. Docker configuration if applicable
        8. CI/CD configuration files (GitHub Actions, etc.) if applicable
        9. Database schemas/migrations if applicable
        10. Any additional files needed for a production-ready application
        
        IMPORTANT: Please provide COMPLETE, DETAILED implementations.
        Do not use comments like "// Add more code here" or placeholders.
        Every function should be fully implemented.
        Focus on clean, efficient code that leverages modern best practices.
        
        If the PRD doesn't specify a project name, use an appropriate name based on the content.
        
        Format your response as JSON with this structure:
        {{
            "project_name": "appropriate_project_name_based_on_content",
            "files": [
                {{
                    "path": "relative/path/to/file.ext",
                    "content": "complete file content here"
                }}
            ]
        }}
        """
        
        # Estimate input tokens
        input_tokens = self.estimate_tokens(prompt)
        print(f"Estimated input tokens: {input_tokens}")
        print(f"Max output tokens: {max_tokens}")
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are Kimi, an AI assistant created by Moonshot AI. You are an expert software developer who creates complete, production-ready code based on requirements. You always respond with valid JSON containing the complete project structure and all file contents."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": max_tokens,
            "temperature": self.temperature,
            "top_p": 1.0,
            "n": 1,
            "stream": False,
            "presence_penalty": 0,
            "frequency_penalty": 0
        }
        
        try:
            print("Sending request to Kimi K2 API...")
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=120  # 2 minute timeout for large responses
            )
            
            response.raise_for_status()
            
            result = response.json()
            
            # Extract the content
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0]['message']['content']
                
                # Get token usage info
                usage = result.get('usage', {})
                token_info = {
                    'actual_input': usage.get('prompt_tokens', input_tokens),
                    'output': usage.get('completion_tokens', 0),
                    'total': usage.get('total_tokens', input_tokens)
                }
                
                print(f"Response received. Tokens used - Input: {token_info['actual_input']}, Output: {token_info['output']}")
                
                # Try to extract JSON from the response
                # Sometimes the model might wrap it in markdown or other text
                import re
                
                # First try to find JSON block in markdown
                json_match = re.search(r'```json\s*([\s\S]*?)\s*```', content)
                if json_match:
                    json_content = json_match.group(1)
                else:
                    # Try to find raw JSON
                    json_match = re.search(r'\{[\s\S]*\}', content)
                    if json_match:
                        json_content = json_match.group()
                    else:
                        json_content = content
                
                # Validate it's proper JSON
                try:
                    json.loads(json_content)
                    return json_content, token_info
                except:
                    # If not valid JSON, wrap the content in a basic structure
                    fallback_response = {
                        "project_name": project_name,
                        "files": [
                            {
                                "path": "README.md",
                                "content": content
                            }
                        ]
                    }
                    return json.dumps(fallback_response, indent=2), token_info
            else:
                print("No choices in response")
                return None, {'actual_input': input_tokens, 'output': 0, 'total': input_tokens}
                
        except requests.exceptions.Timeout:
            print("Request timed out")
            return None, {'actual_input': input_tokens, 'output': 0, 'total': input_tokens}
        except requests.exceptions.RequestException as e:
            print(f"Request error: {str(e)}")
            if hasattr(e.response, 'text'):
                print(f"Response text: {e.response.text}")
            return None, {'actual_input': input_tokens, 'output': 0, 'total': input_tokens}
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return None, {'actual_input': input_tokens, 'output': 0, 'total': input_tokens}