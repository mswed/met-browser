from PySide6.QtCore import QThread, Signal
from loguru import logger


class Fetcher(QThread):
    """
    Thread to access API without blocking UI
    """

    # Progress has three variables: current, total, message
    progress = Signal(int, int, str)
    result_ready = Signal(dict)
    finished = Signal(list)

    def __init__(self, api, record_ids):
        super().__init__()
        self.api = api
        self.record_ids = record_ids
        self.results = []

    def run(self):
        """
        Get records in the background
        """
        total = len(self.record_ids)
        for i, record_id in enumerate(self.record_ids):
            self.progress.emit(i + 1, total, f"Loading {i + 1}/{total}...")

            result = self.api.get_single_record(record_id)

            if result:
                self.results.append(result)
                self.result_ready.emit(result)

        self.finished.emit(self.results)
