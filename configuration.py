# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import fields
from trytond.pyson import Eval
from trytond.pool import Pool, PoolMeta

__all_ = ['Configuration', 'ConfigurationSequence']

intervention_sequence = fields.Many2One(
        'ir.sequence', "Intervention Sequence", required=True,
        domain=[
            ('company', 'in',
                [Eval('context', {}).get('company', -1), None]),
            ('code', '=', 'working_shift.intervention'),
            ])

def default_func(field_name):
    @classmethod
    def default(cls, **pattern):
        return getattr(
            cls.multivalue_model(field_name),
            'default_%s' % field_name, lambda: None)()
    return default


class Configuration(metaclass=PoolMeta):
    __name__ = 'working_shift.configuration'
    intervention_sequence = fields.MultiValue(intervention_sequence)

    @classmethod
    def multivalue_model(cls, field):
        pool = Pool()
        if field == 'intervention_sequence':
            return pool.get('working_shift.configuration.sequence')
        return super(Configuration, cls).multivalue_model(field)

    default_intervention_sequence = default_func('intervention_sequence')


class ConfigurationSequence(metaclass=PoolMeta):
    __name__ = 'working_shift.configuration.sequence'
    intervention_sequence = intervention_sequence

    @classmethod
    def default_intervention_sequence(cls):
        pool = Pool()
        ModelData = pool.get('ir.model.data')
        try:
            return ModelData.get_id(
                'working_shift_interventions', 'sequence_intervention')
        except KeyError:
            return None
