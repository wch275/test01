# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------------
#
#    Copyright (C) 2014  .
#    Coded by: Karim Rouag  
#
#----------------------------------------------------------------------------
from openerp.osv import osv, fields

class rubrique(osv.Model):
    _inherit= "hr.payroll.ligne_rubrique"
    _columns = {
                'echlon_id':fields.many2one('salary_grid.echlon', 'Echlon', ), 
                }