# -*- coding: utf-8 -*-
from openerp import fields, models


#this class defines the symptoms that can exist
class Disease_Symptom(models.Model):
	_name = "disease.symptom"

	name = fields.Char("Name")
	characteristics = fields.Text("Characteristics")

#this class defines the treatment that can exist
class Disease_Treatment(models.Model):
	_name = "disease.treatment"

	name = fields.Char('Name')
	description = fields.Text('Description')

#this class defines the disease with its symptoms and treatments if they exist
class Disease_Disease(models.Model):
	_name = "disease.disease"

	#Basic fields
	name = fields.Char('Name')
	technical_name = fields.Char('Scientific name')
	contagious = fields.Boolean('Contagious',help="Check, if the disease is contagious!")
	pandemic = fields.Boolean('Pandamic',help="Check, if the disease is pandemic!")
	