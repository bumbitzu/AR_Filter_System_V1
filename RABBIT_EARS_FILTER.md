# 🐰 Rabbit Ears Filter - Documentație

## Prezentare Generală

**RabbitEarsFilter** este un filtru AR distractiv care adaugă automat urechi de iepure animate deasupra capului utilizatorului detectat în fluxul video.

---

## 🎯 Caracteristici

- ✅ **Detecție Automată**: Folosește MediaPipe Face Mesh pentru detecție precisă
- ✅ **Scalare Dinamică**: Urechile se ajustează automat în funcție de distanța de cameră
- ✅ **Transparență Perfectă**: Suprapunere cu canal alpha (fără fundal)
- ✅ **Multi-Face Support**: Funcționează cu mai multe fețe simultan
- ✅ **Performance Optimizat**: Processing rapid pentru real-time usage

---

## 📋 Specificații Tehnice

### Detecție și Poziționare

**MediaPipe Landmarks folosite:**
- **Landmark 10**: Top of forehead (vârful frunții) - punct de ancorare principal
- **Landmark 234**: Left temple (templu stâng) - pentru calculare dimensiune
- **Landmark 454**: Right temple (templu drept) - pentru calculare dimensiune

**Algoritm de poziționare:**
```
1. Detectează poziția vârfului frunții (landmark 10)
2. Calculează distanța între temple (234 ↔ 454)
3. Scalează imaginea cu urechi la ~1.8x lățimea feței
4. Poziționează urechile la 35% din înălțimea lor deasupra capului
```

### Scalare Dinamică

Formula scalării:
```python
temple_distance = abs(right_temple_x - left_temple_x)
scale_factor = (temple_distance * 1.8) / original_ears_width
```

**Comportament:**
- Față aproape (200px entre temple) → Urechi mari
- Față departe (120px entre temple) → Urechi mici
- Minimum: 10x10 pixeli (previne artefacte)

---

## 🎨 Asset-ul Grafic

**Fișier**: `assets/rabbit_ears.png`

**Specificații:**
- Format: PNG cu canal alpha (4 canale: BGRA)
- Dimensiune recomandată: 512x512 pixeli sau mai mare
- Transparență: Complet transparentă în afara urechilor
- Design: Urechi de iepure albe cu interior roz

**Cum să înlocuiești imaginea:**
1. Salvează noua imagine ca PNG cu transparență
2. Denumește-o `rabbit_ears.png`
3. Plasează în folder-ul `assets/`
4. Restartează aplicația

---

## 💻 Utilizare în Cod

### Import și Inițializare

```python
from filters.RabbitEarsFilter import RabbitEarsFilter

# Creare instanță
rabbit_filter = RabbitEarsFilter()

# Aplicare pe frame
processed_frame = rabbit_filter.apply(original_frame)
```

### Integrare în Sistem de Tips

În `main.py`, filtrul este configurat astfel:

```python
self.fixed_tips = {
    33:  ('Sparkles', RainSparkleFilter(), 10),
    50:  ('Rabbit Ears', RabbitEarsFilter(), 15),  # ← 50 tokens, 15 secunde
    99:  ('Big Eyes', BigEyeFilter(), 20),
    200: ('Cyber Mask', FaceMask3D(), 30)
}
```

**Activare:**
- Trigger: 50 tokens tip
- Durată: 15 secunde
- Nume afișat: "Rabbit Ears"

---

## 🧪 Testare

### Opțiune 1: Mock Server (Recomandat)

1. **Pornește mock server:**
   ```bash
   python tests/mock_server.py
   ```

2. **Deschide browser:**
   ```
   http://127.0.0.1:5000
   ```

3. **Click pe link:**
   - Chaturbate: "50 tokens (Rabbit Ears 🐰)"
   - Stripchat: "50 tokens (Rabbit Ears 🐰)"
   - Camsoda: "50 tokens (Rabbit Ears 🐰)"

### Opțiune 2: Keyboard Shortcut (Direct în Aplicație)

Pentru a testa rapid, poți modifica main.py să adauge:

```python
elif key == ord('4'):
    self.process_tip(50)  # Test Rabbit Ears
```

### Opțiune 3: API Direct

```bash
# Chaturbate
curl http://127.0.0.1:5000/trigger/chaturbate/50/TestUser

# Stripchat
curl http://127.0.0.1:5000/trigger/stripchat/50/TestUser

# Camsoda
curl http://127.0.0.1:5000/trigger/camsoda/50/TestUser
```

---

## 🔧 Parametri Ajustabili

Dacă vrei să modifici comportamentul filtrului, editează `filters/RabbitEarsFilter.py`:

### 1. **Dimensiunea Urechilor**

```python
# Linia ~104 în _calculate_scale_factor()
scale_factor = (temple_distance * 1.8) / self.rabbit_ears_img.shape[1]
#                                 ^^^
# Mărește acest factor pentru urechi mai mari
# Micșorează pentru urechi mai mici
# Valori sugerate: 1.5 - 2.5
```

### 2. **Poziția Verticală**

```python
# Linia ~133 în _get_ears_position()
offset_y = int(scaled_height * 0.35)
#                               ^^^^
# Mărește pentru urechi mai jos
# Micșorează pentru urechi mai sus
# Valori sugerate: 0.2 - 0.5
```

### 3. **Confidence Thresholds**

```python
# Linia ~18 în __init__()
self.face_mesh = self.mp_face_mesh.FaceMesh(
    refine_landmarks=True,
    min_detection_confidence=0.5,  # Sensitivity la detecție
    min_tracking_confidence=0.5    # Sensitivity la tracking
)
# Valori sugerate: 0.3 - 0.7
```

---

## 🐛 Troubleshooting

### Problema: Urechile nu apar

**Cauze posibile:**
1. **Asset lipsă:**
   ```
   FileNotFoundError: Nu am putut încărca rabbit_ears.png
   ```
   **Soluție:** Verifică că `assets/rabbit_ears.png` există

2. **Nicio față detectată:**
   - Asigură-te că fața e vizibilă în cadru
   - Verifică iluminarea (evită backlight)
   - Mută camera mai aproape

3. **Filtrul nu e în listă:**
   - Verifică că import-ul e în `main.py`
   - Verifică că tier-ul 50 e în `self.fixed_tips`

### Problema: Urechile sunt prea mari/mici

**Soluție:** Ajustează factorul de scalare (vezi parametri mai sus)

### Problema: Urechile "sare" sau "tremură"

**Cauze posibile:**
- Tracking instabil
- Mișcare rapidă a capului

**Soluție:**
- Crește `min_tracking_confidence` la 0.6-0.7
- Implementează smoothing (media ultimelor N poziții)

### Problema: Performance scăzut

**Optimizări:**
1. Reduce rezoluția imaginii asset
2. Limitează FPS-ul la 30
3. Verifică că GPU acceleration e activat pentru MediaPipe

---

## 📊 Performance Metrics

**Overhead estimat:**
- Face detection: ~5-10ms
- Image scaling: ~1-2ms
- Alpha blending: ~2-3ms
- **Total: ~8-15ms per frame**

**FPS Impact:**
- @ 60 FPS: ~5-10% drop
- @ 30 FPS: Neglijabil

---

## 🎨 Customizare Avansată

### Creare Asset Personalizat

Vrei alte asset-uri (coarne, coroniță, etc.)?

1. **Creează imaginea în Photoshop/GIMP:**
   - Canvas: 512x512 sau mai mare
   - Format: PNG-24 cu alpha channel
   - Fundal: Complet transparent
   - Conținut: Centrat

2. **Exportă cu transparență:**
   ```
   File → Export As → PNG
   ✓ 32-bit depth (8 bits/channel + alpha)
   ```

3. **Salvează în assets/:**
   ```
   assets/your_custom_asset.png
   ```

4. **Modifică în `RabbitEarsFilter.py`:**
   ```python
   asset_path = os.path.join(project_root, 'assets', 'your_custom_asset.png')
   ```

### Creare Filtru Derivat

Pentru a crea un alt filtru bazat pe RabbitEars:

```python
from filters.RabbitEarsFilter import RabbitEarsFilter

class CrownFilter(RabbitEarsFilter):
    def _load_rabbit_ears(self):
        # Suprascriem să încărcăm alt asset
        asset_path = os.path.join(self.project_root, 'assets', 'crown.png')
        self.rabbit_ears_img = cv2.imread(asset_path, cv2.IMREAD_UNCHANGED)
    
    def _get_ears_position(self, face_landmarks, w, h, sw, sh):
        # Poziționare diferită (ex: mai sus pe cap)
        x, y = super()._get_ears_position(face_landmarks, w, h, sw, sh)
        return x, y - 30  # 30px mai sus
```

---

## 📚 Resurse Externe

- **MediaPipe Face Mesh**: https://google.github.io/mediapipe/solutions/face_mesh
- **OpenCV Alpha Blending**: https://docs.opencv.org/master/d0/d86/tutorial_py_image_arithmetics.html
- **PNG Transparency**: https://www.w3.org/TR/PNG/#11Transparency

---

## 📝 Changelog

### v1.0 (2026-01-28)
- ✅ Implementare inițială
- ✅ Detecție MediaPipe Face Mesh
- ✅ Scalare dinamică
- ✅ Alpha blending cu transparență
- ✅ Multi-face support
- ✅ Asset rabbit_ears.png generat

---

**Creat**: 2026-01-28  
**Autor**: Senior Python Developer  
**Versiune**: 1.0  
**Status**: Production Ready 🚀
