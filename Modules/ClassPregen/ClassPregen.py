from os import path

base_dir = path.split(__file__)[0]


classes = eval(open(path.join(base_dir, 'classes.json')).read())


def modify_classes():
	global classes
	new_classes = {}
	for key in classes:
		new_classes[key[0]] = classes[key]
		new_classes[key[0]]['name'] = key
	classes = new_classes

# print(classes)

modify_classes()


def create(s, i):
	c = s[i]
	template_size = classes[c]['template_size']
	name = classes[c]['name']
	childs = []
	i += 1
	for j in range(template_size):
		gen, i = create(s, i)
		childs.append(gen)
	if template_size:
		format_str = '<%s>'
	else:
		format_str = '%s'
	return name + (format_str % ', '.join(childs)), i


def pregen(s):
	return create(s, 0)[0]