from PySide6 import QtWidgets, QtCore
from src.api.classification_index import ClassificationIndex
from src.api.met_api import MetAPI
from pprint import pprint


class ResultWidget(QtWidgets.QWidget):
    def __init__(self, title, medium, parent=None):
        super().__init__(parent=parent)
        self.title = title
        self.medium = medium
        self.setup_ui()

    def setup_ui(self):
        main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(main_layout)

        title_label = QtWidgets.QLabel(self.title)
        font = title_label.font()
        font.setBold(True)
        title_label.setFont(font)

        medium_label = QtWidgets.QLabel(self.medium)

        main_layout.addWidget(title_label)
        main_layout.addWidget(medium_label)


class ClassifictionWidget(QtWidgets.QWidget):
    def __init__(self, classification, record_ids, main_window, parent=None):
        super().__init__(parent=parent)
        self.classification = classification
        self.record_ids = record_ids
        self.main_window = main_window
        self.setup_ui()

    @property
    def count(self):
        return len(self.filtered_record_ids)

    @property
    def filtered_record_ids(self):
        if self.main_window.has_images.isChecked():
            return list(
                set(self.main_window.records_with_images) & set(self.record_ids)
            )
        else:
            return self.record_ids

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
        self.records_with_images = self.met_api.get_all_records_with_images()
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
        self.results_list.clear()
        widget = self.classifications_list.itemWidget(current)
        # target_records = self.local_api.get_records_in_classification(current.text())
        for record in widget.filtered_record_ids[:80]:
            result = self.met_api.get_single_record(record)
            pprint(result)
            item = QtWidgets.QListWidgetItem(self.results_list)
            item_widget = ResultWidget(result.get("title"), result.get("medium"))
            item.setSizeHint(item_widget.sizeHint())
            self.results_list.setItemWidget(item, item_widget)
            item.setData(QtCore.Qt.UserRole, result)

    def on_result_item_selected(self, current, previous):
        pprint(current.data(QtCore.Qt.UserRole))

    def on_has_images_toggle(self):
        for i in range(self.classifications_list.count()):
            item = self.classifications_list.item(i)
            widget = self.classifications_list.itemWidget(item)

            if widget:
                widget.update_count()
