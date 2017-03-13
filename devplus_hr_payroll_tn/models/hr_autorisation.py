# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
#
#    Coded by: Amira
#
#-------------------------------------------------------------------------------


from openerp.osv import osv, fields



#-------------------------------------------------------------------------------
# hr_autorisation
#-------------------------------------------------------------------------------
class hr_autorisation(osv.Model):
    _name = "hr.autorisation"
    
    #TODO : with autorisation_delay
    def on_change_date(self, cr, uid, ids, heure_start,duree_prevu,heure_stop, context=None):
        res = {}
        if duree_prevu >= 0 and heure_start and heure_stop and  heure_start<heure_stop :
            duree_actuel=heure_stop-heure_start
            duree_obj=self.pool.get('hr.payroll.parametres')
            duree_search_ids=duree_obj.search(cr,uid,[('name','!=',0)])
            duree_line=duree_obj.browse(cr,uid,duree_search_ids)
            duree_sauv=duree_line.name
            if duree_sauv >= duree_actuel :
                res['value']= {'duree_prevu':duree_actuel,}
                return  res
            elif duree_sauv < duree_actuel :
                res_warning={'title': 'INFO' , 'message':"vous avez dépassé la durée autorisé de sortie" }
                return {'warning': res_warning  }
    
    _columns = {
                
                'date': fields.date('Date',required=True),
                'name': fields.char(u'Numéro'),
                'employee_id': fields.many2one('hr.employee',u'Employé',required=True ),
                'heure_start': fields.float('Heure de sortie',readonly=True, states={'new':[('readonly', False)]}),
                'heure_stop': fields.float('Heure de retour',readonly=True, states={'new':[('readonly', False)]}),
                'duree_prevu':fields.float(u'Durée',readonly=True, states={'new':[('readonly', False)]}),
                'description': fields.text('Description',required=True ,readonly=True, states={'new':[('readonly', False)]}),
                'state':fields.selection([('new','Brouillon'), ('done','Validé'),], 'Etat'),
                'raison_autorisation':fields.selection([('affaire_personnel','Affaire personnel'), ('mission_travail','Mission de Travail'),], "Raison de l'autorisation"),
                }
    _defaults = {
                 'date': fields.date.context_today,
                 'state':  'new',
                 }
    
    def action_terminer(self, cr, uid, ids, context=None):
        self.write(cr,uid,ids[0],{'state': 'done'},context)
        return True

    
    def create(self, cr, uid, vals, context=None):
        if not vals.get('name', False):
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'hr.autorisation', context=context) or '/'
        return super(hr_autorisation, self).create(cr, uid, vals, context=context)

hr_autorisation()   