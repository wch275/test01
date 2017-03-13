# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
#
#    Copyright (C) 2014  .
#    Coded by: Borni DHIFI  (dhifi.borni@gmail.com)
#
#----------------------------------------------------------------------------

from openerp.osv import fields, osv
#from openerp import models, api, _
from openerp.tools.translate import _
from openerp.exceptions import except_orm, Warning, RedirectWarning
import openerp.addons.decimal_precision as dp

class journal_paie(osv.osv):
    _name = 'journal.paie'
    _description = 'journal de paie'
    
    def _get_defaults_fiscal_year(self, cr, uid, data, context={}):
        fiscalyear_obj = self.pool.get('account.fiscalyear')
        fisc = fiscalyear_obj.find(cr, uid)
        data['form'] = fisc
        return data['form']


    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise except_orm(_('Error!'), _('There is no default company for the current user!'))
        return company_id

    def _get_month_id(self, cr, uid, context=None):
        """
        Return  default account period value
        """
        context = context or {}
        if context.get('period_id', False):
            return context['period_id']
        account_period_obj = self.pool.get('hr.month')
        ctx = dict(context, hr_month_prefer_normal=True)
        ids = account_period_obj.find(cr, uid, context=ctx)
        period_id = False
        if ids:
            period_id = ids[0]
        return period_id
    
    def _get_period_id(self, cr, uid, context=None):
        """
        Return  default account period value
        """
        context = context or {}
        if context.get('period_id', False):
            return context['period_id']
        account_period_obj = self.pool.get('hr.month')
        ctx = dict(context, hr_month_prefer_normal=True)
        ids = account_period_obj.find(cr, uid, context=ctx)
        period_id = False
        if ids:
            period_id = ids[0]
            month = self.pool.get('hr.month').browse(cr, uid, ids[0])
            period_id= month.period_id.id
        return period_id
    
    def onchange_month_id(self, cr, uid, ids, month_id):
        month = self.pool.get('hr.month').browse(cr, uid, month_id)
        period_id= month.period_id.id  
        company_id = self.pool.get('res.users')._get_company(cr, uid)
        company = self.pool.get('res.company').browse(cr, uid, company_id)    
        result = {'value': { 'period_id' : period_id,'name' :   _(u"Journal de paie %s du mois %s ") % (company.name, month.name)} }
        return result

    _columns = {
             'name':fields.char('Nom'),
             'month_id':fields.many2one('hr.month', 'Periode', required=True),
             'period_id':fields.many2one('account.period',u"Période"),
             'company_id':fields.many2one('res.company', u'Société', required=True),
             'line_journal_paie_ids': fields.one2many('journal.paie.line','journal_paie_line_id')
             }


    _defaults = {
            'company_id' : _get_default_company,
            'month_id' : _get_month_id,
            'period_id' : _get_period_id,
        }

    def print_report(self, cr, uid, ids, context=None):
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'wizard_journal_paie'
        datas['form'] = self.read(cr, uid, ids, context=context)[0]
        context['landscape']=True
        return self.pool['report'].get_action(cr, uid, [], 'devplus_hr_payroll_tn.report_journal_paie', data=datas, context=context)


    def get_journal(self,cr, uid, ids, context=None):
        #TODO: ajouter le pointage dans le journal 
        journal_paie =self.browse(cr, uid, ids[0], context=context)
        month_id=journal_paie.month_id.id
        sql = '''   DELETE from journal_paie_line where journal_paie_line_id = %s '''
        cr.execute(sql, (journal_paie.id,))
        sql = '''
          SELECT e.matricule ,e.name_related as name,r.name as regime,b.salaire_base,b.salaire_brute,
        b.cotisations_employee,b.cotisations_employer,    
        b.salaire_brute_cotisable,
        b.salaire_net,b.salaire_brute_imposable,
        b.igr,
        b.indemnite,b.avantage,b.exoneration,b.deduction,        
       
        b.prime,
        b.salaire_net_a_payer,
            b.frais_pro,
        e.identification_id,e.birthday,
            b.employee_contract_id as contract
        
        FROM hr_payroll_bulletin b

        LEFT JOIN hr_contract c on (b.employee_contract_id=c.id)
        LEFT JOIN hr_employee e on (b.employee_id=e.id)
        LEFT JOIN hr_contract_regime r on (c.regime_id=r.id)
        WHERE
        (b.month_id=%s )
        ORDER BY e.matricule ASC;  
        ''' % (month_id)
        cr.execute(sql)
        all_lines = cr.dictfetchall()
        line= []
        for line_paie in all_lines:
            val=(0, 0, {   
                            'employee':line_paie['name'],
                            'matricule':line_paie['matricule'],
                            'regime':line_paie['regime'],
                            'salaire_base':line_paie['salaire_base'],
                            'salaire_brut':line_paie['salaire_brute'],
                            'retenu_cnss':line_paie['cotisations_employee'],
                            'salaire_imposable':line_paie['salaire_brute_imposable'],
                            'irpp':line_paie['igr'],
                            'salaire_net':line_paie['salaire_net'],
                            'avance_pret':line_paie['deduction'],
                            'salaire_net_a_paye':line_paie['salaire_net_a_payer'],
                            'journal_paie_line_id': journal_paie.id
                        }) 
            line.append(val)
                     
        value = {  'line_journal_paie_ids': line, 'month_id' : journal_paie.month_id.id,'company_id': journal_paie.company_id.id}   
        self.write(cr, uid, journal_paie.id, value, context=context)  
        return True
journal_paie()

class journal_paie_line(osv.osv):
    _name = 'journal.paie.line' 
    _columns={
        'employee':fields.char(u'Employés'),
        'matricule':fields.char('Matricule'),
        'regime':fields.char(u"Régime"),
        'salaire_base':fields.float(u"Salaire base",digits_compute=dp.get_precision('Montant Paie')) ,
        'salaire_brut':fields.float(u"Salaire Brut",digits_compute=dp.get_precision('Montant Paie')),
        'retenu_cnss':fields.float(u"Retenue CNSS",digits_compute=dp.get_precision('Montant Paie')),
        'salaire_imposable':fields.float(u"Salaire Imposable",digits_compute=dp.get_precision('Montant Paie')),
        'irpp':fields.float(u"IRPP",digits_compute=dp.get_precision('Montant Paie')),
        'salaire_net':fields.float(u"Salaire Net",digits_compute=dp.get_precision('Montant Paie')),
        'avance_pret':fields.float(u"Avance et prets",digits_compute=dp.get_precision('Montant Paie')),
        'salaire_net_a_paye':fields.float(u"Net à payé", digits_compute=dp.get_precision('Montant Paie')),
        'journal_paie_line_id':fields.many2one('journal.paie'),
    }
journal_paie_line()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: