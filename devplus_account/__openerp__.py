# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------------
#
#    Copyright (C) 2014  .
#    Coded by: SmartProo
#
#----------------------------------------------------------------------------
{
    'name': u'Divers fonctionnalités : Comptabilité',
    'version': '8.0',
    'depends': ['account_voucher', 'account_payment'],
    'author': 'SmartProo',
    'category': 'DevPlus',
    'description': u'''
       
        * Grouper les lignes de facture ayant le même taxe lors de la génération des écritures comptable .
        * Ajouter precession décimal pour quelques champs .
        * Ajouter Date échéance, Propriétaire,Banque et mode de paiement dans l'interface du paiement
        * Bordreau de remise
        * Numéro de facture fournisseur unique par fournisseur.
        
        
    ''',
    'data': ['security/ir.model.access.csv',
             'data/data.xml',
             
             'wizard/account_payment_transfert_view.xml',
             'wizard/wizard_bordereau_remise_line.xml',
             'wizard/wizard_ordre_virement_frs_line.xml',
             'wizard/account_payment_transfert_virement_view.xml',
             

             
             'view/account_view.xml',
             'view/account_voucher.xml',
             'view/bordereau_remise_view.xml',
             
             'view/ordre_virement_frs_view.xml',

             
             
             'views/report_bordereau_remise.xml',
             
             'views/report_ordre_virement.xml',
             'views/report.xml'
             ],
    'installable': True,
    'active': False,

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
