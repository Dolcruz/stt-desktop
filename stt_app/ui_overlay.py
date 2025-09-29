from __future__ import annotations

import math
import random
from PySide6 import QtCore, QtGui, QtWidgets


class Particle3D:
    """Represents a single particle in 3D space."""
    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z
        self.size_variation = random.uniform(0.7, 1.3)


def create_sphere_particles(count: int) -> list[Particle3D]:
    """Create particles uniformly distributed on a sphere surface using Fibonacci sphere algorithm."""
    particles = []
    phi = math.pi * (3.0 - math.sqrt(5.0))  # Golden angle in radians
    
    for i in range(count):
        y = 1 - (i / float(count - 1)) * 2  # y goes from 1 to -1
        radius = math.sqrt(1 - y * y)  # radius at y
        
        theta = phi * i  # golden angle increment
        
        x = math.cos(theta) * radius
        z = math.sin(theta) * radius
        
        particles.append(Particle3D(x, y, z))
    
    return particles


def rotate_y(particle: Particle3D, angle: float) -> tuple[float, float, float]:
    """Rotate a particle around the Y axis (horizontal rotation)."""
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    
    x = particle.x * cos_a + particle.z * sin_a
    y = particle.y
    z = -particle.x * sin_a + particle.z * cos_a
    
    return x, y, z


class Particle3DWidget(QtWidgets.QWidget):
    """Widget that displays a 3D sphere of particles that expand/contract with audio level."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._level = 0.0
        self._particle_count = 600  # Reduced from 800 for better performance
        self._base_particle_size = 2.25  # 25% smaller (was 3.0)
        self._glow_intensity = 1.0  # Configurable glow strength (0.0 to 2.0)
        self._color_hue = 200  # Blue by default (0-360)
        
        # Create 3D sphere particles
        self._particles = create_sphere_particles(self._particle_count)
        
        # Animation state
        self._animation_timer = QtCore.QTimer(self)
        self._animation_timer.timeout.connect(self._animate)
        self._animation_timer.start(16)  # ~60 FPS
        
        self._target_level = 0.0
        self._current_level = 0.0
        self._smoothing = 0.25
        
        # Rotation angle for horizontal spin
        self._rotation_angle = 0.0
        self._rotation_speed = 0.3  # Degrees per frame (slow rotation)
        
        self.setMinimumSize(400, 400)
        
    def set_level(self, level: float) -> None:
        """Set the audio level (0.0 to 1.0) with amplification."""
        amplified = level * 8.0  # 8x amplification for sensitivity
        self._target_level = max(0.0, min(1.0, amplified))
    
    def set_particle_count(self, count: int) -> None:
        """Update particle count and regenerate particles."""
        self._particle_count = count
        self._particles = create_sphere_particles(self._particle_count)
        
    def set_glow_intensity(self, intensity: float) -> None:
        """Set glow intensity (0.0 to 2.0)."""
        self._glow_intensity = intensity
        
    def set_color_hue(self, hue: int) -> None:
        """Set color hue (0-360)."""
        self._color_hue = max(0, min(359, hue))  # Clamp to valid HSV hue range
        
    def _animate(self) -> None:
        """Update animation state."""
        # Smooth level interpolation
        self._current_level += (self._target_level - self._current_level) * self._smoothing
        
        # Update rotation angle (passive horizontal rotation)
        self._rotation_angle += self._rotation_speed
        if self._rotation_angle >= 360:
            self._rotation_angle -= 360
            
        self.update()
        
    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        """Render the 3D particle sphere with neon glow effect."""
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        # Enable composition mode for glow effect
        painter.setCompositionMode(QtGui.QPainter.CompositionMode_Plus)
        
        # Center and scale
        center_x = self.width() / 2
        center_y = self.height() / 2
        base_radius = min(self.width(), self.height()) / 2 - 30
        
        # Calculate expansion based on audio level
        # Quiet: 0.5x scale, Loud: 1.5x scale
        min_scale = 0.5
        max_scale = 1.5
        current_scale = min_scale + (max_scale - min_scale) * self._current_level
        
        # Convert rotation angle to radians
        rotation_rad = math.radians(self._rotation_angle)
        
        # Prepare particle data for rendering
        render_data = []
        
        for particle in self._particles:
            # Apply horizontal rotation
            x, y, z = rotate_y(particle, rotation_rad)
            
            # Apply expansion scale
            x *= current_scale
            y *= current_scale
            z *= current_scale
            
            # Project 3D to 2D (simple orthographic projection)
            # x, y are used directly, z is used for depth
            screen_x = center_x + x * base_radius
            screen_y = center_y - y * base_radius  # Flip Y for screen coordinates
            
            # Calculate depth factor (z ranges from -1 to 1)
            # Particles closer to camera (positive z) are larger and brighter
            # Normalize z to 0-1 range for easier use
            depth_factor = (z + 1.0) / 2.0  # 0 = far, 1 = near
            
            render_data.append({
                'x': screen_x,
                'y': screen_y,
                'z': z,
                'depth_factor': depth_factor,
                'size_variation': particle.size_variation
            })
        
        # Sort particles by z-depth (back to front) for proper rendering
        render_data.sort(key=lambda p: p['z'])
        
        # Draw particles
        for data in render_data:
            depth_factor = data['depth_factor']
            
            # Size: larger when closer to camera
            size_scale = 0.4 + 0.6 * depth_factor
            particle_size = self._base_particle_size * data['size_variation'] * size_scale
            
            # Brightness: brighter when closer, dimmer when far
            # Also brighter with higher audio level
            base_brightness = 0.3 + 0.7 * depth_factor
            audio_brightness = 0.7 + 0.3 * self._current_level
            brightness = base_brightness * audio_brightness
            
            # Dynamic color based on hue setting
            # Ensure values are within valid range
            color = QtGui.QColor.fromHsv(
                max(0, min(359, self._color_hue)),  # Hue: 0-359
                200,  # Saturation: 0-255
                max(0, min(255, int(255 * brightness)))  # Value: 0-255
            )
            
            # Draw STRONG neon glow effect (multiple layers)
            
            # Layer 1: Large outer glow (strongest, most visible)
            outer_glow_size = particle_size * 12.0 * self._glow_intensity
            outer_gradient = QtGui.QRadialGradient(
                QtCore.QPointF(data['x'], data['y']),
                outer_glow_size / 2
            )
            # Dynamic color glow (with validation to prevent HSV warnings)
            glow_color = QtGui.QColor.fromHsv(max(0, min(359, self._color_hue)), 180, 255)
            outer_gradient.setColorAt(0, QtGui.QColor(glow_color.red(), glow_color.green(), glow_color.blue(), int(120 * brightness * self._glow_intensity)))
            outer_gradient.setColorAt(0.3, QtGui.QColor(glow_color.red(), glow_color.green(), glow_color.blue(), int(80 * brightness * self._glow_intensity)))
            outer_gradient.setColorAt(0.6, QtGui.QColor(glow_color.red(), glow_color.green(), glow_color.blue(), int(40 * brightness * self._glow_intensity)))
            outer_gradient.setColorAt(1, QtGui.QColor(0, 0, 0, 0))
            
            painter.setBrush(outer_gradient)
            painter.setPen(QtCore.Qt.NoPen)
            painter.drawEllipse(
                QtCore.QPointF(data['x'], data['y']),
                outer_glow_size / 2,
                outer_glow_size / 2
            )
            
            # Layer 2: Medium glow (intense)
            mid_glow_size = particle_size * 6.0 * self._glow_intensity
            mid_gradient = QtGui.QRadialGradient(
                QtCore.QPointF(data['x'], data['y']),
                mid_glow_size / 2
            )
            mid_color = QtGui.QColor.fromHsv(max(0, min(359, self._color_hue)), 200, 255)
            mid_gradient.setColorAt(0, QtGui.QColor(mid_color.red(), mid_color.green(), mid_color.blue(), int(180 * brightness * self._glow_intensity)))
            mid_gradient.setColorAt(0.5, QtGui.QColor(mid_color.red(), mid_color.green(), mid_color.blue(), int(120 * brightness * self._glow_intensity)))
            mid_gradient.setColorAt(1, QtGui.QColor(0, 0, 0, 0))
            
            painter.setBrush(mid_gradient)
            painter.drawEllipse(
                QtCore.QPointF(data['x'], data['y']),
                mid_glow_size / 2,
                mid_glow_size / 2
            )
            
            # Layer 3: Inner bright glow
            inner_glow_size = particle_size * 3.0 * self._glow_intensity
            inner_gradient = QtGui.QRadialGradient(
                QtCore.QPointF(data['x'], data['y']),
                inner_glow_size / 2
            )
            inner_color = QtGui.QColor.fromHsv(max(0, min(359, self._color_hue)), 150, 255)
            inner_gradient.setColorAt(0, QtGui.QColor(inner_color.red(), inner_color.green(), inner_color.blue(), int(255 * brightness * self._glow_intensity)))
            inner_gradient.setColorAt(0.7, QtGui.QColor(inner_color.red(), inner_color.green(), inner_color.blue(), int(180 * brightness * self._glow_intensity)))
            inner_gradient.setColorAt(1, QtGui.QColor(0, 0, 0, 0))
            
            painter.setBrush(inner_gradient)
            painter.drawEllipse(
                QtCore.QPointF(data['x'], data['y']),
                inner_glow_size / 2,
                inner_glow_size / 2
            )
            
            # Draw particle core (bright center)
            painter.fillRect(
                QtCore.QRectF(
                    data['x'] - particle_size/2,
                    data['y'] - particle_size/2,
                    particle_size,
                    particle_size
                ),
                color
            )


class RecordingOverlay(QtWidgets.QWidget):
    """Frameless, always-on-top overlay showing recording status with 3D particle sphere.
    
    Displays a rotating 3D sphere of particles that expand/contract based on audio level,
    positioned at the top-right of the screen.
    """

    cancel_requested = QtCore.Signal()

    def __init__(self) -> None:
        super().__init__()
        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint
            | QtCore.Qt.WindowStaysOnTopHint
            | QtCore.Qt.Tool
        )
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)

        self._elapsed = 0.0
        self._level = 0.0

        # Main container
        container = QtWidgets.QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: rgba(18, 18, 18, 250);
                border-radius: 20px;
                border: 2px solid rgba(80, 80, 80, 180);
            }
        """)
        
        # Drop shadow
        shadow = QtWidgets.QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(40)
        shadow.setOffset(0, 8)
        shadow.setColor(QtGui.QColor(0, 0, 0, 150))
        container.setGraphicsEffect(shadow)

        # Create 3D particle widget
        self._particle_sphere = Particle3DWidget()
        self._particle_sphere.setMinimumSize(360, 360)
        
        # Recording label
        rec_label = QtWidgets.QLabel("AUFNAHME")
        rec_label.setAlignment(QtCore.Qt.AlignCenter)
        rec_label.setStyleSheet("""
            color: #ff4444; 
            font-size: 11pt; 
            font-weight: 700;
            letter-spacing: 2px;
            background: transparent;
        """)
        
        # Timer label
        self._timer_label = QtWidgets.QLabel("00:00")
        self._timer_label.setAlignment(QtCore.Qt.AlignCenter)
        self._timer_label.setStyleSheet("""
            color: #ffffff; 
            font-size: 28pt; 
            font-weight: 700;
            background: transparent;
            letter-spacing: 2px;
        """)

        # Cancel button
        cancel_btn = QtWidgets.QPushButton("Abbrechen")
        cancel_btn.setFixedSize(120, 38)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(100, 50, 50, 200);
                border: 1.5px solid rgba(150, 70, 70, 255);
                border-radius: 19px;
                color: #ff6b6b;
                font-size: 10pt;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: rgba(120, 60, 60, 255);
                border-color: rgba(180, 90, 90, 255);
            }
        """)
        cancel_btn.clicked.connect(self.cancel_requested.emit)

        # Container layout
        container_layout = QtWidgets.QVBoxLayout(container)
        container_layout.setContentsMargins(20, 20, 20, 24)  # Extra bottom margin
        container_layout.setSpacing(12)
        container_layout.addWidget(rec_label, alignment=QtCore.Qt.AlignCenter)
        container_layout.addWidget(self._particle_sphere, alignment=QtCore.Qt.AlignCenter)
        container_layout.addWidget(self._timer_label, alignment=QtCore.Qt.AlignCenter)
        container_layout.addWidget(cancel_btn, alignment=QtCore.Qt.AlignCenter)

        # Main layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(container)

        self.setFixedSize(420, 540)  # Increased height to prevent button cutoff

    @QtCore.Slot(float)
    def update_level(self, level: float) -> None:
        """Update the audio level for particle animation."""
        self._level = level
        self._particle_sphere.set_level(level)

    @QtCore.Slot(float)
    def update_time(self, seconds: float) -> None:
        """Update the elapsed time display."""
        self._elapsed = seconds
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        self._timer_label.setText(f"{mins:02d}:{secs:02d}")

    def show_top_right(self) -> None:
        """Show the overlay at the top-right of the screen."""
        screen = QtWidgets.QApplication.primaryScreen()
        if not screen:
            self.show()
            return
        
        geo = screen.availableGeometry()
        margin = 20
        x = geo.x() + geo.width() - self.width() - margin
        y = geo.y() + margin
        
        self.move(x, y)
        self.show()
        self.raise_()
        self.activateWindow()