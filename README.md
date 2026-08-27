# 🚀 Quick Start Guide - Multi-Platform AR Filter System

## 📦 Installing Dependencies

```bash
pip install -r requirements.txt
```

## ⚙️ Environment Configuration (IMPORTANT!)

The system uses `.env` files for configuration. Two environments are available:

### Test Mode (Default)

Used for testing with the local mock server.

**Automatic activation:**
The `.env` file is already configured for test mode.

**Manual activation (optional):**

```bash
# Windows
copy .env.test .env

# Linux/Mac
cp .env.test .env
```

### Production Mode

Used with real APIs. **Requires API keys!**

1. Complete `.env.production` with your real API keys
2. Activate it:

```bash
# Windows
copy .env.production .env

# Linux/Mac
cp .env.production .env
```

**🎯 Shortcut:** Run `switch_env.bat` on Windows to use the interactive menu!

📖 **Full details:** See [ENV_GUIDE.md](ENV_GUIDE.md)

---

## 🎯 Quick Start

### Step 1: Start the Mock Server

In a terminal:

```bash
python tests/mock_server.py
```

You should see:

```
============================================================
🚀 AR Filter System - Mock API Server
============================================================

📡 Available platforms:
   • Chaturbate: http://127.0.0.1:5000/events/chaturbate
   • Stripchat:  http://127.0.0.1:5000/events/stripchat
   • Camsoda:    http://127.0.0.1:5000/events/camsoda

🌐 Open http://127.0.0.1:5000 for documentation
============================================================
```

### Step 2: Run the Tests (Optional)

In a second terminal:

```bash
python tests/test_multi_platform.py
```

This script will automatically test all three platforms.

### Step 3: Start the Main Application

```bash
python main.py
```

You will be asked to select a camera. Choose the index of the camera you want to use.

### Step 4: Test the Filters

**Option A: Browser (Recommended)**

1. Open http://127.0.0.1:5000 in your browser
2. Click the test links for each platform
3. Watch the filters activate in the AR application

**Option B: Keyboard (Without Server)**
In the AR application, press:

* `1` - Activate the Sparkles filter
* `2` - Activate the Big Eyes filter
* `3` - Activate the Cyber Mask filter
* `q` - Close the application

## 🎨 Available Filters

| Tokens | Key | Filter     | Duration |
| ------ | --- | ---------- | -------- |
| 33     | 1   | Sparkles   | 10s      |
| 99     | 2   | Big Eyes   | 20s      |
| 200    | 3   | Cyber Mask | 30s      |

## 🔧 Configuration

### Enabling/Disabling Platforms

Edit `main.py`:

```python
# Enable all platforms:
CHATURBATE_URL = "http://127.0.0.1:5000/events/chaturbate"
STRIPCHAT_URL = "http://127.0.0.1:5000/events/stripchat"
CAMSODA_URL = "http://127.0.0.1:5000/events/camsoda"

# Disable Stripchat:
CHATURBATE_URL = "http://127.0.0.1:5000/events/chaturbate"
STRIPCHAT_URL = None
CAMSODA_URL = "http://127.0.0.1:5000/events/camsoda"
```

### Changing the Output Mode

```python
app = CameraFiltersAutomation(
    chaturbate_url=CHATURBATE_URL,
    stripchat_url=STRIPCHAT_URL,
    camsoda_url=CAMSODA_URL,
    output_mode="window",  # or "vcam" for a virtual camera
    quality="1080p"        # or "4K"
)
```

## 📚 Detailed Documentation

For complete information about the architecture, data normalization, and error handling, see:

* **[MULTI_PLATFORM_GUIDE.md](MULTI_PLATFORM_GUIDE.md)** - Complete guide

## 🐛 Troubleshooting

### Error: "Cannot connect to server"

* Make sure `mock_server.py` is running
* Make sure port 5000 is not blocked

### Error: "No cameras detected"

* Make sure a camera is connected
* On Windows, allow camera access in Settings

### Filters do not activate

* Check the console for errors
* Make sure the token amount is exactly 33, 99, or 200
* Make sure the listeners started successfully

### An API is not responding

The system will display:

```
⚠️ Stripchat API connection failed. Retrying in 5s...
```

The other platforms will continue to work normally.

## 📞 Project Structure

```
AR_Filter_System_V1/
├── main.py                          # Main application
├── requirements.txt                 # Python dependencies
├── MULTI_PLATFORM_GUIDE.md         # Detailed documentation
├── README_QUICK_START.md           # This file
│
├── core/
│   ├── OutputManager.py            # Video output manager
│   ├── ChaturbateListener.py       # Chaturbate listener
│   ├── StripchatListener.py        # Stripchat listener
│   └── CamsodaListener.py          # Camsoda listener
│
├── filters/
│   ├── BigEyeFilter.py             # Big Eyes filter
│   ├── FaceMask3DFilter.py         # 3D face mask filter
│   └── RainSparkleFilter.py        # Particle filter
│
└── tests/
    ├── mock_server.py              # Test server
    └── test_multi_platform.py      # Automated test script
```

## 🎉 Success!

If you have reached this point and everything is working, your AR Filter System now supports three platforms simultaneously! 🚀

For questions or troubleshooting, consult the detailed documentation in `MULTI_PLATFORM_GUIDE.md`.
