# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
#
#    Copyright (C) 2014  .
#    Coded by: Borni DHIFI  (dhifi.borni@gmail.com)
#
#----------------------------------------------------------------------------
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
from tempfile import TemporaryFile
import base64
import openerp.addons.decimal_precision as dp

LEN_MATR_EMPLOYEUR = 8
LEN_CLE_EMPLOYEUR = 2
LEN_CODE_EXPLOITATION = 4
LEN_TRIMESTRE=1
LEN_ANNEE=4
LEN_NUM_PAGE=3
LEN_NUM_LIGNE=2
LEN_MAT_ASSURE=8
LEN_CLE_ASSURE=2
LEN_IDENTITE_ASSURE=60
LEN_CARTE_IDENTITE=8
LEN_SALAIRE=10
LEN_ZONE_VIERGE=10
    
class wizard_declaration_cnss(models.Model):
    _name = 'payroll.report.declaration_cnss' 
    _description = u'Déclaration CNSS '
        
    TRIMESTER = [
            ('1', u'1er trimestre'),
            ('2', u'2e trimestre'),
            ('3', u'3e trimestre'),
            ('4', u'4e trimestre'),
            ]
    STATE = [
            ('choose', 'choose'),
            ('get', 'get'),
            ]

    SELECTION_STATE = [
            ('draft', 'Brouillon'),
            ('confirmed', u'Confirmé')
            ]
  
    @api.multi
    def action_cancel_draft(self):
        return self.write({'state': 'draft'})
        
    @api.multi
    def action_confirm(self):
        return self.write({'state': 'confirmed'})
     
    @api.model
    def _default_fiscalyear_id(self):
        return self.env['account.fiscalyear'].find()
    
    @api.model
    def _default_company(self):
        return  self.env.user.company_id
    
    @api.multi
    def onchange_trimester_period(self,trimester, period):
        fiscalyear = self.env['account.fiscalyear'].browse(period)
        count=self.search_count([('trimester','=',trimester)] )
        if count > 0 :
            warning = {'title':'Attention', 'message':_(u'La déclaration CNSS doit être unique par société et par trimestre!')}
            value = {'period_id': False,'month_id':False}
            return {'warning': warning, 'value': value}        
        return {'value': {'name' :   _(u"Déclaration CNSS %s du trimestre %s de l'année %s") % (self.env.user.company_id.name, trimester, fiscalyear.name)}}
    
    def generate_cnss(self,cr,uid,ids,context=None):
        datas = self.browse(cr, uid, ids[0], context)
        company_id=datas.company_id
        fiscalyear_id=datas.fiscalyear_id.id
        trimester=datas.trimester
        all_lines = self._get_lines(cr,uid,company_id,fiscalyear_id,trimester)
        line= []
        sql = '''   DELETE from payroll_report_declaration_cnss_line where declaration_line_id = %s '''
        cr.execute(sql, (datas.id,))
        for line_cnss in all_lines:
            #if line_cnss['cnss'] and float(line_cnss['total']or 0.0)+float(line_cnss['totals']or 0.0):
                print '-----------------------------line_cnss----------------------',line_cnss
                val=(0, 0,{ 
                                               'num_ordre' : line_cnss['num_line'],
                                               'employee_id':line_cnss['id'],
                                               'num_page': line_cnss['num_page'],
                                               'num_line': line_cnss['num_line'],
                                               'matricule_cnss': line_cnss['cnss'],
                                                'cin': line_cnss['cin'],
                                                'remuneration_1': float(line_cnss['mois1']or 0.0) ,
                                                'remuneration_2': float(line_cnss['mois2']or 0.0) ,
                                                'remuneration_3': float(line_cnss['mois3']or 0.0) ,
                                                'declaration_line_id': datas.id
                                            }) 
                line.append(val)
                     
        value = {  'line_ids': line}   
        self.write(cr, uid, datas.id, value, context=context)   
        return  True
    
    
    name= fields.Char(string='Nom', readonly=True, states={'draft': [('readonly', False)]})
    date= fields.Date(string='Date', default=fields.Date.context_today , readonly=True, states={'draft': [('readonly', False)]})
    file_name= fields.Char('Nom fichier')
    fiscalyear_id=fields.Many2one('account.fiscalyear', 'Exercice fiscal' , required=1,default=_default_fiscalyear_id, readonly=True, states={'draft': [('readonly', False)]})
    company_id=fields.Many2one('res.company', u'Société', required=1,default=_default_company, readonly=True, states={'draft': [('readonly', False)]})
    trimester=fields.Selection(TRIMESTER,string='Trimestre',   required=1,default=TRIMESTER[1], readonly=True, states={'draft': [('readonly', False)]})
    data= fields.Binary(string='Fichier CNSS', readonly=1, help="Fichier de la déclaration de salaires sur support magnétique")
    line_ids= fields.One2many('payroll.report.declaration_cnss.line','declaration_line_id',  string='Declaration CNSS', readonly=True, states={'draft': [('readonly', False)]})
    state = fields.Selection(SELECTION_STATE, string='Status', default='draft')
        
    def print_report(self, cr, uid, ids, context=None):
        datas = {'ids': []}
        datas['model'] = 'wizard_declaration_cnss'
        datas['form'] = self.read(cr, uid, ids, context=context)[0] 
        context['landscape']=True
        return self.pool['report'].get_action(cr, uid, [], 'devplus_hr_payroll_tn.report_declaration_cnss', data=datas, context=context)
 
    def print_report_recapitulatif(self, cr, uid, ids, context=None):
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'wizard_declaration_cnss'
        datas['form'] = self.read(cr, uid, ids, context=context)[0]
        return self.pool['report'].get_action(cr, uid, [], 'devplus_hr_payroll_tn.report_recapitulatif_cnss', data=datas, context=context)
    
    def _get_lines(self, cr, uid, company_id,fiscalyear_id,trimester):
        period_ids=self.pool.get('account.period').search(cr, uid,[('fiscalyear_id','=',fiscalyear_id)])
        
        # if existe periode ouverture period_ids=13 else period_ids=12
        if period_ids==12 :
            if trimester =='1' : 
                mois1=period_ids[0]
                mois2=period_ids[1]
                mois3=period_ids[2]
            elif trimester =='2' : 
                mois1=period_ids[3]
                mois2=period_ids[4]
                mois3=period_ids[5]           
            elif trimester =='3' : 
                mois1=period_ids[6]
                mois2=period_ids[7]
                mois3=period_ids[8]             
            else : 
                mois1=period_ids[9]
                mois2=period_ids[10]
                mois3=period_ids[11]  
        else :
            if trimester =='1' : 
                mois1=period_ids[1]
                mois2=period_ids[2]
                mois3=period_ids[3]
            elif trimester =='2' : 
                mois1=period_ids[4]
                mois2=period_ids[5]
                mois3=period_ids[6]           
            elif trimester =='3' : 
                mois1=period_ids[7]
                mois2=period_ids[8]
                mois3=period_ids[9]             
            else : 
                mois1=period_ids[10]
                mois2=period_ids[11]
                mois3=period_ids[12]            
           
        
                
        sql = '''
               SELECT e.id ,e.matricule,e.cnss,SUBSTRING(r.name, 0, 60) as name,e.cin,
          
             ( select  b1.salaire_brute_cotisable  from hr_payroll_bulletin  b1 where
               b1.period_id = %s and b1.employee_id=e.id 
                ) as mois1,

    
             ( select  b2.salaire_brute_cotisable  from hr_payroll_bulletin  b2  where
               b2.period_id = %s and b2.employee_id=e.id 
                ) as mois2,

                    
             ( select  b3.salaire_brute_cotisable  from hr_payroll_bulletin  b3 where
               b3.period_id = %s and b3.employee_id=e.id
                ) as mois3 ,
   
            (select  sum(b4.salaire_brute_cotisable)  from hr_payroll_bulletin  b4 where
               b4.period_id  in(%s,%s,%s)  and b4.employee_id=e.id ) as total
            
            
            From  hr_employee e         
            LEFT JOIN resource_resource r on (r.id=e.resource_id)
             where (select count(*) from hr_contract hc where  hc.employee_id=e.id)>0
             ORDER BY e.matricule
            ''' % (mois1, mois2, mois3, mois1, mois2, mois3)
        
        
        cr.execute(sql)
        declaration_cnss = cr.dictfetchall()
        
        num_page=1
        num_line=1
        resultats=[]
        for declaration in declaration_cnss:
            if declaration['cnss'] and float(declaration['total'] or 0.0):
                declaration.update({'num_page':num_page,'num_line':num_line})
                if num_line == 12 :
                    num_page += 1
                    num_line =1
                else :
                    num_line += 1

                resultats.append(declaration)
        return resultats


    def generate_file(self, cr, uid, ids, context=None):
        datas = self.read(cr, uid, ids, context=context)[0]
        this = self.browse(cr, uid, ids)[0]
        company_id=datas['company_id'][0]
        fiscalyear_id=datas['fiscalyear_id'][0]
        trimester=datas['trimester']
        fiscalyear = self.pool.get('account.fiscalyear').browse(cr,uid,fiscalyear_id,context)
        company = self.pool.get('res.company').browse(cr,uid,company_id,context)
        fp = TemporaryFile()        
         
        #cnss employeur
        cnss_employeur=company.cnss
        if not cnss_employeur:
            raise except_orm(_('Attention!'), _(u"Veuillez remplir le CNSS de la société dans la fiche du société"))   
        cnss_employeur=cnss_employeur.split('-')
        if  len(cnss_employeur) != 2  : 
            raise except_orm(_('Attention!'), _(u"Format CNSS de la société est incorrecte : xxxxxxxx-yy "))    
        if not company.code_exploitation : 
            raise except_orm(_('Attention!'), _(u"Veuillez remplir le Code d'exploitation de la société dans la fiche du société"))   



                      
        cle_employeur='00'
        if len(cnss_employeur)==2:
            matricule_employeur=cnss_employeur[0]
            #matricule_employeur= matricule_employeur.rjust(LEN_MATR_EMPLOYEUR,'0')
            #cle_employeur=cnss_employeur[1]
            cle_employeur = cnss_employeur[1]
        matricule_employeur= (matricule_employeur[0:LEN_MATR_EMPLOYEUR]).rjust(LEN_MATR_EMPLOYEUR,'0')
        cle_employeur= (cle_employeur[0:LEN_CLE_EMPLOYEUR]).ljust(LEN_CLE_EMPLOYEUR,'0')
        if company.code_exploitation : 
            code_exploitation= company.code_exploitation
        code_exploitation=((code_exploitation)[0:LEN_CODE_EXPLOITATION]).ljust(LEN_CODE_EXPLOITATION,'0')
        trimester=trimester.ljust(LEN_TRIMESTRE)
        annee=((fiscalyear.code)[0:LEN_ANNEE]).ljust(LEN_ANNEE)
        #get all line
        all_lines=self._get_lines(cr,uid,company_id,fiscalyear_id,trimester)
        file_dec=''
        for line_cnss in all_lines:
            #controle
            if line_cnss['cnss']:
                if not line_cnss['cin']:
                    raise except_orm(_('Attention!'), _(u"Veuillez remplir le CIN de l'employé %s"%line_cnss['name']))
                num_page=line_cnss['num_page']  
                num_page=str(num_page).zfill(LEN_NUM_PAGE)   
                num_line=line_cnss['num_line'] 
                num_line=str(num_line).zfill(LEN_NUM_LIGNE)  
                #cnss employee
                matricule_employee='00000000'
                cle_employee='00'
                cnss= line_cnss['cnss']
                cnss=cnss.split('-')
                if len(cnss)==2:
                    matricule_employee=cnss[0]
                    cle_employee=cnss[1]
                matricule_employee= (matricule_employee[0:LEN_MAT_ASSURE]).ljust(LEN_MAT_ASSURE,'0')
                cle_employee= (cle_employee[0:LEN_CLE_ASSURE]).ljust(LEN_CLE_ASSURE,'0')
                identite_assure=line_cnss['name'].upper()
                identite_assure=identite_assure.ljust(LEN_IDENTITE_ASSURE)
                cin=line_cnss['cin']
                cin=(cin[0:LEN_CARTE_IDENTITE]).ljust(LEN_CARTE_IDENTITE,'0')
                salaire=str('%.3f' % round(line_cnss['total'],3)).replace('.','').replace(',','')
                salaire=str(salaire).zfill(LEN_SALAIRE)   
                zone_vierge=''.ljust(LEN_ZONE_VIERGE)
                
                file_dec+=str(matricule_employeur)+str(cle_employeur)+str(code_exploitation)+str(trimester)+str(annee) + \
                     str(num_page)+str(num_line)+str(matricule_employee)+str(cle_employee)+str(identite_assure)+str(cin)+str(salaire)+str(zone_vierge) \
                     +'\n'
                 
        file_dec=file_dec[0:len(file_dec)-1]
        fp.write(str(file_dec))
        fp.seek(0)
        fp_name= 'DS'+str(matricule_employeur)+str(cle_employeur)+str(code_exploitation)+'.'+str(trimester)+str(annee)+'.txt'
        self.write(cr, uid, ids, {
                                  'data': base64.encodestring(fp.read()),
                                  'file_name':fp_name}, context=context)
        fp.close()  
        return True     

class payroll_report_declaration_cnss_line(models.Model):
    _name = 'payroll.report.declaration_cnss.line' 

    @api.one
    @api.depends('remuneration_1', 'remuneration_2', 'remuneration_3')
    def _compute_total(self):
        self.total = self.remuneration_1 +self.remuneration_2 + self.remuneration_3 
        return True 
                           

    employee_id=fields.Many2one('hr.employee',string='Employés')
    num_ordre=fields.Integer(string=u'Numéro Ordre')
    num_page=fields.Integer(string=u'Numéro Page')
    num_line=fields.Integer(string=u'Numéro Ligne')
    matricule_cnss=fields.Char(related='employee_id.cnss',string='Matricule')
    cin=fields.Char(related='employee_id.cin',string='CIN')
    remuneration_1= fields.Float(string=u'1er mois',digits=dp.get_precision('Montant Paie'))
    remuneration_2= fields.Float(string=u'2éme mois',digits=dp.get_precision('Montant Paie'))
    remuneration_3= fields.Float(string=u'3éme mois',digits=dp.get_precision('Montant Paie'))
    total= fields.Float(string=u'Total Général',compute='_compute_total',digits=dp.get_precision('Montant Paie'))
    declaration_line_id=fields.Many2one('payroll.report.declaration_cnss', string='Declaration de trimestre')
