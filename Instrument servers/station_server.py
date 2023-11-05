import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import GUI_lib as glib
import Instrument_server as server


class stationService(server.generalInstrumentService):
    serviceName='station'

    def __init__(self) -> None:
        super().__init__()
        self.instruments={}
        self.experiments={}

    class ESR_GUI_module():
        def __init__(self,config:dict) -> None:
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


if __name__ == "__main__":
    server.createServer(stationService)