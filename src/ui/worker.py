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
    error = Signal(str)

    def __init__(self, api, record_ids):
        super().__init__()
        self.api = api
        self.record_ids = record_ids
        self.results = []
        self._stop = False

    def stop(self):
        self._stop = True

    def run(self):
        """
        Get records in the background
        """
        total = len(self.record_ids)
        try:
            for i, record_id in enumerate(self.record_ids):
                self.progress.emit(i + 1, total, f"Loading {i + 1}/{total}...")

                if self._stop:
                    logger.info("Fetch cancelled")
                    return

                result = self.api.get_single_record(record_id)

                if result:
                    self.results.append(result)
                    self.result_ready.emit(result)

            if not self._stop:
                self.finished.emit(self.results)

        except ConnectionError as e:
            logger.error(f"Error fatching records: {e}")
            self.error.emit(str(e))
