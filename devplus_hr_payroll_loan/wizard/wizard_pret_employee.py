# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
#
#    Copyright (C) 2014  .
#    Coded by: Borni DHIFI  (dhifi.borni@gmail.com)
#
#----------------------------------------------------------------------------

from openerp.osv import fields, osv
from openerp.tools.translate import _

class wizard_pret_employee(osv.osv_memory):
    _name = 'wizard.pret.employee'
    _description = 'Wizard pret employee'
    _columns = {

                   'period_id_from': fields.many2one('account.period','Periode debut',  required=True, select=1),
                'period_id_to': fields.many2one('account.period','Periode fin', required=True,  select=1),
    } 
  


    def print_report(self, cr, uid, ids, context=None):
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'hr.employee'
        datas['form'] = self.read(cr, uid, ids, context=context)[0]
       
        return self.pool['report'].get_action(cr, uid, [], 'devplus_hr_payroll_loan.report_pret_employee', data=datas, context=context)

    

wizard_pret_employee()