# src/constants/ui_strings.py

# --- General ---
WINDOW_TITLE = "Binance MultiApp"
APP_NAME = "Binance MultiApp"

# --- Tab Names ---
TAB_BALANCE = "Balance"
TAB_TRADE = "Trade"
TAB_SIMULATION_DCA = "Simulation DCA"

# --- Common Labels & Texts ---
LABEL_ENVIRONMENT = "Environnement:"
LABEL_SYMBOL = "Symbole:"
LABEL_API_KEY = "API Key:"
LABEL_SECRET_KEY = "Secret Key:"
LABEL_STATUS_READY = "Status: Prêt"
LABEL_LOADING = "Chargement..."
LABEL_SUBMITTING_ORDER = "Soumission de l'ordre..."
LABEL_ORDER_TYPE = "Type d'ordre:"
LABEL_SIDE = "Côté:"
LABEL_AMOUNT = "Montant:"
LABEL_PRICE_LIMIT_ORDER = "Prix (pour ordre LIMIT):"

# --- Balance Tab ---
LABEL_BALANCE_USDT = "Balance (USDT):"
LABEL_BALANCE_DISPLAY_DEFAULT = "N/A"
BUTTON_FETCH_BALANCE = "Récupérer la Balance"

# --- Trade Tab ---
BUTTON_PLACE_ORDER = "Placer l'Ordre"

# --- Simulation Tab ---
LABEL_SIM_BALANCE = "Balance Total à Investir:"
LABEL_SIM_PRIX_ENTREE = "Prix d'entrée initial:"
LABEL_SIM_PRIX_CATASTROPHIQUE = "Prix catastrophique (seuil d'arrêt):"
LABEL_SIM_DROP_PERCENT = "Pourcentage de drop par niveau (%):"
BUTTON_CALCULATE_SIMULATION = "Calculer la Simulation"

# --- ComboBox Choices ---
# Environment selections (ensure keys here can map to MarketEnvironment enum or logic)
ENV_SPOT = "Spot"
ENV_FUTURES_LIVE = "Futures Live"
ENV_FUTURES_TESTNET = "Futures Testnet"
ENVIRONMENT_CHOICES = [ENV_SPOT, ENV_FUTURES_LIVE, ENV_FUTURES_TESTNET]

# Symbol selections
SYMBOL_BTC_USDT = "BTC/USDT"
SYMBOL_ETH_USDT = "ETH/USDT"
SYMBOL_ADA_USDT = "ADA/USDT"
SYMBOL_SOL_USDT = "SOL/USDT"
DEFAULT_SYMBOLS = [SYMBOL_BTC_USDT, SYMBOL_ETH_USDT, SYMBOL_ADA_USDT, SYMBOL_SOL_USDT]

# Order Type selections
ORDER_TYPE_LIMIT = "LIMIT"
ORDER_TYPE_MARKET = "MARKET"
ORDER_TYPE_CHOICES = [ORDER_TYPE_LIMIT, ORDER_TYPE_MARKET]

# Side selections
SIDE_BUY = "BUY"
SIDE_SELL = "SELL"
SIDE_CHOICES = [SIDE_BUY, SIDE_SELL]

# --- Status Messages (beyond simple "Loading") ---
STATUS_ORDER_SUCCESS_PREFIX = "Ordre placé avec succès! ID: "
STATUS_ORDER_PARTIAL_INFO_SUFFIX = ", Statut: "
