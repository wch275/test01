# -*- coding: utf-8 -*-

from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from datetime import datetime, timedelta

class res_holidays (osv.osv):
    _name = 'res.holidays' 
    _description = 'holidays' 
    _columns = {
              'name':fields.char("Nom jours fériés chômés et payés", required=True),
             'date_start':fields.date('Date Début'),
             'date_end':fields.date('Date Fin'),
             'nb_days':fields.integer('Nombre des jours', required=True),
             'period_id': fields.many2one('account.period', u'Période Comptable'),

                }
    def onchange_date(self, cr, uid,  ids, date_start, date_end ):
        result = {}
        if date_start and date_end:
            start_date=datetime.strptime(date_start, '%Y-%m-%d').date()
            end_date=datetime.strptime(date_end, '%Y-%m-%d').date()
            days = end_date.day - start_date.day + 1
            period_obj = self.pool.get('account.period')
            period_ids = period_obj.search(cr, uid, [('name','=',datetime(end_date.year,end_date.month,end_date.day,0,0).strftime('%m/%Y'))])
            period_id = period_obj.browse(cr, uid, period_ids).id
            result = {'value':{ 'nb_days' : days ,'period_id': period_id}}
        return result
    _sql_constraints = [
        ('date_check2', "CHECK (date_start <= date_end)", "La date de début doit être antérieure à la date de fin."),
    ]
res_holidays()

class res_holidays_resume(osv.osv):
      
    _name = 'res.holidays.resume' 
    _description = 'Resume holidays' 
       
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

    def onchange_holidays_id(self, cr, uid, ids, holidays_id):
        if  holidays_id:
            count=self.search_count(cr,uid,[('holidays_id','=',holidays_id)] )
            if count > 0 :
                warning = {'title':'Attention', 'message':_(u'Le résumé doit être unique par jour férié !')}
                value = {'holidays_id': False}
                return {'warning': warning, 'value': value}
        return True  
    
    _columns = {
                'name': fields.char('Description'),
                'date': fields.date('Date'),
                'month_id': fields.many2one('hr.month', u'Mois', required=True),
                'period_id': fields.many2one('account.period', u'Période Comptable', readonly=True),
                'company_id': fields.many2one('res.company', u'Société', change_default=True, readonly=True, required=True),
                'holidays_line_ids': fields.one2many('res.holidays.resume.line', 'holidays_resume_id', 'Lignes Holidays'),
                'holidays_id':fields.many2one('res.holidays',u'Jour férié'),
                }
    _defaults = {  
                 'company_id': _get_company_id,
                  'month_id':_get_month_id,
                  'date': fields.date.context_today
                }
        
    def onchange_month_id(self, cr, uid, ids, month_id, company_id):
        result={}
        if  month_id and  company_id:
            #TODO: you cannot test by month_id because user can put the month in two year 
            #must use month_id and period_id
            count=self.search_count(cr,uid,[('month_id','=',month_id),('company_id','=',company_id)] )
#             if count > 0 :
#                 warning = {'title':'Attention', 'message':_(u'Le pointage d\'une période doit être unique par société!')}
#                 value = {'period_id': False,'month_id':False}
#                 return {'warning': warning, 'value': value}
            company = self.pool.get('res.company').browse(cr, uid, company_id)
            month = self.pool.get('hr.month').browse(cr, uid, month_id)
            result = {'value':{ 'name' :   _(u'Résumé Jours fériés de %s du mois %s') % (company.name, month.name), 'period_id' : month.period_id.id }}
             
        return result
    

    def add_act_employees(self, cr, uid, ids, context={}):
        employee_obj = self.pool.get('hr.employee')
        holidays = self.browse(cr, uid, ids, context=context)
        month = self.pool.get('hr.month').browse(cr, uid, holidays.month_id.id)
        all_holidays = []
        ids_employees = employee_obj.search(cr, uid, [('active', '=', True), ('contract_ids', '!=', False), ('date_entree', '<=', month.period_id.date_start), ('date_sortie', '=', False )])
        # delete old pointage
        sql = '''   DELETE from res_holidays_resume_line where holidays_resume_id = %s '''
        cr.execute(sql, (holidays.id,))
#         value = {  'holidays_line_ids': {} }   
#         self.write(cr, uid, holidays.id, value, context=context)
        holidays_obj = self.pool.get('res.holidays')
        
        for emp in employee_obj.browse(cr, uid, ids_employees) :
            ids_holidays = holidays_obj.search(cr, uid, [('date_start', '>=', month.period_id.date_start), ('date_end', '<=', month.period_id.date_stop)])
            for holidays_days in holidays_obj.browse(cr, uid, ids_holidays) :
                val = (0, 0, {
                                    'employee_id': emp.id,
                                    'matricule': emp.matricule,
                                    'regime_id':emp.contract_id.regime_id.id,
                                    'date_start': holidays_days.date_start,
                                    'date_end': holidays_days.date_end,
                                    'nb_days_presence' : 0,
                                    'nb_hours_presence': 0,
                                    'nb_non_worked_hours' : 0,
                                    'holidays_id' : holidays_days.id,
                                    }
                            )
                all_holidays.append(val)
        month = self.pool.get('hr.month').browse(cr, uid, holidays.month_id.id)
        value = {  'holidays_line_ids': all_holidays ,'period_id' : month.period_id.id}   
        self.write(cr, uid, holidays.id, value, context=context)
        return True
        
res_holidays_resume()

class res_holidays_resume_line (osv.osv):
    _name = 'res.holidays.resume.line' 
    _columns = {
             'name':fields.char("Description"),
             'holidays_id':fields.many2one('res.holidays',"Jour Férié"),
             'holidays_resume_id':fields.many2one('res.holidays.resume',"Jour Férié"),
             'employee_id':fields.many2one('hr.employee',"Employée"),
             'regime_id':fields.many2one('hr.contract.regime',u"Régime"),
             'matricule': fields.char("Matricule", readonly=True),       
             'nb_days_presence':fields.integer(u'Nombre Jours travaillés', required=True),
             'nb_hours_presence':fields.integer(u'Nombre Heures travaillées', required=True),
               'nb_non_worked_hours':fields.integer(u'Nombre Heures non travaillées', required=True),
             'nb_days':fields.related('holidays_id', 'nb_days', type='integer', relation='res.holidays', string=u'Nombre Jours fériés', store=True),
                }
    
    _sql_constraints = [
        ('date_check', "CHECK ((nb_days_presence <= nb_days))", "Le nombre des jours fériés travaillés doit etre inférieure au nombre des jours fériés."),
    ]
    def onchange_employee_id(self, cr, uid, ids, employee_id, context=None):
        employee=self.pool.get('hr.employee').browse(cr,uid,employee_id,context)
        res={'value':{'matricule':employee.matricule}}
        return res
res_holidays_resume_line()