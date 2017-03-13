# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
#
#    Coded by: Borni DHIFI  (dhifi.borni@gmail.com)
#
#-------------------------------------------------------------------------------

from openerp.osv import fields, osv
from openerp.tools.translate import _

class payment_transfert(osv.osv_memory):
    _name = "account.payment_transfert"
    
    _columns = {
         'name': fields.char(u"Name", ),
         'payment_mode_id':fields.many2one('payment.mode', 'Compte bancaire',required=True),
         'date_remise':fields.date('Date remise'),
         'type' : fields.many2one('account.payment.mode','Type'),

    }
       
    def view_init(self, cr, uid, fields_list, context=None):
        if context is None:
            context = {}
        res = super(payment_transfert, self).view_init(cr, uid, fields_list, context=context)
        account_voucher_obj = self.pool.get('account.voucher')
        active_ids = context.get('active_ids',[])
        for account_voucher in account_voucher_obj.browse(cr, uid, active_ids, context=context):
            if account_voucher.encaisse: 
                print'-------------------encaisse',account_voucher.encaisse
                raise osv.except_osv(_('Attention!'), _(u'Les chéques sélectionnés sont déjà encaissés.'))
            if account_voucher.state=='draft': 
                raise osv.except_osv(_('Attention!'), _(u"Vous ne pouvez pas remettre des chéques en état Brouillon. Veuillez les confirmés tout d'abord ."))
            if account_voucher.payment_mode_id.name not in(u"Traite", u"Chèque" ) :
                raise osv.except_osv(_('Attention!'), _(u"Vous ne pouvez pas remettre que des chéques ou des Traites ."))
        return res

    def create_bordereau(self, cr, uid, ids, context=None):
        context = dict(context or {})
        account_voucher_obj = self.pool.get('account.voucher')
        bordereau_remise_obj = self.pool.get('account.bordereau_remise')
        active_ids = context.get('active_ids', [])
        data=self.browse(cr,uid,ids[0])
        bordereau_remise_id=bordereau_remise_obj.create(cr,uid,{'payment_mode_id':data.payment_mode_id.id})
        
        type_borderau='cheque'
        
        for voucher in account_voucher_obj.browse(cr, uid, active_ids, context=context):
            if voucher.payment_mode_id.name==u"Traite" :
                type_borderau='effet'
            line_val = {
                'numero_cheque': voucher.reference,
                'bank_name': voucher.bank_name,
                'proprietaire': voucher.proprietaire,
                'amount': voucher.amount,
                'bordereau_remise_id': bordereau_remise_id,
                'account_voucher_id':voucher.id,
                'type':voucher.payment_mode_id.id,
                }
            self.pool.get('account.bordereau_remise.line').create(cr, uid, line_val, context=context)
            account_voucher_obj.write(cr,uid,voucher.id,{'encaisse':True,'state_bordereau':'remis'})
            
        bordereau_remise_obj.write(cr,uid,bordereau_remise_id,{'type':type_borderau})    
        mod_obj = self.pool.get('ir.model.data')    
        res = mod_obj.get_object_reference(cr, uid, 'devplus_account', 'bordereau_remise_form')
        res_id = res and res[1] or False,

        return {
            'name': _('Bordereau de remise'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': [res_id],
            'res_model': 'account.bordereau_remise',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'res_id': bordereau_remise_id  or False,
        }   



