# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
#
#    Copyright (C) 2014  .
#    Coded by: Borni DHIFI  (dhifi.borni@gmail.com)
#
#----------------------------------------------------------------------------

from openerp.osv import fields, osv
from openerp.tools.translate import _

class res_company(osv.osv):
    _inherit = "res.company"    
    _columns = {
            'cnss' : fields.char('CNSS', size=11),
            'code_exploitation' : fields.char(u"Code d'exploitation", size=4),
            }
res_company()
 
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
