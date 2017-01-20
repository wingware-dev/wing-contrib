# (c) 2008, Marcin Kasperski
#
# Generate .html files out of WingIDE keymap files.
#
# with changes made 2010-2012 by Mitchell Model, dev@software-concepts.org,
# with permission of the author:
#     -- added the user's keybindings as another output file
#     -- sorted output by keystroke
#     -- fix to work with either Python 2 or Python 3
#     -- minor code cleanup and refactoring
#
# Usage:
#    - if WINGHOME is not defined in your OS environment, change the first
#      assignment statement below to point to the Wing IDE executable
#    - chdir to the directory where result files are to be created
#    - run this script

from __future__ import with_statement # for old Python versions
import sys
import os
import re

keymap_location = os.getenv("WINGHOME") # leave this if WINGHOME is defined
# keymap_location = "/Applications/WingIDE.app/Contents/MacOS"
# keymap_location - r"C:\Program Files (x86)\Wing IDE 4.1"

# probably only need to change this if on Windows
preferences_path = "~/.wingide4/preferences"

keymap_files = ['keymap.' + mapname for mapname in
                ('basic', 'brief', 'emacs', 'normal', 'osx', 'vi', 'visualstudio')]

if not os.path.exists(keymap_location + '/keymap.basic'):
    print('''keymap_location is not correct - it should be set to the path to the directory
containing the wing executable; set it at the beginning of the script and rerun'''
          .format(keymap_location))
    sys.exit()

##########################################################################

class KeymapFile(object):

    # To speed up include handling, here we cache already loaded objects. This maps
    # keymap name to the KeymapFile object.
    _cached_files = {}

    @classmethod
    def load(cls, keymap_name):
        """
        True constructor.

        map = KeymapFile.load("keymap.brief")

        """
        obj =  cls._cached_files.get(keymap_name, None)
        if obj:
            return obj
        obj = KeymapFile(keymap_name)
        cls._cached_files[keymap_name] = obj
        return obj

    def __init__(self, fname):
        """
        Do not use this constructor, call KeymapFile.load() instead.
        """

        # It seems comments are only at the start on the line, # may be mentioned as key
        re_comment = re.compile(r'^#')
        re_mapping = re.compile(r"^'([^']+)'\s*:\s*(['\"])(.+)\2")
        re_include = re.compile(r"^\%include\s+(\S+)")

        # List of assigned keys in order of reading
        self.keys = []
        # Mapping of keys to commands
        self.commands = {}

        with open(os.path.join(keymap_location, fname)) as f:
            for line in f.readlines():
                line = line.strip()
                if not line:
                    continue
                if re_comment.match(line):
                    continue
                m = re_mapping.match(line)
                if m:
                    #print "Mapping %s -> %s" % (m.group(1), m.group(3))
                    self._add_mapping(m.group(1), m.group(3))
                    continue
                m = re_include.match(line)
                if m:
                    #print "Include %s" % m.group(1)
                    self._import_mappings(m.group(1))
                    continue
                raise Exception("Unknown line: file {}, line {}".format(fname, line))

    def _add_mapping(self, key, command):
        # Removing previous key entry if any
        if key in self.keys:
            self.keys.remove(key)
        # Addding this one
        self.keys.append(key)
        # Saving command
        self.commands[key] = command

    def _import_mappings(self, importFromName):
        importFrom = self.load(importFromName)
        for key in importFrom.keys:
            self._add_mapping(key, importFrom.commands[key])

    def text_report(self, filelike):
        for key in self.keys:
            filelike.write( "%s: %s\n" % (key, self.commands[key]) )
        filelike.write('\n')

    def html_report(self, filelike):
        filelike.write("<html><body><table><th><tr><td>Key</td><td>Command</td></tr></th>")
        for key in sorted(self.keys):
            filelike.write( "<tr><td>%s</td><td>%s</td></tr>" % (key, self.commands[key]) )
        filelike.write("</table></body></html>\n")

try:
    import configparser                 # Python 3
except:
    import ConfigParser as configparser # Python 2

try:
    import ast
    evaluate = ast.literal_eval         # safer
except:
    evaluate = eval

class UserKeymap(KeymapFile):
    """Extract the user settings from the WingIDE preferences file"""
    def __init__(self):
        self.keys = []
        self.commands = {}

    def load(self):
        prefpath = os.path.expanduser(preferences_path)
        if not os.path.exists(prefpath):
            print('''Preferences file {} not found - not generating User keymap table:
    set preferences_path at the beginning of the script to the location of your
    preferences file and rerun the script.'''.format(preferences_path))
            return
        config = configparser.RawConfigParser()
        config.read(prefpath)
        if config.has_option('user-preferences', 'gui.keymap-override'):
            for key, value in evaluate(config.get('user-preferences', 'gui.keymap-override')).items():
                self._add_mapping(key, value)
            return self
        else:
            print('No user keybindings found in preferences file - not generating User keymap table')

def report_keymap(keymap_name, keymap):
    print("*** %s ***" % keymap_name)
    #m.text_report(sys.stdout)
    with open(keymap_name + '.html', 'w') as keymap_file:
        keymap.html_report(keymap_file)

for keymap_name in keymap_files:
    report_keymap(keymap_name, KeymapFile.load(keymap_name))
usermap = UserKeymap().load()
if usermap:
    keymap = report_keymap('keymap.user', usermap)
