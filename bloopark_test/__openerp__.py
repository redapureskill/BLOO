# -*- coding: utf-8 -*-
##############################################################################
#

#
##############################################################################

{
    'name': 'BlooPark Test',
    'version': '1.0',
    'category': 'Tests',
 
 
    'description': """
 
==================================

This application allows you to manage diseases and patients.
Calculate the possibility of having a specific disease foreach patients based on his list of symptoms.
When the database is fully well set (especially rules), it can be used as a knowledge base, that means everyone 
can use it to know the symptoms of each disease and can get a good instant diagnosis and treatments about each patient created.
---------------------------------------------------------------------
    This idea can be extended but since we had only 10 days i couldn't do more.
    """,
    'summary':"""
   
**Email:** mireda2012@gmail.com""",
    'author': 'mireda2012@gmail.com',
 
    'depends': [],
    'data': ['views/Rule_Rule.xml','views/Disease_Disease.xml','views/Patient_Patient.xml','views/data.xml'
            ],
    'demo': [ ],
    'test': [ 
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
# 
