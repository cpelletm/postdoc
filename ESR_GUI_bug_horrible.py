import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import GUI_lib as glib

#Config file
config=glib.localVariableDic('ESR_GUI.yaml')
GUI=glib.Graphical_interface(config=config)
######################### Experimental module #########################

class experiment_module():
    def __init__(self) -> None:
        self.status_callbacks=[]
        self.data_callbacks=[]
        self.status=False
        self.fields={}

    def start_acquisition(self):
        self.status=True
        print(self.fields['fmin'].value)
        self.timer=glib.QTimer()
        self.timer.timeout.connect(self.acquire_data)
        self.timer.start(1000)

    def acquire_data(self):
        self.data=glib.np.random.rand(100)
    

    def stop_acquisition(self):
        self.timer.stop()
        self.status=False

    @property
    def status(self):
        return self._status
    
    @status.setter
    def status(self,value):
        self._status=value
        for callback in self.status_callbacks:
            callback(self._status)

    @property
    def data(self):
        return self._data
    @data.setter
    def data(self,value):
        self._data=value
        for callback in self.data_callbacks:
            callback(self._data)

######################### GUI #########################

def setup_GUI(GUI,config,m:experiment_module):

    #Plotting figure
    fig=glib.pgFig(designerWidget=GUI.fig,config=config['fig'])
    ax=fig.addAx(axTitle='ESR')
    ax.setXLabel('Freq. (%s)'%(config['fmax']['unit']['name']))
    ax.setYLabel('PL (%s)'%(config['PL']['unit']['name']))
    x=glib.np.linspace(0,1,100)
    y=glib.np.zeros(len(x))
    l1=ax.addLine(x,y)

    #Fields
    fmin=glib.field(labelDesignerWidget=GUI.label_fmin,lineDesignerWidget=GUI.line_fmin,config=config['fmin'],module=m)
    fmax=glib.field(labelDesignerWidget=GUI.label_fmax,lineDesignerWidget=GUI.line_fmax,config=config['fmax'],module=m)
    power=glib.field(labelDesignerWidget=GUI.label_power,lineDesignerWidget=GUI.line_power,config=config['power'],module=m)
    npoints=glib.field(labelDesignerWidget=GUI.label_npoints,lineDesignerWidget=GUI.line_npoints,config=config['npoints'],module=m)
    dt=glib.field(labelDesignerWidget=GUI.label_dt,lineDesignerWidget=GUI.line_dt,config=config['dt'],module=m)

    experiment_name=glib.field(labelDesignerWidget=GUI.label_experiment_name,lineDesignerWidget=GUI.line_experiment_name,config=config['experiment_name'],module=m)
    sample_name=glib.field(labelDesignerWidget=GUI.label_sample_name,lineDesignerWidget=GUI.line_sample_name,config=config['sample_name'],module=m)

    #Buttons
    button_start=glib.button(designerWidget=GUI.button_start)
    button_stop=glib.button(designerWidget=GUI.button_stop)
    button_add_fit=glib.button(designerWidget=GUI.button_add_fit)
    button_remove_fit=glib.button(designerWidget=GUI.button_remove_fit)
    button_config_fit=glib.button(designerWidget=GUI.button_config_fit)
    button_add_trace=glib.button(designerWidget=GUI.button_add_trace)
    button_remove_trace=glib.button(designerWidget=GUI.button_remove_trace)

    button_save=glib.saveButton(fig=fig,config=config['save'],designerWidget=GUI.button_save,exp_name=experiment_name,sample_name=sample_name)

    #Actions
    button_start.setAction(m.start_acquisition)
    button_stop.setAction(m.stop_acquisition)

    def debug():
        print('debug')
        print(dir(m)) #without this line the code does not run. Makes no sense at all
        
    button_add_fit.setAction(debug)

    #Callbacks
    def update_status(status):
        if status:
            button_start.setEnabled(False)
            button_stop.setEnabled(True)
        else:
            button_start.setEnabled(True)
            button_stop.setEnabled(False)
    m.status_callbacks.append(update_status)
    m.status=False


######################### Server setup #########################

station_connect=glib.stationConnect(buttonDesignerWidget=GUI.button_station_connect,comboBoxDesignerWidget=GUI.combo_station ,config=config['station'])
for widget in GUI.centralWidget().children():
    if widget==GUI.button_station_connect or widget==GUI.combo_station:
        continue
    else:
        try :
            widget.setEnabled(False)
        except:
            pass


def connect_action():   
    for widget in GUI.centralWidget().children():
        if widget==GUI.button_station_connect or widget==GUI.combo_station:
            continue
        else:
            try :
                widget.setEnabled(True)
            except:
                pass
    m=experiment_module()
    setup_GUI(GUI=GUI,config=config,m=m)

station_connect.setAction(connect_action)

if __name__ == "__main__":
    GUI.run()


