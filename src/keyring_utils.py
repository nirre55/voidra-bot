import keyring
import keyring.errors # For NoKeyringError
from .constants import ui_strings # To get APP_NAME_KEYRING

# SERVICE_NAME will be based on the application's name for keyring storage
SERVICE_NAME = ui_strings.APP_NAME # Use APP_NAME from ui_strings, assuming it will be defined appropriately for keyring.

def _get_username_api_key(environment_name_value: str) -> str:
    """Generates the username for storing the API key for a given environment."""
    return f"{environment_name_value}_API_KEY"

def _get_username_secret_key(environment_name_value: str) -> str:
    """Generates the username for storing the Secret key for a given environment."""
    return f"{environment_name_value}_SECRET_KEY"

def save_creds(environment_name_value: str, api_key: str, secret_key: str) -> bool:
    """
    Saves API key and secret key to the system keyring for the given environment.
    environment_name_value should be the .value of the MarketEnvironment enum.
    Returns True on success, False on failure.
    """
    try:
        keyring.set_password(SERVICE_NAME, _get_username_api_key(environment_name_value), api_key)
        keyring.set_password(SERVICE_NAME, _get_username_secret_key(environment_name_value), secret_key)
        # print(f"Credentials saved for {environment_name_value} in service {SERVICE_NAME}") # For debugging
        return True
    except keyring.errors.NoKeyringError:
        print(f"Keyring backend not found. Cannot save credentials for {environment_name_value}.")
        # In a real app, this might be logged or reported to user via a status mechanism
        return False
    except Exception as e:
        print(f"An unexpected error occurred while saving credentials for {environment_name_value}: {e}")
        return False

def load_creds(environment_name_value: str) -> tuple[str | None, str | None]:
    """
    Loads API key and secret key from the system keyring for the given environment.
    environment_name_value should be the .value of the MarketEnvironment enum.
    Returns (api_key, secret_key) or (None, None) if not found or error.
    """
    try:
        api_key_username = _get_username_api_key(environment_name_value)
        secret_key_username = _get_username_secret_key(environment_name_value)

        api_key = keyring.get_password(SERVICE_NAME, api_key_username)
        secret_key = keyring.get_password(SERVICE_NAME, secret_key_username)

        if api_key is not None and secret_key is not None:
            # print(f"Credentials loaded for {environment_name_value} from service {SERVICE_NAME}") # For debugging
            return api_key, secret_key
        else:
            # This means one or both were not found, which is a normal case if not saved yet.
            # print(f"No complete credentials found for {environment_name_value} in service {SERVICE_NAME}")
            return None, None

    except keyring.errors.NoKeyringError:
        print("Keyring backend not found. Cannot load credentials.")
        return None, None
    except Exception as e:
        print(f"An unexpected error occurred while loading credentials for {environment_name_value}: {e}")
        return None, None

def delete_creds(environment_name_value: str) -> bool:
    """
    Deletes API key and secret key from the system keyring for the given environment.
    environment_name_value should be the .value of the MarketEnvironment enum.
    Returns True on success or if credentials didn't exist, False on error.
    """
    try:
        api_key_username = _get_username_api_key(environment_name_value)
        secret_key_username = _get_username_secret_key(environment_name_value)

        # Try to delete. keyring.delete_password usually doesn't error if not found.
        # Check if credentials exist before attempting to delete to avoid potential NoKeyringError on some backends if item not found
        api_key = keyring.get_password(SERVICE_NAME, api_key_username)
        if api_key is not None:
            keyring.delete_password(SERVICE_NAME, api_key_username)

        secret_key = keyring.get_password(SERVICE_NAME, secret_key_username)
        if secret_key is not None:
            keyring.delete_password(SERVICE_NAME, secret_key_username)

        # print(f"Credentials deleted (or did not exist) for {environment_name_value} in service {SERVICE_NAME}") # For debugging
        return True
    except keyring.errors.NoKeyringError:
        print(f"Keyring backend not found. Cannot delete credentials for {environment_name_value}.")
        return False
    except Exception as e:
        print(f"An unexpected error occurred while deleting credentials for {environment_name_value}: {e}")
        return False

