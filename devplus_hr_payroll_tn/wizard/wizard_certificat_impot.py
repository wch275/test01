# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
#
#    Copyright (C) 2014  .
#    Coded by: Borni DHIFI  (dhifi.borni@gmail.com)
#
#----------------------------------------------------------------------------
 
from openerp.osv import fields, osv
from openerp.tools.translate import _

class wizard_certificat_impot(osv.osv_memory):
    _name = 'wizard.certificat.impot'
    _description = 'Wizard certificat impot'

    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id

    _columns = {
         'fiscalyear_id':fields.many2one('account.fiscalyear', 'Année', required=True),
         'company_id':fields.many2one('res.company', u'Société', required=True),
       }

    _defaults = {
        'company_id' : _get_default_company,
#         'fiscalyear_id' : _get_default_period,

    }


    def print_certificat(self, cr, uid, ids, context=None):
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'wizard_certificat_impot'
        datas['form'] = self.read(cr, uid, ids, context=context)[0]
        return self.pool['report'].get_action(cr, uid, [], 'devplus_hr_payroll_tn.report_certificat_impot', data=datas, context=context)
 

wizard_certificat_impot()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

