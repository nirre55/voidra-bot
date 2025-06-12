from src.simulation_logic import calculer_iterations, SimulationError

if __name__ == "__main__":
    print("=== EXEMPLE SCRIPT LOGIC ===")
    try:
        results = calculer_iterations(1000, 40, 4, 50)
        for line in results['details_text']:
            print(line)

        print("\n=== CUSTOM TEST ===")
        results_custom = calculer_iterations(234, 0.00000650, 0.00000010, 10)
        for line in results_custom['details_text']:
            print(line)

        print("\n=== EDGE CASE: Entry <= Catastrophic ===")
        try:
            results_edge = calculer_iterations(1000, 4, 40, 10)
            for line in results_edge['details_text']:
                print(line)
        except SimulationError as e_edge:
            print(f"Caught expected simulation error for edge case: {e_edge}")

        print("\n=== EDGE CASE: Price becomes zero ===")
        try:
            results_zero = calculer_iterations(100, 10, 0, 99.99999999)
            for line in results_zero['details_text']:
                print(line)
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
