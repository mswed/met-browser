from PySide6 import QtGui, QtWidgets, QtCore
from loguru import logger
import requests
from src.api.classification_index import ClassificationIndex
from src.api.met_api import MetAPI
from src.api.image_record_cache import ImageRecordCache
from src.ui.worker import Fetcher
from pprint import pprint


class Image(QtWidgets.QLabel):
    """
    Display an image in the UI
    """

    def __init__(self, size=(200, 200), public_domain=False, parent=None):
        super().__init__(parent=parent)
        self.public_domain = public_domain
        self.setFixedSize(*size)
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setScaledContents(False)
        self.setText("loading...")
        self.setStyleSheet(
            "color: gray; font-size: 10px; background: #f9f9f9; border-radius: 4px;"
        )

    def load_image_from_url(self, image_url):
        if self.public_domain is False:
            self.setText("Image Not In  The Public Domain")
            return

        if not image_url:
            self.setText("No Image")
            return

        try:
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()

            pixmap = QtGui.QPixmap()
            pixmap.loadFromData(response.content)

            if pixmap.isNull():
                self.setText("Invalid Image")
                return

            scaled_pixmap = pixmap.scaled(
                self.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation
            )

            # We have an image style and set propery
            self.setPixmap(scaled_pixmap)
        except Exception as e:
            self.setText("Error Loading Image")
            print(f"Error: Failed to load image {str(e)}")


class ResultWidget(QtWidgets.QWidget):
    def __init__(self, data, parent=None):
        super().__init__(parent=parent)
        self.data = data
        self.is_public_domain = self.data.get("isPublicDomain", False)
        self.setup_ui()
        self.setStyleSheet("""
            ResultWidget {
                background-color: white;
                border-bottom: 1px solid #e0e0e0;
            }
            ResultWidget:hover {
                background-color: #f5f5f5;
            }
        """)

    def setup_ui(self):
        main_layout = QtWidgets.QHBoxLayout()
        main_layout.setContentsMargins(12, 8, 12, 8)
        main_layout.setSpacing(12)
        self.setLayout(main_layout)

        # Left column (Image)
        image = Image(public_domain=self.data.get("isPublicDomain"))
        image.load_image_from_url(self.data.get("primaryImageSmall"))
        main_layout.addWidget(image)

        # Middle column (Text data)
        data_column = QtWidgets.QVBoxLayout()
        data_column.setSpacing(4)
        data_column.setAlignment(QtCore.Qt.AlignTop)
        main_layout.addLayout(data_column)

        # Title
        title = self.data.get("title", "Untitled") or "Untitled"
        title_label = QtWidgets.QLabel(title)
        font = title_label.font()
        font.setBold(True)
        font.setPointSize(13)
        title_label.setFont(font)
        title_label.setWordWrap(True)
        title_label.setStyleSheet("color: #000;")

        # Artist
        artist = (
            self.data.get("artistDisplayName", "Unknown Artist") or "Unknown Artist"
        )
        artist_label = QtWidgets.QLabel(artist)
        artist_label.setStyleSheet("color: #666; font-size: 12px;")

        # Medium
        medium = self.data.get("medium", "Unknown Medium") or "Unknown Medium"
        display_medium = medium[:50] + "..." if len(medium) > 50 else medium
        medium_label = QtWidgets.QLabel(display_medium)
        medium_label = QtWidgets.QLabel(display_medium)
        medium_label.setToolTip(medium)
        medium_label.setStyleSheet("color: #999; font-size: 11px;")

        # Department
        department_label = QtWidgets.QLabel(self.data.get("department", ""))
        department_label.setStyleSheet(
            "color: #0066cc; font-size: 11px; font-weight: 500;"
        )

        data_column.addWidget(title_label)
        data_column.addWidget(artist_label)
        data_column.addWidget(medium_label)
        data_column.addWidget(department_label)
        data_column.addStretch()

        date_label = QtWidgets.QLabel(self.data.get("objectDate", ""))
        date_label.setWordWrap(True)
        date_label.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignRight)
        date_label.setStyleSheet("color: #999; font-size: 11px;")
        main_layout.addWidget(date_label)


class ClassifictionWidget(QtWidgets.QWidget):
    def __init__(self, classification, record_ids, main_window, parent=None):
        super().__init__(parent=parent)
        self.classification = classification
        self.record_ids = set(record_ids)
        self.main_window = main_window
        self.setup_ui()

    @property
    def count(self):
        return len(self.filtered_record_ids)

    @property
    def filtered_record_ids(self):
        if self.main_window.has_images.isChecked():
            return list(self.main_window.records_with_images & self.record_ids)
        else:
            return list(self.record_ids)

    def setup_ui(self):
        main_layout = QtWidgets.QHBoxLayout()
        main_layout.setContentsMargins(8, 4, 8, 4)
        main_layout.setSpacing(8)
        self.setLayout(main_layout)

        classification_label = QtWidgets.QLabel(self.classification)
        font = classification_label.font()
        font.setBold(True)
        font.setPointSize(10)
        classification_label.setFont(font)
        # Split long classifications into two lines
        classification_label.setWordWrap(True)
        classification_label.setMaximumHeight(34)
        main_layout.addWidget(classification_label)
        main_layout.addStretch()

        # Count badge
        self.count_label = QtWidgets.QLabel(str(self.count))
        self.count_label.setAlignment(QtCore.Qt.AlignCenter)
        self.count_label.setMinimumWidth(30)
        self.count_label.setStyleSheet("""
                    QLabel {
                        background-color: #e0e0e0;
                        color: #555;
                        border-radius: 10px;
                        padding: 2px 8px;
                        font-size: 11px;
                    }
                """)

        main_layout.addWidget(self.count_label)

    def update_count(self):
        if self.main_window.has_images.isChecked():
            self.count_label.setText(f"~{self.count}")
            self.count_label.setToolTip("API approximation - some items maybe exluded")
        else:
            self.count_label.setText(str(self.count))


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None) -> None:
        super(MainWindow, self).__init__(parent)

        self.setWindowTitle("Met Browser")
        self.setMinimumSize(400, 300)
        self.fetcher_thread = None
        self.local_api = ClassificationIndex()
        self.met_api = MetAPI()
        self.image_cache = ImageRecordCache()
        self.records_with_images = self.image_cache.load_cache()
        self.current_results = []
        self.setup_progress_bar()
        self.set_ui()
        self.setStyleSheet("""
                    QMainWindow {
                        background-color: #f5f5f5;
                    }
                    QListWidget {
                        background-color: white;
                        border: 1px solid #d0d0d0;
                        border-radius: 6px;
                        outline: none;
                    }
                    QListWidget::item {
                        border-bottom: 1px solid #f0f0f0;
                        padding: 2px;
                    }
                    QListWidget::item:selected {
                        background-color: #0066cc;
                        color: white;
                    }
                    QListWidget::item:hover {
                        background-color: #e8e8e8;
                    }
                    QLineEdit {
                        padding: 6px 8px;
                        border: 1px solid #d0d0d0;
                        border-radius: 6px;
                        background-color: white;
                        font-size: 13px;
                    }
                    QLineEdit:focus {
                        border: 2px solid #0066cc;
                    }
                    QCheckBox {
                        font-size: 13px;
                        spacing: 6px;
                    }
                    QComboBox {
                        padding: 7px 8px;
                        border: 1px solid #d0d0d0;
                        border-radius: 6px;
                        background-color: white;
                        font-size: 13px;
                    }
                    QPushButton {
                        padding: 4px 12px;
                        border: 1px solid #d0d0d0;
                        border-radius: 6px;
                        background-color: white;
                        font-size: 13px;
                    }
                    QPushButton:hover {
                        background-color: #e8e8e8;
                    }
                    QPushButton:pressed {
                        background-color: #d0d0d0;
                    }
                """)

    def setup_progress_bar(self):
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.hide()

        self.statusBar().addPermanentWidget(self.progress_bar)

    def set_ui(self):
        # Main widget setup
        main_layout = QtWidgets.QHBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        main_widget = QtWidgets.QWidget()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Column view
        columns_layout = QtWidgets.QHBoxLayout()
        main_layout.addLayout(columns_layout)

        # Classifications column
        classifications_column = QtWidgets.QWidget()
        classification_layout = QtWidgets.QVBoxLayout()
        classification_layout.setContentsMargins(0, 0, 0, 0)
        classification_layout.setSpacing(8)
        classifications_column.setLayout(classification_layout)
        columns_layout.addWidget(classifications_column)

        # Label
        classification_label = QtWidgets.QLabel("Classifications")
        title_font = classification_label.font()
        title_font.setBold(True)
        title_font.setPointSize(13)
        classification_label.setFont(title_font)

        self.search_field = QtWidgets.QLineEdit()
        self.search_field.setPlaceholderText("Filter Classifications...")
        self.search_field.setClearButtonEnabled(True)
        self.search_field.textChanged.connect(self.filter_classifications)

        self.has_images = QtWidgets.QCheckBox("Has Images")
        self.has_images.checkStateChanged.connect(self.on_has_images_toggle)

        self.classifications_list = QtWidgets.QListWidget()
        self.classifications_list.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.classifications_list.setAlternatingRowColors(False)
        self.classifications_list.currentItemChanged.connect(
            self.on_classification_item_selected
        )

        for key, value in sorted(
            self.local_api.get_classification_list().items(), key=lambda x: x[0].lower()
        ):
            item = QtWidgets.QListWidgetItem(self.classifications_list)
            records = [int(r) for r in value]
            item_widget = ClassifictionWidget(key, records, main_window=self)
            item.setSizeHint(item_widget.sizeHint())
            self.classifications_list.setItemWidget(item, item_widget)

        classification_layout.addWidget(classification_label)
        classification_layout.addWidget(self.search_field)
        classification_layout.addWidget(self.has_images)
        classification_layout.addWidget(self.classifications_list)

        # Results column
        results_column = QtWidgets.QWidget()
        results_layout = QtWidgets.QVBoxLayout()
        results_layout.setContentsMargins(0, 0, 0, 0)
        results_layout.setSpacing(8)
        results_column.setLayout(results_layout)
        columns_layout.addWidget(results_column)

        sorting_label = QtWidgets.QLabel("Sort By Date")
        sorting_font = sorting_label.font()
        sorting_font.setBold(True)
        sorting_font.setPointSize(13)
        sorting_label.setFont(sorting_font)
        self.sorting_combo = QtWidgets.QComboBox()
        self.sorting_combo.addItems(["Ascending", "Descending"])
        self.sorting_combo.currentIndexChanged.connect(self.populate_results)

        results_layout.addWidget(sorting_label)
        results_layout.addWidget(self.sorting_combo)

        self.results_list = QtWidgets.QListWidget()
        self.results_list.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.results_list.setSpacing(0)
        self.results_list.currentItemChanged.connect(self.on_result_item_selected)
        results_layout.addWidget(self.results_list)

    def on_classification_item_selected(self, current, previous):
        if not current:
            return

        # If we already have a process running stop it
        if self.fetcher_thread and self.fetcher_thread.isRunning():
            self.fetcher_thread.stop()
            self.fetcher_thread.wait()

        # Clear existing results
        self.current_results = []
        self.results_list.clear()

        # Get record ids
        widget = self.classifications_list.itemWidget(current)
        record_ids = widget.filtered_record_ids[:80]

        # Setup the progress bar
        self.progress_bar.setMaximum(len(record_ids))
        self.progress_bar.setValue(0)
        self.progress_bar.show()

        # Start a thread so we don't lock the UI
        self.fetcher_thread = Fetcher(self.met_api, record_ids)
        self.fetcher_thread.progress.connect(self.on_fetch_progress)
        self.fetcher_thread.result_ready.connect(self.on_result_ready)
        self.fetcher_thread.finished.connect(self.on_fetch_finished)
        self.fetcher_thread.error.connect(self.on_fetch_error)
        self.fetcher_thread.start()

        self.statusBar().showMessage("Loading results...")

    def on_fetch_progress(self, current, total, message):
        """
        Update progress as results load
        """
        self.progress_bar.setValue(current)
        self.statusBar().showMessage(message)

    def on_result_ready(self, result):
        # We need to filter results without images since the API is unreliable
        if self.has_images.isChecked():
            image_url = result.get("primaryImageSmall")

            if not image_url:
                # Skip it, there's no image here
                return

        self.current_results.append(result)
        self.add_result_item(result)

    def on_fetch_finished(self, results):
        """
        All results loaded
        """

        self.progress_bar.hide()
        self.current_results = results
        self.populate_results()
        self.statusBar().showMessage(f"Loaded {len(results)} objects", 3000)

    def on_fetch_error(self, error_message):
        # Stop the thread
        if self.fetcher_thread and self.fetcher_thread.isRunning():
            self.fetcher_thread.stop()
            self.fetcher_thread.wait(1000)

        self.progress_bar.hide()

        QtWidgets.QMessageBox.warning(
            self,
            "Failed to load results",
            f"Failed to load results from the Met! This is likely do to rate limit issues. Please wait at least 60 seconds and try again",
            QtWidgets.QMessageBox.Ok,
        )

        self.statusBar().showMessage("Failed to load results...", 3000)

    def on_result_item_selected(self, current, previous):
        pprint(current.data(QtCore.Qt.UserRole))

    def on_has_images_toggle(self):
        for i in range(self.classifications_list.count()):
            item = self.classifications_list.item(i)
            widget = self.classifications_list.itemWidget(item)

            if widget:
                widget.update_count()

        current_classification = self.classifications_list.selectedItems()
        if current_classification:
            current_classification = current_classification[0]
        else:
            current_classification = None
        # TODO: This re-fatches the records, we should use cache instead
        self.on_classification_item_selected(current_classification, None)

    def add_result_item(self, result):
        item = QtWidgets.QListWidgetItem(self.results_list)
        item_widget = ResultWidget(result)
        item.setSizeHint(item_widget.sizeHint())
        self.results_list.setItemWidget(item, item_widget)
        item.setData(QtCore.Qt.UserRole, result)

    def populate_results(self):
        self.results_list.clear()
        sort_direction = self.sorting_combo.currentText()
        sort_results = self.sort_results(sort_direction.lower())

        for result in sort_results:
            if self.has_images.isChecked():
                image_url = result.get("primaryImageSmall")

                if not image_url:
                    # Skip it, there's no image here
                    continue

            self.add_result_item(result)

        self.statusBar().showMessage(f"Loaded {len(sort_results)} results")

    def sort_results(self, direction="ascending"):
        return sorted(
            self.current_results,
            key=lambda x: x.get("objectBeginDate", 0),
            reverse=direction != "ascending",
        )

    def filter_classifications(self, search_text):
        search_text = search_text.lower()

        for i in range(self.classifications_list.count()):
            item = self.classifications_list.item(i)
            widget = self.classifications_list.itemWidget(item)

            # Get the classification name
            classification_name = widget.classification.lower()

            # Show/Hide item based on result
            item.setHidden(search_text not in classification_name)
