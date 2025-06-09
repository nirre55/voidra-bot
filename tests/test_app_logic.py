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

        balance = self.logic.get_balance(self.dummy_api_key, self.dummy_secret_key)

        self.assertEqual(balance, 123.45)
        mock_binance_constructor.assert_called_once_with({
            'apiKey': self.dummy_api_key,
            'secret': self.dummy_secret_key,
            'options': {'adjustForTimeDifference': True}
        })
        mock_exchange_instance.fetch_balance.assert_called_once()

    @patch('src.app_logic.ccxt.binance')
    def test_get_balance_usdt_missing(self, mock_binance_constructor):
        """Test when USDT is missing from the balance data."""
        mock_exchange_instance = MagicMock()
        mock_exchange_instance.fetch_balance.return_value = {'total': {'BTC': 1.0}} # USDT missing
        mock_binance_constructor.return_value = mock_exchange_instance

        balance = self.logic.get_balance(self.dummy_api_key, self.dummy_secret_key)

        self.assertEqual(balance, 0.0)
        mock_binance_constructor.assert_called_once_with({
            'apiKey': self.dummy_api_key,
            'secret': self.dummy_secret_key,
            'options': {'adjustForTimeDifference': True}
        })
        mock_exchange_instance.fetch_balance.assert_called_once()

    @patch('src.app_logic.ccxt.binance')
    def test_get_balance_total_missing(self, mock_binance_constructor):
        """Test when 'total' key is missing from the balance data."""
        mock_exchange_instance = MagicMock()
        mock_exchange_instance.fetch_balance.return_value = {'free': {'USDT': 10.0}} # 'total' key missing
        mock_binance_constructor.return_value = mock_exchange_instance

        balance = self.logic.get_balance(self.dummy_api_key, self.dummy_secret_key)

        self.assertEqual(balance, 0.0) # Should default to 0.0 if path to USDT is broken

    def test_get_balance_api_key_missing(self):
        """Test calling get_balance with missing API key."""
        with self.assertRaisesRegex(ApiKeyMissingError, "API Key and Secret Key are required."):
            self.logic.get_balance("", self.dummy_secret_key)

        with self.assertRaisesRegex(ApiKeyMissingError, "API Key and Secret Key are required."):
            self.logic.get_balance(self.dummy_api_key, "")

        with self.assertRaisesRegex(ApiKeyMissingError, "API Key and Secret Key are required."):
            self.logic.get_balance(None, self.dummy_secret_key)

        with self.assertRaisesRegex(ApiKeyMissingError, "API Key and Secret Key are required."):
            self.logic.get_balance(self.dummy_api_key, None)

        with self.assertRaisesRegex(ApiKeyMissingError, "API Key and Secret Key are required."):
            self.logic.get_balance(None, None)

    @patch('src.app_logic.ccxt.binance')
    def test_get_balance_network_error(self, mock_binance_constructor):
        """Test handling of ccxt.NetworkError."""
        mock_exchange_instance = MagicMock()
        mock_exchange_instance.fetch_balance.side_effect = ccxt.NetworkError("Connection failed")
        mock_binance_constructor.return_value = mock_exchange_instance

        with self.assertRaisesRegex(CustomNetworkError, "Network error connecting to Binance: Connection failed"):
            self.logic.get_balance(self.dummy_api_key, self.dummy_secret_key)

    @patch('src.app_logic.ccxt.binance')
    def test_get_balance_exchange_error(self, mock_binance_constructor):
        """Test handling of ccxt.ExchangeError."""
        mock_exchange_instance = MagicMock()
        mock_exchange_instance.fetch_balance.side_effect = ccxt.ExchangeError("Invalid API key")
        mock_binance_constructor.return_value = mock_exchange_instance

        with self.assertRaisesRegex(CustomExchangeError, "Binance API error: Invalid API key"):
            self.logic.get_balance(self.dummy_api_key, self.dummy_secret_key)

    @patch('src.app_logic.ccxt.binance')
    def test_get_balance_unexpected_error(self, mock_binance_constructor):
        """Test handling of other unexpected errors."""
        mock_exchange_instance = MagicMock()
        mock_exchange_instance.fetch_balance.side_effect = RuntimeError("Something went very wrong")
        mock_binance_constructor.return_value = mock_exchange_instance

        expected_message = "An unexpected error occurred in application logic: Something went very wrong"
        with self.assertRaisesRegex(AppLogicError, expected_message):
            self.logic.get_balance(self.dummy_api_key, self.dummy_secret_key)

if __name__ == '__main__':
    unittest.main()
