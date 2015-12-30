import sublime, sublime_plugin

class DecToHexCommand(sublime_plugin.TextCommand):
    MAX_STR_LEN = 10
    def run(self, edit):
        v = self.view
        # Получаем значение первого выделенного блока
        dec = v.substr(v.sel()[0])

        # Заменяем десятичное число шестнадцатеричным или выводим сообщение об ошибке		
        if dec.isdigit():
            v.replace(edit, v.sel()[0], hex(int(dec))[2:].upper())
        else:
            # Обрезаем слишком длинные строки, которые не поместятся в статусбар 
            if len(dec) > self.MAX_STR_LEN:
                logMsg = dec[0:self.MAX_STR_LEN]+ "..."
            else:
                logMsg = dec
            sublime.status_message("\"" + logMsg + "\" isn't a decimal number!")