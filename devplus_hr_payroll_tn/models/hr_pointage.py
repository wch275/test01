# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
#
#    Copyright (C) 2014  .
#    Coded by: Borni DHIFI  (dhifi.borni@gmail.com)
#
#----------------------------------------------------------------------------

from openerp.osv import fields, osv
from openerp.tools.translate import _
import time
import openerp.addons.decimal_precision as dp
 

class hr_pointage(osv.osv):
    
    STATES = [
              ('draft', 'Brouillon'),
              ('confirmed', u'Validé'),
            ]
      
    _name = 'hr.pointage' 
    _inherit = ['mail.thread']
    _description = 'Saisie du pointage' 
       
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
    
    _columns = {
                'name': fields.char('Description', size=64, readonly=True, states={'draft':[('readonly', False)]},),
                'date': fields.date('Date Pointage', readonly=True, states={'draft':[('readonly', False)]}, select=1),
                'month_id': fields.many2one('hr.month', u'Mois', readonly=True, required=True, states={'draft':[('readonly', False)]}, select=1),
                'period_id': fields.many2one('account.period', u'Période Comptable', readonly=True, required=True, states={'draft':[('readonly', False)]}, select=1),
                'company_id': fields.many2one('res.company', u'Société', change_default=True, readonly=True, required=True, states={'draft':[('readonly', False)]}),
                'pointage_line_ids': fields.one2many('hr.pointage.line', 'pointage_id', 'Lignes Pointages', readonly=True, states={'draft':[('readonly', False)]}),
                'note': fields.text('Notes'),
                'state': fields.selection(STATES, 'Etat', select=True, readonly=True, track_visibility='onchange',),
                }
    _defaults = {  
                 'date': lambda *a: time.strftime('%Y-%m-%d'),
                 'state':'draft',
                 'company_id': _get_company_id,
                  'month_id':_get_month_id
                }
        
    def onchange_month_id(self, cr, uid, ids, month_id, company_id):
        result={}
        if  month_id and  company_id:
            #TODO: you cannot test by month_id because user can put the month in two year 
            #must use month_id and period_id
            count=self.search_count(cr,uid,[('month_id','=',month_id),('company_id','=',company_id)] )
            if count > 0 :
                warning = {'title':'Attention', 'message':_(u'Le pointage d\'une période doit être unique par société!')}
                value = {'period_id': False,'month_id':False}
                return {'warning': warning, 'value': value}
            company = self.pool.get('res.company').browse(cr, uid, company_id)
            month = self.pool.get('hr.month').browse(cr, uid, month_id)
            result = {'value':{ 'name' :   _(u'Pointage %s du mois %s') % (company.name, month.name), 'period_id' : month.period_id.id }}
        return result
    
    
    def action_confirm(self, cr, uid, ids, *args):
        '''
        validate pointage
        @return: True
        '''
        self.write(cr, uid, ids, {'state': 'confirmed'})
        return True
    
    def action_draft(self, cr, uid, ids, *args):
        '''
        cancelled to draft
        @return: True
        '''
        self.write(cr, uid, ids, {'state': 'draft'})
        return True
    
    def add_active_employees(self, cr, uid, ids, context={}):
        employee_obj = self.pool.get('hr.employee')
        pointage = self.browse(cr, uid, ids[0], context=context)  
        ids_employees = employee_obj.search(cr, uid, [('active', '=', True), ('contract_ids', '!=', False), ('date_entree', '<=', pointage.date), ('date_sortie', '=', False )])     
        # delete old pointage
        sql = '''   DELETE from hr_pointage_line where pointage_id = %s '''
        cr.execute(sql, (pointage.id,))
        # create new pointage
        all_pointage = []
        for emp in employee_obj.browse(cr, uid, ids_employees) :
            nb_pointage=22
            regime=emp.contract_id.regime_id
            if regime.type_regime=='horaire':
                nb_pointage=regime.hours_horaire *regime.hours_horaire
            if regime.type_regime=='mensuel':
                if regime.hours_mensuel == '48':
                    nb_pointage=26
            # get nb conge paye
            nb_days_holiday = employee_obj._get_nb_days_cp_by_period(cr, uid, emp.id, pointage.period_id.id, context=context)
            # get nb conge impaye
            nb_days_holiday_impaye = employee_obj._get_nb_days_c_impaye_by_period(cr, uid, emp.id, pointage.period_id.id, context=context)
            # get nb férié payé double
            nb_days_holiday_payed_200 = self._get_nb_days_ferie_200(cr, uid, emp.id, pointage.period_id.id, context=context)            
            #get nb total holidays
            nb_days_holiday_payed_100 = self._get_nb_days_ferie_100(cr, uid, emp.id, pointage.period_id.id, context=context) 
            #get nombre absence
            nb_days_absence = self._get_nb_days_absent(cr, uid, emp.id, pointage.period_id.id, context=context)  
            # get nb férié
            #nb_holiday = employee_obj._get_nb_days_ferie_non_payed(cr, uid, pointage.period_id.id, context=context)              
            if regime.type_regime=='horaire':
                nb_days_holiday=nb_days_holiday*regime.hours_horaire_day
                nb_days_holiday_payed_100 = nb_days_holiday_payed_100*regime.hours_horaire_day
                nb_days_absence = self._get_nb_hours_absent(cr, uid, emp.id, pointage.period_id.id)
                nb_pointage= regime.hours_horaire_mensuel
                nb_days_holiday_payed_200 = self._get_nb_days_hours_ferie_200(cr, uid, regime.hours_holidays, emp.id, pointage.period_id.id)
            val = (0, 0, {'nb_pointage':nb_pointage - nb_days_holiday - nb_days_holiday_impaye - nb_days_absence - nb_days_holiday_payed_100 ,
                        'employee_id': emp.id,
                        'nb_days_holiday' : nb_days_holiday,
                        'jour_supplementaire_worked' : nb_days_holiday_payed_200,
                        'jour_supplementaire' : nb_days_holiday_payed_100 - nb_days_holiday_payed_200,
                        'absence':nb_days_absence,
                        }
                    )
            all_pointage.append(val)
             
        value = {  'pointage_line_ids': all_pointage }   
 
        self.write(cr, uid, pointage.id, value, context=context)       
        return True
    def _get_nb_days_hours_ferie_200(self, cr, uid, hours_day, employee_id, period_id, context=None):
        # get nb jour férié travaillé payé double par periode,
        cr.execute("""SELECT 
                h.id,
                h.employee_id,
                h.nb_hours_presence,
                h.nb_days_presence
            from
                res_holidays_resume_line h
                JOIN  res_holidays_resume a
                ON a.id = h.holidays_resume_id
            where
                h.employee_id = %s and 
                a.period_id  =    '%s' 
             """ % (employee_id, period_id))
        res = cr.dictfetchall()
        days = 0
        for r in res :
            days= days+( (r['nb_days_presence'] or 0)*hours_day)+(r['nb_hours_presence'] or 0)
        return days    
    def _get_nb_days_absent(self, cr, uid, employee_id, period_id, context=None):
        period_obj = self.pool.get('account.period')
        period = period_obj.browse(cr, uid, period_id, context=context)
        date_start = period.date_start
        date_stop = period.date_stop
        # get nb jour absence par periodde,
        cr.execute("""SELECT 
                ab.number_absent_days,
                ab.employee_id
            from
                res_absence ab
            where
                ab.employee_id = %s and 
                ab.date_from  >=    '%s' and 
                ab.date_to  <=    '%s' 
             """ % (employee_id, date_start, date_stop))
        res = cr.dictfetchall()
        days = 0
        for r in res :
            days= days+ (r['number_absent_days'] or 0)
        return days 
    
    def _get_nb_hours_absent(self, cr, uid, employee_id, period_id, context=None):
        period_obj = self.pool.get('account.period')
        period = period_obj.browse(cr, uid, period_id, context=context)
        date_start = period.date_start
        date_stop = period.date_stop
        # get nb jour absence par periodde,
        cr.execute("""SELECT 
                ab.number_absent_hours,
                ab.employee_id
            from
                res_absence ab
            where
                ab.employee_id = %s and 
                ab.date_from  >=    '%s' and 
                ab.date_from  <=    '%s' 
             """ % (employee_id, date_start, date_stop))
        res = cr.dictfetchall()
        days = 0
        for r in res :
            days= days+ (r['number_absent_hours'] or 0)
        return days 
    
    def _get_nb_days_ferie_200(self, cr, uid, employee_id, period_id, context=None):
        # get nb jour férié travaillé payé double par periode,
        cr.execute("""SELECT 
                h.id,
                h.employee_id,
                h.nb_days_presence
            from
                res_holidays_resume_line h
                JOIN  res_holidays_resume a
                ON a.id = h.holidays_resume_id
            where
                h.employee_id = %s and 
                a.period_id  =    '%s' 
             """ % (employee_id, period_id))
        res = cr.dictfetchall()
        days = 0
        for r in res :
            days= days+ (r['nb_days_presence'] or 0)
        return days 
    def _get_nb_days_ferie_100(self, cr, uid, employee_id, period_id, context=None):
        # get nb jour férié non travaillé par periode,
        cr.execute("""SELECT 
                h.id,
                h.employee_id,
                h.nb_days
            from
                res_holidays_resume_line h
                JOIN  res_holidays_resume a
                ON a.id = h.holidays_resume_id
            where
                h.employee_id = %s and 
                a.period_id  =    '%s' 
             """ % (employee_id, period_id))
        res = cr.dictfetchall()
        days = 0
        for r in res :
            days= days+ (r['nb_days'] or 0)
        return days 
        
hr_pointage()

class hr_pointage_line(osv.osv):
    _name = 'hr.pointage.line' 
    _description = 'Lignes  pointage'    
    _columns = { 
                'name': fields.char('Description', size=64),
                'pointage_id': fields.many2one('hr.pointage', 'Pointage', ondelete='cascade', select=True),
                'nb_pointage': fields.float('Pointage',),
                'nb_days_holiday': fields.float('Jours C.P',),
                'nb_days_masse': fields.float('Jours masse',),
                'hs100': fields.float('HS100',),
                'hs125': fields.float('HS125',),
                'hs150': fields.float('HS150',),
                'hs175': fields.float('HS175',),
                'hs200': fields.float('HS200',),
                'jour_supplementaire_worked':fields.float("F.T", digits_compute=dp.get_precision('Taux Paie'), help=u"Nombre des jours fériérs travaillés."),
                'jour_supplementaire':fields.float("F.N.T", digits_compute=dp.get_precision('Taux Paie'), help=u"Nombre des jours fériérs non travaillés."),
                'absence':fields.float("Jour A", digits_compute=dp.get_precision('Taux Paie')),
                'employee_id': fields.many2one('hr.employee', u'Employé', required=True),
               # 'regime': fields.related('employee_id', 'contract_id' , 'regime', type='char', relation='hr.contract', string='Regime', readonly=True),
               'regime_id': fields.related('employee_id', 'contract_id' , 'regime_id', type='many2one', relation='hr.contract.regime', string=u'Régime', readonly=True),
                } 


    def onchange_employee_id(self, cr, uid, ids, employee_id,month_id):
        res={}
        if employee_id :
            employee = self.pool.get('hr.employee').browse(cr, uid, employee_id)
            if not employee.contract_id :
                warning = {'title':'Attention', 'message':_(u"Veuillez d\'abord ajoutre un contract pour l'employée %s" % employee.name)}
                value = {'employee_id': False}
                res= {'warning': warning,
                        'value': value}
        return res
    
hr_pointage_line()   

 
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
