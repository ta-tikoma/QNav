# QNav
Its package from Sublime text 3 for quick navigation by file of project.

### Installing
- Get package
  - Install via Package Control by name QNav
  - OR Copy this repository into the Sublime Text 3 "Packages" directory.
- Add keymaps for the commands

### Keymaps
For clear path (or any constant path):
`{ "keys": ["ctrl+shift+o"], "command": "qnav", "args": { "path": "" } }`

For last path:
`{ "keys": ["ctrl+alt+o"], "command": "qnav", "args": {} }`

### Example
Trigger input field and enter first letter of folder name where you want go.

For **open file** you must input letters of path and press Enter.

For **add** file or folder you can write `:afolder_name` after your path.

For **remove** file or foldre you can write `:r` after you path.

For **find in files** file or foldre you can write `:f` after you path.

![example](https://github.com/ta-tikoma/QNav/blob/master/example.gif?raw=true)
