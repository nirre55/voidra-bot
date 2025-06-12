import ccxt
from typing import Optional
from ..app_logic import MarketEnvironment

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
        exchange_config = {
            'apiKey': api_key,
            'secret': secret_key,
            'options': {'adjustForTimeDifference': True}
        }

        # Configuration spécifique pour les futures
        if market_env in [MarketEnvironment.FUTURES_LIVE, MarketEnvironment.FUTURES_TESTNET]:
            exchange_config['options']['defaultType'] = 'future'

        exchange = ccxt.binance(**exchange_config)

        # Activation du mode testnet si nécessaire
        if market_env == MarketEnvironment.FUTURES_TESTNET:
            exchange.set_sandbox_mode(True)

        return exchange 