import os
import json
import string
import winreg

from .config import QSD_REL, PLATFORM_ROOTS


def _find_steam_naraka() -> list:
    paths = []
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam") as k:
            steam = os.path.normpath(winreg.QueryValueEx(k, "SteamPath")[0])
        libs = [steam]
        vdf = os.path.join(steam, "steamapps", "libraryfolders.vdf")
        if os.path.exists(vdf):
            with open(vdf, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    s = line.strip().strip('"')
                    if os.path.isabs(s) and os.path.exists(s):
                        libs.append(s)
        for lib in libs:
            c = os.path.join(lib, "steamapps", "common", "NARAKA BLADEPOINT")
            if os.path.exists(c):
                paths.append(c)
    except Exception:
        pass
    return paths


def find_naraka_paths(platform: str, custom: str = "") -> list:
    if platform == "custom":
        return [custom] if custom and os.path.exists(custom) else []
    if platform == "steam":
        return _find_steam_naraka()
    return [p for p in PLATFORM_ROOTS.get(platform, []) if os.path.exists(p)]


def scan_all_drives() -> list:
    found = []
    skip = {"Windows", "$Recycle.Bin", "System Volume Information",
            "ProgramData", "Recovery", "$WinREAgent", "WpSystem"}
    drives = [f"{d}:\\" for d in string.ascii_uppercase if os.path.exists(f"{d}:\\")]
    for drive in drives:
        for root, dirs, files in os.walk(drive):
            dirs[:] = [d for d in dirs if d not in skip]
            if ("QualitySettingsData.txt" in files and
                    os.path.basename(root) == "NarakaBladepoint_Data"):
                install = os.path.dirname(root)
                if install not in found:
                    found.append(install)
    return found


def apply_physics(install_path: str) -> None:
    for qsd in [
        os.path.join(install_path, QSD_REL),
        os.path.join(install_path, "program", QSD_REL),
    ]:
        if os.path.exists(qsd):
            with open(qsd, "r", encoding="utf-8") as f:
                data = json.load(f)
            if "l22SystemQualitySetting" not in data:
                raise KeyError("Unexpected file format")
            data["l22SystemQualitySetting"]["characterAdditionalPhysics1"] = True
            with open(qsd, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False)
            return
    raise FileNotFoundError(f"QualitySettingsData.txt not found in {install_path}")
