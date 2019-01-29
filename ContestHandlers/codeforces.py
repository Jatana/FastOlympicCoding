import urllib
import urllib.request
import re

		
test_start_input = '<div class="input"><div class="title">Input</div><pre>'
test_start_output = '<div class="output"><div class="title">Output</div><pre>'
test_end = '</pre></div>'

def try_load_tests(contest_id, task_id):
	url = 'https://codeforces.com/contest/{contest_id}/problem/{task_id}'.format(
		contest_id=contest_id,
		task_id=chr(ord('A') + task_id)
	)
	req = urllib.request.urlopen(url)
	text = req.read().decode()
	inputs = []
	outputs = []
	for i in range(len(text)):
		if text[i:i + len(test_start_input)] == test_start_input:
			for j in range(i, len(text)):
				if text[j:j + len(test_end)] == test_end:
					inputs.append(text[i + len(test_start_input):j].replace('<br />', '\n').strip())
					break
		if text[i:i + len(test_start_output)] == test_start_output:
			for j in range(i, len(text)):
				if text[j:j + len(test_end)] == test_end:
					outputs.append(text[i + len(test_start_output):j].replace('<br />', '\n').strip())
					break

	if (len(inputs) != len(outputs)) or (not inputs): return None, None
	return inputs, outputs


contest_name_start = '<div style="padding: 4px 0 0 6px;font-size:1.4rem;position:relative;">'
contest_name_end = '<div style="position:absolute;right:0.25em;top:0.35em;">'

def get_contest_info(contest_id):
	url = 'https://codeforces.com/contests/' + str(contest_id)
	req = urllib.request.urlopen(url)
	text = req.read().decode()
	title = text[text.find(contest_name_start) + len(contest_name_start):text.find(contest_name_end)].strip()
	return {
		'title': title
	}

def get_basename():
	return 'CodeForces'

def is_valid_url(url):
	return url.find('codeforces.com') != -1

def extract_contest_id(url):
	match = re.search(r'\d+', url)
	return match.group(0)

print(extract_contest_id('https://codeforces.com/contest/1078/problem/A'))