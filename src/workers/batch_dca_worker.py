import time
from PyQt5.QtCore import QThread, pyqtSignal
from typing import List, Dict, Any
from ..app_logic import BinanceLogic, MarketEnvironment
from ..services.exchange_factory import ExchangeFactory

class BatchDcaOrderWorker(QThread):
    order_attempt_finished = pyqtSignal(int, str, bool, object)
    batch_processing_finished = pyqtSignal(str)
    batch_error = pyqtSignal(str)

    def __init__(self, binance_logic: BinanceLogic, api_key: str, secret_key: str, market_env: MarketEnvironment,
                 symbol_str: str, dca_levels_data: List[Dict[str, Any]], margin_mode: str, leverage: int, parent=None):
        super().__init__(parent)
        self.binance_logic = binance_logic
        self.api_key = api_key
        self.secret_key = secret_key
        self.market_env = market_env
        self.symbol_str = symbol_str
        self.dca_levels_data = dca_levels_data
        self.margin_mode = margin_mode
        self.leverage = leverage
        self._is_running = True
        self.placed_orders = []

    def stop(self):
        """Arrête le thread sans annuler les ordres."""
        self._is_running = False
        self.wait()

    def _cancel_all_orders(self):
        """Annule tous les ordres placés précédemment."""
        if not self.placed_orders:
            return

        try:
            exchange = ExchangeFactory.create(self.api_key, self.secret_key, self.market_env)
            for order in self.placed_orders:
                try:
                    exchange.cancel_order(order['id'], self.symbol_str)
                except Exception:
                    pass  # Ignorer les erreurs lors de l'annulation
        except Exception:
            pass  # Ignorer les erreurs lors de l'annulation

    def run(self):
        if not self.dca_levels_data:
            self.batch_processing_finished.emit("Aucune donnée de simulation disponible.")
            return

        try:
            for i, level_data in enumerate(self.dca_levels_data):
                if not self._is_running:
                    self._cancel_all_orders()
                    self.batch_processing_finished.emit("Traitement DCA annulé par l'utilisateur.")
                    return

                price = level_data['price']
                amount = level_data['amount']

                if amount <= 0 or price <= 0:
                    self.order_attempt_finished.emit(i, self.symbol_str, False,
                                                   "Le montant et le prix doivent être positifs.")
                    continue

                try:
                    order_response = self.binance_logic.place_order(
                        api_key=self.api_key, secret_key=self.secret_key, market_environment=self.market_env,
                        symbol=self.symbol_str, order_type="LIMIT", side="BUY",
                        amount=amount, price=price,
                        margin_mode=self.margin_mode, leverage=self.leverage
                    )
                    self.placed_orders.append(order_response)
                    self.order_attempt_finished.emit(i, self.symbol_str, True, order_response)
                except Exception as e:
                    self._cancel_all_orders()
                    error_detail = str(e)
                    if "leverage" in error_detail.lower():
                        error_msg = f"Erreur lors du placement de l'ordre {i+1}: Problème avec le levier ({self.leverage}x). Détail: {error_detail}"
                    elif "margin" in error_detail.lower():
                        error_msg = f"Erreur lors du placement de l'ordre {i+1}: Problème avec le mode de marge ({self.margin_mode}). Détail: {error_detail}"
                    elif "insufficient" in error_detail.lower():
                        error_msg = f"Erreur lors du placement de l'ordre {i+1}: Fonds insuffisants. Détail: {error_detail}"
                    else:
                        error_msg = f"Erreur lors du placement de l'ordre {i+1}. Détail: {error_detail}"
                    
                    error_msg += "\nTous les ordres ont été annulés. Veuillez vérifier les paramètres et réessayer."
                    self.batch_error.emit(error_msg)
                    return

                if i < len(self.dca_levels_data) - 1 and self._is_running:
                    time.sleep(0.2)

            if self._is_running:
                self.batch_processing_finished.emit("Traitement DCA terminé avec succès.")

        except Exception as e:
            self._cancel_all_orders()
            error_msg = f"Une erreur inattendue s'est produite: {str(e)}\nTous les ordres ont été annulés. Veuillez réessayer."
            self.batch_error.emit(error_msg) 