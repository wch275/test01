# -*- coding: utf-8 -*-

{
    'name': 'Rapports Ventes/Achats',
    'version': '1.0',
    'depends': ['web', 'account','purchase', 'account_voucher' ,'devplus_account','stock_valued_picking'],
    'author': 'SmartProo',
    'description':u'''
    - Rapport  Journal des ventes  . 
    - Rapport  Journal des paiements clients  . 
    - Rapport  Journal des achats  . 
    - Rapport  Journal des paiements fournisseurs  .    
    ''',
    'data': [
             'wizard/wizard_journal_vente_view.xml',
             'wizard/wizard_journal_achat_view.xml',
             'wizard/wizard_payment_clients.xml',
             'wizard/wizard_payment_fournisseurs.xml',
             
             'report/sale_document_view.xml',
             'report/purchase_document_view.xml',
             'report/sale_document_line_view.xml',
             'report/purchase_document_line_view.xml',
             
             'views/asset.xml',
             'views/report_journal_vente.xml',
             'views/report_journal_achat.xml',
             'views/report_journal_payment_clients.xml',
             'views/report_journal_payment_fournisseurs.xml',
             
             'views/report.xml'
            ],
    'demo_xml': [],
    'installable': True,
    'active': False,
}
