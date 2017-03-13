# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
#
#    Copyright (C) 2014   karim rouag
#
#----------------------------------------------------------------------------
from openerp.osv import osv, fields
import openerp.addons.decimal_precision as dp

class ir_ui_menu(osv.Model):
    _inherit = "ir.ui.menu"
    _columns = {
                 'active':fields.boolean('Active' ), 
                }
    _defaults = {  
        'active': True,  
        }
ir_ui_menu()   
