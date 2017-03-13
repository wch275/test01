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
from datetime import date, datetime


#-------------------------------------------------------------------------------
# hr_employee
#-------------------------------------------------------------------------------
class hr_employee(osv.osv):
    _inherit = "hr.employee"    
    _order = 'matricule' 
    

    def _check_length_cin(self, cr, uid, ids, context=None):
        record = self.browse(cr, uid, ids, context=context)
        for data in record:
            if data.cin and  (len(data.cin) != 8):
                return False
            return True
    def _check_date_sortie(self, cr, uid, ids, context=None):
        record = self.browse(cr, uid, ids, context=context)
        for data in record:
            if data.date_sortie and (data.date_entree >= data.date_sortie):
                return False
            return True
#     def onchange_date_sortie(self, cr, uid, ids, date_sortie, context=None):
#         record = self.browse(cr, uid, ids, context=context)
#         for data in record:
#             contract_ids = self.pool.get('hr.contract').search(cr, uid, [('employee_id', '=', data.id)])
#             self.pool.get('hr.contract').browse(cr, uid, contract_ids).date_end = date_sortie
#             return True
        
    def _action_count_autorisation(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        for employee in self.browse(cr,uid,ids):
            result[employee.id] = len(employee.autorisation_ids) 
        return result 
    
    def _action_count_child(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        for employee in self.browse(cr,uid,ids):
            nb_enfant_etudiant=nb_enfant_handicape=children=0
            result[employee.id]={'nb_enfant_etudiant' : 0,
                                 'nb_enfant_handicape' : 0,
                                 'children':0
                                 }
            
            for child in employee.enfant_line_ids :
                if child.prise_charge:
                    if child.handicap:nb_enfant_handicape+=1
                    elif child.boursier:nb_enfant_etudiant+=1
                    else :children+=1
                        
                
            result[employee.id]['nb_enfant_etudiant'] = nb_enfant_etudiant
            result[employee.id]['nb_enfant_handicape'] = nb_enfant_handicape
            result[employee.id]['children'] = children
        return result  
    
    _columns = {
            'matricule' : fields.char('Matricule', size=64, select=True,required=True),
            'cnss' : fields.char('CNSS', size=11),
            'cin' : fields.char('CIN', size=8,required=True ),
            'cnrps' : fields.char('CNRPS', size=10),
            'date_entree': fields.date(u'Date  entrée'),
            'date_sortie': fields.date(u'Date  sortie'),
            'sortie_cause': fields.char('Cause de sortie'),
            'nb_parents' : fields.integer(u'Nombre parents à charge'),
            'nb_enfant_etudiant' : fields.function(_action_count_child, type='integer', string=u'Nombre enfants étudiants',multi="count"),
            'nb_enfant_handicape' :  fields.function(_action_count_child, type='integer', string=u'Nombre enfants handicapés',multi="count"),
            'children' :  fields.function(_action_count_child, type='integer', string="Nombre d'enfants",multi="count",help=u"Nombre d'enfants autre que etudiants et handicapés"),
            'chef_famille': fields.boolean('Chef de famille'),
            'mode_reglement' : fields.selection([('virement', 'Virement'), ('cheque', u'Chèque'), ('espece', u'Espèce'), ], u'Mode de règlement'),
            'address_home' : fields.char('Adresse Personnelle', size=128),
            'address' : fields.char('Adresse Professionnelle', size=128),
            'res_bank_id': fields.many2one('res.bank', 'Banque'),
            'numero_compte' : fields.char(u'Numéro de compte', size=64,),
            'marital': fields.selection([('c', 'Single'), ('m', 'Married'), ('v', 'Widower'), ('d', 'Divorced')], 'Marital Status'),
            'irpp': fields.boolean(u'IRPP ?'),
            'avance': fields.boolean('Autoriser une avance sur salaire'),
            'action_count_autorisation': fields.function(_action_count_autorisation, type='float', string="Nombre d'autorisation"),
            # redefine
            # redifin to delete domain :domain="[('partner_id','=',address_home_id)]",
            # 'bank_account_id': fields.many2one('res.partner.bank', 'Bank Account Number', help="Employee bank salary account"),
            'autorisation_ids':fields.one2many('hr.autorisation', 'employee_id', 'Autorisations'), 
            'numero_compte' :fields.char('Numéro de compte',size=20),
            'enfant_line_ids': fields.one2many('hr.enfant', 'emp_id', 'Enfants'),

            'zip' :fields.char('ZIP'),
            'state_id': fields.many2one('res.country.state', 'Gouvernorat'),
            'region_id': fields.many2one('res.country.region', 'Délégation'),
            'localite_id': fields.many2one('res.country.localite', 'Localité'),
            'country_id': fields.many2one('res.country', 'Pays'),
            
            'interet_credit': fields.float('Interet Credit', digits_compute=dp.get_precision('Montant Paie')),

        
        
        

            }
    _defaults = {
            'date_entree' : lambda * a: time.strftime('%Y-%m-%d'),
            'cnss':'0000000000',
             'irpp':True
            }

    _constraints = [
                    (_check_length_cin, u'Erreur: Le CIN doit être composé de huit chiffres', ['cin']),
                    (_check_date_sortie, u"Erreur: La date de sortie doit être supérieure à la date d'entrée", ['date_sortie']),
                    ]

    _sql_constraints = [
        ('cin_employee_uniq', 'unique (cin)', u'CIN existe déjà !')
    ]
    _sql_constraints = [
        ('matricule_employee_uniq', 'unique (matricule)', u'Matricule existe déjà !')
    ]
            
    def _get_nb_days_cp_by_period(self, cr, uid, employee_id, period_id, context=None):
        period_obj = self.pool.get('account.period')
        period = period_obj.browse(cr, uid, period_id, context=context)
        date_start = period.date_start
        date_stop = period.date_stop
        # get nb congé payé par periode h.number_of_days  as days,
        cr.execute("""SELECT 
                h.id,
                h.employee_id,
                h.number_of_days_temp
            from
                hr_holidays h
                join hr_holidays_status s on (s.id=h.holiday_status_id)
            where
                h.state='validate' and
                s.payed=True and
                h.employee_id = %s and 
                h.date_from  >    '%s' and 
                h.date_from  <    '%s' 
             """ % (employee_id, date_start, date_stop))
        res = cr.dictfetchall()
        days = 0
        for r in res :
            days= days+ (r['number_of_days_temp'] or 0)
        return days   

    def _get_nb_days_c_impaye_by_period(self, cr, uid, employee_id, period_id, context=None):
        period_obj = self.pool.get('account.period')
        period = period_obj.browse(cr, uid, period_id, context=context)
        date_start = period.date_start
        date_stop = period.date_stop
        # get nb congé payé par periode h.number_of_days  as days,
        cr.execute("""SELECT 
                h.id,
                h.employee_id,
                h.number_of_days_temp
            from
                hr_holidays h
                join hr_holidays_status s on (s.id=h.holiday_status_id)
            where
                h.state='validate' and
                s.payed=False and
                h.employee_id = %s and 
                h.date_from  >    '%s' and 
                h.date_from  <    '%s' 
             """ % (employee_id, date_start, date_stop))
        res = cr.dictfetchall()
        days = 0
        for r in res :
            days= days+ (r['number_of_days_temp'] or 0)
        return days  

    def _get_nb_days_ferie_payed(self, cr, uid, employee_id, period_id, context=None):
        period_obj = self.pool.get('account.period')
        period = period_obj.browse(cr, uid, period_id, context=context)
        date_start = period.date_start
        date_stop = period.date_stop
        # get nb jour férié travaillé par periode,
        cr.execute("""SELECT 
                h.id,
                h.employee_id,
                h.nb_days_presence
            from
                res_holidays_resume_line h
                JOIN  res_holidays_resume a
                ON a.id = h.holidays_id
            where
                h.employee_id = %s and 
                h.date_start  >=    '%s' and 
                h.date_end  <=    '%s' and
                a.type = 'paye'
                
             """ % (employee_id, date_start, date_stop))
        res = cr.dictfetchall()
        days = 0
        for r in res :
            days= days+ (r['nb_days_presence'] or 0)
        print'%s - %s - %s',employee_id, employee_id,days
        return days 

    def _get_nb_days_ferie_non_payed(self, cr, uid, period_id, context):
        period_obj = self.pool.get('account.period')
        period = period_obj.browse(cr, uid, period_id, context=context)
        date_start = period.date_start
        date_stop = period.date_stop
        # get nb jour férié travaillé par periode,
        cr.execute("""SELECT 
                SUM(nb_days) as nb_days
            from
                res_holidays_resume
            where
                date_start  >=    '%s' and 
                date_end  <=    '%s' and
                type = 'non_paye'
             """ % (date_start, date_stop))
        res = cr.dictfetchall()
        days = 0
        for r in res :
            days= days+ (r['nb_days'] or 0)
        print '--------------------------------------days--------------------------',days
        return days
    
    def _get_nb_days_ferie_worked(self, cr, uid, employee_id, period_id, context=None):
        period_obj = self.pool.get('account.period')
        period = period_obj.browse(cr, uid, period_id, context=context)
        date_start = period.date_start
        date_stop = period.date_stop
        # get nb jour férié travaillé par periode,
        cr.execute("""SELECT 
                h.id,
                h.employee_id,
                h.nb_days_presence
            from
                res_holidays_resume_line h
                JOIN  res_holidays_resume a
                ON a.id = h.holidays_id
            where
                h.employee_id = %s and 
                h.date_start  >=    '%s' and 
                h.date_end  <=    '%s' and
                a.type = 'non_paye'
             """ % (employee_id, date_start, date_stop))
        res = cr.dictfetchall()
        days = 0
        for r in res :
            days= days+ (r['nb_days_presence'] or 0)
        print'%s - %s - %s',employee_id, employee_id,days
        return days

         
    def _get_total_days_conge_paye_attribue(self, cr, uid, employee_id, context=None):
        cr.execute("""SELECT 
                  sum(h.number_of_days) as days,
                h.employee_id
            from
                hr_holidays h
                join hr_holidays_status s on (s.id=h.holiday_status_id)
            where
                h.state='validate' and
                 h.type = 'add' and 
                s.payed=True and
                h.employee_id = %s 
                group by h.employee_id
             """ % (employee_id))
        res = cr.dictfetchall()
        
        return abs((res and res[0]['days'])  or 0)
    
    def _get_total_days_conge_pris(self, cr, uid, employee_id, context=None):
        cr.execute("""SELECT 
                  sum(h.number_of_days) as days,
                h.employee_id
            from
                hr_holidays h
                join hr_holidays_status s on (s.id=h.holiday_status_id)
            where
                h.state='validate' and
                 h.type = 'remove' and 
                s.payed=True and
                h.employee_id = %s 
                group by h.employee_id
             """ % (employee_id))
        res = cr.dictfetchall()
        return abs((res and res[0]['days'])  or 0)
       
    def _get_total_days_restante(self, cr, uid, employee_id, context=None):
        days_all = self._get_total_days_conge_paye_attribue(cr, uid, employee_id, context=context)
        pris = self._get_total_days_conge_pris(cr, uid, employee_id, context=context)
        return days_all - pris #abs(days_all - pris) 

    def get_deduction_infraction(self,cr,uid,date_from,date_to,total):
        infraction_obj= self.pool.get('hr.infraction')
        infraction_ids=infraction_obj.search(cr,uid,[('date','>=',date_from),('date','<=',date_to)])
        amount=0.0
        for infraction in infraction_obj.browse(cr,uid,infraction_ids) :
            if infraction.type_id.type== 'percentage' :
                amount += (infraction.type_id.percentage * total) /100.0
            if infraction.type_id.type== 'amount' :
                amount += infraction.type_id.amount
            if infraction.type_id.type== 'nb_days' :
                amount += infraction.type_id.number_days * (total /22.0)  #TODO: 30not fix             
        return amount*(-1)
       
hr_employee()


#-------------------------------------------------------------------------------
# hr_enfant
#-------------------------------------------------------------------------------
class hr_enfant(osv.osv) :
    _name = 'hr.enfant'
    _description = 'Employee Enfant'
    def onchange_boursier(self, cr, uid, ids,boursier):
        if boursier:
            handicap_state=False
            res={'value':{'handicap': handicap_state}}
            return res
        return True  
    def onchange_handicap(self, cr, uid, ids,handicap):
        if handicap:
            boursier_state=False
            res={'value':{'boursier': boursier_state}}
            return res
        return True 

    
    def _check_rang(self, cr, uid, ids, context=None):
        enfant = self.browse(cr, uid, ids, context=context)
        for data in enfant:
            if data.rang_enfant <= 0 :
                return False
        return True           
    _columns = {
            'name':fields.char("Nom"),
            'rang_enfant':fields.integer(u"Rang"), 
            'birth_date':fields.date(u"Date de Naissance"),
            'emp_id':fields.many2one('hr.employee', 'Employe', select=True),
            'prise_charge' : fields.boolean("Prise en Charge"),
            'boursier' : fields.boolean("Boursier"),
            'handicap' : fields.boolean(u"Handicapé"),
            'amount_child': fields.float('Montant', digits_compute=dp.get_precision('Montant Paie')),
            }
    
    _constraints = [(_check_rang,  u'Erreur: Le Rang ne doit pas être null', ['rang_enfant']), ]
    
    def calculate_age(self, cr, uid, born):
        today = date.today()
        born_date=datetime.strptime(born, '%Y-%m-%d').date()
        return today.year - born_date.year - ((today.month, today.day) < (born_date.month, born_date.day))
    
    def onchange_birthday(self, cr, uid, ids,birthday):
        res={}
        if birthday : 
            if self.calculate_age(cr, uid,birthday) < 20:
                res={'value':{'prise_charge': True}}
            else:
                res={'value':{'prise_charge': False}}
        return res


hr_enfant()
#-------------------------------------------------------------------------------
# hr_contract_type
#-------------------------------------------------------------------------------
class hr_contract_type(osv.osv) :
    _inherit = 'hr.contract.type'
    _columns = {
            'irpp' : fields.boolean("Calculer l'impôt?"),
            'cotisation':fields.many2one('hr.payroll.cotisation.type', 'Type cotisations', required=True),
            'date_fin':fields.boolean("Date Fin Obligatoire"),
            'work_accident':fields.boolean("Accident de travail"),
            }

#-------------------------------------------------------------------------------
# hr_contract_regime
#-------------------------------------------------------------------------------
class hr_contract_regime(osv.osv) :
    _name = 'hr.contract.regime'
    _columns = {
                'name':fields.char('Nom',required=True), 
                'type_regime' : fields.selection([('horaire', 'Horaire'), #('journalier', 'Journalier'),
                                                  ('mensuel', 'Mensuel') ], u'Régime', required=True),
                'hours_horaire':fields.integer(u"Nombre d'heure par semaine"), 
                'hours_day':fields.integer(u"Nombre de jour par semaine"),
                'hours_horaire_day':fields.integer(u"Nombre d'heure par jour"),
                'hours_horaire_mensuel':fields.integer(u"Nombre d'heure par mois"),
                'hours_holidays':fields.integer(u"Nombre d'heure par JF/JC "),
                'hours_mensuel':fields.selection([('40','40 H'), ('48','48 H')], u"Nombre d'heure"),
                }
    def onchange_horaire(self, cr, uid, ids, hours_day, hours_horaire):
        result ={}
        if hours_day and hours_horaire:
            result = {'value':{ 'hours_horaire_day' :  hours_horaire/hours_day}}
        return result        
#-------------------------------------------------------------------------------
# hr_contract
#-------------------------------------------------------------------------------
class hr_contract(osv.osv) :
    _inherit = 'hr.contract'
    _description = 'Employee Contract'

    def _check_wage_positive(self, cr, uid, ids, context=None):
        record = self.browse(cr, uid, ids, context=context)
        for data in record:
            if data.wage  < 0 :
                return False
            return True

    _columns = {
                'date':fields.date('Date'),
                'matr' :fields.char('Matricule'),
                #'cotisation':fields.many2one('hr.payroll.cotisation.type', 'Type cotisations'),
                'cotisation':fields.float('Cotisation', digits_compute=dp.get_precision('Taux Paie')),
                'work_accident_rate':fields.float('Taux Accident de travail', digits_compute=dp.get_precision('Taux Paie')),
                'rubrique_ids': fields.one2many('hr.payroll.ligne_rubrique', 'id_contract', 'Les rubriques'),
                # redefine   type_id to delete required=True
                'type_id': fields.many2one('hr.contract.type', "Contract Type", required=True),
                  # redefine  wage to modifiy digits
                'num': fields.char(u'Numéro'),
                'wage': fields.float('Wage', digits_compute=dp.get_precision('Montant Paie'), required=False),
		        'salaire_de_base': fields.float('Salaire de base', digits_compute=dp.get_precision('Montant Paie'),required=True),
                'indemmnite_diff': fields.float('Indemnité différentielle', digits_compute=dp.get_precision('Montant Paie'),readonly=True),
                'salaire_net': fields.float('Salaire Net', digits_compute=dp.get_precision('Montant Paie')),
                'regime_id': fields.many2one('hr.contract.regime', u"Régime", required=True),
                'date_end':fields.date("Date Fin"),
                'date_fin_state':fields.boolean("Date fin"),
               
                ##'regime' : fields.selection([('horaire', 'Horaire'),
                                                   # ('journalier', u'Journalier'),
                                                     #('mensuel', u'Mensuel') ], u'Regime', required=True),
            
	           }
    
    _defaults = {
                 'date': fields.date.context_today,
                 }

    _constraints = [
               (_check_wage_positive,  u'Erreur: Le Montant ne peut pas  être négative', ['wage']),
              ]

    def add_indemnite(self, cr, uid, ids, context=None):
        rubriques=self.pool.get('hr.payroll.ligne_rubrique')
        contrat = self.browse(cr, uid, ids[0], context)
        indemnite_montant= contrat.indemmnite_diff
        if indemnite_montant == 0.0 :
            return True
        
        params_obj= self.pool.get('hr.payroll.parametres')
        fiscalyear_id = self.pool.get('account.fiscalyear').find(cr, uid)
        ids_params = params_obj.search(cr, uid, [('fiscalyear_id', '=', fiscalyear_id)])
        params = params_obj.read(cr, uid, ids_params[0])

        rubriques.create(cr, uid,
                                      { 
                                       'montant' : indemnite_montant,
                                       'permanent': True,
                                       'rubrique_id': params['prime_fonction'][0],
                                       'id_contract': contrat.id,
                                    })
        
        
        
        self.write(cr, uid,ids[0],{'indemmnite_diff': 0.0})

        return True
    def onchange_employee_id(self, cr, uid, ids, employee_id, context=None):
        res = super(hr_contract, self).onchange_employee_id(cr, uid, ids, employee_id)
        employee=self.pool.get('hr.employee').browse(cr,uid,employee_id,context)
        res['value'].update({'matr':employee.matricule})
        return res

    def onchange_type_id(self, cr, uid, ids, type_id, context=None):
        contract=self.pool.get('hr.contract.type').browse(cr,uid,type_id,context)
        tauxpatronal = 0
        if contract.cotisation :
            for cotisation in contract.cotisation.cotisation_ids:
                tauxpatronal = tauxpatronal + cotisation.tauxpatronal
        tauxworkaccident = 0
        if contract.work_accident :
            params_obj= self.pool.get('hr.payroll.parametres')
            fiscalyear_id = self.pool.get('account.fiscalyear').find(cr, uid)
            ids_params = params_obj.search(cr, uid, [('fiscalyear_id', '=', fiscalyear_id)])
            params = params_obj.read(cr, uid, ids_params[0]) 
            tauxworkaccident = params['taux_accident_travail']         
        res={'value':{'date_fin_state':contract.date_fin, 'cotisation': tauxpatronal, 'work_accident_rate': tauxworkaccident}}
        return res            

    def create(self, cr, uid, vals, context=None):
        if not vals.get('num', False):
            vals['num'] = self.pool.get('ir.sequence').get(cr, uid, 'hr.contract', context=context) or '/'
        return super(hr_contract, self).create(cr, uid, vals, context=context)
    
    def net_to_brute(self, cr, uid, ids, context={}):
        '''
        Calculer Brut  apartir du Net
        :param cr:
        :param uid:
        :param ids:
        :param context:
        '''
        contract = self.browse(cr, uid, ids[0])
        #if field   irpp  in contract is false retrun salaire net
        if  contract.type_id and  not contract.type_id.irpp: 
            self.write(cr, uid, [contract.id], {'wage' :contract.salaire_net })
            return True
        
        bulletin_obj=self.pool.get('hr.payroll.bulletin')
        salaire_base = contract.salaire_net
        cotisation = contract.type_id.cotisation
        base = 0                
        #
        #--------------rubriques-------------------------------------------------
        prime = 0.0
        indemnite = 0.0
        avantage = 0.0
        mnt_rubriques=0.0
        exoneration_irpp = 0.0
        exoneration_cotisable = 0.0
        query = '''
        SELECT l.montant, r.name,r.categorie,r.type,r.regime, r.afficher,r.sequence,r.imposable,r.cotisable,r.absence
        FROM hr_payroll_ligne_rubrique l
        LEFT JOIN hr_payroll_rubrique r on (l.rubrique_id=r.id)
        WHERE 
        (l.id_contract=%s and l.permanent=True) OR 
        (l.id_contract=%s and l.date_start <= now() and l.date_stop >= now())
        order by r.sequence
        ''' % (contract.id, contract.id)
        
        cr.execute(query)
        rubriques = cr.dictfetchall()
        
        regime_contact=contract.regime_id.type_regime
        montant_indemnite=0.0
        nb_jour=22
        if regime_contact=='mensuel':
            if contract.regime_id.hours_mensuel == '48':
                nb_jour=26
        if regime_contact=='horaire':
            nb_jour=contract.regime_id.hours_horaire_mensuel /contract.regime_id.hours_horaire_day
        #--------------rubriques  majoration -------------------------------------------------
        for rubrique in rubriques :
            if(rubrique['categorie'] == 'majoration'):
                
                regime_rubrique = rubrique['regime']
                taux = contract.employee_id.leaves_count #bulletin.pointage
                montant = rubrique['montant']
                montant_mensuel = rubrique['montant']
                if contract.regime_id in ('journalier', 'mensuel') :
                    if regime_rubrique == 'mensuel' :
                        montant_mensuel=rubrique['montant']
                        if rubrique['absence'] :
                            taux = contract.employee_id.leaves_count / nb_jour
                        else :
                            taux = 1
                    elif regime_rubrique == 'journalier' :
                        montant_mensuel=rubrique['montant']*nb_jour
                        taux = contract.employee_id.leaves_count 
                    else :
                        taux = contract.employee_id.leaves_count * 8.0
                else :  # regime_contact = horaire
                    month_hours=self.pool.get('hr.contract.regime').browse(cr,uid,contract.regime_id.id).hours_horaire_mensuel
                    day_hours=self.pool.get('hr.contract.regime').browse(cr,uid,contract.regime_id.id).hours_horaire_day
                    if regime_rubrique == 'mensuel' :
                        montant_mensuel=rubrique['montant']
                        taux = contract.employee_id.leaves_count * (1.0 / nb_jour / 8.0)
                        taux = round(taux, self.pool.get('decimal.precision').precision_get(cr, uid, 'Montant Paie'))  
                    elif regime_rubrique == 'journalier' :
                        montant_mensuel=rubrique['montant']*(month_hours/day_hours)
                        taux = contract.employee_id.leaves_count * float(1.0 / 8.0)
                        taux = round(taux, self.pool.get('decimal.precision').precision_get(cr, uid, 'Montant Paie'))  
                    else :
                        taux = contract.employee_id.leaves_count * 1.0
                        montant_mensuel=rubrique['montant']*month_hours
               
                gain = montant * taux
                if not rubrique['cotisable']:
                    exoneration_cotisable+= gain 
                

                #Documeny utilisé : docs/calcul_cnss_irpp.ods
                if not rubrique['imposable']:
                    # salaire_brute_imposable += montant 
                    if rubrique['cotisable'] :
                        exoneration_irpp += (gain*(1-0.0918))#TODO: get taux from params
                        
                    else :
                        exoneration_irpp += gain
                 
                mnt_rubriques += gain
                if rubrique['type'] == 'prime':
                        prime += gain
                elif rubrique['type'] == 'indemnite':
                        indemnite += gain
                elif rubrique['type'] == 'avantage':
                        avantage += gain
                montant_indemnite+=montant_mensuel
        print '---------------------------montant_mensuel----------------------------------------------------', montant_indemnite                           
        #
        
        salaire_brute = salaire_base 
        trouve=False
        trouve2=False
        while(trouve == False):
            salaire_brute_imposable=0
            cotisations_employee=0
            for cot in cotisation.cotisation_ids :
                base = salaire_brute
                cotisations_employee += base * cot['tauxsalarial'] / 100
            salaire_brute_imposable = salaire_brute - cotisations_employee
            mnt_Impot=bulletin_obj.get_irpp(cr, uid, contract.employee_id.id, salaire_brute_imposable)
            if(mnt_Impot < 0):mnt_Impot = 0
            salaire_net=salaire_brute - cotisations_employee - mnt_Impot
            if(int(salaire_net)==int(salaire_base) and trouve2==False):
                trouve2=True
                salaire_brute-=1
            if not trouve2:
                if salaire_base- round(salaire_net,3) > 1000 : salaire_brute +=999
                elif salaire_base-round(salaire_net,3) > 500 : salaire_brute +=499
                elif salaire_base-round(salaire_net,3) > 200 : salaire_brute +=199
                elif salaire_base-round(salaire_net,3) > 100 : salaire_brute +=99
                elif salaire_base-round(salaire_net,3) > 10 : salaire_brute +=9
            if(round(salaire_net,3)==salaire_base):trouve=True
            elif trouve2==False : salaire_brute+=0.9
            elif trouve2==True : 
                if salaire_base- round(salaire_net,3) > 0.5 : salaire_brute +=0.5
                elif salaire_base- round(salaire_net,3) > 0.1 : salaire_brute +=0.1
                elif salaire_base- round(salaire_net,3) > 0.08 : salaire_brute +=0.08
                elif salaire_base- round(salaire_net,3) > 0.05 : salaire_brute +=0.05
                elif salaire_base- round(salaire_net,3) > 0.01 : salaire_brute +=0.01
                elif salaire_base- round(salaire_net,3) > 0.005 : salaire_brute +=0.005
                else : salaire_brute+=0.001

        self.write(cr, uid, [contract.id], {'wage' :salaire_brute ,'indemmnite_diff' :salaire_brute - contract.salaire_de_base - montant_indemnite })
        return True

 
hr_contract()
 
#-------------------------------------------------------------------------------
# hr_holidays_status
#-------------------------------------------------------------------------------
class hr_holidays_status(osv.osv):
    _inherit = "hr.holidays.status"
    _description = 'Holidays'
    _columns = { 'payed':fields.boolean(u'Payé?') }
    _defaults = {'payed': lambda * args: True }
hr_holidays_status()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

class hr_holidays(osv.osv):
    _inherit = "hr.holidays"
    
    _columns = { 'matricule':fields.char('Matricule'), 
                'date': fields.date('Date'),
                'description':fields.text('description'),
                'yeaar': fields.char('Année'),
                }
   
    
    _defaults = {
                 'date': fields.date.context_today,
                 'yeaar' : datetime.now().year,
                 }
    
    
    def onchange_employee(self, cr, uid, ids, employee_id, context=None):
        res = super(hr_holidays, self).onchange_employee(cr, uid, ids, employee_id)
        employee=self.pool.get('hr.employee').browse(cr,uid,employee_id,context)
        res['value'].update({ 'matricule':employee.matricule})
        return res
            
            
hr_holidays()
