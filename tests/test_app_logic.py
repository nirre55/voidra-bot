import unittest
from unittest.mock import patch, MagicMock
import ccxt # Required for ccxt.NetworkError, ccxt.ExchangeError
from src.app_logic import (
    BinanceLogic,
    ApiKeyMissingError,
    CustomNetworkError,
    CustomExchangeError,
    AppLogicError # Though not explicitly testing raising this directly, good to have if logic changes
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

        balance = self.logic.get_balance(self.dummy_api_key, self.dummy_secret_key, use_futures_testnet=False)

        self.assertEqual(balance, 123.45)
        args, kwargs = mock_binance_constructor.call_args
        self.assertEqual(args[0]['apiKey'], self.dummy_api_key)
        self.assertEqual(args[0]['secret'], self.dummy_secret_key)
        self.assertNotIn('defaultType', args[0].get('options', {})) # Check defaultType not set for spot
        mock_exchange_instance.set_sandbox_mode.assert_not_called()
        mock_exchange_instance.fetch_balance.assert_called_once()

    @patch('src.app_logic.ccxt.binance')
    def test_get_balance_usdt_missing(self, mock_binance_constructor):
        """Test when USDT is missing from the balance data."""
        mock_exchange_instance = MagicMock()
        mock_exchange_instance.fetch_balance.return_value = {'total': {'BTC': 1.0}} # USDT missing
        mock_binance_constructor.return_value = mock_exchange_instance

        balance = self.logic.get_balance(self.dummy_api_key, self.dummy_secret_key, use_futures_testnet=False)

        self.assertEqual(balance, 0.0)
        # Basic check for constructor call, detailed check in success test
        mock_binance_constructor.assert_called_once()
        mock_exchange_instance.fetch_balance.assert_called_once()

    @patch('src.app_logic.ccxt.binance')
    def test_get_balance_total_missing(self, mock_binance_constructor):
        """Test when 'total' key is missing from the balance data."""
        mock_exchange_instance = MagicMock()
        mock_exchange_instance.fetch_balance.return_value = {'free': {'USDT': 10.0}} # 'total' key missing
        mock_binance_constructor.return_value = mock_exchange_instance

        balance = self.logic.get_balance(self.dummy_api_key, self.dummy_secret_key, use_futures_testnet=False)

        self.assertEqual(balance, 0.0) # Should default to 0.0 if path to USDT is broken

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
            with self.subTest(api_key=api_key, secret_key=secret_key, use_futures=False):
                with self.assertRaisesRegex(ApiKeyMissingError, "API Key and Secret Key are required."):
                    self.logic.get_balance(api_key, secret_key, use_futures_testnet=False)
            with self.subTest(api_key=api_key, secret_key=secret_key, use_futures=True):
                with self.assertRaisesRegex(ApiKeyMissingError, "API Key and Secret Key are required."):
                    self.logic.get_balance(api_key, secret_key, use_futures_testnet=True)

    @patch('src.app_logic.ccxt.binance')
    def test_get_balance_network_error(self, mock_binance_constructor):
        """Test handling of ccxt.NetworkError."""
        mock_exchange_instance = MagicMock()
        mock_exchange_instance.fetch_balance.side_effect = ccxt.NetworkError("Connection failed")
        mock_binance_constructor.return_value = mock_exchange_instance

        with self.assertRaisesRegex(CustomNetworkError, "Network error connecting to Binance: Connection failed"):
            self.logic.get_balance(self.dummy_api_key, self.dummy_secret_key, use_futures_testnet=False)

    @patch('src.app_logic.ccxt.binance')
    def test_get_balance_exchange_error(self, mock_binance_constructor):
        """Test handling of ccxt.ExchangeError."""
        mock_exchange_instance = MagicMock()
        mock_exchange_instance.fetch_balance.side_effect = ccxt.ExchangeError("Invalid API key")
        mock_binance_constructor.return_value = mock_exchange_instance

        with self.assertRaisesRegex(CustomExchangeError, "Binance API error: Invalid API key"):
            self.logic.get_balance(self.dummy_api_key, self.dummy_secret_key, use_futures_testnet=False)

    @patch('src.app_logic.ccxt.binance')
    def test_get_balance_unexpected_error(self, mock_binance_constructor):
        """Test handling of other unexpected errors."""
        mock_exchange_instance = MagicMock()
        mock_exchange_instance.fetch_balance.side_effect = RuntimeError("Something went very wrong")
        mock_binance_constructor.return_value = mock_exchange_instance

        expected_message = "An unexpected error occurred in application logic: Something went very wrong"
        with self.assertRaisesRegex(AppLogicError, expected_message):
            self.logic.get_balance(self.dummy_api_key, self.dummy_secret_key, use_futures_testnet=False)

    @patch('src.app_logic.ccxt.binance')
    def test_get_balance_futures_testnet_success(self, mock_binance_constructor):
        """Test successful balance retrieval from Futures Testnet."""
        mock_exchange_instance = MagicMock()
        mock_exchange_instance.fetch_balance.return_value = {'total': {'USDT': 500.75}}
        mock_binance_constructor.return_value = mock_exchange_instance

        balance = self.logic.get_balance(self.dummy_api_key, self.dummy_secret_key, use_futures_testnet=True)

        self.assertEqual(balance, 500.75)

        args, kwargs = mock_binance_constructor.call_args
        self.assertEqual(args[0]['apiKey'], self.dummy_api_key)
        self.assertEqual(args[0]['secret'], self.dummy_secret_key)
        self.assertIn('options', args[0])
        self.assertEqual(args[0]['options'].get('defaultType'), 'future') # Check defaultType is 'future'

        mock_exchange_instance.set_sandbox_mode.assert_called_once_with(True)
        mock_exchange_instance.fetch_balance.assert_called_once()

if __name__ == '__main__':
    unittest.main()
