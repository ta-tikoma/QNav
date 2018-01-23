import os
import codecs
import sublime
import sublime_plugin

class qnavCommand(sublime_plugin.WindowCommand):
	current_view = 0
	view_name = "File navigation"

	def get_strings_form_file(self, path):
		data = "---------------------------------------------\n"
		with codecs.open(path, "r", "utf-8") as file:
			for x in range(1,10):
				data += file.readline()
		data += "\n---------------------------------------------\n"
		return data.replace("\r","")

	def show(self, path, file):
		data = "Path: " + path.replace("\\", "/") + "\n"
		for folder in os.listdir(path):
			if os.path.isfile(path + "/" + folder):
				if len(file) != 0:
					if file == folder:
						data += " ► " + folder + "\n"
						data += self.get_strings_form_file(path + "/" + folder)
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

	def find_path(self, path_letters):
		folders = self.window.folders()
		path = folders[0]
		file_selected = ""

		if len(folders) == 1:
			i = 0
			undefined_flag = False
			while i < len(path_letters):
				if (path_letters[i] == ":"):
					break

				items = os.listdir(path)

				max_concurrences_index = 0
				selected_item = ""

				j = 0
				while j < len(items):
					concurrences_index = 0
					k = i
					while (k < len(path_letters)) & (concurrences_index < len(items[j])):
						if path_letters[k] == '\\':
							break
						if items[j][concurrences_index].lower() == path_letters[k]:
							k += 1
							concurrences_index += 1
						else:
							break

					if k < len(path_letters):
						if path_letters[k] == '\\':
							undefined_flag = False
							selected_item = items[j]
							max_concurrences_index = concurrences_index + 1
							break

					if concurrences_index >= max_concurrences_index:
						if concurrences_index == max_concurrences_index:
							undefined_flag = True
						else:
							undefined_flag = False

						selected_item = items[j]
						max_concurrences_index = concurrences_index

					j += 1

			
				i += max_concurrences_index

				if undefined_flag:
					break

				if os.path.isfile(path + "/" + selected_item):
					file_selected = selected_item
					break
				else:
					path += "/" + selected_item

		# print("-------------")
		# print(path)
		# print(file_selected)
		# print(path_letters[i:])

		return [path, file_selected, path_letters[i:]]

	def run(self, **args):
		if "path" in args:
			qnav_path = args["path"]
		else:
			settings = sublime.load_settings('QNav.sublime-settings')
			qnav_path = settings.get("qnav_path")

			if qnav_path == None:
				qnav_path = ""

		self.current_view = self.window.new_file()
		self.current_view.set_name(self.view_name)
		path_and_file = self.find_path(qnav_path)
		self.show(path_and_file[0], "")
		self.window.show_input_panel("Enter path", qnav_path.split(':')[0], self.on_done, self.on_change, self.on_cancel)
		


	def close_view(self):
		if (self.current_view != 0):
			self.current_view.set_scratch(True)
			self.window.focus_view(self.current_view)
			if (self.window.active_view().name() == self.view_name):
				self.window.run_command("close_file")
				self.current_view = 0

	def on_done(self, text):
		path_and_file = self.find_path(text)
		settings = sublime.load_settings('QNav.sublime-settings')
		settings.set("qnav_path", text)
		self.close_view()
		if len(path_and_file[2]) != 0:
			if path_and_file[2][:2] == ":a":
				if path_and_file[2][2:].find(".") == -1:
					os.makedirs(path_and_file[0] + "/" + path_and_file[2][2:])
					self.current_view = self.window.new_file()
					self.current_view.set_name(self.view_name)
					self.show(path_and_file[0], "")
					self.window.show_input_panel("Enter path", text.split(':')[0], self.on_done, self.on_change, self.on_cancel)
				else:
					self.window.open_file(path_and_file[0] + "/" + path_and_file[2][2:])
			elif path_and_file[2][:2] == ":r":
				if len(path_and_file[1]) != 0:
					os.remove(path_and_file[0] + "/" + path_and_file[1])
				else:
					os.rmdir(path_and_file[0])
		elif len(path_and_file[1]) != 0:
				self.window.open_file(path_and_file[0] + "/" + path_and_file[1])


	def on_change(self, text):
		path_and_file = self.find_path(text)
		self.show(path_and_file[0], path_and_file[1])

	def on_cancel(self):
		self.close_view()

