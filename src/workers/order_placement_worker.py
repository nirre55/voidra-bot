from PyQt5.QtCore import QThread, pyqtSignal
from typing import Optional
from ..app_logic import (
    BinanceLogic, ApiKeyMissingError, InvalidOrderParamsError,
    InsufficientFundsError, OrderPlacementError, CustomNetworkError, AppLogicError
)
from ..models.market_environment import MarketEnvironment
from ..constants import error_messages

class OrderPlacementWorker(QThread):
    success = pyqtSignal(object)
    error = pyqtSignal(str)

    def __init__(self, binance_logic: BinanceLogic, api_key: str, secret_key: str,
                 market_environment: MarketEnvironment, symbol: str, order_type: str,
                 side: str, amount: float, price: Optional[float] = None, parent=None):
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
        self._is_running = True

    def stop(self):
        """Arrête le thread."""
        self._is_running = False
        self.wait()

    def run(self):
        if not self._is_running:
            return

        try:
            order_response = self.binance_logic.place_order(
                self.api_key, self.secret_key, self.market_environment,
                self.symbol, self.order_type, self.side, self.amount, self.price
            )
            if self._is_running:
                self.success.emit(order_response)
        except (ApiKeyMissingError, InvalidOrderParamsError, InsufficientFundsError,
                OrderPlacementError, CustomNetworkError, AppLogicError) as e:
            if self._is_running:
                self.error.emit(str(e))
        except Exception as e:
            if self._is_running:
                self.error.emit(f"{error_messages.ERROR_UNEXPECTED}: {str(e)}") 