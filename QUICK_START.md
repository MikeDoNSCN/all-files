# 🚀 QUICK START GUIDE

## 1. Install Dependencies
```bash
pip install -r requirements.txt
```

## 2. Start the Server
```bash
python app.py
```
Or double-click: `start_server.bat`

## 3. Open Browser
Navigate to: http://localhost:5000

## 4. Use the Web Interface
1. Enter your OpenRouter API key
2. Enter project name
3. Set output directory (e.g., `C:\Users\NCPC\Documents\MYRAY FACTORY`)
4. Upload PRD files or paste content
5. Click "Estimate Tokens" to preview costs
6. Click "Generate Code"

## ✅ Fixed Issues

### Path Problem
- **Before**: `/local-context-manager/local-context-manager/`
- **After**: Single path like `C:\Users\NCPC\Documents\MYRAY FACTORY\local-context-manager`

### Backend Implementation
- Full Flask server with API endpoints
- Handles multiple file uploads
- Token estimation endpoint
- Proper error handling
- CORS enabled for browser access

### Features Working
- ✅ Multiple file upload
- ✅ Custom output directory
- ✅ Token estimation before generation
- ✅ Final token usage after generation
- ✅ Cost calculation
- ✅ Server status indicator
- ✅ Drag & drop support

## 📁 Output Structure
```
[Your chosen directory]/
└── [project_name]/
    ├── _generation_info.json    # Token usage & costs
    ├── _raw_response.json      # Full API response
    ├── README.md               # Project documentation
    ├── src/                    # Source code
    └── ...                     # Other project files
```

## 💰 Cost Information
- Input: $7.50 per 1M tokens
- Output: $30.00 per 1M tokens
- Example: 25k input + 25k output ≈ $0.94

## 🎯 Quick Test
1. Run: `run.bat`
2. Choose option 1 (Start Web Server)
3. Browser opens automatically
4. Try with `sample_prd.md` or `sample_prd_ecommerce.md`

## ⚠️ Troubleshooting
- **Server Offline**: Make sure to run `python app.py` first
- **Module not found**: Run `pip install -r requirements.txt`
- **API Error**: Check your OpenRouter API key and credits

## 📞 Support
Check server logs in the terminal for detailed error messages.