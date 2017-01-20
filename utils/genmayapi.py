# This script generates *.pi files for auto-completion w/ Autodesk's Maya. 
# It should be run with Maya's standalone python interpreter -- bin\mayapy.exe 
# in the Maya install directory.


import os
import sys
import maya.standalone

WING_DIR = r'c:\Program Files (x86)\Wing IDE 3.2'
if not os.path.exists(WING_DIR):
    WING_DIR = r'c:\Program Files\Wing IDE 3.2'

sys.path.append(os.path.join(WING_DIR, 'src', 'wingutils'))
import generate_pi

PI_FILES_DIR = os.path.join(os.environ['AppData'], 'Wing IDE 3', 'pi-files')
MOD_LIST = [
    'maya.OpenMaya',
    'maya.OpenMayaAnim',
    'maya.OpenMayaCloth',
    'maya.OpenMayaFX',
    'maya.OpenMayaMPx',
    'maya.OpenMayaRender',
    'maya.OpenMayaUI',
    'maya.cmds',
    'maya.standalone',
    ]


def main():
    
                    
    maya.standalone.initialize()
    
    for mod in MOD_LIST:
        
        pi_filename = os.path.join(PI_FILES_DIR, os.sep.join(mod.split('.')) + '.pi')
        if not os.path.isdir(os.path.dirname(pi_filename)):
            os.makedirs(os.path.dirname(pi_filename))
            
        print 'Generating .pi file for', mod

        f = open(pi_filename, 'w')
        try:
            generate_pi.ProcessModule(mod, file=f)
        finally:
            f.close()
    
if __name__ == '__main__':
    main()
