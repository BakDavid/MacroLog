# 🖱️ MacroLog

**MacroLog** is a simple Python-based keylogger that logs all keystrokes and saves them to a file. It is designed for educational or monitoring purposes in controlled environments.

## 📦 Features

-   Captures all keystrokes
-   Saves to a log file with timestamped entries
-   Runs silently in the background
-   Can be compiled into a standalone executable

## ⚠️ Disclaimer

> This tool is intended for **educational purposes only**. Do not use it to monitor devices without explicit permission. Unauthorized use of keyloggers may violate privacy laws and terms of service.

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/BakDavid/MacroLog.git
cd MacroLog
```

### 2. Create and activate a virtual environment (optional but recommended)

```bash
python -m venv venv
source venv/bin/activate      # On macOS/Linux
venv\Scripts\activate         # On Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

If you're building the executable:

```bash
pip install -r requirements-dev.txt
```

## 🛠 Usage

### Run the script directly

```bash
python main.py
```

This will start the application, where we can start listening for keyboard input and create a log file (e.g., log.json) with all keystrokes.

## 🏗️ Build an Executable

To create a standalone `.exe` file using PyInstaller:

```bash
pyinstaller --onefile --name MacroLog main.py
```

This will create the following:

-   `dist/MacroLog.exe` → your standalone executable

-   `build/` → temporary files used during build

-   `main.spec` → build configuration file (optional to commit)

## 📁 Project Structure

```bash
MacroLog/
│
├── main.py                # The main script
├── requirements.txt       # Runtime dependencies
├── requirements-dev.txt   # Dev tools like PyInstaller
├── .gitignore             # Files/folders to exclude from git
└── README.md              # This file
```

## ✅ .gitignore

Recommended entries:

```bash
__pycache__/
build/
dist/
*.spec
*.log
```

## 📃 License

MIT License or your preferred one.

## 💬 Acknowledgments

Built with PyInstaller (https://pyinstaller.org/)

Uses pynput (https://pypi.org/project/pynput/) for keyboard listening
