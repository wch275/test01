# -*- coding: utf-8 -*-
from openerp.osv import osv, fields
from openerp import tools
from openerp.report import report_sxw
from openerp.addons.account.report.common_report_header import common_report_header

class journal_achat_report(report_sxw.rml_parse, common_report_header):
    def __init__(self, cr, uid, name, context=None):
        super(journal_achat_report, self).__init__(cr, uid, name, context=context)
        self.res = []
        self.dict= {}
        self.localcontext.update({
            'get_start_date':self.get_start_date,
            'get_end_date':self.get_end_date,
            'lines': self.lines,
            'colonnes': self.colonnes,
            'lines_colonnes': self.lines_colonnes,
            'get_total':self.get_total,
            'amount_untaxed':self.amount_untaxed,
            'amount_total':self.amount_total,
            'amount_tax':self.amount_tax,
            'ammount_timbre':self.ammount_timbre,
            'colonnes_head':self.colonnes_head,
        })
        self.context = context
            
    def get_start_date(self, data):
        if data.get('form', False) and data['form'].get('date_begin', False):
            return data['form']['date_begin']
        return ''

    def get_end_date(self, data):
        if data.get('form', False) and data['form'].get('date_end', False):
            return data['form']['date_end']
        return ''

    def lines(self, data):
        date_debut=data['date_begin']
        date_fin=data['date_end']
        invoice_obj = self.pool.get('account.invoice')
        requete="select  a.id, a.date_invoice, a.number, p.name,p.ref, a.amount_untaxed, a.amount_total, a.amount_tax , a.ammount_timbre \
                from account_invoice a \
                left join res_partner p on a.partner_id=p.id \
                where   a.state != 'draft' \
                AND  (a.type= 'in_invoice' or a.type= 'in_refund' ) \
                AND a.date_invoice>= '"+date_debut+"' \
                AND a.date_invoice <= '"+ date_fin +"' \
                order by a.date_invoice, a.number"
             
        self.cr.execute(requete)
        res = []
        self.dict.update({'amount_untaxed':0})
        self.dict.update({'amount_total':0})
        self.dict.update({'amount_tax':0})
        self.dict.update({'ammount_timbre':0})
        for id, date_facture, number,  client,ref, amount_untaxed , amount_total, amount_tax ,ammount_timbre in self.cr.fetchall():
            #expedition=invoice_obj.browse(self.cr, self.uid, id, self.context).expedition or 0.0
            reference=''
            if ref :
                reference=ref
            res.append({
                  'id':id,      
                  'date':date_facture,
                  'number': number or u'Facture Annulée',
                  'partner':'[' + reference + '] '+ client,
                  'amount_untaxed':amount_untaxed or 0.0,
                  'amount_total': amount_total or 0.0,
                  'amount_tax': amount_tax or 0.0,
                  'ammount_timbre':ammount_timbre,
                  })
            amount_untaxed_temp=amount_untaxed or 0.0
            amount_total_temp=amount_total or 0.0
            amount_tax_temp=amount_tax or 0.0
            ammount_timbre_temp=ammount_timbre or 0.0
            
            self.dict['amount_untaxed']=self.dict.get('amount_untaxed',False)+amount_untaxed_temp
            self.dict['amount_total']=self.dict.get('amount_total',False)+amount_total_temp
            self.dict['amount_tax']=self.dict.get('amount_tax',False)+amount_tax_temp
            self.dict['ammount_timbre']=self.dict.get('ammount_timbre',False)+ammount_timbre_temp
         
        return res    
    
    def colonnes(self, data):
        requete="""select distinct tax.name as name
                    from account_invoice_tax tax
                    left join account_invoice invoice on  invoice.id= tax.invoice_id
                    where (invoice.type= 'in_invoice' or invoice.type= 'in_refund' )
                    order by name asc  """
        self.cr.execute(requete)
        res = []
        #res.append({'name': 'EXO - EXO'})
        for name in self.cr.fetchall():
            res.append({
                  'name':name[0],
                  })
        #res.append({'name': 'Timbre Fiscal'}) 
        return res
    
    def colonnes_head(self, data):
        requete="""select distinct tax.name as name
                    from account_invoice_tax tax
                    left join account_invoice invoice on  invoice.id= tax.invoice_id
                    where (invoice.type= 'in_invoice' or invoice.type= 'in_refund' )
                    order by name asc  """
        self.cr.execute(requete)
        res = []
        #res.append({'name': 'EXO - EXO'})
        #self.dict.update({'EXO - EXO':0})
        #self.dict.update({"baseEXO - EXO": 0})
        for name in self.cr.fetchall():
            self.dict.update({name[0]:0})
            self.dict.update({"base"+name[0]: 0})
                  
            res.append({
                  'name':name[0],
                  })
        #res.append({'name': 'Timbre Fiscal'})
        #self.dict.update({'Timbre Fiscal':0})
        #self.dict.update({"baseTimbre Fiscal": 0})
        return res
    
    def get_total(self, colonne):
        res=[]
        base_col="base"+colonne
        res.append({
                    'base':self.dict.get(base_col,False),
                    'amount':self.dict.get(colonne,False),
                    })
        return res
    
    def lines_colonnes(self, colonne, id):
        requete="select  at.base_amount, at.amount \
                from account_invoice_tax at \
                where at.invoice_id= %s AND at.name= %s"
        self.cr.execute(requete,(id, colonne))
        res = []
        base_col="base"+colonne
        t = self.cr.fetchall()
        if(t!=[]):
            self.dict[colonne]=self.dict.get(colonne,False)+t[0][1]
            self.dict["base"+colonne]=self.dict.get("base"+colonne,False)+t[0][0]
            #print("base"+colonne)
            #print(self.dict.get("base"+colonne,False))
            res.append({
                      'base':t[0][0] or 0.0,
                      'taxe_amount': t[0][1] or 0.0,
                      })
        else:
            res.append({
                      'base': 0.0,
                      'taxe_amount':  0.0,
                      })
        #print(self.dict.get(colonne,False))
        return res

    def amount_untaxed(self):
        return ({'amount_untaxed':self.dict.get('amount_untaxed',False)})
    
    def amount_total(self):
        return ({'amount_total':self.dict.get('amount_total',False)}) 

    def amount_tax(self):
        return ({'amount_tax':self.dict.get('amount_tax',False)}) 
    
    def ammount_timbre(self):
        return ({'ammount_timbre':self.dict.get('ammount_timbre',False)})         


   

class report_journal_achat(osv.AbstractModel):
    _name = 'report.devplus_journal_report.report_journal_achat'
    _inherit = 'report.abstract_report'
    _template = 'devplus_journal_report.report_journal_achat'
    _wrapped_report_class = journal_achat_report

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

