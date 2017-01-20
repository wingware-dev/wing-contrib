# Written by Philip Winston
#
# Adds command 'header-flip' that toggles between a C/C++ file and the 
# matching header file. Requires the source and header file are in the 
# same directory right now, but could be extended to search the whole project.

import os
import wingapi

def findMatchingFile(basepath, exts):
    """Return the first file which exists with one of the given extensions."""
    for ext in exts:
        path = basepath + ext
        if os.path.exists(path):
            return path
    return None

def header_flip():
    """Flip between the matching header and source files.
    
    NOTE: We assume both are in the same directory. A more advanced 
    version might look throughout the project for a match.
    """
    
    C_EXTS = ['.c', '.cxx', '.cpp', '.c++', '.cc']
    H_EXTS = ['.h', '.hpp']
    
    app = wingapi.gApplication    
    editor = app.GetActiveEditor()
    if editor is None:
        return None
    context = editor.GetSourceScope()
    if len(context) == 0:
        return None
        
    dirname, filename = os.path.split(context[0])
    basename, ext = os.path.splitext(filename)
    basepath = os.path.join(dirname, basename)
    
    alt = None
    
    if ext.lower() in C_EXTS:
        alt = findMatchingFile(basepath, H_EXTS)
    elif ext.lower() in H_EXTS:
        alt = findMatchingFile(basepath, C_EXTS)
        
    if alt:
        app.OpenEditor(alt)
    else:
        msg = "Cannot flip %s" % filename
        app.ShowMessageDialog("header_flip error", msg)
    
        
        
