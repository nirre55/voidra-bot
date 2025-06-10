import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot

from .ui_main_window import Ui_MainWindow
from .app_logic import (BinanceLogic, ApiKeyMissingError, CustomNetworkError,
                        CustomExchangeError, AppLogicError, MarketEnvironment,
                        OrderPlacementError, InsufficientFundsError, InvalidOrderParamsError)
from .simulation_logic import calculer_iterations, SimulationError

class BalanceWorker(QThread): # Renamed from Worker
    """
    Worker thread for handling Binance balance fetching without freezing the UI.
    """
    success = pyqtSignal(float)
    error = pyqtSignal(str)

    def __init__(self, binance_logic: BinanceLogic, api_key: str, secret_key: str, market_environment: MarketEnvironment, parent=None):
        super().__init__(parent)
        self.binance_logic = binance_logic
        self.api_key = api_key
        self.secret_key = secret_key
        self.market_environment = market_environment

    def run(self):
        """
        Executes the balance fetching logic.
        Emits 'success' with the balance or 'error' with a message.
        """
        try:
            balance = self.binance_logic.get_balance(self.api_key, self.secret_key, self.market_environment)
            self.success.emit(balance)
        except ApiKeyMissingError as e:
            self.error.emit(str(e))
        except CustomNetworkError as e:
            self.error.emit(str(e))
        except CustomExchangeError as e:
            self.error.emit(str(e))
        except AppLogicError as e:
            self.error.emit(str(e))
        except Exception as e:
            self.error.emit(f"An unexpected error occurred in balance worker: {str(e)}")

class OrderPlacementWorker(QThread):
    success = pyqtSignal(object)  # Emits the full order response dict
    error = pyqtSignal(str)

    def __init__(self, binance_logic: BinanceLogic, api_key: str, secret_key: str,
                 market_environment: MarketEnvironment, symbol: str, order_type: str,
                 side: str, amount: float, price: float = None, parent=None):
        super().__init__(parent)
        self.binance_logic = binance_logic
        self.api_key = api_key
        self.secret_key = secret_key
        self.market_environment = market_environment
        self.symbol = symbol
        self.order_type = order_type
        self.side = side
        self.amount = amount
        self.price = price

    def run(self):
        try:
            order_response = self.binance_logic.place_order(
                self.api_key, self.secret_key, self.market_environment,
                self.symbol, self.order_type, self.side, self.amount, self.price
            )
            self.success.emit(order_response)
        except (ApiKeyMissingError, InvalidOrderParamsError, InsufficientFundsError,
                OrderPlacementError, CustomNetworkError, AppLogicError) as e:
            self.error.emit(str(e))
        except Exception as e: # Catch any other unexpected error from logic or ccxt not caught by specific handlers
            self.error.emit(f"An unexpected error occurred in order worker: {str(e)}")


class BinanceAppPyQt(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.binance_logic = BinanceLogic()
        self.balance_worker_thread = None
        self.order_placement_worker_thread = None

        # Connect signals for Balance Tab
        self.ui.fetchBalanceButton.clicked.connect(self.start_fetch_balance)

        # Connect signals for Trade Tab
        self.ui.placeOrderButton.clicked.connect(self.start_place_order)
        self.ui.orderTypeComboBox.currentTextChanged.connect(self.on_order_type_changed)

        # Set initial state for price field
        self.on_order_type_changed(self.ui.orderTypeComboBox.currentText())

        # Connect signals for Simulation Tab
        self.ui.simCalculerButton.clicked.connect(self.handle_simulation_calculation)


    def _get_selected_environment(self, combo_box) -> MarketEnvironment | None:
        env_text = combo_box.currentText()
        try:
            # Convert "Futures Testnet" to "FUTURES_TESTNET" for enum lookup
            return MarketEnvironment[env_text.upper().replace(" ", "_")]
        except KeyError:
            return None

    @pyqtSlot()
    def start_fetch_balance(self):
        api_key = self.ui.apiKeyLineEdit.text().strip()
        secret_key = self.ui.secretKeyLineEdit.text().strip()

        market_env = self._get_selected_environment(self.ui.balanceEnvironmentComboBox)
        if market_env is None:
            self.ui.balanceValueLabel.setText("Error: Invalid environment selected.")
            return

        if not api_key or not secret_key:
            self.ui.balanceValueLabel.setText("API Key and Secret Key are required.")
            return

        self.ui.fetchBalanceButton.setEnabled(False)
        self.ui.balanceValueLabel.setText("Loading...")

        if self.balance_worker_thread and self.balance_worker_thread.isRunning():
            # Potentially handle or wait, for now, new request will queue if old one is slow (unlikely here)
            pass

        self.balance_worker_thread = BalanceWorker(self.binance_logic, api_key, secret_key, market_env)
        self.balance_worker_thread.success.connect(self.on_fetch_success)
        self.balance_worker_thread.error.connect(self.on_fetch_error)
        self.balance_worker_thread.finished.connect(lambda: self.ui.fetchBalanceButton.setEnabled(True))
        self.balance_worker_thread.start()

    @pyqtSlot(float)
    def on_fetch_success(self, balance: float):
        self.ui.balanceValueLabel.setText(f"{balance:.2f} USDT")

    @pyqtSlot(str)
    def on_fetch_error(self, error_message: str):
        self.ui.balanceValueLabel.setText(error_message)

    @pyqtSlot(str)
    def on_order_type_changed(self, order_type_text: str):
        is_limit_order = order_type_text.upper() == "LIMIT"
        self.ui.priceLineEdit.setEnabled(is_limit_order)
        # Assuming self.ui.priceLabel is defined in Ui_MainWindow (it should be via QFormLayout)
        # Find the QLabel associated with priceLineEdit in the QFormLayout
        price_label_widget = self.ui.tradeFormLayout.labelForField(self.ui.priceLineEdit)
        if price_label_widget:
            price_label_widget.setEnabled(is_limit_order)

        if not is_limit_order:
            self.ui.priceLineEdit.clear()

    @pyqtSlot()
    def start_place_order(self):
        api_key = self.ui.apiKeyLineEdit.text().strip() # Using same API keys for now
        secret_key = self.ui.secretKeyLineEdit.text().strip()

        if not api_key or not secret_key:
            self.ui.tradeStatusLabel.setText("Error: API Key and Secret Key are required (from Balance tab).")
            return

        market_env = self._get_selected_environment(self.ui.tradeEnvironmentComboBox)
        if market_env is None:
            self.ui.tradeStatusLabel.setText("Error: Invalid environment selected for trade.")
            return

        symbol = self.ui.symbolLineEdit.text().strip()
        order_type = self.ui.orderTypeComboBox.currentText()
        side = self.ui.sideComboBox.currentText()
        amount_str = self.ui.amountLineEdit.text().strip()
        price_str = self.ui.priceLineEdit.text().strip()

        # Input Validation
        if not symbol:
            self.ui.tradeStatusLabel.setText("Error: Symbol is required.")
            return

        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError("Amount must be positive.")
        except ValueError:
            self.ui.tradeStatusLabel.setText("Error: Invalid amount. Must be a positive number.")
            return

        price = None
        if order_type.upper() == "LIMIT":
            try:
                price = float(price_str)
                if price <= 0:
                    raise ValueError("Price must be positive for LIMIT orders.")
            except ValueError:
                self.ui.tradeStatusLabel.setText("Error: Invalid price. Must be a positive number for LIMIT orders.")
                return

        self.ui.placeOrderButton.setEnabled(False)
        self.ui.tradeStatusLabel.setText("Submitting order...")

        if self.order_placement_worker_thread and self.order_placement_worker_thread.isRunning():
            pass # Similar handling as balance worker

        self.order_placement_worker_thread = OrderPlacementWorker(
            self.binance_logic, api_key, secret_key, market_env,
            symbol, order_type, side, amount, price
        )
        self.order_placement_worker_thread.success.connect(self.on_place_order_success)
        self.order_placement_worker_thread.error.connect(self.on_place_order_error)
        self.order_placement_worker_thread.finished.connect(lambda: self.ui.placeOrderButton.setEnabled(True))
        self.order_placement_worker_thread.start()

    @pyqtSlot(object)
    def on_place_order_success(self, order_response: dict):
        # Example: Displaying more info. Adjust formatting as needed.
        info_str = f"ID: {order_response.get('id')}, Status: {order_response.get('status')}, Symbol: {order_response.get('symbol')}, Side: {order_response.get('side')}, Amount: {order_response.get('amount')}"
        if order_response.get('price'):
             info_str += f", Price: {order_response.get('price')}"
        self.ui.tradeStatusLabel.setText(f"Order Placed Successfully!\n{info_str}")

    @pyqtSlot(str)
    def on_place_order_error(self, error_message: str):
        self.ui.tradeStatusLabel.setText(f"Order Error: {error_message}")

    def closeEvent(self, event):
        """Ensure worker threads are properly handled on close."""
        if hasattr(self, 'balance_worker_thread') and self.balance_worker_thread and self.balance_worker_thread.isRunning():
            self.balance_worker_thread.quit()
            self.balance_worker_thread.wait()

        if hasattr(self, 'order_placement_worker_thread') and self.order_placement_worker_thread and self.order_placement_worker_thread.isRunning():
            self.order_placement_worker_thread.quit()
            self.order_placement_worker_thread.wait()
        event.accept()

    @pyqtSlot()
    def handle_simulation_calculation(self):
        try:
            # 1. Retrieve input values from QLineEdits
            balance_str = self.ui.simBalanceLineEdit.text().strip()
            prix_entree_str = self.ui.simPrixEntreeLineEdit.text().strip()
            prix_catastrophique_str = self.ui.simPrixCatastrophiqueLineEdit.text().strip()
            drop_percent_str = self.ui.simDropPercentLineEdit.text().strip()

            # 2. Validate and convert to float (basic validation)
            if not all([balance_str, prix_entree_str, prix_catastrophique_str, drop_percent_str]):
                self.ui.simResultsTextEdit.setText("Erreur: Tous les champs doivent être remplis.")
                return

            try:
                balance = float(balance_str)
                prix_entree = float(prix_entree_str)
                prix_catastrophique = float(prix_catastrophique_str)
                drop_percent = float(drop_percent_str)
            except ValueError:
                self.ui.simResultsTextEdit.setText("Erreur: Les entrées numériques doivent être des nombres valides (ex: 1000 ou 0.5).")
                return

            # 3. Call the simulation logic function
            results_data = calculer_iterations(
                balance=balance,
                prix_entree=prix_entree,
                prix_catastrophique=prix_catastrophique,
                drop_percent=drop_percent
            )

            # 4. Format and display results
            formatted_results = "\n".join(results_data.get("details_text", []))
            self.ui.simResultsTextEdit.setText(formatted_results)

        except SimulationError as sim_e:
            self.ui.simResultsTextEdit.setText(f"Erreur de Simulation: {sim_e}")
        except Exception as e:
            self.ui.simResultsTextEdit.setText(f"Une erreur inattendue est survenue: {e}")
            # import traceback
            # print(traceback.format_exc()) # For debugging


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = BinanceAppPyQt()
    mainWindow.show()
    sys.exit(app.exec_())
