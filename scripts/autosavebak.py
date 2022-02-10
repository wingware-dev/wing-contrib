# Simple script that installs a handler to place a copy of any saved
# file into a *.bak before overwriting it with the content

import wingapi
def _connect_to_presave(doc):
  def _on_presave(filename, encoding):
    # Avoid operation when saving a copy to another location
    if filename is not None:
      return
    # Write *.bak file
    f = open(doc.GetFilename(), 'r')
    txt = f.read()
    f.close()
    bak_filename = doc.GetFilename() + '.bak'
    f = open(bak_filename, 'w')
    f.write(txt)
    f.close()
  connect_id = doc.Connect('presave', _on_presave)
  
def _init_bak():
  wingapi.gApplication.Connect('document-open', _connect_to_presave)
  for doc in wingapi.gApplication.GetOpenDocuments():
    _connect_to_presave(doc)

_init_bak()

