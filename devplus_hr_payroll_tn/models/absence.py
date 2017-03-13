# -*- encoding: utf-8 -*-
from openerp.osv import fields, osv
from datetime import date, datetime
import openerp.addons.decimal_precision as dp

class gestion_absence(osv.osv):
    _name='res.absence'
    _description='gestion des absences'
    _columns = {
        'name': fields.char('Description', size=64),
        'date_from': fields.date('Start Date', select=True, copy=False),
        'date_to': fields.date('End Date', copy=False), 
        'number_absent_hours':fields.integer("Nombre d'heures"), 
        'number_absent_days':fields.integer("Nombre de jours"), 
        'employee_id': fields.many2one('hr.employee', "Employee", select=True),
        'cause_absence': fields.many2one("res.absence.type",u"Type d'absence",required=True),
        'matricule':fields.related('employee_id', 'matricule', string='Matricule', type='char', relation='hr.employee', store=True),
        'department_id':fields.related('employee_id', 'department_id', string='Department', type='many2one', relation='hr.department', store=True),
        'regime': fields.char(u"Type Régime"), 
        } 
    def onchange_date_to(self, cr, uid, ids,date_to,date_from):
        if date_to and date_from:
            date_to_form = datetime.strptime(date_to, '%Y-%m-%d').date()
            date_from_form = datetime.strptime(date_from, '%Y-%m-%d').date()
            nb_days = date_to_form.day - date_from_form.day
            res={'value':{'number_absent_days': nb_days+1}}
            return res
        return True
    _sql_constraints = [
        ('date_check2', "CHECK (date_from <= date_to)", "La date de début doit être antérieure à la date de fin."),
    ]
    def onchange_employee(self, cr, uid, ids, employee_id):
        result = {'value': {'department_id': False}}
        if employee_id:
            employee = self.pool.get('hr.employee').browse(cr, uid, employee_id)
            regime=employee.contract_id.regime_id.type_regime
            result['value'] = {'department_id': employee.department_id.id,'matricule':employee.matricule,'regime': regime }
        return result      
    
gestion_absence()   
 
class res_absence_type(osv.osv):
    _name = 'res.absence.type'
    _description="Cause d'absence" 
    _columns = {
            'name':fields.char(u"Type d'absence"),
                }
res_absence_type()
