import cv2
import numpy as np
import os

# Load the menu overlay
menu_path = os.path.join("assets", "menu_overlay.png")
print(f"Loading: {menu_path}")
print(f"File exists: {os.path.exists(menu_path)}")

menu_image = cv2.imread(menu_path, cv2.IMREAD_UNCHANGED)

if menu_image is None:
    print(f"❌ FAILED to load!")
    exit(1)

h, w = menu_image.shape[:2]
channels = menu_image.shape[2] if len(menu_image.shape) > 2 else 1

print(f"\n✅ Menu overlay loaded successfully!")
print(f"   Size: {w}x{h} pixels")
print(f"   Channels: {channels}")
print(f"   Data type: {menu_image.dtype}")

if channels == 4:
    alpha = menu_image[:, :, 3]
    print(f"\n📊 Alpha Channel Analysis:")
    print(f"   Min value: {alpha.min()}")
    print(f"   Max value: {alpha.max()}")
    print(f"   Mean value: {alpha.mean():.2f}")
    opaque_pixels = np.sum(alpha > 200)
    semi_pixels = np.sum((alpha > 10) & (alpha <= 200))
    transparent_pixels = np.sum(alpha <= 10)
    total = alpha.size
    print(f"   Opaque pixels (>200): {opaque_pixels:,} ({100*opaque_pixels/total:.1f}%)")
    print(f"   Semi-transparent: {semi_pixels:,} ({100*semi_pixels/total:.1f}%)")
    print(f"   Fully transparent: {transparent_pixels:,} ({100*transparent_pixels/total:.1f}%)")
    
    # Show the BGR content
    bgr = menu_image[:, :, :3]
    print(f"\n🎨 BGR Channels Analysis:")
    print(f"   B channel - min: {bgr[:,:,0].min()}, max: {bgr[:,:,0].max()}")
    print(f"   G channel - min: {bgr[:,:,1].min()}, max: {bgr[:,:,1].max()}")
    print(f"   R channel - min: {bgr[:,:,2].min()}, max: {bgr[:,:,2].max()}")
    
    # Check if there's actual color content where alpha > 0
    mask = alpha > 10
    if np.any(mask):
        visible_bgr = bgr[mask]
        print(f"\n   In visible areas (alpha > 10):")
        print(f"   B: {visible_bgr[:,0].min()}-{visible_bgr[:,0].max()}")
        print(f"   G: {visible_bgr[:,1].min()}-{visible_bgr[:,1].max()}")
        print(f"   R: {visible_bgr[:,2].min()}-{visible_bgr[:,2].max()}")

print(f"\n" + "="*50)
print("Creating test visualization...")

# Create a simple test: black frame with white rectangle where overlay should go
test_frame = np.zeros((1080, 1920, 3), dtype=np.uint8)

# Draw a white rectangle where the menu will be placed
overlay_x, overlay_y = 20, 20
cv2.rectangle(test_frame, (overlay_x, overlay_y), (overlay_x + w, overlay_y + h), (255, 255, 255), 2)
cv2.putText(test_frame, "Menu should appear here", (overlay_x, overlay_y - 10), 
            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

print(f"\nTest frame size: {test_frame.shape[1]}x{test_frame.shape[0]}")
print(f"Menu position: ({overlay_x}, {overlay_y})")
print(f"Menu will occupy: ({overlay_x}, {overlay_y}) to ({overlay_x + w}, {overlay_y + h})")

# Check if it fits
if overlay_x + w > 1920 or overlay_y + h > 1080:
    print(f"\n⚠️ WARNING: Menu is TOO LARGE to fit at position ({overlay_x}, {overlay_y})!")
    print(f"   Menu would need: ({overlay_x + w}, {overlay_y + h})")
    print(f"   Frame size is: (1920, 1080)")
else:
    print(f"\n✅ Menu fits within frame bounds")

# Resize for display
display = cv2.resize(test_frame, (1280, 720))
cv2.imshow("Test - White box shows where menu should appear", display)
print("\nPress any key to close...")
cv2.waitKey(0)
cv2.destroyAllWindows()
