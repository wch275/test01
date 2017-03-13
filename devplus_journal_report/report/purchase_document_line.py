# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
#
#    Coded by: Borni DHIFI  (dhifi.borni@gmail.com)
#
#-------------------------------------------------------------------------------

from openerp import tools
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class purchase_document_line(osv.osv):
    _name = "purchase.document.line"
    _description = "Documents d'Achat"
    _auto = False
    _rec_name = 'date'

    _columns = {
        'product_id': fields.many2one('product.product', 'Produit', readonly=True),
        'product_uom_qty': fields.float(u'Quantité', readonly=True, digits_compute=dp.get_precision('Account')),
        'price_unit': fields.float('Prix unitaire', readonly=True, digits_compute=dp.get_precision('Account')),
        'price_subtotal': fields.float('Sous-total', readonly=True, digits_compute=dp.get_precision('Account')),                
        'date': fields.date('Date', readonly=True), 
        'partner_id': fields.many2one('res.partner', 'Fournisseur', readonly=True),
        'number': fields.char(u'Référence', readonly=True),
        'user_id': fields.many2one('res.users', 'Vendeur', readonly=True),
        'amount_total': fields.float('Total', readonly=True, digits_compute=dp.get_precision('Account')),
        'amount_untaxed': fields.float('Total HT', readonly=True, digits_compute=dp.get_precision('Account')),
        'residual': fields.float('Reste à payer', readonly=True, digits_compute=dp.get_precision('Account')),
        'invoice_state': fields.char(u'Contrôle facturation', readonly=True),
        'ref': fields.reference(u'Numéro', selection=[('account.invoice','Facture'),
                                                        ('sale.order','Bon de Commande'),
                                                         ('stock.picking','Bon de livraison')
                                                        ]),
        'type': fields.selection([
                            ('in_invoice', 'Facture'),
                            ('in_refund', 'Avoir'),
                            ('purchase_order', 'Bon de Commande'),
                            ('picking_in', 'Bon de réception'),
                           ], 'Type', readonly=True),        
        
        'state': fields.selection([
                            ('draft', 'Brouillon'),
                            ('confirmed', u'Confirmé'),
                            ('approved', u'Confirmé'),
                            ('open', u'Ouverte'),
                            ('paid', u'Payé'),
                            ('assigned', u'Prêt à transférer'),
                            ('manual', u'Commande à facturer'),
                            ('done', u'Terminée'),
                            ('exception', 'Exception'),
                            ('cancel', u'Annulée'),
                           ], 'Etat', readonly=True),
    }
    _order = 'date desc'

 
    def init(self, cr):
        #self._table = sale_document
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW purchase_document_line as (
 
select concat(11111,line.id) as id,date(invoice.date_invoice) as date,invoice.partner_id,invoice.user_id,invoice.number,product_id,quantity as product_uom_qty,price_unit,price_subtotal ,invoice.state,'' as invoice_state ,concat('account.invoice,',invoice.id) as ref, 'in_invoice' as type
from account_invoice_line line
left join account_invoice invoice  on line.invoice_id  = invoice.id
where invoice.type = 'in_invoice'
union

select concat(22222,line.id) as id,date(invoice.date_invoice) as date,invoice.partner_id,invoice.user_id,invoice.number,product_id,quantity as product_uom_qty,price_unit,price_subtotal ,invoice.state,'' as invoice_state ,concat('account.invoice,',invoice.id) as ref, 'in_refund' as type
from account_invoice_line line  
left join account_invoice invoice  on line.invoice_id  = invoice.id
 where invoice.type = 'in_refund'
union  

select concat(33333,line.id) as id,date(purchase.date_order) as date,purchase.partner_id,purchase.create_uid,purchase.name,product_id,product_qty as product_uom_qty,price_unit,0.0 as price_subtotal ,purchase.state,'' as invoice_state,  concat('purchase.order,',purchase.id) as ref,'purchase_order' as type
from purchase_order_line line
left join purchase_order purchase  on line.order_id  = purchase.id 
 
union  
select concat(44444,line.id) as id,date(picking.date) as date,picking.partner_id,picking.create_uid,picking.name,product_id,product_uom_qty,price_unit,0.0 as price_subtotal,picking.state,'' as invoice_state,concat('stock.picking,',picking.id) as ref,'picking_in' as type 
from  stock_move line
left join stock_picking picking on line.picking_id=picking.id
left join stock_picking_type st on picking.picking_type_id = st.id 
where  st.code='incoming'  
 

  
            )""" )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
