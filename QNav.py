import os
import codecs
import sublime
import sublime_plugin

class qnavCommand(sublime_plugin.WindowCommand):
    current_view = 0

    VIEW_NAME = "File navigation"
    ACTION_SYMBOL = ":"


    # несколько сток из файла для наглядности
    # path - путь к файлу
    def get_strings_form_file(self, path):
        data = "---------------------------------------------\n"
        with codecs.open(path, "r", "utf-8") as file:
            for x in range(1,10):
                data += file.readline()
        data += "\n---------------------------------------------\n"
        return data.replace("\r","")

    # отрисовывает содержимое папки
    # path - путь к папке
    # file - выбранный файл если он есть
    def show(self, path, file):
        data = "Path: " + path + "\n"
        if path == "":
            folders = self.window.folders()
            for folder in folders:
                data += " + " + os.path.basename(folder) + "\n"
        else:       
            for folder in os.listdir(path):
                if os.path.isfile(os.path.join(path, folder)):
                    if len(file) != 0:
                        if file == folder:
                            data += " ► " + folder + "\n"
                            data += self.get_strings_form_file(os.path.join(path, folder))
                            continue
                    data += "   " + folder + "\n"
                else:
                    data += " + " + folder + "\n"

        self.current_view.run_command("select_all")
        self.current_view.run_command("right_delete")

        current_auto_indent = self.current_view.settings().get("auto_indent")
        self.current_view.settings().set("auto_indent", False)
        self.current_view.run_command("insert", {"characters": data});
        self.current_view.settings().set("auto_indent", current_auto_indent)

    # находит самый подходящи элемент из всех
    # path_letters - сокращенная натация
    # items - элементы для поиска
    # 
    # возвращает
    # обновленный путь и найденный элемент
    def find_selected_item(self, path_letters, items):
        # максимальное количество совпадений
        max_count_coincidence = 0
        # выбранный элемент
        selected_item = ""
        # количество элементов с одинаковым количеством совпадений
        number_of_identical = 0

        for item in items:
            i = 0
            while (i < len(path_letters)) & (i < len(item)):
                # считаем сколько совпалов от начала
                if item[i].lower() != path_letters[i]:
                    break
                i += 1

            # считаем количество одинаковых количеств совпадений
            if max_count_coincidence == i:
                number_of_identical += 1
            else:
                if max_count_coincidence < i:
                    max_count_coincidence = i
                    selected_item = item
                    number_of_identical = 0

        # если после поиска по началу ничего не находит включаем общий поиск
        if selected_item == "":
            for item in items:
                # максимальное количество совпадений в данном эелементе
                max_count_coincidence_in_this_item = 0
                # величина совпадающей подстроки
                count_coincidence = 0
                # для натации
                i = 0
                # для элемента
                j = 0
                # print("-------------")
                while (i < len(path_letters)) & (j < len(item)):
                    # print(path_letters[i])
                    # print(item[j].lower())
                    if path_letters[i] == item[j].lower():
                        # print("+")
                        count_coincidence += 1
                        i += 1
                    else:
                        # print("-")
                        # сохраняем максимальное количество сповадений
                        if max_count_coincidence_in_this_item < count_coincidence:
                            max_count_coincidence_in_this_item = count_coincidence
                        count_coincidence = 0
                        i = 0
                    j += 1

                # условия для конечной цепочки которая не обрабатывается условием в цикле
                if max_count_coincidence_in_this_item < count_coincidence:
                    max_count_coincidence_in_this_item = count_coincidence
                
                # считаем количество одинаковых количеств совпадений
                if max_count_coincidence == max_count_coincidence_in_this_item:
                    number_of_identical += 1
                else:
                    if max_count_coincidence < max_count_coincidence_in_this_item:
                        max_count_coincidence = max_count_coincidence_in_this_item
                        selected_item = item
                        number_of_identical = 0

                # print(path_letters)
                # print(max_count_coincidence_in_this_item)
                # print(item)
                # print("-------------")

        # print("-------------")
        # print(path_letters)
        # print(max_count_coincidence)
        # print(selected_item)
        # print("-------------")

        # условие для перескока в следующую выборку
        if max_count_coincidence < len(path_letters):
            if (path_letters[max_count_coincidence] == "\\") | (path_letters[max_count_coincidence] == "/"):
                max_count_coincidence += 1

        # если сокращенной натации не хватает для точного определения конкретного элемента
        # то ожидаем уточнения
        # if number_of_identical != 0:
            # selected_item = ""

        return [path_letters[max_count_coincidence:], selected_item]



    # находит реальный путь соответствующий сокращенной натации
    # path_letters - сокращенная натация
    # 
    # возвращает
    # реальный путь выбранный файл и комманду
    def find_path(self, path_letters):
        # реальный путь
        path = ""
        # элементы по которым происходит поиск пути
        # по умолчанию открые папки
        items = self.window.folders()
        # если папка в проекте одна по сразу идем в неё
        if len(items) == 1:
            path = items[0]
            items = os.listdir(path)

        
        # инедекс для прохождения по path_letters
        # проходим по всем символам натации
        while len(path_letters) > 0:
            

            # если символ ACTION_SYMBOL значит далее следует команда
            if (path_letters[0] == self.ACTION_SYMBOL):
                break
            # если нет элементов то выходим
            if len(items) == 0:
                break

            path_letters_and_selected_item = self.find_selected_item(path_letters, items)
            # print("-------------")
            # print(path)
            # print(path_letters)
            # print(path_letters_and_selected_item)
            # print("-------------")
            path_letters = path_letters_and_selected_item[0]

            # если дальнейший путь не обноружен то выходим
            if path_letters_and_selected_item[1] == "":
                break

            # если мы уперлись в файл значит это конечная точка и мы её возврщаем
            if os.path.isfile(os.path.join(path, path_letters_and_selected_item[1])):
                return [path, path_letters_and_selected_item[1], path_letters]
            # если нет то формируем дальнейший путь
            else:
                path = os.path.join(path, path_letters_and_selected_item[1])

            # обновляем набор элементов по новому пути
            items = os.listdir(path)


        # print("------end-------")
        # print(path)
        # print(path_letters)
        # print("-------------")

        return [path, "", path_letters]
    
    # запуск команды по сочетанию клавиш
    def run(self, **args):
        if "path" in args:
            qnav_path = args["path"]
        else:
            settings = sublime.load_settings('QNav.sublime-settings')
            qnav_path = settings.get("qnav_path")

            if qnav_path == None:
                qnav_path = ""

        self.current_view = self.window.new_file()
        self.current_view.set_name(self.VIEW_NAME)
        path_and_file = self.find_path(qnav_path)
        self.show(path_and_file[0], "")
        self.window.show_input_panel("Enter path", qnav_path.split(':')[0], self.on_done, self.on_change, self.on_cancel)
        
    # закрываем влкадку навигатор
    def close_view(self):
        if (self.current_view != 0):
            self.current_view.set_scratch(True)
            self.window.focus_view(self.current_view)
            if (self.window.active_view().name() == self.VIEW_NAME):
                self.window.run_command("close_file")
                self.current_view = 0

    # нажали enter - выполняем действие
    def on_done(self, text):
        path_and_file = self.find_path(text)
        settings = sublime.load_settings('QNav.sublime-settings')
        settings.set("qnav_path", text)
        self.close_view()
        if len(path_and_file[2]) != 0:
            # если действие: добавить
            if path_and_file[2][:2] == ":a":
                # добавить дирректорию и открыть нафигатор в ней
                if path_and_file[2][2:].find(".") == -1:
                    os.makedirs(os.path.join(path_and_file[0], path_and_file[2][2:]))
                    self.current_view = self.window.new_file()
                    self.current_view.set_name(self.VIEW_NAME)
                    self.show(path_and_file[0], "")
                    self.window.show_input_panel("Enter path", text.split(':')[0], self.on_done, self.on_change, self.on_cancel)
                # добавить файл и открыть его
                else:
                    self.window.open_file(os.path.join(path_and_file[0], path_and_file[2][2:]))
            # если действие: удалить
            elif path_and_file[2][:2] == ":r":
                # удалить файл
                if len(path_and_file[1]) != 0:
                    os.remove(os.path.join(path_and_file[0], path_and_file[1]))
                # удалить директорию
                else:
                    os.rmdir(path_and_file[0])

            # если действие: найти
            elif path_and_file[2][:2] == ":f":
                # удалить файл
                if len(path_and_file[1]) != 0:
                    path_to_find = os.path.join(path_and_file[0], path_and_file[1])
                # удалить директорию
                else:
                    path_to_find = path_and_file[0]

                self.window.run_command("show_panel", {
                    "panel": "find_in_files",
                    "where": path_to_find
                })
        # если выбран файл открываем его
        elif len(path_and_file[1]) != 0:
                self.window.open_file(os.path.join(path_and_file[0], path_and_file[1]))

    # изменился путь - обновляем окно с навигацией
    def on_change(self, text):
        path_and_file = self.find_path(text)
        self.show(path_and_file[0], path_and_file[1])

    # вызвали отмену - закрываем окно с навигацией
    def on_cancel(self):
        self.close_view()

