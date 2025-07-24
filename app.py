"""
PRD-GENERATOR SERVER - Multi-Model Code Generation Platform
Created: July 23, 2025
Updated: July 23, 2025

Features:
- Multi-model support (Gemini, Kimi K2, Qwen-Plus, Qwen-Max)
- Direct Alibaba Cloud API integration for Qwen models
- File-based configuration storage
- Token estimation and cost calculation
- Automatic code generation from PRDs

Models:
- Gemini 2.5 Pro: Fast, 2M context (via OpenRouter)
- Kimi K2: Agent systems, 128K context (via Moonshot)
- Qwen-Plus: 131K context with thinking mode (via Alibaba Direct)
- Qwen-Max: 32K context, flagship model (via Alibaba Direct)
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import json
from openrouter_client import OpenRouterClient
from moonshot_client import MoonshotClient
from werkzeug.utils import secure_filename
import tempfile
import shutil
import random
import sys
from datetime import datetime
from datetime import datetime

# Import our config manager
from config_manager import config_manager

# Import Alibaba Cloud client (handling hyphenated filename)
import importlib.util
spec = importlib.util.spec_from_file_location("alibaba_cloud_client", "alibaba-cloud-client.py")
alibaba_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(alibaba_module)
AlibabCloudClient = alibaba_module.AlibabCloudClient

# Load Alibaba API keys from environment or config file
ALIBABA_KEYS = []
# Try to load from environment variables
for i in range(1, 4):
    key = os.getenv(f'ALIBABA_API_KEY_{i}')
    if key:
        ALIBABA_KEYS.append(key)

# If no env keys, try config file (but DON'T commit this file!)
if not ALIBABA_KEYS:
    try:
        with open('config/ALIBABA-KEYS.json', 'r') as f:
            ALIBABA_KEYS = json.load(f)  # Directly load the array
    except Exception as e:
        print(f"WARNING: No Alibaba API keys found. Qwen models won't work. Error: {e}")

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
CORS(app)

# Add request logging
@app.before_request
def log_request_info():
    print(f">>> {request.method} {request.path}", flush=True)
    if request.method == 'POST':
        print(f">>> Form data: {dict(request.form)}", flush=True)
        print(f">>> Files: {list(request.files.keys())}", flush=True)

# Add health check endpoint
@app.route('/health')
def health_check():
    """Simple health check endpoint for the UI."""
    return jsonify({'status': 'healthy'}), 200

# Serve the HTML file
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

# Serve static files
@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('.', filename)

# Get API keys from environment
@app.route('/api/config', methods=['GET'])
def get_config():
    return jsonify({
        'openrouterApiKey': os.getenv('OPENROUTER_API_KEY', ''),
        'moonshotApiKey': os.getenv('MOONSHOT_API_KEY', '')
    })

# New configuration management endpoints
@app.route('/api/config/keys', methods=['GET'])
def get_api_keys():
    """Get API keys from local file storage"""
    keys = config_manager.get_api_keys()
    # Also check .env file as fallback
    if not keys.get('openrouter_api_key'):
        keys['openrouter_api_key'] = os.getenv('OPENROUTER_API_KEY', '')
    if not keys.get('moonshot_api_key'):
        keys['moonshot_api_key'] = os.getenv('MOONSHOT_API_KEY', '')
    return jsonify(keys)

@app.route('/api/config/keys', methods=['POST'])
def save_api_keys():
    """Save API keys to local file storage"""
    data = request.json
    for key, value in data.items():
        config_manager.save_api_key(key, value)
    return jsonify({'success': True})

@app.route('/api/config/settings', methods=['GET'])
def get_settings():
    """Get settings from local file storage"""
    return jsonify(config_manager.get_settings())

@app.route('/api/config/settings', methods=['POST'])
def save_settings():
    """Save settings to local file storage"""
    data = request.json
    for key, value in data.items():
        config_manager.save_setting(key, value)
    return jsonify({'success': True})

@app.route('/api/config/paths', methods=['GET'])
def get_path_history():
    """Get path history from local file storage"""
    return jsonify({'paths': config_manager.get_path_history()})

@app.route('/api/config/paths', methods=['POST'])
def add_path():
    """Add path to history"""
    data = request.json
    config_manager.add_path_to_history(data.get('path', ''))
    return jsonify({'success': True})

@app.route('/api/config/paths/remove', methods=['POST'])
def remove_path():
    """Remove path from history"""
    data = request.json
    config_manager.remove_path_from_history(data.get('path', ''))
    return jsonify({'success': True})

@app.route('/api/config/clear', methods=['POST'])
def clear_config():
    """Clear all configuration data"""
    config_manager.clear_all_data()
    return jsonify({'success': True})

@app.route('/api/generate', methods=['POST'])
def generate_code():
    print("DEBUG - /api/generate endpoint hit!", flush=True)
    print(f"DEBUG - Request form data: {dict(request.form)}", flush=True)
    print(f"DEBUG - Request files: {request.files}", flush=True)
    
    try:
        # Get form data
        api_key = request.form.get('apiKey')
        model = request.form.get('model', 'gemini')
        provider = request.form.get('provider', 'openrouter')
        output_dir = request.form.get('outputDir', 'output')
        prd_text = request.form.get('prdText', '')
        max_tokens = request.form.get('maxTokens', '100000')
        alibaba_key_index = request.form.get('alibabaKeyIndex', '0')  # New field for manual selection
        
        print(f"DEBUG - Received: model={model}, provider={provider}, output_dir={output_dir}", flush=True)
        print(f"DEBUG - API key: {api_key[:10] if api_key else 'None'}...", flush=True)
        print(f"DEBUG - ALIBABA_KEYS available: {len(ALIBABA_KEYS)}", flush=True)
        
        # Check if API key is needed (not needed for Alibaba models)
        if model in ['qwen', 'qwen235']:
            # Use built-in Alibaba keys
            if not ALIBABA_KEYS:
                return jsonify({'error': 'Alibaba API keys not configured in server. Please configure ALIBABA_API_KEY_1 environment variable or create config/ALIBABA-KEYS.json file.'}), 400
            
            # Manual key selection
            try:
                key_index = int(alibaba_key_index)
                if 0 <= key_index < len(ALIBABA_KEYS):
                    api_key = ALIBABA_KEYS[key_index]
                    print(f"DEBUG - Using Alibaba key index {key_index}", flush=True)
                else:
                    return jsonify({'error': f'Invalid key index {key_index}. Available: 0-{len(ALIBABA_KEYS)-1}'}), 400
            except ValueError:
                api_key = ALIBABA_KEYS[0]  # Default to first key
                print(f"DEBUG - Using default Alibaba key (index 0)", flush=True)
        elif not api_key or api_key == 'built-in':
            return jsonify({'error': f'Please provide API key for {model}'}), 400
        
        # Clean and validate the output directory path
        output_dir = output_dir.strip('"').strip("'").strip()
        
        # Debug logging
        print(f"DEBUG - Original output_dir: '{output_dir}'")
        
        # Replace forward slashes with backslashes for Windows consistency
        output_dir = output_dir.replace('/', '\\')
        
        # Security: Prevent directory traversal
        if '..' in output_dir:
            return jsonify({'error': 'Invalid output directory path - directory traversal not allowed'}), 400
        
        # Don't validate paths too strictly - let the OS handle it
        # Just ensure it's not empty
        if not output_dir:
            output_dir = 'output'  # Default to 'output' if empty
            
        print(f"DEBUG - Processed output_dir: '{output_dir}'")
        
        # Convert max_tokens to int
        try:
            max_tokens = int(max_tokens)
        except:
            max_tokens = 100000  # Default fallback
        
        # Handle file uploads
        files = request.files.getlist('prdFiles')
        
        # Combine PRD content from files and text
        combined_content = []
        project_name = None
        
        # Add uploaded files content and try to extract project name
        for file in files:
            if file and file.filename:
                content = file.read().decode('utf-8')
                combined_content.append(f"=== File: {file.filename} ===\n{content}")
                
                # Try to extract project name from first file name if not set
                if not project_name:
                    project_name = os.path.splitext(file.filename)[0]
                    # Clean up the project name
                    project_name = project_name.replace(' ', '_').replace('-', '_')
        
        # Add pasted text if no files
        if not combined_content and prd_text:
            combined_content.append(prd_text)
        
        if not combined_content:
            return jsonify({'error': 'No PRD content provided'}), 400
        
        # Combine all content
        full_prd_content = "\n\n".join(combined_content)
        
        # If still no project name, try to extract from content or use default
        if not project_name:
            # Try to find project name in content (look for # Project: or similar)
            import re
            name_match = re.search(r'#\s*(?:Project|App|Application|System)(?:\s*Name)?:\s*(.+)', full_prd_content, re.IGNORECASE)
            if name_match:
                project_name = name_match.group(1).strip()
                project_name = project_name.replace(' ', '_').replace('-', '_')
            else:
                # Use timestamp as default
                project_name = f"generated_project_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Initialize appropriate client based on model selection
        if model == 'kimi':
            print(f"Using Kimi K2 model via Moonshot AI...")
            client = MoonshotClient(api_key)
        elif model == 'qwen':
            print(f"Using Qwen-Plus via Alibaba Direct API...")
            client = AlibabCloudClient(api_key)
            client.set_model('qwen-plus')
            client.enable_thinking = True  # Enable thinking mode for code generation
        elif model == 'qwen235':
            print(f"Using Qwen-Max via Alibaba Direct API...")
            client = AlibabCloudClient(api_key)
            client.set_model('qwen-max')
        else:
            print(f"Using Gemini 2.5 Pro model via OpenRouter...")
            client = OpenRouterClient(api_key)
        
        # Estimate tokens
        estimated_input_tokens = client.estimate_tokens(full_prd_content)
        
        # Send request to selected AI model
        print(f"Sending request to {model.upper()} model...")
        print(f"DEBUG - About to send request with output_dir: '{output_dir}'")
        response, token_info = client.send_prd_request(
            full_prd_content, 
            project_name, 
            output_dir,
            max_tokens
        )
        
        print(f"DEBUG - Got response: {bool(response)}")
        
        if not response:
            return jsonify({'error': 'Failed to get response from API'}), 500
        
        # Create absolute path for output
        abs_output_dir = os.path.abspath(output_dir)
        print(f"DEBUG - Absolute path: '{abs_output_dir}'")
        
        # Validate the path
        if not os.path.exists(abs_output_dir):
            print(f"DEBUG - Directory doesn't exist, trying to create: '{abs_output_dir}'")
            # Try to create it
            try:
                os.makedirs(abs_output_dir, exist_ok=True)
                print(f"DEBUG - Successfully created directory: '{abs_output_dir}'")
            except Exception as e:
                print(f"DEBUG - Failed to create directory: {str(e)}")
                return jsonify({'error': f'Invalid output directory: {str(e)}'}), 400
        
        # Create project directory
        project_path = os.path.join(abs_output_dir, project_name)
        
        # If project already exists, add timestamp
        if os.path.exists(project_path):
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            project_name = f"{project_name}_{timestamp}"
            project_path = os.path.join(abs_output_dir, project_name)
        
        os.makedirs(project_path, exist_ok=True)
        
        # Parse JSON response
        try:
            # Try to find JSON in response
            import re
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                response_data = json.loads(json_match.group())
            else:
                return jsonify({'error': 'Invalid response format from AI'}), 500
        except json.JSONDecodeError as e:
            # Save debug response
            debug_file = f"debug_response_{project_name}.json"
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(response)
            return jsonify({'error': f'Failed to parse AI response. Debug saved to {debug_file}'}), 500
        
        # Create files in project directory
        created_files = []
        for file_info in response_data.get('files', []):
            file_path = file_info['path']
            file_content = file_info['content']
            
            # Create full path
            full_path = os.path.join(project_path, file_path)
            
            # Create directory if needed
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            # Write file
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(file_content)
            
            created_files.append(file_path)
        
        # Create generation info file
        generation_info = {
            'project_name': project_name,
            'model': model,
            'provider': 'alibaba_direct' if model in ['qwen', 'qwen235'] else provider,
            'generation_date': datetime.now().isoformat(),
            'input_tokens': estimated_input_tokens,
            'actual_input_tokens': token_info.get('input_tokens', estimated_input_tokens),
            'output_tokens': token_info.get('output_tokens', 0),
            'total_tokens': token_info.get('total_tokens', estimated_input_tokens),
            'files_created': created_files,
            'prd_summary': full_prd_content[:500] + '...' if len(full_prd_content) > 500 else full_prd_content
        }
        
        with open(os.path.join(project_path, '_generation_info.json'), 'w', encoding='utf-8') as f:
            json.dump(generation_info, f, indent=2)
        
        return jsonify({
            'success': True,
            'projectName': project_name,
            'outputPath': project_path,
            'filesCreated': len(created_files),
            'tokenInfo': {
                'actual_input': token_info.get('input_tokens', estimated_input_tokens),
                'output': token_info.get('output_tokens', 0),
                'total': token_info.get('total_tokens', estimated_input_tokens)
            }
        })
        
    except Exception as e:
        import traceback
        print(f"Error: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/api/estimate', methods=['POST'])
def estimate_tokens():
    try:
        data = request.get_json()
        content = data.get('content', '')
        max_tokens = int(data.get('maxTokens', 100000))
        model = data.get('model', 'gemini')
        
        # Initialize appropriate client just for token estimation
        if model == 'kimi':
            from moonshot_client import MoonshotClient
            client = MoonshotClient("dummy_key")  # Just for estimation
        elif model in ['qwen', 'qwen235']:
            # Use Alibaba client for estimation
            client = AlibabCloudClient("dummy_key")
        else:
            from openrouter_client import OpenRouterClient
            client = OpenRouterClient("dummy_key")  # Just for estimation
        
        estimated_tokens = client.estimate_tokens(content)
        
        # Get model-specific max context
        if model == 'kimi':
            max_context = 128000
        elif model == 'qwen':
            max_context = 131072  # qwen-plus
        elif model == 'qwen235':
            max_context = 32768   # qwen-max
        else:
            max_context = 2000000  # gemini
        
        available_output = max_context - estimated_tokens
        
        # Calculate estimated costs based on model
        if model == 'kimi':
            input_cost = estimated_tokens * 0.00015 / 1000  # $0.15 per 1M tokens
        elif model in ['qwen', 'qwen235']:
            # Alibaba direct pricing (estimated)
            input_cost = estimated_tokens * 0.0001 / 1000  # $0.10 per 1M tokens
        else:
            input_cost = estimated_tokens * 0.000075 / 1000  # $0.075 per 1M tokens
        
        return jsonify({
            'contentSize': len(content),
            'estimatedTokens': estimated_tokens,
            'availableOutputTokens': min(available_output, max_tokens),
            'estimatedInputCost': input_cost,
            'model': model
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("PRD Generator Server starting...")
    print("Access the UI at: http://localhost:5000")
    print("Make sure you have your API keys ready!")
    print("\nSupported models:")
    print("- Gemini 2.5 Pro (via OpenRouter)")
    print("- Kimi K2 (via Moonshot AI)")
    print("- Qwen-Plus (via Alibaba Direct API) 🚀")
    print("- Qwen-Max (via Alibaba Direct API) 🚀")
    
    # SECURITY: Set debug=False for production!
    is_production = os.getenv('FLASK_ENV') == 'production'
    app.run(debug=True, port=5000)  # Force debug=True for troubleshooting