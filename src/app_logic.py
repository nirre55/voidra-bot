import ccxt

# Custom Exceptions
class ApiKeyMissingError(ValueError): # Inherit from ValueError for semantic correctness
    """Custom exception for missing API key or secret."""
    pass

class CustomNetworkError(Exception):
    """Custom exception for CCXT network errors."""
    pass

class CustomExchangeError(Exception):
    """Custom exception for CCXT exchange errors."""
    pass

class AppLogicError(Exception):
    """Custom exception for other application logic errors."""
    pass

class BinanceLogic:
    def __init__(self):
        """
        Initializes the BinanceLogic class.
        For this design, API keys are passed directly to the get_balance method.
        An exchange instance is not stored long-term here to allow for key changes.
        """
        pass

    def get_balance(self, api_key: str, secret_key: str, use_futures_testnet: bool = False) -> float:
        """
        Fetches the total USDT balance from Binance.

        Args:
            api_key: The Binance API key.
            secret_key: The Binance secret key.
            use_futures_testnet: If True, uses Binance Futures Testnet. Defaults to False.

        Returns:
            The total USDT balance as a float.

        Raises:
            ApiKeyMissingError: If API key or secret key is not provided.
            CustomNetworkError: If there's a network issue connecting to Binance.
            CustomExchangeError: If Binance API returns an error.
            AppLogicError: For any other unexpected errors during the process.
        """
        if not api_key or not secret_key:
            raise ApiKeyMissingError("API Key and Secret Key are required.")

        try:
            exchange_config = {
                'apiKey': api_key,
                'secret': secret_key,
                'options': {
                    'adjustForTimeDifference': True,
                }
            }
            if use_futures_testnet:
                # For futures, 'defaultType': 'future' might be needed for some ccxt versions or specific endpoints
                # and set_sandbox_mode(True) is crucial for testnet.
                exchange_config['options']['defaultType'] = 'future'

            exchange = ccxt.binance(exchange_config)

            if use_futures_testnet:
                exchange.set_sandbox_mode(True)

            # Fetch the balance
            # Note: The structure of balance_data might differ slightly between spot and futures.
            # For USDT, it's often found under 'total', 'free', or directly in the asset list.
            # This implementation assumes 'total' for simplicity, adjust if needed based on ccxt's futures balance structure.
            balance_data = exchange.fetch_balance()

            # Extract the total USDT balance
            # The structure of balance_data can vary; 'total' usually holds overall balances
            usdt_balance = balance_data.get('total', {}).get('USDT', 0.0)

            return float(usdt_balance)

        except ccxt.NetworkError as e:
            # Handle network errors (e.g., connection timeout, DNS issues)
            raise CustomNetworkError(f"Network error connecting to Binance: {str(e)}")
        except ccxt.ExchangeError as e:
            # Handle errors returned by the Binance API (e.g., invalid API key, insufficient permissions)
            raise CustomExchangeError(f"Binance API error: {str(e)}")
        except Exception as e:
            # Handle any other unexpected errors
            # In a real application, you might want to log the original exception e
            # print(f"Original exception: {type(e).__name__} - {e}") # For debugging
            raise AppLogicError(f"An unexpected error occurred in application logic: {str(e)}")

if __name__ == '__main__':
    # This section is for basic testing of the BinanceLogic class.
    # It will not run when the module is imported elsewhere.
    print("Testing BinanceLogic...")
    logic = BinanceLogic()

    # Test case 1: Missing API keys
    print("\nTest Case 1: Missing API Keys")
    try:
        logic.get_balance("", "")
    except ApiKeyMissingError as e:
        print(f"Caught expected error: {e}")
    except Exception as e:
        print(f"Caught unexpected error: {e}")

    # Test case 2: Dummy API keys (will likely cause an ExchangeError)
    # Replace with your actual (read-only) keys for a real test, but be cautious.
    print("\nTest Case 2: Dummy API Keys (expecting CustomExchangeError or CustomNetworkError)")
    dummy_api_key = "YOUR_DUMMY_API_KEY"
    dummy_secret_key = "YOUR_DUMMY_SECRET_KEY"
    try:
        balance = logic.get_balance(dummy_api_key, dummy_secret_key)
        print(f"USDT Balance: {balance}")
    except ApiKeyMissingError as e:
        print(f"Caught ApiKeyMissingError: {e}")
    except CustomNetworkError as e:
        print(f"Caught CustomNetworkError: {e}")
    except CustomExchangeError as e:
        print(f"Caught CustomExchangeError: {e}")
    except AppLogicError as e:
        print(f"Caught AppLogicError: {e}")
    except Exception as e:
        print(f"Caught unexpected error: {e}")

    print("\nNote: For Test Case 2, ccxt might raise various errors depending on network and key validity.")
    print("A common error for invalid keys is 'binance Account has insufficient balance for requested action.' or similar.")
    print("If you have no internet, a NetworkError is expected.")
