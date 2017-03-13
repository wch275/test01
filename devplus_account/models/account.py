# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
#
#    Coded by: Borni DHIFI  (dhifi.borni@gmail.com)
#
#-------------------------------------------------------------------------------

from openerp.osv import osv, fields

class account_journal(osv.Model): 
    _inherit = "account.journal"
    _columns = {
                'use_payment':fields.boolean(u'Utilisé comme mode de paiement'), 
                }

account_journal()   