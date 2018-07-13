#!/usr/bin/python

import sys
from getpass import getpass
import requests
import constants
import json
import uuid
import os
import encryptionlib
import urllib

access_keys = {}
def signupFlow():
	while True:
		try:
			email = raw_input("Great! Enter your Email ID: ")
			password = getpass("Enter a secure password: ")
			payload = 'email='+email+'&password='+password
			requests.request('POST',constants.DATANCHOR_ENDPOINT+'/AppUsers',data=payload, headers = {'Content-Type': "application/x-www-form-urlencoded"})
			print "Sign up successful"
			print "-------------------"
			loginFlow()
			break
		except Exception as e:
			print e
			continue

def loginFlow():
	try:
		email = raw_input("Great! Enter your Email ID: ")
		password = getpass("Enter a secure password: ")
		payload = 'email='+email+'&password='+password #We can mention a ttl on the access_token received here
		loginResponse = requests.request('POST',constants.DATANCHOR_ENDPOINT+'/AppUsers/login',data=payload, headers = {'Content-Type': "application/x-www-form-urlencoded"})
		print "Sign in successful"
		print "-------------------"
		global access_keys
		access_keys = loginResponse.json()
		with open('settings_config.json', 'w') as f:
			json.dump(loginResponse.json(),f)
	except Exception as e:
		print e

def getAccessKey():
	global access_keys
	try:
		if os.path.exists('./settings_config.json'):
			with open('./settings_config.json') as f:
				data = json.load(f)
			access_keys = data
		else:
			displayMenu()
	except Exception as e:
		print e
		displayMenu()

def saveLogs():
	try:
		global access_keys
		logsResponse = requests.request('GET',constants.DATANCHOR_ENDPOINT+'/AppUsers/me/AccessLogs/',params={"access_token":access_keys['access_token']})
		with open('access_log.log', 'w') as f:
			json.dump(logsResponse.json(),f)
	except Exception as e:
		print e
		loginFlow()	

def encryptFile(fileName):
	global access_keys
	dataKeyResponse = ""
	getAccessKey()
	while True:
		try:
			dataKeyResponse = requests.request('POST',constants.DATANCHOR_ENDPOINT+'/Datakeys/',data="id="+urllib.quote(fileName),params={"access_token":access_keys['access_token'],"masterKey":access_keys['masterKey']['id']},headers={'Content-Type': "application/x-www-form-urlencoded"})
			break
		except Exception as e:
			print e
			displayMenu()
			continue
	try:
		decryptedDataKey =  dataKeyResponse.json()['access_token']
		encryptionlib.encrypt_file(fileName, decryptedDataKey)
		saveLogs()
	except Exception as e:
		print 'Enter a unique file name. Key already exists'
	os.remove(fileName)

def decryptFile(fileName):
	global access_keys
	getAccessKey()
	while True:
		try:
			dataKeyResponse = requests.request('GET',constants.DATANCHOR_ENDPOINT+'/Datakeys/'+urllib.quote_plus(fileName),params={"access_token":access_keys['access_token'],"masterKey":access_keys['masterKey']['id']})
			break
		except Exception as e:
			print e
			displayMenu()
			continue
	try:
		decryptedDataKey =  dataKeyResponse.json()['access_token']
		encryptionlib.decrypt_file(fileName+'.enc', decryptedDataKey)
		saveLogs()
	except Exception as e:
		print e		

def displayMenu():
	newUser = raw_input("Do you have an account with Datanchor? (Y/n)")
	if newUser.lower() == 'n' or newUser.lower() == 'no':
		signupFlow()
	else:
		loginFlow()
