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
from src.constants import error_messages, ui_strings

class TestBinanceLogic(unittest.TestCase):
    def setUp(self):
        """Set up for test methods."""
        self.logic = BinanceLogic()
        self.dummy_api_key = "test_api_key"
        self.dummy_secret_key = "test_secret_key"

    @patch('src.app_logic.ccxt.binance')
    def test_get_balance_success_spot(self, mock_binance_constructor):
        """Test successful balance retrieval for SPOT market."""
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
        mock_exchange_instance.fetch_balance.return_value = {'total': {'BTC': 1.0}}
        mock_binance_constructor.return_value = mock_exchange_instance

        balance = self.logic.get_balance(self.dummy_api_key, self.dummy_secret_key, MarketEnvironment.SPOT)

        self.assertEqual(balance, 0.0)
        mock_binance_constructor.assert_called_once()
        mock_exchange_instance.fetch_balance.assert_called_once()

    @patch('src.app_logic.ccxt.binance')
    def test_get_balance_total_missing(self, mock_binance_constructor):
        """Test when 'total' key is missing from the balance data."""
        mock_exchange_instance = MagicMock()
        mock_exchange_instance.fetch_balance.return_value = {'free': {'USDT': 10.0}}
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
            with self.subTest(api_key=api_key, secret_key=secret_key, market_mode=MarketEnvironment.SPOT):
                with self.assertRaisesRegex(ApiKeyMissingError, error_messages.PARAM_API_KEYS_REQUIRED):
                    self.logic.get_balance(api_key, secret_key, MarketEnvironment.SPOT)
            with self.subTest(api_key=api_key, secret_key=secret_key, market_mode=MarketEnvironment.FUTURES_TESTNET):
                with self.assertRaisesRegex(ApiKeyMissingError, error_messages.PARAM_API_KEYS_REQUIRED):
                    self.logic.get_balance(api_key, secret_key, MarketEnvironment.FUTURES_TESTNET)

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

    def _setup_mock_exchange_for_order(self, mock_binance_constructor, order_response=None, side_effect=None):
        mock_exchange_instance = MagicMock()
        if side_effect:
            mock_exchange_instance.create_order.side_effect = side_effect
        else:
            mock_exchange_instance.create_order.return_value = order_response
        mock_binance_constructor.return_value = mock_exchange_instance
        return mock_exchange_instance

    @patch('src.app_logic.ccxt.binance')
    def test_place_order_spot_limit_buy_success(self, mock_binance_constructor):
        expected_order_response = {'id': '123', 'symbol': 'BTC/USDT', 'status': 'open'}
        mock_exchange = self._setup_mock_exchange_for_order(mock_binance_constructor, order_response=expected_order_response)

        order_params = {
            'symbol': 'BTC/USDT', 'order_type': ui_strings.ORDER_TYPE_LIMIT, 'side': ui_strings.SIDE_BUY,
            'amount': 1.0, 'price': 30000.0
        }

        actual_order = self.logic.place_order(
            self.dummy_api_key, self.dummy_secret_key,
            MarketEnvironment.SPOT, **order_params
        )

        self.assertEqual(actual_order, expected_order_response)
        args, _ = mock_binance_constructor.call_args
        self.assertNotIn('defaultType', args[0].get('options', {}))
        mock_exchange.set_sandbox_mode.assert_not_called()
        mock_exchange.create_order.assert_called_once_with(
            order_params['symbol'], order_params['order_type'].lower(),
            order_params['side'].lower(), order_params['amount'],
            order_params['price'], {}
        )

    @patch('src.app_logic.ccxt.binance')
    def test_place_order_spot_market_sell_success(self, mock_binance_constructor):
        mock_exchange = MagicMock()
        expected_order_response = {'id': '125', 'symbol': 'ETH/USDT', 'status': 'closed'}
        mock_exchange.create_order.return_value = expected_order_response
        mock_binance_constructor.return_value = mock_exchange

        order_params = {
            'symbol': 'ETH/USDT', 'order_type': ui_strings.ORDER_TYPE_MARKET,
            'side': ui_strings.SIDE_SELL, 'amount': 2.0
        }

        actual_order = self.logic.place_order(
            self.dummy_api_key, self.dummy_secret_key,
            MarketEnvironment.SPOT, **order_params
        )

        self.assertEqual(actual_order, expected_order_response)
        args, _ = mock_binance_constructor.call_args
        self.assertNotIn('defaultType', args[0].get('options', {}))
        mock_exchange.set_sandbox_mode.assert_not_called()
        mock_exchange.create_order.assert_called_once_with(
            order_params['symbol'], order_params['order_type'].lower(),
            order_params['side'].lower(), order_params['amount'],
            None, {}
        )

    @patch('src.app_logic.ccxt.binance')
    def test_place_order_futures_live_limit_buy_success(self, mock_binance_constructor):
        mock_exchange = MagicMock()
        expected_order_response = {'id': '126', 'symbol': 'ADA/USDT', 'status': 'open'}
        mock_exchange.create_order.return_value = expected_order_response
        mock_binance_constructor.return_value = mock_exchange

        order_params = {
            'symbol': 'ADA/USDT', 'order_type': ui_strings.ORDER_TYPE_LIMIT, 'side': ui_strings.SIDE_BUY,
            'amount': 100.0, 'price': 0.5
        }

        actual_order = self.logic.place_order(
            self.dummy_api_key, self.dummy_secret_key,
            MarketEnvironment.FUTURES_LIVE, **order_params
        )

        self.assertEqual(actual_order, expected_order_response)
        args, _ = mock_binance_constructor.call_args
        self.assertEqual(args[0].get('options', {}).get('defaultType'), 'future')
        mock_exchange.set_sandbox_mode.assert_not_called()
        mock_exchange.create_order.assert_called_once_with(
            order_params['symbol'], order_params['order_type'].lower(),
            order_params['side'].lower(), order_params['amount'],
            order_params['price'], {}
        )

    @patch('src.app_logic.ccxt.binance')
    def test_place_order_futures_testnet_market_sell_success(self, mock_binance_constructor):
        mock_exchange = MagicMock()
        expected_order_response = {'id': '127', 'symbol': 'SOL/USDT', 'status': 'closed'}
        mock_exchange.create_order.return_value = expected_order_response
        mock_binance_constructor.return_value = mock_exchange

        order_params = {
            'symbol': 'SOL/USDT', 'order_type': ui_strings.ORDER_TYPE_MARKET, 'side': ui_strings.SIDE_SELL, 'amount': 5.0
        }

        actual_order = self.logic.place_order(
            self.dummy_api_key, self.dummy_secret_key,
            MarketEnvironment.FUTURES_TESTNET, **order_params
        )

        self.assertEqual(actual_order, expected_order_response)
        args, _ = mock_binance_constructor.call_args
        self.assertEqual(args[0].get('options', {}).get('defaultType'), 'future')
        mock_exchange.set_sandbox_mode.assert_called_once_with(True)
        mock_exchange.create_order.assert_called_once_with(
            order_params['symbol'], order_params['order_type'].lower(),
            order_params['side'].lower(), order_params['amount'],
            None, {}
        )

    def test_place_order_invalid_params(self):
        # Base valid parameters, to be overridden by invalid ones
        base_params = {
            'api_key': self.dummy_api_key, 'secret_key': self.dummy_secret_key,
            'market_environment': MarketEnvironment.SPOT, 'symbol': 'BTC/USDT',
            'order_type': ui_strings.ORDER_TYPE_LIMIT, 'side': ui_strings.SIDE_BUY,
            'amount': 1.0, 'price': 30000.0
        }

        invalid_param_cases = [
            ({'symbol': ""}, error_messages.PARAM_SYMBOL_REQUIRED),
            ({'order_type': "INVALID_TYPE"}, error_messages.PARAM_ORDER_TYPE_INVALID),
            ({'side': "INVALID_SIDE"}, error_messages.PARAM_SIDE_INVALID),
            ({'amount': 0}, error_messages.PARAM_AMOUNT_MUST_BE_POSITIVE),
            ({'amount': -1}, error_messages.PARAM_AMOUNT_MUST_BE_POSITIVE),
            # Test price validation specifically for LIMIT orders
            ({'order_type': ui_strings.ORDER_TYPE_LIMIT, 'price': 0}, error_messages.PARAM_PRICE_MUST_BE_POSITIVE_LIMIT),
            ({'order_type': ui_strings.ORDER_TYPE_LIMIT, 'price': -1}, error_messages.PARAM_PRICE_MUST_BE_POSITIVE_LIMIT),
            ({'order_type': ui_strings.ORDER_TYPE_LIMIT, 'price': None}, error_messages.PARAM_PRICE_MUST_BE_POSITIVE_LIMIT),
        ]

        for invalid_data, error_msg in invalid_param_cases:
            with self.subTest(invalid_param_data=invalid_data, expected_error=error_msg):
                # Create a fresh copy of base_params for each subtest
                current_params = base_params.copy()
                # Update with the specific invalid data for this subtest
                current_params.update(invalid_data)

                # Remove price for MARKET order type if it's not the parameter being tested
                if current_params['order_type'] == ui_strings.ORDER_TYPE_MARKET and 'price' not in invalid_data:
                    current_params.pop('price', None) # Remove price if it exists

                with self.assertRaisesRegex(InvalidOrderParamsError, error_msg):
                    self.logic.place_order(**current_params)


    def test_place_order_api_key_missing(self):
        order_params = {
            'market_environment': MarketEnvironment.SPOT, 'symbol': 'BTC/USDT',
            'order_type': ui_strings.ORDER_TYPE_LIMIT, 'side': ui_strings.SIDE_BUY,
            'amount': 1.0, 'price': 30000.0
        }
        with self.assertRaisesRegex(ApiKeyMissingError, error_messages.PARAM_API_KEYS_REQUIRED):
            self.logic.place_order("", self.dummy_secret_key, **order_params)
        with self.assertRaisesRegex(ApiKeyMissingError, error_messages.PARAM_API_KEYS_REQUIRED):
            self.logic.place_order(self.dummy_api_key, "", **order_params)

    @patch('src.app_logic.ccxt.binance')
    def test_place_order_insufficient_funds(self, mock_binance_constructor):
        mock_exchange_instance = MagicMock()
        mock_exchange_instance.create_order.side_effect = ccxt.InsufficientFunds("Test InsufficientFunds")
        mock_binance_constructor.return_value = mock_exchange_instance
        with self.assertRaisesRegex(InsufficientFundsError, "Insufficient funds: Test InsufficientFunds"):
            self.logic.place_order(
                self.dummy_api_key, self.dummy_secret_key, MarketEnvironment.SPOT,
                'BTC/USDT', ui_strings.ORDER_TYPE_LIMIT, ui_strings.SIDE_BUY, 1.0, 30000.0
            )

    @patch('src.app_logic.ccxt.binance')
    def test_place_order_ccxt_invalid_order_error(self, mock_binance_constructor):
        mock_exchange_instance = MagicMock()
        mock_exchange_instance.create_order.side_effect = ccxt.InvalidOrder("Test InvalidOrder from CCXT")
        mock_binance_constructor.return_value = mock_exchange_instance
        with self.assertRaisesRegex(InvalidOrderParamsError, "Invalid order parameters for exchange: Test InvalidOrder from CCXT"):
            self.logic.place_order(
                self.dummy_api_key, self.dummy_secret_key, MarketEnvironment.SPOT,
                'BTC/USDT', ui_strings.ORDER_TYPE_LIMIT, ui_strings.SIDE_BUY, 1.0, 30000.0
            )

    @patch('src.app_logic.ccxt.binance')
    def test_place_order_network_error(self, mock_binance_constructor):
        mock_exchange_instance = MagicMock()
        mock_exchange_instance.create_order.side_effect = ccxt.NetworkError("Test NetworkError")
        mock_binance_constructor.return_value = mock_exchange_instance
        with self.assertRaisesRegex(CustomNetworkError, "Network error during order placement: Test NetworkError"):
            self.logic.place_order(
                self.dummy_api_key, self.dummy_secret_key, MarketEnvironment.SPOT,
                'BTC/USDT', ui_strings.ORDER_TYPE_LIMIT, ui_strings.SIDE_BUY, 1.0, 30000.0
            )

    @patch('src.app_logic.ccxt.binance')
    def test_place_order_exchange_error(self, mock_binance_constructor):
        mock_exchange_instance = MagicMock()
        mock_exchange_instance.create_order.side_effect = ccxt.ExchangeError("Test ExchangeError")
        mock_binance_constructor.return_value = mock_exchange_instance
        with self.assertRaisesRegex(OrderPlacementError, "Binance API error during order placement: Test ExchangeError"):
            self.logic.place_order(
                self.dummy_api_key, self.dummy_secret_key, MarketEnvironment.SPOT,
                'BTC/USDT', ui_strings.ORDER_TYPE_LIMIT, ui_strings.SIDE_BUY, 1.0, 30000.0
            )

    @patch('src.app_logic.ccxt.binance')
    def test_place_order_unexpected_error(self, mock_binance_constructor):
        mock_exchange_instance = MagicMock()
        mock_exchange_instance.create_order.side_effect = Exception("Test Unexpected Exception")
        mock_binance_constructor.return_value = mock_exchange_instance
        with self.assertRaisesRegex(AppLogicError, "An unexpected error occurred during order placement: Test Unexpected Exception"):
            self.logic.place_order(
                self.dummy_api_key, self.dummy_secret_key, MarketEnvironment.SPOT,
                'BTC/USDT', ui_strings.ORDER_TYPE_LIMIT, ui_strings.SIDE_BUY, 1.0, 30000.0
            )

if __name__ == '__main__':
    unittest.main()
