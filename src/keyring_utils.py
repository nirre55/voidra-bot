import keyring
import keyring.errors # For NoKeyringError
from .constants import ui_strings # To get APP_NAME_KEYRING

# SERVICE_NAME will be based on the application's name for keyring storage
SERVICE_NAME = ui_strings.APP_NAME_KEYRING  # Use APP_NAME_KEYRING from ui_strings for keyring operations

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

if __name__ == '__main__':
    # This block is for basic, isolated testing of these functions.
    # It requires a keyring backend.
    # It uses a fixed service name for testing to avoid conflicts and dependency on ui_strings here.
    _TEST_SERVICE_NAME_FOR_MAIN = "BinanceMultiApp_KeyringUtils_DirectTest"

    # Temporarily patch SERVICE_NAME for this test block if ui_strings.APP_NAME_KEYRING is not yet defined
    # This is a bit of a hack for isolated testing. In the actual app, SERVICE_NAME will be set from ui_strings.
    _original_service_name = SERVICE_NAME
    try:
        # Try to use the imported SERVICE_NAME first
        SERVICE_NAME = ui_strings.APP_NAME_KEYRING
    except AttributeError:  # If ui_strings.APP_NAME_KEYRING is not yet defined
        SERVICE_NAME = _TEST_SERVICE_NAME_FOR_MAIN

    print(f"Using service name for testing: {SERVICE_NAME}")

    env_spot_test = "SPOT_KEYRING_TEST"

    print(f"\n--- Testing {env_spot_test} ---")
    if save_creds(env_spot_test, "spot_api_key_123_test", "spot_secret_key_789_test"):
        print(f"Saved creds for {env_spot_test}")
        loaded_api, loaded_secret = load_creds(env_spot_test)
        if loaded_api and loaded_secret:
            print(f"Loaded for {env_spot_test}: API={loaded_api}, Secret={loaded_secret}")
            assert loaded_api == "spot_api_key_123_test"
            assert loaded_secret == "spot_secret_key_789_test"
            print("Load assertion passed.")
        else:
            print(f"Failed to load credentials for {env_spot_test} after saving.")

        if delete_creds(env_spot_test):
            print(f"Attempted to delete credentials for {env_spot_test}.")
            loaded_api_after_delete, loaded_secret_after_delete = load_creds(env_spot_test)
            if loaded_api_after_delete is None and loaded_secret_after_delete is None:
                print(f"Credentials successfully verified as deleted for {env_spot_test}.")
            else:
                print(f"Credentials still found for {env_spot_test} after attempting delete: API={loaded_api_after_delete}, Secret={loaded_secret_after_delete}")
        else:
            print(f"Failed to delete credentials for {env_spot_test}.")
    else:
        print(f"Failed to save credentials for {env_spot_test}. Keyring backend might be missing or not configured.")

    # Restore original SERVICE_NAME if it was changed
    SERVICE_NAME = _original_service_name
    print(f"\nRestored service name to: {SERVICE_NAME if SERVICE_NAME else 'ui_strings.APP_NAME_KEYRING (pending definition)'}")
    print("\nNote: If 'Keyring backend not found' messages appear, keyring is not configured on this system.")
    print("You might need to install a backend like 'keyrings.alt' (e.g., `pip install keyrings.alt`)")
    print("or configure one appropriate for your OS (e.g., KWallet, macOS Keychain, Windows Credential Manager).")
