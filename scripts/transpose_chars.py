# -*- coding: utf-8 -*-
"""
This script adds a comment to transpose the characters at the caret position
and moves the caret one position forward.

Standard legalese (X11 license lowercased):

Copyright (C) 2006 Yves Bastide <stid@acm.org>

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

The Software is provided "as is", without warranty of any kind, express or
implied, including but not limited to the warranties of merchantability,
fitness for a particular purpose and noninfringement. in no event shall the
author be liable for any claim, damages or other liability, whether in an
action of contract, tort or otherwise, arising from, out of or in connection
with the Software or the use or other dealings in the Software.
"""

import wingapi


def transpose_chars(editor=wingapi.kArgEditor):
  """Interchange characters around point, moving forward one character.
  
  A bit convoluted because GetCharRange returns utf-8, not unicode:
  We must get the whole line, convert it to unicode so all characters are
  of length one; then transpose and change the whole line.
  """
  doc = editor.GetDocument()
  if 0:
    assert isinstance(editor, wingapi.CAPIEditor)
  start, end = editor.GetSelection()
  if start != end:
    # Selection; abort.
    return
  start_lineno = doc.GetLineNumberFromPosition(start)
  end_lineno = doc.GetLineNumberFromPosition(end)

  line_start = doc.GetLineStart(start_lineno)
  line_end = doc.GetLineEnd(end_lineno)
  if line_start == line_end:
    return
  begin_txt = doc.GetCharRange(line_start, start).decode("utf-8")
  end_txt = doc.GetCharRange(start, line_end).decode("utf-8")
  if not begin_txt:
    return
  # Back to utf-8 to compute the next cursor pos...
  pos = start + len(begin_txt[-1].encode("utf-8"))
  if not end_txt:                       # EOL
    end_txt = begin_txt[-1]
    begin_txt = begin_txt[:-1]
    pos = start                         # won't move the cursor
  new_txt = begin_txt[:-1] + end_txt[0] + begin_txt[-1] + end_txt[1:]
  doc.BeginUndoAction()
  try:
    doc.DeleteChars(line_start, line_end - 1)
    doc.InsertChars(line_start, new_txt)
    editor.SetSelection(pos, pos)
  finally:
    doc.EndUndoAction()
