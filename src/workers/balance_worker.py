from PyQt5.QtCore import QThread, pyqtSignal
from ..app_logic import BinanceLogic, ApiKeyMissingError, CustomNetworkError, CustomExchangeError, AppLogicError
from ..models.market_environment import MarketEnvironment
from ..constants import error_messages

class BalanceWorker(QThread):
    """
    Worker thread pour récupérer le solde Binance sans bloquer l'UI.
    """
    success = pyqtSignal(float)
    error = pyqtSignal(str)

    def __init__(self, binance_logic: BinanceLogic, api_key: str, secret_key: str, market_environment: MarketEnvironment, parent=None):
        super().__init__(parent)
        self.binance_logic = binance_logic
        self.api_key = api_key
        self.secret_key = secret_key
        self.market_environment = market_environment
        self._is_running = True

    def stop(self):
        """Arrête le thread."""
        self._is_running = False
        self.wait()

    def run(self):
        if not self._is_running:
            return

        try:
            balance = self.binance_logic.get_balance(self.api_key, self.secret_key, self.market_environment)
            if self._is_running:
                self.success.emit(balance)
        except (ApiKeyMissingError, CustomNetworkError, CustomExchangeError, AppLogicError) as e:
            if self._is_running:
                self.error.emit(str(e))
        except Exception as e:
            if self._is_running:
                self.error.emit(f"{error_messages.ERROR_UNEXPECTED}: {str(e)}") 