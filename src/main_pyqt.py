import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot

from .ui_main_window import Ui_MainWindow
from .app_logic import BinanceLogic, ApiKeyMissingError, CustomNetworkError, CustomExchangeError, AppLogicError

class Worker(QThread):
    """
    Worker thread for handling Binance API calls without freezing the UI.
    """
    success = pyqtSignal(float)
    error = pyqtSignal(str)

    def __init__(self, binance_logic: BinanceLogic, api_key: str, secret_key: str, parent=None):
        super().__init__(parent)
        self.binance_logic = binance_logic
        self.api_key = api_key
        self.secret_key = secret_key

    def run(self):
        """
        Executes the balance fetching logic.
        Emits 'success' with the balance or 'error' with a message.
        """
        try:
            balance = self.binance_logic.get_balance(self.api_key, self.secret_key)
            self.success.emit(balance)
        except ApiKeyMissingError as e: # Should be caught before starting thread, but as a safeguard
            self.error.emit(str(e))
        except CustomNetworkError as e:
            self.error.emit(str(e))
        except CustomExchangeError as e:
            self.error.emit(str(e))
        except AppLogicError as e:
            self.error.emit(str(e))
        except Exception as e: # Catch-all for any other unexpected error in the thread
            self.error.emit(f"An unexpected error occurred in worker: {str(e)}")


class BinanceAppPyQt(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.binance_logic = BinanceLogic()
        self.worker_thread = None # To keep a reference to the worker

        # Connect signals
        self.ui.fetchButton.clicked.connect(self.start_fetch_balance)

    @pyqtSlot()
    def start_fetch_balance(self):
        api_key = self.ui.apiKeyLineEdit.text().strip()
        secret_key = self.ui.secretKeyLineEdit.text().strip()

        if not api_key or not secret_key:
            self.ui.balanceValueLabel.setText("API Key and Secret Key are required.")
            # No need to disable/enable button here as it's a quick check
            return

        self.ui.fetchButton.setEnabled(False)
        self.ui.balanceValueLabel.setText("Loading...")

        # Ensure any previous thread is finished before starting a new one
        if self.worker_thread and self.worker_thread.isRunning():
            # Optionally, you might want to wait or terminate the previous thread
            # For simplicity here, we just let it run its course if it's somehow stuck
            # but a new one won't be started until this one is done with.
            # However, the button state handles this mostly.
            pass

        self.worker_thread = Worker(self.binance_logic, api_key, secret_key)
        self.worker_thread.success.connect(self.on_fetch_success)
        self.worker_thread.error.connect(self.on_fetch_error)
        # Re-enable button once the thread is done, regardless of success/failure
        self.worker_thread.finished.connect(lambda: self.ui.fetchButton.setEnabled(True))
        self.worker_thread.start()

    @pyqtSlot(float)
    def on_fetch_success(self, balance: float):
        self.ui.balanceValueLabel.setText(f"{balance:.2f} USDT")
        # The button is re-enabled by the worker's 'finished' signal connection

    @pyqtSlot(str)
    def on_fetch_error(self, error_message: str):
        self.ui.balanceValueLabel.setText(error_message)
        # The button is re-enabled by the worker's 'finished' signal connection

    def closeEvent(self, event):
        """Ensure worker thread is properly handled on close."""
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.quit() # Request termination
            self.worker_thread.wait() # Wait for it to finish
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = BinanceAppPyQt()
    mainWindow.show()
    sys.exit(app.exec_())
