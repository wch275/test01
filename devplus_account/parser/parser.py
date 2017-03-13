# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
#
#    Copyright (C) 2014  .
#  Amira
#
#----------------------------------------------------------------------------

from openerp.report import report_sxw
from openerp.addons.devplus_amount_to_text import convertion
from openerp.osv import osv


class parser_amount(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(parser_amount, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'amount_to_text':self._amount_to_text,
        })

    def _amount_to_text(self, montant):
            devis = 'Dinar'      
            return convertion.trad(montant, devis)
  
class report_ordrevirement(osv.AbstractModel):
    _name = 'report.devplus_account.report_ordre_virement'
    _inherit = 'report.abstract_report'
    _template = 'devplus_account.report_ordre_virement'
    _wrapped_report_class = parser_amount


