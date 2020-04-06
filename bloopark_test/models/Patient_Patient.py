# -*- coding: utf-8 -*-
from openerp import fields, models, api, exceptions, _
import re 
from datetime import date, datetime

genders = [('male','Male'),('female','female')]
_patient_states = [('new','Healthy'),('possible','Possible Sick'),('sick','Sick'),('recovered','Recovered')]

class Medical_History(models.Model):
	_name = 'medical.history'
	_order = 'create_date desc'

	patient_id = fields.Many2one('patient.patient',string="Patient")
	disease_id = fields.Many2one('disease.disease',string="Disease")
	action = fields.Char('Action')

# patient_patient is the patient's model 
class Patient_Patient(models.Model):
	_name = 'patient.patient'
	_order = 'write_date desc'
	#Basic fields
	name = fields.Char(string='Name')
	gender = fields.Selection(genders,string="Gender")
	birthDate = fields.Date('Birth day')
	age = fields.Integer('Age',compute="get_age")
	passport = fields.Char(string="Passport")
	image = fields.Binary('Patient Picture',help="Patient image")
	prediction_disease_console = fields.Html(string="Possibility diseases",readonly=True)
	patient_state = fields.Selection(_patient_states,string="State",default="new")
	#Relational fields
	symptoms_ids = fields.Many2many('disease.symptom',string="Initial Symptoms")
	disease_ids = fields.Many2many('disease.disease',string="Current diseases")
	medical_history_ids = fields.One2many('medical.history','patient_id',string="Medical history")
	treatment_ids = fields.Many2many('disease.treatment',string="Suggested treatments")
	#Helper variable fields
	possible_diseases_str = fields.Char('list')


	#this is for the run diagnosis button 
	@api.one
	@api.depends('symptoms_ids.ids')
	def compute_possible_diseases(self):
		div = """<ul style="color:red;">"""
		rules = self.env['rule.detection'].search([])
		possible_diseases = {}
		possible_diseases_ids = []
		#To improve using threads later
		for rule in rules:
			if rule.symptoms:
				ratio_rule = 100/len(rule.symptoms.ids) 
				commun_sympt = [x for x in self.symptoms_ids.ids if x in rule.symptoms.ids] 
				commun_sympt_pourcentage = ratio_rule * len(commun_sympt)
				#qualifying list of symptoms that are matching over 50% of the disease symptoms
				if commun_sympt_pourcentage >= 50:
					if rule.disease_id:
						possible_diseases_ids.append(rule.disease_id.id)
						possible_diseases.update({rule.disease_id.name:commun_sympt_pourcentage}) 
					else:
						raise exceptions.except_orm(_(u'Sir Mr '+self.env.user.name), _(u'Please specifiy the diseases in your rule of detection database -_-.' ))
		innerHtml =""				
		if len(possible_diseases) > 0:
			for d in possible_diseases:
				innerHtml += "<li>"+ str(possible_diseases[d]) +"% "+"""<a target="_blank" href="https://www.google.com/search?q=""" +d+""" "> """+ d+"</a>"+"</li>"
		if innerHtml=="":
			innerHtml = "No possible diseases!"
			self.patient_state = "new"
		else:
			self.patient_state = "possible"
		self.prediction_disease_console= div + innerHtml + """</ul>"""
		#passing the list of possible diseases through possible_diseases_str
		self.possible_diseases_str = str(possible_diseases_ids)
		
		
				
	
	
	#calculate the age
	@api.depends('birthDate')
	def get_age(self):
		today = date.today()
		if self.birthDate:
			#convert string date to a date object
			match = re.search(r'\d{4}-\d{2}-\d{2}', self.birthDate)
			born = datetime.strptime(match.group(), '%Y-%m-%d').date()
			if born:
				self.age = today.year - born.year - ((today.month, today.day) < (born.month, born.day))

	#basically deleted list = old ids - new ids
	# and added list = new ids -  
	@api.one
	def get_updated_diseases(self,new_disease_vals):
		#new_disease_vals is gonna be something like this [[6, False, [2]]]
		added_diseases, deleted_diseases = [], []
		if self.disease_ids:
			old_ids= self.disease_ids.ids
			#new_disease_vals[0] = [6, False, [2]] and new_disease_vals[0][2] = [2]
			# wich is the [ids] that we're looking for
			new_ids = new_disease_vals[0][2]
			deleted_diseases =  list(set(old_ids)-set(new_ids))
			added_diseases =  list(set(new_ids)-set(old_ids))
			if new_ids == []:# this means if all diseases are cleared than means the patient recovered
				self.patient_state = "recovered"
		else:
			#this is when adding disease for the first time
			added_diseases =  new_disease_vals[0][2]
			self.patient_state = "sick"

		return added_diseases, deleted_diseases

	@api.one
	def create_medical_history(self,added_diseases, deleted_diseases):
		medical_history_obj = self.env['medical.history']
		#handle added
		for add_id in added_diseases:
			action = "is sick with"
			medical_history_obj.create({'patient_id':self.id,'action':action,'disease_id':add_id})
		#handle deleted
		for del_id in deleted_diseases:
			action = "Recovered from"
			medical_history_obj.create({'patient_id':self.id,'action':action,'disease_id':del_id})

	#for the button to confirm inserted diseases
	@api.one
	def confirm_diseases(self):
		if self.disease_ids:	
			if self.patient_state!="sick":
				self.create_medical_history(self.disease_ids.ids, [])
				return self.write({'patient_state':"sick"})
			else:
				return True
		else:
			raise exceptions.except_orm(_(u'Integrity Error'), _(u'Please select at least one disease to confirm!' ))
	#for the button confirm diagnosis
	@api.one
	def confirm_diagnosis(self):
		import json 
		#this is how you convert string list form "[1, 2, 3]" to a list [1, 2, 3]
		ids = json.loads(self.possible_diseases_str)
		self.disease_ids = [[6,0,ids]]
		return True

	@api.one
	def compute_treatments(self):
		rules = self.env['rule.treatment'].search([('disease_id','in',self.disease_ids.ids)])
		treatments_ids = []
		#To improve using threads later
		for rule in rules:
			if rule.treatments and rule.disease_id:
				treatments_ids+=rule.treatments.ids
		treatments_ids = list(dict.fromkeys(treatments_ids))
		self.treatment_ids = [[6,0,treatments_ids]]
		return True
	#this function to clear patient medical history
	@api.one
	def clear_patient_medical_history(self):
		for history in self.medical_history_ids:
			history.unlink()
		return True

	@api.multi
	def write(self,vals):
		#handling diseases updates
		if 'disease_ids' in vals :
			for rec in self :
				#getting list of ids that been added or removed from diseases list of this patient
				added_diseases, deleted_diseases = rec.get_updated_diseases(vals['disease_ids'])[0]
				if rec.patient_state in ("sick","recovered") :
					rec.create_medical_history(added_diseases, deleted_diseases)				
		return super(Patient_Patient,self).write(vals)