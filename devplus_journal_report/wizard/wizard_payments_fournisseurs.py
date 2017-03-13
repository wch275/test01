# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
#
#    Coded by: Borni DHIFI  (dhifi.borni@gmail.com)
#
#-------------------------------------------------------------------------------

from openerp.osv import osv, fields

class wizard_supplier_payment(osv.Model):
    _name = "wizard.supplier.payment"
    _description = u"Wizard rapport caisse"    

    _columns = {
                'date_debut': fields.date(u'Date de début',required=True),
                'date_fin': fields.date(u'Date de fin',required=True),
                'user_id' :fields.many2one('hr.employee', string='Caissier'),
      
      }
    def print_report(self, cr, uid, ids, context=None):
        datas = {'ids': context.get('active_ids', [])}
        datas['form'] = self.read(cr, uid, ids, context=context)[0]
        return self.pool['report'].get_action(cr, uid, [], 'devplus_journal_report.journal_payment_fournisseurs_report',data=datas, context=context) 
wizard_supplier_payment()
