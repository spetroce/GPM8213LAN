# -*- coding: utf-8 -*-
"""
`GPM8213LAN.variable` implements the following classes:
    
:Variable: variable which GPM-8213 can measure

"""
def variable_available():
    """
    

    Returns
    -------
    *list of str*
        all variable of GPM-8213.

    """
    return ['U', 'I', 'P', 'S', 'Q', 'LAMB', 'PHI', 'FU', 'FI', 'UPPeak', 'UMPeak', 'IPPeak', 'IMPeak', 'TIME', 'WH', 'WHP', 'WHM', 'AH', 'AHP', 'AHM', 'PPPeak', 'PMPeak', 'CFU', 'CFI', 'UTHD', 'ITHD', 'URANge', 'IRANge']

class Variable():
    """
Function to display, to find the list go to page 76 and 77 in user manual
see `variable_available` to see variable of GPM-821

Parameters
----------
function : *str* 
    find the list in variable_available().

Raises
------
TypeError
    if the parameter function is not in variable_available().

Returns
-------
None.

        """
    def __init__(self,function):
        self.variable_available =['U', 'I', 'P', 'S', 'Q', 'LAMB', 'PHI', 'FU', 'FI', 'UPPeak', 'UMPeak', 'IPPeak', 'IMPeak', 'TIME', 'WH', 'WHP', 'WHM', 'AH', 'AHP', 'AHM', 'PPPeak', 'PMPeak', 'CFU', 'CFI', 'UTHD', 'ITHD', 'URANge', 'IRANge']
        if type(function)!=str:
            raise TypeError('must be a string (str)')
        if not(function in self.variable_available):
            raise TypeError('{function} not available')
        self.function = function
    def __str__(self):
        return '{}'.format(self.function)
    def __repr__(self):
        return self.function
    
    

