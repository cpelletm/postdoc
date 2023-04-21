import GUI_lib as gui
import Mat_data_processing as mat




class plot2DGUI(gui.Graphical_interface):
    def __init__(self):
        itemLists=[]
        super().__init__(*itemLists, title='2D plot')