# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
#
#    Copyright (C) 2014  .
#    Coded by: Borni DHIFI  (dhifi.borni@gmail.com)
#
#----------------------------------------------------------------------------

from openerp  import netsvc
from openerp.osv import fields, osv
from openerp  import pooler
from openerp.tools.translate import _
import time
from datetime import date, datetime
import openerp.addons.decimal_precision as dp



#-------------------------------------------------------------------------------
# hr_payroll_bulletin
#-------------------------------------------------------------------------------
class hr_payroll_bulletin(osv.osv):
    _inherit = "hr.payroll.bulletin"
    
    def get_prets(self, cr, uid, pointage_line):
        all_pret=super(hr_payroll_bulletin, self).get_prets(cr, uid,  pointage_line)
        
        loan_line_obj = self.pool.get('hr.payroll.loan.line')
        ids_loan_line = loan_line_obj.search(cr, uid, [('month_id', '=', pointage_line.pointage_id.month_id.id) ])
        
        for  loan_line_id in ids_loan_line :
            loan_line = loan_line_obj.browse(cr, uid, loan_line_id)
            if loan_line.loan_id.employee_id.id == pointage_line.employee_id.id  and loan_line.loan_id.state == 'progress':
                pret = {'name' : loan_line.name,
                        'montant':loan_line.amount,
                       }
                all_pret.append(pret)
        return all_pret
    
hr_payroll_bulletin()


class hr_payroll_loan(osv.osv):
    _name = 'hr.payroll.loan'
    _inherit = ['mail.thread']  
    _description = u'Prêts' 

    STATES = [
              ('draft', 'Brouillon'),
              ('progress', 'En cours'),
              ('done', 'Terminé'),
              ('cancelled', 'Annulé')                    
            ]
    def _get_company_id(self, cr, uid, data, context={}):
        if context is None:
            context = {}
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        company_id = context.get('company_id', user.company_id.id)
        return  company_id  
           
    _columns = {
                'description': fields.char('Description', size=64, readonly=True, states={'draft':[('readonly', False)]},),
                'name': fields.char('Référence'),
                'date': fields.date('Date', readonly=True, states={'draft':[('readonly', False)]}, select=1),
                'employee_id': fields.many2one('hr.employee', u'Employé', required=True, readonly=True, states={'draft':[('readonly', False)]}),
                'period_id_from': fields.many2one('hr.month', u'Mois début', readonly=True, required=True, states={'draft':[('readonly', False)]}, select=1),
                'period_id_to': fields.many2one('hr.month', u'Mois fin', readonly=True, required=True, states={'draft':[('readonly', False)]}, select=1),
                'number_monthly': fields.integer('Nombre de mois' , readonly=True, states={'draft':[('readonly', False)]}) ,
                'amount':fields.float('Montant Prêt', digits_compute=dp.get_precision('Account'), readonly=True, states={'draft':[('readonly', False)]}),
                'amount_monthly':fields.float('Retenue mensuelle', digits_compute=dp.get_precision('Account'), readonly=True, states={'draft':[('readonly', False)]}),
                'company_id': fields.many2one('res.company', u'Société', change_default=True, readonly=True, required=True, states={'draft':[('readonly', False)]}),
                'note': fields.text('Notes'),
                'state': fields.selection(STATES, 'Etat', select=True, readonly=True, track_visibility='onchange',),
                'loan_line_ids': fields.one2many('hr.payroll.loan.line', 'loan_id', u'Lignes prêts', readonly=True, states={'draft':[('readonly', False)]}),
                  }
    
    _defaults = {  
                 'date': lambda *a: time.strftime('%Y-%m-%d'),
                 'state':'draft',
                 'company_id': _get_company_id,
                }
    
    def create(self, cr, uid, vals, context=None):
        if not vals.get('name', False):
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'hr.payroll.loan', context=context) or '/'
        return super(hr_payroll_loan, self).create(cr, uid, vals, context=context)
    
    def on_change_date(self, cr, uid, ids, period_id_from,period_id_to, context=None):
        res = {}
        number_monthly=0
        if period_id_from and period_id_to and  period_id_from<period_id_to :
            number_monthly=period_id_to-period_id_from+1
        res['value']= {'number_monthly':number_monthly,}
        print'res-----------',res
        return  res

    def onchange_amount(self, cr, uid, ids, number_monthly, amount): 
        result = {}
        if number_monthly :            
            result = {'value': {  'amount_monthly' :  float(amount / number_monthly) }  }
        return result
    
    
    def action_confirm(self, cr, uid, ids, *args):
        '''
        validate loan
        @return: True
        '''
        self.write(cr, uid, ids, {'state': 'progress'})
        # create echeance
        period_obj = self.pool.get('account.period')
        loan = self.browse(cr, uid, ids[0],)
        period_id_from = loan.period_id_from
        i = 0;
        all_line = []
        while i < loan.number_monthly  :
            period = period_obj.browse(cr, uid, (period_id_from.id) + i)
            loan_line = (0, 0, {'name' :u'Prêt période de ' + period.name,
                               'month_id':period.id,
                               'amount' : loan.amount_monthly,
                          }
                    )
            all_line.append(loan_line)
            i = i + 1
        value = {  'loan_line_ids': all_line }   
        self.write(cr, uid, ids, value)        
        return True
    
    def action_done(self, cr, uid, ids, *args):
        '''
        cancel loan
        @return: True
        '''
        self.write(cr, uid, ids, {'state': 'done'})
        return True
    
    def action_cancelled(self, cr, uid, ids, *args):
        '''
        cancel loan
        @return: True
        '''
        self.write(cr, uid, ids, {'state': 'cancelled'})
        return True
    
      
hr_payroll_loan()

class hr_payroll_loan_line(osv.osv):
    _name = 'hr.payroll.loan.line'
    _description = u'Lignes des prêts' 
    _columns = {
                'name': fields.char('Description'),
                'month_id': fields.many2one('hr.month', u'Mois', required=True,),
                'amount':fields.float('Montant', digits_compute=dp.get_precision('Account')),
                'loan_id':fields.many2one('hr.payroll.loan', u'Prêt', required=True),
                'note': fields.text('Notes'),
                'etat':fields.selection([('new',' En cours'), ('done','Payé'),], 'État de Prêt'),
        }
   
hr_payroll_loan_line()
 
 
