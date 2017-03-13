# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
#
#    Copyright (C) 2014  .
#    Coded by: Borni DHIFI  (dhifi.borni@gmail.com)
#
#----------------------------------------------------------------------------

from openerp.report import report_sxw
import convertion
from openerp.osv import osv

class declaration_cnss_report(report_sxw.rml_parse):
    _name = 'report.declaration.cnss'
    
    def __init__(self, cr, uid, name, context):
        if context is None:
            context = {}
        super(declaration_cnss_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'get_page' : self.get_page,
            'get_nb_page':self.get_nb_page,
            'get_nb_employees' : self.get_nb_employees,
            'get_total' : self.get_total,
            'amount_to_text':self._amount_to_text,
        })

    def _amount_to_text(self, montant):
            devis = 'Dinar'      
            return convertion.trad(montant, devis)  
   
    def _get_lines(self, company_id,fiscalyear_id,trimester):
        period_ids=self.pool.get('account.period').search(self.cr,self.uid,[('fiscalyear_id','=',fiscalyear_id)])
        
        # if existe periode ouverture period_ids=13 else period_ids=12
        if period_ids==12 :
            if trimester =='1' : 
                mois1=period_ids[0]
                mois2=period_ids[1]
                mois3=period_ids[2]
            elif trimester =='2' : 
                mois1=period_ids[3]
                mois2=period_ids[4]
                mois3=period_ids[5]           
            elif trimester =='3' : 
                mois1=period_ids[6]
                mois2=period_ids[7]
                mois3=period_ids[8]             
            else : 
                mois1=period_ids[9]
                mois2=period_ids[10]
                mois3=period_ids[11]  
        else :
            if trimester =='1' : 
                mois1=period_ids[1]
                mois2=period_ids[2]
                mois3=period_ids[3]
            elif trimester =='2' : 
                mois1=period_ids[4]
                mois2=period_ids[5]
                mois3=period_ids[6]           
            elif trimester =='3' : 
                mois1=period_ids[7]
                mois2=period_ids[8]
                mois3=period_ids[9]             
            else : 
                mois1=period_ids[10]
                mois2=period_ids[11]
                mois3=period_ids[12]            
           
        
                
        sql = '''
               SELECT e.id ,e.matricule,e.cnss,SUBSTRING(r.name, 0, 60) as name,e.cin,
          
             ( select  b1.salaire_brute_cotisable  from hr_payroll_bulletin  b1 where
               b1.period_id = %s and b1.employee_id=e.id 
                ) as mois1,

    
             ( select  b2.salaire_brute_cotisable  from hr_payroll_bulletin  b2  where
               b2.period_id = %s and b2.employee_id=e.id 
                ) as mois2,

                    
             ( select  b3.salaire_brute_cotisable  from hr_payroll_bulletin  b3 where
               b3.period_id = %s and b3.employee_id=e.id
                ) as mois3 ,
                                
            (select  sum(b4.salaire_brute_cotisable)  from hr_payroll_bulletin  b4 where
               b4.period_id  in(%s,%s,%s)  and b4.employee_id=e.id ) as total

                           
            From  hr_employee e         
            LEFT JOIN resource_resource r on (r.id=e.resource_id)
             where (select count(*) from hr_contract hc where  hc.employee_id=e.id)>0
             ORDER BY e.matricule
            ''' % (mois1, mois2,mois3,  mois1, mois2, mois3)
        
        
        self.cr.execute(sql)
        declaration_cnss = self.cr.dictfetchall()
        
        num_page=1
        num_line=1
        resultats=[]
        sub_total = 0
        for declaration in declaration_cnss:
            if declaration['cnss'] and float(declaration['total'] or 0.0):
                declaration.update({'num_page':num_page,'num_line':num_line })
                
                if num_line == 12 :
                    num_page += 1
                    num_line =1
                else :
                    num_line += 1
                if num_line == 1:
                    sub_total +=float(declaration['total'] or 0.0)
                    declaration.update({'sub_tot':{'sub_total':sub_total, 'num_page':num_page}})
                    sub_total =0
                else :
                    sub_total +=float(declaration['total']or 0.0)  
                    declaration.update({'sub_tot':{'sub_total':0, 'num_page':num_page}})
                    
                declaration.update({'mois1':float(declaration['mois1'] or 0.0),'mois2':float(declaration['mois2'] or 0.0),'mois3':float(declaration['mois3'] or 0.0),'total':float(declaration['total'] or 0.0)})
                resultats.append(declaration)
        return resultats

    def get_page(self, company_id,fiscalyear_id,trimester,num_page):
        all_lines=self._get_lines(company_id,fiscalyear_id,trimester)
        res=[]
        for line_cnss in all_lines:
            if line_cnss['num_page'] == num_page :
                res.append(line_cnss)
        return res
  
       
    def get_nb_page(self, company_id,fiscalyear_id,trimester):
        all_lines=self._get_lines(company_id,fiscalyear_id,trimester)
        pages=[]
        for line in all_lines :
            if  pages.count(line['num_page']) ==0 :
                pages.append(line['num_page'])
        return pages

       
    def get_nb_employees(self, company_id,fiscalyear_id,trimester):
        all_lines=self._get_lines(company_id,fiscalyear_id,trimester)
        return len(all_lines)
        

    def get_total(self, company_id,fiscalyear_id,trimester):
        all_lines=self._get_lines(company_id,fiscalyear_id,trimester)
        total_mois1=total_mois2=total_mois3=salaire=sub_total=0.0
        for line in all_lines : 
                total_mois1+=float(line['mois1']or 0.0)
                total_mois2+=float(line['mois2'] or 0.0 )            
                total_mois3+=float(line['mois3'] or 0.0)
                salaire+=float(line['total'] or 0.0)
         
        params_obj= self.pool.get('hr.payroll.parametres')
        ids_params = params_obj.search(self.cr, self.uid, [('fiscalyear_id', '=', fiscalyear_id)])
        param = params_obj.read(self.cr, self.uid, ids_params[0])
        taux_accident_travail='taux_accident_travail' in param.keys() and param['taux_accident_travail']  or 0.5
        
        cots_obj= self.pool.get('hr.payroll.cotisation')
        ids_cots = cots_obj.search(self.cr, self.uid, [('code', '=', 'CNSS')])
        cortis = cots_obj.read(self.cr, self.uid, ids_cots[0])
        
        taux_cotisation='tauxTotal' in cortis.keys() and cortis['tauxTotal']  or 25.0
        taux_cnss=taux_cotisation
        montant_accident_travail= salaire * taux_accident_travail/100.0
        montant_cnss= salaire * taux_cnss/100.0
        montant_total =  montant_cnss+montant_accident_travail
    
        res = {
                'total_mois1' :total_mois1,
                'total_mois2' :total_mois2,
                'total_mois3' :total_mois3,
                'salaire' : salaire,
                'taux_cnss':taux_cnss,
                'taux_accident_travail':taux_accident_travail,
                'taux_cotisation':taux_cotisation,
                'total_taux' : taux_cnss+taux_accident_travail,
                'montant_cnss' :montant_cnss,
                'montant_accident_travail':montant_accident_travail,
                'montant_total' :montant_total,
                'montant_total_text':convertion.trad(montant_total,'Dinar')   
             }
       
        return res
 

class report_declaration_cnss(osv.AbstractModel):
    _name = 'report.devplus_hr_payroll_tn.report_declaration_cnss'
    _inherit = 'report.abstract_report'
    _template = 'devplus_hr_payroll_tn.report_declaration_cnss'
    _wrapped_report_class = declaration_cnss_report       

class report_recapitulatif_cnss(osv.AbstractModel):
    _name = 'report.devplus_hr_payroll_tn.report_recapitulatif_cnss'
    _inherit = 'report.abstract_report'
    _template = 'devplus_hr_payroll_tn.report_recapitulatif_cnss'
    _wrapped_report_class = declaration_cnss_report       
                             
