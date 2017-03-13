# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
#
#    Author  Borni DHIFI  : dhifi.borni@gmail.com
#    2014
#
#----------------------------------------------------------------------------

from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
#--------------------------------------------------------------------------------
# account_move_line
#--------------------------------------------------------------------------------
class account_move_line(osv.osv):
    _inherit = "account.move.line"
 
    '''inherit to add decimal_precision'''
    
    def _amount_residual(self, cr, uid, ids, field_names, args, context=None):
        return super(account_move_line,self)._amount_residual(cr, uid, ids, field_names, args, context)
    
    _columns = {
        'amount_residual_currency': fields.function(_amount_residual, string='Residual Amount in Currency', multi="residual",
                                                     digits_compute=dp.get_precision('Account'),
                                                     help="The residual amount on a receivable or payable of a journal entry expressed in its currency (maybe different of the company currency)."),
        'amount_residual': fields.function(_amount_residual, string='Residual Amount', multi="residual",
                                            digits_compute=dp.get_precision('Account'),
                                            help="The residual amount on a receivable or payable of a journal entry expressed in the company currency."),

        }    
    
account_move_line()


        