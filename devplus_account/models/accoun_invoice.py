# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
#
#    Author  Borni DHIFI  : dhifi.borni@gmail.com
#    2014
#
#----------------------------------------------------------------------------

from openerp import models, fields, api, _

class account_invoice(models.Model): 
    _inherit = "account.invoice"

    supplier_invoice_number = fields.Char(string=u'Numéro de facture fournisseur',
         readonly=True,copy=False, states={'draft': [('readonly', False)]})
       
    #TODO: la ligne des produits génére comptablement prend le nom du premier article
    #modifier la description par : vente..
    
    def inv_line_characteristic_hashcode(self, invoice_line):
        """Overridable hashcode generation for invoice lines. Lines having the same hashcode
        will be grouped together if the journal has the 'group line' option. Of course a module
        can add fields to invoice lines that would need to be tested too before merging lines
        or not."""
        return "%s-%s-%s-%s" % (
            invoice_line['account_id'],
            invoice_line.get('tax_code_id', "False"),
            # invoice_line.get('product_id',"False"),
            invoice_line.get('analytic_account_id', "False"),
            invoice_line.get('date_maturity', "False"))
        
    def _check_supplier_invoice_number(self, cr, uid, ids, context=None):
        for invoice in self.browse(cr, uid, ids, context):
            if invoice.type =='in_invoice' and invoice.supplier_invoice_number:
                count=self.search_count(cr,uid,[('id','!=',invoice.id),
                                                ('type','=','in_invoice'),
                                                ('partner_id','=',invoice.partner_id.id),
                                                ('supplier_invoice_number','=',invoice.supplier_invoice_number)
                                                ]
                                        )
                if count > 0 :
                    return False
        return True
    
    _constraints = [(_check_supplier_invoice_number, 'Numéro de facture fournisseur doit être unique par Fournisseur', ['supplier_invoice_number']), ] 
     
