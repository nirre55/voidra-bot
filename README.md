# Binance Balance Checker (PyQt5 Version)

This Python desktop application provides a graphical user interface (GUI) built with PyQt5 to check your USDT balance on the Binance cryptocurrency exchange using your API keys.

## Features

-   User-friendly GUI built with PyQt5.
-   Securely input your Binance API Key and Secret Key.
-   Fetches and displays your total USDT balance from Binance.
-   Asynchronous API calls using QThread to prevent UI freezing.
-   Visual feedback ("Loading...") during data fetching.
-   Clear error messages for API issues, network problems, or missing keys.
-   Unit tests for the application logic.
-   Tabbed interface: "Balance", "Trade", and "Simulation" tabs for clear separation of functions.
-   Environment selectors (Spot, Futures Live, Futures Testnet) for both Balance and Trade operations.
-   Trade Tab: Place LIMIT and MARKET orders for Spot, Futures Live, and Futures Testnet environments.
-   Simulation Tab: Calculate Dollar Cost Averaging (DCA) iteration strategies based on balance, entry price, catastrophic price, and drop percentage.

## Project Structure

The project is organized into the following key files:

-   `/src`: Contains the main application source code.
    -   `main_pyqt.py`: Main application script (PyQt5).
    -   `ui_main_window.py`: Defines the UI structure (PyQt5).
    -   `app_logic.py`: Handles application logic (Binance API interaction).
-   `/tests`: Contains unit tests.
    -   `test_app_logic.py`: Unit tests for `app_logic.py`.
-   `README.md`: This file, providing information about the project.
-   `requirements.txt`: Python dependencies.
-   `.gitignore`: Specifies intentionally untracked files that Git should ignore.

## Prerequisites

-   Python 3.x (developed with 3.10 or newer recommended)
-   `pip` (Python package installer)
-   Access to a command line/terminal.

## Setup Instructions

1.  **Clone the repository (or download the files):**
    ```bash
    # If you have git installed
    git clone <repository_url>
    cd <repository_directory_name>
    ```
    Alternatively, download the necessary files (`main_pyqt.py`, `ui_main_window.py`, `app_logic.py`, `requirements.txt`) into a local directory.

2.  **Create a virtual environment (highly recommended):**
    Open your terminal or command prompt in the project directory and run:
    ```bash
    python -m venv venv
    ```
    Activate the virtual environment:
    -   On Windows:
        ```bash
        .\venv\Scripts\activate
        ```
    -   On macOS and Linux:
        ```bash
        source venv/bin/activate
        ```

3.  **Install dependencies:**
    With your virtual environment activated, install the required packages using the `requirements.txt` file:
    ```bash
    pip install -r requirements.txt
    ```
    This will install `ccxt` (for Binance API interaction) and `PyQt5` (for the GUI).

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
    -   **Do Not Share**: Never share your API keys with anyone or commit them to version control (e.g., Git). This application stores them in memory only while it's running.
-   **Test Thoroughly**:
    -   **ALWAYS use the "Futures Testnet" environment for initial testing and familiarization.** This allows you to place test orders without risking real money.
    -   Verify that orders are placed as expected and that balance updates reflect trades correctly in the testnet environment.
-   **No Warranty**: This software is provided "AS-IS" without any warranties of any kind, express or implied. This includes but is not limited to implied warranties of merchantability, fitness for a particular purpose, and non-infringement.
-   **Use At Your Own Risk**: You assume all responsibility for any and all gains and losses, financial, emotional or otherwise, experienced, suffered or incurred by you as a result of using this software. Use this software for live trading entirely at your own risk.

## Usage

The application window has two main tabs: "Balance" and "Trade". API Keys entered on the "Balance" tab are used for operations on both tabs.

### Balance Tab

1.  **Enter API Credentials**:
    -   Input your Binance **API Key** in the "API Key:" field.
    -   Input your Binance **Secret Key** in the "Secret Key:" field (input will be masked).
2.  **Select Environment**:
    -   Choose the desired market environment from the "Environment" dropdown:
        -   **Spot**: Your main Binance spot account (live trading).
        -   **Futures Live**: Your Binance Futures live trading account.
        -   **Futures Testnet**: The Binance Futures test trading environment (uses separate testnet API keys and funds).
    -   **API Key Note**: Remember that **Futures Testnet API keys are different** from your live Spot/Futures API keys. Get them from the [Binance Futures Testnet website](https://testnet.binancefuture.com/).
3.  **Fetch Balance**:
    -   Click the "**Fetch Balance**" button.
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
    -   Click the "**Place Order**" button.
5.  **Check Status**:
    -   The "Status:" label at the bottom of the Trade tab will update to show "Submitting order...", then the success response (including Order ID) or an error message from the exchange or application.

### Simulation Tab

The "Simulation" tab allows you to calculate and visualize a Dollar Cost Averaging (DCA) strategy based on a set of input parameters. This helps in understanding how many DCA levels can be achieved and the investment at each price point down to a catastrophic price.

1.  **Enter Simulation Parameters**:
    -   **Balance Total à Investir**: The total amount of capital you want to allocate for this DCA simulation.
    -   **Prix d'entrée initial**: The price at which your first investment level is considered.
    -   **Prix catastrophique (seuil d'arrêt)**: The price threshold. The simulation calculates DCA levels down to this price. If the price drops to or below this level, no further DCA steps are considered beyond the one that hits/crosses this threshold.
    -   **Pourcentage de drop par niveau (%)**: The percentage the price must drop from the previous level for a new DCA investment to occur (e.g., 50 for a 50% drop).
2.  **Calculate Simulation**:
    -   Click the "**Calculer la Simulation**" button.
3.  **View Results**:
    -   The results will be displayed in the text area below the button.
    -   This includes:
        -   A summary of your input parameters.
        -   The total number of DCA levels possible.
        -   The amount of capital to be invested at each level.
        -   A detailed breakdown for each DCA level, showing the entry price and the quantity of the asset that can be bought with the allocated amount for that level.
    -   If there are errors in your input (e.g., non-numeric values, invalid percentages), an error message will be shown in the results area.

## Running Unit Tests

To ensure the application logic for interacting with the Binance API is working correctly, you can run the provided unit tests:

1.  **Ensure your virtual environment is activated** and dependencies are installed.
2.  **Navigate to the project's root directory** in your terminal.
3.  **Run the tests:**
    ```bash
    python -m unittest test_app_logic.py
    ```
    Or, for more verbose output:
    ```bash
    python -m unittest discover -v tests
    ```
    The tests will mock the actual network calls to Binance, so you don't need live API keys to run them.

## Disclaimer

-   Use this application at your own risk.
-   Always ensure your API keys are kept secure and have the minimum necessary permissions (read-only for this application).
-   The developers of this application are not responsible for any loss of funds, security breaches, or issues arising from its use.
-   This tool is for informational purposes only and is not financial advice.
```
