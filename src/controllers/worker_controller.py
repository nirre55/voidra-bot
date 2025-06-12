from PyQt5.QtCore import QObject, pyqtSignal
from typing import Optional, List, Dict, Any
from ..app_logic import BinanceLogic, MarketEnvironment
from ..workers.balance_worker import BalanceWorker
from ..workers.order_placement_worker import OrderPlacementWorker
from ..workers.batch_dca_worker import BatchDcaOrderWorker

class WorkerController(QObject):
    # Signaux pour le BalanceWorker
    balance_success = pyqtSignal(float)
    balance_error = pyqtSignal(str)
    balance_finished = pyqtSignal()

    # Signaux pour le OrderPlacementWorker
    order_success = pyqtSignal(object)
    order_error = pyqtSignal(str)
    order_finished = pyqtSignal()

    # Signaux pour le BatchDcaOrderWorker
    dca_order_attempt_finished = pyqtSignal(int, str, bool, object)
    dca_batch_finished = pyqtSignal(str)
    dca_batch_error = pyqtSignal(str)

    def __init__(self, binance_logic: BinanceLogic):
        super().__init__()
        self.binance_logic = binance_logic
        self.balance_worker: Optional[BalanceWorker] = None
        self.order_placement_worker: Optional[OrderPlacementWorker] = None
        self.batch_dca_worker: Optional[BatchDcaOrderWorker] = None

    def start_fetch_balance(self, api_key: str, secret_key: str, market_env: MarketEnvironment):
        """Démarre le worker pour récupérer le solde."""
        if self.balance_worker and self.balance_worker.isRunning():
            return

        self.balance_worker = BalanceWorker(self.binance_logic, api_key, secret_key, market_env)
        self.balance_worker.success.connect(self.balance_success)
        self.balance_worker.error.connect(self.balance_error)
        self.balance_worker.finished.connect(self.balance_finished)
        self.balance_worker.start()

    def start_place_order(self, api_key: str, secret_key: str, market_env: MarketEnvironment,
                         symbol: str, order_type: str, side: str, amount: float,
                         price: Optional[float] = None):
        """Démarre le worker pour placer un ordre."""
        if self.order_placement_worker and self.order_placement_worker.isRunning():
            return

        self.order_placement_worker = OrderPlacementWorker(
            self.binance_logic, api_key, secret_key, market_env,
            symbol, order_type, side, amount, price
        )
        self.order_placement_worker.success.connect(self.order_success)
        self.order_placement_worker.error.connect(self.order_error)
        self.order_placement_worker.finished.connect(self.order_finished)
        self.order_placement_worker.start()

    def start_place_dca_orders(self, api_key: str, secret_key: str, market_env: MarketEnvironment,
                              symbol: str, dca_levels_data: List[Dict[str, Any]],
                              margin_mode: str, leverage: int):
        """Démarre le worker pour placer les ordres DCA."""
        if self.batch_dca_worker and self.batch_dca_worker.isRunning():
            return

        self.batch_dca_worker = BatchDcaOrderWorker(
            self.binance_logic, api_key, secret_key, market_env,
            symbol, dca_levels_data, margin_mode, leverage
        )
        self.batch_dca_worker.order_attempt_finished.connect(self.dca_order_attempt_finished)
        self.batch_dca_worker.batch_processing_finished.connect(self.dca_batch_finished)
        self.batch_dca_worker.batch_error.connect(self.dca_batch_error)
        self.batch_dca_worker.start()

    def stop_all_workers(self):
        """Arrête tous les workers en cours d'exécution."""
        if self.balance_worker and self.balance_worker.isRunning():
            self.balance_worker.quit()
            self.balance_worker.wait()

        if self.order_placement_worker and self.order_placement_worker.isRunning():
            self.order_placement_worker.quit()
            self.order_placement_worker.wait()

        if self.batch_dca_worker and self.batch_dca_worker.isRunning():
            self.batch_dca_worker.stop()
            self.batch_dca_worker.wait() 