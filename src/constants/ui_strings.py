# src/constants/ui_strings.py

# --- General ---
WINDOW_TITLE = "Binance MultiApp"
APP_NAME = "Binance MultiApp"
APP_NAME_KEYRING = "BinanceMultiApp" # For Keyring Service Name

# --- Tab Names ---
TAB_CONFIG = "Config" # Renamed from TAB_BALANCE
TAB_TRADE = "Trade"
TAB_SIMULATION_DCA = "Simulation DCA"
TAB_DCA_ORDERS = "Ordres DCA"

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
CHECKBOX_SAVE_API_KEYS = "Mémoriser les clés API pour cet environnement"
LABEL_KEYRING_UNAVAILABLE = "Keyring non disponible. Les clés ne peuvent pas être sauvegardées/chargées."


# --- Trade Tab ---
BUTTON_PLACE_ORDER = "Placer l'Ordre"

# --- Simulation Tab ---
LABEL_SIM_BALANCE = "Balance Total à Investir:"
LABEL_SIM_PRIX_ENTREE = "Prix d'entrée initial:"
LABEL_SIM_PRIX_CATASTROPHIQUE = "Prix catastrophique (seuil d'arrêt):"
LABEL_SIM_DROP_PERCENT = "Pourcentage de drop par niveau (%):"
BUTTON_CALCULATE_SIMULATION = "Calculer la Simulation"
BUTTON_PLACE_DCA_ORDERS = "Placer Ordres DCA (LIMIT BUY)" # Text for the original button, might be removed or repurposed


# --- DCA Orders Tab ---
LABEL_DCA_SYMBOL = "Symbole:"
LABEL_DCA_SYMBOL_DEFAULT = "N/A"
BUTTON_PLACE_DCA_ORDERS_NEW_TAB = "Placer les Ordres DCA"
BUTTON_LOAD_DCA_DATA = "Charger les Données de Simulation"
LABEL_DCA_STATUS_READY = "Prêt. Chargez les données de simulation."
LABEL_DCA_NO_SIMULATION_DATA_LOADED = "Aucune donnée de simulation n'est chargée. Veuillez exécuter une simulation et la charger ici."
DCA_TAB_SIMULATION_DATA_HEADER = "Données de Simulation Chargées:"
DCA_TAB_ORDERS_SUBMITTING = "Soumission des ordres DCA en cours..."
DCA_TAB_ORDER_LEVEL_SUCCESS = "Niveau {level} ({symbol}): Ordre {order_id} placé avec succès. Statut: {status}"
DCA_TAB_ORDER_LEVEL_ERROR = "Niveau {level} ({symbol}): Erreur lors du placement de l'ordre. Détail: {error}"
DCA_TAB_BATCH_COMPLETE = "Traitement par lots des ordres DCA terminé."
DCA_TAB_DATA_CLEARED = "Données de simulation effacées ou modifiées. Veuillez recharger."
LABEL_MERGE_MODE = "Mode de Marge:"
MERGE_MODE_ISOLATED = "Isolé"
MERGE_MODE_CROSS = "Croisé"
LABEL_LEVERAGE = "Effet de Levier:"
ERROR_LEVERAGE_INVALID_NUMBER = "L'effet de levier doit être un nombre."
ERROR_LEVERAGE_OUT_OF_RANGE = "L'effet de levier doit être compris entre 1 et 100 (inclus)."


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

# --- Simulation Tab - DCA Order Placement Status Messages ---
# These might be reused or moved to a more general DCA section if applicable
DCA_ORDER_SUBMITTING = "Soumission des ordres DCA en cours..." # Already exists, could be reused
DCA_ORDER_LEVEL_SUCCESS = "Ordre DCA Niveau {level} ({symbol}): Succès - ID {order_id}, Statut: {status}" # Already exists
DCA_ORDER_LEVEL_ERROR = "Ordre DCA Niveau {level} ({symbol}): Erreur - {error}" # Already exists
DCA_BATCH_COMPLETE = "Traitement du lot d'ordres DCA terminé." # Already exists
DCA_NO_SIMULATION_RESULTS = "Erreur: Aucune donnée de simulation valide à utiliser. Veuillez d'abord calculer une simulation."
DCA_API_KEYS_MISSING = "Erreur: Clés API non fournies dans l'onglet Balance." # Or use existing general API key error
DCA_SYMBOL_MISSING = "Erreur: Symbole non sélectionné dans l'onglet Simulation pour le placement d'ordres DCA."
DCA_ENVIRONMENT_MISSING = "Erreur: Environnement non sélectionné dans l'onglet Simulation pour le placement d'ordres DCA."
