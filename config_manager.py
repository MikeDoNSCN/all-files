import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging

class ConfigManager:
    """Manages all configuration settings in local files instead of browser storage"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        
        # Define configuration files (following naming convention)
        self.api_keys_file = self.config_dir / "API-KEYS.json"
        self.settings_file = self.config_dir / "SETTINGS.json"
        self.path_history_file = self.config_dir / "path-history.json"
        
        # Initialize files if they don't exist
        self._initialize_files()
        
    def _initialize_files(self):
        """Create config files if they don't exist"""
        default_api_keys = {
            "openrouter_api_key": "",
            "moonshot_api_key": ""
        }
        
        default_settings = {
            "selected_model": "kimi",
            "max_tokens": 100000,
            "temperature": 0.6,
            "output_dir": "output"
        }
        
        default_paths = {
            "recent_paths": [],
            "max_paths": 20
        }
        
        # Create files with defaults if they don't exist
        if not self.api_keys_file.exists():
            self._save_json(self.api_keys_file, default_api_keys)
            
        if not self.settings_file.exists():
            self._save_json(self.settings_file, default_settings)
            
        if not self.path_history_file.exists():
            self._save_json(self.path_history_file, default_paths)
    
    def _load_json(self, filepath: Path) -> Dict[str, Any]:
        """Load JSON data from file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Error loading {filepath}: {e}")
            return {}
    
    def _save_json(self, filepath: Path, data: Dict[str, Any]):
        """Save JSON data to file"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logging.error(f"Error saving {filepath}: {e}")
    
    # API Keys Management
    def get_api_keys(self) -> Dict[str, str]:
        """Get all API keys"""
        return self._load_json(self.api_keys_file)
    
    def save_api_key(self, key_name: str, key_value: str):
        """Save a single API key"""
        keys = self.get_api_keys()
        keys[key_name] = key_value
        self._save_json(self.api_keys_file, keys)
    
    def get_api_key(self, key_name: str) -> Optional[str]:
        """Get a specific API key"""
        keys = self.get_api_keys()
        return keys.get(key_name)
    
    # Settings Management
    def get_settings(self) -> Dict[str, Any]:
        """Get all settings"""
        return self._load_json(self.settings_file)
    
    def save_setting(self, setting_name: str, value: Any):
        """Save a single setting"""
        settings = self.get_settings()
        settings[setting_name] = value
        self._save_json(self.settings_file, settings)
    
    def get_setting(self, setting_name: str) -> Optional[Any]:
        """Get a specific setting"""
        settings = self.get_settings()
        return settings.get(setting_name)
    
    # Path History Management
    def get_path_history(self) -> List[str]:
        """Get recent paths"""
        data = self._load_json(self.path_history_file)
        return data.get("recent_paths", [])
    
    def add_path_to_history(self, path: str):
        """Add a path to history"""
        if not path or path == "output":
            return
            
        data = self._load_json(self.path_history_file)
        paths = data.get("recent_paths", [])
        max_paths = data.get("max_paths", 20)
        
        # Remove if already exists
        if path in paths:
            paths.remove(path)
        
        # Add to beginning
        paths.insert(0, path)
        
        # Keep only max_paths
        paths = paths[:max_paths]
        
        data["recent_paths"] = paths
        self._save_json(self.path_history_file, data)
    
    def remove_path_from_history(self, path: str):
        """Remove a path from history"""
        data = self._load_json(self.path_history_file)
        paths = data.get("recent_paths", [])
        
        if path in paths:
            paths.remove(path)
            data["recent_paths"] = paths
            self._save_json(self.path_history_file, data)
    
    def clear_all_data(self):
        """Clear all configuration data"""
        self._initialize_files()
        
# Singleton instance
config_manager = ConfigManager()
