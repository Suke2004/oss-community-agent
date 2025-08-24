# 🔧 Environment Files Guide

## 📁 Environment File Structure

Your OSS Community Agent project now uses a **single consolidated environment file**:

### **Unified Configuration**
```
📄 .env.example          # Configuration template
📄 .env                  # Your actual configuration
```

## 🎯 **How It Works**

The system uses **one centralized configuration file**:

1. **Root `.env`** - Contains ALL settings for both frontend and backend
2. Auto-creates from **`.env.example`** if it doesn't exist
3. All components (UI, agent, tools) load from this single file

## 🚀 **Setup Instructions**

### **Quick Setup**
```bash
cd /home/irshad/Desktop/oss-community-agent
cp .env.example .env
nano .env  # Edit with your API keys
```

### **Required Configuration**

Edit your `.env` file with these essential settings:

```bash
# Reddit API (required for backend)
REDDIT_CLIENT_ID=your_actual_client_id
REDDIT_CLIENT_SECRET=your_actual_client_secret  
REDDIT_USERNAME=your_reddit_username
REDDIT_PASSWORD=your_reddit_password

# OpenAI API (required for AI responses)
OPENAI_API_KEY=your_actual_openai_api_key
```

### **Getting API Keys**

1. **Reddit API Keys:**
   - Go to https://www.reddit.com/prefs/apps/
   - Click "Create Application"
   - Choose "script" type
   - Copy Client ID and Secret

2. **OpenAI API Key:**
   - Go to https://platform.openai.com/api-keys
   - Click "Create new secret key"
   - Copy the key (starts with `sk-`)

## 🛠️ **Current Configuration Status**

You now have a clean, single configuration setup:
- ✅ `.env.example` - Configuration template
- ✅ `.env` - Your active configuration (ready to edit)

## 🎮 **Running the Project**

After setting up your `.env` file:

```bash
# Run the complete system
./start.sh

# Or run individual components
python3 run_ui.py              # Frontend only
python3 apps/agent/main.py     # Backend only
```

## 🔄 **Simplified Structure**

- ✅ **Single configuration file** - No more confusion about multiple .env files
- ✅ **Centralized settings** - All components use the same configuration
- ✅ **Easier management** - Edit one file for all settings
- ✅ **Clean project structure** - No duplicate environment files

---

💡 **Result:** One `.env` file to rule them all! 🎯
