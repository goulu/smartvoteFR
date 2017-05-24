#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
création de "smartmaps" politiques sur le modèle de smartvote.ch avec données de l'Assemblée Nationale Française Edit

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

import logging

import xml.etree.ElementTree as ET
from collections import OrderedDict
from Goulib.table import Table # like a pandas.dataFrame, but simpler ...

        
# build a dictionary of "organes" and their members deputies (="acteurs")
tree = ET.parse('AMO10_deputes_actifs_mandats_actifs_organes_XIV.xml')

organes={}

root=tree.getroot()
nodes=root.find('organes')
for node in nodes:
    uid=node.find('uid').text
    organes[uid]=[]
    
acteurs={}
        
for node in root.findall('acteurs/acteur'):
    uid=node.find('uid').text
    ident=node.find('etatCivil/ident')
    nom=ident.find('prenom').text+' '+ident.find('nom').text
    acteurs[uid]=nom
    for m in node.findall('mandats/mandat'):
        for o in m.find('organes'):
            ref=o.text
            organes[ref].append(uid)
    
# parse the votes and build table

res=Table()
        
tree = ET.parse('Scrutins_XIV.xml')
root=tree.getroot()
for scrutin in root:
    line=OrderedDict() # so that id,date and title stay in the first cols
    line['id']=scrutin.find('uid').text
    line['date']=scrutin.find('dateScrutin').text
    line['titre']=scrutin.find('titre').text
    
    groupes=scrutin.find('ventilationVotes/organe/groupes')
    for groupe in groupes:
        ref=groupe.find('organeRef').text
        pm=groupe.find('vote/positionMajoritaire').text
        votes=['contre','abstention','pour']
        default=votes.index(pm)-1 # against=-1, no vote=0
        
        # first we consider all members of the group voted as default:
        for actor in organes[ref]:
            line[acteurs[actor]]=default
            
        # then remove those who didn't vote:
        for votant in groupe.find('vote/decompteNominatif/nonVotants'):
            ref=votant.find('acteurRef').text
            try:    
                del line[acteurs[ref]]
            except KeyError:
                pass # already deleted (in a different group)
        
        # and modify those who voted differently:
        for i,vote in enumerate(votes):
            for votant in groupe.find('vote/decompteNominatif/%ss'%vote):
                ref=votant.find('acteurRef').text
                try:
                    line[acteurs[ref]]=i-1
                    print(acteurs[ref],'voted',vote)
                except KeyError:
                    logging.error("actor ref %s doesn't exist"%ref)
            
    res.append(line)
            
res.save('votes.csv',encoding='iso-8859-15')
