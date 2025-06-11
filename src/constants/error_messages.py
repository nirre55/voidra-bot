# src/constants/error_messages.py

# --- General UI Errors (from main_pyqt.py) ---
ERROR_INVALID_ENVIRONMENT_SELECTED = "Erreur: Environnement invalide sélectionné."
ERROR_API_KEYS_REQUIRED_UI = "Erreur: API Key et Secret Key sont requis."
ERROR_ALL_SIM_FIELDS_REQUIRED = "Erreur: Tous les champs de simulation doivent être remplis."
ERROR_SIM_NUMERIC_INPUT = "Erreur: Les entrées numériques pour la simulation doivent être des nombres valides (ex: 1000 ou 0.5)."
ERROR_UNEXPECTED_SIM_ISSUE = "Une erreur inattendue est survenue lors de la simulation."

# --- Order Placement UI Errors (from main_pyqt.py) ---
ERROR_ORDER_SYMBOL_REQUIRED = "Erreur: Le symbole est requis pour passer un ordre."
ERROR_ORDER_AMOUNT_POSITIVE = "Erreur: Le montant doit être un nombre positif." # Used if ValueError in main_pyqt for amount
ERROR_ORDER_PRICE_POSITIVE_LIMIT = "Erreur: Le prix doit être un nombre positif pour les ordres LIMIT." # Used if ValueError in main_pyqt for price
ERROR_ORDER_AMOUNT_INVALID_NUMBER = "Erreur: Montant invalide. Entrez un nombre." # Used for float conversion error
ERROR_ORDER_PRICE_INVALID_NUMBER = "Erreur: Prix invalide. Entrez un nombre." # Used for float conversion error


# --- Application Logic Errors (from app_logic.py custom exceptions) ---
# Messages used when raising exceptions in app_logic.py, if they are static.
# Many exceptions in app_logic construct messages dynamically with error details from ccxt.

# From app_logic.ApiKeyMissingError (message is already part of the exception)
# API_KEY_SECRET_REQUIRED = "API Key and Secret Key are required." # Defined in app_logic.py
PARAM_API_KEYS_REQUIRED = "API Key et Secret Key sont requis."

# From app_logic.InvalidOrderParamsError (some are specific in exception, these are from validation)
PARAM_SYMBOL_REQUIRED = "Le symbole est requis."
PARAM_ORDER_TYPE_INVALID = "Le type d'ordre doit être LIMIT ou MARKET."
PARAM_SIDE_INVALID = "Le côté doit être BUY ou SELL."
PARAM_AMOUNT_MUST_BE_POSITIVE = "Le montant doit être positif."
PARAM_PRICE_MUST_BE_POSITIVE_LIMIT = "Le prix doit être positif pour les ordres LIMIT."

# --- Simulation Logic Errors (from simulation_logic.py SimulationError) ---
# These are messages used when raising SimulationError in simulation_logic.py
SIM_ERROR_BALANCE_POSITIVE = "La balance doit être un nombre positif."
SIM_ERROR_PRIX_ENTREE_POSITIVE = "Le prix d'entrée doit être un nombre positif."
SIM_ERROR_PRIX_CATASTROPHIQUE_NOT_NEGATIVE = "Le prix catastrophique ne peut pas être négatif."
SIM_ERROR_PRIX_ENTREE_MUST_BE_GREATER = "Le prix d'entrée doit être supérieur au prix catastrophique."
SIM_ERROR_DROP_PERCENT_RANGE = "Le pourcentage de drop doit être entre 0 et 100 (exclusif)."
SIM_ERROR_NO_ITERATIONS_POSSIBLE = "Aucune itération possible avec les paramètres donnés (le prix d'entrée est peut-être déjà inférieur ou égal au prix catastrophique)."

# --- Generic Catch-All ---
ERROR_UNEXPECTED = "Une erreur inattendue est survenue."
