# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
#
#    Coded by: Borni DHIFI  (dhifi.borni@gmail.com)
#
#-------------------------------------------------------------------------------

from openerp.osv import fields, osv
from openerp.tools.translate import _

class payment_transfert_virement(osv.osv_memory):
    _name = "account.payment_transfert.virement"
    
    _columns = {
         'name': fields.char(u"Name", ),
         'payment_mode_id':fields.many2one('payment.mode', 'Compte bancaire',required=True),
         'date_remise':fields.date('Date remise'),
         'type' : fields.many2one('account.payment.mode','Type'),

    }
       
    def view_init(self, cr, uid, fields_list, context=None):
        if context is None:
            context = {}
        res = super(payment_transfert_virement, self).view_init(cr, uid, fields_list, context=context)
        account_voucher_obj = self.pool.get('account.voucher')
        active_ids = context.get('active_ids',[])
        for account_voucher in account_voucher_obj.browse(cr, uid, active_ids, context=context):
            if account_voucher.encaisse:
                print'-------------------encaisse',account_voucher.encaisse
                raise osv.except_osv(_('Attention!'), _(u'Les virements sélectionnés sont déjà encaissés.'))
            if account_voucher.state=='draft': 
                raise osv.except_osv(_('Attention!'), _(u"Vous ne pouvez pas remettre des virements en état Brouillon. Veuillez les confirmés tout d'abord ."))
            if account_voucher.payment_mode_id.name not in( u"Virement") :
                raise osv.except_osv(_('Attention!'), _(u"Vous ne pouvez pas remettre que des virement ."))
        return res




    def create_ordre_virement(self, cr, uid, ids, context=None):
        context = dict(context or {})
        account_voucher_obj = self.pool.get('account.voucher')
        ordre_virement_frs_obj = self.pool.get('ordre.virement.frs')
        active_ids = context.get('active_ids', [])
        data=self.browse(cr,uid,ids[0])
        ordre_virement_frs_id=ordre_virement_frs_obj.create(cr,uid,{'payment_mode_id':data.payment_mode_id.id})
        type_ordre='virement'
        for voucher in account_voucher_obj.browse(cr, uid, active_ids, context=context):
            print'voucher.payment_mode_id.id-----------------------',voucher.payment_mode_id.name
            line_val = {
                'numero_virement': voucher.partner_id.bank_ids.acc_number,
                'bank_name': voucher.partner_id.bank_ids.bank_name,
                'proprietaire': voucher.partner_id.name,
                'amount': voucher.amount,
                'ordre_virement_frs_id': ordre_virement_frs_id,
                'account_voucher_id':voucher.id,
                }
            self.pool.get('ordre.virement.frs.line').create(cr, uid, line_val, context=context)
            account_voucher_obj.write(cr,uid,voucher.id,{'encaisse':True,'state_ordre':'remis'})
            
        ordre_virement_frs_obj.write(cr,uid,ordre_virement_frs_id,{'type':type_ordre})    
        mod_obj = self.pool.get('ir.model.data')    
        res = mod_obj.get_object_reference(cr, uid, 'devplus_account', 'ordre_virement_frs_form')
        res_id = res and res[1] or False,

        return {
            'name': _('Ordre de Virement'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': [res_id],
            'res_model': 'ordre.virement.frs',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'res_id': ordre_virement_frs_id  or False,
        }   

