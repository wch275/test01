#----------------------------------------------------------------------------
#
#    Copyright (C) 2014  .
#    Coded by: Borni DHIFI  (dhifi.borni@gmail.com)
#
#----------------------------------------------------------------------------

from openerp.report import report_sxw
import time
import convertion
from openerp.osv import osv


class ordre_virement(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(ordre_virement, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'get_period'  : self.get_period,
            'get_city' : self.get_city,
            'get_net' : self.get_net,
            'get_total' : self.get_total,
            'get_bank' :self.get_bank,
            'total_text' : self.total_text,
            'get_bic' :self.get_bic,
            'get_bank_street' :self.get_bank_street,
        })
    
        
    def get_city(self, company_id):
        company_obj = self.pool.get('res.company')
        return company_obj.read(self.cr, self.uid, [company_id], ['city'])[0]['city']

    
    def get_period(self, period_id):
        period_obj = self.pool.get('account.period')
        period = period_obj.read(self.cr, self.uid, [period_id])[0]
        return period['name']



    def get_bic(self, bank_id,company_id):
        bank_ids=self.pool.get('res.company').browse(self.cr, self.uid,company_id).bank_ids
        numero_compte= ''
        if bank_ids :
            for bank in bank_ids :
                if  bank.bank.id == bank_id :
                    numero_compte = bank.acc_number
        return numero_compte	

    def get_bank(self, bank_id):
        banque = self.pool.get('res.bank')
        return banque.read(self.cr, self.uid, [bank_id], ['name'])[0]['name']


    def get_bank_street(self, bank_id):
        _banque = self.pool.get('res.bank')
        return _banque.read(self.cr, self.uid, [bank_id], ['street'])[0]['street']
 



    
    def total_text(self, montant):
            devis = 'Dinar'      
            return convertion.trad(montant, devis)

    def get_function(self, contract_id):
        contract = self.pool.get('hr.contract')
        c = contract.read(self.cr, self.uid, [contract_id])[0]
        function = self.pool.get('hr.job')
        f = function.read(self.cr, self.uid, [c['id']])[0]
        return f['name']

    def get_net(self, period_id):

        sql = '''
        SELECT e.name_related as name,e.matricule,e.res_bank_id,e.numero_compte,e.res_bank_id as bank,b.salaire_net_a_payer,b.employee_contract_id as contract
        FROM hr_payroll_bulletin b
        LEFT JOIN hr_contract c on (b.employee_contract_id=c.id)
        LEFT JOIN resource_resource r on (b.employee_id=r.id)
        LEFT JOIN hr_employee e on (e.id=r.id)
        WHERE 
        (b.period_id=%s and e.mode_reglement='virement')
        ''' % (period_id)
        self.cr.execute(sql)
        journal = self.cr.dictfetchall()
        return journal
    
    def get_total(self, period_id):
        salaire_net_a_payer = 0
        for b in self.get_net(period_id):
            salaire_net_a_payer += b['salaire_net_a_payer']
        return salaire_net_a_payer



class report_ordre_virement(osv.AbstractModel):
    _name = 'report.devplus_hr_payroll_tn.report_ordre_virement'
    _inherit = 'report.abstract_report'
    _template = 'devplus_hr_payroll_tn.report_ordre_virement'
    _wrapped_report_class =  ordre_virement      
             
       
               
