# This script causes Wing to auto-save all files every few seconds, as configured,
# whenever they contain edits.

# WARNING:  This is not a good idea unless all the files you're editing are in
# revision control.  Otherwise unintended edits may be saved without any way to
# find and fix them.

# Written by Stephan Deibel

import wingapi

kSaveFrequency = 5  # seconds
gPendingSaves = {}

def _connect_to_document(doc):
  def _on_modified(savepoint):
    if savepoint:
      return
    gPendingSaves[doc.GetFilename()] = doc
  connect_id = doc.Connect('save-point', _on_modified)

def _do_saves():
  for fn, doc in gPendingSaves.items():
    doc.Save()
  gPendingSaves.clear()
  return True  # Keep calling this
  
def _init():
  wingapi.gApplication.Connect('document-open', _connect_to_document)
  for doc in wingapi.gApplication.GetOpenDocuments():
    _connect_to_document(doc)
    
  wingapi.gApplication.InstallTimeout(kSaveFrequency*1000, _do_saves)

_init()
