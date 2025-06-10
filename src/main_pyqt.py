import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QStatusBar
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot

from .ui_main_window import Ui_MainWindow
from .app_logic import (BinanceLogic, ApiKeyMissingError, CustomNetworkError,
                        CustomExchangeError, AppLogicError, MarketEnvironment,
                        OrderPlacementError, InsufficientFundsError, InvalidOrderParamsError)
from .constants import ui_strings, error_messages
from .simulation_logic import calculer_iterations, SimulationError
from . import keyring_utils
import keyring # For keyring.get_keyring()
import keyring.errors # For NoKeyringError

class BalanceWorker(QThread):
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
        except (ApiKeyMissingError, CustomNetworkError, CustomExchangeError, AppLogicError) as e:
            self.error.emit(str(e))
        except Exception as e:
            self.error.emit(f"{error_messages.ERROR_UNEXPECTED}: {str(e)}")

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
        except Exception as e:
            self.error.emit(f"{error_messages.ERROR_UNEXPECTED}: {str(e)}")


class BinanceAppPyQt(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setStatusBar(QStatusBar(self)) # Add a status bar

        self.binance_logic = BinanceLogic()
        self.balance_worker_thread = None
        self.order_placement_worker_thread = None
        self.keyring_available = True

        # Keyring availability check and initial load
        try:
            keyring.get_keyring()
            self.keyring_available = True
            self.statusBar().showMessage(ui_strings.APP_NAME + ": Keyring initialisé.", 3000)
        except keyring.errors.NoKeyringError:
            self.keyring_available = False
            self.ui.saveApiKeysCheckBox.setEnabled(False)
            self.ui.saveApiKeysCheckBox.setToolTip(ui_strings.LABEL_KEYRING_UNAVAILABLE)
            self.statusBar().showMessage(ui_strings.LABEL_KEYRING_UNAVAILABLE, 5000)
            print(ui_strings.LABEL_KEYRING_UNAVAILABLE) # Console fallback

        # Connect signals for Balance Tab
        self.ui.fetchBalanceButton.clicked.connect(self.start_fetch_balance)
        self.ui.balanceEnvironmentComboBox.currentTextChanged.connect(self._load_api_keys_for_selected_env)
        self._load_api_keys_for_selected_env() # Load for initially selected env

        # Connect signals for Trade Tab
        self.ui.placeOrderButton.clicked.connect(self.start_place_order)
        self.ui.orderTypeComboBox.currentTextChanged.connect(self.on_order_type_changed)

        # Set initial state for price field for Trade Tab
        self.on_order_type_changed(self.ui.orderTypeComboBox.currentText())

        # Connect signals for Simulation Tab
        self.ui.simCalculerButton.clicked.connect(self.handle_simulation_calculation)

    def _get_selected_environment(self, comboBox_current_text: str) -> MarketEnvironment | None:
        env_text = comboBox_current_text
        if env_text == ui_strings.ENV_SPOT:
            return MarketEnvironment.SPOT
        elif env_text == ui_strings.ENV_FUTURES_LIVE:
            return MarketEnvironment.FUTURES_LIVE
        elif env_text == ui_strings.ENV_FUTURES_TESTNET:
            return MarketEnvironment.FUTURES_TESTNET
        return None

    @pyqtSlot()
    def _load_api_keys_for_selected_env(self):
        if not self.keyring_available:
            self.ui.saveApiKeysCheckBox.setEnabled(False) # Ensure it's disabled if called before __init__ check fully completes
            self.ui.saveApiKeysCheckBox.setChecked(False)
            return

        selected_env_text = self.ui.balanceEnvironmentComboBox.currentText()
        market_env = self._get_selected_environment(selected_env_text)

        if market_env:
            api_key, secret_key = keyring_utils.load_creds(market_env.value)
            if api_key and secret_key:
                self.ui.apiKeyLineEdit.setText(api_key)
                self.ui.secretKeyLineEdit.setText(secret_key)
                self.ui.saveApiKeysCheckBox.setChecked(True)
            else:
                self.ui.apiKeyLineEdit.clear()
                self.ui.secretKeyLineEdit.clear()
                self.ui.saveApiKeysCheckBox.setChecked(False)
            self.ui.saveApiKeysCheckBox.setEnabled(True) # Enable if keyring is available
        else:
            self.ui.apiKeyLineEdit.clear()
            self.ui.secretKeyLineEdit.clear()
            self.ui.saveApiKeysCheckBox.setChecked(False)
            # Keep checkbox enabled if keyring is available, user might select a valid env next
            self.ui.saveApiKeysCheckBox.setEnabled(self.keyring_available)


    @pyqtSlot()
    def start_fetch_balance(self):
        api_key = self.ui.apiKeyLineEdit.text().strip()
        secret_key = self.ui.secretKeyLineEdit.text().strip()

        market_env_text = self.ui.balanceEnvironmentComboBox.currentText()
        market_env = self._get_selected_environment(market_env_text)

        if market_env is None:
            self.ui.balanceValueLabel.setText(error_messages.ERROR_INVALID_ENVIRONMENT_SELECTED)
            return

        if not api_key or not secret_key:
            self.ui.balanceValueLabel.setText(error_messages.ERROR_API_KEYS_REQUIRED_UI)
            return

        # Save or delete keys based on checkbox state FOR THE CURRENTLY SELECTED ENVIRONMENT
        if self.keyring_available:
            if self.ui.saveApiKeysCheckBox.isChecked():
                if api_key and secret_key: # Don't save empty keys
                    keyring_utils.save_creds(market_env.value, api_key, secret_key)
            else:
                # If unchecked, delete previously stored keys for this environment
                keyring_utils.delete_creds(market_env.value)

        self.ui.fetchBalanceButton.setEnabled(False)
        self.ui.balanceValueLabel.setText(ui_strings.LABEL_LOADING)

        if self.balance_worker_thread and self.balance_worker_thread.isRunning():
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
        is_limit_order = order_type_text.upper() == ui_strings.ORDER_TYPE_LIMIT
        self.ui.priceLineEdit.setEnabled(is_limit_order)

        price_label_widget = self.ui.tradeFormLayout.labelForField(self.ui.priceLineEdit)
        if price_label_widget: # price_label_widget is self.ui.tradePriceLabel
            price_label_widget.setEnabled(is_limit_order)

        if not is_limit_order:
            self.ui.priceLineEdit.clear()

    @pyqtSlot()
    def start_place_order(self):
        api_key = self.ui.apiKeyLineEdit.text().strip()
        secret_key = self.ui.secretKeyLineEdit.text().strip()

        if not api_key or not secret_key:
            self.ui.tradeStatusLabel.setText(error_messages.ERROR_API_KEYS_REQUIRED_UI + " (depuis l'onglet Balance)")
            return

        trade_market_env_text = self.ui.tradeEnvironmentComboBox.currentText()
        market_env = self._get_selected_environment(trade_market_env_text)

        if market_env is None:
            self.ui.tradeStatusLabel.setText(error_messages.ERROR_INVALID_ENVIRONMENT_SELECTED)
            return

        symbol = self.ui.tradeSymbolLineEdit.text().strip()
        order_type = self.ui.orderTypeComboBox.currentText()
        side = self.ui.sideComboBox.currentText()
        amount_str = self.ui.amountLineEdit.text().strip()
        price_str = self.ui.priceLineEdit.text().strip()

        if not symbol:
            self.ui.tradeStatusLabel.setText(error_messages.ERROR_ORDER_SYMBOL_REQUIRED)
            return

        try:
            amount = float(amount_str)
            if amount <= 0:
                self.ui.tradeStatusLabel.setText(error_messages.ERROR_ORDER_AMOUNT_POSITIVE)
                return
        except ValueError:
            self.ui.tradeStatusLabel.setText(error_messages.ERROR_ORDER_AMOUNT_INVALID_NUMBER)
            return

        price = None
        if order_type.upper() == ui_strings.ORDER_TYPE_LIMIT:
            if not price_str:
                self.ui.tradeStatusLabel.setText(error_messages.ERROR_ORDER_PRICE_POSITIVE_LIMIT)
                return
            try:
                price = float(price_str)
                if price <= 0:
                    self.ui.tradeStatusLabel.setText(error_messages.ERROR_ORDER_PRICE_POSITIVE_LIMIT)
                    return
            except ValueError:
                self.ui.tradeStatusLabel.setText(error_messages.ERROR_ORDER_PRICE_INVALID_NUMBER)
                return

        self.ui.placeOrderButton.setEnabled(False)
        self.ui.tradeStatusLabel.setText(ui_strings.LABEL_SUBMITTING_ORDER)

        if self.order_placement_worker_thread and self.order_placement_worker_thread.isRunning():
            pass

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
        status_text = (f"{ui_strings.STATUS_ORDER_SUCCESS_PREFIX}{order_response.get('id', 'N/A')}"
                       f"{ui_strings.STATUS_ORDER_PARTIAL_INFO_SUFFIX}{order_response.get('status', 'N/A')}\n"
                       f"Symbol: {order_response.get('symbol')}, Side: {order_response.get('side')}, "
                       f"Amount: {order_response.get('amount')}")
        if order_response.get('price'):
            status_text += f", Price: {order_response.get('price')}"
        self.ui.tradeStatusLabel.setText(status_text)

    @pyqtSlot(str)
    def on_place_order_error(self, error_message: str):
        self.ui.tradeStatusLabel.setText(f"Erreur d'Ordre: {error_message}")

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
            balance_str = self.ui.simBalanceLineEdit.text().strip()
            prix_entree_str = self.ui.simPrixEntreeLineEdit.text().strip()
            prix_catastrophique_str = self.ui.simPrixCatastrophiqueLineEdit.text().strip()
            drop_percent_str = self.ui.simDropPercentLineEdit.text().strip()

            if not all([balance_str, prix_entree_str, prix_catastrophique_str, drop_percent_str]):
                self.ui.simResultsTextEdit.setText(error_messages.ERROR_ALL_SIM_FIELDS_REQUIRED)
                return

            try:
                balance = float(balance_str)
                prix_entree = float(prix_entree_str)
                prix_catastrophique = float(prix_catastrophique_str)
                drop_percent = float(drop_percent_str)
            except ValueError:
                self.ui.simResultsTextEdit.setText(error_messages.ERROR_SIM_NUMERIC_INPUT)
                return

            results_data = calculer_iterations(
                balance=balance,
                prix_entree=prix_entree,
                prix_catastrophique=prix_catastrophique,
                drop_percent=drop_percent
            )

            formatted_results = "\n".join(results_data.get("details_text", []))
            self.ui.simResultsTextEdit.setText(formatted_results)

        except SimulationError as sim_e:
            self.ui.simResultsTextEdit.setText(f"Erreur de Simulation: {sim_e}")
        except Exception as e:
            self.ui.simResultsTextEdit.setText(f"{error_messages.ERROR_UNEXPECTED_SIM_ISSUE}: {e}")
            # import traceback
            # print(traceback.format_exc()) # For debugging


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = BinanceAppPyQt()
    mainWindow.show()
    sys.exit(app.exec_())
