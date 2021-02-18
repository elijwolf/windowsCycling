import pyvisa
import sys
import numpy as np

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
	if keithleyAddress != 'test':
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
	else:
		keithleyObject = 'test'
	return keithleyObject

def shutdownKeithley(keithleyObject):
	if keithleyObject != 'test':
		keithleyObject.write('OUTP OFF')
		rm.close()
	print ('Keithley Disconnected')

def setOutput(keithleyObject, myBool):
	if myBool:
		if keithleyObject != 'test':
			keithleyObject.write('OUTP ON')
		print ('Keithley output enabled.')
	else:
		if keithleyObject != 'test':
			keithleyObject.write('OUTP OFF')
		print ('Keithley output disabled.')

def setFrontTerminal(keithleyObject):
	if keithleyObject != 'test':
		keithleyObject.write('ROUT:TERM FRON')
	print ('Keithley set to front terminal')

def setRearTerminal(keithleyObject):
	if keithleyObject != 'test':
		keithleyObject.write('ROUT:TERM REAR')
	print ('Keithley set to rear terminal.')

def prepareVoltage(keithleyObject, NPLC=1, voltlimit = 10):
	'''
	Prepares the Keithley to measure voltage.
	NPLC Range [0.01,10]
	'''
	# keithleyObject.write('*RST')
	if keithleyObject != 'test':
		keithleyObject.write('SOUR:FUNC CURR')
		keithleyObject.write('SOUR:CURR:MODE FIXED')
		keithleyObject.write('SOUR:CURR:RANG:AUTO ON')
		keithleyObject.write('SENS:FUNC "VOLT"')
		keithleyObject.write('SENS:VOLT:PROT {:.12f}'.format(voltlimit))
		keithleyObject.write('SENS:VOLT:RANG:AUTO ON')
		keithleyObject.write('SENS:VOLT:NPLC {:.12f}'.format(NPLC))
		keithleyObject.write('TRIG:COUN 1')
	print ('Keithley prepared for voltage measurment.')

def setCurrent(keithleyObject, current=0):
	'''
	Set the current to be applied.
	'''
	if keithleyObject != 'test':
		keithleyObject.write('SOUR:CURR:LEV {:.12f}'.format(current))
	print (f'Keithley current set to {current:f} A.')

def measureVoltage(keithleyObject):
	'''
	Measures voltage.
	'''
	if keithleyObject != 'test':
		rawData = keithleyObject.query_ascii_values('READ?')
		rawDataArray = np.array(rawData)
		return rawDataArray
	print ('Keithley voltage measured.')

def prepareCurrent(keithleyObject, NPLC=1, currentlimit=1):
	'''
	Prepares the Keithley to measure current.
	NPLC Range [0.01,10]
	'''
	# keithleyObject.write('*RST')
	if keithleyObject != 'test':
		keithleyObject.write('SOUR:FUNC VOLT')
		keithleyObject.write('SOUR:VOLT:MODE FIXED')
		keithleyObject.write('SOUR:VOLT:RANG:AUTO ON')
		keithleyObject.write('SENS:FUNC "CURR"')
		keithleyObject.write('SENS:CURR:PROT {:.12f}'.format(currentlimit))
		keithleyObject.write('SENS:CURR:RANG:AUTO ON')
		keithleyObject.write('SENS:CURR:NPLC {:.12f}'.format(NPLC))
		keithleyObject.write('TRIG:COUN 1')
	print ('Keithley prepared for current measurment.')

def setVoltage(keithleyObject, voltage=0):
	'''
	Set the voltage to be applied.
	'''
	if keithleyObject != 'test':
		keithleyObject.write('SOUR:VOLT:LEV {:.12f}'.format(voltage))
	print (f'Keithley voltage set to {voltage:f} V.')

def measureCurrent(keithleyObject):
	'''
	Measures current.
	'''
	if keithleyObject != 'test':
		rawData = keithleyObject.query_ascii_values('READ?')
		rawDataArray = np.array(rawData)
		return rawDataArray
	print ('Keithley current measured.')

if __name__ == "__main__":
	# rm = pyvisa.ResourceManager()
	# print(rm.list_resources())

	keithley = connectToKeithley('GPIB0::22::INSTR')

	prepareCurrent(keithley, NPLC = 0.01)
	setVoltage(keithley, voltage = 0.00001)
	setOutput(keithley, True)
	dataCurrent = measureCurrent(keithley)
	print (dataCurrent[0,:])

	prepareVoltage(keithley, NPLC = 0.01)
	setCurrent(keithley, current=0.0000000001)
	setOutput(keithley, True)
	dataVoltage = measureVoltage(keithley)
	print (dataVoltage[0,:])

	prepareCurrent(keithley, NPLC = 0.01)
	setVoltage(keithley, voltage = 0.2)
	setOutput(keithley, True)
	dataCurrent = measureCurrent(keithley)
	print (dataCurrent[0,:])

	prepareVoltage(keithley, NPLC = 0.01)
	setCurrent(keithley, current = 0.01)
	setOutput(keithley, True)
	dataVoltage = measureVoltage(keithley)
	print (dataVoltage[0,:])

	shutdownKeithley(keithley)