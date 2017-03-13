# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
#
#    Copyright (C) 2014  .
#    Coded by Borni DHIFI
#
# ----------------------------------------------------------------------------
import time

import openerp.addons.decimal_precision as dp
from openerp.osv import osv, fields
from openerp.tools.translate import _


class hr_payroll_tn(osv.osv):
    _inherit = "hr.payroll"
    _columns = {
        'move_id': fields.many2one('account.move', u'Pièce comptable', readonly=True),
    }

    def draft_cb(self, cr, uid, ids, context=None):
        for sal in self.browse(cr, uid, ids):
            if sal.move_id:
                raise osv.except_osv(_('Error !'), _(
                    u'Veuillez d\'abord supprimer les écritures comptables associés'))
            # delete old attribution congé      
            conge_automatique = sal.period_id.name
#             conge_like=u'Droit à des congés payés pour le mois : '+conge_automatique
#             print '-------------------------conge_like--------------------------',conge_like
#             sql = '''   DELETE from hr_holidays  where holiday_status_id=1 AND name LIKE %(conge_like)s ESCAPE '"'  ''' 
#             cr.execute(sql,dict(conge_like=u'Droit à des congés payés pour le mois : '+conge_automatique,))
            

            #del_holidays = holidays_obj.read(cr, uid, ids_holidays[0])
            #print '----------------ids_holidays----------------',ids_holidays
            
            #for holidays in holidays_obj.browse(cr, uid, ids_holidays, context=context):
                #delete old lines
                #print '---------------------holidays-------------------------',holidays.id
                #self.pool.get('hr.holidays').write(cr, uid, ids_holidays[], {'state': 'confirm'}, context=context)
     
            sql = '''   UPDATE  hr_holidays SET state='draft'  where holiday_status_id=1 AND name LIKE %(conge_like)s ESCAPE '"'  ''' 
            cr.execute(sql,dict(conge_like=u'Droit à des congés payés pour le mois : '+conge_automatique,))
            holidays_obj = self.pool.get('hr.holidays')
            ids_holidays = holidays_obj.search(cr, uid, [('holiday_status_id', '=', 1),('name', '=', u'Droit à des congés payés pour le mois : '+conge_automatique),('state','=','draft')])
            self.pool.get('hr.holidays').unlink(cr,uid,ids_holidays)            
            
            

            for sal in self.browse(cr, uid, ids):
                bulletins = self.pool.get('hr.payroll.bulletin').search(cr, uid, [('id_payroll', '=', sal.id)])
                print bulletins
                bulletins2 = self.pool.get('hr.payroll.bulletin').browse(cr, uid, bulletins)
                for bul in bulletins2:
                    bul.draft_bulletin()
        return self.write(cr, uid, ids, {'state': 'draft'}, context=context)

    def confirm_cb(self, cr, uid, ids, context=None):
        super(hr_payroll_tn, self).confirm_cb(cr, uid, ids, context=context)
        # pour gener les ecritures
        #self.action_move_create(cr, uid, ids)
        return self.write(cr, uid, ids, {'state': 'confirmed'}, context=context)

    def cancel_cb(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'cancelled'}, context=context)
    
    def action_comptabiliser(self, cr, uid, ids, context=None):
        # pour gener les ecritures
        self.action_move_create(cr, uid, ids)
#         bulletin = self.browse(cr, uid, ids[0], context)
#         if not bulletin.move_id :
#             raise osv.except_osv(_('Error !'), _(u'Absence des écritures comptables associés'))
#         if bulletin.move_id.state=='draft' :
#             raise osv.except_osv(_('Error !'), _(u'Veuillez d\'abord comptabiliser les écritures comptables associés')) 
        return self.write(cr, uid, ids, {'state': 'paid'}, context=context)

    # generation des ecriture comptable
    def action_move_create(self, cr, uid, ids):
        context = {}
        for sal in self.browse(cr, uid, ids):
            # parametres account
            params = self.pool.get('hr.payroll.parametres')
            ids_params = params.search(cr, uid, [('fiscalyear_id', '=', sal.period_id.fiscalyear_id.id)])
            if not ids_params:
                raise osv.except_osv(_('Erreur !'), _(u"Veuillez vérifier les paramétres de paie pour l'anée Fiscal courante"))
            dict_param = params.read(cr, uid, ids_params[0])
            # Journal  and currency
            journal_id = dict_param['account_journal_id'][0]
            if not journal_id:
                raise osv.except_osv(_('UserError'), _('Veuillez indiquer un journal des salaires dans le paramétrage de la comptabilité de la paie. '))
            journal = self.pool.get('account.journal').browse(cr, uid, journal_id, context=context)
            if journal.centralisation:
                raise osv.except_osv(
                    _('UserError'), _('Cannot create salary move on centralised journal'))
            currency_id = journal.currency and journal.currency.id or journal.company_id.currency_id.id
            # date and period
            date_move = sal.date_salary or time.strftime('%Y-%m-%d')
            period_id = sal.period_id and sal.period_id.id or False
            #
            #--------------cotisations TODO not get[0]-------------------------
            cotisation_obj = self.pool.get('hr.payroll.cotisation')
            cotisation_ids = cotisation_obj.search(cr, uid, [])           
            cotisation=cotisation_obj.browse(cr, uid, cotisation_ids[0])
            taux_tfp = round(dict_param['taux_tfp']/100.000, self.pool.get('decimal.precision').precision_get(cr, uid, 'Montant Paie')) 
            taux_accident_travail = round(dict_param['taux_accident_travail']/100.000, self.pool.get('decimal.precision').precision_get(cr, uid, 'Montant Paie')) 
            #taux_cotisation= dict_param['taux_cotisation']/100.0
            taux_foprolos = round(dict_param['taux_foprolos']/100.000, self.pool.get('decimal.precision').precision_get(cr, uid, 'Montant Paie')) 
            #taux_cnss=round(cotisation.tauxpatronal / 100.000, self.pool.get('decimal.precision').precision_get(cr, uid, 'Montant Paie')) 
            
            if not period_id:
                raise osv.except_osv(_('UserError'), _(u'Période obligaoire'))
            
            period = self.pool.get('account.period').browse(cr, uid, period_id, context=context)
            # name
            name_move = "Salaire " + period.name
            # move_lines
            move = {}
            move_lines = []
            sql_move = '''
                select sum(h.salaire_brute)        as salaire_brute,
                       sum(h.salaire_net_a_payer)  as salaire_net_a_payer,
                       sum(h.igr)                  as irpp,
                       sum(h.cotisations_employee)  as cnss,
                       sum(h.prime)                as primes,
                       sum(h.deduction)            as retenues,
                       sum(h.salaire_brute)*%s   as tfp,
                       sum(h.salaire_brute)*%s   as foprolos,
                       sum(h.salaire_brute * (c.cotisation)/100) as cnss2,
                       sum(h.salaire_brute * (c.work_accident_rate)/100) as accident_travail,
                       h.period_id
                 from hr_payroll_bulletin h
                 Join hr_contract c
                 on h.employee_contract_id= c.id
                 where h.period_id=%s
                 group by h.period_id
                ''' % (taux_tfp, taux_foprolos,period_id)
            cr.execute(sql_move)
            res_sql = cr.dictfetchall()
            # move = res_sql[0]
            res_sql = res_sql[0]
            # line salaire_brute
            if res_sql['salaire_brute']:
                if not dict_param['account_brut_id']:
                    raise osv.except_osv(_('Erreur'), _(
                        'Veuillez vérifier les comptes comptable dans le paramétrage de la comptabilité de la paie'))
                name_move = 'Bruts'

                ml_salaire_brute = {
                    'account_id': dict_param['account_brut_id'][0],
                    # 'analytic_account_id':
                    'period_id': period_id,
                    'journal_id': journal_id,
                    'date': date_move,
                    'name': name_move,
                    'debit': ((res_sql['salaire_net_a_payer']+res_sql['retenues']) + res_sql['irpp'])+ res_sql['cnss'],#res_sql['salaire_brute'],
                    'credit': 0.0,
                    # 'currency_id': currency_id,
                    'state': 'valid'
                }
                move_lines.append((0, 0, ml_salaire_brute))
            # line salaire_net_a_payer
            if res_sql['salaire_net_a_payer']:
                if not dict_param['account_net_paye_id']:
                    raise osv.except_osv(_('Erreur'), _(
                        'Veuillez vérifier les comptes comptable dans le paramétrage de la comptabilité de la paie'))
                name_move = u'Nets payées'
                ml_salaire_net_a_payer = {
                    'account_id': dict_param['account_net_paye_id'][0],
                    'period_id': period_id,
                    'journal_id': journal_id,
                    'date': date_move,
                    'name': name_move,
                    'debit': 0.0,
                    'credit': res_sql['salaire_net_a_payer'],
                    # 'currency_id': currency_id,
                    'state': 'valid'
                }
                move_lines.append((0, 0, ml_salaire_net_a_payer))
            # line ml_irpp
            if res_sql['irpp']:
                if not dict_param['account_irpp_id']:
                    raise osv.except_osv(_('Erreur'), _(
                        'Veuillez vérifier les comptes comptable dans le paramétrage de la comptabilité de la paie'))
                name_move = u'IRPP'
                ml_irpp = {
                    'account_id': dict_param['account_irpp_id'][0],
                    'period_id': period_id,
                    'journal_id': journal_id,
                    'date': date_move,
                    'name': name_move,
                    'debit': 0,
                    'credit': res_sql['irpp'],
                    # 'currency_id': currency_id,
                    'state': 'valid'
                }
                move_lines.append((0, 0, ml_irpp))
            # line cnss
            if res_sql['cnss']:
                if not dict_param['account_cnss_id']:
                    raise osv.except_osv(_('Erreur'), _(
                        'Veuillez vérifier les comptes comptable dans le paramétrage de la comptabilité de la paie'))
                name_move = u'CNSS'
                ml_cnss = {
                    'account_id': dict_param['account_cnss_id'][0],
                    'period_id': period_id,
                    'journal_id': journal_id,
                    'date': date_move,
                    'name': name_move,
                    'debit': 0,
                    'credit': res_sql['cnss'],
                    # 'currency_id': currency_id,
                    'state': 'valid'
                }
                move_lines.append((0, 0, ml_cnss))
            # line primes : #TODO: incorrect jai mis montant =0

            if res_sql['primes']:
                if not dict_param['account_prime_id']:
                    raise osv.except_osv(_('Erreur'), _(
                        'Veuillez vérifier les comptes comptable dans le paramétrage de la comptabilité de la paie'))
                name_move = u'Primes'
                ml_primes = {
                    'account_id': dict_param['account_prime_id'][0],
                    'period_id': period_id,
                    'journal_id': journal_id,
                    'date': date_move,
                    'name': name_move,
                    'debit':  0,#res_sql['primes'],
                    'credit': 0,
                    # 'currency_id': currency_id,
                    'state': 'valid'
                }
                move_lines.append((0, 0, ml_primes))
            # line retenues : #TODO: incorrect jai mis montant =0
            if res_sql['retenues']:
                if not dict_param['account_retenue_id']:
                    raise osv.except_osv(_('Erreur'), _(
                        'Veuillez vérifier les comptes comptable dans le paramétrage de la comptabilité de la paie'))
                name_move = u'Retenues'
                ml_retenues = {
                    'account_id': dict_param['account_retenue_id'][0],
                    'period_id': period_id,
                    'journal_id': journal_id,
                    'date': date_move,
                    'name': name_move,
                    'debit': 0,
                    'credit':  res_sql['retenues'],
                    # 'currency_id': currency_id,
                    'state': 'valid'
                }
                move_lines.append((0, 0, ml_retenues))

            # line tfp_d
            if res_sql['tfp']:
                if not dict_param['account_tfp_d_id']:
                    raise osv.except_osv(_('Erreur'), _(
                        'Veuillez vérifier les comptes comptable dans le paramétrage de la comptabilité de la paie'))
                name_move = u'Prise ch.employeur : TFP'
                ml_tfp_d = {
                    'account_id': dict_param['account_tfp_d_id'][0],
                    'period_id': period_id,
                    'journal_id': journal_id,
                    'date': date_move,
                    'name': name_move,
                    'debit': res_sql['tfp'],
                    'credit': 0.0,
                    # 'currency_id': currency_id,
                    'state': 'valid'
                }
                move_lines.append((0, 0, ml_tfp_d))
            # line tfp_c
            if res_sql['tfp']:
                if not dict_param['account_tfp_c_id']:
                    raise osv.except_osv(_('Erreur'), _(
                        'Veuillez vérifier les comptes comptable dans le paramétrage de la comptabilité de la paie'))
                name_move = u'Prise ch.employeur : TFP'
                ml_tfp_c = {
                    'account_id': dict_param['account_tfp_c_id'][0],
                    'period_id': period_id,
                    'journal_id': journal_id,
                    'date': date_move,
                    'name': name_move,
                    'debit': 0,
                    'credit': res_sql['tfp'],
                    # 'currency_id': currency_id,
                    'state': 'valid'
                }
                move_lines.append((0, 0, ml_tfp_c))
            # line foprolos_d
            if res_sql['foprolos']:
                if not dict_param['account_foprolos_d_id']:
                    raise osv.except_osv(_('Erreur'), _(
                        'Veuillez vérifier les comptes comptable dans le paramétrage de la comptabilité de la paie'))
                name_move = u'Prise ch.employeur : FoProLos'
                ml_foprolos_d = {
                    'account_id': dict_param['account_foprolos_d_id'][0],
                    'period_id': period_id,
                    'journal_id': journal_id,
                    'date': date_move,
                    'name': name_move,
                    'debit': res_sql['foprolos'],
                    'credit': 0,
                    # 'currency_id': currency_id,
                    'state': 'valid'
                }
                move_lines.append((0, 0, ml_foprolos_d))
            # line foprolos_c
            if res_sql['foprolos']:
                if not dict_param['account_foprolos_c_id']:
                    raise osv.except_osv(_('Erreur'), _(
                        'Veuillez vérifier les comptes comptable dans le paramétrage de la comptabilité de la paie'))
                name_move = u'Prise ch.employeur : FoProLos'
                ml_foprolos_c = {
                    'account_id': dict_param['account_foprolos_c_id'][0],
                    'period_id': period_id,
                    'journal_id': journal_id,
                    'date': date_move,
                    'name': name_move,
                    'debit': 0,
                    'credit': res_sql['foprolos'],
                    # 'currency_id': currency_id,
                    'state': 'valid'
                }
                move_lines.append((0, 0, ml_foprolos_c))
            # line cnss_c
            if res_sql['cnss2']:
                if not dict_param['account_cnss_c_id']:
                    raise osv.except_osv(_('Erreur'), _(
                        'Veuillez vérifier les comptes comptable dans le paramétrage de la comptabilité de la paie'))
                name_move = u'Prise ch.employeur : CNSS'
                mnt_cnss_c = round(res_sql['cnss2'], self.pool.get(
                    'decimal.precision').precision_get(cr, uid, 'Paie tn : Montant'))
                ml_cnss_c = {
                    'account_id': dict_param['account_cnss_c_id'][0],
                    'period_id': period_id,
                    'journal_id': journal_id,
                    'date': date_move,
                    'name': name_move,
                    'debit': 0,
                    'credit': mnt_cnss_c,
                    # 'currency_id': currency_id,
                    'state': 'valid'
                }
                move_lines.append((0, 0, ml_cnss_c))
            # line accident_travail
            if res_sql['accident_travail']:
                if not dict_param['account_accident_travail_c_id'] or not  dict_param['account_accident_travail_d_id']:
                    raise osv.except_osv(_('Erreur'), _('Veuillez vérifier les comptes comptable dans le paramétrage de la comptabilité de la paie'))

                name_move = u'Accident de travail'
                mnt_accident_travail = round(res_sql['accident_travail'], self.pool.get('decimal.precision').precision_get(cr, uid, 'Paie tn : Montant'))
                               
                ml_accident_travail = {
                    'account_id': dict_param['account_accident_travail_d_id'][0],
                    'period_id': period_id,
                    'journal_id': journal_id,
                    'date': date_move,
                    'name': name_move,
                    'debit': mnt_accident_travail,
                    'credit': 0,
                    # 'currency_id': currency_id,
                    'state': 'valid'
                }
                move_lines.append((0, 0, ml_accident_travail))                 
                
                ml_accident_travail = {
                    'account_id': dict_param['account_accident_travail_c_id'][0],
                    'period_id': period_id,
                    'journal_id': journal_id,
                    'date': date_move,
                    'name': name_move,
                    'debit': 0,
                    'credit': mnt_accident_travail,
                    # 'currency_id': currency_id,
                    'state': 'valid'
                }
                move_lines.append((0, 0, ml_accident_travail))
                
            # line cnss_d
            if res_sql['cnss2']:
                if not dict_param['account_cnss_d_id']:
                    raise osv.except_osv(_('Erreur'), _('Veuillez vérifier les comptes comptable dans le paramétrage de la comptabilité de la paie'))
                
                name_move = u'Prise ch.employeur'
                mnt = round((mnt_cnss_c), self.pool.get('decimal.precision').precision_get(cr, uid, 'Paie tn : Montant'))
                ml_cnss_d = {
                    'account_id': dict_param['account_cnss_d_id'][0],
                    'period_id': period_id,
                    'journal_id': journal_id,
                    'date': date_move,
                    'name': name_move,
                    'debit': mnt,
                    'credit': 0,
                    # 'currency_id': currency_id,
                    'state': 'valid'
                }
                move_lines.append((0, 0, ml_cnss_d))
            # move_lines.sort(cmp=None, key=None, reverse=True)
            # create move
            move = {'ref': '/',
                    'period_id': period_id,
                    'journal_id': journal_id,
                    'date': date_move,
                    'state': 'draft',
                    'name': sal.name or '/',
                    'line_id': move_lines
                    }
            move_id = self.pool.get('account.move').create(
                cr, uid, move, context=context)
            # write move_id for this salaire
            self.pool.get('hr.payroll').write(
                cr, uid, sal.id, {'move_id': move_id})
            return True

hr_payroll_tn()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
