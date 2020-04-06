# -*- coding: utf-8 -*-
from openerp import fields, models, api

# Rule_Rule is the rule's model 
#(PS: we dont need to create a table for this one, to avoid database increase)
class Rule_Rule(models.Model):
	_name = 'rule.rule'
	_auto = False
	
	
	#Relational fields
	disease_id = fields.Many2one('disease.disease',"Disease")
 

#Detection_Rule is the model class of all rules with type = 'detect'
#in one rule  [1..n]Symptoms -Lead to-> 1 Disease 
class Detection_Rule(Rule_Rule):
	_name = 'rule.detection'
	_auto = True 

	#Basic fields
	name = fields.Char('Name',compute="get_name")
	#Relational fields
	symptoms = fields.Many2many('disease.symptom',string="Symptoms List")

	@api.multi
	def get_name(self):
		for rec in self:
			symptoms_text = "[ "
			for symptom in rec.symptoms:
				symptoms_text+= symptom.name+", "
			symptoms_text=symptoms_text[:-2]+" ]"
			rec.name =  symptoms_text+ " --Causes---> [ "+(rec.disease_id.name or "") +" ]" 
#Detection_Rule is the model class of all rules with type = 'detect'
# in one rule [1..n]Treatments -Treat-> 1 Disease 
class Treatment_Rule(Rule_Rule):
	_name = 'rule.treatment'
	_auto = True

	#Basic fields
	name = fields.Char('Name',compute="get_name")
	#Relational fields
	treatments = fields.Many2many('disease.treatment',string="Treatments List")

	@api.multi
	def get_name(self):
		for rec in self:
			treats_text = "[ "
			for treat in rec.treatments:
				treats_text+= treat.name+", "
			treats_text= treats_text[:-2]+" ]"
			rec.name =  treats_text+ " --Teats---> [ "+(rec.disease_id.name or "") +" ]" 