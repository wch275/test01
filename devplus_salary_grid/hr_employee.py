# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------------
#
#    Copyright (C) 2014  .
#    Coded by: Karim Rouag  
#
#----------------------------------------------------------------------------
from openerp.osv import osv, fields
from openerp.tools.translate import _

class hr_employee(osv.Model):
    _inherit= "hr.employee"
    _columns = {
                'categorie_id':fields.many2one('salary_grid.categorie', u'Catégorie', required=True), 
                'echlon_id':fields.many2one('salary_grid.echlon', 'Echlon', required=True),
                # for create auto contract
                'create_contract': fields.boolean(u'Créer un contrat?'),
                'contract_type_id':fields.many2one('hr.contract.type', 'Type de contrat', required=True),
                'regime' : fields.selection([('horaire', 'Horaire'),
                                                        ('journalier', u'Journalier'),
                                                         ('mensuel', u'Mensuel') ], u'Regime', required=True),
                
                }  
    
    def create(self, cr, uid, vals, context=None):
        new_employee=super(hr_employee, self).create(cr, uid, vals, context=context)
        employee=self.browse(cr,uid,new_employee,context)
        #create contrat
        if employee.create_contract :
            contract_obj = self.pool.get('hr.contract')
            contract={
                      'name': _('Contrat : ')+employee.name,
                      'employee_id' : employee.id,
                      'type_id' : employee.contract_type_id.id,
                      'regime_id' :employee.regime.id ,
                      }
            values=contract_obj.onchange_employee_id(cr,uid,[],employee.id,context)
            rubriques=[]
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
                    rubriques.append((0,False,ligne))
                    
            contract.update(values['value'])
            contract.update({'rubrique_ids':rubriques})
            
            contract_obj.create(cr,uid,contract,context)
        return new_employee    
    
        
