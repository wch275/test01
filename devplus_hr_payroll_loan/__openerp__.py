# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
#
#    Copyright (C) 2014  .
#    Coded by: SmartProo
#
#----------------------------------------------------------------------------
{
    'name': u'Gestion des prêts ',
    'version' : '1.0',
    'author' : 'SmartProo',
    'website' : ' ',
    'category' : 'Payroll',
    'depends' : ['devplus_hr_payroll_tn','devplus_report_style'],
    'description': u'''
            Gestion des prêts
     ''',
    'init_xml' : [],
    'demo_xml' : [],
    'data' : [ 'security/ir.model.access.csv',
               'view/hr_payroll_loan.xml', 
               'wizard/wizard_pret_employee_view.xml',
               'views/report_payroll_loan.xml',
               'views/report_pret_employee.xml',
               'views/report.xml',
               'data/data.xml',
               
              ],
    'installable' : True,
    'active' : False,
}
