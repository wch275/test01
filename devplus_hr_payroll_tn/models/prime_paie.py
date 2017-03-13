# -*- encoding: utf-8 -*-
from openerp.osv import fields, osv
from datetime import date, datetime
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _

class hr_prime(osv.osv):
    _name = 'hr.prime'
    _description=u"Gestion des primes" 
    
    def _get_company_id(self, cr, uid, data, context={}):
        if context is None:
            context = {}
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        company_id = context.get('company_id', user.company_id.id)
        return  company_id 
     
    def _get_month_id(self, cr, uid, context=None):
        """
        Return  default account period value
        """
        context = context or {}
        period_ids = self.pool.get('hr.month').find(cr, uid, context=context)
        return period_ids and period_ids[0] or False    

    def onchange_month_id(self, cr, uid, ids, month_id):
        result={}
        if  month_id:
            month = self.pool.get('hr.month').browse(cr, uid, month_id)
            result = {'value':{ 'period_id' : month.period_id.id }}
             
        return result
        
    _columns = {
                
        'name': fields.char("Description"),
        'prime_line_ids':fields.one2many('hr.prime.line','prime_id','Information'),
        'date': fields.date('Date'),
        'month_id': fields.many2one('hr.month', u'Mois'),
        'period_id': fields.many2one('account.period', u'Période Comptable'),
        'company_id': fields.many2one('res.company', u'Société',required=True),              
                 }
    
    _defaults = {  
                 'company_id': _get_company_id,
                 'month_id':_get_month_id,
                }

hr_prime()

class hr_prime_note(osv.osv):
    _name = 'hr.prime.note'
    _description=u"Gestion des primes" 
    
    _columns = {
        'classe':  fields.float("Classe",digits_compute=dp.get_precision('Montant Paie')), 
        'name':  fields.integer("Note"), 
             
                 }
hr_prime_note()

class hr_prime_line(osv.osv):
    _name = 'hr.prime.line'
    _description=u"Gestion des lines des primes"  

    def _sel_rubrique(self, cr, uid, context=None):
        obj = self.pool.get('hr.payroll.rubrique')
        ids = obj.search(cr, uid, [])
        res = obj.read(cr, uid, ids, ['name', 'id'], context)
        res = [(r['id'], r['name']) for r in res]
        return res    
    _columns = {
                
        'name': fields.char("Description"),
        'employee_id': fields.many2one('hr.employee', "Employee", select=True),
        'matricule': fields.char("Matricule", readonly=True),
        'montant': fields.float("Montant"),
        'rubrique_id' : fields.many2one('hr.payroll.rubrique', 'Rubrique', selection=_sel_rubrique, required=True),
        'prime_id': fields.many2one('hr.prime', 'Bordereau', select=True),       
                }
    def onchange_employee_id(self, cr, uid, ids, employee_id, context=None):
        employee=self.pool.get('hr.employee').browse(cr,uid,employee_id,context)
        res={'value':{'matricule':employee.matricule}}
        return res
hr_prime_line()

class hr_note_prime(osv.osv):
    _name = 'hr.note.prime'
    _description=u"Gestion des primes par note" 
    
    def _get_company_id(self, cr, uid, data, context={}):
        if context is None:
            context = {}
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        company_id = context.get('company_id', user.company_id.id)
        return  company_id 
     
    def _get_month_id(self, cr, uid, context=None):
        """
        Return  default account period value
        """
        context = context or {}
        period_ids = self.pool.get('hr.month').find(cr, uid, context=context)
        return period_ids and period_ids[0] or False    

    def onchange_month_id(self, cr, uid, ids, month_id):
        result={}
        if  month_id:
            month = self.pool.get('hr.month').browse(cr, uid, month_id)
            result = {'value':{ 'period_id' : month.period_id.id }}
             
        return result
        
    _columns = {
                
        'name': fields.char("Description"),
        'prime_line_ids':fields.one2many('hr.note.prime.line','prime_id','Information'),
        'date': fields.date('Date'),
        'month_id': fields.many2one('hr.month', u'Mois'),
        'period_id': fields.many2one('account.period', u'Période Comptable'),
                 }
    
    _defaults = {  
                 'month_id':_get_month_id,
                }

    def add_active_employees(self, cr, uid, ids, context={}):
        employee_obj = self.pool.get('hr.employee')
        this = self.browse(cr, uid, ids[0], context=context)  
        ids_employees = employee_obj.search(cr, uid, [('active', '=', True), ('contract_ids', '!=', False), ('date_entree', '<=', this.period_id.date_start), ('date_sortie', '=', False )])     
        # delete old pointage
        sql = '''   DELETE from hr_note_prime_line where prime_id = %s '''
        cr.execute(sql, (this.id,))
        # create new pointage
        all_prime = []
        for emp in employee_obj.browse(cr, uid, ids_employees) :
            val = (0, 0, {
                        'employee_id': emp.id,
                        'critere_1' : 0,
                        'critere_2' : 0,
                        'critere_3' : 0,
                        'critere_4' : 0,
                        'critere_5' : 0,
                        'total' : 0,
                        'montant_prime' : 0.0,
                        }
                    )
            all_prime.append(val)
             
        value = {  'prime_line_ids': all_prime }   
 
        self.write(cr, uid, this.id, value, context=context)       
        return True

hr_note_prime()

class hr_note_prime_line(osv.osv):
    _name = 'hr.note.prime.line'
    _description=u"Gestion des lines des primes"  

    def _action_count_note(self, cr, uid, ids, field_name, arg, context={}):
        result = []
        #total=[]
        val = 0
        for note in self.browse(cr,uid,ids, context):
            val = note.critere_1 + note.critere_2 + note.critere_3 +  note.critere_4 +  note.critere_5
            print '------------------note.id--------------------',note.id
            result[note.id]['total'] = val
        return result
     
    _columns = {
                
        'name': fields.char("Description"),
        'employee_id': fields.many2one('hr.employee', "Employee", select=True),
        'critere_1':fields.integer(u"Critére 1"),
        'critere_2': fields.integer(u"Critére 2"),
        'critere_3': fields.integer(u"Critére 3"),
        'critere_4': fields.integer(u"Critére 4"),
        'critere_5': fields.integer(u"Critére 5"),
        'total' : fields.integer("Total"),
        'montant_prime' : fields.float("Montant Prime"),
        #'total': fields.function(_action_count_note, type='integer', string=u'Total', multi = 'sum'),
        'prime_id': fields.many2one('hr.note.prime', 'Primes', select=True), 
                }

hr_note_prime_line()