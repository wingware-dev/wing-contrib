""" pygtk_to_pi.py -- setup pi files for PyGTK and gnome-python so
that that Wing IDE can offer auto-completion and other code 
intelligence features for PyGTK and gnome-print.

Version 0.6

Written by Stephan Deibel and John Ehresman

Copyright (c) 2004-2008, Wingware  All rights reserved.

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

Usage:
  
Change into the PyGTK or gnome-python source directory and run as follows:
  
python pygtk_to_pi.py .

This will write a *.pi file next to each *.so/*.pyd extension
module file.

You will also need to make sure Wing's source analyser can find your PyGTK or
gnome-python installation, by setting Python Path values using Project
Properties from the Project menu.

Implementation notes:

This code has only been tested against a built-in-place (not installed) copy
of PyGTK and gnome-python. For installed copies, the *.pi files can be copied
into place next to the corresponding *.so/*.pyd files.

Known problems:

* The documentation URL sometimes incorrect
* The *.pi files are not valid Python because the gtk defs contain
  functions, methods, and arguments that are Python keywords.
  They're close enough so that Wing's source analyser can read
  them.
* Would be nice to actually parse out the gtk documentation and
  add the appropriate docstrings in the *.pi files (and not 
  just documentation links)
* "Fields" in defs are ignored.

--------------------

Thanks to Brian Tipton for the gnome_python configuration

"""

import os
import sys

kUsePyGTKDocs = 1

if kUsePyGTKDocs:
  kBaseDocUrl = "http://www.pygtk.org/docs/pygtk"
else:
  kBaseDocUrl = "http://developer.gnome.org/doc/API/2.0"

#-----------------------------------------------------------------------
def _CreateDocUrl(module, class_cname, method_cname=None):
  """Create probably URL for documentation of given class or method."""
  
  # XXX Currently this only gets it right primarily for module gtk and
  # XXX rarely for gdk and others

  if module is None:
    return None

  if kUsePyGTKDocs:
    class_cname = class_cname.lower()
    if method_cname is not None:
      if method_cname == '__init__':
        method_cname = 'constructor-%s' % class_cname
      else:
        method_cname = method_cname.lower().replace('_', '-')
        method_cname = 'method-%s--%s' % (class_cname, method_cname)
      doc_url = "%s/class-%s.html#%s" % (kBaseDocUrl, class_cname, method_cname)
    else:
      doc_url = "%s/class-%s.html" % (kBaseDocUrl, class_cname)

  else:
    url_mod = module.lower()
    if url_mod == 'g':
      url_mod = 'gobject'

    if method_cname is not None:
      doc_url = "%s/%s/%s.html#%s" % (kBaseDocUrl, url_mod, class_cname, 
                                      method_cname.replace('_', '-'))
    else:
      doc_url = "%s/%s/%s.html" % (kBaseDocUrl, url_mod, class_cname)

  return doc_url

#-----------------------------------------------------------------------
class CFunction:

  def __init__(self, name, param_types, params, returns, comments, namespace, indent=0):
    self.name = name
    self.param_types = param_types
    self.params = params
    self.returns = returns
    self.comments = comments
    self.namespace = namespace
    self.indent = indent

  def __str__(self):
    returns = _CTypeToPythonDummyValue(self.returns, self.namespace)
    if self.name == '__init__':
      returns = 'self'
    if returns is not None:
      returns = 'return %s' % returns
    else:
      returns = 'pass'
    returns = '  ' * (self.indent + 1) + returns
    params = []
    for n, t in self.param_types:
      tstr = _CTypeToPythonTypeSpec(t, self.namespace)
      if not t.startswith('!'):
        tstr += ' (C type: %s)' % t
      params.append('     ' + n + ' -- ' + tstr)
    if len(params) > 0:
      params.insert(0, 'Parameter types:')
    comments = params + self.comments
    comments = '  ' * (self.indent + 1) + '"""%s"""' % ('\n' + '  ' * (self.indent + 1)).join(comments)

    return "%sdef %s(%s):\n%s\n%s" % ('  ' * self.indent,
                                      self.name,
                                      ', '.join(self.params),
                                      comments,
                                      returns)
  
#-----------------------------------------------------------------------
class CMethod(CFunction):

  def __init__(self, name, param_types, params, returns, comments, namespace):
    CFunction.__init__(self, name, param_types, ['self'] + params, returns, comments, namespace, indent=1)
    
#-----------------------------------------------------------------------
class CClass:

  def __init__(self, name, cname, module, cparents, fields, comments, namespace):
    self.name = name
    self.cname = cname
    self.module = module
    self.cparents = cparents
    self.fields = fields
    self.comments = comments
    self.def_found = False

    self.namespace = namespace
    self.namespace[cname] = self
    
    self.methods = {}
    
  def add_method(self, method):
    self.methods[method.name] = method
    
  def __str__(self):

    if not self.def_found:
      sys.stderr.write("Warning: No class defn for %s\n" % self.cname)

    # Add constructor now if one wasn't explicitly defined
    if not self.methods.has_key('__init__'):
      m = CMethod('__init__', [], [], self.name, ['Constructor'],
                  self.namespace)
      self.add_method(m)

    # Compute list of inherited Python classes
    inherits = []
    for cp in self.cparents:
      p = self.namespace.get(cp)
      if p is not None:
        inherits.append(p.name)
    if len(inherits) > 0:
      inherits = "(%s)" % ', '.join(inherits)
    else:
      inherits = ''

    # Write class definition
    retval = []
    retval.append('class %s%s:' % (self.name, inherits))
    if len(self.comments) > 0:
      retval.append('  """' + '\n  '.join(self.comments) + '"""')
    
    # XXX Currently ignoring fields

    # Write methods
    keys = self.methods.keys()
    keys.sort()
    for key in keys:
      method = self.methods[key]
      retval.append('')
      retval.append(str(method))
      
    return '\n'.join(retval)

#-----------------------------------------------------------------------
def StripQuotes(txt):
  if len(txt) > 1 and txt[0] == txt[-1] and txt[0] in '"\'':
    return txt[1:-1]
  else:
    return txt

#-----------------------------------------------------------------------
def ParseTuple(tokens, pos):
  """Parse tuple in tokens -- returns the tuple and position of next
  tuple"""

  assert tokens[pos] == '('

  i = pos + 1
  retval = []

  while i < len(tokens):
    t = tokens[i]
    if t == '(':
      sub_tuple, i = ParseTuple(tokens, i)
      retval.append(sub_tuple)
    elif t == ')':
      return tuple(retval), i + 1
    else:
      retval.append(t)
      i += 1
      
  assert 0, "Unexpected end of tokens in %s" % str(tokens)
      
#-----------------------------------------------------------------------
def _CTypeToPythonDummyValue(spec, namespace):
  """Convert C type into a dummy Python value that represents the type
  as far as source analysis of the resulting Python code is concerned"""
  
  spec = spec.strip()
  if spec.find('char*') >= 0:
    spec = '""'
  elif spec == 'gunichar':
    spec = 'u""'
  elif spec in ('guint', 'gint', 'guint32', 'gint32', 'int', 'uint', 'long', 'ulong',
                'guint*', 'gint*', 'guint32*', 'gint32*', 'int*', 'uint*', 'long*', 'ulong*'):
    spec = '0'
  elif spec == 'none':
    spec = None
  elif spec == 'gboolean':
    spec = '1'
  elif spec == 'gpointer':
    spec = '""  # Returns any value'
  elif spec == 'Function':
    spec = 'lambda x: x  # Returns a callable function'
  elif spec.startswith('!'):
    spec = spec[1:]
    if spec.startswith('tuple'):
      spec = '()'
    elif spec.startswith('list'):
      spec = '[]'
    elif spec.startswith('dict'):
      spec = '{}'
  elif spec == 'unspecified':
    spec = '""  # Unspecified type'
  else:
    if spec is not None:
      while len(spec) > 0 and spec.endswith('*'):
        spec = spec[:-1]
    if namespace.has_key(spec):
      spec = namespace[spec].name
    spec += "()"
  return spec

#-----------------------------------------------------------------------
def _CTypeToPythonTypeSpec(spec, namespace):
  """Convert a C type into a human-readable type specification appropriate
  for use in Python code"""
  
  spec = spec.strip()
  if spec.find('char*') >= 0:
    spec = 'string'
  elif spec == 'gunichar':
    spec = 'unicode string'
  elif spec in ('guint', 'gint', 'guint32', 'gint32', 'int', 'uint', 'long', 'ulong',
                'guint*', 'gint*', 'guint32*', 'gint32*', 'int*', 'uint*', 'long*', 'ulong*'):
    spec = 'integer'
  elif spec == 'none':
    spec = 'None'
  elif spec == 'gboolean':
    spec = 'boolean'
  elif spec == 'gpointer':
    spec = 'any value'
  elif spec == 'Function':
    spec = 'a callable'
  elif spec.startswith('!'):
    spec = spec[1:]
  elif spec == 'unspecified':
    spec = 'unspecified type'
  else:
    if spec is not None and spec.endswith('*'):
      while len(spec) > 0 and spec.endswith('*'):
        spec = spec[:-1]
    if namespace.has_key(spec):
      spec = namespace[spec].name
    spec = 'instance of %s' % spec

  return spec

#-----------------------------------------------------------------------
def __CValueToPythonValue(value):
  """Convert a C value to corresponding Python value"""
  
  if value == 'NULL':
    value = 'None'
  elif value.startswith('GDK_'):
    value = value.replace('GDK_', '')
  elif value.startswith('GTK_'):
    value = value.replace('GTK_', '')
  elif value.lower() == 'true':
    value = '1'
  elif value.lower() == 'false':
    value = '0'
  return value

#-----------------------------------------------------------------------
def ParseDefsFile(filename, namespace={}, cnames={}):
  """Parse a def file into a representation of the interface being described"""

  sys.stderr.write("Parsing defs file %s\n" % filename)
  
  from codegen import scmexpr
  
  all_toplevels = []
  for toplevel in scmexpr.parse(filename):
    if len(toplevel) == 0:
      continue

    if toplevel[0] == 'ifdef':
      all_toplevels.extend(toplevel[1:])
    else:
      all_toplevels.append(toplevel)
    
  for toplevel in all_toplevels:
    if toplevel[0] == 'include':
      subfile = os.path.join(os.path.dirname(filename), toplevel[1])
      ParseDefsFile(subfile, namespace, cnames)
    else:
      ParseTopLevel(toplevel, namespace, cnames)
      
  return namespace

def ParseTopLevel(tokens, namespace, cnames):
  def_type, def_name = tokens[:2]
  def_body = tokens[2:]
  def_name = StripQuotes(def_name)
  def_dict = {}
  for t in def_body:
    tup = t[1:]
    if def_dict.has_key(t[0]):
      l = list(def_dict[t[0]])
      l.extend(tup)
      def_dict[t[0]] = tuple(l)
    else:
      def_dict[t[0]] = tup

  # Class definition
  if def_type in ('define-object', 'define-interface', 'define-enum',
                  'define-flags'):

    # Extract values from parse
    module_info = def_dict.get('in-module')
    if module_info is not None:
      module = StripQuotes(module_info[0])
    else:
      module = None
    cparent = def_dict.get('parent')
    if cparent is not None:
      cparent = StripQuotes(cparent[0])
      cparents = [cparent]
    else:
      cparents = []
    implements = def_dict.get('implements', [])
    for impl in implements:
      cparents.append(StripQuotes(impl))
    fields = def_dict.get('fields', [])
    def_fields = []
    for field in fields:
      def_fields.append((StripQuotes(field[0]), StripQuotes(field[1])))
    class_cname = StripQuotes(def_dict.get('c-name')[0])

    comments = []
    doc_url = _CreateDocUrl(module, class_cname)
    comments.append("Docs: %s " % doc_url)

    # Update existing class (created previously if method def seen first)
    if namespace.has_key(class_cname):
      c = namespace[class_cname]
      c.name = def_name
      c.module = module
      c.cparents = cparents
      c.fields = def_fields
      c.comments = comments
      
    # Create new class
    else:
      c = CClass(def_name, class_cname, module, cparents, def_fields, comments, namespace)

    cnames[class_cname] = c
    c.def_found = True

  # Function or method definition
  else:

    # Extract parameters from parse
    def_params = list(def_dict.get('parameters', ()))
    python_params = []
    param_types = []
    for p in def_params:
      argname = StripQuotes(p[1]).strip()
      # Compensate for bugs in some defs entries
      if argname.startswith('(*'):
        argname = argname[2:]
      if argname.startswith('*'):
        argname = argname[1:]
      param_types.append((argname, StripQuotes(p[0])))
      if len(p) == 3 and p[-1][0] == 'default':
        default = StripQuotes(p[-1][-1]).strip()
        default = __CValueToPythonValue(default)
        python_params.append(StripQuotes(p[1]).strip() + '=' + default)
      else:
        python_params.append(argname)

    # Extract return type from parse
    def_returns = def_dict.get('return-type', ('none',))
    def_returns = StripQuotes(def_returns[0]).strip()

    # Extract comment info from parse
    comments = []
    if def_dict.has_key('deprecated'):
      comments.append("Deprecated: %s" % StripQuotes(def_dict['deprecated'][0]).strip())
    if def_dict.has_key('c-name'):
      cname = StripQuotes(def_dict['c-name'][0]).strip()
      comments.append("C impl: %s()" % cname)
    else:
      cname = None
    def_comments = comments

    # Constructors are functions we treat as __init__ methods
    # XXX Generation of __init__ is probably not always entirely correct
    if def_dict.has_key('is-constructor-of'):
      def_name = '__init__'
      def_type = 'define-method'
      def_dict['of-object'] = def_dict['is-constructor-of']
      def_returns = StripQuotes(def_dict['is-constructor-of'][0])
      # Newer versions of pygtk use properties-based constructors
      props = def_dict.get('properties')
      if props is not None:
        python_params = []
        param_types = []
        for prop in props:
          python_params.append(StripQuotes(prop[0]))
          param_types.append((StripQuotes(prop[0]), 'unspecified'))
          
    # Function definition
    if def_type == 'define-function':
      fct = CFunction(def_name, param_types, python_params, def_returns,
                      def_comments, namespace)
      namespace[def_name] = fct
      if cname is not None:
        cnames[cname] = fct

    # Method definition
    elif def_type == 'define-method':
      class_cname = StripQuotes(def_dict.get('of-object')[0])
      if namespace.has_key(class_cname):
        c = namespace[class_cname]
        module = c.module
      else:
        # Place holder that will get updated when class def is found
        default_name = class_cname
        if default_name.startswith('Gtk'):
          default_name = default_name[3:]
          module = 'Gtk'
        else:
          module = None
        c = CClass(default_name, class_cname, module, [], [], [], namespace)
        cnames[class_cname] = c
    
      if module is not None and cname is not None:
        if kUsePyGTKDocs:
          doc_url = _CreateDocUrl(module, class_cname, def_name)
        else:
          doc_url = _CreateDocUrl(module, class_cname, cname)
        def_comments.append("Docs: %s " % doc_url)

      # Prefer duplicate with longer list of args, since that's generally more
      # complete -- this is mainly used for __init__
      if not c.methods.has_key(def_name) or len(c.methods[def_name].params) <= len(python_params) + 1:                
        m = CMethod(def_name, param_types, python_params, def_returns, def_comments, namespace)
        c.add_method(m)
        if cname is not None:
          cnames[cname] = m
        

#-----------------------------------------------------------------------
def _ResolveCExpr(code, expr, pos):
  """Look up the C expression that is assigned to the variable given
  in expr, if it is not already an expression.  Looks backwards in
  given code starting at given position."""
  
  if expr.find('(') >= 0 or expr == 'Py_None':
    return expr
    
  assign = code.rfind(expr + ' = ', 0, pos)
  if assign < 0:
    return None

  spos = assign + len(expr + ' = ')
  retval = code[spos:code.find(';', spos)]
  return _ResolveCExpr(code, retval, assign - 1)

#-----------------------------------------------------------------------
def _ArgSpecToCType(spec):
  """Convert arg spec in form used for Py_BuildValue and Py_ParseArgs
  into appropriate CType that can later be converted to Python type using
  _CTypeToPythonDummyValue()"""

  sub_part = ""
  cspec = []
  
  paren_count = 0
  bracket_count = 0
  dict_count = 0

  i = 0
  while i < len(spec):
    c = spec[i]

    if c == '(':
      paren_count += 1
    elif c == ')':
      paren_count -= 1
      if paren_count + bracket_count + dict_count == 0:
        cspec.append('tuple(' + ', '.join(_ArgSpecToCType(sub_part)) + ')')
        sub_part = ""

    elif c == '[':
      bracket_count += 1
    elif c == ']':
      bracket_count -= 1
      if paren_count + bracket_count + dict_count == 0:
        cspec.append('list(' + ', '.join(_ArgSpecToCType(sub_part)) + ')')
        sub_part = ""

    elif c == '{':
      dict_count += 1
    elif c == '}':
      dict_count -= 1
      if paren_count + bracket_count + dict_count == 0:
        cspec.append('dict(' + ', '.join(_ArgSpecToCType(sub_part)) + ')')
        sub_part = ""

    elif paren_count + bracket_count + dict_count > 0:
      sub_part += c

    else:
      if c in ('#', '&', '!', '|'):
        pass
      elif c in ('s', 'z'):
        cspec.append('string')
      elif c == 'u':
        cspec.append('unicode')
      elif c in ('i', 'b', 'h', 'l'):
        cspec.append('integer')
      elif c == 'c':
        cspec.append('char')
      elif c == 'd':
        cspec.append('float')
      elif c == 'D':
        cspec.append('complex')
      elif c in ('O', 'S', 'U', 'N'):
        cspec.append('object')
      else:
        cspec.append('unspecified')
        
    i += 1
      
  return cspec
  
#-----------------------------------------------------------------------
def _ArgSpecToArgTypes(argnames, spec):
  """Convert arg spec in form used for PyArg_ParseTuple* calls into a
  list of (argname, ctype) where the types can later be converted to 
  Python type using _CTypeToPythonTypeSpec()"""

  sub_part = ""
  cspec = []
  
  paren_count = 0
  bracket_count = 0
  dict_count = 0

  i = 0
  argpos = 0
  while i < len(spec) and argpos < len(argnames):
    c = spec[i]

    if c == '(':
      paren_count += 1
    elif c == ')':
      paren_count -= 1
      if paren_count + bracket_count + dict_count == 0:
        cspec.append((argnames[argpos], '!tuple(' + ', '.join(_ArgSpecToCType(sub_part)) + ')'))
        argpos += 1
        sub_part = ""

    elif c == '[':
      bracket_count += 1
    elif c == ']':
      bracket_count -= 1
      if paren_count + bracket_count + dict_count == 0:
        cspec.append((argnames[argpos], '!list(' + ', '.join(_ArgSpecToCType(sub_part)) + ')'))
        argpos += 1
        sub_part = ""

    elif c == '{':
      dict_count += 1
    elif c == '}':
      dict_count -= 1
      if paren_count + bracket_count + dict_count == 0:
        cspec.append((argnames[argpos], '!dict(' + ', '.join(_ArgSpecToCType(sub_part)) + ')'))
        argpos += 1
        sub_part = ""

    elif paren_count + bracket_count + dict_count > 0:
      sub_part += c

    else:
      if c in ('&', '|'):
        pass
      elif c in ('!', '#'):
        cspec[-1] = ((argnames[argpos], cspec[-1][1] + ' (C type: %s)' % cspec[-1][0]))
        argpos += 1
      elif c in ('s', 'z'):
        cspec.append((argnames[argpos], '!string'))
        argpos += 1
      elif c == 'u':
        cspec.append((argnames[argpos], '!unicode'))
        argpos += 1
      elif c in ('i', 'b', 'h', 'l'):
        cspec.append((argnames[argpos], '!integer'))
        argpos += 1
      elif c == 'c':
        cspec.append((argnames[argpos], '!char'))
        argpos += 1
      elif c == 'd':
        cspec.append((argnames[argpos], '!float'))
        argpos += 1
      elif c == 'D':
        cspec.append((argnames[argpos], '!complex'))
        argpos += 1
      elif c in ('O', 'S', 'U', 'N'):
        cspec.append((argnames[argpos], '!object'))
        argpos += 1
      else:
        cspec.append((argnames[argpos], 'unspecified'))
        argpos += 1
        
    i += 1
      
  return cspec
  
#-----------------------------------------------------------------------
def _CExprToCType(expr):
  """Determine the C type for the given C expression, in such a way
  that the Python type can later be determined with _CTypeToPythonDummyValue()"""

  expr = expr.strip()
  
  if expr == 'Py_None':
    return 'NULL'
  elif expr.startswith('PyInt'):
    return 'int'
  elif expr.startswith('PyString'):
    return 'char *'
  elif expr.startswith('PyUnicode'):
    return '!unicode'
  elif expr.startswith('PyObject_Is'):
    return 'gboolean'
  elif expr.startswith('PyTuple'):
    return 'tuple'
  elif expr.startswith('PyList'):
    return 'list'
  elif expr.startswith('PyDict'):
    return 'dict'
  elif expr.startswith('pyg_value_as_pyobject') or expr.startswith('pyg_object_new'):
    return '!object'
  elif expr.startswith('pyg_boxed_new('):
    args = expr[len('pyg_boxed_new('):-2]
    args = [a.strip() for a in args.split(',')]
    return '!object (GTYPE=%s)' % args[0]
  
  # expr in form: x ? Py_True : Py_False;
  parts = [x.strip() for x in expr.strip().split()]
  if (len(parts) >= 5 and parts[-1].endswith(';') and 
      (parts[-1].find('Py_False') >= 0 or parts[-1].find('Py_True') >= 0) and
      parts[-2] == ':' and parts[-3] in ('Py_True', 'Py_False') and parts[-4] == '?'):
    return 'gboolean'

  if expr.startswith('Py_BuildValue('):
    args = expr[len('Py_BuildValue('):-2]
    args = [a.strip() for a in args.split(',')]
    argspec = args[0][1:-1]
    ctype = _ArgSpecToCType(argspec)
    if len(ctype) > 1:
      ctype = '!tuple(' + ', '.join(ctype) + ')'
    elif len(ctype) == 1:
      ctype = '!' + ctype[0]
    else:
      sys.stderr.write('Warning: Empty Py_BuildValue spec for %s\n' % fct)
      ctype = 'unspecified'
    return ctype
  
  # Could not determine type
  return None

#-----------------------------------------------------------------------
def _GetArgs(code, pos):
  """Get arguments for function at given position"""
  
  paren_count = 1
  start = code.find('(', pos)
  if start == -1:
    return None

  i = start + 1
  while i < len(code):
    c = code[i]
    if c == '(':
      paren_count += 1
    elif c == ')':
      paren_count -= 1
    if paren_count == 0:
      return code[start:i]
    i += 1

  return None
  
#-----------------------------------------------------------------------
def _ExtractParseTupleAndKeywords(fct, code, pos):
  """Attempt to extract list of (name, ctype) from PyArg_ParseTupleAndKeywords
  call in given code"""

  pos = code.find('PyArg_ParseTupleAndKeywords(', pos)
  if pos == -1:
    return None

  args = _GetArgs(code, pos)
  args = [a.strip() for a in args.split(',')]
  if len(args) < 4:
    sys.stderr.write("Warning: Malformed PyArg_ParseTupleAndKeywords call for %s\n" % fct)
    return None
  argspeck = args[2][1:-1]
  argspec = argspeck.split(':')
  if len(argspec) < 2:
    argspec = argspeck.split(';')
  if len(argspec) < 2:
    argspec = argspeck
  else:
    argspec = argspec[0]

  argnames = [a[1:] for a in args[4:]]
  retval = _ArgSpecToArgTypes(argnames, argspec)

  return retval  

#-----------------------------------------------------------------------
def _ExtractParseTuple(fct, code, pos):
  """Attempt to extract list of (name, ctype) from PyArg_ParseTupleAndKeywords
  call in given code"""

  pos = code.find('PyArg_ParseTuple(', pos)
  if pos == -1:
    return None

  args = _GetArgs(code, pos)
  args = [a.strip() for a in args.split(',')]
  if len(args) < 2:
    sys.stderr.write("Warning: Malformed PyArg_ParseTuple call for %s\n" % fct)
    return None
  argspeck = args[1][1:-1]
  argspec = argspeck.split(':')
  if len(argspec) < 2:
    argspec = argspeck.split(';')
  if len(argspec) < 2:
    argspec = argspeck
  else:
    argspec = argspec[0]

  argnames = [a[1:] for a in args[2:]]
  retval = _ArgSpecToArgTypes(argnames, argspec)

  return retval  

#-----------------------------------------------------------------------
def _ExtractKWArgTypes(fct, code):
  """Extract list of (name, ctype) for kwargs type function defn
  in the given code"""
 
  start = code.find('_wrap_')
  if start == -1:
    sys.stderr.write("Warning: could not find _wrap_ fct for %s\n" % fct)
    start = 0

  retval = _ExtractParseTupleAndKeywords(fct, code, start)
  if retval is not None:
    return retval
  
  retval = _ExtractParseTuple(fct, code, start)
  if retval is not None:
    return retval
  
  sys.stderr.write("Warning: could not find arg parsing code for %s\n" % fct)
  return None

#-----------------------------------------------------------------------
def _ExtractReturnType(fct, code):
  """Extract return type (as ctype) for function def in the given code"""

  start = code.rfind('_wrap_')
  if start == -1:
    sys.stderr.write("Warning: could not find _wrap_ fct for %s\n" % fct)
    start = 0

  # Return type is defined by first non-NULL return statement in
  # the _wrap_ function (or first in code if couldn't find _wrap_)
  retpos = code.find('return ', start) + len('return ')
  while retpos >= 0:
    retexpr = code[retpos:code.find(';', retpos)]
    retexpr = _ResolveCExpr(code, retexpr, retpos - len('return ') - 1)
    if retexpr != 'NULL' and retexpr != None:
      ctype = _CExprToCType(retexpr)
      if ctype is not None:
        return ctype
    retpos = code.find('return ', retpos)
    if retpos >= 0 :
      retpos += len('return ')

  sys.stderr.write("Warning: Unknown return type for %s\n" % fct)
  return 'NULL'
    
#-----------------------------------------------------------------------
def ParseOverridesFile(override_file, namespace, cnames):
  """Parse given overrides file and add/update interface info in
  given name space"""

  sys.stderr.write("Parsing override file %s\n" % override_file)
  
  from codegen import override
  o = override.Overrides(override_file)
  
  for fct, code in o.overrides.items():
    defn = cnames.get(fct)
    if isinstance(defn, CFunction):
      if o.wants_kwargs(fct):
        param_types = _ExtractKWArgTypes(fct, code)
        returns = _ExtractReturnType(fct, code)
      elif o.wants_noargs(fct):
        param_types = []
        returns = _ExtractReturnType(fct, code)
      else:
        param_types = _ExtractKWArgTypes(fct, code)
        returns = _ExtractReturnType(fct, code)
        
      if param_types is not None:
        defn.param_types = param_types
        defn.params = [n for n, t in param_types]
      if returns is not None:
        defn.returns = returns
        
    else:
      sys.stderr.write("Warning: Could not look up override %s\n" % fct)

  # These can be ignored as they don't add any info not already obtained
  # from the defs file:

  #for fct, code in o.override_attrs.items():
    #obj, attr = fct.split('.')
    #defn = cnames.get(obj)
    #pass
  
  #for fct, code in o.override_slots.items():
    #obj, slot = fct.split('.')
    #defn = cnames.get(obj)
    #pass
    
def LoadFlagsAndEnums(mod_name, namespace):

  try:
    import gobject
  except Exception:
    gobject = None
  try:
    mod = __import__(mod_name, fromlist=[''])
  except Exception:
    return
  
  py_names = {}
  for value in namespace.itervalues():
    py_names[value.name] = value
  
  for name, value in mod.__dict__.iteritems():
    if name in py_names:
      continue
    
    rhs = None
    if gobject is not None and isinstance(value, (gobject.GFlags, gobject.GEnum)):
      int_literal = '0'
      if isinstance(value, gobject.GFlags):
        try:
          int_literal = hex(value)
        except Exception:
          pass
      else:
        try:
          int_literal = int(value)
        except Exception:
          pass

      type_obj = type(value)
      if type_obj.__name__ in py_names:
        rhs = '%s(%s)' % (type_obj.__name__, int_literal)
      else:
        rhs = int_literal
    elif isinstance(value, (basestring, int, long, float)):
      rhs = repr(rhs)                            
    else:
      #print name
      pass

    if rhs is not None:
      namespace[name] = '%s = %s' % (name, rhs)

class CGenerateOneModule:
  
  def __init__(self, def_files, mod_name, output_dir):
    
    self.namespace = {}
    self.cnames = {}
    self.def_files = def_files
    self.mod_name = mod_name
    self.output_dir = output_dir
    
  def Generate(self):
    # Parse the defs file (if it exists)
    for src in self.def_files:
      if os.path.exists(src):
        ParseDefsFile(src, self.namespace, self.cnames)
      
      # Parse overrides files (if it exists)
      override = src[:-5] + '.override'
      if os.path.exists(override):
        ParseOverridesFile(override, self.namespace, self.cnames)
        
    if len(self.namespace) != 0:
      LoadFlagsAndEnums(self.mod_name, self.namespace)
  
    # Write the PI output file if the name space is not empty
    if len(self.namespace) > 0:
      dest = os.path.join(self.output_dir, 
                          self.mod_name.replace('.', os.sep) + '.pi')
      try:
        os.makedirs(os.path.dirname(dest))
      except OSError:
        pass
      f = open(dest, 'w')
      for key, value in sorted(self.namespace.items()):
        py_src = str(value)
        if py_src.lstrip().startswith('class') or py_src.lstrip().startswith('def'):
          f.write('\n')
        f.write(py_src + '\n')
      f.close()

def GenerateModuleList(gen_list, output_dir):
  
  for mod_name, def_files in gen_list:
    gen = CGenerateOneModule(def_files, mod_name, output_dir)
    gen.Generate()

def GetModuleList(dirname):
  
  mod_list = [
    # pygtk modules
    ('gtk._gtk', ['gtk/gtk-base.defs', 'gtk/gtk-2.10.defs', 'gtk/gtk.defs']),
    ('gtk.gdk', ['gtk/gdk-base.defs', 'gtk/gdk-2.10.defs', 'gtk/gdk.defs']),
    ('gtk.glade', ['gtk/libglade.defs']),
    ('atk', ['atk.defs']),
    ('pango', ['pango.defs']),
    ('pangocairo', ['pangocairo.defs']),
    # gnome-python modules
    ('gnome._gnome', ['gnome/gnome.defs']),
    ('gnome.ui', ['ui.defs']),
    ('gconf', ['gconf/gconf.defs']),
    ('gnomecanvas', ['gnomecanvas/canvas.defs']),
    # gnome-python-desktop
    ('gnomeapplet', ['gnomeapplet/applet.defs']),
    ('gnomedesktop._gnomedesktop', ['gnomedesktop/_gnomedesktop.defs']),
    ('gnomekeyring', ['gnomekeyring/gnomekeyring.defs']),
    ('gnomeprint._print', ['gnomeprint/print.defs']),
    ('gnomeprint.ui', ['gnomeprint/printui.defs']),
    ('gtksourceview', ['gtksourceview/gtksourceview.defs']),
    ('mediaprofiles', ['mediaprofiles/mediaprofiles.defs']),
    ('metacity', ['metacity/metacity.defs']),
    ('nautilusburn', ['nautilusburn/nautilus_burn.defs']),
    ('rsvg', ['rsvg/rsvg.defs']),
    ('totem.plparser', ['totem/plparser.defs']),
    ('wnck', ['wnck/wnck.defs']),
    
    # gnome-python-extras
    ('egg.tray', ['egg/tray/trayicon.defs']),
    ('egg.recent', ['egg/recent/eggrecent.defs']),
    ('gda', ['gda/gda.defs']),
    ('gdl', ['gdl/gdl.defs']),
    ('gksu._gksu', ['gksu/gksu.defs']),
    ('gksu.ui', ['gksu/gksuui.defs']),
    ('gtkhtml2', ['gtkhtml2/gtkhtml2.defs']),
    ('gtkmozembed', ['gtkmozembed/gtkmozembed.defs']),
    ('gtkspell', ['gtkspell/gtkspell.defs']),
  ]

  ret_list = []
  for modname, def_list in mod_list:
    pair = (modname, [os.path.join(dirname, defname) for defname in def_list])
    ret_list.append(pair)
    
  return ret_list

def FindDirForCodegen(argv):
  
  codegen_prefix = '--codegen-dir='
  for a in argv:
    if a.startswith(codegen_prefix):
      return a[len(codegen_prefix):]

  for a in argv:
    if a.startswith('-') or '=' in a:
      continue
    
    init_name = os.path.join(a, 'codegen', '__init__.py')
    if os.path.isfile(init_name):
      return a
    
  return None

############################################################################

def main(argv):
  """ Process any arg that doesn't begin with '-' as a directory
  with pygtk / gnome-python-* source trees.  Two other arguments
  are recognized:
    --output-dir: directory to write .pi files to; defaults to
      source directories if not specified.
    --codegen-dir: directory that the codegen package is in
      as a subdirectory.  Searches all other directory entries
      and uses default sys.path if not specified.
  """
  
  
  codegen_dir = FindDirForCodegen(argv)
  if codegen_dir is not None:
    sys.path.append(codegen_dir)

  output_dir = None
  for a in argv:
    output_dir_prefix = '--output-dir='
    if a.startswith(output_dir_prefix):
      output_dir = a[len(output_dir_prefix):]
      break

  for a in argv:
    if a.startswith('-'):
      continue
    
    mod_list = GetModuleList(a)
    if output_dir is not None:
      mod_output_dir = output_dir
    else:
      mod_output_dir = a
    GenerateModuleList(mod_list, mod_output_dir)

if __name__ == '__main__':

  main(list(sys.argv))
