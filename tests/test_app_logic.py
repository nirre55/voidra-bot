import unittest
from unittest.mock import patch, MagicMock
import ccxt # Required for ccxt.NetworkError, ccxt.ExchangeError, ccxt.InsufficientFunds, ccxt.InvalidOrder
from src.app_logic import (
    BinanceLogic,
    MarketEnvironment,
    ApiKeyMissingError,
    CustomNetworkError,
    CustomExchangeError,
    AppLogicError,
    OrderPlacementError,
    InsufficientFundsError,
    InvalidOrderParamsError
)

class TestBinanceLogic(unittest.TestCase):
    def setUp(self):
        """Set up for test methods."""
        self.logic = BinanceLogic()
        self.dummy_api_key = "test_api_key"
        self.dummy_secret_key = "test_secret_key"

    @patch('src.app_logic.ccxt.binance')
    def test_get_balance_success(self, mock_binance_constructor):
        """Test successful balance retrieval."""
        mock_exchange_instance = MagicMock()
        mock_exchange_instance.fetch_balance.return_value = {'total': {'USDT': 123.45}}
        mock_binance_constructor.return_value = mock_exchange_instance

        balance = self.logic.get_balance(self.dummy_api_key, self.dummy_secret_key, MarketEnvironment.SPOT)

        self.assertEqual(balance, 123.45)
        args, kwargs = mock_binance_constructor.call_args
        self.assertEqual(args[0]['apiKey'], self.dummy_api_key)
        self.assertEqual(args[0]['secret'], self.dummy_secret_key)
        self.assertNotIn('defaultType', args[0].get('options', {}))
        mock_exchange_instance.set_sandbox_mode.assert_not_called()
        mock_exchange_instance.fetch_balance.assert_called_once()

    @patch('src.app_logic.ccxt.binance')
    def test_get_balance_usdt_missing(self, mock_binance_constructor):
        """Test when USDT is missing from the balance data."""
        mock_exchange_instance = MagicMock()
        mock_exchange_instance.fetch_balance.return_value = {'total': {'BTC': 1.0}} # USDT missing
        mock_binance_constructor.return_value = mock_exchange_instance

        balance = self.logic.get_balance(self.dummy_api_key, self.dummy_secret_key, MarketEnvironment.SPOT)

        self.assertEqual(balance, 0.0)
        mock_binance_constructor.assert_called_once()
        mock_exchange_instance.fetch_balance.assert_called_once()

    @patch('src.app_logic.ccxt.binance')
    def test_get_balance_total_missing(self, mock_binance_constructor):
        """Test when 'total' key is missing from the balance data."""
        mock_exchange_instance = MagicMock()
        mock_exchange_instance.fetch_balance.return_value = {'free': {'USDT': 10.0}} # 'total' key missing
        mock_binance_constructor.return_value = mock_exchange_instance

        balance = self.logic.get_balance(self.dummy_api_key, self.dummy_secret_key, MarketEnvironment.SPOT)

        self.assertEqual(balance, 0.0)

    def test_get_balance_api_key_missing(self):
        """Test calling get_balance with missing API key."""
        test_cases = [
            ("", self.dummy_secret_key),
            (self.dummy_api_key, ""),
            (None, self.dummy_secret_key),
            (self.dummy_api_key, None),
            (None, None)
        ]
        for api_key, secret_key in test_cases:
            # API key check is before market_mode specific logic, so testing one mode is sufficient
            with self.subTest(api_key=api_key, secret_key=secret_key):
                with self.assertRaisesRegex(ApiKeyMissingError, "API Key and Secret Key are required."):
                    self.logic.get_balance(api_key, secret_key, MarketEnvironment.SPOT)

    @patch('src.app_logic.ccxt.binance')
    def test_get_balance_network_error(self, mock_binance_constructor):
        """Test handling of ccxt.NetworkError."""
        mock_exchange_instance = MagicMock()
        mock_exchange_instance.fetch_balance.side_effect = ccxt.NetworkError("Connection failed")
        mock_binance_constructor.return_value = mock_exchange_instance

        with self.assertRaisesRegex(CustomNetworkError, "Network error connecting to Binance: Connection failed"):
            self.logic.get_balance(self.dummy_api_key, self.dummy_secret_key, MarketEnvironment.SPOT)

    @patch('src.app_logic.ccxt.binance')
    def test_get_balance_exchange_error(self, mock_binance_constructor):
        """Test handling of ccxt.ExchangeError."""
        mock_exchange_instance = MagicMock()
        mock_exchange_instance.fetch_balance.side_effect = ccxt.ExchangeError("Invalid API key")
        mock_binance_constructor.return_value = mock_exchange_instance

        with self.assertRaisesRegex(CustomExchangeError, "Binance API error: Invalid API key"):
            self.logic.get_balance(self.dummy_api_key, self.dummy_secret_key, MarketEnvironment.SPOT)

    @patch('src.app_logic.ccxt.binance')
    def test_get_balance_unexpected_error(self, mock_binance_constructor):
        """Test handling of other unexpected errors."""
        mock_exchange_instance = MagicMock()
        mock_exchange_instance.fetch_balance.side_effect = RuntimeError("Something went very wrong")
        mock_binance_constructor.return_value = mock_exchange_instance

        expected_message = "An unexpected error occurred in application logic: Something went very wrong"
        with self.assertRaisesRegex(AppLogicError, expected_message):
            self.logic.get_balance(self.dummy_api_key, self.dummy_secret_key, MarketEnvironment.SPOT)

    @patch('src.app_logic.ccxt.binance')
    def test_get_balance_futures_testnet_success(self, mock_binance_constructor):
        """Test successful balance retrieval from Futures Testnet."""
        mock_exchange_instance = MagicMock()
        mock_exchange_instance.fetch_balance.return_value = {'total': {'USDT': 500.75}}
        mock_binance_constructor.return_value = mock_exchange_instance

        balance = self.logic.get_balance(self.dummy_api_key, self.dummy_secret_key, MarketEnvironment.FUTURES_TESTNET)

        self.assertEqual(balance, 500.75)
        args, kwargs = mock_binance_constructor.call_args
        self.assertEqual(args[0]['apiKey'], self.dummy_api_key)
        self.assertEqual(args[0]['secret'], self.dummy_secret_key)
        self.assertEqual(args[0].get('options', {}).get('defaultType'), 'future')
        mock_exchange_instance.set_sandbox_mode.assert_called_once_with(True)
        mock_exchange_instance.fetch_balance.assert_called_once()

    @patch('src.app_logic.ccxt.binance')
    def test_get_balance_futures_live_success(self, mock_binance_constructor):
        """Test successful balance retrieval from Futures Live."""
        mock_exchange_instance = MagicMock()
        mock_exchange_instance.fetch_balance.return_value = {'total': {'USDT': 1500.25}}
        mock_binance_constructor.return_value = mock_exchange_instance

        balance = self.logic.get_balance(self.dummy_api_key, self.dummy_secret_key, MarketEnvironment.FUTURES_LIVE)

        self.assertEqual(balance, 1500.25)
        args, kwargs = mock_binance_constructor.call_args
        self.assertEqual(args[0]['apiKey'], self.dummy_api_key)
        self.assertEqual(args[0]['secret'], self.dummy_secret_key)
        self.assertEqual(args[0].get('options', {}).get('defaultType'), 'future')
        mock_exchange_instance.set_sandbox_mode.assert_not_called()
        mock_exchange_instance.fetch_balance.assert_called_once()

    # --- Tests for place_order ---

    @patch('src.app_logic.ccxt.binance')
    def test_place_order_spot_limit_buy_success(self, mock_binance_constructor):
        mock_exchange_instance = MagicMock()
        expected_order_response = {'id': '123', 'symbol': 'BTC/USDT', 'status': 'open'}
        mock_exchange_instance.create_order.return_value = expected_order_response
        mock_binance_constructor.return_value = mock_exchange_instance

        order_params_dict = {
            'symbol': 'BTC/USDT', 'order_type': 'LIMIT', 'side': 'BUY',
            'amount': 1.0, 'price': 30000.0
        }

        actual_order = self.logic.place_order(
            self.dummy_api_key, self.dummy_secret_key,
            MarketEnvironment.SPOT, **order_params_dict
        )

        self.assertEqual(actual_order, expected_order_response)
        args, _ = mock_binance_constructor.call_args
        self.assertNotIn('defaultType', args[0].get('options', {}))
        mock_exchange_instance.set_sandbox_mode.assert_not_called()
        mock_exchange_instance.create_order.assert_called_once_with(
            order_params_dict['symbol'], order_params_dict['order_type'].lower(),
            order_params_dict['side'].lower(), order_params_dict['amount'],
            order_params_dict['price'], {}
        )

    @patch('src.app_logic.ccxt.binance')
    def test_place_order_futures_testnet_market_sell_success(self, mock_binance_constructor):
        mock_exchange_instance = MagicMock()
        expected_order_response = {'id': '124', 'symbol': 'ETH/USDT', 'status': 'closed'}
        mock_exchange_instance.create_order.return_value = expected_order_response
        mock_binance_constructor.return_value = mock_exchange_instance

        order_params_dict = {
            'symbol': 'ETH/USDT', 'order_type': 'MARKET', 'side': 'SELL', 'amount': 10.0
        }

        actual_order = self.logic.place_order(
            self.dummy_api_key, self.dummy_secret_key,
            MarketEnvironment.FUTURES_TESTNET, **order_params_dict
        )

        self.assertEqual(actual_order, expected_order_response)
        args, _ = mock_binance_constructor.call_args
        self.assertEqual(args[0].get('options', {}).get('defaultType'), 'future')
        mock_exchange_instance.set_sandbox_mode.assert_called_once_with(True)
        mock_exchange_instance.create_order.assert_called_once_with(
            order_params_dict['symbol'], order_params_dict['order_type'].lower(),
            order_params_dict['side'].lower(), order_params_dict['amount'],
            None, {} # Price is None for MARKET order
        )

    def test_place_order_invalid_params(self):
        base_params = {
            'api_key': self.dummy_api_key, 'secret_key': self.dummy_secret_key,
            'market_environment': MarketEnvironment.SPOT, 'symbol': 'BTC/USDT',
            'order_type': 'LIMIT', 'side': 'BUY', 'amount': 1.0, 'price': 30000.0
        }

        invalid_cases = [
            ('symbol', "", "Symbol is required."),
            ('order_type', "INVALID_TYPE", "Order type must be LIMIT or MARKET."),
            ('side', "INVALID_SIDE", "Side must be BUY or SELL."),
            ('amount', 0, "Amount must be positive."),
            ('amount', -1, "Amount must be positive."),
            ('price', 0, "Price must be positive for LIMIT orders.", {'order_type': 'LIMIT'}),
            ('price', -1, "Price must be positive for LIMIT orders.", {'order_type': 'LIMIT'}),
            ('price', None, "Price must be positive for LIMIT orders.", {'order_type': 'LIMIT'}),
        ]

        for param_key, invalid_value, error_msg, *conditional_params_list in invalid_cases:
            with self.subTest(param_to_test=param_key, invalid_value=invalid_value):
                current_params = {**base_params, param_key: invalid_value}
                if conditional_params_list: # Apply conditional params like setting order_type to LIMIT
                    current_params.update(conditional_params_list[0])

                # Remove price for non-LIMIT if it's not the parameter being tested for None
                if current_params['order_type'] != 'LIMIT' and param_key != 'price':
                    current_params['price'] = None


                with self.assertRaisesRegex(InvalidOrderParamsError, error_msg):
                    self.logic.place_order(**{k: v for k, v in current_params.items() if k in self.logic.place_order.__code__.co_varnames})


    def test_place_order_api_key_missing(self):
        with self.assertRaisesRegex(ApiKeyMissingError, "API Key and Secret Key are required."):
            self.logic.place_order(
                "", self.dummy_secret_key, MarketEnvironment.SPOT,
                'BTC/USDT', 'LIMIT', 'BUY', 1.0, 30000.0
            )

    @patch('src.app_logic.ccxt.binance')
    def test_place_order_insufficient_funds(self, mock_binance_constructor):
        mock_exchange_instance = MagicMock()
        mock_exchange_instance.create_order.side_effect = ccxt.InsufficientFunds("Test InsufficientFunds")
        mock_binance_constructor.return_value = mock_exchange_instance
        with self.assertRaisesRegex(InsufficientFundsError, "Insufficient funds: Test InsufficientFunds"):
            self.logic.place_order(
                self.dummy_api_key, self.dummy_secret_key, MarketEnvironment.SPOT,
                'BTC/USDT', 'LIMIT', 'BUY', 1.0, 30000.0
            )

    @patch('src.app_logic.ccxt.binance')
    def test_place_order_ccxt_invalid_order_error(self, mock_binance_constructor):
        mock_exchange_instance = MagicMock()
        mock_exchange_instance.create_order.side_effect = ccxt.InvalidOrder("Test InvalidOrder from CCXT")
        mock_binance_constructor.return_value = mock_exchange_instance
        with self.assertRaisesRegex(InvalidOrderParamsError, "Invalid order parameters for exchange: Test InvalidOrder from CCXT"):
            self.logic.place_order(
                self.dummy_api_key, self.dummy_secret_key, MarketEnvironment.SPOT,
                'BTC/USDT', 'LIMIT', 'BUY', 1.0, 30000.0
            )

    @patch('src.app_logic.ccxt.binance')
    def test_place_order_network_error(self, mock_binance_constructor):
        mock_exchange_instance = MagicMock()
        mock_exchange_instance.create_order.side_effect = ccxt.NetworkError("Test NetworkError")
        mock_binance_constructor.return_value = mock_exchange_instance
        with self.assertRaisesRegex(CustomNetworkError, "Network error during order placement: Test NetworkError"):
            self.logic.place_order(
                self.dummy_api_key, self.dummy_secret_key, MarketEnvironment.SPOT,
                'BTC/USDT', 'LIMIT', 'BUY', 1.0, 30000.0
            )

    @patch('src.app_logic.ccxt.binance')
    def test_place_order_exchange_error(self, mock_binance_constructor):
        mock_exchange_instance = MagicMock()
        # Simulate a more generic ExchangeError that isn't InsufficientFunds or InvalidOrder
        mock_exchange_instance.create_order.side_effect = ccxt.ExchangeError("Test ExchangeError")
        mock_binance_constructor.return_value = mock_exchange_instance
        with self.assertRaisesRegex(OrderPlacementError, "Binance API error during order placement: Test ExchangeError"):
            self.logic.place_order(
                self.dummy_api_key, self.dummy_secret_key, MarketEnvironment.SPOT,
                'BTC/USDT', 'LIMIT', 'BUY', 1.0, 30000.0
            )

    @patch('src.app_logic.ccxt.binance')
    def test_place_order_unexpected_error(self, mock_binance_constructor):
        mock_exchange_instance = MagicMock()
        mock_exchange_instance.create_order.side_effect = Exception("Test Unexpected Exception")
        mock_binance_constructor.return_value = mock_exchange_instance
        with self.assertRaisesRegex(AppLogicError, "An unexpected error occurred during order placement: Test Unexpected Exception"):
            self.logic.place_order(
                self.dummy_api_key, self.dummy_secret_key, MarketEnvironment.SPOT,
                'BTC/USDT', 'LIMIT', 'BUY', 1.0, 30000.0
            )

if __name__ == '__main__':
    unittest.main()
