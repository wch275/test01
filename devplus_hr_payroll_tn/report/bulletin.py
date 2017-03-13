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
from openerp.osv import osv


class bulletin(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(bulletin, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'total_text':self.total_text,
            'gross_wage_line' : self.gross_wage_line,
            'cotisation_line' : self.cotisation_line,
            'get_hs_line' : self.get_hs_line,
            'ir_line' :   self.ir_line,
            'redevance_line':self.redevance_line,
            'get_total' : self.get_total,
            'get_situation_faml' : self.get_situation_faml,
            'get_conge_all' :self.get_conge_all,
            'get_conge_pris':self.get_conge_pris,
            'get_conge_restant':self.get_conge_restant,
           'get_retenu_line':self.get_retenu_line
        })

    def total_text(self, montant):
            devis = 'Dinar'      
            return convertion.trad(montant, devis)
  
  
    def get_situation_faml(self, situation):
        situation_faml = ""
        if situation == 'm'   :
            situation_faml = u'Marié'
        elif  situation == 'c'   :  
            situation_faml = u'Célibataire'
        elif  situation == 'v'   :  
            situation_faml = u'Veuf(ve)'
        elif  situation == 'd'   :  
            situation_faml = u'Divorcé(e)'                        
        return   situation_faml     
    
    
    def get_conge_all(self, employee_id):
        employee_obj = self.pool.get('hr.employee')
        return   employee_obj._get_total_days_conge_paye_attribue(self.cr, self.uid, employee_id) 
    
    def get_conge_pris(self, employee_id):
        employee_obj = self.pool.get('hr.employee')
        return   employee_obj._get_total_days_conge_pris(self.cr, self.uid, employee_id) 
    
    def get_conge_restant(self, employee_id):
        employee_obj = self.pool.get('hr.employee')
        return   employee_obj._get_total_days_restante(self.cr, self.uid, employee_id) 
           
    def gross_wage_line(self, salary_line_ids) :
        listt = []
        for line in salary_line_ids :
            if line.type == 'brute' and line.afficher:
                dictt = {'name' : line.name,
                      'base' : line.base,
                      'taux' : float(line.taux),
                      'gain' :  round(line.gain, self.pool.get('decimal.precision').precision_get(self.cr, self.uid, 'Montant Paie')),
                      'retenu': line.retenu,
                      }
                listt.append(dictt)
        return listt
   
            
    def cotisation_line(self, salary_line_ids):    
        listt = []
        for line in salary_line_ids :
            if  line.afficher and line.type == 'cotisation' :
                dictt = {'name' : line.name,
                      'base' : line.base,
                      'taux' : line.taux,
                      'gain' : line.gain,
                      'retenu' : line.retenu,
                      'rate_employer' : line.rate_employer,
                      'subtotal_employer' : line.subtotal_employer,
                      } 
                listt.append(dictt)
        return listt
    
    def get_hs_line(self, salary_line_ids):    
        listt = []
        for line in salary_line_ids :
            if   line.afficher and line.type == 'hs' :
                dictt = {'name' : line.name,
                      'base' : line.base,
                      'taux' : line.taux,
                      'gain' : line.gain,
                      'rate_employer' : line.rate_employer,
                      'subtotal_employer' : line.subtotal_employer,
                      } 
                listt.append(dictt)
        return listt
    
    def get_retenu_line(self, salary_line_ids):    
        listt = []
        for line in salary_line_ids :
            if   line.afficher and line.type == 'retenu' :
                dictt = {'name' : line.name,
                        'base' : line.base,
                        'taux' : 1.0,
                        'gain' :  line.gain,
                       'retenu': round(line.retenu, self.pool.get('decimal.precision').precision_get(self.cr, self.uid, 'Montant Paie')),
                      } 
                listt.append(dictt)
        return listt
    
    
    def ir_line(self, salary_line_ids):    
        listt = []
        for line in salary_line_ids :
            if  line.afficher and line.type == 'ir' :
                dictt = {'name' : line.name,
                      'base' : line.base,
                      'taux' : '-',
                      'gain' : line.gain,
                      'retenu' : line.retenu,
                      'rate_employer' : '-',
                      'subtotal_employer' : line.subtotal_employer,
                      } 
                listt.append(dictt)
        return listt

    def redevance_line(self, salary_line_ids):    
        listt = []
        for line in salary_line_ids :
            if  line.afficher and line.type == 'redevance' :
                dictt = {'name' : line.name,
                      'base' : line.base,
                      'taux' : line.taux,
                      'gain' : line.gain,
                      'retenu' : line.retenu, 
                      } 
                listt.append(dictt)
        return listt
        
    def get_total(self, employee_id, fiscalyear_id):
        periods = self.pool.get('account.period').search(self.cr, self.uid, [('fiscalyear_id', '=', fiscalyear_id.id)])
        period_query_cond = str(tuple(periods))
        query = """
        SELECT sum(salaire_brute) AS salaire_brute, sum(salaire_brute_imposable) AS salaire_brute_imposable,
        sum(cotisations_employee) as cotisations_employee,sum(cotisations_employer) as cotisations_employer,
        sum(pointage) as pointage,sum(salaire_brute_imposable) as salaire_brute_imposable,sum(igr) as igr FROM hr_payroll_bulletin WHERE period_id IN %s and employee_id = %s
         """ % (str(period_query_cond), employee_id.id)
        self.cr.execute(query)
        data = self.cr.dictfetchall()
        return data
 

class report_bulletin(osv.AbstractModel):
    _name = 'report.devplus_hr_payroll_tn.bulletin_report'
    _inherit = 'report.abstract_report'
    _template = 'devplus_hr_payroll_tn.bulletin_report'
    _wrapped_report_class = bulletin
