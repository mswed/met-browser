from typing import Dict, Optional
from PySide6 import QtGui, QtWidgets, QtCore
import requests


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

    def load_image_from_url(self, image_url: str) -> None:
        """
        Load an image into the label

        :param image_url: Url of image to load
        """
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
    """
    UI for a single record, shows title, artist, medium, department and work creation date
    """

    def __init__(self, data: Dict, parent: Optional[QtWidgets.QWidget] = None):
        """
        Initialize the widget

        :param data: Dictionary of record data
        :param parent: Parent widget
        """
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


class ClassificationWidget(QtWidgets.QWidget):
    """
    UI for displaying classification info Name and record count.
    """

    def __init__(
        self,
        classification: str,
        record_ids: list,
        main_window: QtWidgets.QMainWindow,
        parent: Optional[QtWidgets.QWidget] = None,
    ):
        """
        Initialize the widget

        :param classification: Classification name
        :param record_ids: List of records in the classification (based on local cache)
        :main_window: Pointer to the app's main UI so we can check its state
        :param parent: Parent widget
        """
        super().__init__(parent=parent)
        self.classification = classification
        self.record_ids = set(record_ids)
        self.main_window = main_window
        self.setup_ui()

    @property
    def count(self):
        """
        Number of records in the category (changes if we has_images is selected)
        """
        return len(self.filtered_record_ids)

    @property
    def filtered_record_ids(self):
        """
        Records in the category filtered if has_images is selected
        """
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
        font.setPointSize(9)
        classification_label.setFont(font)
        # Split long classifications into two lines
        classification_label.setWordWrap(True)
        classification_label.setMinimumHeight(40)
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
        """
        Update the UI with the current record count
        """
        if self.main_window.has_images.isChecked():
            self.count_label.setText(f"~{self.count}")
            self.count_label.setToolTip("API approximation - some items maybe exluded")
        else:
            self.count_label.setText(str(self.count))
