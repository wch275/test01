# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
#
#    Copyright (C) 2014  .
#    TeamIT
#
#----------------------------------------------------------------------------
from openerp.osv import osv
from openerp.report import report_sxw


class journal_caisse_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(journal_caisse_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
        'get_caissiers':self._get_caissiers, 
        'get_mode_paiements' : self._get_mode_paiements,
        'get_paiements_for_journal' : self._get_paiements_for_journal,
        'get_total_paiements_for_journal' : self._get_total_paiements_for_journal,
        'get_somme_total_paiements' : self._get_somme_total_paiements,
         
        })
   
    def _get_caissiers(self,data,context=None):
        hr_employee_obj=self.pool.get('hr.employee')
        if data['user_id']  :
            employee=hr_employee_obj.browse(self.cr,self.uid,data['user_id'][0],context)
            return employee.user_id
        else :
            users=False
            search_ids=hr_employee_obj.search(self.cr,self.uid,[],context)
            if search_ids :
                users=[employee.user_id for employee in hr_employee_obj.browse(self.cr,self.uid,search_ids,context)]
            return users

    def _get_mode_paiements(self,date_debut,date_fin,context=None):
        all_modes= set()
        account_vouche_obj=self.pool.get('account.voucher')
        search_ids=account_vouche_obj.search(self.cr,self.uid,[('date','>=',date_debut),('date','<=',date_fin)],context)
        for voucher in account_vouche_obj.browse(self.cr,self.uid,search_ids,context) :
            all_modes.add(voucher.journal_id.id)
        all_modes = list(all_modes)    
        return self.pool.get('account.journal').browse(self.cr,self.uid,all_modes,context)
    
    def _get_paiements_for_journal(self,journal_id,date_debut,date_fin,context=None):
        account_vouche_obj=self.pool.get('account.voucher')
        search_ids=account_vouche_obj.search(self.cr,self.uid,[('journal_id','=',journal_id),('date','>=',date_debut),('date','<=',date_fin)],context)
        return self.pool.get('account.voucher').browse(self.cr,self.uid,search_ids,context)
    
    def _get_total_paiements_for_journal(self,journal_id,date_debut,date_fin,context=None):
        total=0.0
        for voucher in self._get_paiements_for_journal(journal_id, date_debut, date_fin, context) :
            total+= voucher.amount
        return total
    def _get_somme_total_paiements(self,date_debut,date_fin,context=None):
        somme=0.0
        for journal in self._get_mode_paiements (date_debut, date_fin, context) :
            somme+= self._get_total_paiements_for_journal(journal.id, date_debut, date_fin, context)
        return somme
                
class report_journal_caisse(osv.AbstractModel):
    _name = 'report.devplus_journal_report.journal_payment_clients_report'
    _inherit = 'report.abstract_report'
    _template = 'devplus_journal_report.journal_payment_clients_report'
    _wrapped_report_class = journal_caisse_report  