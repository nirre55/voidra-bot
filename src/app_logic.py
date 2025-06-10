import ccxt
import enum
from .constants import error_messages, ui_strings # Added ui_strings for order types/sides

# Market Environment Enum
class MarketEnvironment(enum.Enum):
    SPOT = "SPOT"
    FUTURES_LIVE = "FUTURES_LIVE"
    FUTURES_TESTNET = "FUTURES_TESTNET"

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

# Order Specific Exceptions
class OrderPlacementError(Exception): # General order error
    pass

class InsufficientFundsError(OrderPlacementError): # Specific type of order error
    pass

class InvalidOrderParamsError(ValueError): # For issues with parameters before sending to API
    pass

class BinanceLogic:
    def __init__(self):
        """
        Initializes the BinanceLogic class.
        For this design, API keys are passed directly to the get_balance method.
        An exchange instance is not stored long-term here to allow for key changes.
        """
        pass

    def get_balance(self, api_key: str, secret_key: str, market_environment: MarketEnvironment) -> float:
        """
        Fetches the total USDT balance from Binance.

        Args:
            api_key: The Binance API key.
            secret_key: The Binance secret key.
            market_environment: The market environment (SPOT, FUTURES_LIVE, FUTURES_TESTNET).

        Returns:
            The total USDT balance as a float.

        Raises:
            ApiKeyMissingError: If API key or secret key is not provided.
            CustomNetworkError: If there's a network issue connecting to Binance.
            CustomExchangeError: If Binance API returns an error.
            AppLogicError: For any other unexpected errors during the process.
        """
        if not api_key or not secret_key:
            raise ApiKeyMissingError(error_messages.PARAM_API_KEYS_REQUIRED)

        try:
            exchange_config = {
                'apiKey': api_key,
                'secret': secret_key,
                'options': {'adjustForTimeDifference': True}
            }

            if market_environment == MarketEnvironment.FUTURES_LIVE:
                exchange_config['options']['defaultType'] = 'future'
            elif market_environment == MarketEnvironment.FUTURES_TESTNET:
                exchange_config['options']['defaultType'] = 'future'
            # For SPOT, 'defaultType' is usually not needed or defaults to 'spot'

            exchange = ccxt.binance(exchange_config)

            if market_environment == MarketEnvironment.FUTURES_TESTNET:
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

    def place_order(self,
                    api_key: str,
                    secret_key: str,
                    market_environment: MarketEnvironment,
                    symbol: str,
                    order_type: str, # e.g., 'LIMIT', 'MARKET'
                    side: str,       # e.g., 'BUY', 'SELL'
                    amount: float,
                    price: float = None): # Price is optional, for MARKET orders
        if not api_key or not secret_key:
            raise ApiKeyMissingError(error_messages.PARAM_API_KEYS_REQUIRED)
        if not symbol:
            raise InvalidOrderParamsError(error_messages.PARAM_SYMBOL_REQUIRED)
        if order_type.upper() not in [ui_strings.ORDER_TYPE_LIMIT, ui_strings.ORDER_TYPE_MARKET]:
            raise InvalidOrderParamsError(error_messages.PARAM_ORDER_TYPE_INVALID)
        if side.upper() not in [ui_strings.SIDE_BUY, ui_strings.SIDE_SELL]:
            raise InvalidOrderParamsError(error_messages.PARAM_SIDE_INVALID)
        if amount <= 0:
            raise InvalidOrderParamsError(error_messages.PARAM_AMOUNT_MUST_BE_POSITIVE)
        if order_type.upper() == ui_strings.ORDER_TYPE_LIMIT and (price is None or price <= 0):
            raise InvalidOrderParamsError(error_messages.PARAM_PRICE_MUST_BE_POSITIVE_LIMIT)

        exchange_config = {
            'apiKey': api_key,
            'secret': secret_key,
            'options': {'adjustForTimeDifference': True}
        }

        if market_environment == MarketEnvironment.FUTURES_LIVE:
            exchange_config['options']['defaultType'] = 'future'
        elif market_environment == MarketEnvironment.FUTURES_TESTNET:
            exchange_config['options']['defaultType'] = 'future'
        # For SPOT, no 'defaultType' change needed here for placing orders usually.

        try:
            exchange = ccxt.binance(exchange_config)
            if market_environment == MarketEnvironment.FUTURES_TESTNET:
                exchange.set_sandbox_mode(True)

            # Prepare params for create_order
            ccxt_order_type = order_type.lower()
            ccxt_side = side.lower()

            final_price = None
            if order_type.upper() == ui_strings.ORDER_TYPE_LIMIT: # Use ui_strings constant
                final_price = price

            # The 'params' argument can be used for non-standard parameters if needed.
            order_response = exchange.create_order(symbol, ccxt_order_type, ccxt_side, amount, final_price, {})
            return order_response # Return the full order response from CCXT

        except ccxt.InsufficientFunds as e:
            raise InsufficientFundsError(f"Insufficient funds: {str(e)}")
        except ccxt.InvalidOrder as e: # Covers various order logical errors like invalid price, size etc.
            raise InvalidOrderParamsError(f"Invalid order parameters for exchange: {str(e)}")
        except ccxt.NetworkError as e:
            raise CustomNetworkError(f"Network error during order placement: {str(e)}")
        # Ensure ExchangeError is caught after more specific CCXT errors like InvalidOrder
        except ccxt.ExchangeError as e:
            raise OrderPlacementError(f"Binance API error during order placement: {str(e)}")
        except InvalidOrderParamsError: # Re-raise if caught from our own validation (should not happen if logic is correct here)
            raise
        except Exception as e:
            # Log original error e here in a real app
            # print(f"Original exception: {type(e).__name__} - {e}") # For debugging
            raise AppLogicError(f"An unexpected error occurred during order placement: {str(e)}")


if __name__ == '__main__':
    # This section is for basic testing of the BinanceLogic class.
    # It will not run when the module is imported elsewhere.
    print("Testing BinanceLogic...")
    logic = BinanceLogic()

    # Example usage for get_balance (replace with actual test keys for real test)
    print("\nTest Case: Get Balance (SPOT - requires valid read-only keys)")
    try:
        # balance = logic.get_balance("YOUR_API_KEY", "YOUR_SECRET_KEY", MarketEnvironment.SPOT)
        # print(f"SPOT USDT Balance: {balance}")
        logic.get_balance("", "", MarketEnvironment.SPOT) # Test ApiKeyMissingError
    except ApiKeyMissingError as e:
        print(f"Caught expected error for get_balance: {e}")
    except Exception as e:
        print(f"Error during get_balance test: {e}")

    # Example usage for place_order (VERY CAREFUL WITH REAL KEYS - USE TESTNET)
    print("\nTest Case: Place Order (FUTURES_TESTNET - requires valid Futures Testnet keys)")
    # Ensure you have separate API keys for Binance Futures Testnet
    # These keys are DIFFERENT from your live Binance keys.
    # Get them from: https://testnet.binancefuture.com/
    testnet_api_key = "YOUR_FUTURES_TESTNET_API_KEY"
    testnet_secret_key = "YOUR_FUTURES_TESTNET_SECRET_KEY"

    if testnet_api_key == "YOUR_FUTURES_TESTNET_API_KEY" or testnet_secret_key == "YOUR_FUTURES_TESTNET_SECRET_KEY":
        print("Skipping place_order test as placeholder API keys are used.")
        print("Replace with your actual Binance Futures Testnet API keys to run this test.")
    else:
        try:
            # Example: Place a LIMIT BUY order on BTC/USDT futures testnet
            # Symbol for futures might be 'BTCUSDT' (without '/') depending on CCXT/exchange
            order_details = logic.place_order(
                api_key=testnet_api_key,
                secret_key=testnet_secret_key,
                market_environment=MarketEnvironment.FUTURES_TESTNET,
                symbol="BTC/USDT",  # Or "BTCUSDT" - check CCXT documentation for futures symbols
                order_type="LIMIT",
                side="BUY",
                amount=0.001,      # Example amount (e.g., 0.001 BTC)
                price=20000        # Example price (e.g., $20,000 for BTC)
            )
            print(f"Order placed successfully on Futures Testnet: {order_details}")
        except ApiKeyMissingError as e:
            print(f"ApiKeyMissingError for place_order: {e}")
        except InvalidOrderParamsError as e:
            print(f"InvalidOrderParamsError for place_order: {e}")
        except InsufficientFundsError as e:
            print(f"InsufficientFundsError for place_order: {e}")
        except OrderPlacementError as e:
            print(f"OrderPlacementError for place_order: {e}")
        except CustomNetworkError as e:
            print(f"NetworkError for place_order: {e}")
        except AppLogicError as e:
            print(f"AppLogicError for place_order: {e}")
        except Exception as e:
            print(f"Unexpected error during place_order test: {e}")
