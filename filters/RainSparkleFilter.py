import cv2
import random
import math

class RainSparkleFilter:
    def __init__(self):
        # List to hold all active sparkles: [x, y, size, speed, opacity]
        self.particles = []
        self.max_particles = 50

    def apply(self, frame):
        h, w, _ = frame.shape

        # 1. Randomly spawn new sparkles at the top
        if len(self.particles) < self.max_particles:
            if random.random() > 0.8:  # Control the "downpour" rate
                # [x, y, size, speed, rotation]
                self.particles.append([
                    random.randint(0, w),  # Random horizontal start
                    -10,  # Start just above the screen
                    random.randint(5, 16),  # Random size
                    random.uniform(10, 20),  # Falling speed
                    random.uniform(0, 360)  # Initial rotation
                ])

        # 2. Update and Draw particles
        new_particles = []
        for p in self.particles:
            x, y, size, speed, angle = p

            # Update position (make them fall and sway slightly)
            y += speed
            x += math.sin(y / 20) * 2  # Gentle side-to-side sway
            angle += 5  # Rotate as they fall

            # Keep if still on screen
            if y < h:
                self._draw_star(frame, int(x), int(y), int(size), angle)
                new_particles.append([x, y, size, speed, angle])

        self.particles = new_particles
        return frame

    def _draw_star(self, img, x, y, size, angle):
        # 1. Generate Rainbow Color using Math (Sine Waves)
        # This creates a smooth transition between colors without cv2.cvtColor
        frequency = 0.1
        r = int(math.sin(frequency * (y / 5) + 0) * 127 + 128)
        g = int(math.sin(frequency * (y / 5) + 2) * 127 + 128)
        b = int(math.sin(frequency * (y / 5) + 4) * 127 + 128)
        color = (b, g, r)  # OpenCV uses BGR

        # 2. Draw the sparkle lines
        # We use thickness 2 for the main cross to make it "pop"
        for a in range(0, 360, 90):
            rad = math.radians(a + angle)
            x_end = int(x + math.cos(rad) * size)
            y_end = int(y + math.sin(rad) * size)
            cv2.line(img, (x, y), (x_end, y_end), color, 2)

        # 3. Draw the smaller diagonal cross
        for a in range(45, 405, 90):
            rad = math.radians(a + angle)
            x_end = int(x + math.cos(rad) * (size * 0.6))
            y_end = int(y + math.sin(rad) * (size * 0.6))
            cv2.line(img, (x, y), (x_end, y_end), color, 1)

        # 4. White center core
        cv2.circle(img, (x, y), 2, (255, 255, 255), -1)
