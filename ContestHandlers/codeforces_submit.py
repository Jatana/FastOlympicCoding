import sys
import requests
import random
import string
from bs4 import BeautifulSoup

def genBfaa():
	return 'f1b3f18c715565b589b7823cda7448ce'

def randomString(len):
	return ''.join([random.choice(string.ascii_letters + string.digits) for n in range(len)])

def genFtaa():
	return randomString(18)

def getCsrf(s, url):
	page = s.get(url)
	soup = BeautifulSoup(page.content, 'html.parser')
	tag = soup.find('meta', {'name' : 'X-Csrf-Token'})
	csrf = tag['content']
	return csrf

def saveHTML(response, filename):
	with open(filename, 'w') as f:
		f.write(response.content.decode('utf-8'))

def logIn(s, user):
	csrf = getCsrf(s, 'https://codeforces.com/enter')
	s.ftaa = genFtaa()
	s.bfaa = genBfaa()
	data = {
		'csrf_token':    csrf,
		'action':        'enter',
		'ftaa':          s.ftaa,
		'bfaa':          s.bfaa,
		'handleOrEmail': user['username'],
		'password':      user['password'],
		'_tta':          '176',
		'remember':      'on'
	}
	response = s.post('https://codeforces.com/enter', data = data)
	# saveHTML(response, 'out.html')

def submit(s, contestID, problemID, langID, source):
	submitURL = 'https://codeforces.com/contest/{}/submit'.format(contestID)
	csrf = getCsrf(s, submitURL)
	data = {
		'csrf_token':            csrf,
		'ftaa':                  s.ftaa,
		'bfaa':                  s.bfaa,
		'action':                'submitSolutionFormSubmitted',
		'submittedProblemIndex': problemID,
		'programTypeId':         langID,
		'source':                source,
		'tabSize':               '4',
		'_tta':                  '594',
		'sourceCodeConfirmed':   'true'
	}
	response = s.post(submitURL, data = data)
	# saveHTML(response, 'submitted.html')

helpString = '''Print action id
0 - submit a code
1 - exit'''

def processSubmission(s):
	print('Print contest id (example: 1)')
	contestID = input()
	print('Print problemID (example: A)')
	problemID = input()
	print('Print langID (54 for C++17)')
	langID = input()
	print('Print source relative filename')
	filename = input()
	source = open(filename).read()
	submit(s, contestID, problemID, langID, source)
	print('Successfully submitted')

def loop(s):
	print(helpString)
	try:
		while (True):
			x = input()
			if (x == '0'):
				processSubmission(s)
			if (x == '1'):
				sys.exit()
	except KeyboardInterrupt:
		sys.exit()

def perform_submission(contestID, problemID, code, user):
	s = requests.Session()
	logIn(s, user)
	print('Logged in as', user['username'])
	submit(s, contestID, problemID, 54, code)
	# loop(s)

