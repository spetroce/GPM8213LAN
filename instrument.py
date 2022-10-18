# -*- coding: utf-8 -*-
"""
`GPM8213LAN.instrument` implements the following classes:
    
:Instrument: High-level of GPM representation

"""
from variable import Variable
import time as tm
import socket as sk
import numpy as np

# =============================================================================
# in next realese : 
#         methode to change the parameters and screens 
#         continous mode
#         integrator mode
#         link to user manual in documentation
# =============================================================================
class Instrument():
    """
        

Parameters
----------
HOST : *str*
    local ip address of the GPM (voir System > Congig > LAN on the GPM)..
PORT : *int*, optional
    23 for the GPM ,Telnet protocol. The default is 23.
timeout : *float*, optional
    time seconds to raise an error. 
variables : *list of Variable*, optional
    variables to measure. The default is [].
pattern : *int* de 1 à 4 , optional
    preset varaibles see page 94 and 95 of user manual. The default is 4.
mode : mode AC ,DC or AC + DC. The default is 'ACDC'.


Raises
------
OverflowError
    if len(variables)>34.

Returns
-------
None.

    """
    def __init__(self,HOST,PORT = 23,timeout = 2,variables = [], pattern = 4,mode='ACDC',I_range=10,V_range=600,CF=3):

        self.location = HOST
        self.port = PORT
        self.timeout = timeout 
        self.connect_to_instrument()
        self.identification()
        if len(variables)>0 : 
            pattern = 0
            if len(variables)>= 34 : 
                raise OverflowError('Pas plus de 34 variables')
            self.change_variables(variables)
        self.pattern = pattern
        if pattern!=0:
            self.change_pattern(pattern)
        self.set_mode(mode)
        self.set_range(I_range,V_range,CF)
    def __str__(self):
        return "{}".format(self.name)
    def __repr__(self):
        return "{},{},{}".format(self.name, self.location, self.port)
    def __del__(self):
        try :
            self.socket.getpeername()
            self.close_connection()
        except OSError :
            self.socket.close()
            pass
    def add_variable(self,variable):
        """
add a Variable or list of Variable to the list of varaible (max : 34), don't use self.variables.append(variable)

Parameters
----------
variable : *Variable* or *list of Variable*
    variables to add.

Raises
------
OverflowError
    if len(variable)>34.

Returns
-------
None.

        """
        self.pattern = 0
        if len(self.variables)>= 34 : 
            raise OverflowError('Pas plus de 34 variables')
        if type(variable)==list :
            for var in variable:
                if type(var)!=Variable : 
                    self.variables.append(Variable(var)) 
                else : 
                    self.variables.append(var) 
            if len(self.variables)>= 34 : 
                raise OverflowError('Pas plus de 34 variables')
            self.set_variable()
        elif type(variable)!=Variable : 
            self.variables.append(Variable(variable)) 
            if len(self.variables)>= 34 : 
                raise OverflowError('Pas plus de 34 variables')
            self.set_a_variable(self.variables[-1], len(self.variables))
        else : 
            self.variables.append(variable)
            if len(self.variables)>= 34 : 
                raise OverflowError('Pas plus de 34 variables')
            self.set_a_variable(self.variables[-1], len(self.variables))
        return
    def change_variables(self,variables):
        """
Reset variables then add variables

Parameters
----------
variables : *Variable* or *list of Variable*
    new variables.

Returns
-------
None.

        """
        self.variables = []
        self.add_variable(variables)
        return
    def connect_to_instrument(self):
        """
Establishes the connection with a GPM (via the socket library) and verifies that it is accessible

Returns
-------
None.

        """
        self.socket = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
        self.socket.settimeout(self.timeout)
        try :
            self.socket.connect((self.location, self.port))
        except : 
            print('impossible d\'ouvrir la liaison avec {}::{}'.format(self.location, self.port))
            self.socket.close()
            raise
        return
    def close_connection(self):
        """
close the connection and remove the remote control on the GPM

Returns
-------
None.

        """
        message = ':COMM:REM 0\r\n'
        self.socket.send(message.encode('ASCII'))
        self.socket.close()
        return
    def identification(self):
        """
fetch the basics data about the GPM used

Returns
-------
None.

        """
        data = self.send_query('*IDN?\r\n')
        self.name = data[0:-2].decode("utf-8")
        return
    def send_query(self,message,buffer_size=9):
        """
Send a query, see user manual to know which command are query or set

Parameters
----------
message :*str*
     message to send to the GPM with the ending \\r\\n.
buffer_size : *int*, optional
    the size of reception buffer is 2**(buffer_size). The default is 9.
            
Returns
-------
data : *str*
    GPM's answer.

        """
        # print('query  '+message)
        # self.connect_to_instrument()
        self.socket.send(message.encode('ASCII'))
        try :     
            data = self.socket.recv(2**(buffer_size))
        except :
            print('{}::{} doesn\'t answer'.format(self.location, self.port))
            self.close_connection()
            raise
        # self.close_connection()
        return data
    def send_set(self,message):
        """
Send a set, see user manual to know which command are query or set \n

Parameters
----------
message :*str*
    message to send to the GPM with the ending \\r\\n.

Returns
-------
None.

        """
        # self.connect_to_instrument()
        # print('set  '+message)
        self.socket.send(message.encode('ASCII'))
        # self.close_connection()
    def set_a_variable(self,variable,number):
        """
send set to change 1 Variable of VALUE? command. 

Parameters
----------
variable : *Variable*
    New variable type.
number : *int*
    the position of the item in VALUE? command.

Returns
-------
None.

        """
        self.send_set(':NUM:NORM:ITEM{} {}\r\n'.format(number, variable.function))
        self.send_set(':NUM:NORM:NUMB {}\r\n'.format(len(self.variables)))
        return
    def set_variable(self):
        """
DO NOT USE, send set to change VariableS of VALUE? command.

Returns
-------
None.

        """
        size = len(self.variables)
        self.send_set(':NUM:NORM:NUMB {}\r\n'.format(size))
        for number in range(1,size+1) :
             self.send_set(':NUM:NORM:ITEM{} {}\r\n'.format(number, self.variables[number-1].function))
        return
    def variables_pattern(self):
        """
DO NOT USE, associate variables with the current PRESET.

Returns
-------
None.

        """
        self.variables = [Variable('U'),Variable('I'),Variable('P')]
        if self.pattern>=2 :
            self.variables += [Variable('S'),Variable('Q'),Variable('LAMB'),Variable('PHI'),Variable('FU'),Variable('FI')]
        if self.pattern>=3 :
            self.variables += [Variable('UPPeak'),Variable('UMPeak'),Variable('IPPeak'),Variable('IMPeak'),Variable('PPPeak'),Variable('PMPeak')]
        if self.pattern>=4 :
            self.variables[13] = Variable('TIME')
            self.variables[14] = Variable('WH')
            self.variables += [Variable('WHP'),Variable('WHM'),Variable('AH'),Variable('AHP'),Variable('AHM'),Variable('PPPeak'),Variable('PMPeak'),Variable('CFU'),Variable('CFI'),Variable('UTHD'),Variable('ITHD'),Variable('URANge'),Variable('IRANge')]
        return
    def change_pattern(self,new_patt):
        """
change the preset and make the change in the GPM

Parameters
----------
new_patt : *int*  1 to 4
    preset varaibles see page 94 and 95 of user manual.
Raises
------
TypeError
    if new_patt is not in [1,4]

Returns
-------
None.

        """
        if (new_patt>=1) and (new_patt<=4) :
            self.pattern = new_patt
            self.variables_pattern()
            self.send_set(':NUM:NORM:PRES {}\r\n'.format(new_patt))
        else :
            raise TypeError('pattern doit être entre 1 et 4')
        return
    def ask_variable(self):
        """
Ask the value of the variables to the GPM

Returns
-------
data : *str*
    variables values. (unparsed)

        """
        data  = self.send_query(':NUM:NORM:VALUE?\r\n')
        return data
    def mesure_variable(self):
        """:return: *dict of float*,variables values"""
        data_pars = self.parser_variables(self.ask_variable())
        return data_pars
    def parser_variables(self,data):
        """
Convert string format to  dico of float format.
        
Parameters
----------
data : *str* ,variables values
   values in string format

Returns
-------
dict_values :  *dict of float*
    variables values
    
        """
        values = data.decode("utf-8").split(',')
        dict_values = {}
        try:
            for number in range(0,len(values)) :
                dict_values[str(self.variables[number])]=float(values[number])
        except:
            pass
        return dict_values
    def clear_buffer(self):
        """
clear the reception buffer

Returns
-------
data : *str* or None
data fetch in the buffer.

        """
        self.socket.settimeout(0.1)
        try :     
            data = self.socket.recv(2**(32))
        except :
            data = None
        self.socket.settimeout(self.timeout)
        return data
    def continous_measure(self,sample_time = 1,time=10):
        
        start=tm.time()
        while((tm.time()-start)<time):
            start_sample =tm.time()
            for instrument in self.instruments : 
                self.send_set(':NUM:NORM:VALUE?\r\n')
            while((tm.time()-start_sample)<sample_time):
                pass
        n=int(np.log(10*len(self.instruments)*time/sample_time)/np.log(2)+1)
        return
        #tout envoyer puis récupérer essayer avec deux sockets différentes
    def set_mode(self,mode='DC'):
        """
        

        Parameters
        ----------
        mode : *str* in 'DC','AC' or 'ACDC'
            change the mode of the GPM . The default is 'DC'.

        Raises
        ------
        TypeError
            mode must be 'DC' , 'AC' or 'ACDC'.

        Returns
        -------
        None.

        """
        if (mode!='DC') and  (mode!='AC') and   (mode!='ACDC') :
            raise TypeError("""mode must be 'DC' , 'AC' or 'ACDC'""")
        self.send_set(':INPUT:MODE {}\r\n'.format(mode))
        self.mode= mode
        return
    def set_range(self,I_range=10,V_range=600,CF=3):
        """
        

        Parameters
        ----------
        I_range : *int* or *float*, optional
            Current range. The default is 10.
        V_range : *int* or *float*, optional
            Voltage range. The default is 600.
        CF : *int*, optional
            Crest factor. The default is 3.

        Raises
        ------
        ValueError
            if I_range,V_range or CF have wrongs value see p105 of user manual.

        Returns
        -------
        None.

        """
        if CF==3 : 
            if not(V_range in [15, 30, 60, 150, 300, 600]):
                raise ValueError('with CF=3, V_range must be in [15, 30, 60, 150, 300, 600]')
            if not(I_range in [0.005, 0.010, 0.020, 0.050, 0.100, 0.200, 0.500,1, 2, 5, 10, 20]):
                raise ValueError('with CF=3, I_range must be in [0.005, 0.010, 0.020, 0.050, 0.100, 0.200, 0.500,1, 2, 5, 10, 20]')
            self.send_set(':INP:VOLT:RANG {}V\r\n'.format(V_range))
            if (I_range<1):
                self.send_set(':INP:CURR:RANG {}mA\r\n'.format(int(1000*I_range)))
            else :
                self.send_set(':INP:CURR:RANG {}A\r\n'.format(I_range))
        elif CF==6 : 
            if not(V_range in [7.5, 15, 30, 75, 150, 300]):
                raise ValueError('with CF=3, V_range must be in [7.5, 15, 30, 75, 150, 300]')
            if not(I_range in [0.0025, 0.005, 0.010, 0.025, 0.050, 0.100, 0.250,0.5, 1, 2.5, 5, 10]):
                raise ValueError('with CF=3, I_range must be in [0.0025, 0.005, 0.010, 0.025, 0.050, 0.100, 0.250,0.5, 1, 2.5, 5, 10]')
            self.send_set(':INP:VOLT:RANG {}V\r\n'.format(V_range))
            if (I_range<0.5):
                if I_range==0.0025:
                    self.send_set(':INP:CURR:RANG 2.5mA\r\n')
                else:
                    self.send_set(':INP:CURR:RANG {}mA\r\n'.format(int(1000*I_range)))
                
            else :
                self.send_set(':INP:CURR:RANG {}A\r\n'.format(I_range))
        else :
            raise ValueError('CF must be in [3,6]')
        return