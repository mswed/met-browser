import sys
from pathlib import Path


def get_app_data_dir():
    """
    A python app and a macOS bundles have different places it can write to
    so we need to figure out where our files can live
    """
    if getattr(sys, "frozen", False):
        # We are running as a bundle
        app_support = Path.home() / "Library" / "Application Support" / "Met Browser"
        app_support.mkdir(parents=True, exist_ok=True)

        # Copy over the files
        bundle_data = Path(sys._MEIPASS) / "data"
        for f in ["classification_index.json", "image_cache.json"]:
            dest = app_support / f
            if not dest.exists() and (bundle_data / f).exists():
                import shutil

                shutil.copy2(bundle_data / f, dest)
        return app_support
    else:
        return Path(__file__).parent.parent.parent / "data"
