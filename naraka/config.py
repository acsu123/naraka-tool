import os
from pathlib import Path

BASE_DIR      = Path(__file__).parent.parent
CONVERTED_DIR = BASE_DIR / "converted"
CONVERTED_DIR.mkdir(exist_ok=True)

SOURCE_HOST      = "yjwujian.cn"
SOURCE_PATH      = "/yjwj/studio_share/game_detail"
NARAKA_BASE      = "https://www.narakathegame.com/h5/20260401/yingpengfx/"
CONVERTED_SUFFIX = "CONVERTED"
DEBUG            = False

QSD_REL = os.path.join("NarakaBladepoint_Data", "QualitySettingsData.txt")

PLATFORM_ROOTS = {
    "epic": [r"C:\Program Files\Epic Games\NarakaBladepoint"],
    "vng": [
        r"C:\Program Files (x86)\Level Up Games\Naraka Bladepoint",
        r"C:\Program Files\Level Up Games\Naraka Bladepoint",
    ],
}

# Color palette
BG        = "#1a1a1a"
SURFACE   = "#242424"
CARD      = "#2c2c2c"
BORDER    = "#383838"
TEXT      = "#e0e0e0"
MUTED     = "#6b6b6b"
ACCENT    = "#4f8ef7"
GREEN     = "#3dd68c"
GREEN_DIM = "#1a3d2e"
RED       = "#f56565"
YELLOW    = "#f0c040"
