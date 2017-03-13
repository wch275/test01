# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
#
#    Coded by: Borni DHIFI  (dhifi.borni@gmail.com)
#
#-------------------------------------------------------------------------------

from openerp.osv import fields, osv
from openerp.tools.translate import _



class wizard_bordereau_remise_line(osv.osv_memory):
    _name = "wizard.bordereau_remise.line"

    _columns = { 
        'name': fields.char('Name'),
    }
      
    def action_delete(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        bordereau_remise_line_obj = self.pool.get('account.bordereau_remise.line')
        active_ids = context['active_ids']
        bordereau_remise_id=bordereau_remise_line_obj.browse(cr, uid, active_ids[0], context=context).bordereau_remise_id.id
        bordereau_remise_line_obj.action_delete( cr, uid, active_ids, context=context)
        #TODO: fix it bug: Uncaught Record not correctly loaded
        return {
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'account.bordereau_remise',
                    'type': 'ir.actions.act_window',
                    'res_id': bordereau_remise_id,
                    'context': context
                }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
