import pyvisa
import sys
import numpy as np
from PyQt5 import QtTest

#####TO-DO#####
'''
- find out if you can use wait_for_srq or wai*
- determine Digital Output configuration required to open and close the shutter. The functions currently work, but the output configuration is a guess.
- consider changing TRIG:COUN for repeated measurements instead of repeating the command


'''
###############
def connectToKeithley(keithleyAddress='GPIB0::22::INSTR'):
	'''
	This creates a Keithley object with which to interact with.
	Attempt to connect to a Keithley, then send an ID query to confirm connection. If this fails, send an error message to the terminal and terminate the program.
	'''
	try:
		global rm
		rm = pyvisa.ResourceManager()
		# print(rm.list_resources())
		print ('Attempting to connect to keithley.')
		keithleyObject = rm.open_resource(keithleyAddress)
		print (keithleyObject.query('*IDN?'))
		# keithleyObject.timeout = 100000
		keithleyObject.write('*RST')
		keithleyObject.write('SENS:FUNC:CONC OFF')
		keithleyObject.write('SYST:RSEN ON')
		keithleyObject.write('ROUT:TERM REAR')
		# keithleyObject.write('ROUT:TERM FRON')
		print ('Setup Done')
	except:
		print ('Could not establish connection with Keithley.')
		print ('Check connection with Keithley')
		sys.exit()
	return keithleyObject

def shutdownKeithley(keithleyObject):
	keithleyObject.write('OUTP OFF')
	rm.close()

def setFrontTerminal(keithleyObject):
	keithleyObject.write('ROUT:TERM FRON')

def setRearTerminal(keithleyObject):
	keithleyObject.write('ROUT:TERM REAR')

def prepareVoltage(keithleyObject, NPLC=1, voltlimit = 10):
	'''
	Prepares the Keithley to measure voltage.
	NPLC Range [0.01,10]
	'''
	# keithleyObject.write('*RST')
	keithleyObject.write('SOUR:FUNC CURR')
	keithleyObject.write('SOUR:CURR:MODE FIXED')
	keithleyObject.write('SOUR:CURR:RANG:AUTO ON')
	keithleyObject.write('SENS:FUNC "VOLT"')
	keithleyObject.write('SENS:VOLT:PROT {:.12f}'.format(voltlimit))
	keithleyObject.write('SENS:VOLT:RANG:AUTO ON')
	keithleyObject.write('SENS:VOLT:NPLC {:.12f}'.format(NPLC))
	keithleyObject.write('TRIG:COUN 1')
	keithleyObject.write('OUTP ON')

def setCurrent(keithleyObject, current=0):
	'''
	Set the current to be applied.
	'''
	keithleyObject.write('SOUR:CURR:LEV {:.12f}'.format(current))

def measureVoltage(keithleyObject):
	'''
	Measures voltage.
	'''
	rawData = keithleyObject.query_ascii_values('READ?')
	rawDataArray = np.array(rawData)
	return rawDataArray

def prepareCurrent(keithleyObject, NPLC=1, currentlimit=1):
	'''
	Prepares the Keithley to measure current.
	NPLC Range [0.01,10]
	'''
	# keithleyObject.write('*RST')
	keithleyObject.write('SOUR:FUNC VOLT')
	keithleyObject.write('SOUR:VOLT:MODE FIXED')
	keithleyObject.write('SOUR:VOLT:RANG:AUTO ON')
	keithleyObject.write('SENS:FUNC "CURR"')
	keithleyObject.write('SENS:CURR:PROT {:.12f}'.format(currentlimit))
	keithleyObject.write('SENS:CURR:RANG:AUTO ON')
	keithleyObject.write('SENS:CURR:NPLC {:.12f}'.format(NPLC))
	keithleyObject.write('TRIG:COUN 1')
	keithleyObject.write('OUTP ON')

def setVoltage(keithleyObject, voltage=0):
	'''
	Set the voltage to be applied.
	'''
	keithleyObject.write('SOUR:VOLT:LEV {:.12f}'.format(voltage))

def measureCurrent(keithleyObject):
	'''
	Measures current.
	'''
	rawData = keithleyObject.query_ascii_values('READ?')
	rawDataArray = np.array(rawData)
	return rawDataArray

if __name__ == "__main__":
	# rm = pyvisa.ResourceManager()
	# print(rm.list_resources())

	keithley = connectToKeithley('GPIB0::22::INSTR')

	prepareCurrent(keithley, NPLC = 0.01, polarity=polarity)
	dataCurrent = measureCurrent(keithley,voltage=0.00001,n=10, polarity=polarity)
	print (dataCurrent[0,:])

	prepareVoltage(keithley, NPLC = 0.01, polarity=polarity)
	dataVoltage = measureVoltage(keithley, current=0.0000000001, n=10, polarity=polarity)
	print (dataVoltage[0,:])

	prepareCurrent(keithley, NPLC = 0.01, polarity=polarity)
	dataCurrent = measureCurrent(keithley,voltage=0.2,n=10, polarity=polarity)
	print (dataCurrent[0,:])

	prepareVoltage(keithley, NPLC = 0.01, polarity=polarity)
	dataVoltage = measureVoltage(keithley, current=0.01, n=10, polarity=polarity)
	print (dataVoltage[0,:])

	shutdownKeithley(keithley)