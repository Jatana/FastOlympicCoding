# import sublime, sublime_plugin

# from xml.etree import ElementTree as ET
# import urllib

# GOOGLE_AC = r"http://translate.google.com/#ru/en/%s"

# class TranslitAutocomplete(sublime_plugin.EventListener):
#     def on_query_completions(self, view, prefix, locations):
#         elements = ET.parse(
#             urllib.request.urlopen(GOOGLE_AC % prefix)
#         ).getroot().findall("./CompleteSuggestion/suggestion")
#         sugs = [(x.attrib["data"],) * 2 for x in elements]
        
#         return sugs