import cv2
import numpy as np
import os

def overlay_image_alpha(img, overlay, pos):
    """Test the alpha blending function"""
    if overlay is None:
        return
    
    x, y = pos
    h, w = overlay.shape[:2]
    
    # Boundary check
    if x < 0 or y < 0 or x + w > img.shape[1] or y + h > img.shape[0]:
        print(f"⚠️ Overlay out of bounds! Position: ({x}, {y}), Size: {w}x{h}, Frame: {img.shape[1]}x{img.shape[0]}")
        return
    
    # Extract ROI
    roi = img[y:y+h, x:x+w]
    
    # Check if overlay has alpha channel
    if len(overlay.shape) == 3 and overlay.shape[2] == 4:
        print("✅ Overlay has 4 channels (BGRA)")
        
        # Get alpha channel stats
        alpha_channel = overlay[:, :, 3]
        print(f"   Alpha min: {alpha_channel.min()}, max: {alpha_channel.max()}, mean: {alpha_channel.mean():.2f}")
        
        # BGRA image with alpha channel
        overlay_bgr = overlay[:, :, :3].astype(float)
        alpha_mask = overlay[:, :, 3].astype(float) / 255.0
        
        # Expand alpha mask to 3 channels
        alpha_3ch = cv2.merge([alpha_mask, alpha_mask, alpha_mask])
        
        # Blend
        blended = (overlay_bgr * alpha_3ch + roi.astype(float) * (1.0 - alpha_3ch)).astype('uint8')
        
        # Place result back
        img[y:y+h, x:x+w] = blended
        print("✅ Alpha blending completed")
    else:
        print(f"⚠️ Overlay has {overlay.shape[2] if len(overlay.shape) > 2 else 1} channels (expected 4)")
        img[y:y+h, x:x+w] = overlay

# Test 1: Load the menu overlay
print("=" * 60)
print("TEST 1: Loading Menu Overlay")
print("=" * 60)

menu_path = os.path.join("assets", "menu_overlay.png")
menu_image = cv2.imread(menu_path, cv2.IMREAD_UNCHANGED)

if menu_image is None:
    print(f"❌ FAILED to load: {menu_path}")
    print(f"   Current directory: {os.getcwd()}")
    print(f"   File exists: {os.path.exists(menu_path)}")
    exit(1)

h, w = menu_image.shape[:2]
channels = menu_image.shape[2] if len(menu_image.shape) > 2 else 1
print(f"✅ Loaded: {w}x{h}px, {channels} channels")
print(f"   Shape: {menu_image.shape}")
print(f"   Dtype: {menu_image.dtype}")

# Test 2: Check alpha channel
print("\n" + "=" * 60)
print("TEST 2: Analyzing Alpha Channel")
print("=" * 60)

if channels == 4:
    alpha = menu_image[:, :, 3]
    print(f"   Alpha channel stats:")
    print(f"   - Min: {alpha.min()}")
    print(f"   - Max: {alpha.max()}")
    print(f"   - Mean: {alpha.mean():.2f}")
    print(f"   - Non-zero pixels: {np.count_nonzero(alpha)}/{alpha.size} ({100*np.count_nonzero(alpha)/alpha.size:.1f}%)")
    
    # Show alpha channel visualization
    alpha_visual = cv2.merge([alpha, alpha, alpha])
    cv2.imshow("Alpha Channel (white = opaque)", alpha_visual)
else:
    print("   ⚠️ No alpha channel found!")

# Test 3: Create test frame and overlay
print("\n" + "=" * 60)
print("TEST 3: Testing Overlay on Sample Frame")
print("=" * 60)

# Create a colorful test frame (1920x1080)
test_frame = np.zeros((1080, 1920, 3), dtype=np.uint8)
# Add gradient background
for i in range(1080):
    test_frame[i, :] = [i * 255 // 1080, 128, 255 - i * 255 // 1080]

print(f"   Created test frame: {test_frame.shape}")

# Apply overlay at position (20, 20)
test_frame_copy = test_frame.copy()
overlay_image_alpha(test_frame_copy, menu_image, (20, 20))

# Test 4: Show results
print("\n" + "=" * 60)
print("TEST 4: Visual Comparison")
print("=" * 60)
print("   Press any key to cycle through images...")
print("   Press 'q' to quit")

# Resize for display
display_width = 1280
display_height = 720

while True:
    # Show original frame
    frame1 = cv2.resize(test_frame, (display_width, display_height))
    cv2.imshow("1. Original Frame (no overlay)", frame1)
    key = cv2.waitKey(0) & 0xFF
    if key == ord('q'):
        break
    
    # Show frame with overlay
    frame2 = cv2.resize(test_frame_copy, (display_width, display_height))
    cv2.imshow("2. Frame WITH Menu Overlay", frame2)
    key = cv2.waitKey(0) & 0xFF
    if key == ord('q'):
        break
    
    # Show just the menu (BGR only)
    if channels == 4:
        menu_bgr = menu_image[:, :, :3]
        cv2.imshow("3. Menu Image (BGR only)", menu_bgr)
        key = cv2.waitKey(0) & 0xFF
        if key == ord('q'):
            break
    
    break

cv2.destroyAllWindows()

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
print("If you saw the menu overlay in image 2, the code is working!")
print("If not, there may be an issue with the PNG file's alpha channel.")
