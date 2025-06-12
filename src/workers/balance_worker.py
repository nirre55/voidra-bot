from PyQt5.QtCore import QThread, pyqtSignal
from ..app_logic import BinanceLogic, MarketEnvironment, ApiKeyMissingError, CustomNetworkError, CustomExchangeError, AppLogicError
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

    def run(self):
        try:
            balance = self.binance_logic.get_balance(self.api_key, self.secret_key, self.market_environment)
            self.success.emit(balance)
        except (ApiKeyMissingError, CustomNetworkError, CustomExchangeError, AppLogicError) as e:
            self.error.emit(str(e))
        except Exception as e:
            self.error.emit(f"{error_messages.ERROR_UNEXPECTED}: {str(e)}") 