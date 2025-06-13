import unittest
from unittest.mock import MagicMock, patch
from PyQt5.QtCore import QCoreApplication
from src.viewmodels.main_viewmodel import MainViewModel
from src.models.market_environment import MarketEnvironment

class TestMainViewModel(unittest.TestCase):
    def setUp(self):
        """Set up for test methods."""
        self.app = QCoreApplication([])
        self.viewmodel = MainViewModel()

    def tearDown(self):
        """Clean up after test methods."""
        self.viewmodel.cleanup()
        self.app.quit()

    def test_fetch_balance_success(self):
        """Test successful balance fetch."""
        # Mock the worker
        mock_worker = MagicMock()
        with patch('src.viewmodels.main_viewmodel.BalanceWorker', return_value=mock_worker):
            # Connect to signals
            balance_received = []
            error_received = []
            self.viewmodel.balance_updated.connect(lambda x: balance_received.append(x))
            self.viewmodel.balance_error.connect(lambda x: error_received.append(x))

            # Call the method
            self.viewmodel.fetch_balance("test_key", "test_secret", MarketEnvironment.SPOT)

            # Verify worker was created and started
            mock_worker.start.assert_called_once()

            # Simulate success
            mock_worker.success.emit(100.0)

            # Verify signal was received
            self.assertEqual(balance_received, [100.0])
            self.assertEqual(error_received, [])

    def test_fetch_balance_error(self):
        """Test balance fetch with error."""
        # Mock the worker
        mock_worker = MagicMock()
        with patch('src.viewmodels.main_viewmodel.BalanceWorker', return_value=mock_worker):
            # Connect to signals
            balance_received = []
            error_received = []
            self.viewmodel.balance_updated.connect(lambda x: balance_received.append(x))
            self.viewmodel.balance_error.connect(lambda x: error_received.append(x))

            # Call the method
            self.viewmodel.fetch_balance("test_key", "test_secret", MarketEnvironment.SPOT)

            # Simulate error
            mock_worker.error.emit("Test error")

            # Verify signal was received
            self.assertEqual(balance_received, [])
            self.assertEqual(error_received, ["Test error"])

    def test_place_order_success(self):
        """Test successful order placement."""
        # Mock the worker
        mock_worker = MagicMock()
        with patch('src.viewmodels.main_viewmodel.OrderPlacementWorker', return_value=mock_worker):
            # Connect to signals
            order_received = []
            error_received = []
            self.viewmodel.order_placed.connect(lambda x: order_received.append(x))
            self.viewmodel.order_error.connect(lambda x: error_received.append(x))

            # Call the method
            self.viewmodel.place_order(
                "test_key", "test_secret", MarketEnvironment.SPOT,
                "BTC/USDT", "LIMIT", "BUY", 1.0, 30000.0
            )

            # Simulate success
            mock_worker.success.emit({"id": "123", "status": "open"})

            # Verify signal was received
            self.assertEqual(order_received, [{"id": "123", "status": "open"}])
            self.assertEqual(error_received, [])

    def test_place_order_error(self):
        """Test order placement with error."""
        # Mock the worker
        mock_worker = MagicMock()
        with patch('src.viewmodels.main_viewmodel.OrderPlacementWorker', return_value=mock_worker):
            # Connect to signals
            order_received = []
            error_received = []
            self.viewmodel.order_placed.connect(lambda x: order_received.append(x))
            self.viewmodel.order_error.connect(lambda x: error_received.append(x))

            # Call the method
            self.viewmodel.place_order(
                "test_key", "test_secret", MarketEnvironment.SPOT,
                "BTC/USDT", "LIMIT", "BUY", 1.0, 30000.0
            )

            # Simulate error
            mock_worker.error.emit("Test error")

            # Verify signal was received
            self.assertEqual(order_received, [])
            self.assertEqual(error_received, ["Test error"])

    def test_cleanup(self):
        """Test cleanup of workers."""
        # Mock workers
        mock_balance_worker = MagicMock()
        mock_order_worker = MagicMock()
        mock_batch_worker = MagicMock()

        with patch('src.viewmodels.main_viewmodel.BalanceWorker', return_value=mock_balance_worker), \
             patch('src.viewmodels.main_viewmodel.OrderPlacementWorker', return_value=mock_order_worker), \
             patch('src.viewmodels.main_viewmodel.BatchDcaOrderWorker', return_value=mock_batch_worker):

            # Start all workers
            self.viewmodel.fetch_balance("test_key", "test_secret", MarketEnvironment.SPOT)
            self.viewmodel.place_order("test_key", "test_secret", MarketEnvironment.SPOT,
                                     "BTC/USDT", "LIMIT", "BUY", 1.0, 30000.0)
            self.viewmodel.place_batch_orders("test_key", "test_secret", MarketEnvironment.SPOT,
                                           "BTC/USDT", [], "CROSS", 1)

            # Cleanup
            self.viewmodel.cleanup()

            # Verify all workers were stopped
            mock_balance_worker.stop.assert_called_once()
            mock_order_worker.stop.assert_called_once()
            mock_batch_worker.stop.assert_called_once() 