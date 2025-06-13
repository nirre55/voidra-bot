import ccxt
from typing import Optional
from ..models.market_environment import MarketEnvironment

class ExchangeFactory:
    @staticmethod
    def create(api_key: str, secret_key: str, market_env: MarketEnvironment) -> ccxt.Exchange:
        """
        Crée une instance d'exchange configurée selon l'environnement spécifié.
        
        Args:
            api_key: La clé API Binance
            secret_key: La clé secrète Binance
            market_env: L'environnement de marché (SPOT, FUTURES_LIVE, FUTURES_TESTNET)
            
        Returns:
            Une instance configurée de l'exchange Binance
        """
        exchange = ccxt.binance()
        exchange.apiKey = api_key
        exchange.secret = secret_key
        exchange.options = getattr(exchange, 'options', {})
        exchange.options['adjustForTimeDifference'] = True

        # Configuration spécifique pour les futures
        if market_env in [MarketEnvironment.FUTURES_LIVE, MarketEnvironment.FUTURES_TESTNET]:
            exchange.options['defaultType'] = 'future'

        # Activation du mode testnet si nécessaire
        if market_env == MarketEnvironment.FUTURES_TESTNET:
            exchange.set_sandbox_mode(True)

        return exchange 