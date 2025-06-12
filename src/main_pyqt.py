import sys
import time # Required for BatchDcaOrderWorker
import logging
from PyQt5.QtWidgets import QApplication, QMainWindow, QStatusBar
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot

from .ui_main_window import Ui_MainWindow
from .app_logic import (BinanceLogic, ApiKeyMissingError, CustomNetworkError,
                        CustomExchangeError, AppLogicError, MarketEnvironment,
                        OrderPlacementError, InsufficientFundsError, InvalidOrderParamsError)
from .constants import ui_strings, error_messages
from .simulation_logic import calculer_iterations, SimulationError
from . import keyring_utils
import keyring
import keyring.errors

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
        try:
            balance = self.binance_logic.get_balance(self.api_key, self.secret_key, self.market_environment)
            self.success.emit(balance)
        except (ApiKeyMissingError, CustomNetworkError, CustomExchangeError, AppLogicError) as e:
            self.error.emit(str(e))
        except Exception as e:
            self.error.emit(f"{error_messages.ERROR_UNEXPECTED}: {str(e)}")

class OrderPlacementWorker(QThread):
    success = pyqtSignal(object)
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

class BatchDcaOrderWorker(QThread):
    order_attempt_finished = pyqtSignal(int, str, bool, object)
    batch_processing_finished = pyqtSignal(str)

    def __init__(self, binance_logic, api_key, secret_key, market_env,
                 symbol_str, dca_levels_data, margin_mode: str, leverage: int, parent=None):
        super().__init__(parent)
        self.binance_logic = binance_logic
        self.api_key = api_key
        self.secret_key = secret_key
        self.market_env = market_env
        self.symbol_str = symbol_str
        self.dca_levels_data = dca_levels_data # List of {'price': p, 'amount': q}
        self.margin_mode = margin_mode
        self.leverage = leverage
        self._is_running = True

    def run(self):
        if not self.dca_levels_data:
            self.batch_processing_finished.emit(ui_strings.DCA_NO_SIMULATION_RESULTS)
            return

        for i, level_data in enumerate(self.dca_levels_data):
            if not self._is_running:
                self.batch_processing_finished.emit("Traitement DCA annulé par l'utilisateur.")
                return

            price = level_data['price']
            amount = level_data['amount']

            # Basic check, exchange will do more precise validation
            # Consider adding minimum order size checks here if known for the exchange/symbol
            if amount <= 0 or price <= 0:
                self.order_attempt_finished.emit(i, self.symbol_str, False,
                                                 error_messages.PARAM_AMOUNT_MUST_BE_POSITIVE if amount <=0 else error_messages.PARAM_PRICE_MUST_BE_POSITIVE_LIMIT)
                continue
            try:
                order_response = self.binance_logic.place_order(
                    api_key=self.api_key, secret_key=self.secret_key, market_environment=self.market_env,
                    symbol=self.symbol_str, order_type=ui_strings.ORDER_TYPE_LIMIT, side=ui_strings.SIDE_BUY, # Assuming DCA is LIMIT BUY
                    amount=amount, price=price,
                    margin_mode=self.margin_mode, leverage=self.leverage # Pass new params
                )
                self.order_attempt_finished.emit(i, self.symbol_str, True, order_response)
            except Exception as e:
                self.order_attempt_finished.emit(i, self.symbol_str, False, str(e))

            if i < len(self.dca_levels_data) - 1 and self._is_running: # Don't sleep after the last one or if stopped
                time.sleep(0.2) # Small delay between order attempts

        if self._is_running:
            self.batch_processing_finished.emit(ui_strings.DCA_BATCH_COMPLETE)

    def stop(self):
        self._is_running = False


class BinanceAppPyQt(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setStatusBar(QStatusBar(self))

        self.binance_logic = BinanceLogic()
        self.balance_worker_thread = None
        self.order_placement_worker_thread = None
        self.batch_dca_worker_thread = None # For BatchDcaOrderWorker
        self.last_simulation_dca_levels = None
        self.keyring_available = True

        try:
            keyring.get_keyring()
            self.keyring_available = True
            self.statusBar().showMessage(ui_strings.APP_NAME + ": Keyring initialisé.", 3000)
        except keyring.errors.NoKeyringError:
            self.keyring_available = False
            self.ui.saveApiKeysCheckBox.setEnabled(False)
            self.ui.saveApiKeysCheckBox.setToolTip(ui_strings.LABEL_KEYRING_UNAVAILABLE)
            self.statusBar().showMessage(ui_strings.LABEL_KEYRING_UNAVAILABLE, 5000)
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
        # self.ui.simPlaceDcaOrdersButton.clicked.connect(self.start_place_dca_orders) # Button removed from UI

        # Connect signals for DCA Orders Tab
        self.ui.tabWidget.setTabText(self.ui.tabWidget.indexOf(self.ui.dcaOrdersTab), ui_strings.TAB_DCA_ORDERS)
        self.ui.dcaSymbolDisplayLabel.setText(ui_strings.LABEL_DCA_SYMBOL) # Already set in ui_strings but good practice
        self.ui.dcaSymbolValueLabel.setText(ui_strings.LABEL_DCA_SYMBOL_DEFAULT)
        self.ui.dcaPlaceOrdersButton.setText(ui_strings.BUTTON_PLACE_DCA_ORDERS_NEW_TAB)
        self.ui.dcaStatusLabel.setText(ui_strings.LABEL_DCA_STATUS_READY)
        self.ui.dcaLoadDataButton.setText(ui_strings.BUTTON_LOAD_DCA_DATA) # Ensure text is set if not by ui_strings in .ui

        self.ui.dcaLoadDataButton.clicked.connect(self._load_dca_data_to_tab)
        self.ui.dcaPlaceOrdersButton.clicked.connect(self.start_place_dca_orders_from_dca_tab)

        # Initial states for DCA Orders Tab
        self.ui.dcaPlaceOrdersButton.setEnabled(False)
        self.ui.dcaSimResultsTextEdit.setText(ui_strings.LABEL_DCA_NO_SIMULATION_DATA_LOADED)
        self.ui.dcaSymbolValueLabel.setText(ui_strings.LABEL_DCA_SYMBOL_DEFAULT)
        self.ui.dcaLeverageLineEdit.setText("20") # Default leverage


        self.ui.simBalanceLineEdit.textChanged.connect(self._clear_dca_simulation_state)
        self.ui.simPrixEntreeLineEdit.textChanged.connect(self._clear_dca_simulation_state)
        self.ui.simPrixCatastrophiqueLineEdit.textChanged.connect(self._clear_dca_simulation_state)
        self.ui.simDropPercentLineEdit.textChanged.connect(self._clear_dca_simulation_state)
        self.ui.simSymbolComboBox.currentTextChanged.connect(self._clear_dca_simulation_state)

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
            self.ui.saveApiKeysCheckBox.setEnabled(False)
            self.ui.saveApiKeysCheckBox.setChecked(False)
            return

        selected_env_text = self.ui.globalEnvironmentComboBox.currentText()
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
        market_env = self._get_selected_environment(market_env_text)

        if market_env is None:
            self.ui.balanceValueLabel.setText(error_messages.ERROR_INVALID_ENVIRONMENT_SELECTED)
            return

        if not api_key or not secret_key:
            self.ui.balanceValueLabel.setText(error_messages.ERROR_API_KEYS_REQUIRED_UI)
            return

        if self.keyring_available:
            if self.ui.saveApiKeysCheckBox.isChecked():
                if api_key and secret_key:
                    keyring_utils.save_creds(market_env.value, api_key, secret_key)
            else:
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
        if price_label_widget:
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

        trade_market_env_text = self.ui.globalEnvironmentComboBox.currentText()
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

    @pyqtSlot()
    def _clear_dca_simulation_state(self):
        # Clear data related to the simulation calculation
        if self.last_simulation_dca_levels is not None:
            self.last_simulation_dca_levels = None
            # self.ui.simPlaceDcaOrdersButton.setEnabled(False) # Button is removed

        # Update DCA Orders Tab UI to reflect cleared/invalidated data
        self.ui.dcaSymbolValueLabel.setText(ui_strings.LABEL_DCA_SYMBOL_DEFAULT)
        self.ui.dcaSimResultsTextEdit.setText(ui_strings.DCA_TAB_DATA_CLEARED) # Or NO_SIMULATION_DATA_LOADED
        self.ui.dcaPlaceOrdersButton.setEnabled(False)
        self.ui.dcaStatusLabel.setText(ui_strings.DCA_TAB_DATA_CLEARED) # Or a general ready status if preferred

    @pyqtSlot()
    def _load_dca_data_to_tab(self):
        self.ui.dcaSimResultsTextEdit.clear()
        if self.last_simulation_dca_levels:
            current_sim_symbol = self.ui.simSymbolComboBox.currentText() # Get symbol from sim tab
            self.ui.dcaSymbolValueLabel.setText(current_sim_symbol if current_sim_symbol else ui_strings.LABEL_DCA_SYMBOL_DEFAULT)

            self.ui.dcaSimResultsTextEdit.append(ui_strings.DCA_TAB_SIMULATION_DATA_HEADER + "\n")
            for i, level in enumerate(self.last_simulation_dca_levels):
                # TODO: Use a more structured display, perhaps a QTableWidget in future. For now, text.
                # Consider adding a ui_string for this format
                level_text = f"Niveau {i+1}: Prix: {level['price']}, Montant: {level['amount']}"
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
        self._clear_dca_simulation_state() # Clear previous state and disable button

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
                self.last_simulation_dca_levels = []
                for i in range(len(results_data['prix_iterations'])):
                    self.last_simulation_dca_levels.append({
                        'price': results_data['prix_iterations'][i],
                        'amount': results_data['quantites_par_iteration'][i]
                    })
                # self.ui.simPlaceDcaOrdersButton.setEnabled(True) # Button removed
                # Automatically load to DCA tab if it's the current tab, or user can click "Load"
                # For now, let's rely on the explicit button press.
                # if self.ui.tabWidget.currentWidget() == self.ui.dcaOrdersTab:
                #    self._load_dca_data_to_tab()
            else:
                self.last_simulation_dca_levels = None
                # self.ui.simPlaceDcaOrdersButton.setEnabled(False) # Button removed

        except SimulationError as sim_e:
            self.ui.simResultsTextEdit.setText(f"Erreur de Simulation: {sim_e}")
            # self.ui.simPlaceDcaOrdersButton.setEnabled(False) # Button removed
        except Exception as e:
            self.ui.simResultsTextEdit.setText(f"{error_messages.ERROR_UNEXPECTED_SIM_ISSUE}: {e}")
            # self.ui.simPlaceDcaOrdersButton.setEnabled(False) # Button removed
            # import traceback
            # print(traceback.format_exc()) # For debugging

    @pyqtSlot()
    def start_place_dca_orders_from_dca_tab(self):
        self.ui.dcaStatusLabel.setText(ui_strings.DCA_TAB_ORDERS_SUBMITTING)
        self.ui.dcaSimResultsTextEdit.append("\n" + ui_strings.DCA_TAB_ORDERS_SUBMITTING) # Log in text area as well

        # Get and validate Margin Mode and Leverage first
        margin_mode_str = self.ui.dcaMergeModeComboBox.currentText()
        leverage_str = self.ui.dcaLeverageLineEdit.text().strip()
        leverage_int = 0

        if not leverage_str:
            self.ui.dcaStatusLabel.setText(ui_strings.ERROR_LEVERAGE_INVALID_NUMBER) # Or "Leverage required"
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

        if not (1 <= leverage_int <= 100): # Assuming range 1-100
            self.ui.dcaStatusLabel.setText(ui_strings.ERROR_LEVERAGE_OUT_OF_RANGE)
            self.ui.dcaSimResultsTextEdit.append(ui_strings.ERROR_LEVERAGE_OUT_OF_RANGE)
            self.ui.dcaPlaceOrdersButton.setEnabled(True)
            return

        api_key = self.ui.apiKeyLineEdit.text().strip()
        secret_key = self.ui.secretKeyLineEdit.text().strip()

        if not api_key or not secret_key:
            err_msg = error_messages.ERROR_API_KEYS_REQUIRED_UI + " (depuis l'onglet Config)"
            self.ui.dcaStatusLabel.setText(err_msg)
            self.ui.dcaSimResultsTextEdit.append(err_msg)
            return

        dca_tab_env_text = self.ui.globalEnvironmentComboBox.currentText() # Use global env for DCA orders
        market_env = self._get_selected_environment(dca_tab_env_text)
        if market_env is None:
            err_msg = error_messages.ERROR_INVALID_ENVIRONMENT_SELECTED
            self.ui.dcaStatusLabel.setText(err_msg)
            self.ui.dcaSimResultsTextEdit.append(err_msg)
            return

        dca_symbol = self.ui.dcaSymbolValueLabel.text()
        if not dca_symbol or dca_symbol == ui_strings.LABEL_DCA_SYMBOL_DEFAULT:
            err_msg = error_messages.ERROR_ORDER_SYMBOL_REQUIRED # Or a more specific one for DCA tab
            self.ui.dcaStatusLabel.setText(err_msg)
            self.ui.dcaSimResultsTextEdit.append(err_msg)
            return

        if not self.last_simulation_dca_levels:
            err_msg = ui_strings.LABEL_DCA_NO_SIMULATION_DATA_LOADED
            self.ui.dcaStatusLabel.setText(err_msg)
            self.ui.dcaSimResultsTextEdit.append(err_msg)
            return

        self.ui.dcaPlaceOrdersButton.setEnabled(False)

        if self.batch_dca_worker_thread and self.batch_dca_worker_thread.isRunning():
            # This message could also go to dcaSimResultsTextEdit
            self.ui.dcaStatusLabel.setText("Un lot d'ordres DCA est déjà en cours.")
            self.ui.dcaPlaceOrdersButton.setEnabled(True)
            return

        self.batch_dca_worker_thread = BatchDcaOrderWorker(
            binance_logic=self.binance_logic, api_key=api_key, secret_key=secret_key,
            market_env=market_env, symbol_str=dca_symbol,
            dca_levels_data=self.last_simulation_dca_levels,
            margin_mode=margin_mode_str, leverage=leverage_int
        )
        self.batch_dca_worker_thread.order_attempt_finished.connect(self._on_dca_tab_order_attempt_finished)
        self.batch_dca_worker_thread.batch_processing_finished.connect(self._on_dca_tab_batch_finished)
        self.batch_dca_worker_thread.start()

    @pyqtSlot(int, str, bool, object)
    def _on_dca_tab_order_attempt_finished(self, level_idx, symbol, success, result_obj):
        if success:
            order_response = result_obj
            msg = ui_strings.DCA_TAB_ORDER_LEVEL_SUCCESS.format(
                level=level_idx + 1,
                symbol=symbol,
                order_id=order_response.get('id', 'N/A'), # Use .get for safety
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
        self.ui.dcaStatusLabel.setText(msg) # Update status label with the latest attempt
        cursor = self.ui.dcaSimResultsTextEdit.textCursor()
        cursor.movePosition(cursor.End)
        self.ui.dcaSimResultsTextEdit.setTextCursor(cursor)

    @pyqtSlot(str)
    def _on_dca_tab_batch_finished(self, summary_message):
        final_msg = f"{ui_strings.DCA_TAB_BATCH_COMPLETE} {summary_message}"
        self.ui.dcaSimResultsTextEdit.append(f"\n{final_msg}")
        self.ui.dcaStatusLabel.setText(final_msg)
        self.ui.dcaPlaceOrdersButton.setEnabled(True)
        self.batch_dca_worker_thread = None # Clear the thread reference
        cursor = self.ui.dcaSimResultsTextEdit.textCursor()
        cursor.movePosition(cursor.End)
        self.ui.dcaSimResultsTextEdit.setTextCursor(cursor)

    def closeEvent(self, event):
        """Ensure worker threads are properly handled on close."""
        if hasattr(self, 'balance_worker_thread') and self.balance_worker_thread and self.balance_worker_thread.isRunning():
            self.balance_worker_thread.quit()
            self.balance_worker_thread.wait()

        if hasattr(self, 'order_placement_worker_thread') and self.order_placement_worker_thread and self.order_placement_worker_thread.isRunning():
            self.order_placement_worker_thread.quit()
            self.order_placement_worker_thread.wait()

        if hasattr(self, 'batch_dca_worker_thread') and self.batch_dca_worker_thread and self.batch_dca_worker_thread.isRunning():
            self.batch_dca_worker_thread.stop()
            self.batch_dca_worker_thread.wait(1000)
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = BinanceAppPyQt()
    mainWindow.show()
    sys.exit(app.exec_())
