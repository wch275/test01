# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
#
#    Copyright (C) 2014  .
#    
#
#----------------------------------------------------------------------------

{
    'name': 'Gestion de la Paie Tunisienne',
    'version' : '8.0',
    'author' : 'Smart Pro',
    'website' : ' ',
    'category' : 'Payroll',
    'depends' : ['base', 'hr', 'hr_contract', 'hr_holidays', 'account','devplus_report_style'],
    'description': u'''
            Gestion de la Paie Tunisienne:
            Gestion des employés.
            Gestion des contrats.
            Configuration des differents paramètres (barème IR,cotisations CNSS,Autres cotisations ...)
            Configuration des rubriques de paie(primes,indemnités,avantages...).
            Pointage  et interfacage avec les pointeuse.
            Gestion des salaires(heures supplémentaire,cotisations salariales et patronales,IR...)
            Gestion des congés(Calcul automatique des congés non payés à partir du module hr_holidays)
            Comptabilisation de la paie(géneration d'une seule écritures comptable pour tout les employés chaque période)
            Reporting(Impression des bulletins de paie,journale de paie par période,Ordres de virement par période,déclaration...)
     ''',
    'data' : [
                'security/payroll_security.xml',
                'security/ir.model.access.csv',
#                'data/hr_payroll_tn_data.xml',
                'data/infraction_data.xml',
                'data/custom_paperformat.xml',
                 
                'view/hr_payroll_menuitem.xml',
                'view/hr_view.xml',
                'view/hr_payroll_config_view.xml',
                'view/hr_payroll_rubriques_view.xml',
                'view/hr_payroll_tn_view.xml',
                'view/hr_infraction.xml',
                'view/hr_autorisation_view.xml',
                'view/hr_avance_view.xml',
                'view/absence_view.xml',
                'view/holidays_view.xml',
                'view/hr_pointage.xml',
                'view/res_company.xml',
#                 'view/hr_employee.xml',
                'view/prime_paie.xml',
                'view/historique_irpp_paie_view.xml',
                
                
                'report/hr_payroll_tn_report.xml',
                 
	            'wizard/wizard_journal_paie_view.xml',
                'wizard/wizard_declaration_cnss.xml',
                'wizard/wizard_ordre_virement.xml',
                'wizard/wizard_certificat_impot.xml',
                 
                'views/payroll.xml',
                'views/report_bulletin.xml',
                'views/report_declaration_cnss.xml',
                'views/report_recapitulatif_cnss.xml',
                'views/report_journal_paie.xml',
                'views/report_ordre_virement.xml',
                'views/report_certificat_impot.xml',
                'views/report_autorisation.xml',
                'views/report_dde_conge.xml',
                'views/report_avance.xml',
                'views/report_hr_contact.xml',
                'views/report_attestation_travail.xml',
                'views/report_approbation_conge.xml',
                'views/report.xml',
                'views/report_saisie_paie.xml',
            
 
        ],
    'installable' : True,
    'active' : False,
}
