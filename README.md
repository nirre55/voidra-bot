# Binance MultiApp (PyQt5 Version)

This Python desktop application provides a graphical user interface (GUI) built with PyQt5 to check your Binance account balance, place trades, and simulate Dollar Cost Averaging (DCA) strategies.

## Features

-   User-friendly GUI built with PyQt5 featuring a tabbed interface ("Balance", "Trade", "Simulation").
-   **Secure API Key Storage**: Optionally save and load API keys securely using the system's native keyring/keychain service.
-   **Balance Tab**:
    -   Securely input your Binance API Key and Secret Key.
    -   Select market environment (Spot, Futures Live, Futures Testnet).
    -   Fetch and display your total USDT balance.
-   **Trade Tab**:
    -   Place LIMIT and MARKET orders.
    -   Select market environment (Spot, Futures Live, Futures Testnet).
    -   Input for symbol, order type, side, amount, and price.
    -   Real-time status updates for order placement.
-   **Simulation Tab**:
    -   Calculate Dollar Cost Averaging (DCA) iteration strategies based on balance, entry price, catastrophic price, and drop percentage.
    -   Optionally select symbol and environment for context (currently not used in calculation but planned for future enhancements like pre-filling entry price).
    -   Place multiple DCA LIMIT BUY orders directly based on simulation results for a chosen symbol and environment.
-   Asynchronous API calls using QThread to prevent UI freezing.
-   Visual feedback ("Loading...", "Submitting order...") during operations.
-   Clear error messages for API issues, network problems, or invalid inputs.
-   Unit tests for application logic and simulation logic.

## Project Structure

The project is organized into the following key files:

-   `/src`: Contains the main application source code.
    -   `__init__.py`: Makes `src` a Python package.
    -   `main_pyqt.py`: Main application script (PyQt5), handles UI logic and event handling.
    -   `ui_main_window.py`: Defines the UI structure (PyQt5).
    -   `app_logic.py`: Handles core application logic, including Binance API interaction via `ccxt` (balance fetching, order placement).
    -   `simulation_logic.py`: Contains logic for the DCA simulation calculations.
    -   `keyring_utils.py`: Manages secure storage and retrieval of API keys using the system keyring.
    -   `constants/`: Stores application-wide constants.
        -   `__init__.py`: Makes `constants` a Python package.
        -   `ui_strings.py`: Constants for UI text elements (labels, buttons, etc.).
        -   `error_messages.py`: Constants for user-facing error messages.
-   `/tests`: Contains unit tests.
    -   `test_app_logic.py`: Unit tests for `app_logic.py`.
    -   `test_simulation_logic.py`: Unit tests for `simulation_logic.py`.
-   `README.md`: This file.
-   `requirements.txt`: Python dependencies.
-   `.gitignore`: Specifies intentionally untracked files that Git should ignore.

## Prerequisites

-   Python 3.x (developed with 3.10 or newer recommended)
-   `pip` (Python package installer)
-   Access to a command line/terminal.
-   A compatible keyring backend (see "Secure API Key Storage" section below).

## Setup Instructions

1.  **Clone the repository (or download the files):**
    ```bash
    git clone <repository_url> # Replace <repository_url> with the actual URL
    cd <repository_directory_name>
    ```
    Alternatively, download the necessary files into a local directory.

2.  **Create a virtual environment (highly recommended):**
    Open your terminal or command prompt in the project directory and run:
    ```bash
    python -m venv venv
    ```
    Activate the virtual environment:
    -   On Windows: `.\venv\Scripts\activate`
    -   On macOS and Linux: `source venv/bin/activate`

3.  **Install dependencies:**
    With your virtual environment activated, install the required packages:
    ```bash
    pip install -r requirements.txt
    ```
    This will install `ccxt`, `PyQt5`, and `keyring` among other necessary packages. For `keyring` to function, you might need to install a backend if one is not already present on your system (e.g., `sudo apt-get install python3-dbus dbus -y; pip install keyrings.alt` on some Linux systems, or ensure GNOME Keyring / KWallet is set up. Windows and macOS usually have backends by default).

## Running the Application

1.  **Ensure your virtual environment is activated** (if you created one).
2.  **Navigate to the project's root directory.** Ensure you are in the project's root directory (the one containing the `src` folder and `requirements.txt`) when running this command.
3.  **Run the application:**
    ```bash
    python -m src.main_pyqt
    ```

## ⚠️ Important Warnings and Risks ⚠️

> **This application can place REAL orders on LIVE markets if configured for "Spot" or "Futures Live" environments. Trading cryptocurrencies involves a significant risk of substantial financial loss. Understand the risks before proceeding.**

-   **Financial Risk**: Be aware that using this tool for live trading can result in the loss of your invested capital. Market conditions can be volatile, and software may have bugs.
-   **API Key Security**:
    -   Your API keys grant access to your Binance account. Treat them like passwords.
    -   **Permissions**: For live trading, API keys MUST have trading permissions enabled. For balance checking only, read-only keys are sufficient and much safer.
    -   **Create Specific Keys**: It is strongly recommended to create new API keys specifically for this application rather than using keys shared with other services.
    -   **IP Restrictions**: If possible, enable IP restrictions for your API keys in your Binance account settings, whitelisting only your own IP address.
    -   **Do Not Share**: Never share your API keys with anyone or commit them to version control (e.g., Git). This application uses the system keyring for storage if enabled, which is generally safer than plain text files.
-   **Test Thoroughly**:
    -   **ALWAYS use the "Futures Testnet" environment for initial testing and familiarization.** This allows you to place test orders without risking real money.
    -   Verify that orders are placed as expected and that balance updates reflect trades correctly in the testnet environment.
-   **No Warranty**: This software is provided "AS-IS" without any warranties of any kind, express or implied. This includes but is not limited to implied warranties of merchantability, fitness for a particular purpose, and non-infringement.
-   **Use At Your Own Risk**: You assume all responsibility for any and all gains and losses, financial, emotional or otherwise, experienced, suffered or incurred by you as a result of using this software. Use this software for live trading entirely at your own risk.

## Usage

The application window has three main tabs: "Balance", "Trade", and "Simulation". API Keys entered on the "Balance" tab are used for operations on the "Balance" and "Trade" tabs, and also for placing DCA orders from the "Simulation" tab.

### Secure API Key Storage (Keyring)

-   The application can securely store and retrieve your API keys for different environments (Spot, Futures Live, Futures Testnet) using your system's native keyring or keychain service (e.g., Windows Credential Manager, macOS Keychain, Linux Secret Service/KWallet).
-   This means you don't have to re-enter them every time you start the application for environments where you've chosen to save them.
-   **How it works**:
    -   On the "Balance" tab, you'll find a checkbox: "**Mémoriser les clés API pour cet environnement**".
    -   If you check this box, enter your API key and Secret Key, select an environment, and click "**Récupérer la Balance**" (Fetch Balance), the keys will be saved to your system's keyring, associated with the chosen environment.
    -   Subsequently, when you select that environment in the "Environnement" dropdown on the "Balance" tab, the application will attempt to automatically load the saved keys into the input fields. If keys are loaded, the "Mémoriser..." checkbox will also be checked.
    -   If you uncheck the box and click "Récupérer la Balance", any stored keys for that specific environment will be deleted from your keyring.
-   **Keyring Backend Requirement**:
    -   The `keyring` library requires a compatible backend service on your operating system. Most modern desktop environments (Windows, macOS, GNOME, KDE) provide one.
    -   If no backend is found, the "Mémoriser..." checkbox will be disabled, and a message indicating this may appear in the status bar or console.
    -   On some Linux systems, you might need to install a backend like `gnome-keyring` or `kwallet` and the necessary Python bindings (e.g., `python3-dbus`, `keyrings.alt`). Refer to the [Python Keyring library documentation](https://pypi.org/project/keyring/) for more details on backend setup.

### Balance Tab

1.  **Enter API Credentials**:
    -   Input your Binance **API Key** in the "API Key:" field.
    -   Input your Binance **Secret Key** in the "Secret Key:" field (input will be masked).
2.  **Save API Keys (Optional)**:
    -   Check the "**Mémoriser les clés API pour cet environnement**" box if you want the application to save these keys securely for the environment selected below. Uncheck it to remove previously saved keys for the selected environment upon the next "Fetch Balance" action.
3.  **Select Environment**:
    -   Choose the desired market environment from the "Environment" dropdown:
        -   **Spot**: Your main Binance spot account (live trading).
        -   **Futures Live**: Your Binance Futures live trading account.
        -   **Futures Testnet**: The Binance Futures test trading environment (uses separate testnet API keys and funds).
    -   **API Key Note**: Remember that **Futures Testnet API keys are different** from your live Spot/Futures API keys. Get them from the [Binance Futures Testnet website](https://testnet.binancefuture.com/).
4.  **Fetch Balance**:
    -   Click the "**Récupérer la Balance**" button.
    -   The "Balance (USDT):" field will show "Loading..." and then display your total USDT balance for the selected environment, or an error message.

### Trade Tab

1.  **API Keys**: Ensure your API keys are entered on the "Balance" tab. These keys will be used for placing orders. **They must have trading permissions enabled for the selected live environment.**
2.  **Select Trading Environment**:
    -   Choose the environment ("Spot", "Futures Live", "Futures Testnet") from the "Environment" dropdown. This determines where your order will be placed.
3.  **Enter Order Details**:
    -   **Symbol**: Enter the trading symbol (e.g., `BTC/USDT` for spot, `BTCUSDT` for futures often – check CCXT/Binance conventions).
    -   **Order Type**: Select "LIMIT" or "MARKET" from the dropdown.
        -   If "LIMIT" is selected, the "Price" field will be enabled.
        -   If "MARKET" is selected, the "Price" field will be disabled and its content cleared.
    -   **Side**: Select "BUY" or "SELL".
    -   **Amount**: Enter the quantity of the base asset to trade (e.g., amount of BTC in BTC/USDT).
    -   **Price (for LIMIT orders)**: If you selected "LIMIT" order type, enter your desired price.
4.  **Place Order**:
    -   Click the "**Placer l'Ordre**" button.
5.  **Check Status**:
    -   The "Status:" label at the bottom of the Trade tab will update to show "Submitting order...", then the success response (including Order ID) or an error message from the exchange or application.

### Simulation Tab

The "Simulation" tab allows you to calculate and visualize a Dollar Cost Averaging (DCA) strategy. This feature helps in understanding how many DCA levels can be achieved and the investment at each price point down to a specified catastrophic price. After calculating a simulation, you can choose to place the generated DCA orders.

1.  **Enter Simulation Parameters**:
    -   **Symbole**: Select or enter a trading symbol (e.g., BTC/USDT). This symbol will be used if you decide to place DCA orders.
    -   **Environnement**: Select the market environment (Spot, Futures Live, Futures Testnet) where DCA orders would be placed. *API keys from the "Balance" tab will be used.*
        -   **Important**: Ensure the API keys have trading permissions for the selected live environment if you intend to place orders. For "Futures Testnet", ensure you are using specific Futures Testnet API keys.
    -   **Balance Total à Investir**: The total amount of capital you want to allocate for this DCA simulation (e.g., 1000 USDT).
    -   **Prix d'entrée initial**: The price at which your first investment level is considered (e.g., 40000 for BTC).
    -   **Prix catastrophique (seuil d'arrêt)**: The price threshold. The simulation calculates DCA levels down to this price.
    -   **Pourcentage de drop par niveau (%)**: The percentage the price must drop from the *previous level's entry price* for a new DCA investment to occur (e.g., 10 for a 10% drop).
2.  **Calculate Simulation**:
    -   Click the "**Calculer la Simulation**" button.
    -   The results, including the number of DCA levels, price per level, and amount/quantity per level, will be displayed in the text area.
    -   If the calculation is successful, the "**Placer Ordres DCA (LIMIT BUY)**" button will become enabled.
3.  **Placing Orders Based on Simulation (Optional)**:
    -   **Verify all inputs** (Symbol, Environment on this tab, and API Keys on the Balance tab).
    -   Click the "**Placer Ordres DCA (LIMIT BUY)**" button.
    -   The application will attempt to place a series of LIMIT BUY orders based on the calculated simulation levels.
    -   The results area will show the status of each order placement attempt.
    -   **CAUTION**: This will place REAL orders if "Spot" or "Futures Live" is selected. Test with "Futures Testnet" first. See the "⚠️ Important Warnings and Risks ⚠️" section.
4.  **View Results**:
    -   The results of the calculation or order placement will be displayed in the text area below the buttons.
    -   This includes:
        -   A summary of your input parameters for calculation.
        -   The total number of DCA levels possible.
        -   The amount of capital to be invested at each level.
        -   A detailed breakdown for each DCA level: entry price and quantity.
        -   Status of each order placed if the "Placer Ordres DCA" button was used.
    -   If there are errors in your input or during API interaction, an error message will be shown.

## Running Unit Tests

To ensure the application logic for interacting with the Binance API is working correctly, you can run the provided unit tests:

1.  **Ensure your virtual environment is activated** and dependencies are installed.
2.  **Navigate to the project's root directory** in your terminal.
3.  **Run the tests:**
    ```bash
    python -m unittest tests/test_app_logic.py tests/test_simulation_logic.py
    ```
    Or, for more verbose output and discovery (recommended):
    ```bash
    python -m unittest discover -s tests -v
    ```
    The tests will mock the actual network calls to Binance, so you don't need live API keys to run them.

## Disclaimer

-   Use this application at your own risk.
-   Always ensure your API keys are kept secure and have the minimum necessary permissions (read-only for this application, trading permissions if using the trade tab).
-   The developers of this application are not responsible for any loss of funds, security breaches, or issues arising from its use.
-   This tool is for informational purposes only and is not financial advice.
```
