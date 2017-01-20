"""
This script reformats Python code in a pretty print way. It adds the
commands pformat, shorten_method, and expand_method.


Copyright (c) 2005, Ken Kinder All rights reserved.

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
"""

import wingapi
import gettext
import pprint
_ = gettext.translation('scripts_editor_extensions', fallback = 1).ugettext
_i18n_module = 'scripts_editor_extensions'

def _handle_stack_char(stack, char):
    if char in """'"[](){}""":
        if stack:
            if char in '"\'' and stack[-1] == char:
                stack.pop()
            elif char == ']' and stack[-1] == '[':
                stack.pop()
            elif char == ')' and stack[-1] == '(':
                stack.pop()
            elif char == '}' and stack[-1] == '{':
                stack.pop()
            else:
                stack.append(char)
        else:
            stack.append(char)

def _getclipboard():
    editor = wingapi.gApplication.GetActiveEditor()
    doc = editor.GetDocument()
    start, end = editor.GetSelection()
    
    return doc.GetCharRange(start, end)

def _setclipboard(txt):
    editor = wingapi.gApplication.GetActiveEditor()
    doc = editor.GetDocument()
    start, end = editor.GetSelection()
    
    doc.BeginUndoAction()
    try:
        doc.DeleteChars(start, end-1)
        doc.InsertChars(start, txt)
    finally:
        doc.EndUndoAction()

def pformat():
    """Toggle block comment (with ## at start) on the selected lines in editor.
    This is a different style of block commenting than Wing implements by default
    (the default in Wing is intended to work better with some of the other
    editor functionality)"""
    txt = _getclipboard()
    
    pyValue = eval(txt, {}, {})
    newtxt = pprint.pformat(pyValue)
    
    if txt[0] == '\n': newtxt = '\n%s' % newtxt
    if txt[-1] == '\n': newtxt += '\n'
    
    _setclipboard(newtxt)

def _shorten_method(txt):
    # This is ghetto, but whatever
    txt = txt.replace('\n', ' ')
    newtxt = ''
    stack = []
    lastChar = None
    parenFound = False
    for char in txt:
        if char == '(' and not parenFound:
            parenFound = True
        else:
            _handle_stack_char(stack, char)
        if not (char == ' ' and (lastChar == ' ' and newtxt.strip()) and not stack):
            # Trim out extra space
            newtxt += char
        lastChar = char
    
    if txt[0] == '\n': newtxt = '\n%s' % newtxt
    if txt[-1] == '\n': newtxt += '\n'
    return newtxt

def shorten_method():
    """
    Puts something like foo(a,b,x=1) on one line.
    """
    _setclipboard(_shorten_method(_getclipboard()))

def expand_method():
    """
    Puts something like foo(a,b,x=1) on several lines.
    """
    txt = _getclipboard()
    
    txt = _shorten_method(txt)
    
    # This is too is what the kids call, ghetto.
    newtxt = ''
    stack = []
    indentLevel = None
    for char in txt:
        if indentLevel is None and char == '(' and not stack:
            indentLevel = len(newtxt)
        else:
            _handle_stack_char(stack, char)
        if char == ',' and not stack:
            newtxt += '%s\n%s' % (char, ' '*indentLevel)
        else:
            newtxt += char
    
    if txt[0] == '\n': newtxt = '\n%s' % newtxt
    if txt[-1] == '\n': newtxt += '\n'
    
    _setclipboard(newtxt)
    
