# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
#
#    Copyright (C) 2014  .
#    TreamIT
#
#----------------------------------------------------------------------------

from openerp.osv import osv
from openerp.report import report_sxw


class report_pret_employee_print(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(report_pret_employee_print, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
         'get_employees': self._get_employees,
          'get_prets':self.get_prets,
          'get_period':self.get_period,
        })

    def _get_employees(self, ids):
        employees = self.pool.get('hr.employee').browse(self.cr, self.uid, ids)
        return employees
    
    def get_period(self,ids):
        period_obj = self.pool.get('account.period').browse(self.cr, self.uid,ids)
        print period_obj
        return period_obj
   
 
    def get_prets(self,employee_id):
        loan_obj = self.pool.get('hr.payroll.loan')
        loan_ids = loan_obj.search(self.cr, self.uid,[('employee_id', '=', employee_id) ])
        return loan_obj.browse(self.cr, self.uid,loan_ids)
    
class report_note(osv.AbstractModel):
    _name = 'report.devplus_hr_payroll_loan.report_pret_employee'
    _inherit = 'report.abstract_report'
    _template = 'devplus_hr_payroll_loan.report_pret_employee'
    _wrapped_report_class = report_pret_employee_print

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
