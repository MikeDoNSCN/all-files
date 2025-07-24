# PRD Generator - Multi-Model AI Code Generation

Convert Product Requirements Documents (PRD) into complete, production-ready codebases using either **Gemini 2.5 Pro** or **Kimi K2** AI models.

## 🚀 What's New in v1.1.0

- **Multi-Model Support**: Choose between Gemini 2.0 Flash and Kimi K2
- **Model Selection UI**: Easy switching between models with persistent preferences
- **Direct API Integration**: Kimi K2 via Moonshot AI's direct API
- **Optimized Token Management**: Model-specific limits and pricing

## ✨ Features

- **Dual AI Model Support**:
  - **Gemini 2.5 Pro** (Google via OpenRouter) - 2M token context
  - **Kimi K2** (Moonshot AI Direct) - 128K token context, best for complex coding
- Generate complete project structures with all code files
- Automatic project naming from PRD content
- Support for multiple input files
- Real-time token estimation and cost calculation
- Production-ready code with tests and documentation
- Persistent settings (API keys, model preference, paths)

## 📊 Model Comparison

| Feature | Gemini 2.5 Pro | Kimi K2 |
|---------|------------------|---------|
| **Provider** | OpenRouter | Moonshot AI (Direct) |
| **Max Context** | 2M tokens | 128K tokens |
| **Parameters** | Not disclosed | 1T total / 32B active |
| **Input Price** | $0.075/1M tokens | $0.15/1M tokens |
| **Output Price** | $0.30/1M tokens | $2.50/1M tokens |
| **Best For** | General code generation | Complex coding & agents |
| **Speed** | Very Fast | Fast |

## 🛠️ Setup

### 1. Install Requirements
```bash
pip install flask flask-cors requests
pip install tiktoken  # Optional, for better token estimation
```

### 2. Get API Keys

#### For Gemini (via OpenRouter):
1. Sign up at https://openrouter.ai
2. Get your API key from https://openrouter.ai/keys
3. Add credits to your account

#### For Kimi K2 (via Moonshot AI):
1. Sign up at https://platform.moonshot.ai
2. Generate an API key in your dashboard
3. Add credits to your account

### 3. Run the Application
```bash
python app.py
```
Open http://localhost:5000 in your browser

## 📱 Usage

### Web Interface (Recommended)

1. **Select Your Model**: Choose between Gemini and Kimi K2 based on your needs
2. **Enter API Key**: Your key is saved locally for convenience
3. **Input PRD**: Upload files or paste content directly
4. **Set Output Directory**: Choose where to save generated code
5. **Review Token Estimate**: See estimated costs before generation
6. **Generate**: Click to create your complete project

### Features by Model

#### Use Gemini 2.5 Pro when you need:
- Maximum context (up to 2M tokens)
- Lower cost per token
- General purpose code generation
- Very fast response times

#### Use Kimi K2 when you need:
- Superior coding accuracy (65.8% on SWE-bench)
- Complex architectural decisions
- Advanced reasoning for system design
- Agentic capabilities (tool use, autonomous problem-solving)

## 📁 Output Structure

Generated projects include:
```
your_project_name/
├── src/               # Source code
├── tests/             # Unit tests
├── docs/              # Documentation
├── README.md          # Project documentation
├── package.json       # Dependencies (if applicable)
├── requirements.txt   # Python dependencies (if applicable)
├── Dockerfile         # Container configuration (if applicable)
├── .env.example       # Environment variables template
└── _generation_info.json  # Generation metadata
```

## 💡 Tips for Best Results

### PRD Best Practices:
1. **Be Specific**: Include technical requirements, frameworks, and libraries
2. **Define Structure**: Outline desired file organization
3. **Specify Features**: List all functionality clearly
4. **Include Examples**: Provide sample inputs/outputs
5. **Set Constraints**: Mention performance or security requirements

### Model Selection Guide:
- **Quick prototypes**: Use Gemini (faster, cheaper)
- **Production systems**: Use Kimi K2 (more accurate, better architecture)
- **Large PRDs (>100K tokens)**: Use Gemini (2M context)
- **Complex logic**: Use Kimi K2 (superior reasoning)

## 🔧 Advanced Configuration

### Environment Variables
```bash
# Optional: Set default API keys
export OPENROUTER_API_KEY=sk-or-...
export MOONSHOT_API_KEY=sk-...
```

### Custom Token Limits
Adjust max tokens in the UI based on your needs:
- Gemini: Up to 900,000 tokens recommended
- Kimi K2: Up to 100,000 tokens recommended

## 🐛 Troubleshooting

### Common Issues:

1. **"Server Offline" Error**
   - Ensure Flask server is running: `python app.py`
   - Check firewall settings for port 5000

2. **API Key Errors**
   - Verify key format (OpenRouter: `sk-or-...`)
   - Check available credits in your account
   - Ensure correct key for selected model

3. **Token Limit Exceeded**
   - Split large PRDs into smaller sections
   - Reduce max output tokens
   - Use model with larger context (Gemini)

4. **Generation Failures**
   - Check `debug_response_*.json` files
   - Verify PRD format and clarity
   - Try with a simpler PRD first

## 📈 Cost Optimization

### Minimize Costs:
1. **Use Token Estimation**: Always check before generating
2. **Optimize PRDs**: Remove unnecessary content
3. **Choose Wisely**: Gemini for drafts, Kimi for final
4. **Set Limits**: Use reasonable max token values

### Example Costs (10K tokens in, 50K out):
- **Gemini**: $0.75 + $15.00 = $15.75
- **Kimi K2**: $1.50 + $125.00 = $126.50

## 🔐 Security

- API keys are stored locally in browser localStorage
- Never commit API keys to version control
- Keys are only sent to official API endpoints
- No data is stored on our servers

## 🚦 System Requirements

- Python 3.7+
- Modern web browser
- Internet connection
- At least 1GB free disk space

## 📝 Version History

- **v1.1.0** (2025-01-18): Added Kimi K2 support, model selection UI
- **v1.0.0** (2025-01-11): Initial release with Gemini 2.5 Pro

## 🤝 Contributing

Feel free to submit issues or pull requests. See `doc/CONTRIBUTING.md` for guidelines.

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- Google Gemini team for the powerful AI model
- Moonshot AI for Kimi K2 and excellent API
- OpenRouter for unified API access
- Flask community for the web framework

---

**Need Help?** Check the `doc/` folder for detailed documentation or open an issue on GitHub.