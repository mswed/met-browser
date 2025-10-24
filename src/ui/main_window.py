from PySide6 import QtGui, QtWidgets, QtCore
import requests
from src.api.classification_index import ClassificationIndex
from src.api.met_api import MetAPI
from src.api.image_record_cache import ImageRecordCache
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

    def load_image_from_url(self, image_url):
        if self.public_domain is False:
            self.setText("Image Not In Public Domain")
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

            self.setPixmap(scaled_pixmap)
        except Exception as e:
            self.setText("Error Loading Image")
            print(f"Error: Failed to load image {str(e)}")


class ResultWidget(QtWidgets.QWidget):
    def __init__(self, data, parent=None):
        super().__init__(parent=parent)
        self.data = data
        self.setup_ui()

    def setup_ui(self):
        main_layout = QtWidgets.QHBoxLayout()
        self.setLayout(main_layout)

        image_column = QtWidgets.QVBoxLayout()
        main_layout.addLayout(image_column)
        image = Image(public_domain=self.data.get("isPublicDomain"))
        image.load_image_from_url(self.data.get("primaryImageSmall"))
        image_column.addWidget(image)

        data_column = QtWidgets.QVBoxLayout()
        main_layout.addLayout(data_column)
        title_label = QtWidgets.QLabel(self.data.get("title"))
        font = title_label.font()
        font.setBold(True)
        title_label.setFont(font)

        medium_label = QtWidgets.QLabel(self.data.get("medium"))
        department_label = QtWidgets.QLabel(self.data.get("department"))
        id_label = QtWidgets.QLabel(str(self.data.get("objectID")))
        public_domain_label = QtWidgets.QLabel(str(self.data.get("isPublicDomain")))

        data_column.addWidget(title_label)
        data_column.addWidget(medium_label)
        data_column.addWidget(department_label)
        data_column.addWidget(id_label)
        data_column.addWidget(public_domain_label)

        date_column = QtWidgets.QVBoxLayout()
        main_layout.addLayout(date_column)
        date_label = QtWidgets.QLabel(self.data.get("objectDate"))
        date_column.addWidget(date_label)


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
        self.setLayout(main_layout)

        classification_label = QtWidgets.QLabel(self.classification)
        font = classification_label.font()
        font.setBold(True)
        classification_label.setFont(font)

        self.count_label = QtWidgets.QLabel(str(self.count))

        main_layout.addWidget(classification_label)
        main_layout.addWidget(self.count_label)

    def update_count(self):
        self.count_label.setText(str(self.count))


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None) -> None:
        super(MainWindow, self).__init__(parent)

        self.setWindowTitle("Met Browser")
        self.setMinimumSize(400, 300)
        self.local_api = ClassificationIndex()
        self.met_api = MetAPI()
        self.image_cache = ImageRecordCache()
        self.records_with_images = self.image_cache.load_cache()
        self.current_results = []
        self.set_ui()

    def set_ui(self):
        # Main widget setup
        main_layout = QtWidgets.QHBoxLayout()
        main_widget = QtWidgets.QWidget()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Column view
        columns_layout = QtWidgets.QHBoxLayout()
        main_layout.addLayout(columns_layout)

        # Classifications column
        classifications_column = QtWidgets.QWidget()
        classification_layout = QtWidgets.QVBoxLayout()
        classifications_column.setLayout(classification_layout)
        columns_layout.addWidget(classifications_column)

        # Label
        classification_label = QtWidgets.QLabel("Classifications")
        classification_layout.addWidget(classification_label)

        # Top search filter
        search_widget = QtWidgets.QWidget()
        search_layout = QtWidgets.QHBoxLayout()
        search_widget.setLayout(search_layout)
        self.search_field = QtWidgets.QLineEdit()
        self.search_field.setPlaceholderText("Filter Classifications...")
        self.has_images = QtWidgets.QCheckBox("Has Images")
        self.has_images.checkStateChanged.connect(self.on_has_images_toggle)
        search_layout.addWidget(self.search_field)
        search_layout.addWidget(self.has_images)
        classification_layout.addWidget(search_widget)

        self.classifications_list = QtWidgets.QListWidget()
        self.classifications_list.currentItemChanged.connect(
            self.on_classification_item_selected
        )
        classification_layout.addWidget(self.classifications_list)
        for key, value in sorted(
            self.local_api.get_classification_list().items(), key=lambda x: x[0].lower()
        ):
            item = QtWidgets.QListWidgetItem(self.classifications_list)
            records = [int(r) for r in value]
            item_widget = ClassifictionWidget(key, records, main_window=self)
            item.setSizeHint(item_widget.sizeHint())
            self.classifications_list.setItemWidget(item, item_widget)

        # Results column
        results_column = QtWidgets.QWidget()
        results_layout = QtWidgets.QVBoxLayout()
        results_column.setLayout(results_layout)
        columns_layout.addWidget(results_column)

        # Sorting (temp label)
        sorting_label = QtWidgets.QLabel("Sort By Date")
        results_layout.addWidget(sorting_label)
        self.results_list = QtWidgets.QListWidget()
        self.results_list.currentItemChanged.connect(self.on_result_item_selected)
        results_layout.addWidget(sorting_label)
        results_layout.addWidget(self.results_list)

        # Details column
        details_column = QtWidgets.QWidget()
        details_layout = QtWidgets.QGridLayout()
        details_column.setLayout(details_layout)
        columns_layout.addWidget(details_column)
        details_label = QtWidgets.QLabel("Details")
        details_layout.addWidget(details_label)

    def on_classification_item_selected(self, current, previous):
        self.statusBar().showMessage("Loading results...")

        # Clear existing results
        self.current_results = []
        self.results_list.clear()

        widget = self.classifications_list.itemWidget(current)

        for record in widget.filtered_record_ids[:80]:
            result = self.met_api.get_single_record(record)
            if result:
                self.current_results.append(result)
                pprint(result)

        self.populate_results()

    def on_result_item_selected(self, current, previous):
        pprint(current.data(QtCore.Qt.UserRole))

    def on_has_images_toggle(self):
        for i in range(self.classifications_list.count()):
            item = self.classifications_list.item(i)
            widget = self.classifications_list.itemWidget(item)

            if widget:
                widget.update_count()

    def populate_results(self):
        self.results_list.clear()
        sort_results = self.sort_results()

        for result in sort_results:
            item = QtWidgets.QListWidgetItem(self.results_list)
            item_widget = ResultWidget(result)
            item.setSizeHint(item_widget.sizeHint())
            self.results_list.setItemWidget(item, item_widget)
            item.setData(QtCore.Qt.UserRole, result)

        self.statusBar().showMessage(f"Loaded {len(sort_results)} results")

    def sort_results(self, direction="ascending"):
        return sorted(
            self.current_results,
            key=lambda x: x.get("objectBeginDate", 0),
            reverse=direction != "ascending",
        )
