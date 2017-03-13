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
       ('cheque',u'Chèque'),
       ('effet','Effet'),
        ]

TYPE_EFFET_SELECTION=[
       ('escompte','Escompte'),
       ('encaissement','Encaissement'),
        ]

class bordereau_remise(osv.Model):
    _name= "account.bordereau_remise"
    _inherit = ['mail.thread']
    _description = 'Bordereau remise' 
    _order = 'id desc' 

    def _total(self, cursor, user, ids, name, args, context=None):
        if not ids:
            return {}
        res = {}
        
        for bordereau in self.browse(cursor, user, ids, context=context):
            res[bordereau.id]={ 'total':0.0,'nb_cheque':0}
            total=0.0
            if bordereau.line_ids:
                total = reduce(lambda x, y: x + y.amount, bordereau.line_ids, 0.0)
            nb_cheque=len(bordereau.line_ids)
            res[bordereau.id]={ 'total':total,'nb_cheque':nb_cheque}
        return res
    
    _columns = {
                'name':fields.char(u'Reférence',readonly=True,), 
                'payment_mode_id':fields.many2one('payment.mode', 'Compte bancaire',required=True, readonly=True,  states={'draft':[('readonly',False)]}, ), 
                'date_created': fields.date(u'Date création'),
                'date_remise': fields.date(u'Date remise'),
                'type':fields.selection(TYPE_SELECTION, 'Type', readonly=True,  states={'draft':[('readonly',False)]}, ),
                'type_effet':fields.selection(TYPE_EFFET_SELECTION, 'Type Effet', readonly=True,  states={'draft':[('readonly',False)]}, ),
                'period_id': fields.many2one('account.period', u'Période', ),
                'total': fields.function(_total, string="Montant Total", type='float',multi="nb",digits_compute=dp.get_precision('Account')),
                'nb_cheque': fields.function(_total, string="Nombre Total", type='integer',multi="nb"),
                'user_id': fields.many2one('res.users', 'Responsable',  states={'done': [('readonly', True)]}),
                'company_id': fields.related('payment_mode_id', 'company_id', type='many2one', relation='res.company', string='Company', store=True, readonly=True),
                'line_ids': fields.one2many('account.bordereau_remise.line', 'bordereau_remise_id', 'Lines',readony=True),
                'state':fields.selection(STATE_SELECTION, 'Etat', select=True, readonly=True),
                'comment': fields.text('Note'),   
                'move_ids':fields.one2many('account.move', 'bordereau_remise_id', u'Pièces comptables',readonly=True),        
                }
    
    _defaults = {
        'user_id': lambda self,cr,uid,context: uid,
        'state': 'draft',
        'date_created': lambda *a: time.strftime('%Y-%m-%d'),
    }


    def onchange_date_remise(self, cr, uid, ids, date_remise, context=None):
        if context is None:
            context ={}
        res = {'value': {}}
        #set the period of the voucher
        period_pool = self.pool.get('account.period')
        ctx = context.copy()
        pids = period_pool.find(cr, uid, date_remise, context=ctx)
        if pids:
            res['value'].update({'period_id':pids[0]})
        return res
 

    def action_sent(self, cr, uid, ids, *args):
        ir_seq_obj = self.pool.get('ir.sequence')
        for order in self.read(cr, uid, ids, ['name','period_id']):
            if not order['name']:
                c = {}
                period= self.pool.get('account.period').browse(cr,uid,order['period_id'][0])
                c.update({'fiscalyear_id': period.fiscalyear_id.id ,'fiscalperiod_id': period.id})
                name = ir_seq_obj.get(cr, uid, 'account.bordereau_remise',context=c)
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
                raise osv.except_osv(_('Action Invalide!'), _(u'Vous ne pouvez pas supprimer  bordereau(s) qui sont déjà remis ou comptabilisé.'))
        return super(bordereau_remise, self).unlink(cr, uid, ids, context=context)
   

    def create_move(self, cr, uid, ids, context=None):
        context = dict(context or {})
        account_move_obj = self.pool.get('account.move')
        account_move_line_obj = self.pool.get('account.move.line')
        
        bordereau = self.browse(cr, uid, ids[0], context=context)
        
        #active_ids = context.get('active_ids', [])
        
        for line in bordereau.line_ids:
            #create new account move
            name=str('Bordereau n° ')+str(bordereau.name)
            move_vals = {
                    'ref':name,
                    'journal_id': bordereau.payment_mode_id.journal.id,
                    'date': bordereau.date_remise,
                    'period_id':bordereau.period_id.id,
                    'company_id': bordereau.company_id.id,
                    'bordereau_remise_id':bordereau.id
                    }
            move_id = account_move_obj.create(cr, uid, move_vals, context=context)
        
            #search move line inverse
            account_ids=[]
            if line.account_voucher_id.journal_id.default_debit_account_id :
                account_ids.append(line.account_voucher_id.journal_id.default_debit_account_id.id)
            if line.account_voucher_id.journal_id.default_credit_account_id :
                account_ids.append(line.account_voucher_id.journal_id.default_credit_account_id.id)
            serach_ids=account_move_line_obj.search(cr,uid,[('move_id','=',line.account_voucher_id.move_id.id),('account_id','in',account_ids)],context=context)
            move_line=account_move_line_obj.browse(cr, uid, serach_ids[0], context=context)
            
            #create first line
            if move_line.debit == 0.0 :
                account_id=line.account_voucher_id.journal_id.default_debit_account_id.id
                account_id_2=bordereau.payment_mode_id.journal.default_credit_account_id.id
            else :
                account_id=line.account_voucher_id.journal_id.default_credit_account_id.id
                account_id_2=bordereau.payment_mode_id.journal.default_debit_account_id.id  
            
            account_move_line1={
                        'partner_id': move_line.partner_id and move_line.partner_id.id or False,
                        'name': name,
                        'date':  bordereau.date_remise,
                        'debit':move_line.credit,
                        'credit': move_line.debit,
                        'account_id':  account_id,
                        'ref': move_line.name,
                        'move_id':move_id,
                        }
            move_line_1_id = account_move_line_obj.create(cr, uid, account_move_line1, context=context)
            # second line
            account_move_line2={
                        'partner_id': move_line.partner_id and move_line.partner_id.id or False,
                        'name': name,
                        'date': bordereau.date_remise,
                        'debit':move_line.debit,
                        'credit': move_line.credit,
                        'account_id':  account_id_2,
                        'ref': move_line.name,
                        'move_id':move_id,
                        }            
            move_line_2_id = account_move_line_obj.create(cr, uid, account_move_line2, context=context)
            #post move
            move=account_move_obj.browse(cr, uid, move_id, context=context)
            move.post()
            #move_ids.append(move_id)
            #reconcile
            account_move_line_obj.reconcile(cr, uid, [move_line.id,move_line_1_id], context=context)
            
        return True
                
bordereau_remise()
#-------------------------------------------------------------------------------
# bordereau_remise_line
#-------------------------------------------------------------------------------
class bordereau_remise_line(osv.Model):
    _name= "account.bordereau_remise.line"
    _description = 'Bordereau remise Lines' 
    _columns = {
                'numero_cheque':fields.char(u'Numéro',), 
                'bank_name':fields.char(u'Banque',), 
                'proprietaire':fields.char(u'Nom de tireur',), 
                'amount':fields.float(u'Montant', digits_compute=dp.get_precision('Account')), 
                'bordereau_remise_id': fields.many2one('account.bordereau_remise', 'Order', required=True, ondelete='cascade', select=True),
                'account_voucher_id': fields.many2one('account.voucher', 'Paiement', ondelete='cascade'),
                'state': fields.related('bordereau_remise_id','state', type='selection', selection=STATE_SELECTION, string='State'), 
                }
    
    def action_delete(self, cr, uid, ids, context=None):
        context = context or {}
        voucher_obj = self.pool.get('account.voucher')
        for line in self.browse(cr, uid, ids, context=context):
            if line.bordereau_remise_id.state == 'draft':
                voucher_obj.write(cr,uid,line.account_voucher_id.id,{'encaisse':False,
                                                                     'state_bordereau' : 'non_remis'})
                self.unlink(cr,uid,line.id)
        return True

bordereau_remise_line()

#-------------------------------------------------------------------------------
# account_move
#-------------------------------------------------------------------------------
class account_move(osv.Model):
    _inherit= "account.move"
    _columns = {
              'bordereau_remise_id': fields.many2one('account.bordereau_remise', 'Bordereau de remise',ondelete='cascade'),
             }