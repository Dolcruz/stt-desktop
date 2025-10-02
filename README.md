# 🎙️ STTDesktop - Speech-to-Text Desktop App

Professionelle Speech-to-Text Anwendung mit modernster KI-Unterstützung, 3D-Visualisierung und Dialog-Modus.

[![Latest Release](https://img.shields.io/github/v/release/Dolcruz/stt-desktop?label=Download)](https://github.com/Dolcruz/stt-desktop/releases/latest)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## ⚡ **Quick Start für Endbenutzer**

### **📥 Download & Installation**

1. **Lade die neueste Version herunter:**
   
   👉 **[STTDesktop.exe herunterladen](https://github.com/Dolcruz/stt-desktop/releases/latest/download/STTDesktop.exe)**

2. **Starte die Datei** (Doppelklick auf `STTDesktop.exe`)

3. **Fertig!** 🎉

> **Windows Defender Warnung?** Das ist normal für neue .exe-Dateien!
> - Klicke auf "Weitere Informationen"
> - Dann auf "Trotzdem ausführen"

---

## ✨ **Features**

### 🎯 **Kern-Funktionen**
- ✅ **Speech-to-Text** mit Whisper (Groq API)
- ✅ **Grammatik-Korrektur** mit KI
- ✅ **Übersetzung** in 6+ Sprachen
- ✅ **Dialog-Modus** mit kostenloser Sprachausgabe (Microsoft Edge TTS)
- ✅ **Globale Hotkeys** (Alt+T zum Starten/Stoppen)
- ✅ **Automatische Updates** (ein Klick!)

### 🎨 **UI & UX**
- 🌑 **Modernes Dark Theme**
- 🔮 **3D-Partikel-Visualisierung** mit Live-Audio-Feedback
- 📜 **Verlauf** mit Volltext-Ansicht
- 🎛️ **Anpassbare Visualisierung** (Partikel, Farbe, Glow)
- ⌨️ **Tastenkombinationen** für alle Funktionen

### 🌍 **Dialog-Modus**
- 🗣️ **Zwei-Wege-Übersetzung** in Echtzeit
- 🔊 **Kostenlose Sprachausgabe** (kein API-Key nötig!)
- 📝 **Gesprächsverlauf** mit Original & Übersetzung
- 🔄 **Automatischer Sprecher-Wechsel**
- 🎙️ **6 Sprachen**: Deutsch, Englisch, Spanisch, Französisch, Italienisch, Arabisch

---

## 🚀 **Erste Schritte**

### **1. API Key einrichten**

Du benötigst einen **kostenlosen Groq API Key** für Transkription:

1. Gehe zu https://console.groq.com/keys
2. Erstelle einen kostenlosen Account
3. Kopiere deinen API Key
4. Öffne STTDesktop
5. Klicke auf **⚙ Einstellungen**
6. Füge den API Key ein
7. **Fertig!** 🎉

### **2. Erste Aufnahme**

1. Drücke **Alt+T** oder klicke **"Aufnahme starten"**
2. Sprich etwas ein
3. Drücke **Alt+T** erneut oder klicke **"Aufnahme beenden"**
4. Warte auf die Transkription
5. **Fertig!** Der Text wird automatisch kopiert

### **3. Dialog-Modus nutzen**

1. Klicke **🗣️ Dialog-Modus**
2. Wähle zwei Sprachen aus
3. Klicke **🎙️ Aufnahme starten**
4. Sprich in Sprache A
5. Höre die Übersetzung in Sprache B
6. **Sprecher wechselt automatisch!**

---

## 🎨 **Screenshots**

### Hauptfenster mit Visualisierung
![Main Window](https://via.placeholder.com/800x500?text=Hauptfenster+mit+3D+Visualisierung)

### Dialog-Modus
![Dialog Mode](https://via.placeholder.com/800x500?text=Dialog-Modus+mit+Echtzeit-Übersetzung)

### Einstellungen
![Settings](https://via.placeholder.com/800x500?text=Einstellungen+%26+Anpassung)

---

## ⚙️ **Einstellungen & Anpassung**

### **Hotkeys**
- **Alt+T**: Aufnahme starten/stoppen
- **Esc**: Aufnahme abbrechen

### **Visualisierung anpassen**
1. Klicke **⚙ Visualisierung**
2. Passe an:
   - Partikel-Anzahl (200-1000)
   - Glow-Intensität (0.1-2.0)
   - Farbe (Hue 0-359)
3. **Live-Vorschau** mit echtem Mikrofon!

### **Grammatik-Korrektur**
- **Automatisch**: Korrigiert jeden Text sofort
- **Manuell**: Button nach Transkription

---

## 🔄 **Updates**

Die App **prüft automatisch** auf Updates beim Start!

### **Was passiert?**
1. App startet
2. Prüft GitHub nach neuer Version (im Hintergrund)
3. Wenn verfügbar: **Update-Dialog** erscheint
4. Ein Klick auf **"Jetzt updaten"**
5. Download mit Fortschrittsbalken
6. Automatische Installation & Neustart
7. **Fertig!** ✨

### **Manuelle Installation:**
Falls Auto-Update nicht funktioniert:
👉 https://github.com/Dolcruz/stt-desktop/releases/latest

---

## 🛠️ **Für Entwickler**

### **Voraussetzungen**
- Python 3.10+
- Windows 10/11 (für globale Hotkeys)

### **Installation (Development)**

```bash
# Repository klonen
git clone https://github.com/Dolcruz/stt-desktop.git
cd stt-desktop

# Virtual Environment erstellen
python -m venv .venv
.venv\Scripts\Activate.ps1

# Dependencies installieren
pip install -r requirements.txt

# App starten
python main.py
```

### **.exe bauen**

```powershell
# Einfach:
.\build_release.ps1

# Oder manuell:
pip install pyinstaller
pyinstaller --clean STTDesktop.spec
```

Die fertige `.exe` ist in `dist\STTDesktop.exe`

### **Release erstellen**

Siehe **[RELEASE_GUIDE.md](RELEASE_GUIDE.md)** für eine komplette Anleitung!

Kurz:
1. Build .exe
2. VERSION erhöhen
3. GitHub Release erstellen mit Tag `v1.0.1`
4. `.exe` hochladen
5. **Fertig!** Alle User bekommen Auto-Update

---

## 📦 **Technische Details**

### **Stack**
- **UI Framework**: PySide6 (Qt for Python)
- **Speech-to-Text**: Groq API (Whisper)
- **LLM**: Groq API (Kimi K2)
- **TTS**: Microsoft Edge TTS (kostenlos!)
- **Audio**: sounddevice, soundfile
- **Hotkeys**: keyboard (globale Hotkeys)
- **Updates**: GitHub Releases API

### **Architektur**
```
main.py                    # Controller & App-Logik
├── stt_app/
│   ├── ui_main.py        # Hauptfenster
│   ├── ui_overlay.py     # 3D-Visualisierung
│   ├── ui_dialog.py      # Dialog-Modus
│   ├── ui_update.py      # Update-Dialog
│   ├── audio.py          # Audio-Aufnahme
│   ├── groq_client.py    # Groq API Integration
│   ├── tts_client.py     # Text-to-Speech
│   ├── updater.py        # Auto-Update System
│   ├── theme.py          # Dark Theme
│   └── config.py         # Einstellungen
```

### **API-Kosten**
- **Groq API**: Kostenlos (mit Limits)
- **Edge TTS**: Komplett kostenlos!
- **GitHub Releases**: Kostenlos

---

## 🤝 **Mitwirken**

Contributions sind willkommen! 🎉

1. Fork das Repository
2. Erstelle einen Feature-Branch (`git checkout -b feature/AmazingFeature`)
3. Commit deine Änderungen (`git commit -m 'Add some AmazingFeature'`)
4. Push zum Branch (`git push origin feature/AmazingFeature`)
5. Öffne einen Pull Request

---

## 📄 **Lizenz**

Dieses Projekt ist unter der MIT-Lizenz lizenziert - siehe [LICENSE](LICENSE) für Details.

---

## 🙏 **Credits**

- **Whisper** von OpenAI
- **Groq** für blitzschnelle AI-Inferenz
- **Microsoft Edge TTS** für kostenlose Sprachausgabe
- **PySide6** für das UI-Framework

---

## 📞 **Support**

- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/Dolcruz/stt-desktop/issues)
- 💡 **Feature Requests**: [GitHub Issues](https://github.com/Dolcruz/stt-desktop/issues)
- 📖 **Dokumentation**: [Wiki](https://github.com/Dolcruz/stt-desktop/wiki)

---

## 🎉 **Happy Transcribing!**

Made with ❤️ and lots of ☕

---

**[⬇️ Download Latest Release](https://github.com/Dolcruz/stt-desktop/releases/latest/download/STTDesktop.exe)**
