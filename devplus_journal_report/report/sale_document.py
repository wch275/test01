# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
#
#    Coded by: Borni DHIFI  (dhifi.borni@gmail.com)
#
#-------------------------------------------------------------------------------

from openerp import tools
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class sale_document(osv.osv):
    _name = "sale.document"
    _description = "Documents de vente"
    _auto = False
    _rec_name = 'date'

    _columns = {
        'date': fields.date('Date', readonly=True), 
        'partner_id': fields.many2one('res.partner', 'Client', readonly=True),
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
                            ('out_invoice', 'Facture'),
                            ('out_refund', 'Avoir'),
                            ('sale_order', 'Bon de Commande'),
                            ('picking_out', 'Bon de Livraison'),
                           ], 'Type', readonly=True),        
        
        'state': fields.selection([
                            ('draft', 'Brouillon'),
                            ('confirmed', u'Confirmé'),
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
        cr.execute("""CREATE or REPLACE VIEW sale_document as (
            
select concat(11111,id) as id,date(date_invoice) as date,partner_id,number,user_id,amount_total,amount_untaxed,residual,state ,'' as invoice_state ,concat('account.invoice,',id) as ref, 'out_invoice' as type
from account_invoice where type = 'out_invoice'

union

select concat(22222,id) as id,date(date_invoice) as date,partner_id,number,user_id,amount_total,amount_untaxed,residual,state ,'' as invoice_state ,concat('account.invoice,',id) as ref, 'out_refund' as type
from account_invoice where type = 'out_refund'

union  

select concat(33333,id) as id,date(date_order) as date,partner_id,name,user_id,amount_total,amount_untaxed,0,state ,'' as invoice_state, concat('sale.order,',id) as ref,'sale_order' as type
from sale_order

union  
select concat(44444,s.id) as id,date(date) as date,partner_id, s.name,s.create_uid,amount_total,amount_untaxed,0,state , invoice_state  ,concat('stock.picking,',s.id) as ref,'picking_out' as type 
from  stock_picking s left join stock_picking_type st on s.picking_type_id = st.id where  st.code='outgoing'             

  
            )""" )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
