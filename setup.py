from setuptools import setup

APP = ["src/main.py"]
DATA_FILES = [("data", ["data/classification_index.json", "data/image_cache.json"])]
OPTIONS = {
    "argv_emulation": False,
    "packages": ["PySide6", "loguru", "requests", "tqdm"],
    "includes": [
        "src.ui.main_window",
        "src.api.met_api",
        "src.api.classification_index",
        "src.api.image_record_cache",
        "src.ui.widgets",
        "src.ui.worker",
    ],
    "iconfile": None,
    "plist": {
        "CFBundleName": "Met Browser",
        "CFBundleDisplayName": "Met Browser",
        "CFBundleIdentifier": "com.metbrowser",
        "CFBundleVersion": "0.1.0",
        "CFBundleShortVersionString": "0.1.0",
        "NSHighResolutionCapable": True,
    },
}

setup(
    name="Met Browser",
    app=APP,
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)
