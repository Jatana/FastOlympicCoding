from os import path


base_dir = path.split(__file__)[0]

def modify_classes(classes):
	new_classes = {}
	for key in classes:
		new_classes[classes[key].get('bind', key[0])] = classes[key]
		new_classes[classes[key].get('bind', key[0])]['name'] = key
	return new_classes

def create(s, i, config, classes):
	if i >= len(s):
		return None, i, ''

	c = s[i]

	if not c in classes.keys():
		return None, i, ''

	template_size = classes[c]['template_size']
	name = classes[c]['name']
	childs = []
	source = c
	i += 1
	for j in range(template_size):
		gen, i, sub_source = create(s, i, config, classes)
		if gen is None:
			return None, i, ''

		source += sub_source
		childs.append(gen)
	if template_size:
		format_str = '<%s>'
	else:
		format_str = '%s'

	if source in config['dont_expand']:
		rez = source
	else:
		rez = name + (format_str % ', '.join(childs))
	return rez, i, source

def gen(s, config):
	s = s.rstrip()
	gen, i, _ = create(s, 0, config, modify_classes(config['classes']))
	if i != len(s):
		return None
	return gen