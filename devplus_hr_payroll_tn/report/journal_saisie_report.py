# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
#
#    Copyright (C) 2014  .
#    Coded by: Borni DHIFI  (dhifi.borni@gmail.com)
#
#----------------------------------------------------------------------------

from openerp.report import report_sxw
import time
from openerp.osv import osv

class journal_saisie_report(report_sxw.rml_parse):
    _name = 'hr.payroll'
    
    def __init__(self, cr, uid, name, context):
        super(journal_saisie_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            #'get_journal' : self.get_journal,
            'get_total' : self.get_total,		
        })
        
    def get_total(self, month_id):

        salaire_base = 0
        salaire_brute = 0
        salaire_brute_imposable = 0
        salaire_net_a_payer = 0
        cotisations_employee = 0
        cotisations_employer = 0
        igr = 0
        salaire_net = 0
        prime = 0
        indemnite = 0
        avantage = 0
        exoneration = 0
        deduction = 0
        normal_hours = 0
        prime_anciennete = 0
        working_unite = 0
        frais_pro = 0
        personnes = 0
        absence = 0
        bulletins = self.pool.get('hr.payroll.bulletin')
        # bulletins_ids=bulletins.search(self.cr,self.uid,[('period_id','=',int(period_id))])
        bulletins_ids = bulletins.search(self.cr, self.uid, [('month_id', '=', month_id)])
        liste = bulletins.read(self.cr, self.uid, bulletins_ids, [])
        for b in liste:
            salaire_base += b['salaire_base']
            salaire_brute += b['salaire_brute']
            salaire_brute_imposable += b['salaire_brute_imposable']
            salaire_net_a_payer += b['salaire_net_a_payer']
            cotisations_employee += b['cotisations_employee']
            cotisations_employer += b['cotisations_employer']
            salaire_net += b['salaire_net']
            
            igr += b['igr']
            prime += b['prime']
            indemnite += b['indemnite']
            avantage += b['avantage']
            exoneration += b['exoneration']
            deduction += b['deduction']
            normal_hours += 0  # b['normal_hours']
            prime_anciennete += 0  # b['prime_anciennete']
            working_unite += 0  # b['working_unite']
            frais_pro += b['frais_pro']
            personnes += 0  # b['personnes']
            absence += 0  # b['absence']
            
        liste = []
        total_line = {
            'salaire_base':salaire_base,
            'salaire_brute':salaire_brute,
            'salaire_brute_imposable':salaire_brute_imposable,
            'salaire_net_a_payer':salaire_net_a_payer,
            'cotisations_employee':cotisations_employee,
            'cotisations_employer':cotisations_employer,
            'salaire_net' : salaire_net,
            'igr':igr,
            'prime':prime,
            'indemnite':indemnite,
            'avantage':avantage,
            'exoneration':exoneration,
            'deduction':deduction,
            'normal_hours':normal_hours,
            'prime_anciennete':prime_anciennete,
            'working_unite':working_unite,
            'frais_pro':frais_pro,
            'personnes':personnes,
            'absence':absence,
            }
        liste.append(total_line)
        return liste
    
class report_saisie_paie(osv.AbstractModel):
    _name = 'report.devplus_hr_payroll_tn.report_saisie_paie'
    _inherit = 'report.abstract_report'
    _template = 'devplus_hr_payroll_tn.report_saisie_paie'
    _wrapped_report_class = journal_saisie_report     
       
               
