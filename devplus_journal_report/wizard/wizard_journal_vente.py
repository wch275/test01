# encoding: utf8
from openerp.osv import fields, osv


class journal_vente(osv.osv_memory):
    _name = "wizard.journal.vente"
    _description = "Journal vente"
   
    _columns = {
        'date_begin': fields.date('Date début', required=True),
        'date_end': fields.date('Date fin', required=True),
        'clt_exorene' :  fields.boolean('Afficher les clients exorénés de la TVA')
           }

    _defaults = {
    }
    
    def check_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = {}
        
        data['form'] = self.read(cr, uid, ids, ['date_begin', 'date_end','clt_exorene'], context=context)[0]
        for field in ['date_begin', 'date_end','clt_exorene']:
            if isinstance(data['form'][field], tuple):
                data['form'][field] = data['form'][field][0]
        return self._print_report(cr, uid, ids, data, context=context)

    def _print_report(self, cr, uid, ids, data, context=None):
        context['landscape'] = True
        return self.pool['report'].get_action(cr, uid, [], 'devplus_journal_report.report_journal_vente', data=data, context=context)

