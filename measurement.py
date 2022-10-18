# -*- coding: utf-8 -*-
"""
`GPM8213LAN.measurement` implements the following classes:
    
:Measurement: instance of measuring to automate the measure process

:Measurement_mode: type of measurement with specific parameter

"""
from instrument import Instrument
from variable import variable_available
import time as tm

class Measurement():
    """
Creates a measurement Insantance to specify the **mode**, **devices** and `variables` to be measured. You have to specifies variables of each Instrument or use homogenize_variables(). Call the class to begin the measure.         

Parameters
----------
mode : *str* or *Measurement_mode*, optional
   'single' or 'continuous' or 'integrator'. The default is 'single'.
instruments : *list of Instrument* , optional
    GPMs, you are using. The default is [].

Returns
-------
None.

        """
    def __init__(self,mode ='single',instruments = []):

        if type(mode)!=Measurement_mode :
            self.mode = Measurement_mode(mode)
        else :
            self.mode = mode
        self.instruments = instruments
    def __str__(self):
        return "{}{}".format(self.mode, self.instruments)
    def __repr__(self):
        return "{}{}".format(self.mode, self.instruments)
    def __sizeof__(self):
        """
        

Returns
-------
int
    number of instrument.

        """
        return len(self.instruments)
    def __call__(self):
        results = []
        if self.mode.name=='single' :
            
            for instrument in self.instruments : 
                instrument.send_set(':NUM:NORM:VALUE?\r\n')
            
            for instrument in self.instruments :
                results.append(instrument.mesure_variable())
                results[-1]['Instrument']=instrument.__repr__()
        elif self.mode.name=='continuous':
            start=tm.time()
            while((tm.time()-start)<self.mode.time):
                start_sample =tm.time()
                for instrument in self.instruments : 
                    results.append(instrument.mesure_variable())
                    results[-1]['Instrument']=instrument.__repr__()
        return results
    def add_intruments(self,instrument):
        """
add an Instrument        

Parameters
----------
instrument : *Instrument*
   instrument to add.

Returns
-------
None.

        """
        if type(instrument)!=Instrument : 
            self.instruments.append(Instrument(instrument)) 
        else : 
            self.instruments.append(instrument) 
        return
    def homogenize_variables(self,variables=[],pattern=4): 
        """
change variables/Preset of each instrument

Parameters
----------
variables : *list of Variable*, optional
    variable to measure. The default is [].
pattern : *int* de 1 à 4, optional
    preset varaibles see page 94 and 95 of user manual. The default is 4.

Returns
-------
None.

        """
        if variables==[]:
            for instrument in self.instruments :
                instrument.change_pattern(pattern)
        else :
            for instrument in self.instruments :
                instrument.change_variables(variables)
        return
class Measurement_mode():
    """
defines type of measurment and its parameters

Parameters
----------
mode :*str* in : 
    single : one measure on  call.
    continuous : multiple single measure.
    integrator : interger power during time (see user manual p53).

Raises
------
TypeError
    if mode is not in 'single', 'continuous' and 'integrator'.

Returns
-------
None.

        """
    def __init__(self,mode):

        if ((mode!='single') and (mode!='continuous') and (mode!='integrator')):
            raise TypeError('must be a string (str) in single, continuous and integrator')
        self.name = mode
        self.specification()
    def specification(self,sample_time= 1,time = 10):
        """
defines time and sample time which will be use if necessary 

Parameters
----------
sample_time : *int*, optional
    sample time in secondes (continuous mode). The default is 1.
time : *int*, optional
    time in secondes (continuous and integrator mode). The default is 10.

Returns
-------
None.

        """
        self.sample_time = sample_time
        self.time = time
        return 
    def __str__(self):
        return "<{}>".format(self.name)
    def __repr__(self):
        return self.name