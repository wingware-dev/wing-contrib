# -*- coding: utf-8 -*-
"""
This script indents comments on the selected line(s) to the configured
COMMENT_COLUMN. If no comment exists on a non-blank line then one is
created and indented.

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

import re
import wingapi

# This could be customizable
COMMENT_COLUMN = 40

########################################################################
# Regexp matching Python comments.
# Inspired from Jeffrey Friedl and Fred Curtis' C-comment matching.
# See _Mastering Regular Expressions_ or perlfaq6.
_re_comment_start = re.compile(
  r"^"                                  # line start
  r"("                                  # group for what precedes the comment
  r"(?:"                                # either:
  r"\"(?:\\.|[^\\\"])*\""               # ""-delimited string; skip r'\.' inside
  r"|"                                  # or...
  r"'(?:\\.|[^\\'])*'"                  # ''-delimited string; skip r'\.' inside
  "|"                                   # or...
  r"[^'\"#]"                            # anything but a string or #
  r")*"                                 # repeat as necessary
  r")"                                  # end of not-the-comment
  r"(#.*)$"                             # comment
  )
def _try_to_indent_comment(editor, doc, line_start, line_end, linetxt,
                           indent_if_blank, move_cursor):
  """Try to indent an existing comment.
  
  Return True if successful. If False,the caller should insert an new comment.
  editor, doc, line_start, line_end, linetxt: as per name.
  indent_if_blank: if False, a comment-only line is not indented.
  move_cursor: if False, _try_to_indent_comment don't change selection.
  """
  
  mo = _re_comment_start.match(linetxt)
  if not mo:
    return False
  curr_start, comment = mo.groups()
  start = curr_start.rstrip()
  if comment == "#":
    comment = "# "                      # We might not do this if start==""?
  elif comment[1] != " ":
    comment = "# " + comment[1:]        # Nicer. :-)
  # (Re)indent if needed
  if start or indent_if_blank:
    spaces = " " * max(1, COMMENT_COLUMN - len(start))
  else:
    # Don't change indentation
    start = curr_start
    spaces = ""
  new_txt = "%s%s%s" % (start, spaces, comment)
  if new_txt != linetxt:
    doc.DeleteChars(line_start, line_end - 1)
    doc.InsertChars(line_start, new_txt)
  pos = line_start + len(start) + len(spaces) + 2
  # Position the cursor
  if move_cursor:
    editor.SetSelection(pos, pos)
  return True

def _do_ifc(editor, doc, lineno, line_start, line_end, indent_if_blank):
  """Indent one line for comment.
  
  * Empty line and not indent_if_blank:
    align with indent-to-match
  * Otherwise:
    - if there's a comment already, indent it
    - if not, add one and indent it.
  """
  if 0:
    assert isinstance(editor, wingapi.CAPIEditor)
    assert isinstance(doc, wingapi.CAPIDocument)
  linetxt = doc.GetCharRange(line_start, line_end)
  if (line_start == line_end or linetxt.isspace()) and not indent_if_blank:
    # We must insert 'natural' indentation.
    # Do it the easy way: position the cursor then call indent-to-match.
    editor.SetSelection(line_start, line_end)
    editor.ExecuteCommand("indent-to-match")
    instxt = ""
    line_end = doc.GetLineEnd(lineno)
  else:
    if "#" in linetxt and _try_to_indent_comment(editor, doc,
                                                 line_start, line_end, linetxt,
                                                 indent_if_blank, True):
      return
    instxt = " " * max(1, COMMENT_COLUMN - (line_end - line_start))
  instxt += "# "
  doc.InsertChars(line_end, instxt)
  # Move cursor
  line_end = doc.GetLineEnd(lineno)
  editor.SetSelection(line_end, line_end)

def indent_for_comment(editor=wingapi.kArgEditor):
  """For each line in the selection, adjust any comment to configured
  COMMENT_COLUMN or add a new comment at that column on any non-blank line
  if no comment exists"""
  
  doc = editor.GetDocument()
  start, end = editor.GetSelection()
  start_lineno = doc.GetLineNumberFromPosition(start)
  end_lineno = doc.GetLineNumberFromPosition(end)
  doc.BeginUndoAction()
  try:
    for lineno in range(start_lineno, end_lineno + 1):
      line_start = doc.GetLineStart(lineno)
      line_end = doc.GetLineEnd(lineno)
      _do_ifc(editor, doc, lineno, line_start, line_end, False)
  finally:
    doc.EndUndoAction()

