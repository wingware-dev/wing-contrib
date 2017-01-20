"""
This script adds a couple of context menu options relevant for gnome.

Copyright (c) 2009, Ken Kinder All rights reserved.

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

Details:

On files in the Project panel, it adds a "Gnome Open" command that opens the selected file
with whatever the appropriate Gnome program is. In WingIDE preferences, you can specify
external commands, but this saves you the time of having to do that if Gnome already knows
what to do. It just uses the "open" OS command.

For directories in the Project panel, there is a "Browse in Nautilus" command, which is
pretty self-explanatory.

In an editor, you can right click and choose "Diff to Disk", which shows you a meld window
that compares your current buffer to what's on the disk. Obviously, you need to have meld
installed.

"""

import gettext
import os
import subprocess
import tempfile
import wingapi
import thread

_ = gettext.translation('scripts_editor_extensions', fallback = 1).ugettext

def gnome_open(filenames=wingapi.kArgFilename):
    """Perform svn diff on the given files or directories."""
    app = wingapi.gApplication
    subprocess.Popen(['gnome-open'] + filenames)
   
gnome_open.label = _('_Gnome Open')
gnome_open.contexts = [wingapi.kContextEditor(), 
                     wingapi.kContextProject()]

def _nautilus_browse_available(filenames=wingapi.kArgFilename):
    for f in filenames:
        if os.path.isdir(f):
            return True

def nautilus_browse(filenames=wingapi.kArgFilename):
    """Perform svn diff on the given files or directories."""
    for f in filenames:
        if os.path.isdir(f):
            subprocess.Popen(['nautilus'] + [f])

nautilus_browse.available = _nautilus_browse_available
nautilus_browse.label = _('_Browse in Nautilus')
nautilus_browse.contexts = [wingapi.kContextProject()]
  
def diff_to_file_on_disk():
    editor = wingapi.gApplication.GetActiveEditor()
    doc = editor.GetDocument()
    
    tmp = tempfile.NamedTemporaryFile()
    originalFile = doc.GetFilename()
    currentBufferFile = os.tempnam()   
    open(currentBufferFile, 'w').write(doc.GetText())
    
    def waiter():
        subprocess.call(['meld', originalFile, currentBufferFile])
        os.remove(currentBufferFile)
    thread.start_new_thread(waiter, tuple())
    
diff_to_file_on_disk.label = _('_Diff to disk')
diff_to_file_on_disk.contexts = [wingapi.kContextEditor()]
