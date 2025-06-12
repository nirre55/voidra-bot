from src.app_logic import (
    BinanceLogic,
    MarketEnvironment,
    ApiKeyMissingError,
    InvalidOrderParamsError,
    InsufficientFundsError,
    OrderPlacementError,
    CustomNetworkError,
    AppLogicError,
)

if __name__ == "__main__":
    print("Testing BinanceLogic...")
    logic = BinanceLogic()

    print("\nTest Case: Get Balance (SPOT - requires valid read-only keys)")
    try:
        logic.get_balance("", "", MarketEnvironment.SPOT)
    except ApiKeyMissingError as e:
        print(f"Caught expected error for get_balance: {e}")
    except Exception as e:
        print(f"Error during get_balance test: {e}")

    print("\nTest Case: Place Order (FUTURES_TESTNET - requires valid Futures Testnet keys)")
    testnet_api_key = "YOUR_FUTURES_TESTNET_API_KEY"
    testnet_secret_key = "YOUR_FUTURES_TESTNET_SECRET_KEY"

    if testnet_api_key == "YOUR_FUTURES_TESTNET_API_KEY" or testnet_secret_key == "YOUR_FUTURES_TESTNET_SECRET_KEY":
        print("Skipping place_order test as placeholder API keys are used.")
        print("Replace with your actual Binance Futures Testnet API keys to run this test.")
    else:
        try:
            order_details = logic.place_order(
                api_key=testnet_api_key,
                secret_key=testnet_secret_key,
                market_environment=MarketEnvironment.FUTURES_TESTNET,
                symbol="BTC/USDT",
                order_type="LIMIT",
                side="BUY",
                amount=0.001,
                price=20000,
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
