# Binance Balance Checker

This Python desktop application allows you to check your USDT balance on Binance using your API keys. It provides a simple graphical user interface built with Tkinter.

## Features

- Securely input your Binance API Key and Secret Key.
- Fetch and display your total USDT balance.
- User-friendly interface.

## Prerequisites

- Python 3.x
- `pip` (Python package installer)

## Setup Instructions

1.  **Clone the repository (or download the files):**
    ```bash
    # If you have git installed
    git clone <repository_url>
    cd <repository_directory>
    ```
    Alternatively, download `main_app.py` and `requirements.txt` into a local directory.

2.  **Create a virtual environment (recommended):**
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
    This will install `ccxt` (for Binance API interaction) and ensure `tkinter` (for the GUI) is available (usually included with Python, but `python3-tk` might be needed on some Linux systems if not installed via `apt-get` previously).

## Running the Application

1.  **Ensure your virtual environment is activated** (if you created one).
2.  **Navigate to the directory** where `main_app.py` is located.
3.  **Run the application:**
    ```bash
    python main_app.py
    ```

## Usage

1.  Upon running the application, a window titled "Binance Balance Checker" will appear.
2.  Enter your Binance **API Key** in the "API Key:" field.
3.  Enter your Binance **Secret Key** in the "Secret Key:" field.
    *   **Important Security Note:** It is highly recommended to use API keys with **read-only access** enabled. This application only needs permission to fetch balances, not to trade or withdraw.
4.  Click the "**Fetch Balance**" button.
5.  The application will connect to Binance and display your total USDT balance in the "Balance (USDT):" field.
6.  If there are any errors (e.g., incorrect API keys, network issues), an error message will be displayed in the balance field.

## Disclaimer

- Use this application at your own risk.
- Always ensure your API keys are kept secure and have restricted permissions.
- The developers are not responsible for any loss of funds or security breaches.

This will replace the current content of `README.md`.
