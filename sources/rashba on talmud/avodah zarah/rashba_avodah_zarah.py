# -*- coding: utf-8 -*-
import urllib
import urllib2
from urllib2 import URLError, HTTPError
import json 
import pdb
import os
import sys
from bs4 import BeautifulSoup
import re
p = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, p)
sys.path.insert(0, '../../Match/')
from match import Match
os.environ['DJANGO_SETTINGS_MODULE'] = "sefaria.settings"
from local_settings import *

sys.path.insert(0, SEFARIA_PROJECT_PATH)
from sefaria.model import *
from sefaria.model.schema import AddressTalmud	

gematria = {}
gematria['א'] = 1
gematria['ב'] = 2
gematria['ג'] = 3
gematria['ד'] = 4
gematria['ה'] = 5
gematria['ו'] = 6
gematria['ז'] = 7
gematria['ח'] = 8
gematria['ט'] = 9
gematria['י'] = 10
gematria['כ'] = 20
gematria['ל'] = 30
gematria['מ'] = 40
gematria['נ'] = 50
gematria['ס'] = 60
gematria['ע'] = 70
gematria['פ'] = 80
gematria['צ'] = 90
gematria['ק'] = 100
gematria['ר'] = 200
gematria['ש'] = 300
gematria['ת'] = 400
def post_text(ref, text):
    textJSON = json.dumps(text)
    ref = ref.replace(" ", "_")
    url = SEFARIA_SERVER+'/api/texts/'+ref
    values = {'json': textJSON, 'apikey': API_KEY}
    data = urllib.urlencode(values)
    req = urllib2.Request(url, data)
    try:
        response = urllib2.urlopen(req)
        print response.read()
    except HTTPError, e:
        print 'Error code: ', e.code
        print e.read()
def get_text(ref):
    ref = ref.replace(" ", "_")
    url = 'http://www.sefaria.org/api/texts/'+ref
    req = urllib2.Request(url)
    try:
        response = urllib2.urlopen(req)
        data = json.load(response)
        for i, line in enumerate(data['he']):      
			data['he'][i] = data['he'][i].replace(u"\u05B0", "")
			data['he'][i] = data['he'][i].replace(u"\u05B1", "")
			data['he'][i] = data['he'][i].replace(u"\u05B2", "")
			data['he'][i] = data['he'][i].replace(u"\u05B3", "")
			data['he'][i] = data['he'][i].replace(u"\u05B4", "")
			data['he'][i] = data['he'][i].replace(u"\u05B5", "")
			data['he'][i] = data['he'][i].replace(u"\u05B6", "")
			data['he'][i] = data['he'][i].replace(u"\u05B7", "")
			data['he'][i] = data['he'][i].replace(u"\u05B8", "")
			data['he'][i] = data['he'][i].replace(u"\u05B9", "")
			data['he'][i] = data['he'][i].replace(u"\u05BB", "")
			data['he'][i] = data['he'][i].replace(u"\u05BC", "")
			data['he'][i] = data['he'][i].replace(u"\u05BD", "")
			data['he'][i] = data['he'][i].replace(u"\u05BF", "")
			data['he'][i] = data['he'][i].replace(u"\u05C1", "")
			data['he'][i] = data['he'][i].replace(u"\u05C2", "")
			data['he'][i] = data['he'][i].replace(u"\u05C3", "")
			data['he'][i] = data['he'][i].replace(u"\u05C4", "")
        return data['he']
    except:
        print 'Error'

def hasTags(comment):
	tag = re.compile('.*\d+.*')
	match = tag.match(comment)
	if match:
		return True

def gematriaFromTxt(txt):
	index=0
	sum=0
	while index <= len(txt)-1:
		if txt[index:index+2] in gematria:
			sum += gematria[txt[index:index+2]]
		index+=1
	return sum

def convertHebrewToNumber(daf):
	daf_num = gematriaFromTxt(daf.split(",")[0])
	amud_num = gematriaFromTxt(daf.split(",")[1])
	if amud_num == 1:
		daf = daf_num*2-1
	elif amud_num == 2:
		daf = daf_num*2
	return daf
	
def post_link(info):
	url = SEFARIA_SERVER+'/api/links/'
	infoJSON = json.dumps(info)
	values = {
		'json': infoJSON, 
		'apikey': API_KEY
	}
	data = urllib.urlencode(values)
	req = urllib2.Request(url, data)
	try:
		response = urllib2.urlopen(req)
		print response.read()
		
	except HTTPError, e:
		print 'Error code: ', e.code


title="R-7-"
title_option = 18
dh_dict = {}
comm_dict = {}
before_dh_dict = {}
for count_file in range(10):
	f = open(title+str(title_option+count_file)+".txt")
	for line in f:
		line=line.replace("\n","")
		if len(line)<4:
			continue
		line = line.replace("@04", "")
		if line.find("@20") >= 0:
			start = line.find("@20")
			end = max(line.find("@30"), line.find("@70"))
			if end == -1:
				print "@20 but not @30/70"
				pdb.set_trace()
			actual_start = line.find("[")
			actual_end = line.find("]")
			if actual_start > start and actual_end < end:
				before_dh = line[start+3:end].replace(line[actual_start:actual_end+1],"").replace("@40","")
				daf = line[actual_start:actual_end+1].replace("[","").replace("]","").replace(" ","")
			daf = convertHebrewToNumber(daf)
			if len(before_dh)>1:
			 if daf in comm_dict:
				before_dh_dict[(daf, len(comm_dict[daf]))] = before_dh
			 else:
				before_dh_dict[(daf, 0)] = before_dh
		if line.find("@30") >= 0 or line.find("@70") >= 0:
			start = max(line.find("@30"), line.find("@70"))
			end = line.rfind("@40")
			if end == -1:
				print "@30/70 but not @40"
				pdb.set_trace()
			dh = line[start+3:end]
			if daf not in dh_dict:
				dh_dict[daf] = []
			dh_dict[daf].append(dh)
			just_added_dh = True
		if line.rfind("@40") >= 0 and (line.find("@60") == -1 or line.find("@60") > 2):
			start = line.rfind("@40")
			end = max(line.find("@10"), line.find("@60"))
			if end == -1:
				print "@40 but no end tag"
				pdb.set_trace()
			comm = line[start+3:end]
			if daf not in dh_dict:
				print "comment without a daf"
				pdb.set_trace()
			if daf not in comm_dict:
				comm_dict[daf] = []
			comm_dict[daf].append(comm)
			if just_added_dh == False:
				dh_dict[daf].append("")
		elif line.find("@60") >= 0 and line.find("@60") < 2:
			start = line.find("@60")
			end = max(line.rfind("@60"), line.find("@10"))
			if end == -1:
				print "@60 but no end tag"
				pdb.set_trace()
			comm = line[start+3:end]
			if daf not in dh_dict:
				print "comment without a daf"
				pdb.set_trace()
			if daf not in comm_dict:
				comm_dict[daf] = []
			if just_added_dh == False:
				dh_dict[daf].append("")
			comm_dict[daf].append(comm)
		else:
			pdb.set_trace()
		if hasTags(comm) or hasTags(dh) or hasTags(before_dh):
			pdb.set_trace()
		before_dh = ""
		just_added_dh = False
result = {}
guess=0
no_guess=0
for daf in dh_dict.keys():
	if len(dh_dict[daf]) != len(comm_dict[daf]):
		pdb.set_trace()
for daf in dh_dict.keys():
	text = get_text("Avodah Zarah."+AddressTalmud.toStr("en", daf))
	try:
		match_obj=Match(in_order=True, min_ratio=70, guess=False, range=True, maxLine=len(text)-1)
	except:
		pdb.set_trace()
	dh_arr = []
	for i in range(len(dh_dict[daf])):
		if len(dh_dict[daf][i]) > 0:
			dh_arr.append(dh_dict[daf][i])
	result[daf] = match_obj.match_list(dh_arr, text)
	dh_count = 1
	'''
	if len(dh_dict[daf][i]) == 0, then comm_dict[daf][i] gets added to comm_dict[daf][i-1]+"<br>"
	'''
	for i in range(len(comm_dict[daf])):
		 if (daf, i) in before_dh_dict:
		 	comm_dict[daf][i] = before_dh_dict[(daf, i)]+"<b>"+dh_dict[daf][i]+"</b>"+comm_dict[daf][i]
		 else:
		 	comm_dict[daf][i] = "<b>"+dh_dict[daf][i]+"</b>"+comm_dict[daf][i]
	found = 0
	if len(dh_dict[daf][0]) == 0:
		pdb.set_trace()
	for i in range(len(dh_dict[daf])):
		if len(dh_dict[daf][i]) > 0:
			old_found = found
			found = i
			if found - old_found > 1:
				temp=""
		 		for j in range(found-old_found-1): 
		 			temp+="<br>"+comm_dict[daf][j+old_found+1]
		 		comm_dict[daf][old_found] += temp
	comments = []
	for i in range(len(comm_dict[daf])):
		if len(dh_dict[daf][i])>0:
			comments.append(comm_dict[daf][i])
	#NOW create new array skipping blank ones
	for i in range(len(comm_dict[daf])):
		 if len(dh_dict[daf][i]) > 0:
		 	line_n  = result[daf][dh_count]
		 	dh_count+=1 
		 	if line_n.find("0:")>=0:
		 		no_guess += 1
		 	line_n = line_n.replace("0:", "")
		 	guess+=1
			post_link({
					"refs": [
							"Avodah Zarah"+"."+AddressTalmud.toStr("en", daf)+"."+str(line_n), 
							"Rashba on Avodah Zarah."+AddressTalmud.toStr("en", daf)+"."+str(i+1)
						],
					"type": "commentary",
					"auto": True,
					"generated_by": "Rashba on Avodah Zarah linker",
				 })
	send_text = {
				"versionTitle": "Rashba on Avodah Zarah",
				"versionSource": "http://www.sefaria.org",
				"language": "he",
				"text": comments,
				}
	
	post_text("Rashba on Avodah Zarah."+AddressTalmud.toStr("en", daf), send_text)
	pdb.set_trace()


print float(guess)/float(guess+no_guess)
print no_guess