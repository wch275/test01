# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------------
#
#    Copyright (C) 2014  .
#    Coded by: Borni DHIFI  (dhifi.borni@gmail.com)
#
#----------------------------------------------------------------------------
from openerp.osv import osv, fields
import openerp.addons.decimal_precision as dp

#-------------------------------------------------------------------------------
# hr_payroll_parametres
#-------------------------------------------------------------------------------
class hr_payroll_parametres(osv.osv):
    _name = 'hr.payroll.parametres'
    _description = 'Parametres'
    _columns = {
            #'regime':fields.selection([
                   # ('40','40 H'),
                    #('48','48 H'),
                    # ],    u'Régime', select=True,required=True ),
            'smig' : fields.float('SMIG', digits_compute=dp.get_precision('Montant Paie')),
            'month_by_year' : fields.float(u'NB Mois/Année'),
            'fraispro' : fields.float(u'Frais Professionnels en %'),
            'fraispro_max': fields.float(u'Majoration Frais Professionnels'),
            'parent_charge' : fields.float(u' Taux parent(s) à charge', digits_compute=dp.get_precision('Montant Paie')),
            'chef_famille' : fields.float('Chef de famille', digits_compute=dp.get_precision('Montant Paie')),
            'enfant1' : fields.float(u'Enfant 1 ', digits_compute=dp.get_precision('Montant Paie')),
            'enfant2' : fields.float(u'Enfant 2 ', digits_compute=dp.get_precision('Montant Paie')),
            'enfant3' : fields.float(u'Enfant 3 ', digits_compute=dp.get_precision('Montant Paie')),
            'enfant4' : fields.float(u'Enfant 4 ', digits_compute=dp.get_precision('Montant Paie')),
            'enfant_etudiant' : fields.float(u'Enfant étudiant ', digits_compute=dp.get_precision('Montant Paie')),
            'enfant_handicape' : fields.float(u'Enfant handicapé ', digits_compute=dp.get_precision('Montant Paie')),
            'fiscalyear_id': fields.many2one('account.fiscalyear', u'Année fiscale', required=True),
            'droit_conge' : fields.float(u' Nombre de jours par mois  '),
            'auto_droit_conge' : fields.boolean(u'Affecter automatiquement droit des congés payés'),
            #redevance de compensation
            'redevance_taux' : fields.float('Taux',required=True),
            'redevance_from' : fields.float(u'Applicables à partir du',required=True, digits_compute=dp.get_precision('Montant Paie')),
            'redevance_max' : fields.float(u'Montant maximum',required=True, digits_compute=dp.get_precision('Montant Paie')),
            
            'month_ids':fields.one2many('hr.month','parametre_id',u'Paramétre'),
			'prime_fonction':fields.many2one('hr.payroll.rubrique',u'Prime de fonction'),
            
            'autorisation_delay':fields.float(u"Durée d'autorisation"),
            } 

    
hr_payroll_parametres()

 
#-------------------------------------------------------------------------------
# hr_ir
#-------------------------------------------------------------------------------
class hr_ir(osv.osv):
    _name = 'hr.payroll.ir'
    _description = 'IR'
    _columns = {
            'debuttranche' : fields.float(u'Début de tranche', digits_compute=dp.get_precision('Montant Paie')),
            'fintranche' : fields.float('Fin de tranche', digits_compute=dp.get_precision('Montant Paie')),
            'taux' : fields.float('Taux', digits_compute=dp.get_precision('Montant Paie')),
            'somme' : fields.float(u'Somme à deduire', digits_compute=dp.get_precision('Montant Paie'))
            }   
hr_ir()

#-------------------------------------------------------------------------------
# hr_cotisation
#-------------------------------------------------------------------------------
class hr_cotisation(osv.osv):
    _name = 'hr.payroll.cotisation'
    _description = 'les cotisations'
    _columns = {
            'code' : fields.char('Code', size=64, required=True),
            'name' : fields.char(u'Désignation', size=64, required=True),
            'tauxsalarial' : fields.float('Taux Salarial'),
            'tauxpatronal' : fields.float('Taux Patronal'),
            'tauxTotal' : fields.float("Taux Total"),
             }

    def on_change_taux(self, cr, uid, ids, tauxsalarial,tauxpatronal, context=None):
        res = {}
        tauxTotal=0
        if tauxsalarial and tauxpatronal :
            tauxTotal=tauxsalarial+tauxpatronal
        res['value']= {'tauxTotal':tauxTotal,}
        return  res  

hr_cotisation()

#-------------------------------------------------------------------------------
# hr_cotisation_type
#-------------------------------------------------------------------------------
class hr_cotisation_type(osv.osv):
    _name = 'hr.payroll.cotisation.type'
    _description = 'Les types de cotisation'
    _columns = {
            'code' : fields.char('Code', size=64),
            'name' : fields.char('Designation', required=1),
            'cotisation_ids' : fields.many2many('hr.payroll.cotisation', 'salary_cotisation', 'cotisation_id', 'cotisation_type_id', 'Cotisations'),
            }
hr_cotisation_type()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
