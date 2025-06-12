from typing import Tuple, Optional
from ..app_logic import MarketEnvironment
from ..constants import ui_strings, error_messages

class MarketUtils:
    @staticmethod
    def get_environment_from_text(env_text: str) -> Optional[MarketEnvironment]:
        """
        Convertit le texte de l'environnement en énumération MarketEnvironment.
        
        Args:
            env_text: Le texte de l'environnement sélectionné
            
        Returns:
            L'environnement de marché correspondant ou None si invalide
        """
        if env_text == ui_strings.ENV_SPOT:
            return MarketEnvironment.SPOT
        elif env_text == ui_strings.ENV_FUTURES_LIVE:
            return MarketEnvironment.FUTURES_LIVE
        elif env_text == ui_strings.ENV_FUTURES_TESTNET:
            return MarketEnvironment.FUTURES_TESTNET
        return None

    @staticmethod
    def validate_api_keys(api_key: str, secret_key: str) -> Tuple[bool, Optional[str]]:
        """
        Valide les clés API.
        
        Args:
            api_key: La clé API à valider
            secret_key: La clé secrète à valider
            
        Returns:
            Un tuple contenant :
            - Un booléen indiquant si les clés sont valides
            - Un message d'erreur si les clés sont invalides, None sinon
        """
        if not api_key or not secret_key:
            return False, error_messages.ERROR_API_KEYS_REQUIRED_UI

        api_key = api_key.strip()
        secret_key = secret_key.strip()

        if not api_key or not secret_key:
            return False, error_messages.ERROR_API_KEYS_REQUIRED_UI

        return True, None 