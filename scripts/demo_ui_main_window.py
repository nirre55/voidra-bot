from PyQt5.QtWidgets import QApplication, QMainWindow
from src.ui_main_window import Ui_MainWindow

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    main_window = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(main_window)
    main_window.show()
    sys.exit(app.exec_())
