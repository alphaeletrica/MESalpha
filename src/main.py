import sys
from PySide6.QtWidgets import QApplication
from gui.main_window import MainWindow
from database.db_handler import DatabaseHandler


def main():

    app = QApplication(sys.argv)

    db = DatabaseHandler()

    window = MainWindow(db)
    window.showMaximized()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()