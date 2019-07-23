# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool
from . import configuration
from . import intervention


def register():
    Pool.register(
        configuration.Configuration,
        configuration.ConfigurationSequence,
        intervention.Intervention,
        intervention.WorkingShift,
        module='working_shift_interventions', type_='model')
