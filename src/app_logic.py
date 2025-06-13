import ccxt
from ccxt.base.types import ConstructorArgs, OrderType, OrderSide
from typing import Optional, Literal, cast
from .constants import error_messages, ui_strings
from .services.exchange_factory import ExchangeFactory
from .models.market_environment import MarketEnvironment

# Custom Exceptions
class ApiKeyMissingError(Exception):
    """Exception raised when API keys are missing."""
    pass

class CustomNetworkError(Exception):
    """Custom exception for CCXT network errors."""
    pass

class CustomExchangeError(Exception):
    """Custom exception for CCXT exchange errors."""
    pass

class AppLogicError(Exception):
    """Exception for unexpected errors in application logic."""
    pass

# Order Specific Exceptions
class OrderPlacementError(Exception):
    """Exception for order placement errors."""
    pass

class InsufficientFundsError(Exception):
    """Exception for insufficient funds errors."""
    pass

class InvalidOrderParamsError(Exception):
    """Exception for invalid order parameters."""
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
            exchange = ExchangeFactory.create(api_key, secret_key, market_environment)
            balance_data = exchange.fetch_balance()
            usdt_balance = balance_data.get('total', {}).get('USDT', 0.0)
            return float(usdt_balance)

        except ccxt.NetworkError as e:
            raise CustomNetworkError(f"Network error connecting to Binance: {str(e)}")
        except ccxt.ExchangeError as e:
            raise CustomExchangeError(f"Binance API error: {str(e)}")
        except Exception as e:
            raise AppLogicError(f"An unexpected error occurred in application logic: {str(e)}")

    def place_order(self,
                    api_key: str,
                    secret_key: str,
                    market_environment: MarketEnvironment,
                    symbol: str,
                    order_type: str,
                    side: str,
                    amount: float,
                    price: Optional[float] = None,
                    margin_mode: Optional[str] = None,
                    leverage: Optional[int] = None):
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

        try:
            exchange = ExchangeFactory.create(api_key, secret_key, market_environment)

            # Futures-specific setup: Margin Mode and Leverage
            if market_environment in [MarketEnvironment.FUTURES_LIVE, MarketEnvironment.FUTURES_TESTNET]:
                if symbol and margin_mode and leverage is not None:
                    ccxt_margin_mode = ""
                    if margin_mode == ui_strings.MERGE_MODE_ISOLATED:
                        ccxt_margin_mode = "ISOLATED"
                    elif margin_mode == ui_strings.MERGE_MODE_CROSS:
                        ccxt_margin_mode = "CROSSED"

                    if ccxt_margin_mode:
                        try:
                            exchange.set_margin_mode(ccxt_margin_mode, symbol, params={'adjustForTimeDifference': True})
                        except ccxt.ExchangeError as e_margin:
                            raise OrderPlacementError(f"Failed to set margin mode to {ccxt_margin_mode} for {symbol}: {str(e_margin)}")
                        except Exception as e_generic_margin:
                            raise OrderPlacementError(f"Unexpected error setting margin mode for {symbol}: {str(e_generic_margin)}")

                    if leverage > 0:
                        try:
                            exchange.set_leverage(leverage, symbol, params={'adjustForTimeDifference': True})
                        except ccxt.ExchangeError as e_leverage:
                            raise OrderPlacementError(f"Failed to set leverage to {leverage} for {symbol}: {str(e_leverage)}")
                        except Exception as e_generic_leverage:
                            raise OrderPlacementError(f"Unexpected error setting leverage for {symbol}: {str(e_generic_leverage)}")

            ccxt_order_type = cast(OrderType, order_type.lower())
            ccxt_side = cast(OrderSide, side.lower())
            
            assert ccxt_order_type in ['limit', 'market'], f"Invalid order type: {ccxt_order_type}"
            assert ccxt_side in ['buy', 'sell'], f"Invalid order side: {ccxt_side}"

            final_price = None
            if order_type.upper() == ui_strings.ORDER_TYPE_LIMIT:
                final_price = price

            order_response = exchange.create_order(symbol, ccxt_order_type, ccxt_side, amount, final_price, {})
            return order_response

        except ccxt.InsufficientFunds as e:
            raise InsufficientFundsError(f"Insufficient funds: {str(e)}")
        except ccxt.InvalidOrder as e:
            raise InvalidOrderParamsError(f"Invalid order parameters for exchange: {str(e)}")
        except ccxt.NetworkError as e:
            raise CustomNetworkError(f"Network error during order placement: {str(e)}")
        except ccxt.ExchangeError as e:
            raise OrderPlacementError(f"Binance API error during order placement: {str(e)}")
        except InvalidOrderParamsError:
            raise
        except Exception as e:
            raise AppLogicError(f"An unexpected error occurred during order placement: {str(e)}")
