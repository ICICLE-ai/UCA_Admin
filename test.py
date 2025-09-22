import unittest

from colorama import Fore, Style, init

from src.database.rules_engine.rules_engine_unit_test import TestRuleEngineClient

if __name__ == "__main__":
	# auto resetting colorama color
	init(autoreset=True)
	
	# testing the RuleEngineClient class in then src/database/rules_engine/rules_engine_client.py file
	print(Fore.CYAN + Style.BRIGHT + "running test for rules engine class")
	rules_engine_test_suite = unittest.TestLoader().loadTestsFromTestCase(TestRuleEngineClient)
	unittest.TextTestRunner(verbosity=2).run(rules_engine_test_suite)
	print()