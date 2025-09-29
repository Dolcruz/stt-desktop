# Änderungsprotokoll

## Version 3.0 - Dark Mode & Partikel-Audio-Feedback (2025-09-29)

### Visuelles Audio-Feedback - Komplett neu

#### Kreisförmiges Partikel-System
- **800 Partikel** in einem Ring angeordnet
- **Dynamische Animation**: Ring expandiert und schrumpft basierend auf Lautstärke
- **Smooth Transitions**: Sanfte Interpolation für flüssige Bewegungen
- **Farbverläufe**: Blaue bis Cyan-Töne, Helligkeit variiert mit Audio-Level
- **60 FPS Animation** für butterweiche Performance
- **Position**: Oben rechts am Bildschirm
- **Transparenter Hintergrund**: Nur die Partikel sind sichtbar

#### Technische Details des Partikel-Systems
- Base Radius: 80px
- Max Expansion: 40px
- Particle Size: 2px
- Smoothing Factor: 0.15 für natürliche Bewegungen
- HSV Color-System für lebendige Farben

### Dark Mode - Professionelles dunkles Design

#### Farbschema
- **Haupt-Hintergrund**: #181818 (sehr dunkel)
- **Sekundär**: #1a1a1a (dunkel)
- **Rahmen**: #3d3d3d (mittel)
- **Text**: #f0f0f0 (hell)
- **Accent Blue**: #4287f5 (modernes Blau)
- **Danger Red**: #ff6b6b (sanftes Rot)

#### UI-Komponenten
- **Buttons**: Dunkle Hintergründe mit subtilen Hover-Effekten
- **Inputs**: Dunkel mit blauen Focus-Borders
- **Lists**: Dunkler Hintergrund mit hellen Hover-States
- **Scrollbars**: Minimalistisch, dunkelgrau
- **Checkboxen**: Moderne dunkle Checkboxen mit blauem Active-State

### Keine Emojis mehr

Alle Emojis wurden aus der UI entfernt für ein professionelleres Erscheinungsbild:
- Hauptfenster: Kein Mikrofon-Emoji mehr im Header
- Buttons: Text ohne Emojis
- Settings: Sektions-Header ohne Icon-Emojis
- Info-Label: Kein Glühbirnen-Emoji

### Overlay-Position

#### Neue Positionierung
- **Oben rechts** statt zentriert
- **20px Margin** vom Bildschirmrand
- **Automatische Screen-Detection** für Multi-Monitor-Setups
- **Immer im Vordergrund** während der Aufnahme

### Bug-Fixes

1. **Deprecated Warnings behoben**:
   - Entfernt: `AA_EnableHighDpiScaling` (deprecated)
   - Entfernt: `AA_UseHighDpiPixmaps` (deprecated)
   - Ersetzt durch: `AA_ShareOpenGLContexts`
   - Keine "transform" CSS-Property mehr (nicht unterstützt in Qt)

2. **Theme-Konsistenz**:
   - Alle Dialoge nutzen jetzt konsistentes Dark Mode Styling
   - Result-Popup in Dark Mode
   - Settings-Dialog in Dark Mode

### Performance-Optimierungen

#### Partikel-Rendering
- Anti-Aliasing aktiviert für glatte Kreise
- Keine Pens (nur Brushes) für bessere Performance
- Effiziente Trigonometrie-Berechnungen
- Timer-basierte Animation statt continuous repaint

#### Smooth Level-Transitions
- Exponential Smoothing für natürliche Bewegungen
- Target/Current Level System verhindert ruckelige Übergänge
- 15% Smoothing-Faktor für optimale Balance

### Technische Änderungen

#### Neue Dateien/Klassen
- `ParticleRingWidget`: Eigenständiges Widget für Partikel-Ring
- Vollständig neugeschriebenes `RecordingOverlay`

#### Geänderte Funktionen
- `show_centered()` → `show_top_right()` in RecordingOverlay
- `apply_modern_light_theme()` → `apply_dark_theme()` komplett neu

#### API-Änderungen
- `update_level()`: Jetzt an ParticleRingWidget weitergeleitet
- Overlay-Größe: 280x320 (optimiert für Partikel-Ring)

### Bekannte Limitierungen

- Partikel-System benötigt OpenGL/Hardware-Beschleunigung für beste Performance
- Bei sehr schwachen GPUs könnte 60 FPS nicht erreicht werden
- Transparenz funktioniert nur auf Windows mit Aero/DWM

### Migration von Version 2.0

Keine Breaking Changes! Die App funktioniert wie zuvor, nur mit:
- Dark Mode statt Light Mode
- Partikel-Ring statt Progress Bar
- Position oben rechts statt zentriert

Alle Settings und Hotkeys bleiben unverändert.

---

## Version 2.0 - Modernes Design & Verbesserte Hotkeys (2025-09-29)

### Visuelles Design - Komplett überarbeitet

[... vorherige Changelog-Einträge bleiben erhalten ...]