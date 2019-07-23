# This file is part working_shift_interventions module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
import unittest
import doctest
import trytond.tests.test_tryton
from trytond.tests.test_tryton import ModuleTestCase
from trytond.tests.test_tryton import doctest_setup, doctest_teardown
from trytond.tests.test_tryton import doctest_checker
from trytond.tests.test_tryton import suite as test_suite


class WorkingShiftInterventionsTestCase(ModuleTestCase):
    'Test Working Shift Interventions module'
    module = 'working_shift_interventions'


def suite():
    suite = test_suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
            WorkingShiftInterventionsTestCase))
    suite.addTests(doctest.DocFileSuite(
            'scenario_working_shift_interventions.rst',
            setUp=doctest_setup, tearDown=doctest_teardown, encoding='utf-8',
            checker=doctest_checker,
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE))
    return suite
