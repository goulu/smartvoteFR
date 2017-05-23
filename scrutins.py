#!/usr/bin/env python
# coding: utf8
"""
création de "smartmaps" politiques sur le modèle de smartvote.ch avec données de l'Assemble Nationale Française Edit

reads data from http://data.assemblee-nationale.fr/acteurs/deputes-en-exercice
and http://data.assemblee-nationale.fr/travaux-parlementaires/votes
to create a table of who voted what
"""

__author__ = "Philippe Guglielmetti"
__copyright__ = "Copyright 2017, Philippe Guglielmetti"
__credits__ = [
    "https://www.drgoulu.com/2017/05/14/la-politique-francaise-dans-la-deuxieme-dimension/#comment-3320769433",
    ]
__license__ = "LGPL"

import xml.etree.ElementTree as ET
        
# build a dictionary of "organes" and their members deputies (="acteurs")
tree = ET.parse('AMO10_deputes_actifs_mandats_actifs_organes_XIV.xml')

organes={}

root=tree.getroot()
nodes=root.find('organes')
for node in nodes:
    uid=node.find('uid').text
    organes[uid]=[]
    
acteurs={}
        
nodes=root.find('acteurs')
for node in nodes:
    uid=node.find('uid').text
    ident=node.find('etatCivil').find('ident')
    nom=ident.find('prenom').text+' '+ident.find('nom').text
    acteurs[uid]=nom
    for m in node.find('mandats'):
        for o in m.find('organes'):
            ref=o.text
            organes[ref].append(uid)
   
print(acteurs)  
for o in organes:   
    print(o,organes[o])
    
# parse the votes
        
tree = ET.parse('Scrutins_XIV.xml')
root=tree.getroot()
for scrutin in root:
    print(scrutin.find('titre').text)