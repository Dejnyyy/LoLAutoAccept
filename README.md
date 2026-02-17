# LoL Auto-Accept ✓

A lightweight background application that **automatically accepts League of Legends matches** when they pop up. Runs quietly in your system tray.

## How It Works

- Detects the running League client on your machine
- Polls the local [LCU API](https://developer.riotgames.com/docs/lol#league-client) every second
- When a match is found, instantly accepts it
- Shows status in the system tray with color-coded icons

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run

```bash
python main.py
```

A tray icon will appear:

- 🟡 **Yellow** — Searching for League client
- 🟢 **Green** — Connected and auto-accepting
- ⚫ **Gray** — Disabled (paused)
- 🔴 **Red** — Error

### 3. Controls

Right-click the tray icon to:

- **Enable / Disable** auto-accept
- **Quit** the application

## Build as .exe

To create a standalone executable (no Python required to run):

```bash
build.bat
```

The output will be at `dist/LoLAutoAccept.exe`.

## Requirements

- Python 3.8+
- Windows (uses Windows-specific process detection)
- League of Legends client must be running

## Notes

- The app only communicates with `127.0.0.1` (your local machine) — no data is sent anywhere
- Uses the official LCU API that the League client exposes locally
- Completely safe — it only reads process info and calls the local accept endpoint
