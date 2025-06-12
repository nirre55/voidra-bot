import sys
import logging
from PyQt5.QtWidgets import QApplication, QMainWindow, QStatusBar
from PyQt5.QtCore import pyqtSlot
from typing import Optional

from .ui_main_window import Ui_MainWindow
from .app_logic import BinanceLogic, MarketEnvironment
from .constants import ui_strings, error_messages
from .simulation_logic import calculer_iterations, SimulationError
from . import keyring_utils
from .controllers.worker_controller import WorkerController
from .utils.market_utils import MarketUtils
import keyring
import keyring.errors

class BinanceAppPyQt(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self._status_bar = QStatusBar(self)
        self.setStatusBar(self._status_bar)

        self.binance_logic = BinanceLogic()
        self.worker_controller = WorkerController(self.binance_logic)
        self.last_simulation_dca_levels = None
        self.original_simulation_dca_levels = None
        self.keyring_available = True

        try:
            keyring.get_keyring()
            self.keyring_available = True
            self._status_bar.showMessage(ui_strings.APP_NAME + ": Keyring initialisé.", 3000)
        except keyring.errors.NoKeyringError:
            self.keyring_available = False
            self.ui.saveApiKeysCheckBox.setEnabled(False)
            self.ui.saveApiKeysCheckBox.setToolTip(ui_strings.LABEL_KEYRING_UNAVAILABLE)
            self._status_bar.showMessage(ui_strings.LABEL_KEYRING_UNAVAILABLE, 5000)
            logging.warning(ui_strings.LABEL_KEYRING_UNAVAILABLE)

        # Connect signals for Balance Tab
        self.ui.fetchBalanceButton.clicked.connect(self.start_fetch_balance)
        self.ui.globalEnvironmentComboBox.currentTextChanged.connect(self._load_api_keys_for_selected_env)
        self._load_api_keys_for_selected_env()

        # Connect signals for Trade Tab
        self.ui.placeOrderButton.clicked.connect(self.start_place_order)
        self.ui.orderTypeComboBox.currentTextChanged.connect(self.on_order_type_changed)
        self.on_order_type_changed(self.ui.orderTypeComboBox.currentText())

        # Connect signals for Simulation Tab
        self.ui.simCalculerButton.clicked.connect(self.handle_simulation_calculation)

        # Connect signals for DCA Orders Tab
        self.ui.tabWidget.setTabText(self.ui.tabWidget.indexOf(self.ui.dcaOrdersTab), ui_strings.TAB_DCA_ORDERS)
        self.ui.dcaSymbolDisplayLabel.setText(ui_strings.LABEL_DCA_SYMBOL)
        self.ui.dcaSymbolValueLabel.setText(ui_strings.LABEL_DCA_SYMBOL_DEFAULT)
        self.ui.dcaPlaceOrdersButton.setText(ui_strings.BUTTON_PLACE_DCA_ORDERS_NEW_TAB)
        self.ui.dcaStatusLabel.setText(ui_strings.LABEL_DCA_STATUS_READY)
        self.ui.dcaLoadDataButton.setText(ui_strings.BUTTON_LOAD_DCA_DATA)

        self.ui.dcaLoadDataButton.clicked.connect(self._load_dca_data_to_tab)
        self.ui.dcaPlaceOrdersButton.clicked.connect(self.start_place_dca_orders_from_dca_tab)

        # Initial states for DCA Orders Tab
        self.ui.dcaPlaceOrdersButton.setEnabled(False)
        self.ui.dcaSimResultsTextEdit.setText(ui_strings.LABEL_DCA_NO_SIMULATION_DATA_LOADED)
        self.ui.dcaSymbolValueLabel.setText(ui_strings.LABEL_DCA_SYMBOL_DEFAULT)
        self.ui.dcaLeverageLineEdit.setText("20")

        # Connect worker controller signals
        self.worker_controller.balance_success.connect(self.on_fetch_success)
        self.worker_controller.balance_error.connect(self.on_fetch_error)
        self.worker_controller.balance_finished.connect(lambda: self.ui.fetchBalanceButton.setEnabled(True))

        self.worker_controller.order_success.connect(self.on_place_order_success)
        self.worker_controller.order_error.connect(self.on_place_order_error)
        self.worker_controller.order_finished.connect(lambda: self.ui.placeOrderButton.setEnabled(True))

        self.worker_controller.dca_order_attempt_finished.connect(self._on_dca_tab_order_attempt_finished)
        self.worker_controller.dca_batch_finished.connect(self._on_dca_tab_batch_finished)
        self.worker_controller.dca_batch_error.connect(self._on_dca_tab_batch_error)

        # Connect simulation state clearing signals
        self.ui.simBalanceLineEdit.textChanged.connect(self._clear_dca_simulation_state)
        self.ui.simPrixEntreeLineEdit.textChanged.connect(self._clear_dca_simulation_state)
        self.ui.simPrixCatastrophiqueLineEdit.textChanged.connect(self._clear_dca_simulation_state)
        self.ui.simDropPercentLineEdit.textChanged.connect(self._clear_dca_simulation_state)
        self.ui.simSymbolComboBox.currentTextChanged.connect(self._clear_dca_simulation_state)

    @pyqtSlot()
    def _load_api_keys_for_selected_env(self):
        if not self.keyring_available:
            self.ui.saveApiKeysCheckBox.setEnabled(False)
            self.ui.saveApiKeysCheckBox.setChecked(False)
            return

        selected_env_text = self.ui.globalEnvironmentComboBox.currentText()
        market_env = MarketUtils.get_environment_from_text(selected_env_text)

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
            self.ui.saveApiKeysCheckBox.setEnabled(True)
        else:
            self.ui.apiKeyLineEdit.clear()
            self.ui.secretKeyLineEdit.clear()
            self.ui.saveApiKeysCheckBox.setChecked(False)
            self.ui.saveApiKeysCheckBox.setEnabled(self.keyring_available)

    @pyqtSlot()
    def start_fetch_balance(self):
        api_key = self.ui.apiKeyLineEdit.text().strip()
        secret_key = self.ui.secretKeyLineEdit.text().strip()

        market_env_text = self.ui.globalEnvironmentComboBox.currentText()
        market_env = MarketUtils.get_environment_from_text(market_env_text)

        if market_env is None:
            self.ui.balanceValueLabel.setText(error_messages.ERROR_INVALID_ENVIRONMENT_SELECTED)
            return

        is_valid, error_msg = MarketUtils.validate_api_keys(api_key, secret_key)
        if not is_valid:
            self.ui.balanceValueLabel.setText(error_msg)
            return

        if self.keyring_available:
            if self.ui.saveApiKeysCheckBox.isChecked():
                if api_key and secret_key:
                    keyring_utils.save_creds(market_env.value, api_key, secret_key)
            else:
                keyring_utils.delete_creds(market_env.value)

        self.ui.fetchBalanceButton.setEnabled(False)
        self.ui.balanceValueLabel.setText(ui_strings.LABEL_LOADING)

        self.worker_controller.start_fetch_balance(api_key, secret_key, market_env)

    @pyqtSlot(float)
    def on_fetch_success(self, balance: float):
        self.ui.balanceValueLabel.setText(f"{round(balance, 2):.2f} USDT")

    @pyqtSlot(str)
    def on_fetch_error(self, error_message: str):
        self.ui.balanceValueLabel.setText(error_message)

    @pyqtSlot(str)
    def on_order_type_changed(self, order_type_text: str):
        is_limit_order = order_type_text.upper() == ui_strings.ORDER_TYPE_LIMIT
        self.ui.priceLineEdit.setEnabled(is_limit_order)

        price_label_widget = self.ui.tradeFormLayout.labelForField(self.ui.priceLineEdit)
        if price_label_widget:
            price_label_widget.setEnabled(is_limit_order)

        if not is_limit_order:
            self.ui.priceLineEdit.clear()

    @pyqtSlot()
    def start_place_order(self):
        api_key = self.ui.apiKeyLineEdit.text().strip()
        secret_key = self.ui.secretKeyLineEdit.text().strip()

        is_valid, error_msg = MarketUtils.validate_api_keys(api_key, secret_key)
        if not is_valid:
            self.ui.tradeStatusLabel.setText(f"{error_msg} (depuis l'onglet Balance)")
            return

        trade_market_env_text = self.ui.globalEnvironmentComboBox.currentText()
        market_env = MarketUtils.get_environment_from_text(trade_market_env_text)

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
                self.ui.tradeStatusLabel.setText(error_messages.PARAM_AMOUNT_MUST_BE_POSITIVE)
                return
        except ValueError:
            self.ui.tradeStatusLabel.setText(error_messages.ERROR_ORDER_AMOUNT_INVALID_NUMBER)
            return

        price = None
        if order_type.upper() == ui_strings.ORDER_TYPE_LIMIT:
            if not price_str:
                self.ui.tradeStatusLabel.setText(error_messages.PARAM_PRICE_MUST_BE_POSITIVE_LIMIT)
                return
            try:
                price = float(price_str)
                if price <= 0:
                    self.ui.tradeStatusLabel.setText(error_messages.PARAM_PRICE_MUST_BE_POSITIVE_LIMIT)
                    return
            except ValueError:
                self.ui.tradeStatusLabel.setText(error_messages.ERROR_ORDER_PRICE_INVALID_NUMBER)
                return

        self.ui.placeOrderButton.setEnabled(False)
        self.ui.tradeStatusLabel.setText(ui_strings.LABEL_SUBMITTING_ORDER)

        self.worker_controller.start_place_order(
            api_key, secret_key, market_env,
            symbol, order_type, side, amount, price
        )

    @pyqtSlot(object)
    def on_place_order_success(self, order_response: dict):
        status_text = (f"{ui_strings.STATUS_ORDER_SUCCESS_PREFIX}{order_response.get('id', 'N/A')}"
                       f"{ui_strings.STATUS_ORDER_PARTIAL_INFO_SUFFIX}{order_response.get('status', 'N/A')}\n"
                       f"Symbol: {order_response.get('symbol')}, Side: {order_response.get('side')}, "
                       f"Amount: {round(float(order_response.get('amount', 0)), 2):.2f}")
        if order_response.get('price'):
            status_text += f", Price: {round(float(order_response.get('price', 0)), 2):.2f}"
        self.ui.tradeStatusLabel.setText(status_text)

    @pyqtSlot(str)
    def on_place_order_error(self, error_message: str):
        self.ui.tradeStatusLabel.setText(f"Erreur d'Ordre: {error_message}")

    @pyqtSlot()
    def _clear_dca_simulation_state(self):
        if self.last_simulation_dca_levels is not None:
            self.last_simulation_dca_levels = None
            self.original_simulation_dca_levels = None

        self.ui.dcaSymbolValueLabel.setText(ui_strings.LABEL_DCA_SYMBOL_DEFAULT)
        self.ui.dcaSimResultsTextEdit.setText(ui_strings.DCA_TAB_DATA_CLEARED)
        self.ui.dcaPlaceOrdersButton.setEnabled(False)
        self.ui.dcaStatusLabel.setText(ui_strings.DCA_TAB_DATA_CLEARED)

    @pyqtSlot()
    def _load_dca_data_to_tab(self):
        self.ui.dcaSimResultsTextEdit.clear()
        if self.original_simulation_dca_levels:
            current_sim_symbol = self.ui.simSymbolComboBox.currentText()
            self.ui.dcaSymbolValueLabel.setText(current_sim_symbol if current_sim_symbol else ui_strings.LABEL_DCA_SYMBOL_DEFAULT)

            try:
                leverage = int(self.ui.dcaLeverageLineEdit.text().strip())
            except ValueError:
                leverage = 1

            self.ui.dcaSimResultsTextEdit.append(ui_strings.DCA_TAB_SIMULATION_DATA_HEADER + "\n")
            
            self.last_simulation_dca_levels = [
                {
                    'price': level['price'],
                    'amount': float(level['amount']) * leverage
                }
                for level in self.original_simulation_dca_levels
            ]

            for i, level in enumerate(self.last_simulation_dca_levels):
                level_text = f"Niveau {i+1}: Prix: {round(float(level['price']), 2):.2f}, Montant: {round(float(level['amount']), 2):.2f} (x{leverage})"
                self.ui.dcaSimResultsTextEdit.append(level_text)

            self.ui.dcaPlaceOrdersButton.setEnabled(True)
            self.ui.dcaStatusLabel.setText(ui_strings.LABEL_DCA_STATUS_READY)
        else:
            self.ui.dcaSymbolValueLabel.setText(ui_strings.LABEL_DCA_SYMBOL_DEFAULT)
            self.ui.dcaSimResultsTextEdit.setText(ui_strings.LABEL_DCA_NO_SIMULATION_DATA_LOADED)
            self.ui.dcaPlaceOrdersButton.setEnabled(False)
            self.ui.dcaStatusLabel.setText(ui_strings.LABEL_DCA_NO_SIMULATION_DATA_LOADED)

    @pyqtSlot()
    def handle_simulation_calculation(self):
        self.ui.simResultsTextEdit.clear()
        self._clear_dca_simulation_state()

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

            if results_data and results_data.get('nombre_total_iterations', 0) > 0 and \
               'prix_iterations' in results_data and 'quantites_par_iteration' in results_data:
                self.original_simulation_dca_levels = []
                for i in range(len(results_data['prix_iterations'])):
                    self.original_simulation_dca_levels.append({
                        'price': results_data['prix_iterations'][i],
                        'amount': results_data['quantites_par_iteration'][i]
                    })
                self.last_simulation_dca_levels = self.original_simulation_dca_levels.copy()
            else:
                self.original_simulation_dca_levels = None
                self.last_simulation_dca_levels = None

        except SimulationError as sim_e:
            self.ui.simResultsTextEdit.setText(f"Erreur de Simulation: {sim_e}")
        except Exception as e:
            self.ui.simResultsTextEdit.setText(f"{error_messages.ERROR_UNEXPECTED_SIM_ISSUE}: {e}")

    @pyqtSlot()
    def start_place_dca_orders_from_dca_tab(self):
        self.ui.dcaStatusLabel.setText(ui_strings.DCA_TAB_ORDERS_SUBMITTING)
        self.ui.dcaSimResultsTextEdit.append("\n" + ui_strings.DCA_TAB_ORDERS_SUBMITTING)

        margin_mode_str = self.ui.dcaMergeModeComboBox.currentText()
        leverage_str = self.ui.dcaLeverageLineEdit.text().strip()
        leverage_int = 0

        if not leverage_str:
            self.ui.dcaStatusLabel.setText(ui_strings.ERROR_LEVERAGE_INVALID_NUMBER)
            self.ui.dcaSimResultsTextEdit.append(ui_strings.ERROR_LEVERAGE_INVALID_NUMBER)
            self.ui.dcaPlaceOrdersButton.setEnabled(True)
            return
        try:
            leverage_int = int(leverage_str)
        except ValueError:
            self.ui.dcaStatusLabel.setText(ui_strings.ERROR_LEVERAGE_INVALID_NUMBER)
            self.ui.dcaSimResultsTextEdit.append(ui_strings.ERROR_LEVERAGE_INVALID_NUMBER)
            self.ui.dcaPlaceOrdersButton.setEnabled(True)
            return

        if not (1 <= leverage_int <= 100):
            self.ui.dcaStatusLabel.setText(ui_strings.ERROR_LEVERAGE_OUT_OF_RANGE)
            self.ui.dcaSimResultsTextEdit.append(ui_strings.ERROR_LEVERAGE_OUT_OF_RANGE)
            self.ui.dcaPlaceOrdersButton.setEnabled(True)
            return

        api_key = self.ui.apiKeyLineEdit.text().strip()
        secret_key = self.ui.secretKeyLineEdit.text().strip()

        is_valid, error_msg = MarketUtils.validate_api_keys(api_key, secret_key)
        if not is_valid:
            self.ui.dcaStatusLabel.setText(error_msg)
            self.ui.dcaSimResultsTextEdit.append(error_msg)
            return

        dca_tab_env_text = self.ui.globalEnvironmentComboBox.currentText()
        market_env = MarketUtils.get_environment_from_text(dca_tab_env_text)
        if market_env is None:
            err_msg = error_messages.ERROR_INVALID_ENVIRONMENT_SELECTED
            self.ui.dcaStatusLabel.setText(err_msg)
            self.ui.dcaSimResultsTextEdit.append(err_msg)
            return

        dca_symbol = self.ui.dcaSymbolValueLabel.text()
        if not dca_symbol or dca_symbol == ui_strings.LABEL_DCA_SYMBOL_DEFAULT:
            err_msg = error_messages.ERROR_ORDER_SYMBOL_REQUIRED
            self.ui.dcaStatusLabel.setText(err_msg)
            self.ui.dcaSimResultsTextEdit.append(err_msg)
            return

        if not self.last_simulation_dca_levels:
            err_msg = ui_strings.LABEL_DCA_NO_SIMULATION_DATA_LOADED
            self.ui.dcaStatusLabel.setText(err_msg)
            self.ui.dcaSimResultsTextEdit.append(err_msg)
            return

        self.ui.dcaPlaceOrdersButton.setEnabled(False)

        self.worker_controller.start_place_dca_orders(
            api_key, secret_key, market_env,
            dca_symbol, self.last_simulation_dca_levels,
            margin_mode_str, leverage_int
        )

    @pyqtSlot(int, str, bool, object)
    def _on_dca_tab_order_attempt_finished(self, level_idx, symbol, success, result_obj):
        if success:
            order_response = result_obj
            msg = ui_strings.DCA_TAB_ORDER_LEVEL_SUCCESS.format(
                level=level_idx + 1,
                symbol=symbol,
                order_id=order_response.get('id', 'N/A'),
                status=order_response.get('status', 'N/A')
            )
        else:
            error_detail = str(result_obj)
            msg = ui_strings.DCA_TAB_ORDER_LEVEL_ERROR.format(
                level=level_idx + 1,
                symbol=symbol,
                error=error_detail
            )
        self.ui.dcaSimResultsTextEdit.append(msg)
        self.ui.dcaStatusLabel.setText(msg)
        cursor = self.ui.dcaSimResultsTextEdit.textCursor()
        cursor.movePosition(cursor.End)
        self.ui.dcaSimResultsTextEdit.setTextCursor(cursor)

    @pyqtSlot(str)
    def _on_dca_tab_batch_error(self, error_message: str):
        self.ui.dcaSimResultsTextEdit.append(f"\n{error_message}")
        self.ui.dcaStatusLabel.setText(error_message)
        self.ui.dcaPlaceOrdersButton.setEnabled(True)

    @pyqtSlot(str)
    def _on_dca_tab_batch_finished(self, summary_message):
        final_msg = f"{ui_strings.DCA_TAB_BATCH_COMPLETE} {summary_message}"
        self.ui.dcaSimResultsTextEdit.append(f"\n{final_msg}")
        self.ui.dcaStatusLabel.setText(final_msg)
        self.ui.dcaPlaceOrdersButton.setEnabled(True)
        cursor = self.ui.dcaSimResultsTextEdit.textCursor()
        cursor.movePosition(cursor.End)
        self.ui.dcaSimResultsTextEdit.setTextCursor(cursor)

    def closeEvent(self, event):
        """Assure que les workers sont correctement arrêtés à la fermeture."""
        self.worker_controller.stop_all_workers()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = BinanceAppPyQt()
    mainWindow.show()
    sys.exit(app.exec_())
