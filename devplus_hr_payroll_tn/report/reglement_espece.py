# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
#
#    Copyright (C) 2014  .
#    Coded by: Borni DHIFI  (dhifi.borni@gmail.com)
#
#----------------------------------------------------------------------------

from openerp.report import report_sxw
import time
import convertion

class reglement_espece(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(reglement_espece, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'get_lines' : self.get_lines,
            'get_total' : self.get_total,
        })
    
    
    def total_text(self, montant):
            devis = 'Dinar'      
            return convertion.trad(montant, devis)

    def get_lines(self, hr_payroll_id):
        lines=[]
        hr_payroll_obj= self.pool.get('hr.payroll')
        for hr_payroll  in hr_payroll_obj.browse(self.cr,self.uid,[hr_payroll_id]) :
            for bulletin  in hr_payroll.bulletin_line_ids : 
                if bulletin.employee_id.mode_reglement!='virement':
                    line ={
                           'matricule' : bulletin.employee_id.matricule,
                           'name' : bulletin.employee_id.name,
                           'salaire_net_a_payer' : bulletin.salaire_net_a_payer
                           }
                    lines.append(line)
        return lines
    
    def get_total(self, hr_payroll_id):
        salaire_net_a_payer = 0 
        hr_payroll_obj= self.pool.get('hr.payroll')
        for hr_payroll  in hr_payroll_obj.browse(self.cr,self.uid,[hr_payroll_id]) :
            for bulletin  in hr_payroll.bulletin_line_ids :
                if bulletin.employee_id.mode_reglement!='virement':
                    salaire_net_a_payer += bulletin.salaire_net_a_payer
        return salaire_net_a_payer

report_sxw.report_sxw('report.regelements.espece', 'hr.payroll', 'devplus_hr_payroll_tn/report/regelements_espece.rml', reglement_espece)
       
       
               
