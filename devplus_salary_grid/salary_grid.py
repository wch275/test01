# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------------
#
#    Copyright (C) 2014  .
#    Coded by: Karim Rouag  
#
#----------------------------------------------------------------------------

from openerp.osv import fields, osv
from openerp.tools.translate import _
import time
import openerp.addons.decimal_precision as dp

#----------------------------------------------------------------------------
# salary_grid_echlon
#----------------------------------------------------------------------------
class salary_grid_echlon(osv.osv):
    _name = "salary_grid.echlon"
    _description = "Echlon"
    _order = 'sequence' 

    _columns = {
        'name' :fields.char(u'Libellé', required=True),
        'code':fields.char('Code'),
        'sequence':fields.integer(u'Séquence', size=64),
        'duree':fields.char(u'Durée', size=64),
        'salaire_base':fields.float('Salaire de base', digits_compute=dp.get_precision('Montant Paie')),
        'avancement':fields.boolean('Avancement automatique?'),
        'categorie_id':fields.many2one('salary_grid.categorie', u'Catégorie', required=True), 
        'rubrique_ids': fields.one2many('hr.payroll.ligne_rubrique', 'echlon_id', 'Les rubriques'),
         
         }

salary_grid_echlon()


#----------------------------------------------------------------------------
# salary_grid_categorie
#----------------------------------------------------------------------------
class salary_grid_categorie(osv.osv):
    _name = "salary_grid.categorie"
    _description = "Categorie"
    _order = 'sequence' 
    _columns = {
        'name' : fields.char('Nom', required=True),
        'code':fields.char('Code'),
        'description':fields.text('Description',),
        'categorie_ids':fields.one2many('salary_grid.echlon', 'categorie_id', u'Echlons',),
        'sequence':fields.integer(u'Séquence'),
         }
salary_grid_categorie()


#----------------------------------------------------------------------------
# salary_grid_categorie
#----------------------------------------------------------------------------
class salary_grid_avancement(osv.osv):
    _name = "salary_grid.avancement"
    _description = "Avancements"
        
    def action_validate(self,cr,uid,ids,context=None):
        data = self .browse(cr,uid,ids[0],context=context)
        contract_obj = self.pool.get('hr.contract')
        old_contrat= data.employee_id.contract_id
        if not old_contrat :
            raise osv.except_osv(_('Action non valide  !'),
                                 _(u"Veuillez saisir un contrat  pour cet employé !", ))  
        lignes=[]
        ligne=False
        for  rubrique in data.nouveau_echlon_id.rubrique_ids :
                    ligne={
                        'rubrique_id' :rubrique.rubrique_id.id,
                        'montant' : rubrique.montant,
                        'period_id': rubrique.period_id.id,
                        'permanent' : rubrique.permanent,
                        'date_start': rubrique.date_start,
                        'date_stop':rubrique.date_stop,
                        'note' : rubrique.note,
                        }
                    lignes.append((0,False,ligne))
        contrat_val={
                         'categorie_id' : data.nouveau_categorie_id.id ,
                         'echlon_id' : data.nouveau_echlon_id.id,
                         'rubrique_ids' :lignes,
                        'name' : old_contrat.name,
                        'job_id':old_contrat.job_id and  old_contrat.job_id.id,
                        'regime':old_contrat.regime,
                        'wage':data.nouveau_echlon_id.salaire_base,
                        'employee_id':old_contrat.employee_id.id,
                        'cotisation':old_contrat.cotisation.id,
                        'visa_no':old_contrat.visa_no,
                        'permit_no':old_contrat.permit_no,
                        'visa_expire':old_contrat.visa_expire,
                       }
        new_contratc_id=contract_obj.create(cr,uid,contrat_val,context)
        employee_obj = self.pool.get('hr.employee')
        update_val= { 'categorie_id' : data.nouveau_categorie_id.id ,
                     'echlon_id' : data.nouveau_echlon_id.id}
        employee_obj.write(cr,uid,[data.employee_id.id],update_val,context)
        self.write(cr,uid,data.id,{'state':'confirmed'})
        
        models_data = self.pool.get('ir.model.data')
        form_view = models_data.get_object_reference(cr, uid, 'devplus_hr_payroll_tn', 'view_order_form2')
        value = {
                 'domain': str([('id', '=', new_contratc_id)]),
                 'view_type': 'form',
                 'view_mode': 'form',
                 'res_model': 'hr.contract',
                 'view_id': False,
                 'views': [(form_view and form_view[1] or False, 'form')],
                 'type': 'ir.actions.act_window',
                 'res_id': new_contratc_id,
                 'target': 'current',
                 'nodestroy': True
             }
        return value
    
 
    def onchange_employee_id(self,cr,uid,ids,employee_id,context=None):
        res={ 'ancien_categorie_id': False,
              'ancien_echlon_id': False,
              'nouveau_categorie_id':False ,
              'nouveau_echlon_id' : False ,
            }
           
        if employee_id :
            employee_obj=self.pool.get("hr.employee")
            employee=employee_obj.browse(cr,uid,employee_id,context)
            if employee.categorie_id and employee.echlon_id :         
                echlon_obj = self.pool.get('salary_grid.echlon')
                cherche_seq_ids = echlon_obj.search(cr, uid,[('categorie_id','=',employee.categorie_id.id)])
                echlons = echlon_obj.read(cr,uid,cherche_seq_ids,['sequence'],context=context)
                all_seq_echlon=[]
                for echl in echlons :
                    all_seq_echlon.append(echl['sequence'])  
                sequence_max = max(all_seq_echlon)
                sequence_ech = employee.echlon_id.sequence
                new_echlon_id=new_categorie_id=False
                if sequence_ech < sequence_max:
                    index_next_sequence_eclon=all_seq_echlon.index(sequence_ech)+1
                    next_sequence_eclon=all_seq_echlon[index_next_sequence_eclon]
                    search_ids=echlon_obj.search(cr,uid,[('sequence','=',next_sequence_eclon)])            
                    new_echlon_id=search_ids[0]
                    new_categorie_id = employee.categorie_id.id 
                else :
                    categorie_obj = self.pool.get('salary_grid.categorie')
                    cherche_seq_cat_ids = categorie_obj.search(cr, uid,[])
                    categories = categorie_obj.read(cr,uid,cherche_seq_cat_ids,['sequence'],context=context)
                    all_seq_categorie=[]
                    for cat in categories :
                        all_seq_categorie.append(cat['sequence'])  
                        sequence_max_cat = max(all_seq_categorie)
                        sequence_cat = employee.categorie_id.sequence
                    if sequence_cat < sequence_max_cat:
                        index_next_sequence_cat=all_seq_categorie.index(sequence_cat)+1
                        next_sequence_cat=all_seq_categorie[index_next_sequence_cat]
                        search_cat_ids=categorie_obj.search(cr,uid,[('sequence','=',next_sequence_cat)]) 
                        if  search_cat_ids :          
                            new_categorie_id=search_cat_ids[0]
                        cherche_echlon_ids = echlon_obj.search(cr, uid,[('categorie_id','=',new_categorie_id)])
                        if cherche_echlon_ids:
                            new_echlon_id = cherche_echlon_ids[0]
                        
                res.update({ 'ancien_categorie_id':employee.categorie_id.id or False,
                        'ancien_echlon_id':employee.echlon_id.id or False,
                        'nouveau_categorie_id':new_categorie_id ,
                         'nouveau_echlon_id' : new_echlon_id ,
                        })
           
                    
        return {'value':res}
        
      
    _columns = {
               
                'employee_id':fields.many2one('hr.employee', u'Employé',required=True ),
                'ancien_categorie_id': fields.related('employee_id','categorie_id', type='many2one',
                                    relation='salary_grid.categorie',string=u'Ancienne catégorie',readonly=True), 
                'ancien_echlon_id': fields.related('employee_id','echlon_id', type='many2one', 
                                    relation='salary_grid.echlon', string=u'Ancien échlon',readonly=True), 
                 'date': fields.date('Date', readonly=True, states={'draft':[('readonly', False)]}, select=1),
                
                'description':fields.text('Description',),
                'active':fields.boolean("Active"),
                'nouveau_categorie_id':fields.many2one('salary_grid.categorie', u'Nouvelle catégorie',required=True  ),
                'nouveau_echlon_id':fields.many2one('salary_grid.echlon', u'Nouveau échlon',required=True ),
                
                'type' : fields.char('Type', size=64,),
                'state':fields.selection([('draft','Brouillon'),
                                          ('confirmed', u'Validée'),
                                           ], string="Etat",readonly=True),
               
         }
    _defaults = {
                 'date': lambda *a: time.strftime('%Y-%m-%d'),
                 
                'active':True,
                'state':'draft',
                }
salary_grid_avancement() 