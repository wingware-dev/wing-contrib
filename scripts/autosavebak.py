# Simple script that make a copy of any saved file to a *.bak before overwriting 
# it with newly saved content

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
  doc.Connect('presave', _on_presave)
  
def _init_bak():
  wingapi.gApplication.Connect('document-open', _connect_to_presave)
  for doc in wingapi.gApplication.GetOpenDocuments():
    _connect_to_presave(doc)

_init_bak()

