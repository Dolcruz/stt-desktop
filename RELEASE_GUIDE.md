# 🚀 **Einfache Release-Anleitung für STTDesktop**

Diese Anleitung ist für **dich** und **jeden**, der ein Update veröffentlichen will - **ohne Technik-Kenntnisse**!

---

## 📦 **Schritt 1: .exe bauen (5 Minuten)**

### **Option A: Mit PowerShell Script (EINFACH)** ⭐

1. Öffne PowerShell im Projektordner
2. Führe aus:
   ```powershell
   .\build_release.ps1
   ```
3. **Fertig!** Die .exe ist in `dist\STTDesktop.exe`

### **Option B: Manuell**

1. Öffne PowerShell im Projektordner
2. Aktiviere venv:
   ```powershell
   .venv\Scripts\Activate.ps1
   ```
3. Installiere alles:
   ```powershell
   pip install -r requirements.txt
   pip install pyinstaller
   ```
4. Baue .exe:
   ```powershell
   pyinstaller --clean STTDesktop.spec
   ```
5. Die fertige .exe ist in `dist\STTDesktop.exe`

---

## 🧪 **Schritt 2: Teste die .exe (2 Minuten)**

1. Öffne `dist\STTDesktop.exe` (Doppelklick)
2. Teste alle Funktionen:
   - ✅ Aufnahme funktioniert?
   - ✅ Transkription funktioniert?
   - ✅ Dialog-Modus funktioniert?
3. **Wenn alles klappt** → Weiter zu Schritt 3!

---

## 🔢 **Schritt 3: Version erhöhen (30 Sekunden)**

1. Öffne die Datei `VERSION` im Projektordner
2. Erhöhe die Nummer:
   - **Bugfix**: `1.0.0` → `1.0.1`
   - **Neue Features**: `1.0.0` → `1.1.0`
   - **Große Änderungen**: `1.0.0` → `2.0.0`
3. Speichere die Datei
4. Committe:
   ```bash
   git add VERSION
   git commit -m "Bump version to 1.0.1"
   git push
   ```

---

## 🎉 **Schritt 4: GitHub Release erstellen (3 Minuten)**

### **1. Gehe zu GitHub Releases:**
👉 https://github.com/Dolcruz/stt-desktop/releases

### **2. Klicke auf "Draft a new release"**

### **3. Fülle die Felder aus:**

#### **Tag:**
- Klicke auf "Choose a tag"
- Gib ein: **`v1.0.1`** (mit "v" davor!)
- Klicke "Create new tag: v1.0.1 on publish"

#### **Release title:**
```
Version 1.0.1 - Dialog-Modus & Bugfixes
```

#### **Release notes:**
```markdown
## 🆕 Was ist neu?

- ✨ Dialog-Modus mit kostenloser Sprachausgabe
- 🔄 Automatisches Update-System
- 🎨 Verbesserte UI

## 🐛 Bugfixes

- Windows Audio-Playback behoben
- Overlay-Fehler behoben
- Sprecher-Wechsel funktioniert jetzt

## 📥 Installation

1. Lade `STTDesktop.exe` herunter (siehe unten)
2. Starte die Datei (Doppelklick)
3. Fertig! Viel Spaß! 🎉

**Wichtig:** Windows Defender könnte warnen - klicke auf "Weitere Informationen" → "Trotzdem ausführen"
```

### **4. Lade die .exe hoch:**
- Ziehe `dist\STTDesktop.exe` in den Bereich "Attach binaries"
- **WICHTIG:** Die Datei MUSS `STTDesktop.exe` heißen!

### **5. Klicke "Publish release"**

---

## ✅ **FERTIG! Das war's!** 🎊

### **Was passiert jetzt?**

1. **Alle User** bekommen beim nächsten App-Start eine **Update-Benachrichtigung**
2. Sie klicken auf **"Jetzt updaten"**
3. Die neue .exe wird automatisch heruntergeladen
4. Die App startet neu mit der neuen Version
5. **Fertig!** ✨

### **Neue User:**

- Können direkt auf der Release-Seite die .exe herunterladen
- Link: https://github.com/Dolcruz/stt-desktop/releases/latest

---

## 📝 **Tipps & Tricks**

### **Download-Link für neue User:**

Gib ihnen diesen Link:
```
https://github.com/Dolcruz/stt-desktop/releases/latest/download/STTDesktop.exe
```

Das ist ein **direkter Download-Link** zur neuesten .exe!

### **Badge für README:**

Füge das zu deinem README.md hinzu:
```markdown
[![Latest Release](https://img.shields.io/github/v/release/Dolcruz/stt-desktop)](https://github.com/Dolcruz/stt-desktop/releases/latest)
```

### **Windows Defender Warnung?**

Das ist normal für neue .exe-Dateien! User müssen:
1. "Weitere Informationen" klicken
2. "Trotzdem ausführen" klicken

---

## 🆘 **Probleme?**

### **"PyInstaller nicht gefunden"**
```powershell
pip install pyinstaller
```

### **".exe startet nicht"**
- Teste auf einem anderen Computer
- Prüfe ob alle Dependencies in `requirements.txt` sind

### **"User können nicht updaten"**
- Prüfe ob `.exe` wirklich `STTDesktop.exe` heißt
- Prüfe ob Tag mit "v" beginnt (z.B. `v1.0.1`)

---

## 🎯 **Checkliste für jedes Release:**

- [ ] Code funktioniert einwandfrei
- [ ] .exe gebaut und getestet
- [ ] VERSION erhöht
- [ ] Git committed und gepusht
- [ ] GitHub Release erstellt
- [ ] Tag erstellt (z.B. `v1.0.1`)
- [ ] Release Notes geschrieben
- [ ] `STTDesktop.exe` hochgeladen
- [ ] Release veröffentlicht
- [ ] Link getestet

---

## 🚀 **Fertig!**

Jetzt kann **jeder** deine App einfach herunterladen und nutzen - **ohne Python**, **ohne Installation**, **ohne Technik-Kenntnisse**! 🎊

**Happy Releasing!** ✨

