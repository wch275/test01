# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
#
#    Coded by: Borni DHIFI  (dhifi.borni@gmail.com)
#
#-------------------------------------------------------------------------------

from openerp.osv import osv, fields
import openerp.addons.decimal_precision as dp
import time
from openerp.tools.translate import _

#--------------------------------------------------------------------------------
# bordereau_remise
#--------------------------------------------------------------------------------

STATE_SELECTION=[
       ('draft','Brouillon'),
       ('sent',u'Remis'),
       ('cancel',u'Annulé'),
       ('done',u'Traité'),
        ]
TYPE_SELECTION=[
       ('virement',u'Virement'),
       
        ] 

class ordre_virement_frs(osv.Model):
    _name= "ordre.virement.frs"
    _description = 'Ordre de Virement' 

    def _total(self, cursor, user, ids, name, args, context=None):
        if not ids:
            return {}
        res = {}
        
        for virement in self.browse(cursor, user, ids, context=context):
            res[virement.id]={ 'total':0.0,'nb_virement':0}
            total=0.0
            if virement.line_ids:
                total = reduce(lambda x, y: x + y.amount, virement.line_ids, 0.0)
            nb_virement=len(virement.line_ids)
            res[virement.id]={ 'total':total,'nb_virement':nb_virement}
        return res
    
    _columns = {
                'name':fields.char(u'Reférence',readonly=True,), 
                'payment_mode_id':fields.many2one('payment.mode', 'Compte bancaire',required=True, readonly=True,  states={'draft':[('readonly',False)]}, ), 
                'date_remise': fields.date(u'Date remise'),
                'type':fields.selection(TYPE_SELECTION, 'Type', readonly=True,  states={'draft':[('readonly',False)]}, ),
                'total': fields.function(_total, string="Montant Total", type='float',multi="nb",digits_compute=dp.get_precision('Account')),
                'nb_virement': fields.function(_total, string="Nombre Total", type='integer',multi="nb"),
                'user_id': fields.many2one('res.users', 'Responsable',  states={'done': [('readonly', True)]}),
                'company_id': fields.related('payment_mode_id', 'company_id', type='many2one', relation='res.company', string='Company', store=True, readonly=True),
                'line_ids': fields.one2many('ordre.virement.frs.line', 'ordre_virement_frs_id', 'Lines',readony=True),
                'state':fields.selection(STATE_SELECTION, 'Etat', select=True, readonly=True),
                'comment': fields.text('Note'),   
                }
    
    _defaults = {
        'user_id': lambda self,cr,uid,context: uid,
        'state': 'draft',
        'date_remise': lambda *a: time.strftime('%Y-%m-%d'),
    }

    def action_sent(self, cr, uid, ids, *args):
        ir_seq_obj = self.pool.get('ir.sequence')
        for order in self.read(cr, uid, ids, ['name']):
            if not order['name']:
                c = {}
                
                name = ir_seq_obj.get(cr, uid, 'ordre.virement.frs',context=c)
                self.write(cr, uid, order['id'], {'state': 'sent','name':name})
        return True
 
    
    def action_draft(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state': 'draft'})
        return True
    
    def action_cancel(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state': 'cancel'})
        return True
    
    def action_done(self, cr, uid, ids, *args):
        self.create_move(cr, uid, ids)
        self.write(cr, uid, ids, {'state': 'done'})
        return True   
         
    def unlink(self, cr, uid, ids, context=None):
        for t in self.read(cr, uid, ids, ['state'], context=context):
            if t['state'] not in ('draft', 'cancel'):
                raise osv.except_osv(_('Action Invalide!'), _(u'Vous ne pouvez pas supprimer  oredre de vire;ent(s) qui sont déjà remis.'))
        return super(bordereau_remise, self).unlink(cr, uid, ids, context=context)
    

   
                
ordre_virement_frs()
#-------------------------------------------------------------------------------
# ordre_virement_frs_line
#-------------------------------------------------------------------------------
class ordre_virement_frs_line(osv.Model):
    _name= "ordre.virement.frs.line"
    _description = 'Ordre de Virement Lines' 
    _columns = {
                'numero_virement':fields.char(u'Numéro',), 
                'bank_name':fields.char(u'Banque',), 
                'proprietaire':fields.char(u'Nom de tireur',), 
                'amount':fields.float(u'Montant', digits_compute=dp.get_precision('Account')), 
                'ordre_virement_frs_id': fields.many2one('ordre.virement.frs', 'Order', required=True, ondelete='cascade', select=True),
                'account_voucher_id': fields.many2one('account.voucher', 'Paiement', ondelete='cascade'),
                'state': fields.related('ordre_virement_frs_id','state', type='selection', selection=STATE_SELECTION, string='State'), 
                }
     
    def action_delete(self, cr, uid, ids, context=None):
        context = context or {}
        voucher_obj = self.pool.get('account.voucher')
        for line in self.browse(cr, uid, ids, context=context):
            if line.ordre_virement_frs_id.state == 'draft':
                voucher_obj.write(cr,uid,line.account_voucher_id.id,{'encaisse':False,
                                                                     'state_ordre' : 'non_remis'})
                self.unlink(cr,uid,line.id)
        return True

ordre_virement_frs_line()

