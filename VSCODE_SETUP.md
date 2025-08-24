# 🚀 VS Code Setup Guide for OSS Community Agent

This guide will help you set up and run the OSS Community Agent project in VS Code.

## 📋 Prerequisites

Before you begin, make sure you have:

- **Python 3.11+** installed on your system
- **VS Code** installed
- **Git** installed (if you cloned from a repository)

## 🔧 Quick Setup

### 1. Open Project in VS Code

```bash
cd /home/irshad/Desktop/oss-community-agent
code .
```

### 2. Install Recommended Extensions

When you first open the project, VS Code will ask to install recommended extensions. Click **"Install All"** or install them manually:

- **Python** (ms-python.python) - Essential for Python development
- **Pylance** (ms-python.vscode-pylance) - Fast Python language server
- **Black Formatter** (ms-python.black-formatter) - Code formatting
- **Flake8** (ms-python.flake8) - Linting

### 3. Set Up Python Environment

#### Option A: Create Virtual Environment
```bash
# In VS Code terminal (Ctrl+`)
python -m venv .venv
source .venv/bin/activate  # On Linux/Mac
# .venv\Scripts\activate   # On Windows
```

#### Option B: Use existing environment
If you already have a Python environment set up, make sure VS Code is using it:
- Press `Ctrl+Shift+P`
- Type "Python: Select Interpreter"
- Choose your Python 3.11+ interpreter

### 4. Install Dependencies

You can install dependencies in several ways:

#### Using VS Code Task (Recommended)
- Press `Ctrl+Shift+P`
- Type "Tasks: Run Task"
- Select "📦 Install Dependencies"

#### Using Terminal
```bash
pip install -r infra/requirements.txt
```

### 5. Set Up Environment Variables

#### Using VS Code Task
- Press `Ctrl+Shift+P`
- Type "Tasks: Run Task" 
- Select "🔧 Setup Environment"

#### Manual Setup
1) Copy the example env file at the project root:
```bash
cp .env.example .env
```
2) Edit the root `.env` with your API keys:
```env
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USERNAME=your_reddit_username
REDDIT_PASSWORD=your_reddit_password
OPENAI_API_KEY=your_openai_api_key
LLM_PROVIDER=none   # optional for local demo without LLM
```

All components (UI, agent, tools) read from the single root `.env` now. Remove any old per-app .env files.

## 🚀 Running the Project

### Method 1: Using Debug/Run Configuration (Recommended)

1. Press `F5` or go to **Run and Debug** panel (Ctrl+Shift+D)
2. Select **"🤖 Run OSS Community Agent UI"** from the dropdown
3. Click the green play button or press `F5`

The Streamlit app will start and automatically open in your browser at `http://localhost:8501`

### Method 2: Using VS Code Tasks

1. Press `Ctrl+Shift+P`
2. Type "Tasks: Run Task"
3. Select **"🚀 Start UI Server"**

### Method 3: Using Terminal

```bash
python run_ui.py  # Uses the root .env automatically
```

### Method 4: Direct Streamlit Command

```bash
streamlit run apps/ui/streamlit_app.py
```

## 🎯 Available Run Configurations

In the **Run and Debug** panel, you have several options:

- **🤖 Run OSS Community Agent UI** - Start the full web interface
- **🚀 Run Streamlit App Directly** - Start just the Streamlit app
- **🔧 Debug Backend Agent** - Debug the Portia agent backend
- **🧪 Test RAG Tool** - Test the RAG system independently

## 📝 Useful VS Code Features

### Keyboard Shortcuts
- `F5` - Start debugging/run the app
- `Ctrl+Shift+D` - Open Run and Debug panel
- `Ctrl+Shift+P` - Command Palette
- `Ctrl+`` - Toggle integrated terminal
- `Ctrl+Shift+G` - Source Control (Git)

### Tasks Available
- **🚀 Start UI Server** - Launch the application
- **📦 Install Dependencies** - Install all required packages
- **🔧 Setup Environment** - Copy .env.example to .env
- **🧹 Clean Cache** - Remove Python cache files
- **🧪 Test RAG System** - Test the RAG functionality

### VS Code Terminal Tips

The integrated terminal will automatically:
- Activate your virtual environment
- Set the correct PYTHONPATH
- Use the project root as working directory

## 🔍 Debugging

### Frontend (Streamlit)
1. Set breakpoints in your Python files
2. Use the **"🤖 Run OSS Community Agent UI"** configuration
3. The debugger will stop at breakpoints in your Streamlit code

### Backend Agent
1. Use the **"🔧 Debug Backend Agent"** configuration
2. Set breakpoints in `apps/agent/main.py` or other backend files

### Common Debugging Tips
- Use `st.write()` or `st.json()` for quick debugging in Streamlit
- Check the VS Code Debug Console for error messages
- Use the integrated terminal to run individual components

## 🎨 Code Formatting and Linting

The project is configured to use:
- **Black** for code formatting (runs on save)
- **Flake8** for linting
- **Import sorting** (isort)

To format code manually:
- Right-click in editor → "Format Document"
- Or press `Shift+Alt+F`

## 🐛 Troubleshooting

### Common Issues

#### 1. "Module not found" errors
```bash
# Make sure PYTHONPATH is set correctly
export PYTHONPATH="${PWD}:${PWD}/apps/ui"
```

#### 2. VS Code not finding Python interpreter
- Press `Ctrl+Shift+P`
- Type "Python: Select Interpreter"
- Choose the correct Python executable

#### 3. Dependencies not installed
```bash
pip install -r infra/requirements.txt
```

#### 4. Environment variables not loaded
- Make sure a `.env` file exists at the project root
- Check that all required variables are set

#### 5. Port already in use
- Kill any existing Streamlit processes: `pkill -f streamlit`
- Or change the port in launch.json

### Performance Tips

1. **Exclude unnecessary files** - The `.vscode/settings.json` already excludes `__pycache__`, etc.
2. **Use virtual environment** - Keeps dependencies isolated
3. **Close unused tabs** - Better performance in large projects

## 🔧 Advanced Configuration

### Custom Python Path
Edit `.vscode/settings.json`:
```json
{
    "python.defaultInterpreterPath": "/path/to/your/python"
}
```

### Custom Streamlit Port
Edit `.vscode/launch.json` and change the `--server.port` argument.

### Additional Environment Variables
Add to `.vscode/settings.json`:
```json
{
    "terminal.integrated.env.linux": {
        "CUSTOM_VAR": "value"
    }
}
```

## 📱 VS Code Extensions for Web Development

For enhanced development experience, consider these additional extensions:

- **Thunder Client** - API testing
- **GitLens** - Enhanced Git capabilities  
- **Todo Tree** - Track TODO comments
- **Bracket Pair Colorizer** - Visual bracket matching
- **Auto Rename Tag** - Automatically rename paired tags

## 🚀 Quick Start Checklist

- [ ] Open project in VS Code
- [ ] Install recommended extensions
- [ ] Set up Python environment
- [ ] Install dependencies (`pip install -r infra/requirements.txt`)
- [ ] Copy `.env.example` to `.env` and configure
- [ ] Press `F5` to run the application
- [ ] Open browser to `http://localhost:8501`

## 📞 Getting Help

If you encounter issues:

1. Check the **Problems** panel (Ctrl+Shift+M) for errors
2. Look at the **Terminal** output for detailed error messages
3. Check the **Debug Console** when debugging
4. Review the project's main README.md
5. Open an issue on the project repository

---

🎉 **You're all set!** The OSS Community Agent should now be running in VS Code with a beautiful web interface for managing your AI-powered Reddit support bot.
