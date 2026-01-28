"""
Test script pentru RabbitEarsFilter
Testează încărcarea asset-ului și funcționalitatea de bază
"""
import cv2
import sys
import os

# Adaugă path-ul proiectului
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from filters.RabbitEarsFilter import RabbitEarsFilter


def test_filter_initialization():
    """Testează inițializarea filtrului"""
    print("=" * 60)
    print("TEST 1: Inițializare RabbitEarsFilter")
    print("=" * 60)
    
    try:
        filter_instance = RabbitEarsFilter()
        print("✅ Filtrul s-a inițializat cu succes")
        
        # Verifică dacă asset-ul a fost încărcat
        if filter_instance.rabbit_ears_img is not None:
            h, w, c = filter_instance.rabbit_ears_img.shape
            print(f"✅ Asset încărcat: {w}x{h} pixeli, {c} canale")
            
            if c == 4:
                print("✅ Canal alpha detectat")
            else:
                print(f"⚠️  WARNING: Imaginea are doar {c} canale (ar trebui 4)")
        else:
            print("❌ Asset-ul NU a fost încărcat")
            return False
            
    except FileNotFoundError as e:
        print(f"❌ EROARE: {e}")
        print("\n💡 Soluție: Rulează mai întâi scriptul pentru a genera asset-ul")
        return False
    except Exception as e:
        print(f"❌ EROARE neașteptată: {e}")
        return False
    
    print()
    return True


def test_face_detection():
    """Testează detecția feței cu camera"""
    print("=" * 60)
    print("TEST 2: Detecție față și aplicare filtru")
    print("=" * 60)
    print("\n📷 Pornesc camera...")
    print("Instrucțiuni:")
    print("  - Privește în cameră pentru a testa detecția")
    print("  - Apasă 'q' pentru a închide")
    print("  - Apasă 's' pentru a salva un screenshot")
    print()
    
    try:
        # Inițializare filtru
        rabbit_filter = RabbitEarsFilter()
        
        # Pornește camera
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        if not cap.isOpened():
            print("❌ Nu am putut accesa camera")
            return False
        
        print("✅ Camera pornită")
        print("\nTesting filtru in live mode...")
        
        cv2.namedWindow("Rabbit Ears Filter Test", cv2.WINDOW_NORMAL)
        
        frame_count = 0
        faces_detected = False
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame = cv2.flip(frame, 1)  # Mirror effect
            
            # Aplică filtrul
            filtered_frame = rabbit_filter.apply(frame)
            
            # Adaugă informații pe frame
            cv2.putText(filtered_frame, "Rabbit Ears Filter Test", (20, 40),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            cv2.putText(filtered_frame, "Press 'q' to quit | 's' to screenshot", (20, 680),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
            
            # Verifică dacă s-a detectat vreo față
            if filtered_frame is not frame:  # Frame-ul s-a modificat
                if not faces_detected:
                    print("✅ Față detectată! Urechile ar trebui să fie  vizibile.")
                    faces_detected = True
            
            cv2.imshow("Rabbit Ears Filter Test", filtered_frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                filename = f"rabbit_ears_test_{frame_count}.jpg"
                cv2.imwrite(filename, filtered_frame)
                print(f"📸 Screenshot salvat: {filename}")
            
            frame_count += 1
        
        cap.release()
        cv2.destroyAllWindows()
        
        if faces_detected:
            print("\n✅ Test reușit! Filtrul funcționează corect.")
        else:
            print("\n⚠️  Nu s-a detectat nicio față în timpul testului")
            print("   Verifică iluminarea și poziția camerei")
        
        return True
        
    except Exception as e:
        print(f"❌ EROARE în timpul testului: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_asset_display():
    """Afișează asset-ul pentru verificare vizuală"""
    print("=" * 60)
    print("TEST 3: Verificare vizuală asset")
    print("=" * 60)
    
    try:
        rabbit_filter = RabbitEarsFilter()
        
        # Creează un canvas pentru afișare
        canvas = cv2.cvtColor(
            (cv2.imread("assets/rabbit_ears.png", cv2.IMREAD_UNCHANGED)[:,:,:3]),
            cv2.COLOR_BGR2RGB
        ) if os.path.exists("assets/rabbit_ears.png") else None
        
        if canvas is not None:
            print("✅ Asset găsit")
            print(f"   Dimensiune: {canvas.shape[1]}x{canvas.shape[0]}")
            print("\n📊 Afișez asset-ul (apasă orice tastă pentru a închide)...")
            
            cv2.imshow("Rabbit Ears Asset", canvas)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            return True
        else:
            print("❌ Nu am putut încărca asset-ul pentru afișare")
            return False
            
    except Exception as e:
        print(f"❌ EROARE: {e}")
        return False


def main():
    """Rulează toate testele"""
    print("\n" + "🐰" * 30)
    print(" " * 10 + "RABBIT EARS FILTER - TEST SUITE")
    print("🐰" * 30 + "\n")
    
    tests_passed = 0
    total_tests = 3
    
    # Test 1: Inițializare
    if test_filter_initialization():
        tests_passed += 1
    
    # Test 2: Asset vizual
    if test_asset_display():
        tests_passed += 1
    
    # Test 3: Live camera
    if test_face_detection():
        tests_passed += 1
    
    # Rezultate finale
    print("\n" + "=" * 60)
    print(f"REZULTATE FINALE: {tests_passed}/{total_tests} teste reușite")
    print("=" * 60)
    
    if tests_passed == total_tests:
        print("\n🎉 SUCCESS! Toate testele au trecut!")
        print("Filtrul Rabbit Ears este gata de utilizare.")
        return 0
    else:
        print(f"\n⚠️  {total_tests - tests_passed} test(e) au eșuat")
        print("Verifică erorile de mai sus.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
