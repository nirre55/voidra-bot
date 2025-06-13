from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from typing import Optional
from ..app_logic import BinanceLogic
from ..models.market_environment import MarketEnvironment
from ..workers.balance_worker import BalanceWorker
from ..workers.order_placement_worker import OrderPlacementWorker
from ..workers.batch_dca_worker import BatchDcaOrderWorker

class MainViewModel(QObject):
    # Signaux pour la mise à jour de l'UI
    balance_updated = pyqtSignal(float)
    balance_error = pyqtSignal(str)
    order_placed = pyqtSignal(object)
    order_error = pyqtSignal(str)
    batch_order_progress = pyqtSignal(int, str, bool, object)
    batch_completed = pyqtSignal(str)
    batch_error = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.binance_logic = BinanceLogic()
        self._current_balance_worker: Optional[BalanceWorker] = None
        self._current_order_worker: Optional[OrderPlacementWorker] = None
        self._current_batch_worker: Optional[BatchDcaOrderWorker] = None

    @pyqtSlot(str, str, MarketEnvironment)
    def fetch_balance(self, api_key: str, secret_key: str, market_env: MarketEnvironment):
        """Démarre le worker pour récupérer le solde."""
        if self._current_balance_worker is not None:
            self._current_balance_worker.stop()
            self._current_balance_worker.wait()

        self._current_balance_worker = BalanceWorker(
            self.binance_logic, api_key, secret_key, market_env
        )
        self._current_balance_worker.success.connect(self.balance_updated)
        self._current_balance_worker.error.connect(self.balance_error)
        self._current_balance_worker.start()

    @pyqtSlot(str, str, MarketEnvironment, str, str, str, float, Optional[float])
    def place_order(self, api_key: str, secret_key: str, market_env: MarketEnvironment,
                   symbol: str, order_type: str, side: str, amount: float, price: Optional[float] = None):
        """Démarre le worker pour placer un ordre."""
        if self._current_order_worker is not None:
            self._current_order_worker.stop()
            self._current_order_worker.wait()

        self._current_order_worker = OrderPlacementWorker(
            self.binance_logic, api_key, secret_key, market_env,
            symbol, order_type, side, amount, price
        )
        self._current_order_worker.success.connect(self.order_placed)
        self._current_order_worker.error.connect(self.order_error)
        self._current_order_worker.start()

    @pyqtSlot(str, str, MarketEnvironment, str, list, str, int)
    def place_batch_orders(self, api_key: str, secret_key: str, market_env: MarketEnvironment,
                          symbol: str, dca_levels: list, margin_mode: str, leverage: int):
        """Démarre le worker pour placer une série d'ordres DCA."""
        if self._current_batch_worker is not None:
            self._current_batch_worker.stop()
            self._current_batch_worker.wait()

        self._current_batch_worker = BatchDcaOrderWorker(
            self.binance_logic, api_key, secret_key, market_env,
            symbol, dca_levels, margin_mode, leverage
        )
        self._current_batch_worker.order_attempt_finished.connect(self.batch_order_progress)
        self._current_batch_worker.batch_processing_finished.connect(self.batch_completed)
        self._current_batch_worker.batch_error.connect(self.batch_error)
        self._current_batch_worker.start()

    def cleanup(self):
        """Nettoie les workers en cours."""
        if self._current_balance_worker is not None:
            self._current_balance_worker.stop()
            self._current_balance_worker.wait()
        if self._current_order_worker is not None:
            self._current_order_worker.stop()
            self._current_order_worker.wait()
        if self._current_batch_worker is not None:
            self._current_batch_worker.stop()
            self._current_batch_worker.wait() 