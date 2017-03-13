# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
#
#    Copyright (C) 2014  .
#    Coded by Borni DHIFI
#
# ----------------------------------------------------------------------------
from openerp.osv import osv, fields


class payroll_account(osv.osv):
    _inherit = 'hr.payroll.parametres'
    _columns = {
        'account_journal_id': fields.many2one('account.journal', 'Journal de Paie',),
        # a la charge de  employee
        'account_brut_id': fields.many2one('account.account', 'Brut',),
        'account_net_paye_id': fields.many2one('account.account', u'Net à payer',),
        'account_cnss_id': fields.many2one('account.account', 'CNSS',),
        'account_irpp_id': fields.many2one('account.account', 'IRPP',),
        'account_prime_id': fields.many2one('account.account', u'Primes',),
        'account_retenue_id': fields.many2one('account.account', u'Retenues',),
        # a la charge de emplyoeur
        'account_tfp_d_id': fields.many2one('account.account', u' TFP : Compte de débit',),
        'account_tfp_c_id': fields.many2one('account.account', u' TFP : Compte de crédit',),
        'account_foprolos_d_id': fields.many2one('account.account', u' FoProLos : Compte de débit',),
        'account_foprolos_c_id': fields.many2one('account.account', u' FoProLos : Compte de crédit',),
        'account_cnss_d_id': fields.many2one('account.account', u'CNSS : Compte de débit',),
        'account_cnss_c_id': fields.many2one('account.account', u'CNSS : Compte de crédit',),
        'account_accident_travail_d_id': fields.many2one('account.account', u' Accident de travail : Compte de débit',),
        'account_accident_travail_c_id': fields.many2one('account.account', u' Accident de travail : Compte de crédit',),
        'taux_tfp': fields.float('Taux TFP'), 
        'taux_accident_travail': fields.float('Taux Accident de travail'), 
#         'taux_cnss': fields.float('Taux Cotisation'), 
        'taux_cotisation': fields.float('Taux Cotisation'), 
        'taux_foprolos': fields.float('Taux FoProLos'), 
                       
    }
payroll_account()
