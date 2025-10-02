"""
Auto-Update System using GitHub Releases
Checks for new versions and downloads updates automatically
"""

import logging
import requests
import subprocess
import sys
from pathlib import Path
from typing import Optional, Tuple
from packaging import version

logger = logging.getLogger(__name__)

# GitHub repository information
GITHUB_OWNER = "Dolcruz"
GITHUB_REPO = "stt-desktop"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest"


def get_current_version() -> str:
    """Get current application version from VERSION file."""
    try:
        # Check if running as frozen exe (PyInstaller)
        if getattr(sys, 'frozen', False):
            # Running as .exe - look in PyInstaller temp folder first
            if hasattr(sys, '_MEIPASS'):
                version_file = Path(sys._MEIPASS) / "VERSION"
                logger.info(f"Looking for VERSION in PyInstaller temp: {version_file}")
                if version_file.exists():
                    ver = version_file.read_text(encoding="utf-8").strip()
                    logger.info(f"Found VERSION in bundle: {ver}")
                    return ver
            
            # Fallback: next to .exe
            version_file = Path(sys.executable).parent / "VERSION"
            logger.info(f"Looking for VERSION next to exe: {version_file}")
            if version_file.exists():
                ver = version_file.read_text(encoding="utf-8").strip()
                logger.info(f"Found VERSION next to exe: {ver}")
                return ver
        else:
            # Running as Python script
            version_file = Path(__file__).parent.parent / "VERSION"
            if version_file.exists():
                return version_file.read_text(encoding="utf-8").strip()
        
        logger.warning("VERSION file not found, defaulting to 1.0.0")
        return "1.0.0"
    except Exception as e:
        logger.error(f"Could not read VERSION file: {e}")
        return "1.0.0"


def check_for_updates() -> Optional[Tuple[str, str, str]]:
    """
    Check GitHub for new releases.
    
    Returns:
        Tuple of (new_version, download_url, release_notes) if update available, None otherwise
    """
    try:
        current = get_current_version()
        logger.info(f"Current version: {current}")
        
        # Query GitHub API for latest release
        response = requests.get(GITHUB_API_URL, timeout=10)
        response.raise_for_status()
        
        release_data = response.json()
        latest_version = release_data.get("tag_name", "").lstrip("v")
        release_notes = release_data.get("body", "Keine Release-Notes verfügbar")
        
        logger.info(f"Latest version on GitHub: {latest_version}")
        
        # Compare versions
        if version.parse(latest_version) > version.parse(current):
            # Find Windows .exe asset
            assets = release_data.get("assets", [])
            exe_asset = next(
                (a for a in assets if a["name"].endswith(".exe")),
                None
            )
            
            if exe_asset:
                download_url = exe_asset["browser_download_url"]
                logger.info(f"Update available: {latest_version}")
                return (latest_version, download_url, release_notes)
            else:
                logger.warning("No .exe file found in latest release")
                return None
        else:
            logger.info("Application is up to date")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error checking for updates: {e}")
        return None
    except Exception as e:
        logger.error(f"Error checking for updates: {e}")
        return None


def download_update(download_url: str, progress_callback=None) -> Optional[Path]:
    """
    Download update from GitHub.
    
    Args:
        download_url: URL to download .exe from
        progress_callback: Optional callback function(bytes_downloaded, total_bytes)
    
    Returns:
        Path to downloaded file, or None on error
    """
    try:
        logger.info(f"Downloading update from {download_url}")
        
        # Download to temp directory
        response = requests.get(download_url, stream=True, timeout=30)
        response.raise_for_status()
        
        total_size = int(response.headers.get("content-length", 0))
        downloaded = 0
        
        # Save to temp file
        temp_file = Path.home() / "Downloads" / "STTDesktop_Update.exe"
        temp_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(temp_file, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if progress_callback:
                        progress_callback(downloaded, total_size)
        
        logger.info(f"Update downloaded to {temp_file}")
        return temp_file
        
    except Exception as e:
        logger.error(f"Error downloading update: {e}")
        return None


def install_update(update_file: Path) -> bool:
    """
    Install downloaded update by replacing current executable.
    
    Args:
        update_file: Path to downloaded .exe
    
    Returns:
        True if installation started successfully
    """
    try:
        if not update_file.exists():
            logger.error(f"Update file not found: {update_file}")
            return False
        
        # Get current executable path
        if getattr(sys, 'frozen', False):
            # Running as .exe
            current_exe = Path(sys.executable)
            logger.info(f"Current exe: {current_exe}")
            
            # Create update script that will:
            # 1. Wait for current app to close
            # 2. Replace old .exe with new one
            # 3. Start new .exe
            # 4. Delete itself
            
            update_script = current_exe.parent / "_update.bat"
            script_content = f"""@echo off
echo Warte auf Beendigung der Anwendung...
timeout /t 2 /nobreak >nul
echo Installiere Update...
move /Y "{update_file}" "{current_exe}"
echo Starte Anwendung neu...
start "" "{current_exe}"
del "%~f0"
"""
            update_script.write_text(script_content, encoding="utf-8")
            
            # Start update script and exit current app
            subprocess.Popen(
                ["cmd.exe", "/c", str(update_script)],
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            logger.info("Update script started, exiting application")
            return True
        else:
            # Running as Python script - just show message, don't try to update
            logger.warning("Running from Python source - auto-update is only available for .exe version")
            import os
            # Open download folder
            os.startfile(update_file.parent)
            return False
            
    except Exception as e:
        logger.error(f"Error installing update: {e}")
        return False

