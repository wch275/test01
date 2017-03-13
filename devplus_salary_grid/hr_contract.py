# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------------
#
#    Copyright (C) 2014  .
#    Coded by: Karim Rouag  
#
#----------------------------------------------------------------------------
from openerp.osv import osv, fields
class hr_contract(osv.Model):
    _inherit= "hr.contract"
    def onchange_employee_id(self,cr,uid,ids,employee_id,context=None):
        res = super(hr_contract, self).onchange_employee_id(cr, uid, ids, employee_id,context=context)
        if employee_id :
            employee_obj=self.pool.get("hr.employee")
            employee=employee_obj.browse(cr,uid,employee_id,context)
            print 
            lignes=[]
            for  rubrique in employee.echlon_id.rubrique_ids :
                ligne={
                    'rubrique_id' :rubrique.rubrique_id.id,
                    'montant' : rubrique.montant,
                    'period_id': rubrique.period_id.id,
                    'permanent' : rubrique.permanent,
                    'date_start': rubrique.date_start,
                    'date_stop':rubrique.date_stop,
                    'note' : rubrique.note,
                    }
                lignes.append(ligne)
                
            res={ 'value':{'categorie_id':employee.categorie_id.id or False,
                           'echlon_id':employee.echlon_id.id or False,
						   'job_id':employee.job_id and employee.job_id.id or False,
                           #'wage':employee.echlon_id.salaire_base,
                           'salaire_de_base':employee.echlon_id.salaire_base,						   
                           'rubrique_ids' : lignes,
                             }}
        return res
            
    
    
    _columns = {
                'categorie_id':fields.many2one('salary_grid.categorie', 'Categorie', required=False,readonly=True ), 
                'echlon_id':fields.many2one('salary_grid.echlon', 'Echlon', required=False,readonly=True ),
                }
                