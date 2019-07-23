# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from decimal import Decimal
from trytond.model import ModelSQL, ModelView, fields
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval
from trytond.i18n import gettext
from trytond.model.exceptions import AccessError
from trytond.exceptions import UserError
from trytond.modules.working_shift.working_shift import start_date_searcher

__all__ = ['Intervention', 'WorkingShift']

STATES = {
    'readonly': Eval('shift_state') != 'draft',
    }
DEPENDS = ['shift_state']


class Intervention(ModelSQL, ModelView):
    'Intervention'
    __name__ = 'working_shift.intervention'
    code = fields.Char('Code', required=True, readonly=True)
    shift = fields.Many2One('working_shift', 'Working Shift',
        required=True, select=True, ondelete='CASCADE', states=STATES,
        depends=DEPENDS)
    shift_state = fields.Function(fields.Selection([], 'Shift State'),
        'on_change_with_shift_state')
    reference = fields.Char('Reference', states=STATES, depends=DEPENDS)
    contact_name = fields.Char('Contact Name', states=STATES, depends=DEPENDS)
    party = fields.Many2One('party.party', 'Party', states=STATES,
        depends=DEPENDS)
    start = fields.DateTime('Start', required=True, states=STATES,
        depends=DEPENDS)
    start_date = fields.Function(fields.Date('Start Date'),
        'get_start_date', searcher='search_start_date')
    end = fields.DateTime('End', domain=[
            ['OR',
                ('end', '=', None),
                ('end', '>', Eval('start')),
                ],
            ],
        states=STATES, depends=DEPENDS+['start'])
    hours = fields.Function(fields.Numeric('Hours', digits=(16, 2)),
        'on_change_with_hours')
    comments = fields.Text('Comments', states=STATES, depends=DEPENDS)

    @classmethod
    def __setup__(cls):
        super(Intervention, cls).__setup__()
        cls._order = [
            ('code', 'DESC'),
            ('id', 'DESC'),
            ]
        # Copy selection from shift
        Shift = Pool().get('working_shift')
        cls.shift_state.selection = Shift.state.selection

    @staticmethod
    def default_shift_state():
        return 'draft'

    def get_rec_name(self, name):
        res = self.code
        if self.reference:
            res += ' (' + self.reference + ')'
        return res

    @classmethod
    def search_rec_name(cls, name, clause):
        return ['OR',
            ('code',) + tuple(clause[1:]),
            ('reference',) + tuple(clause[1:]),
            ]

    @fields.depends('shift', '_parent_shift.state')
    def on_change_with_shift_state(self, name=None):
        return self.shift.state if self.shift else 'draft'

    def get_start_date(self, name):
        if self.start:
            return self.start.date()

    @classmethod
    def search_start_date(cls, name, clause):
        return start_date_searcher(name, clause)

    @fields.depends('start', 'end')
    def on_change_with_hours(self, name=None):
        if not self.start or not self.end:
            return Decimal(0)
        hours = (self.end - self.start).total_seconds() / 3600.0
        digits = self.__class__.hours.digits
        return Decimal(str(hours)).quantize(Decimal(str(10 ** -digits[1])))

    @classmethod
    def validate(cls, interventions):
        super(Intervention, cls).validate(interventions)
        for intervention in interventions:
            intervention.check_working_shift_period()

    def check_working_shift_period(self):
        error = False
        if self.start < self.shift.start:
            error = True
        if self.shift.end:
            if (self.start >= self.shift.end
                    or (self.end and self.end > self.shift.end)):
                error = True
        if self.end:
            if self.end <= self.shift.start:
                error = True

        if error:
            raise UserError(gettext(
                    'working_shift_interventions.date_outside_working_shift',
                    intervention=self.rec_name,
                    shift=self.shift.rec_name))

    @classmethod
    def create(cls, vlist):
        pool = Pool()
        Sequence = pool.get('ir.sequence')
        Config = pool.get('working_shift.configuration')

        config = Config(1)
        if not config.intervention_sequence:
            raise UserError(gettext(
                'working_shift_interventions.missing_intervention_sequence'))
        for value in vlist:
            if value.get('code'):
                continue
            value['code'] = Sequence.get_id(config.intervention_sequence.id)
        return super(Intervention, cls).create(vlist)

    @classmethod
    def delete(cls, interventions):
        for intervention in interventions:
            if intervention.shift.state != 'draft':
                raise AccessError(gettext(
                    'working_shift_interventions.delete_non_draft_intervention',
                    intervention=intervention.rec_name))
        super(Intervention, cls).delete(interventions)

STATES = {
    'readonly': Eval('state') != 'draft',
    }
DEPENDS = ['state']


class WorkingShift(metaclass=PoolMeta):
    __name__ = 'working_shift'
    interventions = fields.One2Many('working_shift.intervention', 'shift',
        'Interventions', states=STATES, depends=DEPENDS)
