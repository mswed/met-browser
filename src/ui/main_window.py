from typing import Dict
from PySide6 import QtGui, QtWidgets, QtCore
from src.ui.widgets import ClassificationWidget, ResultWidget
from src.api.classification_index import ClassificationIndex
from src.api.met_api import MetAPI
from src.api.image_record_cache import ImageRecordCache
from src.ui.worker import Fetcher
from pprint import pprint


class MainWindow(QtWidgets.QMainWindow):
    """
    Main application window
    """

    def __init__(self, parent=None) -> None:
        super(MainWindow, self).__init__(parent)

        self.setWindowTitle("Met Browser")
        self.setMinimumSize(800, 600)
        self.fetcher_thread = None
        self.local_api = ClassificationIndex()
        self.met_api = MetAPI()
        self.image_cache = ImageRecordCache()
        self.records_with_images = self.image_cache.load_cache()
        self.current_results = []
        self.setup_progress_bar()
        self.set_ui()
        self.create_menubar()
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

    def set_ui(self):
        """
        Build the main UI
        """
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
        self.has_images.stateChanged.connect(self.on_has_images_toggle)

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
            item_widget = ClassificationWidget(key, records, main_window=self)
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
        results_layout.addWidget(self.results_list)

    def setup_progress_bar(self):
        """
        Setup a progress bar at the bottom right of the window
        """
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.hide()

        self.statusBar().addPermanentWidget(self.progress_bar)

    def create_menubar(self):
        """
        Create a menu bar with File and Tools menus
        """
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        quit_action = QtGui.QAction("Quit", self)
        quit_action.setShortcut(QtGui.QKeySequence("Ctrl+Q"))
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        tools_menu = menubar.addMenu("Tools")
        refresh_cache_action = QtGui.QAction("Refresh Image Cache...", self)
        refresh_cache_action.triggered.connect(self.refresh_image_cache_callback)
        tools_menu.addAction(refresh_cache_action)

    def refresh_image_cache_callback(self):
        """
        Ask the user if they really want to update the cache, since it takes a while
        """
        # Using a custom dialog to match Mac standards a little better
        msg = QtWidgets.QMessageBox(self)
        msg.setIcon(QtWidgets.QMessageBox.Question)
        msg.setWindowTitle("Refresh Image Cache")
        msg.setText("This will rebuild the cache of records with images.")
        msg.setInformativeText("This takes a couple of minutes. Continue?")

        rebuild_btn = msg.addButton("Rebuild", QtWidgets.QMessageBox.AcceptRole)
        cancel_btn = msg.addButton("Cancel", QtWidgets.QMessageBox.RejectRole)

        msg.setDefaultButton(cancel_btn)

        msg.exec()

        if msg.clickedButton() == rebuild_btn:
            self.rebuild_cache()

    def rebuild_cache(self):
        """
        Refresh the cache of records with images (according to the API at least)
        """
        # We will iterate over all letters
        self.progress_bar.setMaximum(26)
        self.progress_bar.setValue(0)
        self.progress_bar.show()

        # Disable the UI (at least partly)
        self.classifications_list.setEnabled(False)
        self.results_list.setEnabled(False)

        def progress_callback(current, total, message):
            self.progress_bar.setValue(current)
            self.statusBar().showMessage(message)
            # We want to keep the UI responsive
            QtWidgets.QApplication.processEvents()

        try:
            # Fetch the new cache
            self.image_cache.save_cache(progress_callback=progress_callback)

            # Load it into the app
            self.records_with_images = self.image_cache.load_cache()

            self.progress_bar.hide()
            self.statusBar().showMessage(
                f"Cache rebuilt {len(self.records_with_images)} records with images",
                5000,
            )

            QtWidgets.QMessageBox.information(
                self, "Cache rebuilt", "Image cache updated!"
            )

            # Refresh the count badges
            self.on_has_images_toggle()

        except Exception as e:
            self.progress_bar.hide()
            QtWidgets.QMessageBox.critical(
                self, "Cache rebuild failed!", f"Failed to rebuild cache {e}"
            )
        finally:
            # Re-enable to UI
            self.classifications_list.setEnabled(True)
            self.results_list.setEnabled(True)
            self.progress_bar.hide()

    def on_classification_item_selected(self, current, previous):
        """
        When a classification is selected we fetch 80 records from the database, and display them in the results column.
        This uses a thread so we don't lock up the UI and provide constant updates

        :param current: Current ListItemWidget selected in the UI
        :param previous: Previous ListItemWidget selected in the UI (Not used)
        """
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

    def on_fetch_progress(self, current: int, total: int, message: str):
        """
        Update progress as results load
        :param current: Current number of record being processed
        :param total: Total records to process
        :param message: Message to display to the user
        """
        self.progress_bar.setValue(current)
        self.statusBar().showMessage(message)

    def on_result_ready(self, result: Dict):
        """
        When a single record finishes processing we add it to the results list and to the gui

        :param result: Record data from the API
        """
        # We need to filter results without images since the API is unreliable
        if self.has_images.isChecked():
            image_url = result.get("primaryImageSmall")

            if not image_url:
                # Skip it, there's no image here
                return

        self.current_results.append(result)
        self.add_result_item(result)

    def on_fetch_finished(self, results: list[Dict]):
        """
        When all of the results are loaded we sort them and display them in the UI

        :param results: List of fetched records data
        """

        self.progress_bar.hide()
        self.current_results = results
        self.populate_results()
        self.statusBar().showMessage(f"Loaded {len(results)} objects", 3000)

    def on_fetch_error(self, error_message: str):
        """
        If we got an error while fetching (most likey rate limit) we warn the user and stop the thread.

        :param error_message: The error message from the API module, at the moment we do not display it
        """

        # Stop the thread
        if self.fetcher_thread and self.fetcher_thread.isRunning():
            self.fetcher_thread.stop()
            self.fetcher_thread.wait(1000)

        self.progress_bar.hide()

        QtWidgets.QMessageBox.warning(
            self,
            "Failed to load results",
            "Failed to load results from the Met! This is likely do to rate limit issues. Please wait at least 60 seconds and try again",
            QtWidgets.QMessageBox.Ok,
        )

        self.statusBar().showMessage("Failed to load results...", 3000)

    def add_result_item(self, result: Dict):
        """
        Add a record to the results column

        :param result: Dictionary containing all of the record data
        """

        item = QtWidgets.QListWidgetItem(self.results_list)
        item_widget = ResultWidget(result)
        item.setSizeHint(item_widget.sizeHint())
        self.results_list.setItemWidget(item, item_widget)
        item.setData(QtCore.Qt.UserRole, result)

    def populate_results(self):
        """
        Rebuild the results list in the results column. This is used instead of in place sorting
        """

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

    def sort_results(self, direction: str = "ascending") -> list[Dict]:
        """
        Sort the results list so that populate_results can create the widgets in the right order

        :param direction: Sort direction ascending or descending
        :returns: List of sorted records
        """
        return sorted(
            self.current_results,
            key=lambda x: x.get("objectBeginDate", 0),
            reverse=direction != "ascending",
        )

    def on_has_images_toggle(self):
        """
        When we toggle the has_images checkbox we need to update the record count
        """
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

    def filter_classifications(self, search_text: str):
        """
        Filters the classification list based on th search text

        :param search_text: A string to search for in the classification name
        """
        search_text = search_text.lower()

        for i in range(self.classifications_list.count()):
            item = self.classifications_list.item(i)
            widget = self.classifications_list.itemWidget(item)

            # Get the classification name
            classification_name = widget.classification.lower()

            # Show/Hide item based on result
            item.setHidden(search_text not in classification_name)
