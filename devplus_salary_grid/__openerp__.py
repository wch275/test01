# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------------
#
#    Copyright (C) 2014  .
#    Coded by: Karim Rouag  
#
#----------------------------------------------------------------------------
{
    "name": "Grille de salaire",
    "version": "1.0",
    'author' : 'Smart Pro',
    "depends": ['devplus_hr_payroll_tn','hr'],
    "category": "Payroll",
    "description": """
        Grille de salaire
    """,
    "init_xml": [],
    'update_xml': [
                ],
    'data': [ 
             'security/ir.model.access.csv',
             'view/categorie_view.xml',
             'view/echlon_view.xml',
             'view/employee_view.xml',
              'view/avancement_view.xml',
              'view/contract_view.xml',
              
              'views/report_salary_grid.xml',
              'views/salary_grid_report.xml',
             ],
    'demo_xml': [],
    'installable': True,
    'active': False,

}
