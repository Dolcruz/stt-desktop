# 🚀 Release-Anleitung für STTDesktop

Diese Anleitung erklärt, wie du ein neues Update für alle User veröffentlichst.

## 📋 Voraussetzungen

- Alle Änderungen sind committed und gepusht
- Die App funktioniert einwandfrei
- Du hast die .exe mit PyInstaller gebaut

## 🔢 Schritt 1: Version erhöhen

1. Öffne die Datei `VERSION` im Projektordner
2. Erhöhe die Versionsnummer (z.B. von `1.0.0` auf `1.0.1`)
   - **Patch** (z.B. 1.0.**1**): Bugfixes
   - **Minor** (z.B. 1.**1**.0): Neue Features
   - **Major** (z.B. **2**.0.0): Große Änderungen
3. Speichere die Datei

## 📦 Schritt 2: .exe bauen

1. Öffne PowerShell im Projektordner
2. Führe den Build-Befehl aus:
   ```powershell
   .\build_windows.ps1
   ```
   oder
   ```powershell
   pyinstaller STTDesktop.spec
   ```
3. Die fertige .exe befindet sich in `dist\STTDesktop.exe`

## 🏷️ Schritt 3: Git Release vorbereiten

1. **Committe die VERSION-Änderung:**
   ```bash
   git add VERSION
   git commit -m "Bump version to 1.0.1"
   git push
   ```

## 🎉 Schritt 4: GitHub Release erstellen

1. Gehe zu deinem GitHub Repository:
   https://github.com/Dolcruz/stt-desktop

2. Klicke auf **"Releases"** (rechts in der Sidebar)

3. Klicke auf **"Draft a new release"**

4. **Tag erstellen:**
   - Klicke auf "Choose a tag"
   - Gib die neue Version ein: **`v1.0.1`** (mit "v" am Anfang!)
   - Klicke auf "Create new tag: v1.0.1 on publish"

5. **Release Title:**
   - Gib einen Titel ein: z.B. **"Version 1.0.1 - Bugfixes"**

6. **Release Notes:**
   - Beschreibe was neu ist, z.B.:
   ```markdown
   ## 🆕 Neu
   - Dialog-Modus mit kostenloser TTS
   - Auto-Update System
   
   ## 🐛 Bugfixes
   - Windows Audio-Playback behoben
   - Overlay-Start Fehler behoben
   
   ## 📦 Installation
   1. Lade `STTDesktop.exe` herunter
   2. Starte die Anwendung
   3. Fertig!
   ```

7. **Dateien hochladen:**
   - Ziehe `dist\STTDesktop.exe` in den "Attach binaries" Bereich
   - **WICHTIG**: Die Datei MUSS `STTDesktop.exe` heißen!

8. Klicke auf **"Publish release"**

## ✅ Fertig!

Das war's! 🎉

**Alle User** bekommen jetzt beim nächsten App-Start automatisch eine **Update-Benachrichtigung** und können mit **einem Klick** auf die neue Version updaten!

---

## 🔄 Was passiert automatisch?

1. User startet die App
2. App prüft GitHub nach neuer Version
3. Wenn neue Version gefunden: **Update-Dialog erscheint**
4. User klickt auf "Jetzt updaten"
5. Update wird heruntergeladen (mit Fortschrittsbalken)
6. App wird automatisch ersetzt und neu gestartet
7. **Fertig! User hat die neue Version!** ✨

---

## 📝 Tipps

- **Immer Version erhöhen** bevor du ein Release machst
- **Aussagekräftige Release Notes** schreiben
- **Testen** bevor du veröffentlichst!
- Bei großen Änderungen: **Major Version** (2.0.0)
- Bei neuen Features: **Minor Version** (1.1.0)
- Bei Bugfixes: **Patch Version** (1.0.1)

## 🆘 Hilfe

Wenn User Probleme haben:
1. Ältere Version manuell löschen
2. Neue .exe aus GitHub Releases herunterladen
3. Neu installieren

---

**Das war's! Happy Releasing! 🚀**

