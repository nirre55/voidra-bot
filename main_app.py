import tkinter as tk
from tkinter import ttk
import ccxt

class BinanceApp:
    def __init__(self, master):
        self.master = master
        master.title("Binance Balance Checker")

        # API Key
        self.api_key_label = ttk.Label(master, text="API Key:")
        self.api_key_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.api_key_entry = ttk.Entry(master, width=50)
        self.api_key_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Secret Key
        self.secret_key_label = ttk.Label(master, text="Secret Key:")
        self.secret_key_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.secret_key_entry = ttk.Entry(master, width=50, show="*")
        self.secret_key_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        # Balance Display
        self.balance_label = ttk.Label(master, text="Balance (USDT):")
        self.balance_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.balance_display_var = tk.StringVar(master, value="N/A")
        self.balance_display = ttk.Label(master, textvariable=self.balance_display_var, anchor="e")
        self.balance_display.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        # Fetch Balance Button
        self.fetch_button = ttk.Button(master, text="Fetch Balance", command=self.fetch_balance)
        self.fetch_button.grid(row=3, column=0, columnspan=2, pady=10)

        master.columnconfigure(1, weight=1) # Make the entry and display widgets expand

    def fetch_balance(self):
        # Placeholder for fetching balance logic
        # This will be implemented in a later step.
        self.fetch_button.config(state=tk.DISABLED)
        self.balance_display_var.set("Loading...")

        api_key = self.api_key_entry.get()
        secret_key = self.secret_key_entry.get()

        if not api_key or not secret_key:
            self.balance_display_var.set("API Key and Secret Key are required.")
            self.fetch_button.config(state=tk.NORMAL)
            return

        # print(f"API Key: {api_key}") # Optional: for debugging, but remove for production
        # print(f"Secret Key: {secret_key}") # Optional: for debugging, but remove for production

        try:
            exchange = ccxt.binance({
                'apiKey': api_key,
                'secret': secret_key,
                # 'enableRateLimit': True, # Optional: to avoid hitting API rate limits
            })
            balance_data = exchange.fetch_balance()
            usdt_balance = balance_data['total'].get('USDT', 0.0)
            self.balance_display_var.set(f"{usdt_balance:.2f} USDT")
        except ccxt.NetworkError as e:
            self.balance_display_var.set(f"Network Error: {e}")
        except ccxt.ExchangeError as e:
            self.balance_display_var.set(f"Exchange Error: {e}")
        except Exception as e:
            self.balance_display_var.set(f"An error occurred: {e}")
        finally:
            self.fetch_button.config(state=tk.NORMAL)


if __name__ == '__main__':
    root = tk.Tk()
    app = BinanceApp(root)
    root.mainloop()
