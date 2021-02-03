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
	if keithleyAddress=='Test':
		print ('Keithley Code running in Test Mode. All of the following data is generated not measured.')
		from scipy.interpolate import interp1d as interp
		global datetime
		import datetime
		global time
		import time
		global sleepTime
		sleepTime = 0.001
		global start
		start = datetime.datetime.now()
		global k
# 		k = 8.617e-5
		k = 1.38e-23        
		global T0
		T0 = 273.15
		global Iph
		Iph = 0
		global q
		q = 1.602e-19

		def testIV(V,Iph,I0=1e-13,T=25,VF=1.1,VR=1,V0=0.56):
# 			I = -Iph + I0*(np.exp((V-VF+V0)/(k*(T+T0)))-1) + 0.01*np.random.uniform(-1,1)
			I = -Iph + I0*(np.exp(q*(V-VF+V0)/(k*(T+T0)))-1) + np.random.uniform(-.0001,.0001)
			return I

		def testIVinv(I,Iph,I0=1e-13,T=25,VF=1.1,VR=1,V0=0.56):
			V = k*(T+T0)*np.log(1+((I+Iph)/I0))/q + np.random.uniform(-.001,.001)
			return V

		global getI
		getI = testIV

		global getV
		getV = testIVinv

		return keithleyAddress

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
	if keithleyObject == 'Test':
		return
	keithleyObject.write('OUTP OFF')
	rm.close()

def openShutter(keithleyObject):
	'''
	Opens the Solar Sim shutter to allow light through and illuminate a device.
	'''
	if keithleyObject == 'Test':
		global Iph
		activeArea = 0.06 #cm^2
		simulatedJsc = 20 #mA/cm^2
		photoCurrent = simulatedJsc*activeArea/1000 + np.random.uniform(-.010,.01)
		Iph = photoCurrent #Units are Amps
		return
	keithleyObject.write('SOUR2:TTL {:d}'.format(0b0000))
	print('shutter open')

def closeShutter(keithleyObject):
	'''
	Closes the Solar Sim shutter to block light and prevent illumination of a device.
	'''
	if keithleyObject == 'Test':
		global Iph
		Iph = 0
		return
	keithleyObject.write('SOUR2:TTL {:d}'.format(0b1111))
	print('shutter closed')

def setFrontTerminal(keithleyObject):
	if keithleyObject != 'Test':
		keithleyObject.write('ROUT:TERM FRON')

def setRearTerminal(keithleyObject):
	if keithleyObject != 'Test':
		keithleyObject.write('ROUT:TERM REAR')

def prepareVoltage(keithleyObject, NPLC=1, voltlimit = 10, polarity='pin'):
	'''
	Prepares the Keithley to measure voltage.
	NPLC Range [0.01,10]
	'''
# 	print (polarity)
	if polarity == 'pin':
		voltlimit *= -1
	if keithleyObject == 'Test':
		return
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

def measureVoltage(keithleyObject, current=0, n=1, polarity='pin'):
	'''
	Sets the current and measures voltage n times.
	'''
# 	print (polarity)
	if polarity == 'pin':
		current *= -1

	if keithleyObject == 'Test':
		time.sleep(sleepTime)
		timeStamp = (datetime.datetime.now()-start).total_seconds()
		simVolt = getV(current,Iph)
		rawData = np.array([simVolt,current,9.91e+37, timeStamp, 0b00000000])
		rawDataArray = np.array(rawData)
		for i in range(n-1):
			time.sleep(sleepTime)
			timeStamp = (datetime.datetime.now()-start).total_seconds()
			simVolt = getV(current,Iph)
			rawData = np.array([simVolt,current,9.91e+37, timeStamp, 0b00000000])
			rawDataArray = np.vstack((rawDataArray,rawData))
		data = rawDataArray
		if polarity == 'pin':
			data[:,0:2] *= -1
		return data
	keithleyObject.write('SOUR:CURR:LEV {:.12f}'.format(current))
	rawData = keithleyObject.query_ascii_values('READ?')
	rawDataArray = np.array(rawData)
	for i in range(n-1):
		rawData = keithleyObject.query_ascii_values('READ?')
		rawDataArray = np.vstack((rawDataArray,rawData))
	data = rawDataArray
	if polarity == 'pin':
		data[:,0:2] *= -1
	return data

def prepareCurrent(keithleyObject, NPLC=1, currentlimit=1e-2, polarity='pin'):
	'''
	Prepares the Keithley to measure current.
	NPLC Range [0.01,10]
	'''
# 	print("fromkeithley prep")
# 	print(polarity)
	if polarity == 'pin':
		currentlimit *= -1

	if keithleyObject == 'Test':
		return
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

def measureCurrent(keithleyObject, voltage=0, n=1, polarity='pin'):
	'''
	Sets the voltage and measures current n times.
	'''
# 	print("fromkeithley meas")
# 	print (polarity)
	if polarity == 'pin':
		voltage *= -1

	if keithleyObject == 'Test':
		time.sleep(sleepTime)
		timeStamp = (datetime.datetime.now()-start).total_seconds()
		simCurrent = getI(voltage,Iph)
		rawData = np.array([voltage,simCurrent,9.91e+37, timeStamp, 0b00000000])
		rawDataArray = np.array(rawData)
		for i in range(n-1):
			time.sleep(sleepTime)
			timeStamp = (datetime.datetime.now()-start).total_seconds()
			simCurrent = getI(voltage,Iph)
			rawData = np.array([voltage,simCurrent,9.91e+37, timeStamp, 0b00000000])
			rawDataArray = np.vstack((rawDataArray,rawData))
		data = rawDataArray
		if polarity == 'pin':
			data[:,0:2] *= -1
		return data
	keithleyObject.write('SOUR:VOLT:LEV {:.12f}'.format(voltage))
	rawData = keithleyObject.query_ascii_values('READ?')
	rawDataArray = np.array(rawData)
	for i in range(n-1):
		rawData = keithleyObject.query_ascii_values('READ?')
		rawDataArray = np.vstack((rawDataArray,rawData))
	data = rawDataArray
	if polarity == 'pin':
		data[:,0:2] *= -1
	return data

def takeIV(keithleyObject, minV=-0.2, maxV=1.2, stepV=0.1, delay=10, forw=1, polarity='pin', NPLC = 1, Ilimit=100E-3):
	'''
	This takes an IV sweep. startV must be less than stopV.
	Returns an (n,5) numpy array.
	Columns are...
	[Voltage,Current,Resistance,Time,Status]
	Resistance is noramlly disabled and will result in all values in the third column be equal to 9.91e+37.
	See Keithley manual for the explanatoin of the value of status.
	NPLC Range [0.01,10]
	'''
	delay = delay/1000 # convert delay from ms to seconds
# 	print("fromkeithley meas: ",polarity)
	if polarity =='pin':
		minV, maxV = -maxV, -minV
		forw = not forw

	if forw:
		startV, stopV = minV, maxV
	else:
		startV, stopV = maxV, minV
		stepV *= -1

	if keithleyObject == 'Test':
		volts = np.arange(startV, stopV+stepV, stepV)
		global start
		start = datetime.datetime.now()
		timeStamp = (datetime.datetime.now()-start).total_seconds()
		simCurrent = getI(volts[0],Iph)
		rawData = np.array([volts[0],simCurrent,9.91e+37, timeStamp, 0b00000000])
		rawDataArray = np.array(rawData)
		for volt in volts[1:]:
# 			time.sleep(sleepTime)
			QtTest.QTest.qWait(sleepTime)#qWait is better than sleep because it does not freeze the gui during waiting time
			timeStamp = (datetime.datetime.now()-start).total_seconds()
			simCurrent = getI(volt,Iph)
			rawData = np.array([volt,simCurrent,9.91e+37, timeStamp, 0b00000000])
			rawDataArray = np.vstack((rawDataArray,rawData))
		data = rawDataArray
		if polarity == 'pin':
			data[:,0:2] *= -1
		return data

	n = round(1 + (stopV - startV) /stepV)
	keithleyObject.timeout = 100000
	# keithleyObject.write('*RST')
	keithleyObject.write('SOUR:FUNC VOLT')

	keithleyObject.write('SOUR:VOLT:STAR {:.12f}'.format(startV))
	keithleyObject.write('SOUR:VOLT:STOP {:.12f}'.format(stopV))
	keithleyObject.write('SOUR:VOLT:STEP {:.12f}'.format(stepV))
	keithleyObject.write('SOUR:VOLT:MODE SWE')
	keithleyObject.write('SOUR:SWE:RANG AUTO')
	keithleyObject.write('SOUR:SWE:SPAC LIN')
	keithleyObject.write('SOUR:SWE:POIN {:d}'.format(n))
	keithleyObject.write('SOUR:DEL {:.12f}'.format(delay))
	keithleyObject.write('SENS:FUNC "CURR"')
	keithleyObject.write('SENS:CURR:PROT {:.12f}'.format(Ilimit))
	keithleyObject.write('SENS:CURR:NPLC {:.12f}'.format(NPLC))
	keithleyObject.write('TRIG:COUN {:d}'.format(n))
	keithleyObject.write('SYST:TIME:RES')
	keithleyObject.write('OUTP ON')
	rawData = keithleyObject.query_ascii_values('READ?')
	keithleyObject.write('OUTP OFF')
	data = np.reshape(rawData, (-1,5))
	if polarity == 'pin':
		data[:,0:2] *= -1
	return data

if __name__ == "__main__":

	import matplotlib.pyplot as plt

	# rm = pyvisa.ResourceManager()
	# print(rm.list_resources())

	keithley = connectToKeithley('GPIB0::22::INSTR')
	# keithley = connectToKeithley('Test')
	polarity = 'nip'
	forw = 0
	# keithley = connectToKeithley('Test')
	
	# rawDataDark = takeIV(keithley, stepV = 0.01, forw=forw, polarity=polarity)

	# openShutter(keithley)
# 	closeShutter(keithley)

	prepareCurrent(keithley, NPLC = 0.01, polarity=polarity)
	dataCurrent = measureCurrent(keithley,voltage=0.00001,n=10, polarity=polarity)
	print (dataCurrent[0,:])

	prepareVoltage(keithley, NPLC = 0.01, polarity=polarity)
	dataVoltage = measureVoltage(keithley, current=0.0000000001, n=10, polarity=polarity)
	print (dataVoltage[0,:])




	rawDataLight = takeIV(keithley, stepV = 0.01, forw=forw, polarity=polarity)

	# closeShutter(keithley)




	# prepareCurrent(keithley, NPLC = 0.01, polarity=polarity)
	# dataCurrent = measureCurrent(keithley,voltage=0.2,n=10, polarity=polarity)
	# print (dataCurrent[0,:])

	# prepareVoltage(keithley, NPLC = 0.01, polarity=polarity)
	# dataVoltage = measureVoltage(keithley, current=0.01, n=10, polarity=polarity)
	# print (dataVoltage[0,:])

	shutdownKeithley(keithley)
	plt.axhline(color = 'k')
	plt.axvline(color = 'k')
	plt.plot(rawDataLight[:,0],rawDataLight[:,1], color = 'r')
	plt.scatter(rawDataLight[0,0],rawDataLight[0,1], label = 'start', color = 'y')
	plt.scatter(rawDataLight[-1,0],rawDataLight[-1,1], label = 'end', color = 'g')
	# plt.plot(rawDataDark[:,0],rawDataDark[:,1], color = 'b')
	# plt.scatter(rawDataDark[0,0],rawDataDark[0,1], label = 'start', color = 'cyan')
	# plt.scatter(rawDataDark[-1,0],rawDataDark[-1,1], label = 'end', color = 'purple')
	plt.legend()

	plt.show()