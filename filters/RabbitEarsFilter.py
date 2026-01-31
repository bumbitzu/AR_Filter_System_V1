import cv2
import mediapipe as mp
import numpy as np
import os
import math

from core.FaceMeshFactory import create_face_mesh


class RabbitEarsFilter:
    """
    Filtru AR care adaugă urechi de iepure deasupra capului utilizatorului.
    Folosește MediaPipe Face Mesh pentru detecție și poziționare precisă.
    """
    
    def __init__(self):
        """
        Inițializează detectorul Face Mesh și încarcă imaginea cu urechi de iepure.
        """
        self.face_mesh = create_face_mesh(
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        
        # Landmarks key points pentru poziționare
        # Vârful capului / partea superioară a frunții
        self.forehead_top = 10  # Top of forehead
        self.left_temple = 234   # Left temple
        self.right_temple = 454  # Right temple
        
        # Additional landmarks for better rotation calculation
        self.left_eye_outer = 33   # Left eye outer corner
        self.right_eye_outer = 362  # Right eye outer corner
        self.nose_tip = 1          # Nose tip
        self.chin = 175            # Chin center
        
        # Încarcă imaginea cu urechi de iepure
        self.rabbit_ears_img = None
        self._load_rabbit_ears()
        
    def _load_rabbit_ears(self):
        """
        Încarcă imaginea cu urechi de iepure din assets folder.
        Imaginea trebuie să aibă canal alpha (transparență).
        """
        # Determină calea relativă la assets folder
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        asset_path = os.path.join(project_root, 'assets', 'rabbit_ears.png')
        
        # Încarcă imaginea cu canal alpha (UNCHANGED flag păstrează transparența)
        self.rabbit_ears_img = cv2.imread(asset_path, cv2.IMREAD_UNCHANGED)
        
        if self.rabbit_ears_img is None:
            raise FileNotFoundError(
                f"Nu am putut încărca imaginea de urechi de iepure din: {asset_path}\n"
                f"Asigură-te că fișierul 'rabbit_ears.png' există în folder-ul 'assets'."
            )
        
        # Verifică dacă imaginea are canal alpha
        if self.rabbit_ears_img.shape[2] != 4:
            raise ValueError(
                f"Imaginea rabbit_ears.png trebuie să aibă canal alpha (4 canale).\n"
                f"Imaginea curentă are doar {self.rabbit_ears_img.shape[2]} canale."
            )
    
    def _calculate_scale_factor(self, face_landmarks, frame_width, frame_height):
        """
        Calculează factorul de scalare bazat pe distanța dintre temple.
        Cu cât fața e mai aproape, cu atât urechile vor fi mai mari.
        
        Args:
            face_landmarks: Landmarks-urile feței din MediaPipe
            frame_width: Lățimea frame-ului
            frame_height: Înălțimea frame-ului
            
        Returns:
            float: Factorul de scalare pentru imagine
        """
        # Obține pozițiile temple-urilor
        left_temple_lm = face_landmarks.landmark[self.left_temple]
        right_temple_lm = face_landmarks.landmark[self.right_temple]
        
        # Calculează distanța în pixeli
        left_x = left_temple_lm.x * frame_width
        right_x = right_temple_lm.x * frame_width
        temple_distance = abs(right_x - left_x)
        
        # Scalare bazată pe distanță (ajustează acest factor pentru dimensiune potrivită)
        # De obicei, distanța între temple este ~120-200 pixeli
        # Vrem ca urechile să fie ~1.5x lățimea feței
        scale_factor = (temple_distance * 1.8) / self.rabbit_ears_img.shape[1]
        
        return scale_factor
    
    def _get_ears_position(self, face_landmarks, frame_width, frame_height, scaled_width, scaled_height):
        """
        Calculează poziția unde trebuie plasate urechile (centrul imaginii).
        
        Args:
            face_landmarks: Landmarks-urile feței
            frame_width: Lățimea frame-ului
            frame_height: Înălțimea frame-ului
            scaled_width: Lățimea imaginii scalate
            scaled_height: Înălțimea imaginii scalate
            
        Returns:
            tuple: (x, y) poziția centrului urechilor
        """
        # Obține punctul din vârful capului
        forehead_lm = face_landmarks.landmark[self.forehead_top]
        
        # Calculează poziția în pixeli
        head_x = int(forehead_lm.x * frame_width)
        head_y = int(forehead_lm.y * frame_height)
        
        # Offset pentru a poziționa urechile deasupra capului
        # Ajustează acest offset în funcție de unde vrei să apară urechile
        offset_y = int(scaled_height * 0.35)  # Urechile încep la ~35% din înălțimea lor deasupra capului
        
        # Poziția finală (centrul imaginii cu urechi)
        ears_center_x = head_x
        ears_center_y = head_y - offset_y
        
        return ears_center_x, ears_center_y
    
    def _overlay_image_alpha(self, frame, overlay_img, x, y):
        """
        Suprapune o imagine cu canal alpha peste frame.
        Gestionează corect transparența.
        
        Args:
            frame: Frame-ul original (BGR)
            overlay_img: Imaginea de suprapus (BGRA)
            x: Coordonata x a centrului imaginii
            y: Coordonata y a centrului imaginii
            
        Returns:
            np.array: Frame-ul cu imaginea suprapusă
        """
        overlay_height, overlay_width = overlay_img.shape[:2]
        frame_height, frame_width = frame.shape[:2]
        
        # Calculează colțul stânga-sus al imaginii overlay
        x1 = x - overlay_width // 2
        y1 = y - overlay_height // 2
        x2 = x1 + overlay_width
        y2 = y1 + overlay_height
        
        # Verifică dacă imaginea iese din bounds
        # Dacă da, ajustează sau skip
        if x1 >= frame_width or y1 >= frame_height or x2 <= 0 or y2 <= 0:
            return frame  # Imaginea e complet în afara frame-ului
        
        # Calculează zona de overlap
        # Region în overlay image
        overlay_x1 = max(0, -x1)
        overlay_y1 = max(0, -y1)
        overlay_x2 = overlay_width - max(0, x2 - frame_width)
        overlay_y2 = overlay_height - max(0, y2 - frame_height)
        
        # Region în frame
        frame_x1 = max(0, x1)
        frame_y1 = max(0, y1)
        frame_x2 = min(frame_width, x2)
        frame_y2 = min(frame_height, y2)
        
        # Extrage regiunea de interes din overlay
        overlay_roi = overlay_img[overlay_y1:overlay_y2, overlay_x1:overlay_x2]
        
        if overlay_roi.size == 0:
            return frame  # Nu există overlap
        
        # Separă canalele BGR și Alpha
        overlay_bgr = overlay_roi[:, :, :3]
        overlay_alpha = overlay_roi[:, :, 3:4] / 255.0  # Normalizează la [0, 1]
        
        # Extrage regiunea din frame
        frame_roi = frame[frame_y1:frame_y2, frame_x1:frame_x2]
        
        # Blend folosind alpha channel
        blended = (overlay_bgr * overlay_alpha + frame_roi * (1 - overlay_alpha)).astype(np.uint8)
        
        # Pune înapoi în frame
        frame[frame_y1:frame_y2, frame_x1:frame_x2] = blended
        
        return frame
    
    def _calculate_rotation_angle(self, face_landmarks):
        """
        Calculate the rotation angle of the head based on multiple landmarks for better accuracy.

        Args:
            face_landmarks: Landmarks of the face from MediaPipe.

        Returns:
            float: Adjusted rotation angle in degrees.
        """
        # Get eye corner landmarks (more stable than temples)
        left_eye = face_landmarks.landmark[self.left_eye_outer]
        right_eye = face_landmarks.landmark[self.right_eye_outer]
        
        # Calculate the slope of the line connecting the eye corners
        delta_y = right_eye.y - left_eye.y
        delta_x = right_eye.x - left_eye.x
        
        # Calculate the angle in radians and convert to degrees
        angle = np.arctan2(delta_y, delta_x) * (180.0 / np.pi)
        
        # Apply much more subtle scaling for natural look
        scaling_factor = 0.3  # Much smaller factor for subtle rotation
        return -angle * scaling_factor  # Negative sign to match head rotation direction

    def _rotate_image(self, image, angle):
        """
        Rotate an image around its center.

        Args:
            image: The image to rotate.
            angle: The angle in degrees to rotate the image.

        Returns:
            np.array: The rotated image.
        """
        h, w = image.shape[:2]
        center = (w // 2, h // 2)

        # Get the rotation matrix
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)

        # Perform the rotation
        rotated_image = cv2.warpAffine(image, rotation_matrix, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
        return rotated_image

    def apply(self, frame):
        """
        Aplică filtrul de urechi de iepure pe frame.
        
        Args:
            frame: Frame-ul video curent (BGR format)
            
        Returns:
            np.array: Frame-ul cu urechile de iepure aplicate
        """
        # Verifică dacă imaginea a fost încărcată cu succes
        if self.rabbit_ears_img is None:
            return frame
        
        h, w = frame.shape[:2]
        
        # Convertește la RGB pentru MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Procesează frame-ul cu Face Mesh
        results = self.face_mesh.process(rgb_frame)
        
        # Dacă nu s-a detectat nicio față, returnează frame-ul original
        if not results.multi_face_landmarks:
            return frame
        
        # Creăm o copie a frame-ului pentru a nu modifica originalul direct
        output_frame = frame.copy()
        
        # Procesează fiecare față detectată
        for face_landmarks in results.multi_face_landmarks:
            # Calculează factorul de scalare bazat pe dimensiunea feței
            scale_factor = self._calculate_scale_factor(face_landmarks, w, h)
            
            # Scalează imaginea cu urechi
            new_width = int(self.rabbit_ears_img.shape[1] * scale_factor)
            new_height = int(self.rabbit_ears_img.shape[0] * scale_factor)
            
            # Evită scalare la dimensiuni prea mici
            if new_width < 10 or new_height < 10:
                continue
            
            scaled_ears = cv2.resize(
                self.rabbit_ears_img,
                (new_width, new_height),
                interpolation=cv2.INTER_AREA
            )

            # Calculează unghiul de rotație al capului
            rotation_angle = self._calculate_rotation_angle(face_landmarks)

            # Rotatează imaginea cu urechi
            rotated_ears = self._rotate_image(scaled_ears, rotation_angle)

            # Get the position where the ears should be placed
            ears_x, ears_y = self._get_ears_position(
                face_landmarks, w, h, new_width, new_height
            )

            # Overlay the rotated ears image
            output_frame = self._overlay_image_alpha(
                output_frame, rotated_ears, ears_x, ears_y
            )
        
        return output_frame
