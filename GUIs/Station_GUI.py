import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import GUI_lib as glib

GUI=glib.Graphical_interface(designerFile='Station_idea')

GUI.run()