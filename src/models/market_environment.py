import enum

class MarketEnvironment(enum.Enum):
    SPOT = "SPOT"
    FUTURES_LIVE = "FUTURES_LIVE"
    FUTURES_TESTNET = "FUTURES_TESTNET" 