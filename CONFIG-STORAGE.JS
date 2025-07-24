// CONFIG-STORAGE.JS - File-based storage management
// Replaces localStorage with server-side file storage

class ConfigStorage {
    constructor() {
        this.apiBase = window.location.origin;
    }

    // API Keys Management
    async getApiKeys() {
        try {
            const response = await fetch(`${this.apiBase}/api/config/keys`);
            if (response.ok) {
                return await response.json();
            }
            return { openrouter_api_key: '', moonshot_api_key: '' };
        } catch (error) {
            console.error('Error fetching API keys:', error);
            return { openrouter_api_key: '', moonshot_api_key: '' };
        }
    }

    async saveApiKey(keyName, keyValue) {
        try {
            const data = {};
            data[keyName] = keyValue;
            const response = await fetch(`${this.apiBase}/api/config/keys`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            return response.ok;
        } catch (error) {
            console.error('Error saving API key:', error);
            return false;
        }
    }

    // Settings Management
    async getSettings() {
        try {
            const response = await fetch(`${this.apiBase}/api/config/settings`);
            if (response.ok) {
                return await response.json();
            }
            return {};
        } catch (error) {
            console.error('Error fetching settings:', error);
            return {};
        }
    }

    async saveSetting(settingName, value) {
        try {
            const data = {};
            data[settingName] = value;
            const response = await fetch(`${this.apiBase}/api/config/settings`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            return response.ok;
        } catch (error) {
            console.error('Error saving setting:', error);
            return false;
        }
    }

    // Path History Management
    async getPathHistory() {
        try {
            const response = await fetch(`${this.apiBase}/api/config/paths`);
            if (response.ok) {
                const data = await response.json();
                return data.paths || [];
            }
            return [];
        } catch (error) {
            console.error('Error fetching path history:', error);
            return [];
        }
    }

    async addPath(path) {
        try {
            const response = await fetch(`${this.apiBase}/api/config/paths`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ path })
            });
            return response.ok;
        } catch (error) {
            console.error('Error adding path:', error);
            return false;
        }
    }

    async removePath(path) {
        try {
            const response = await fetch(`${this.apiBase}/api/config/paths/remove`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ path })
            });
            return response.ok;
        } catch (error) {
            console.error('Error removing path:', error);
            return false;
        }
    }

    // Clear all data (optional, not used in UI)
    async clearAll() {
        try {
            const response = await fetch(`${this.apiBase}/api/config/clear`, {
                method: 'POST'
            });
            return response.ok;
        } catch (error) {
            console.error('Error clearing config:', error);
            return false;
        }
    }
}

// Create global instance
window.configStorage = new ConfigStorage();
