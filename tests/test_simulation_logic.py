import unittest
from src.simulation_logic import calculer_iterations, SimulationError
from src.constants import error_messages

class TestSimulationLogic(unittest.TestCase):

    def test_example_case_from_user(self):
        # calculer_iterations(1000, 40, 4, 50)
        # Expected iterations based on manual run of user's script:
        # P_iter: [40, 20, 10, 5, 2.5] -> 2.5 is <= 4, so last is 5. User script added the one that broke threshold.
        # The user script's loop:
        # 1. P=40. P_next=20.
        # 2. P=20. P_next=10.
        # 3. P=10. P_next=5.
        # 4. P=5.  P_next=2.5. (2.5 <= 4, so this is the last iteration according to user script)
        # The provided simulation_logic.py seems to capture this correctly.
        # Iterations: [40, 20, 10, 5, 2.5] -> 5 iterations. Amount/iter = 1000/5 = 200.
        # Q: [200/40=5, 200/20=10, 200/10=20, 200/5=40, 200/2.5=80]

        results = calculer_iterations(balance=1000, prix_entree=40, prix_catastrophique=4, drop_percent=50)
        self.assertEqual(results["inputs"]["balance"], 1000)
        self.assertEqual(results["nombre_total_iterations"], 5)
        self.assertAlmostEqual(results["montant_par_iteration"], 200.0)
        self.assertEqual(len(results["prix_iterations"]), 5)
        self.assertAlmostEqual(results["prix_iterations"][0], 40)
        self.assertAlmostEqual(results["prix_iterations"][1], 20)
        self.assertAlmostEqual(results["prix_iterations"][2], 10)
        self.assertAlmostEqual(results["prix_iterations"][3], 5)
        self.assertAlmostEqual(results["prix_iterations"][4], 2.5) # This is the price that hit/passed catastrophic

        self.assertEqual(len(results["quantites_par_iteration"]), 5)
        self.assertAlmostEqual(results["quantites_par_iteration"][0], 5.0)    # 200/40
        self.assertAlmostEqual(results["quantites_par_iteration"][1], 10.0)   # 200/20
        self.assertAlmostEqual(results["quantites_par_iteration"][2], 20.0)   # 200/10
        self.assertAlmostEqual(results["quantites_par_iteration"][3], 40.0)   # 200/5
        self.assertAlmostEqual(results["quantites_par_iteration"][4], 80.0)   # 200/2.5

        # Check details_text structure (basic checks)
        self.assertIn("Balance: 1000.00", results["details_text"])
        self.assertIn("Nombre total de niveaux de DCA: 5", results["details_text"])
        self.assertIn("Montant par niveau de DCA: 1000.00 / 5 = 200.00", results["details_text"])
        self.assertTrue(any("Niveau 5:" in line and "80.00000000 (quantité)" in line for line in results["details_text"]))


    def test_prix_entree_equals_catastrophique(self):
        # If entry price is already at catastrophic, only 1 iteration at that price.
        results = calculer_iterations(balance=100, prix_entree=10, prix_catastrophique=10, drop_percent=10)
        self.assertEqual(results["nombre_total_iterations"], 1)
        self.assertAlmostEqual(results["prix_iterations"][0], 10)
        self.assertAlmostEqual(results["montant_par_iteration"], 100)
        self.assertAlmostEqual(results["quantites_par_iteration"][0], 10)

    def test_prix_entree_below_catastrophique(self):
        with self.assertRaisesRegex(SimulationError, error_messages.SIM_ERROR_PRIX_ENTREE_MUST_BE_GREATER):
            calculer_iterations(balance=100, prix_entree=9, prix_catastrophique=10, drop_percent=10)

    def test_invalid_inputs(self):
        with self.subTest("Negative balance"):
            with self.assertRaisesRegex(SimulationError, error_messages.SIM_ERROR_BALANCE_POSITIVE):
                calculer_iterations(balance=-100, prix_entree=10, prix_catastrophique=5, drop_percent=10)

        with self.subTest("Zero balance"):
            with self.assertRaisesRegex(SimulationError, error_messages.SIM_ERROR_BALANCE_POSITIVE):
                calculer_iterations(balance=0, prix_entree=10, prix_catastrophique=5, drop_percent=10)

        with self.subTest("Negative entry price"):
            with self.assertRaisesRegex(SimulationError, error_messages.SIM_ERROR_PRIX_ENTREE_POSITIVE):
                calculer_iterations(balance=100, prix_entree=-10, prix_catastrophique=5, drop_percent=10)

        with self.subTest("Zero entry price"):
            with self.assertRaisesRegex(SimulationError, error_messages.SIM_ERROR_PRIX_ENTREE_POSITIVE):
                calculer_iterations(balance=100, prix_entree=0, prix_catastrophique=5, drop_percent=10)

        with self.subTest("Negative catastrophic price"):
            with self.assertRaisesRegex(SimulationError, error_messages.SIM_ERROR_PRIX_CATASTROPHIQUE_NOT_NEGATIVE):
                calculer_iterations(balance=100, prix_entree=10, prix_catastrophique=-5, drop_percent=10)

        with self.subTest("Drop percent zero"):
            with self.assertRaisesRegex(SimulationError, error_messages.SIM_ERROR_DROP_PERCENT_RANGE):
                calculer_iterations(balance=100, prix_entree=10, prix_catastrophique=5, drop_percent=0)

        with self.subTest("Drop percent 100"):
            with self.assertRaisesRegex(SimulationError, error_messages.SIM_ERROR_DROP_PERCENT_RANGE):
                calculer_iterations(balance=100, prix_entree=10, prix_catastrophique=5, drop_percent=100)

        with self.subTest("Drop percent negative"):
            with self.assertRaisesRegex(SimulationError, error_messages.SIM_ERROR_DROP_PERCENT_RANGE):
                calculer_iterations(balance=100, prix_entree=10, prix_catastrophique=5, drop_percent=-10)

        with self.subTest("Drop percent > 100"):
            with self.assertRaisesRegex(SimulationError, error_messages.SIM_ERROR_DROP_PERCENT_RANGE):
                calculer_iterations(balance=100, prix_entree=10, prix_catastrophique=5, drop_percent=110)

    def test_no_drop_possible_high_catastrophic(self):
        # Price starts at 10, catastrophic is 9, drop is 50%. 10 * (1-0.5) = 5.
        # So, first level is 10. Next level is 5, which is <= 9.
        # Iterations: [10, 5]
        results = calculer_iterations(balance=100, prix_entree=10, prix_catastrophique=9, drop_percent=50)
        self.assertEqual(results["nombre_total_iterations"], 2)
        self.assertAlmostEqual(results["prix_iterations"][0], 10)
        self.assertAlmostEqual(results["prix_iterations"][1], 5)
        self.assertAlmostEqual(results["montant_par_iteration"], 50)

    def test_zero_division_if_iterations_is_zero(self):
        # This scenario should be caught by "prix_entree <= prix_catastrophique" validation.
        # The function raises SimulationError before a ZeroDivisionError can occur from nombre_total_iterations = 0.
        # If for some reason it wasn't, this test would be for that.
        # For now, this is covered by test_prix_entree_below_catastrophique
        pass

    def test_precision_and_small_numbers(self):
        results = calculer_iterations(balance=234, prix_entree=0.00000650, prix_catastrophique=0.00000010, drop_percent=10)
        self.assertTrue(results["nombre_total_iterations"] > 0) # Just ensure it runs
        self.assertTrue(len(results["details_text"]) > 5) # Check some output is generated
        # Example from logic file: results in 38 iterations
        self.assertEqual(results["nombre_total_iterations"], 38)
        self.assertAlmostEqual(results["montant_par_iteration"], 234 / 38)
        # Check that the last calculated price for DCA is indeed at or below catastrophic,
        # or if it's above, the *next* one would be.
        # The logic in simulation_logic includes the price that breaches the catastrophic threshold.
        last_dca_price = results["prix_iterations"][-1]
        self.assertTrue(last_dca_price <= results["inputs"]["prix_catastrophique"] or \
                        (len(results["prix_iterations"]) > 1 and \
                         results["prix_iterations"][-2] * (1 - results["inputs"]["drop_percent"]/100) <= results["inputs"]["prix_catastrophique"]) or \
                        (len(results["prix_iterations"]) == 1 and \
                         results["inputs"]["prix_entree"] * (1 - results["inputs"]["drop_percent"]/100) <= results["inputs"]["prix_catastrophique"])
                        )


if __name__ == '__main__':
    unittest.main()

