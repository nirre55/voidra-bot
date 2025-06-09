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
-   Option to switch between Binance Spot (default) and Binance Futures Testnet.

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

## Usage

1.  Upon running the application, a window titled "Binance Balance Checker (PyQt)" will appear.
2.  Enter your Binance **API Key** in the "API Key:" field.
3.  Enter your Binance **Secret Key** in the "Secret Key:" field. The input will be masked.
    *   **Security Note for Live Keys:** For live Binance accounts (Spot), it is **highly recommended** to use API keys with **read-only access** enabled. This application only needs permission to fetch balances, not to trade or withdraw funds.
4.  **Select Market Type (Optional):**
    - By default, the application fetches balances from your main Binance Spot account.
    - To fetch balances from the **Binance Futures Testnet**, check the "Use Binance Futures Testnet" checkbox.
    - **Important Note for Futures Testnet:** API keys for the Binance Futures Testnet are **separate and different** from your live Binance API keys. You need to generate them specifically from the [Binance Futures Testnet website](https://testnet.binancefuture.com/) after logging in with your testnet account. Using live keys with the testnet option (or vice-versa) will result in errors.
5.  Click the "**Fetch Balance**" button.
6.  The "Balance (USDT):" field will show "Loading..." while the data is being fetched.
7.  Once fetched, your total USDT balance for the selected account type will be displayed (e.g., "123.45 USDT").
8.  If there are any errors (e.g., incorrect API keys for the selected environment, network issues, API errors from Binance), an informative error message will be displayed in the balance field. The "Fetch Balance" button will re-enable after an attempt.

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
