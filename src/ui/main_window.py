from PySide6 import QtWidgets, QtCore
from PySide6.QtGui import Qt
from src.api.classification_index import ClassificationIndex
from src.api.met_api import MetAPI
from pprint import pprint


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None) -> None:
        super(MainWindow, self).__init__(parent)

        self.setWindowTitle("Met Browser")
        self.setMinimumSize(400, 300)
        self.local_api = ClassificationIndex()
        self.met_api = MetAPI()
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
        search_layout.addWidget(self.search_field)
        search_layout.addWidget(self.has_images)
        classification_layout.addWidget(search_widget)

        self.classifications_list = QtWidgets.QListWidget()
        self.classifications_list.currentItemChanged.connect(
            self.on_classification_item_selected
        )
        classification_layout.addWidget(self.classifications_list)
        for c in self.local_api.get_classification_list():
            item = QtWidgets.QListWidgetItem(c)
            self.classifications_list.addItem(item)

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
        target_records = self.local_api.get_records_in_classification(current.text())
        for record in target_records:
            result = self.met_api.get_single_record(record)
            pprint(result)
            item = QtWidgets.QListWidgetItem()
            item.setText(result.get("title"))
            item.setData(QtCore.Qt.UserRole, result)
            self.results_list.addItem(item)

    def on_result_item_selected(self, current, previous):
        pprint(current.data(QtCore.Qt.UserRole))
