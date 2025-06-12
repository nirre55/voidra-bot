from src.keyring_utils import save_creds, load_creds, delete_creds, SERVICE_NAME

if __name__ == "__main__":
    TEST_SERVICE_NAME = "BinanceMultiApp_KeyringUtils_DirectTest"
    _original_service = SERVICE_NAME
    try:
        SERVICE_NAME = TEST_SERVICE_NAME
    except Exception:
        pass

    print(f"Using service name for testing: {SERVICE_NAME}")

    env_spot_test = "SPOT_KEYRING_TEST"
    print(f"\n--- Testing {env_spot_test} ---")
    if save_creds(env_spot_test, "spot_api_key_123_test", "spot_secret_key_789_test"):
        print(f"Saved creds for {env_spot_test}")
        loaded_api, loaded_secret = load_creds(env_spot_test)
        if loaded_api and loaded_secret:
            print(f"Loaded for {env_spot_test}: API={loaded_api}, Secret={loaded_secret}")
        else:
            print(f"Failed to load credentials for {env_spot_test} after saving.")

        if delete_creds(env_spot_test):
            print(f"Attempted to delete credentials for {env_spot_test}.")
            loaded_api_after_delete, loaded_secret_after_delete = load_creds(env_spot_test)
            if loaded_api_after_delete is None and loaded_secret_after_delete is None:
                print(f"Credentials successfully verified as deleted for {env_spot_test}.")
            else:
                print(
                    f"Credentials still found for {env_spot_test} after attempting delete: API={loaded_api_after_delete}, Secret={loaded_secret_after_delete}"
                )
        else:
            print(f"Failed to delete credentials for {env_spot_test}.")
    else:
        print(
            f"Failed to save credentials for {env_spot_test}. Keyring backend might be missing or not configured."
        )

    SERVICE_NAME = _original_service
    print(f"\nRestored service name to: {SERVICE_NAME if SERVICE_NAME else 'ui_strings.APP_NAME (pending definition)'}")
