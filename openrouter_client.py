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

try:
    from config import MODEL, MAX_TOKENS, TEMPERATURE
except ImportError:
    # Default values if config.py doesn't exist
    MODEL = "google/gemini-2.5-pro"
    MAX_TOKENS = 900000
    TEMPERATURE = 0.7

class OpenRouterClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:3000",
            "X-Title": "PRD Generator"
        }
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
        """Send PRD to Gemini and get code response"""
        
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
        
        IMPORTANT: With our 900k token limit, please provide COMPLETE, DETAILED implementations.
        Do not use comments like "// Add more code here" or placeholders.
        Every function should be fully implemented.
        
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
        
        payload = {
            "model": MODEL,  # Uses model from config.py
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": TEMPERATURE,
            "max_tokens": max_tokens if max_tokens else MAX_TOKENS
        }
        
        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            
            # Extract token usage if available
            usage = result.get('usage', {})
            token_info = {
                'estimated_input': input_tokens,
                'actual_input': usage.get('prompt_tokens', 0),
                'output': usage.get('completion_tokens', 0),
                'total': usage.get('total_tokens', 0)
            }
            
            return result, token_info
            
        except requests.exceptions.RequestException as e:
            print(f"Error calling API: {e}")
            if hasattr(e, 'response') and e.response:
                print(f"Response status: {e.response.status_code}")
                print(f"Response body: {e.response.text}")
            return None, None    
    def save_project_files(self, response_data, output_dir="output", token_info=None):
        """Save the generated code files to disk"""
        
        if not response_data:
            print("No response data to save")
            return False
        
        try:
            # Extract the content from API response
            content = response_data['choices'][0]['message']['content']
            
            # Debug: Save raw content for inspection
            debug_path = os.path.join(output_dir, f"raw_content_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
            os.makedirs(output_dir, exist_ok=True)
            with open(debug_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Debug: Raw content saved to {debug_path}")
            
            # Try to parse as JSON
            project_data = None
            
            # Method 1: Direct JSON parsing with fixing
            if content.strip().startswith('{'):
                try:
                    # First, try to fix common JSON issues
                    fixed_content = content
                    
                    # Fix unterminated strings by ensuring quotes are closed
                    fixed_content = re.sub(r'("(?:[^"\\]|\\.)*?)(?<!\\)$', r'\1"', fixed_content, flags=re.MULTILINE)
                    
                    # Remove trailing commas
                    fixed_content = re.sub(r',\s*}', '}', fixed_content)
                    fixed_content = re.sub(r',\s*\]', ']', fixed_content)
                    
                    # Ensure the JSON is properly closed
                    open_braces = fixed_content.count('{') - fixed_content.count('}')
                    if open_braces > 0:
                        fixed_content += '}' * open_braces
                    
                    open_brackets = fixed_content.count('[') - fixed_content.count(']')
                    if open_brackets > 0:
                        fixed_content += ']' * open_brackets
                    
                    project_data = json.loads(fixed_content)
                    print("Successfully parsed JSON (with fixes applied)")
                except json.JSONDecodeError as e:
                    print(f"Direct JSON parsing failed: {e}")
            
            # Method 2: Extract from markdown code blocks
            if not project_data:
                import re
                # Try to find JSON in code blocks
                json_matches = re.findall(r'```(?:json)?\s*([\s\S]*?)\s*```', content)
                
                for match in json_matches:
                    try:
                        # Apply same fixes to code block content
                        fixed_match = match
                        
                        # Fix unterminated strings
                        fixed_match = re.sub(r'("(?:[^"\\]|\\.)*?)(?<!\\)$', r'\1"', fixed_match, flags=re.MULTILINE)
                        
                        # Remove trailing commas
                        fixed_match = re.sub(r',\s*}', '}', fixed_match)
                        fixed_match = re.sub(r',\s*\]', ']', fixed_match)
                        
                        # Ensure proper closing
                        open_braces = fixed_match.count('{') - fixed_match.count('}')
                        if open_braces > 0:
                            fixed_match += '}' * open_braces
                        
                        open_brackets = fixed_match.count('[') - fixed_match.count(']')
                        if open_brackets > 0:
                            fixed_match += ']' * open_brackets
                        
                        project_data = json.loads(fixed_match)
                        print("Successfully extracted JSON from code block (with fixes)")
                        break
                    except json.JSONDecodeError:
                        continue
            
            # Method 3: Try to extract just the files array if JSON is partial
            if not project_data:
                # Look for project name
                name_match = re.search(r'"project_name"\s*:\s*"([^"]+)"', content)
                project_name = name_match.group(1) if name_match else 'generated_project'
                
                # Look for files array
                files_match = re.search(r'"files"\s*:\s*\[([\s\S]+)\]', content)
                if files_match:
                    try:
                        # Try to parse just the files array
                        files_content = '[' + files_match.group(1) + ']'
                        files_array = json.loads(files_content)
                        project_data = {
                            'project_name': project_name,
                            'files': files_array
                        }
                        print("Successfully reconstructed project data from partial JSON")
                    except:
                        pass
            
            if not project_data:
                print("Could not parse response as JSON. Please check the raw content file.")
                return False
            
            # Create output directory
            project_name = project_data.get('project_name', 'generated_project')
            project_path = os.path.join(output_dir, project_name)
            os.makedirs(project_path, exist_ok=True)
            
            # Save each file
            saved_files = []
            total_size = 0
            for file_info in project_data.get('files', []):
                file_path = os.path.join(project_path, file_info['path'])
                file_dir = os.path.dirname(file_path)
                
                # Create directories if needed
                os.makedirs(file_dir, exist_ok=True)
                
                # Write file
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(file_info['content'])
                
                saved_files.append(file_path)
                total_size += len(file_info['content'])
                print(f"Created: {file_path}")
            
            # Save token usage info if provided
            if token_info:
                info_path = os.path.join(project_path, '_generation_info.json')
                with open(info_path, 'w', encoding='utf-8') as f:
                    json.dump({
                        'generation_date': datetime.now().isoformat(),
                        'model': MODEL,
                        'token_usage': token_info,
                        'files_created': len(saved_files),
                        'total_size_bytes': total_size,
                        'output_directory': os.path.abspath(project_path)
                    }, f, indent=2)
            
            print(f"\nProject created successfully at: {os.path.abspath(project_path)}")
            print(f"Total files created: {len(saved_files)}")
            print(f"Total size: {total_size / 1024:.2f} KB")
            
            if token_info:
                print(f"\nToken Usage:")
                print(f"- Estimated input: {token_info['estimated_input']:,} tokens")
                print(f"- Actual input: {token_info['actual_input']:,} tokens")
                print(f"- Output: {token_info['output']:,} tokens")
                print(f"- Total: {token_info['total']:,} tokens")
                cost_input = token_info['actual_input'] * 0.0075 / 1000  # $7.50 per 1M tokens
                cost_output = token_info['output'] * 0.03 / 1000  # $30 per 1M tokens
                print(f"- Estimated cost: ${cost_input + cost_output:.4f}")
            
            return True
            
        except Exception as e:
            print(f"Error saving files: {e}")
            import traceback
            traceback.print_exc()
            return False