# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
#
#    Coded by: Borni DHIFI  (dhifi.borni@gmail.com)
#
#-------------------------------------------------------------------------------

from openerp.osv import osv, fields
import openerp.addons.decimal_precision as dp

#--------------------------------------------------------------------------------
# account_voucher
#--------------------------------------------------------------------------------
class account_voucher(osv.Model):
    _inherit= "account.voucher"

    #def _get_writeoff_amount(self, cr, uid, ids, name, args, context=None):
       # return super(account_voucher,self)._get_writeoff_amount(cr, uid, ids, name, args, context)
    
    def onchange_partner_id(self, cr, uid, ids, partner_id, journal_id, amount, currency_id, ttype, date, context=None):
        res=super(account_voucher,self).onchange_partner_id(cr, uid, ids, partner_id, journal_id, amount, currency_id, ttype, date)
#         nom=self.pool.get('res.partner').browse(cr,uid,partner_id).name
#         res['value'].update({'proprietaire':nom})
        return res
    
    def onchange_journal(self, cr, uid, ids, journal_id, line_ids, tax_id, partner_id, date, amount, ttype, company_id, context=None):
        res=super(account_voucher,self).onchange_journal(cr, uid, ids, journal_id, line_ids, tax_id, partner_id, date, amount, ttype, company_id)
        voucher=self.browse(cr,uid,ids)
        banks = self.pool.get('res.partner.bank').search(cr,uid,[('journal_id','!=',False)])
        for bank in self.pool.get('res.partner.bank').browse(cr,uid,banks):
            if bank.journal_id.id == journal_id:           
                res['value'].update({'bank_journal_id':bank.id})
        return res  
       
    def _paid_amount_in_company_currency(self, cr, uid, ids, name, args, context=None):
        return super(account_voucher,self)._paid_amount_in_company_currency(cr, uid, ids, name, args, context)
    
    _columns = {        
                'partner_id':fields.many2one('res.partner', 'Partner', change_default=1, readonly=True, states={'draft':[('readonly',False)]}),
                'date_echeance': fields.date(u'Date échéance',readonly=True,  states={'draft':[('readonly',False)]},),
                'bank_name':fields.many2one('res.bank', u'Banque',readonly=True,  states={'draft':[('readonly',False)]}, ), 
                'bank_journal_id':fields.many2one('res.partner.bank', u'Banque Journal' ), 
                'proprietaire':fields.char(u'Propriétaire',readonly=True,  states={'draft':[('readonly',False)]},), 
                'payment_mode_id':fields.many2one('account.payment.mode', 'Mode de paiement',required=True,readonly=True,  states={'draft':[('readonly',False)]},), 
                'encaisse':fields.boolean(u'Remis',copy=False), 
                'payment_type':fields.char(u'Type Payement'), 
                #ADD digits_compute
                #'writeoff_amount': fields.function(_get_writeoff_amount,digits_compute=dp.get_precision('Account'), string='Difference Amount', type='float', readonly=True, help="Computed as the difference between the amount stated in the voucher and the sum of allocation on the voucher lines."),
                'paid_amount_in_company_currency': fields.function(_paid_amount_in_company_currency,digits_compute=dp.get_precision('Account') ,string='Paid Amount in Company Currency', type='float', readonly=True),
                'state_bordereau':fields.selection(
                                            [('remis','Remis'),
                                             ('non_remis','Non Remis'), 
                                             ], 'Statut ', readonly=True, copy=False,),
                'state_ordre':fields.selection(
                                            [('remis','Remis'),
                                             ('non_remis','Non Remis'), 
                                             ], 'Statut ', readonly=True, copy=False,),                
                }
    
    _defaults = { 
                 
          'state_bordereau': 'non_remis',  
          'state_ordre': 'non_remis' 
          } 
    
    def action_remis(self, cr, uid, ids, context=None):
        self.write(cr,uid,ids[0],{'state': 'remis'},context)
        return True
    #TODO: IT
    #===========================================================================
    # def button_proforma_voucher(self, cr, uid, ids, context=None):
    #     context = context or {}
    #     wf_service = netsvc.LocalService("workflow")
    #     for vid in ids:
    #         wf_service.trg_validate(uid, 'account.voucher', vid, 'proforma_voucher', cr)
    #         #update date_echeance_paiement
    #         if context.get('invoice_id', False) :
    #             voucher=self.pool.get('account.voucher').browse(cr,uid,vid,context=context)
    #             invoice=self.pool.get('account.invoice').browse(cr,uid,context['invoice_id'],context=context)
    #             if voucher.date_rembourssement > invoice.date_echeance_paiement :
    #                 self.pool.get('account.invoice').write(cr,uid,invoice.id,{ 'date_echeance_paiement':voucher.date_rembourssement},context=context)
    #     return {'type': 'ir.actions.act_window_close'}
    #===========================================================================

    
    def onchange_payment_mode_id(self,cr,uid,ids,payment_mode_id,context=None):
        res={}
        if payment_mode_id:
            mode=self.pool.get('account.payment.mode').browse(cr,uid,payment_mode_id,context)
            if mode.journal_id:
                val={'journal_id': mode.journal_id.id ,'payment_type':mode.type }
                res.update({'value':val})
        return res
   
account_voucher()

 
#-------------------------------------------------------------------------------
# account_payment_mode
#-------------------------------------------------------------------------------
class account_payment_mode(osv.Model):
    _name = 'account.payment.mode' 
    _description = 'Type de paiement' 
    _columns = {
                'code':fields.char('Code',size=5), 
                'name':fields.char('Nom',required=True), 
                'journal_id':fields.many2one('account.journal',u'Journal par défaut'), 
                'type':fields.selection([
                    ('cash',u'Espéce'),
                    ('bank','Banque'),
                     ],    'Type', select=True, required=True),
                }

account_payment_mode() 