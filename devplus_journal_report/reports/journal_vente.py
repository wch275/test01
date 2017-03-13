# -*- coding: utf-8 -*-
from openerp.osv import osv, fields
from openerp import tools
from openerp.report import report_sxw
from openerp.addons.account.report.common_report_header import common_report_header

class journal_vente_report(report_sxw.rml_parse, common_report_header):
    _name = 'report.account.journal.sale'

    def __init__(self, cr, uid, name, context=None):
        super(journal_vente_report, self).__init__(cr, uid, name, context=context)
        self.res = []
        self.dict= {}
        self.taxes={}
        
        self.localcontext.update({
            'get_start_date':self.get_start_date,
            'get_end_date':self.get_end_date,
            'lines': self.lines,
            'lines_colonnes': self.lines_colonnes,
            'get_total':self.get_total,
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

    def lines(self, data,type):
        '''
        get lines for all invoice
        :param data:
        :param type:
        '''
        date_debut=data['date_begin']
        date_fin=data['date_end']
        invoice_obj = self.pool.get('account.invoice')
        requete="select  a.id, a.date_invoice, a.number, p.name,p.ref, a.amount_untaxed, a.amount_total, a.amount_tax , a.type,  a.ammount_timbre \
                from account_invoice a \
                left join res_partner p on a.partner_id=p.id \
                where   a.state != 'draft' \
                AND  a.type= '"+type+"'  \
                AND a.date_invoice>= '"+date_debut+"' \
                AND a.date_invoice <= '"+ date_fin +"' \
                order by a.date_invoice, a.number"
             
        self.cr.execute(requete)
        res = []
        for id, date_facture, number,  client,ref, amount_untaxed , amount_total, amount_tax, type ,ammount_timbre in self.cr.fetchall():
            reference=''
            if ref :
                reference=ref
            res.append({
                  'id':id,      
                  'date':date_facture,
                  'number': number or u'Facture Annulée',
                  'partner':'[' + reference + '] '+ client,
                  'amount_untaxed': amount_untaxed or 0.0,
                  'amount_total': amount_total or 0.0,
                  'amount_tax': amount_tax or 0.0,
                  'type':type,
                  'ammount_timbre': ammount_timbre,
                  })
    
         
        return res
  
    def colonnes_head(self):
        ''''
        Get list of taxes and base taxe
        create a new dict  'taxes' to calculate amount for each taxe
        ex: for tax 6% : {'6%':{'amount_invoice' : 0.0 ,'amount_refund' :0.0} , 'base6%':{'amount_invoice' : 0.0 ,'amount_refund' :0.0}
        @return:      dict  of all taxes name.     
        '''
        requete="""select distinct tax.name as name
                    from account_invoice_tax tax
                    left join account_invoice invoice on  invoice.id= tax.invoice_id
                    where invoice.type in ('out_invoice','out_refund')
                    order by name asc  """
        self.cr.execute(requete)
        res = [] 
        for name in self.cr.fetchall():
            self.taxes.update({name[0]:{'amount_invoice' : 0.0 ,'amount_refund' :0.0}})
            self.taxes.update({"base"+name[0]:{'amount_invoice' : 0.0 ,'amount_refund' :0.0}})
            
            res.append({  'name':name[0]}) 
        return res
  
    def lines_colonnes(self, colonne, type,id):
        '''
        Get amount base and amount tax  of tax 'colonne' for invoice 'id'
        
        :param colonne: name of tax
        :param type: type of invoice : out_invoice or out_refund
        :param id: id of invoice
        Update the dict taxes
        @return : dict with amount base and amount tax
        '''
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
            
            if type=='out_invoice':
                tax_val=self.taxes.get(colonne)['amount_invoice']+t[0][1]
                tax_base_val=self.taxes.get(base_col)['amount_invoice']+t[0][0]
                self.taxes[colonne]['amount_invoice'] =tax_val 
                self.taxes[base_col]['amount_invoice'] =tax_base_val 
            
            if type=='out_refund':
                tax_val=self.taxes.get(colonne)['amount_refund']+t[0][1]
                tax_base_val=self.taxes.get(base_col)['amount_refund']+t[0][0]
                self.taxes[colonne]['amount_refund'] =tax_val 
                self.taxes[base_col]['amount_refund'] =tax_base_val 
                                  
            res.append({
                      'base':t[0][0] or 0.0,
                      'taxe_amount': t[0][1] or 0.0,
                      })
        else:
            res.append({
                      'base': 0.0,
                      'taxe_amount':  0.0,
                      })
        return res

    def get_total(self, colonne):
        res=[]
        base_col="base"+colonne
        res.append({
                        'base':self.taxes.get(base_col)['amount_invoice'] - self.taxes.get(base_col)['amount_refund'] ,
                        'amount':self.taxes.get(colonne)['amount_invoice'] - self.taxes.get(base_col)['amount_refund'] ,
                        })
        return res
    
    


   

class report_journal_vente(osv.AbstractModel):
    _name = 'report.devplus_journal_report.report_journal_vente'
    _inherit = 'report.abstract_report'
    _template = 'devplus_journal_report.report_journal_vente'
    _wrapped_report_class = journal_vente_report

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

