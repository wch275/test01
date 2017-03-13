# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
#
#    Copyright (C) 2014  .
#    Coded by: Borni DHIFI  (dhifi.borni@gmail.com)
#
#----------------------------------------------------------------------------
from openerp.osv import osv
from openerp.report import report_sxw
import time
import convertion



class certificat1(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(certificat1, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'bulletin_line':self._bulletin_line
        })

  
           
    def _bulletin_line(self, employee_id,fiscalyear_id) :
        bulletin_obj = self.pool.get('hr.payroll.bulletin')
#         bulletin_ids = bulletin_obj.search(self.cr, self.uid,
#                                            [('employee_id','=',employee_id),('period_id.fiscalyear_id','=',fiscalyear_id)],
#                                      
#                                            )
#         salaire_brute_imposable=0.0
#         total_salaire_brute_imposable=0.0
#         igr=0.0
#         salaire_net_a_payer=0.0
#         for line in bulletin_obj.browse(self.cr,self.uid,bulletin_ids) :
#             salaire_brute_imposable += line.salaire_brute_imposable
#             total_salaire_brute_imposable += line.salaire_brute_imposable
#             igr += line.igr
#             salaire_net_a_payer += line.salaire_net_a_payer
# 
#             
#         return {'salaire_brute_imposable' : salaire_brute_imposable,
#                 'total_salaire_brute_imposable' : salaire_brute_imposable,
#                 'igr' : igr,
#                 'salaire_net_a_payer' : salaire_net_a_payer,
#                        
#               }
    
    
    
   
            
   

class report_certificat1(osv.AbstractModel):
    _name = 'report.devplus_hr_payroll_tn.report_solde_decompte'
    _inherit = 'report.abstract_report'
    _template = 'devplus_hr_payroll_tn.report_solde_decompte'
    _wrapped_report_class = certificat1
