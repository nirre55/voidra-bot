import math

class SimulationError(ValueError):
    """Custom exception for simulation errors."""
    pass

def calculer_iterations(balance: float, prix_entree: float, prix_catastrophique: float, drop_percent: float) -> dict:
    """
    Calcule le nombre d'itérations possibles avec un drop de prix.

    Args:
        balance: Le montant total disponible
        prix_entree: Le prix de départ
        prix_catastrophique: Le prix limite (seuil d'arrêt)
        drop_percent: Le pourcentage de drop à chaque itération (e.g., 50 for 50%)

    Returns:
        A dictionary containing the simulation results or raises SimulationError.
    """
    if balance <= 0:
        raise SimulationError("La balance doit être un nombre positif.")
    if prix_entree <= 0:
        raise SimulationError("Le prix d'entrée doit être un nombre positif.")
    if prix_catastrophique < 0: # Can be 0 if we want to allow going to zero
        raise SimulationError("Le prix catastrophique ne peut pas être négatif.")
    if prix_entree <= prix_catastrophique:
        raise SimulationError("Le prix d'entrée doit être supérieur au prix catastrophique.")
    if not (0 < drop_percent < 100):
        raise SimulationError("Le pourcentage de drop doit être entre 0 et 100 (exclusif).")

    prix_actuel = prix_entree
    # iteration_count = 0 # Correctly count iterations passed
    # prix_iterations = []
    # details_text_list = []

    # Calculer toutes les itérations
    # Loop while current price is strictly greater than catastrophic price
    # and also check against a max number of iterations to prevent infinite loops with tiny drops
    max_iterations_cap = 1000 # Safety cap

    # Re-thinking the loop based on the provided script's print statements:
    # The script prints "Xème itération - Prix d'entrée: P_current", then calculates P_next.
    # The loop condition is `while P_current > P_catastrophic`.
    # If P_current makes the loop run, P_current is added. Then P_next is calculated.
    # If P_next <= P_catastrophic, the original script adds *another* iteration with P_next.

    # Let's simplify: the list of prices will be the entry prices for each DCA level.
    # The number of DCA levels is the number of iterations.

    # Resetting for clearer logic based on user's script's output behavior:
    prix_actuel = prix_entree
    prix_iterations_for_dca = [] # Prices at which we would DCA

    iteration_num = 1
    while True:
        if iteration_num > max_iterations_cap: # Safety break
            # Consider raising an error or warning if max_iterations_cap is hit
            # For now, just break, results will be based on iterations up to this point
            break

        # This price is a potential DCA level
        prix_iterations_for_dca.append(prix_actuel)
        # details_text_list.append(f"Niveau {iteration_num} - Entrée à: {prix_actuel:.8f}")


        if prix_actuel <= prix_catastrophique: # If current price is already at or below catastrophic, this is the last possible DCA
            break

        prix_prochain = prix_actuel * (1 - drop_percent / 100)

        # If the *next* price would be below catastrophic (but current is not),
        # we should still consider the current price as a DCA level.
        # And if that next price IS the catastrophic price or just passed it, it's also a level.
        if prix_prochain <= prix_catastrophique and prix_actuel > prix_catastrophique:
            # Current prix_actuel is the last one *above* catastrophic.
            # The next one (prix_prochain) will be at or below.
            # The user script includes this prix_prochain as a level.
            prix_iterations_for_dca.append(prix_prochain)
            # details_text_list.append(f"Niveau {iteration_num+1} - Entrée à: {prix_prochain:.8f} (niveau catastrophique atteint)")
            break # Stop after adding the catastrophic level

        prix_actuel = prix_prochain
        iteration_num += 1
        if prix_actuel < 0.00000001 and prix_actuel > 0: # Avoid extremely small prices leading to too many iterations
            if drop_percent > 0: # Only if drop_percent is causing this, not if price_catastrophic is just very low
                 break # Safety for extreme drops close to zero


    nombre_total_iterations = len(prix_iterations_for_dca)

    if nombre_total_iterations == 0:
        # This case should be caught by "prix_entree <= prix_catastrophique" earlier,
        # but as a safeguard:
        raise SimulationError("Aucune itération possible avec les paramètres donnés (le prix d'entrée est peut-être déjà inférieur ou égal au prix catastrophique).")

    montant_par_iteration = balance / nombre_total_iterations
    quantites_par_iteration = []

    # Final details text generation
    details_text_list_final = []
    details_text_list_final.append(f"Balance: {balance:.2f}")
    details_text_list_final.append(f"Prix d'entrée initial: {prix_entree:.8f}")
    details_text_list_final.append(f"Prix catastrophique: {prix_catastrophique:.8f}")
    details_text_list_final.append(f"Drop par niveau: {drop_percent}%")
    details_text_list_final.append("-" * 50)
    details_text_list_final.append(f"Nombre total de niveaux de DCA: {nombre_total_iterations}")
    details_text_list_final.append(f"Montant par niveau de DCA: {balance:.2f} / {nombre_total_iterations} = {montant_par_iteration:.2f}")
    details_text_list_final.append("-" * 50)
    details_text_list_final.append("Répartition par niveau de DCA:")

    for i, prix in enumerate(prix_iterations_for_dca, 1):
        if prix <= 0:
            # This should ideally not be reached if prix_catastrophique is > 0 and validation is correct.
            # If prix_catastrophique can be 0, then quantite would be infinite.
            quantite = float('inf') if montant_par_iteration > 0 else 0
            details_text_list_final.append(f"Niveau {i}: Prix de {prix:.8f} est invalide pour calculer la quantité.")
        else:
            quantite = montant_par_iteration / prix
            details_text_list_final.append(f"Niveau {i}: {montant_par_iteration:.2f} / {prix:.8f} = {quantite:.8f} (quantité)")
        quantites_par_iteration.append(quantite)


    return {
        "inputs": {
            "balance": balance,
            "prix_entree": prix_entree,
            "prix_catastrophique": prix_catastrophique,
            "drop_percent": drop_percent,
        },
        "prix_iterations": prix_iterations_for_dca,
        "nombre_total_iterations": nombre_total_iterations,
        "montant_par_iteration": montant_par_iteration,
        "quantites_par_iteration": quantites_par_iteration,
        "details_text": details_text_list_final,
    }

if __name__ == '__main__':
    print("=== EXEMPLE SCRIPT LOGIC ===")
    try:
        # Test case from user
        results = calculer_iterations(1000, 40, 4, 50)
        for line in results['details_text']:
            print(line)

        print("\n=== CUSTOM TEST ===")
        # results_custom = calculer_iterations(100, 10, 1, 10) # price_catastrophic reached
        # results_custom = calculer_iterations(100, 10, 0.5, 10) # price_catastrophic reached
        results_custom = calculer_iterations(234, 0.00000650, 0.00000010, 10)
        for line in results_custom['details_text']:
            print(line)

        print("\n=== EDGE CASE: Entry <= Catastrophic ===")
        try:
            results_edge = calculer_iterations(1000, 4, 40, 10) # Should raise error
            for line in results_edge['details_text']:
                print(line)
        except SimulationError as e_edge:
            print(f"Caught expected simulation error for edge case: {e_edge}")


        print("\n=== EDGE CASE: Price becomes zero ===")
        try:
            # This should hit the catastrophic price if it's > 0, or finish if catastrophic is 0
            results_zero = calculer_iterations(100, 10, 0, 99.99999999)
            for line in results_zero['details_text']:
                print(line)
            # Test with catastrophic price being zero
            results_cat_zero = calculer_iterations(100, 10, 0, 50)
            print("\nResults for catastrophic price zero:")
            for line in results_cat_zero['details_text']:
                print(line)


        except SimulationError as e_zero:
            print(f"Caught simulation error for zero price case: {e_zero}")


    except SimulationError as e:
        print(f"Erreur de simulation: {e}")
    except Exception as e:
        print(f"Autre Erreur: {type(e).__name__} {e}")
```
