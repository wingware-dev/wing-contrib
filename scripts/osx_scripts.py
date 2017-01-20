"""
This module exposes two wingide extension scripts. place this file on your 
user defined scripts path.

The scripts are added to your 'Scripts' menu by default.

The exposed scripts are:

open_osx_finder_in_project_dir() - opens an osx finder in your project 
                                   directory.
open_osx_terminal_in_project_dir() - opens an osx terminal in your project
                                     directory by running an osascript.

Note that if Terminal is not already running an initial default terminal 
window is opened before the one in your project directory. you can just
close this extra terminal window. this is a limitation of appscript.

Written by Steven M Gava

"""

import os
import wingapi

def open_osx_terminal_in_project_dir():
    """
    open an osx Terminal.app console in the project directory by
    running an osascript.
    """
    term_cmd_str="cd "+_get_current_project_dir()
    _run_command_with_args_in_project_dir("osascript",
                    '-e tell application "Terminal"',
                    "-e activate",
                    '-e do script with command "'+term_cmd_str+'"',
                    "-e end tell")

open_osx_terminal_in_project_dir.contexts=[wingapi.kContextNewMenu('Sc_ripts')]

def open_osx_finder_in_project_dir():
    """
    open an osx finder window in the project directory.
    """
    _run_command_with_args_in_project_dir('open',_get_current_project_dir())

open_osx_finder_in_project_dir.contexts=[wingapi.kContextNewMenu('Sc_ripts')]
    
def _run_command_with_args_in_project_dir(command_str,*args):
    """
    runs a command (with args) in the project directory.
    """
    project_dir=_get_current_project_dir()
    _run_command_with_args_in_dir(command_str,project_dir,*args)

def _run_command_with_args_in_dir(command_str,dir_str,*args):
    """
    runs a command (with args) in the specified directory.
    """
    app=wingapi.gApplication
    handler=app.AsyncExecuteCommandLine(command_str,dir_str,*args)
   
def _get_current_project_dir():
    """
    returns the current project directory.
    """
    app=wingapi.gApplication
    project=app.GetProject()
    project_filename=project.GetFilename()
    project_dirname=os.path.abspath(os.path.dirname(project_filename))
    return project_dirname
