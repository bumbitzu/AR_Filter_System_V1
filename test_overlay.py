import cv2
import os

# Test loading the menu overlay
menu_path = os.path.join("assets", "menu_overlay.png")
menu_image = cv2.imread(menu_path, cv2.IMREAD_UNCHANGED)

if menu_image is None:
    print(f"❌ Failed to load: {menu_path}")
else:
    h, w = menu_image.shape[:2]
    channels = menu_image.shape[2] if len(menu_image.shape) > 2 else 1
    print(f"✅ Loaded: {w}x{h}px, {channels} channels")
    print(f"   Shape: {menu_image.shape}")
    print(f"   Dtype: {menu_image.dtype}")
    
    # Create a test frame
    test_frame = cv2.imread("assets/menu_overlay.png", cv2.IMREAD_COLOR)
    if test_frame is not None:
        print(f"✅ Test frame created: {test_frame.shape}")
        
        # Display the menu image itself
        cv2.imshow("Menu Image", menu_image[:, :, :3] if channels == 4 else menu_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
