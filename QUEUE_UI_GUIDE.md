# Queue UI Server - OBS Integration Guide

## Overview
The Queue UI Server displays the current filter queue in real-time with a beautiful interface that can be embedded in OBS (Open Broadcaster Software).

## Features
- Real-time queue updates using Server-Sent Events (SSE)
- Shows current active filter
- Displays next 3 filters in queue
- Shows total queue count
- Beautiful gradient design with animations
- Transparent background for OBS integration

## Starting the Application

The UI server starts automatically when you run `main.py`:

```bash
python main.py
```

The UI will be available at: **http://127.0.0.1:8080**

## OBS Integration

### Step 1: Add Browser Source
1. Open OBS Studio
2. In your scene, click the **+** button in the Sources panel
3. Select **Browser**
4. Name it "Filter Queue" (or any name you prefer)

### Step 2: Configure Browser Source
- **URL**: `http://127.0.0.1:8080`
- **Width**: 600
- **Height**: 400
- **FPS**: 30
- ✅ Check "Shutdown source when not visible" (optional, saves resources)
- ✅ Check "Refresh browser when scene becomes active" (optional)

### Step 3: Position and Resize
- Drag the source to position it where you want on your stream
- Resize using the red handles if needed
- The background is transparent, so it will blend with your scene

## Testing

### Test with Mock Server
1. Start the mock server:
```bash
cd tests
python mock_server.py
```

2. Start the main application:
```bash
python main.py
```

3. Trigger a test tip:
```bash
# In your browser, visit:
http://127.0.0.1:5000/trigger/chaturbate/120/TestUser
```

4. Watch the queue update in real-time at http://127.0.0.1:8080

## Configuration

### Filter Duration
By default, each filter stays active for 5 seconds before moving to the next. You can adjust this in `main.py`:

```python
# In the _worker method, change this line:
threading.Timer(5.0, next_filter).start()  # Change 5.0 to desired seconds
```

### UI Server Port
If port 8080 is already in use, you can change it in `main.py`:

```python
run_ui_server(host='127.0.0.1', port=8080)  # Change port here
```

### Styling
The UI appearance can be customized in `templates/queue.html`. The CSS is inline and easy to modify:
- Colors: Look for hex codes like `#00d9ff` and `#ff00ff`
- Sizes: Adjust font-size, padding, border-radius values
- Animations: Modify the `@keyframes` sections

## API Endpoints

The UI server also provides REST API endpoints:

- **GET** `/api/queue` - Get current queue state as JSON
- **POST** `/api/next` - Manually advance to next filter
- **POST** `/api/add/<filter>/<username>/<amount>` - Add filter to queue (testing)
- **GET** `/api/stream` - Server-Sent Events stream for real-time updates

## Troubleshooting

### UI doesn't update
- Check that main.py is running
- Verify the server started at http://127.0.0.1:8080
- Check browser console for errors (F12)

### Can't access UI in OBS
- Make sure the URL is exactly `http://127.0.0.1:8080`
- Try accessing it in a regular browser first
- Restart OBS if the source shows blank

### Queue shows "No active filter"
- Ensure tips are being received (check main.py console)
- Verify the tip amounts match your configured ranges
- Check that UI_SERVER_AVAILABLE is True in console output

## Disabling the UI Server

If you don't want the UI server to run, you can disable it in the .env file or when creating the TipKeyAutomation instance:

```python
app = TipKeyAutomation(
    # ... other parameters
    enable_ui_server=False  # Disable UI server
)
```
