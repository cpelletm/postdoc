import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import GUI_lib_qt6 as glib

#Config file
def configDic():
    return glib.localVariableDic('ESR_GUI.yaml')

######################### Experimental module #########################

class experiment_module():
    def __init__(self,config) -> None:
        self.status_callbacks=[]
        self.data_callbacks=[]
        self.status=False
        self.fields={}
        self.config=config

    def start_acquisition(self):
        self.status=True
        self.fmin=self.fields['fmin'].value
        self.fmax=self.fields['fmax'].value
        self.npoints=self.fields['npoints'].value
        self.freqs=glib.np.linspace(self.fmin,self.fmax,self.npoints)
        self.data=glib.np.zeros(len(self.freqs))
        self.timer=glib.QTimer()
        self.timer.timeout.connect(self.acquire_data)
        self.timer.start(30)

    def acquire_data(self):
        self.data=glib.np.random.rand(self.npoints)
    

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

######################### Server setup #########################
# station_service=glib.rpyc.connect_by_service("STATION ON "+config['station'])
# station=station_service.root
# m=station.ESR_GUI_module(config=config)



######################### GUI #########################

def setup_GUI(config,m:experiment_module):
    GUI=glib.Graphical_interface(config=config)
    #Plotting figure
    fig=glib.pgFig(designerWidget=GUI.fig,config=config['fig'])
    ax=fig.addAx(axTitle='ESR')
    ax.setXLabel('Freq. (%s)'%(config['fmax']['unit']['name']))
    ax.setYLabel('PL (%s)'%(config['PL']['unit']['name']))
    x=glib.np.linspace(0,1,100)
    y=glib.np.zeros(len(x))
    l1=ax.addLine(x,y,typ='average')

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

    print(button_start.widget.actions())

    #Callbacks
    def update_status(status):
        if status:
            button_start.setEnabled(False)
            button_stop.setEnabled(True)
            l1.reset()
        else:
            button_start.setEnabled(True)
            button_stop.setEnabled(False)
    m.status_callbacks.append(update_status)
    m.status=False

    def update_l1(data):
        x=m.freqs
        x=x/config['fmax']['unit']['multiplier']
        y=data
        l1.update(x,y)
    m.data_callbacks.append(update_l1)

    return GUI




if __name__ == "__main__":
    qApp=glib.QApplication(sys.argv)
    config=configDic()
    m=experiment_module(config=config)
    GUI=setup_GUI(config=config,m=m)
    GUI.show()
    sys.exit(qApp.exec())


