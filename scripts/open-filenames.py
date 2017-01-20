"""These scripts allow opening the filename at the current caret position or last click
location. For partial paths, the full path is resolved relative to the directory where the
editor's file is located. No action is taken if the file does not exist. """

# Written by Stephan Deibel

import os
import wingapi

def open_selected_filename():
    '''Open the selected file name.  Relative paths are resolved using the
    location of the editor's file.'''
    editor = wingapi.gApplication.GetActiveEditor()
    start, end = editor.GetSelection()
    _open_filename_at_position(editor, start)
    
def open_clicked_filename():
    '''Open the clicked file name.  Relative paths are resolved using the
    location of the editor's file.'''
    editor = wingapi.gApplication.GetActiveEditor()
    try:
        pos = editor.GetClickLocation()
    except:
        pos = editor.fEditor._FindPoint()[1]
    _open_filename_at_position(editor, pos)    

open_clicked_filename.contexts = (wingapi.kContextEditor(), )
open_clicked_filename.label = "Open Clicked Filename"
    
_kNonFilenameChars = ' \t\n\r()*,;\'"'

def _open_filename_at_position(editor, start):
    
    document = editor.GetDocument()
    startpos, endpos = None, None
    offset = 0
    doclen = document.GetLength()
    while startpos is None or endpos is None:
        if start - offset > 0 and startpos is None:
            c1 = document.GetCharRange(start-offset-1, start-offset)
            if c1 in _kNonFilenameChars:
                startpos = start - offset
        if start + offset < doclen - 1 and endpos is None:
            c1 = document.GetCharRange(start+offset, start+offset+1)
            if c1 in _kNonFilenameChars:
                endpos = start + offset
        offset += 1
        if offset > 1000:
            return 
    filename = document.GetCharRange(startpos, endpos)
    dirname = os.path.dirname(document.GetFilename())
    old_dir = os.getcwd()
    try:
        os.chdir(dirname)
        filename = os.path.abspath(filename)
        filename = os.path.expanduser(filename)
        filename = os.path.normpath(filename)
    finally:
        os.chdir(old_dir)
        
    if os.path.exists(filename):
        wingapi.gApplication.OpenEditor(filename)
    
