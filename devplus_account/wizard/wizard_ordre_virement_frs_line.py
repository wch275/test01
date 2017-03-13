# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
#
#    Coded by: Borni DHIFI  (dhifi.borni@gmail.com)
#
#-------------------------------------------------------------------------------

from openerp.osv import fields, osv
from openerp.tools.translate import _



class wizard_ordre_virement_frs_line(osv.osv_memory):
    _name = "wizard.ordre.virement.frs.line"

    _columns = { 
        'name': fields.char('Name'),
    }
      
    def action_delete(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        ordre_virement_frs_line_obj = self.pool.get('ordre.virement.frs.line')
        active_ids = context['active_ids']
        ordre_virement_frs_id=ordre_virement_frs_line_obj.browse(cr, uid, active_ids[0], context=context).ordre_virement_frs_id.id
        ordre_virement_frs_line_obj.action_delete( cr, uid, active_ids, context=context)
        #TODO: fix it bug: Uncaught Record not correctly loaded
        return {
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'ordre.virement.frs',
                    'type': 'ir.actions.act_window',
                    'res_id': ordre_virement_frs_id,
                    'context': context
                }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
