# Speech-to-Text Desktop App (Windows)

Eine moderne, professionelle Desktop-Anwendung für Speech-to-Text mit elegantem Design, 
globalen Hotkeys und lokalen Tastenkombinationen. Verwendet Groq Whisper Large v3 für 
präzise Transkription mit Echtzeit-Aufnahme-Feedback und Auto-Copy/Paste-Funktion.

## Features

- **Modernes Dark Mode Design** - Professionelles dunkles Interface
- **Kreisförmiges Partikel-Audio-Feedback** - 800 Partikel im Ring, expandiert/schrumpft mit Lautstärke
- **Doppelte Hotkey-Unterstützung** - Globale Hotkeys (systemweit) + Lokale Shortcuts (im Fenster)
- **Datenschutz** - API-Schlüssel sicher im Windows Credential Manager gespeichert
- **Auto-Copy & Paste** - Transkription automatisch in Zwischenablage oder direkt einfügen
- **Verlauf** - Alle Transkriptionen werden lokal gespeichert
- **Overlay oben rechts** - Nicht-intrusives Feedback während der Aufnahme

## Quick Start (Windows PowerShell)

1. Create a virtual environment
```
python -m venv .venv
```
2. Activate it
```
.\.venv\Scripts\Activate.ps1
```
3. Install dependencies
```
pip install -r requirements.txt
```
4. Run the app
```
python main.py
```

## API Key

- Recommended: Set the API key via the Settings dialog in the app (stored securely via Windows Credential Manager using `keyring`).
- Alternatively, set an environment variable before running:
```
setx GROQ_API_KEY "YOUR_GROQ_API_KEY"
```
- Or via CLI once (saves to keyring):
```
python -m stt_app.cli set-key YOUR_GROQ_API_KEY
```

## Tastenkombinationen

### Globale Hotkeys (funktionieren systemweit)
- **Alt+T**: Aufnahme starten/stoppen
- **ESC**: Aktuelle Aufnahme abbrechen

### ✨ Globale Hotkeys aktivieren (empfohlen!)

**Option 1: Batch-Skript verwenden (einfachste Methode)**
```
Doppelklick auf: start_with_admin.bat
```
Das Skript startet die App automatisch mit Admin-Rechten. Die globalen Hotkeys funktionieren dann überall!

**Option 2: Manuell mit Admin-Rechten starten**
1. Rechtsklick auf PowerShell → "Als Administrator ausführen"
2. Navigiere zum Projekt:
   ```powershell
   cd "C:\Users\DEIN_BENUTZER\Speech to text"
   ```
3. Starte die App:
   ```powershell
   python main.py
   ```

**Option 3: Verknüpfung mit Admin-Rechten erstellen**
1. Rechtsklick auf Desktop → Neu → Verknüpfung
2. Ziel: `C:\Windows\System32\cmd.exe /c "cd /d C:\Users\DEIN_BENUTZER\Speech to text && python main.py"`
3. Rechtsklick auf die Verknüpfung → Eigenschaften → Erweitert
4. Haken bei "Als Administrator ausführen" ✓
5. OK → Anwenden

### Lokale Shortcuts (funktionieren wenn Fenster im Fokus ist)
Die gleichen Tastenkombinationen funktionieren auch als lokale Shortcuts, falls globale Hotkeys 
nicht verfügbar sind (z.B. ohne Admin-Rechte).

**Hinweis**: Die App zeigt dir im Status-Bereich an, ob globale Hotkeys aktiv sind oder nur 
lokale Shortcuts verfügbar sind.

## Notes
- Audio is recorded at 16 kHz, 16-bit PCM (WAV). Temporary audio files are deleted after transcription by default.
- By default, results are copied to clipboard and can be auto-pasted into the focused app.

## Packaging (PyInstaller)
```
pyinstaller --noconfirm --noconsole --name "STTDesktop" --icon .\assets\app.ico main.py
```

If `pyinstaller` is not installed:
```
pip install pyinstaller
```

## Troubleshooting

### Tastenkombinationen funktionieren nicht
- **Lösung 1**: Stelle sicher, dass das Fenster im Fokus ist. Die lokalen Shortcuts (Alt+T, ESC) 
  funktionieren immer wenn das Fenster fokussiert ist.
- **Lösung 2**: Für globale Hotkeys (systemweit), starte die App mit Administrator-Rechten:
  - Rechtsklick auf PowerShell → "Als Administrator ausführen"
  - Dann `python main.py` ausführen
- **Status prüfen**: Die App zeigt im Status-Bereich an, ob "Globale Hotkeys aktiv" sind oder 
  "Tastenkürzel funktionieren wenn Fenster im Fokus ist"

### Weitere Probleme
- **Audiogeräte nicht gefunden**: Mikrofon-Zugriff in Windows Datenschutz-Einstellungen aktivieren
- **API-Fehler**: Groq API-Schlüssel in den Einstellungen überprüfen
- **Logs**: Detaillierte Logs findest du unter `%LOCALAPPDATA%/STTDesktop/logs`
