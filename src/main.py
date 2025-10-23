import sys
from PySide6 import QtWidgets
from src.ui.main_window import MainWindow


def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("macOS")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
