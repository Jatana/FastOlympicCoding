# import sublime, sublime_plugin

# from xml.etree import ElementTree as ET
# import urllib

# GOOGLE_AC = r"http://google.com/complete/search?output=toolbar&q=%s"

# class GoogleAutocomplete(sublime_plugin.EventListener):
#     def on_query_completions(self, view, prefix, locations):
#         elements = ET.parse(
#             urllib.request.urlopen(GOOGLE_AC % prefix)
#         ).getroot().findall("./CompleteSuggestion/suggestion")
#         print(elements)
#         sugs = [(x.attrib["data"],) * 2 for x in elements]

#         return sugs