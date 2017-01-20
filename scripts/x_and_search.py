"""These scripts simultaneously initiate Find Uses and Batch Search, or Rename Refactoring
and Batch Search. Two variants exist to work off the current selection or the
last click location. """

# Written by Stephan Deibel

import wingapi

def find_uses_and_search():
    app = wingapi.gApplication
    ed = app.GetActiveEditor()
    start, end = ed.GetSelection()
    if start == end:
        app.ExecuteCommand('select-current-word')
    app.ExecuteCommand('find-points-of-use')
    app.ExecuteCommand('batch-search')
    
find_uses_and_search.label = "Find Uses and Search"

def rename_and_search():
    app = wingapi.gApplication
    ed = app.GetActiveEditor()
    start, end = ed.GetSelection()
    if start == end:
        app.ExecuteCommand('select-current-word')
    app.ExecuteCommand('rename-symbol')
    app.ExecuteCommand('batch-search')
    
rename_and_search.label = "Rename and Search"

def find_clicked_uses_and_search():
    app = wingapi.gApplication
    ed = app.GetActiveEditor()
    try:
        pos = ed.GetClickLocation()
    except:
        pos = ed.fEditor._FindPoint()[1]
    ed.SetSelection(pos, pos)
    app.ExecuteCommand('select-current-word')
    app.ExecuteCommand('find-points-of-use')
    app.ExecuteCommand('batch-search')
    
find_clicked_uses_and_search.contexts = (wingapi.kContextEditor(), )
find_clicked_uses_and_search.label = "Find Uses and Search"

def rename_clicked_and_search():
    app = wingapi.gApplication
    ed = app.GetActiveEditor()
    try:
        pos = ed.GetClickLocation()
    except:
        pos = ed.fEditor._FindPoint()[1]
    ed.SetSelection(pos, pos)
    app.ExecuteCommand('select-current-word')
    app.ExecuteCommand('rename-symbol')
    app.ExecuteCommand('batch-search')
    
rename_clicked_and_search.contexts = (wingapi.kContextEditor(), )
rename_clicked_and_search.label = "Rename and Search"

