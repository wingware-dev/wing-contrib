"""Implement symbol and syllable commands analogous to six common word commands

Mitchell L Model <dev@software-concepts.org>, 2012
No rights reserved; all uses permitted.

==== Installation ====

Copy this file to your .wingide4/scripts directory.

==== Commands ====

This script provides symbol and syllable commands analogous to six common
Wing word commands:

    Wing WORD Command     new SYMBOL Command      new SYLLABLE Command

    forward-word          forward-symbol          forward-syllable
    forward-word-extend   forward-symbol-extend   forward-syllable-extend
    forward-delete-word   forward-delete-symbol   forward-delete-syllable
    backward-word         backward-symbol         backward-syllable
    backward-word-extend  backward-symbol-extend  backward-syllable-extend
    backward-delete-word  backward-delete-symbol  backward-delete-syllable

In short, symbols are like words, but the symbol commands behave somewhat
differently with regard to word boundaries; in particular, they do not stop at
punctuation other than periods inside sequences of letters and digits. Syllables
are smaller units; the syllable commands stop at underscores and most lettercase
changes.

==== Behavior ====

Definition of a syllable:

    a non-empty sequence beginning with 0 or more characters in string.uppercase
    followed 0 or more characters in string.lowercase or string.digit 

Examples:

    * the sequences a, typical, and name, in a_typical_name
    * the sequences Typical, Class, and Name in TypicalClassName
    * CONSTANT is a single syllable
    * POSITIONx11a is a single syllable 

A side-effect of the way the syllable commands handle underscores and mixed case is that
they will stop at mixed case boundaries even if the mixed-case character sequence is
within a symbol that contains underscores.

Symbols are the same as what Wing considers to be words for the purposes of its word
commands. However, the symbol commands defined here behave somewhat differently than the
word commands. In particular, they don't stop at punctuation such as parentheses. (They do
stop at periods that have adjacent letters, numbers, or underscores, as in object.field)
Bind keystrokes to these commands if you prefer this behavior, otherwise use the regular
Wing word commands.

==== Keybindings ====

You have to decide for each command you want to use whether to rebind an existing Wing
keybinding or choose an unused key. Here are a few suggestions to consider:

    * You could rebind standard key sequences for word commands to the corresponding
      symbol or syllable commands.
    * Wing makes a distinction between shifted and unshifted versions of control-
      and alt-modified keys. Therefore, you could use a shifted control- or
      alt- key for one command and the unshifted version for another. (For
      example, you could use one variation for syllable commands and another
      for symbol commands.)
    & In some cases, with details depending on your choice of keyboard personality,
      two keys are bound to the same Wing word command. You could replace one of those
      with a syllable or symbol command. For instance, in the Emacs personality,
      alt-F and control-Right are both bound to forward-word. If you only use one of
      these, you could rebind the other to forward-symbol or forward-syllable. 

Important Note

The syllable and symbol commands will only work in an editor. They will not be operative
in a Python Shell, Debug Probe, or any other tool. A key bound to a syllable or symbol
command will do nothing in a tool. For additional keybindings this will only be a slight
annoyance, but this is more of a problem for standard Wing keybindings that you replace
with syllable or symbol commands. Fortunately, there is a fallback mechanism.

Wing provides a way to bind more than one command to the same key, and the first one that
is operative in the current "context" will be used. The way to do this is to list the
commands separated by a comma. Therefore, you could bind a key to a syllable or symbol
command followed by a comma and the standard Wing command. That way, you'd get the
syllable or symbol behavior in an editor and the word behavior elsewhere. For exmaple, you
could bind alt-F to "forward-symbol,forward-word". This is certainly not ideal, but it is
the best that can be done given Wing's current implementation.

Another Note

Whatever bindings you choose, check whether you are overriding bindings for other commands
you use. You can see what a key is bound to with the command describe-key-briefly. You can
also use the ConvertKeymapsToHtml utility to get html lists of keybindings for each of the
keyboard personalities. Bindings you've defined are in the gui.keymap-override section of
your ~/.wingide4/preferences file.

A Keybinding Example

I use the Emacs keyboard personality, and I usually type alt-keys rather than arrow keys
when there is a choice. I rebind the keys for the word commands to corresponding syllable
commands. I bind shifted versions of the move and delete commands to symbol commands, and
for the symbol-extend commands I use alt-shift left/right, replacing
forward/backward-extend-char-rect. I don't bother binding the Wing word commands, as I
almost always want the symbol or syllable behavior.

Here's what my preferences file keybindings look like for word, symbol, and syllable
commands. Note that each key is bound to the corresponding word command in addition to the
syllable/symbol. As described under #ImportantNote above, the syllable/symbol command will
take precedence when focus is in a document editor, while the word command will be invoked
when the key is used in a tool.

       'Alt-F': 'forward-syllable, forward-word',
       'Ctrl-Right': 'forward-syllable, forward-word',
       'Ctrl-Shift-right': 'forward-syllable-extend, forward-word-extend',
       'Alt-D': 'forward-delete-syllable, forward-delete-word',
       'Alt-Delete': 'forward-delete-syllable, forward-delete-word',
       'Alt-B': 'backward-syllable, backward-word',
       'Ctrl-Left': 'backward-syllable, backward-word',
       'Ctrl-Shift-left': 'backward-syllable-extend, backward-word-extend',
       'Alt-H': 'backward-delete-syllable, backward-word-syllable',
       'Alt-Backspace': 'backward-delete-syllable, backward-delete-word',
       'Alt-Shift-F': 'forward-symbol, forward-word',
       'Alt-Shift-D': 'forward-delete-symbol, forward-delete-word',
       'Alt-Shift-right': 'forward-symbol-extend, forward-word-extend',
       'Alt-Shift-Delete': 'forward-delete-symbol, forward-delete-word',
       'Alt-Shift-B': 'backward-symbol, backward-word',
       'Alt-Shift-left': 'backward-symbol-extend, backward-word-extend',
       'Alt-Shift-H': 'backward-delete-symbol, backward-delete-word',
       'Alt-Shift-Backspace': 'backward-delete-symbol, backward-delete-word',

"""

import wingapi
import string

_syllable_characters = string.lowercase + string.digits
_symbol_candidates = string.letters + string.digits
_symbol_characters = string.letters + string.digits + '_/'

def _forward_symbol(extendflg):
    wingapi.gApplication.GetActiveEditor().ExecuteCommand("forward-extend-word"
                                                          if extendflg
                                                          else "forward-word",
                                                          delimiters=_symbol_characters)
def forward_symbol():
    _forward_symbol(False)

def forward_symbol_extend():
    _forward_symbol(True)

def _forward_syllable(extendflg):
    editor = wingapi.gApplication.GetActiveEditor()
    doc =  editor.GetDocument()
    start, end = editor.GetSelection()
    cmd = "forward-word-extend" if extendflg else "forward-word"

    if (doc.GetCharRange(start, start+1) in string.uppercase and
        doc.GetCharRange(start+1, start+2) in string.uppercase):
        editor.ExecuteCommand(cmd, delimiters=string.uppercase, gravity='start')
    else:
        editor.ExecuteCommand(cmd, delimiters=_syllable_characters)

def forward_syllable():
    _forward_syllable(False)

def forward_syllable_extend():
    _forward_syllable(True)

def _backward_symbol(extendflg):
    editor = wingapi.gApplication.GetActiveEditor()
    editor.ExecuteCommand("backward-char-extend" if extendflg else "backward-char")
    editor.ExecuteCommand("backward-word-extend" if extendflg else "backward-word",
                          delimiters=_symbol_characters,
                          gravity='end')

def backward_symbol():
    _backward_symbol(False)

def backward_symbol_extend():
    _backward_symbol(True)

def _backward_syllable(extendflg):
    editor = wingapi.gApplication.GetActiveEditor()
    doc =  editor.GetDocument()
    start, end = editor.GetSelection()
    char_cmd = "backward-char-extend" if extendflg else "backward-char"
    word_cmd = "backward-word-extend" if extendflg else "backward-word"

    # back up until a letter or digit is previous char
    while (start >  0 and
           doc.GetCharRange(start-1, start) not in _symbol_candidates):
        start -= 1
        editor.ExecuteCommand(char_cmd)

    if doc.GetCharRange(start-1, start) not in string.uppercase:
        editor.ExecuteCommand(word_cmd,
                              delimiters=_syllable_characters,
                              gravity='end')
    start, end = editor.GetSelection()
    while doc.GetCharRange(start-1, start) in string.uppercase:
        start -= 1
        editor.ExecuteCommand(char_cmd)

def backward_syllable():
    _backward_syllable(False)

def backward_syllable_extend():
    _backward_syllable(True)

def _delete(movefn):
    """movefn must be one of:
        forward_syllable, backward_syllable, forward_symbol, backward_symbol"""
    editor = wingapi.gApplication.GetActiveEditor()
    doc = editor.GetDocument()
    start1, end1 = editor.GetSelection()
    movefn()
    start2, end2 = editor.GetSelection()
    # generalizing simplistically; may fix someday
    doc.DeleteChars(min(start1, end1, start2, end2),
                    max(start1, end1, start2, end2) - 1,
                    )

def forward_delete_symbol():
    _delete(forward_symbol)

def backward_delete_symbol():
    _delete(backward_symbol)

def forward_delete_syllable():
    _delete(forward_syllable)

def backward_delete_syllable():
    _delete(backward_syllable)

# copied from editor_extensions then compressed
# focus test added so these operate only when focus is in an editor --
# GetActiveEditor returns an editor if it is visible even if focus is
# in a tool. Keys should be bound to one of these, comma, standard word
# command
def _active_editor_exists():
    editor = wingapi.gApplication.GetActiveEditor()
    return editor and wingapi.wgtk.GetFocusChild(editor.fEditor._fScint)

forward_syllable_extend.available = _active_editor_exists
forward_delete_syllable.available = _active_editor_exists
backward_syllable.available = _active_editor_exists
backward_syllable_extend.available = _active_editor_exists
backward_delete_syllable.available = _active_editor_exists

forward_symbol.available = _active_editor_exists
forward_symbol_extend.available = _active_editor_exists
forward_delete_symbol.available = _active_editor_exists
backward_symbol.available = _active_editor_exists
backward_symbol_extend.available = _active_editor_exists
backward_delete_symbol.available = _active_editor_exists
