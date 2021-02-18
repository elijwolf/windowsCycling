import datetime
# from PyQt5.QtCore import QThread, pyqtSignal

print ('importing sys...')
import sys
print ('importing os...')
import os
print ('importing numpy...')
import numpy as np
######################################################################################################
print ('importing PyQt5...')
from PyQt5 import QtCore, QtWidgets, QtGui
print ('importing Matplotlib...')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from matplotlib.backend_bases import Event
from matplotlib.figure import Figure
######################################################################################################
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib
matplotlib.use("Qt5Agg")
######################################################################################################
print ('Importing myKeithleyFunctions')
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),'Keithley Code'))
import myKeithleyFunctions as mkf
######################################################################################################

pan = NavigationToolbar.pan
def new_pan (self, *args, **kwargs):
	s = 'pan_event'
	event = Event(s, self)
	self.canvas.callbacks.process(s, event)
	pan(self, *args, **kwargs)
NavigationToolbar.pan = new_pan

zoom = NavigationToolbar.zoom
def new_zoom (self, *args, **kwargs):
	s = 'zoom_event'
	event = Event(s, self)
	self.canvas.callbacks.process(s, event)
	zoom(self, *args, **kwargs)
NavigationToolbar.zoom = new_zoom

configureSubplots = NavigationToolbar.configure_subplots
def new_config (self, *args, **kwargs):
	s = 'config_event'
	event = Event(s, self)
	self.canvas.callbacks.process(s, event)
	config(self, *args, **kwargs)
NavigationToolbar.config = new_config
# save = NavigationToolbar.save_figure

class myProgressBar(QtWidgets.QProgressBar):
	def text(self):
		self.totalSteps = self.maximum() - self.minimum()
		if self.totalSteps <= 0:
			self.progress = 0
		else:
			self.progress = 100*(self.value()-self.minimum())/(self.maximum() - self.minimum())
			self.progress = np.floor(100*self.progress)/100
		self.progressString = f'{self.progress:.2f}'
		self.progressBarString = self.format().replace('%p', str(self.value())).replace('%m',str(self.totalSteps)).replace('%v',self.progressString)
		return self.progressBarString

class Worker(QtCore.QObject):
	def __init__(self, parent=None, totalLoops=1):
		super(Worker, self).__init__(parent)

	finished = QtCore.pyqtSignal()
	progress = QtCore.pyqtSignal(int,object)

	def run(self):
		# self.times = []
		# self.referenceTime = datetime.datetime.now()

		#C Convert Strings to Ints
		self.initialWait = int(window.initialWaitLineEdit.text())
		self.totalLoops = int(window.totalLoopsLineEdit.text())
		self.depositionTime = int(window.depositionTimeLineEdit.text())
		self.depositionWait = int(window.depositionWaitLineEdit.text())
		self.stripTime = int(window.stripTimeLineEdit.text())
		self.stripWait = int(window.stripWaitLineEdit.text())

		# Convert Strings to Floats
		self.depositionVoltage = float(window.depositionVoltageLineEdit.text())
		self.stripVoltage = float(window.stripVoltageLineEdit.text())

		self.loopTime = self.depositionTime + self.depositionWait + self.stripTime + self.stripWait
		self.totalTime = self.initialWait + self.totalLoops*self.loopTime

		self.timeInterval = window.timeInterval
		self.totalIterations = 1000*self.totalTime//self.timeInterval
		self.currentIteration = 0

		self.timer = QtCore.QTimer(self)
		self.timer.setInterval(self.timeInterval)
		self.timer.setTimerType(QtCore.Qt.PreciseTimer)
		self.timer.timeout.connect(self.doScience)
		self.timer.start()

	def doScience(self):
		# self.deltaTime = datetime.datetime.now()-self.referenceTime
		# self.times.append(self.deltaTime.total_seconds())
		# if len(self.times) >=2:
		# 	self.timeDiffs = 1000*np.diff(self.times)
		# 	self.timeErrors = self.timeDiffs-self.timeInterval
		# 	self.timeS = self.timeErrors**2
		# 	self.timeMS = np.mean(self.timeS)
		# 	self.timeRMS = np.sqrt(self.timeMS)
		# 	self.maxError = np.max(np.abs(self.timeDiffs-self.timeInterval))

		# 	print (f'{self.timeRMS:.2f}\t{self.maxError:.2f}')

		# Trigger Keithley Events
		if self.currentIteration - 1000*self.initialWait//self.timeInterval < 0:
			if self.currentIteration == 0:
				print ('Status: Initial Wait')
				self.setVolt = 0
				self.simCurrent = 0
		else:
			self.elapsedCycleIterations = (max(0,self.currentIteration - 1000*self.initialWait//self.timeInterval))%(self.loopTime*1000//self.timeInterval)
			if self.elapsedCycleIterations == 0 and self.currentIteration != self.totalIterations:
				print ('Start cycle')

			if self.depositionTime != 0 and self.elapsedCycleIterations == 0 and self.currentIteration != self.totalIterations:
				print ('Start Deposition')
				self.setVolt = self.depositionVoltage
				self.simCurrent = self.setVolt * 2

			elif self.depositionWait != 0 and self.elapsedCycleIterations == self.depositionTime*1000//self.timeInterval:
				print ('Dposition Wait')
				self.setVolt = 0
				self.simCurrent = 0

			elif self.stripTime != 0 and self.elapsedCycleIterations == (self.depositionTime + self.depositionWait)*1000//self.timeInterval:
				print ('Start Stripping')
				self.setVolt = self.stripVoltage
				self.simCurrent = self.setVolt *2

			elif self.stripWait != 0 and self.elapsedCycleIterations == (self.depositionTime + self.depositionWait + self.stripTime)*1000//self.timeInterval:
				print ('Strip Wait')
				self.setVolt = 0
				self.simCurrent = 0

			elif self.currentIteration == self.totalIterations:
				print ('Cycling Finished')
				self.setVolt = 0
				self.simCurrent = 0

		# Measure from the Keithley
		if self.currentIteration == 0:
			self.start = datetime.datetime.now()
			self.timeStamp = 0
		else:
			self.timeStamp = (datetime.datetime.now()-self.start).total_seconds()
		self.rawData = np.array([self.setVolt,self.simCurrent,9.91e+37, self.timeStamp, 0b00000000])

		self.progress.emit(self.currentIteration,self.rawData)
		self.currentIteration += 1
		if self.currentIteration > self.totalIterations:
			self.timer.stop()
			self.finished.emit()
		if window.stopScienceFlag == True:
			self.timer.stop()
			print ('Abort detected!')
			self.finished.emit()

class Window(QtWidgets.QMainWindow):
	def __init__(self,parent=None):
		QtWidgets.QMainWindow.__init__(self)
		QtWidgets.QApplication.setStyle(QtWidgets.QStyleFactory.create("Fusion"))

		self.title = 'Windows Cycling'
		self.timeInterval = 250
		self.initUI()

	def initUI(self):
		self.setWindowTitle(self.title)
		self.setWindowIcon(QtGui.QIcon('simple_icon.png'))
		self.resize(1280,720)
		# Define the parent widget
		self.mainWidget = QtWidgets.QWidget()
		# Define a layout for the parent widget
		self.gridLayout = QtWidgets.QGridLayout(self.mainWidget)



		# Create widgets to hold the form layouts and to be placed in the grid
		self.inputFormWidget = QtWidgets.QWidget(self)
		self.inputFormLayout = QtWidgets.QFormLayout(self.inputFormWidget)



		# Create Matplotlib Canvas for I vs t
		self.IvtWidget = QtWidgets.QWidget(self)
		self.IvtGridLayout = QtWidgets.QGridLayout(self.IvtWidget)	
		self.Ivtcanvas = FigureCanvas(Figure(figsize=(5, 3)))
		self.Ivtcanvas.mpl_connect('pan_event', self.IvtToolbarClicked)
		self.Ivtcanvas.mpl_connect('zoom_event', self.IvtToolbarClicked)
		self.Ivtcanvas.mpl_connect('config_event', self.IvtToolbarClicked)
		
		self.Ivttoolbar = NavigationToolbar(self.Ivtcanvas, self)
		self.Ivttoolbar.setMinimumWidth(500)

		self.Ivtaxes = self.Ivtcanvas.figure.subplots()
		self.Ivtaxes.axhline(0,c='k')
		self.Ivtaxes.axvline(0,c='k')

		self.IvtPlay = QtWidgets.QPushButton(self.mainWidget)
		self.IvtPlay.setIcon(QtGui.QIcon(os.path.join('assets','play.png')))
		self.IvtPlay.setCheckable(True)
		self.IvtPlay.setChecked(True)
		self.IvtStop = QtWidgets.QPushButton(self.mainWidget)
		self.IvtStop.setIcon(QtGui.QIcon(os.path.join('assets','stop.png')))
		self.IvtStop.setCheckable(True)
		self.IvtStop.setChecked(False)

		self.IvtGridLayout.addWidget(self.Ivttoolbar, 0,0,1,1)
		self.IvtGridLayout.addWidget(self.IvtPlay, 0,1,1,1)
		self.IvtGridLayout.addWidget(self.IvtStop, 0,2,1,1)
		self.IvtGridLayout.addWidget(self.Ivtcanvas, 1,0,1,3)



		# Create Matplotlib Canvas for Q vs t
		self.QvtWidget = QtWidgets.QWidget(self)
		self.QvtGridLayout = QtWidgets.QGridLayout(self.QvtWidget)
		self.Qvtcanvas = FigureCanvas(Figure(figsize=(5, 3)))
		self.Qvtcanvas.mpl_connect('pan_event', self.QvtToolbarClicked)
		self.Qvtcanvas.mpl_connect('zoom_event', self.QvtToolbarClicked)
		self.Qvtcanvas.mpl_connect('config_event', self.QvtToolbarClicked)
		
		self.Qvttoolbar = NavigationToolbar(self.Qvtcanvas, self)
		self.Qvttoolbar.setMinimumWidth(500)

		self.Qvtaxes = self.Qvtcanvas.figure.subplots()
		self.Qvtaxes.axhline(0,c='k')
		self.Qvtaxes.axvline(0,c='k')

		self.QvtPlay = QtWidgets.QPushButton(self.mainWidget)
		self.QvtPlay.setIcon(QtGui.QIcon(os.path.join('assets','play.png')))
		self.QvtPlay.setCheckable(True)
		self.QvtPlay.setChecked(True)

		self.QvtStop = QtWidgets.QPushButton(self.mainWidget)
		self.QvtStop.setIcon(QtGui.QIcon(os.path.join('assets','stop.png')))
		self.QvtStop.setCheckable(True)
		self.QvtStop.setChecked(False)

		self.QvtGridLayout.addWidget(self.Qvttoolbar, 0,0,1,1)
		self.QvtGridLayout.addWidget(self.QvtPlay, 0,1,1,1)
		self.QvtGridLayout.addWidget(self.QvtStop, 0,2,1,1)
		self.QvtGridLayout.addWidget(self.Qvtcanvas, 1,0,1,3)



		self.cycleProfilecanvas = FigureCanvas(Figure(figsize=(5,3)))
		self.cycleProfileaxes = self.cycleProfilecanvas.figure.subplots()
		self.cycleProfileaxes.axhline(0, c='k')
		self.cycleProfileaxes.axvline(0, c='k')



		# Create Tab Widget to hold multiple plots
		self.tabWidget = QtWidgets.QTabWidget(self)
		self.tabWidget.addTab(self.IvtWidget,'I v t')
		self.tabWidget.addTab(self.QvtWidget, 'Q v t')
		self.tabWidget.addTab(self.cycleProfilecanvas, 'Cycle Profile')



		# Create Buttons
		self.cdPushButton = QtWidgets.QPushButton(self.mainWidget)
		self.cdPushButton.setIcon(QtGui.QIcon(os.path.join('assets','folder.png')))
		self.cdPushButton.setToolTip('Go to a specific directory.')
		self.saveLocationLineEdit = QtWidgets.QLineEdit()
		self.saveLocationLineEdit.setReadOnly(True)
		self.startScienceButton = QtWidgets.QPushButton(self.mainWidget)
		self.startScienceButton.setText('Start')
		self.stopScienceButton = QtWidgets.QPushButton(self.mainWidget)
		self.stopScienceButton.setText('STOP')
		self.stopScienceButton.setEnabled(False)

		self.loopProgressBar = myProgressBar(self)
		self.myLoopValue = 00.00
		self.loopProgressBar.setMaximum(100)
		self.loopProgressBar.setValue(self.myLoopValue)
		# self.loopProgressBar.setFormat("%p/%m")
		self.loopProgressBar.setFormat('%v%')

		self.totalProgressBar = myProgressBar(self)
		self.myValue = 00.00
		self.totalProgressBar.setMaximum(100)
		self.totalProgressBar.setValue(self.myValue)
		# self.totalProgressBar.setFormat("%p/%m")
		self.totalProgressBar.setFormat('%v%')


		self.buttonSizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)
		self.buttonSizePolicy.setHorizontalStretch(0)
		self.buttonSizePolicy.setVerticalStretch(0)

		self.cdPushButton.setSizePolicy(self.buttonSizePolicy)
		# self.startScienceButton.setSizePolicy(self.buttonSizePolicy)
		self.IvtPlay.setSizePolicy(self.buttonSizePolicy)
		self.IvtStop.setSizePolicy(self.buttonSizePolicy)
		self.QvtPlay.setSizePolicy(self.buttonSizePolicy)
		self.QvtStop.setSizePolicy(self.buttonSizePolicy)

		# Add Widgets to the grid
		self.gridLayout.addWidget(self.cdPushButton, 0,0,1,1)
		self.gridLayout.addWidget(self.saveLocationLineEdit, 0,1,1,2)
		self.gridLayout.addWidget(self.inputFormWidget, 1,0,1,2)
		self.gridLayout.addWidget(self.tabWidget, 1,2,5,1)
		self.gridLayout.addWidget(self.startScienceButton, 2,0,1,2)
		self.gridLayout.addWidget(self.stopScienceButton, 3,0,1,2)
		self.gridLayout.addWidget(self.loopProgressBar, 4, 0,1,2)
		self.gridLayout.addWidget(self.totalProgressBar, 5, 0, 1, 2)

		# Create Labels
		self.depositionTimeLabel = QtWidgets.QLabel(self.mainWidget)
		self.depositionTimeLabel.setText('t<sub>deposition</sub> (s)')
		self.depositionVoltageLabel = QtWidgets.QLabel(self.mainWidget)
		self.depositionVoltageLabel.setText('V<sub>deposition</sub> (V)')
		self.depositionWaitLabel = QtWidgets.QLabel(self.mainWidget)
		self.depositionWaitLabel.setText('t<sub>deposition, wait</sub> (s)')

		self.stripTimeLabel = QtWidgets.QLabel(self.mainWidget)
		self.stripTimeLabel.setText('t<sub>strip</sub> (s)')
		self.stripVoltageLabel = QtWidgets.QLabel(self.mainWidget)
		self.stripVoltageLabel.setText('V<sub>strip</sub> (V)')
		self.stripWaitLabel = QtWidgets.QLabel(self.mainWidget)
		self.stripWaitLabel.setText('t<sub>strip, wait</sub> (s)')	

		self.cutOffDepositionILabel = QtWidgets.QLabel(self.mainWidget)
		self.cutOffDepositionILabel.setText('I<sub>deposition, cutoff</sub> (mA)')

		self.totalLoopsLabel = QtWidgets.QLabel(self.mainWidget)
		self.totalLoopsLabel.setText('Loop Count')

		self.initialWaitLabel = QtWidgets.QLabel(self.mainWidget)
		self.initialWaitLabel.setText('t<sub>initial</sub> (s)')

		self.activeVoltageLabel = QtWidgets.QLabel(self.mainWidget)
		self.activeVoltageLabel.setText('V (V)')
		self.activeCurrentLabel = QtWidgets.QLabel(self.mainWidget)
		self.activeCurrentLabel.setText('I (mA)')
		self.activeChargeLabel = QtWidgets.QLabel(self.mainWidget)
		self.activeChargeLabel.setText('Q (mC)')

		self.currentLoopLabel = QtWidgets.QLabel(self.mainWidget)
		self.currentLoopLabel.setText('Current Cycle')
		
		self.elapsedCycleTimeLabel = QtWidgets.QLabel(self.mainWidget)
		self.elapsedCycleTimeLabel.setText('Elapsed Cycle Time (s)')
		self.totalCycleTimeLabel = QtWidgets.QLabel(self.mainWidget)
		self.totalCycleTimeLabel.setText('Total Cycle Time (s)')
		self.remainingCycleTimeLabel = QtWidgets.QLabel(self.mainWidget)
		self.remainingCycleTimeLabel.setText('Remaining Cycle Time (s)')
		
		self.elapsedTimeLabel = QtWidgets.QLabel(self.mainWidget)
		self.elapsedTimeLabel.setText('Elapsed Time (s)')
		self.totalTimeLabel = QtWidgets.QLabel(self.mainWidget)
		self.totalTimeLabel.setText('Total Time (s)')
		self.remainingTimeLabel = QtWidgets.QLabel(self.mainWidget)
		self.remainingTimeLabel.setText('Time Remaining (s)')

		# Add Labels to the Form
		self.inputFormLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.depositionTimeLabel)
		self.inputFormLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.depositionVoltageLabel)
		self.inputFormLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.depositionWaitLabel)
		self.inputFormLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.stripTimeLabel)
		self.inputFormLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.stripVoltageLabel)
		self.inputFormLayout.setWidget(5, QtWidgets.QFormLayout.LabelRole, self.stripWaitLabel)
		self.inputFormLayout.setWidget(6, QtWidgets.QFormLayout.LabelRole, self.cutOffDepositionILabel)
		self.inputFormLayout.setWidget(7, QtWidgets.QFormLayout.LabelRole, self.totalLoopsLabel)
		self.inputFormLayout.setWidget(8, QtWidgets.QFormLayout.LabelRole, self.initialWaitLabel)

		self.inputFormLayout.setWidget(9, QtWidgets.QFormLayout.LabelRole, self.activeVoltageLabel)
		self.inputFormLayout.setWidget(10, QtWidgets.QFormLayout.LabelRole, self.activeCurrentLabel)
		self.inputFormLayout.setWidget(11, QtWidgets.QFormLayout.LabelRole, self.activeChargeLabel)
		self.inputFormLayout.setWidget(12, QtWidgets.QFormLayout.LabelRole, self.currentLoopLabel)
		self.inputFormLayout.setWidget(13, QtWidgets.QFormLayout.LabelRole, self.elapsedCycleTimeLabel)
		self.inputFormLayout.setWidget(14, QtWidgets.QFormLayout.LabelRole, self.totalCycleTimeLabel)
		self.inputFormLayout.setWidget(15, QtWidgets.QFormLayout.LabelRole, self.remainingCycleTimeLabel)
		self.inputFormLayout.setWidget(16, QtWidgets.QFormLayout.LabelRole, self.elapsedTimeLabel)
		self.inputFormLayout.setWidget(17, QtWidgets.QFormLayout.LabelRole, self.totalTimeLabel)
		self.inputFormLayout.setWidget(18, QtWidgets.QFormLayout.LabelRole, self.remainingTimeLabel)

		# Create Line Edits
		self.fixedWidth = 110
		self.depositionTimeLineEdit = QtWidgets.QLineEdit()
		self.depositionTimeLineEdit.setText('20')
		self.depositionTimeLineEdit.setFixedWidth(self.fixedWidth)

		self.depositionVoltageLineEdit = QtWidgets.QLineEdit()
		self.depositionVoltageLineEdit.setText('-0.7')
		self.depositionVoltageLineEdit.setFixedWidth(self.fixedWidth)

		self.depositionWaitLineEdit = QtWidgets.QLineEdit()
		self.depositionWaitLineEdit.setText('2')
		self.depositionWaitLineEdit.setFixedWidth(self.fixedWidth)

		self.stripTimeLineEdit = QtWidgets.QLineEdit()
		self.stripTimeLineEdit.setText('60')
		self.stripTimeLineEdit.setFixedWidth(self.fixedWidth)

		self.stripVoltageLineEdit = QtWidgets.QLineEdit()
		self.stripVoltageLineEdit.setText('1')
		self.stripVoltageLineEdit.setFixedWidth(self.fixedWidth)

		self.stripWaitLineEdit = QtWidgets.QLineEdit()
		self.stripWaitLineEdit.setText('2')
		self.stripWaitLineEdit.setFixedWidth(self.fixedWidth)

		self.cutOffDepositionILineEdit = QtWidgets.QLineEdit()
		self.cutOffDepositionILineEdit.setText('1')
		self.cutOffDepositionILineEdit.setFixedWidth(self.fixedWidth)

		self.totalLoopsLineEdit = QtWidgets.QLineEdit()
		self.totalLoopsLineEdit.setText('10')
		self.totalLoopsLineEdit.setFixedWidth(self.fixedWidth)

		self.initialWaitLineEdit = QtWidgets.QLineEdit()
		self.initialWaitLineEdit.setText('4')
		self.initialWaitLineEdit.setFixedWidth(self.fixedWidth)

		self.activeVoltageLineEdit = QtWidgets.QLineEdit()
		self.activeVoltageLineEdit.setReadOnly(True)
		self.activeVoltageLineEdit.setText('open')
		self.activeVoltageLineEdit.setFixedWidth(self.fixedWidth)

		self.activeCurrentLineEdit = QtWidgets.QLineEdit()
		self.activeCurrentLineEdit.setReadOnly(True)
		self.activeCurrentLineEdit.setText('0')
		self.activeCurrentLineEdit.setFixedWidth(self.fixedWidth)

		self.activeChargeLineEdit = QtWidgets.QLineEdit()
		self.activeChargeLineEdit.setReadOnly(True)
		self.activeChargeLineEdit.setText('0')
		self.activeChargeLineEdit.setFixedWidth(self.fixedWidth)

		self.currentLoopLineEdit = QtWidgets.QLineEdit()
		self.currentLoopLineEdit.setReadOnly(True)
		self.currentLoopLineEdit.setText('0')
		self.currentLoopLineEdit.setFixedWidth(self.fixedWidth)

		self.elapsedCycleTimeLineEdit = QtWidgets.QLineEdit()
		self.elapsedCycleTimeLineEdit.setReadOnly(True)
		self.elapsedCycleTimeLineEdit.setText('00:00:00')
		self.elapsedCycleTimeLineEdit.setFixedWidth(self.fixedWidth)

		self.totalCycleTimeLineEdit = QtWidgets.QLineEdit()
		self.totalCycleTimeLineEdit.setReadOnly(True)
		self.totalCycleTimeLineEdit.setFixedWidth(self.fixedWidth)

		self.remainingCycleTimeLineEdit = QtWidgets.QLineEdit()
		self.remainingCycleTimeLineEdit.setReadOnly(True)
		self.remainingCycleTimeLineEdit.setFixedWidth(self.fixedWidth)

		self.elapsedTimeLineEdit = QtWidgets.QLineEdit()
		self.elapsedTimeLineEdit.setReadOnly(True)
		self.elapsedTimeLineEdit.setText('00:00:00')
		self.elapsedTimeLineEdit.setFixedWidth(self.fixedWidth)

		self.totalTimeLineEdit = QtWidgets.QLineEdit()
		self.totalTimeLineEdit.setReadOnly(True)
		self.totalTimeLineEdit.setFixedWidth(self.fixedWidth)

		self.remainingTimeLineEdit = QtWidgets.QLineEdit()
		self.remainingTimeLineEdit.setReadOnly(True)
		self.remainingTimeLineEdit.setFixedWidth(self.fixedWidth)

		# Add Validators the Line Edits
		self.intValidator = QtGui.QIntValidator()
		self.floatValidator = QtGui.QDoubleValidator()

		self.depositionTimeLineEdit.setValidator(self.intValidator)
		self.depositionVoltageLineEdit.setValidator(self.floatValidator)
		self.depositionWaitLineEdit.setValidator(self.intValidator)
		self.stripTimeLineEdit.setValidator(self.intValidator)
		self.stripVoltageLineEdit.setValidator(self.floatValidator)
		self.stripWaitLineEdit.setValidator(self.intValidator)
		self.cutOffDepositionILineEdit.setValidator(self.floatValidator)
		self.totalLoopsLineEdit.setValidator(self.intValidator)
		self.initialWaitLineEdit.setValidator(self.intValidator)

		# Add Line Edits to the Form
		self.inputFormLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.depositionTimeLineEdit)
		self.inputFormLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.depositionVoltageLineEdit)
		self.inputFormLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.depositionWaitLineEdit)
		self.inputFormLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.stripTimeLineEdit)
		self.inputFormLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.stripVoltageLineEdit)
		self.inputFormLayout.setWidget(5, QtWidgets.QFormLayout.FieldRole, self.stripWaitLineEdit)
		self.inputFormLayout.setWidget(6, QtWidgets.QFormLayout.FieldRole, self.cutOffDepositionILineEdit)
		self.inputFormLayout.setWidget(7, QtWidgets.QFormLayout.FieldRole, self.totalLoopsLineEdit)
		self.inputFormLayout.setWidget(8, QtWidgets.QFormLayout.FieldRole, self.initialWaitLineEdit)

		self.inputFormLayout.setWidget(9, QtWidgets.QFormLayout.FieldRole, self.activeVoltageLineEdit)
		self.inputFormLayout.setWidget(10, QtWidgets.QFormLayout.FieldRole, self.activeCurrentLineEdit)
		self.inputFormLayout.setWidget(11, QtWidgets.QFormLayout.FieldRole, self.activeChargeLineEdit)
		self.inputFormLayout.setWidget(12, QtWidgets.QFormLayout.FieldRole, self.currentLoopLineEdit)
		self.inputFormLayout.setWidget(13, QtWidgets.QFormLayout.FieldRole, self.elapsedCycleTimeLineEdit)
		self.inputFormLayout.setWidget(14, QtWidgets.QFormLayout.FieldRole, self.totalCycleTimeLineEdit)
		self.inputFormLayout.setWidget(15, QtWidgets.QFormLayout.FieldRole, self.remainingCycleTimeLineEdit)
		self.inputFormLayout.setWidget(16, QtWidgets.QFormLayout.FieldRole, self.elapsedTimeLineEdit)
		self.inputFormLayout.setWidget(17, QtWidgets.QFormLayout.FieldRole, self.totalTimeLineEdit)
		self.inputFormLayout.setWidget(18, QtWidgets.QFormLayout.FieldRole, self.remainingTimeLineEdit)

		# Set Font Properties
		self.font = QtGui.QFont()
		self.font.setFamily("Arial")
		self.font.setPointSize(20)

		# Apply Font to Widgets
		self.depositionTimeLabel.setFont(self.font)
		self.depositionVoltageLabel.setFont(self.font)
		self.depositionWaitLabel.setFont(self.font)
		self.stripTimeLabel.setFont(self.font)
		self.stripVoltageLabel.setFont(self.font)
		self.stripWaitLabel.setFont(self.font)
		self.cutOffDepositionILabel.setFont(self.font)
		self.totalLoopsLabel.setFont(self.font)
		self.initialWaitLabel.setFont(self.font)
		
		self.depositionTimeLineEdit.setFont(self.font)
		self.depositionVoltageLineEdit.setFont(self.font)
		self.depositionWaitLineEdit.setFont(self.font)
		self.stripTimeLineEdit.setFont(self.font)
		self.stripVoltageLineEdit.setFont(self.font)
		self.stripWaitLineEdit.setFont(self.font)
		self.cutOffDepositionILineEdit.setFont(self.font)
		self.totalLoopsLineEdit.setFont(self.font)
		self.initialWaitLineEdit.setFont(self.font)

		self.activeVoltageLabel.setFont(self.font)
		self.activeCurrentLabel.setFont(self.font)
		self.activeChargeLabel.setFont(self.font)

		self.currentLoopLabel.setFont(self.font)

		self.elapsedCycleTimeLabel.setFont(self.font)
		self.totalCycleTimeLabel.setFont(self.font)
		self.remainingCycleTimeLabel.setFont(self.font)

		self.elapsedTimeLabel.setFont(self.font)
		self.totalTimeLabel.setFont(self.font)
		self.remainingTimeLabel.setFont(self.font)

		self.activeVoltageLineEdit.setFont(self.font)
		self.activeCurrentLineEdit.setFont(self.font)
		self.activeChargeLineEdit.setFont(self.font)

		self.currentLoopLineEdit.setFont(self.font)
		
		self.elapsedCycleTimeLineEdit.setFont(self.font)
		self.totalCycleTimeLineEdit.setFont(self.font)
		self.remainingCycleTimeLineEdit.setFont(self.font)
		
		self.elapsedTimeLineEdit.setFont(self.font)
		self.totalTimeLineEdit.setFont(self.font)
		self.remainingTimeLineEdit.setFont(self.font)

		self.saveLocationLineEdit.setStyleSheet("QLineEdit { background: rgb(223, 223, 223);}")
		self.activeVoltageLineEdit.setStyleSheet("QLineEdit { background: rgb(223, 223, 223);}")
		self.activeCurrentLineEdit.setStyleSheet("QLineEdit { background: rgb(223, 223, 223);}")
		self.activeChargeLineEdit.setStyleSheet("QLineEdit { background: rgb(223, 223, 223);}")
		self.currentLoopLineEdit.setStyleSheet("QLineEdit { background: rgb(223, 223, 223);}")
		self.elapsedCycleTimeLineEdit.setStyleSheet("QLineEdit { background: rgb(223, 223, 223);}")
		self.totalCycleTimeLineEdit.setStyleSheet("QLineEdit { background: rgb(223, 223, 223);}")
		self.remainingCycleTimeLineEdit.setStyleSheet("QLineEdit { background: rgb(223, 223, 223);}")
		self.elapsedTimeLineEdit.setStyleSheet("QLineEdit { background: rgb(223, 223, 223);}")
		self.totalTimeLineEdit.setStyleSheet("QLineEdit { background: rgb(223, 223, 223);}")
		self.remainingTimeLineEdit.setStyleSheet("QLineEdit { background: rgb(223, 223, 223);}")

		# Define the size policy of the line edits
		self.sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)
		self.sizePolicy.setHorizontalStretch(0)
		self.sizePolicy.setVerticalStretch(0)

		# Define and set the size policies of the Plot
		self.plotWindowSizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Expanding)
		self.plotWindowSizePolicy.setHorizontalStretch(1)
		self.plotWindowSizePolicy.setVerticalStretch(1)
		self.Ivtcanvas.setSizePolicy(self.plotWindowSizePolicy)

		# Set the size policy
		self.depositionTimeLineEdit.setSizePolicy(self.sizePolicy)
		self.depositionVoltageLineEdit.setSizePolicy(self.sizePolicy)
		self.depositionWaitLineEdit.setSizePolicy(self.sizePolicy)
		self.stripTimeLineEdit.setSizePolicy(self.sizePolicy)
		self.stripVoltageLineEdit.setSizePolicy(self.sizePolicy)
		self.stripWaitLineEdit.setSizePolicy(self.sizePolicy)
		self.cutOffDepositionILineEdit.setSizePolicy(self.sizePolicy)
		self.totalLoopsLineEdit.setSizePolicy(self.sizePolicy)
		self.initialWaitLineEdit.setSizePolicy(self.sizePolicy)

		self.activeVoltageLineEdit.setSizePolicy(self.sizePolicy)
		self.activeCurrentLineEdit.setSizePolicy(self.sizePolicy)
		self.activeChargeLineEdit.setSizePolicy(self.sizePolicy)
		self.currentLoopLineEdit.setSizePolicy(self.sizePolicy)
		
		self.elapsedCycleTimeLineEdit.setSizePolicy(self.sizePolicy)
		self.totalCycleTimeLineEdit.setSizePolicy(self.sizePolicy)
		self.remainingCycleTimeLineEdit.setSizePolicy(self.sizePolicy)
		
		self.elapsedTimeLineEdit.setSizePolicy(self.sizePolicy)
		self.totalTimeLineEdit.setSizePolicy(self.sizePolicy)
		self.remainingTimeLineEdit.setSizePolicy(self.sizePolicy)

		# Connect Signals
		self.cdPushButton.clicked.connect(self.setSaveLocation)
		self.startScienceButton.clicked.connect(self.startScience)
		self.stopScienceButton.clicked.connect(self.stopScienceButtonFunc)
		self.myIvtAutoscale = True
		self.myQvtAutoscale = True
		self.IvtPlay.clicked.connect(self.startIvtAutoscale)
		self.IvtStop.clicked.connect(self.stopIvtAutoscale)
		self.QvtPlay.clicked.connect(self.startQvtAutoscale)
		self.QvtStop.clicked.connect(self.stopQvtAutoscale)

		self.depositionTimeLineEdit.textEdited.connect(self.parametersEdited)
		self.depositionVoltageLineEdit.textEdited.connect(self.parametersEdited)
		self.depositionWaitLineEdit.textEdited.connect(self.parametersEdited)
		self.stripTimeLineEdit.textEdited.connect(self.parametersEdited)
		self.stripVoltageLineEdit.textEdited.connect(self.parametersEdited)
		self.stripWaitLineEdit.textEdited.connect(self.parametersEdited)
		self.cutOffDepositionILineEdit.textEdited.connect(self.parametersEdited)
		self.totalLoopsLineEdit.textEdited.connect(self.parametersEdited)
		self.initialWaitLineEdit.textEdited.connect(self.parametersEdited)

		self.setCentralWidget(self.mainWidget)
		self.show()
		self.move(50,50)

		# Initialize Default Values
		self.parametersEdited()
		plt.show()

	def setSaveLocation(self):
		self.newSaveLocation = QtWidgets.QFileDialog.getExistingDirectory(None, 'Select the Folder')
		if self.newSaveLocation != '':
			print ('updating save location')
			self.saveLocationLineEdit.setText(self.newSaveLocation)
		else:
			print ('keeping old save location')
			return 'canceled'

	def startScience(self):
		self.stopScienceFlag = False
		if self.saveLocationLineEdit.text() == '':
			status = self.setSaveLocation()
			if status == 'canceled':
				self.stopScience()
				return

		self.startScienceButton.setEnabled(False)
		self.stopScienceButton.setEnabled(True)
		self.currentLoopLineEdit.setText("0")

		self.depositionTimeLineEdit.setReadOnly(True)
		self.depositionVoltageLineEdit.setReadOnly(True)
		self.depositionWaitLineEdit.setReadOnly(True)
		self.stripTimeLineEdit.setReadOnly(True)
		self.stripVoltageLineEdit.setReadOnly(True)
		self.stripWaitLineEdit.setReadOnly(True)
		self.cutOffDepositionILineEdit.setReadOnly(True)
		self.totalLoopsLineEdit.setReadOnly(True)
		self.initialWaitLineEdit.setReadOnly(True)

		self.depositionTimeLineEdit.setStyleSheet("QLineEdit { background: rgb(223, 223, 223);}")
		self.depositionVoltageLineEdit.setStyleSheet("QLineEdit { background: rgb(223, 223, 223);}")
		self.depositionWaitLineEdit.setStyleSheet("QLineEdit { background: rgb(223, 223, 223);}")
		self.stripTimeLineEdit.setStyleSheet("QLineEdit { background: rgb(223, 223, 223);}")
		self.stripVoltageLineEdit.setStyleSheet("QLineEdit { background: rgb(223, 223, 223);}")
		self.stripWaitLineEdit.setStyleSheet("QLineEdit { background: rgb(223, 223, 223);}")
		self.cutOffDepositionILineEdit.setStyleSheet("QLineEdit { background: rgb(223, 223, 223);}")
		self.totalLoopsLineEdit.setStyleSheet("QLineEdit { background: rgb(223, 223, 223);}")
		self.initialWaitLineEdit.setStyleSheet("QLineEdit { background: rgb(223, 223, 223);}")

		self.activeVoltageList = []
		self.activeCurrentList = []
		self.activeTimeList = []
		self.activeChargeList = []

		if self.tabWidget.currentIndex() == 2:
			self.tabWidget.setCurrentIndex(0)
		self.thread = QtCore.QThread()
		self.worker = Worker()
		self.worker.moveToThread(self.thread)
		self.thread.started.connect(self.worker.run)
		self.worker.finished.connect(self.thread.quit)
		self.worker.finished.connect(self.worker.deleteLater)
		self.thread.finished.connect(self.thread.deleteLater)
		self.worker.progress.connect(self.stepIteration)
		self.thread.start()

		# self.thread.finished.connect(
		# 	lambda: self.startScienceButton.setEnabled(True)
		# )
		# self.thread.finished.connect(
		# 	lambda: self.currentLoopLineEdit.setText("0")
		# )
		self.thread.finished.connect(self.stopScience)
		print ('Science Started')

	def stopScienceButtonFunc(self):
		self.stopScienceFlag = True

	def stopScience(self):
		if self.stopScienceFlag == True:
			print ('Abort detected. Thread finished.')
		self.stopScienceButton.setEnabled(False)
		self.startScienceButton.setEnabled(True)
		self.depositionTimeLineEdit.setReadOnly(False)
		self.depositionVoltageLineEdit.setReadOnly(False)
		self.depositionWaitLineEdit.setReadOnly(False)
		self.stripTimeLineEdit.setReadOnly(False)
		self.stripVoltageLineEdit.setReadOnly(False)
		self.stripWaitLineEdit.setReadOnly(False)
		self.cutOffDepositionILineEdit.setReadOnly(False)
		self.totalLoopsLineEdit.setReadOnly(False)
		self.initialWaitLineEdit.setReadOnly(False)

		self.depositionTimeLineEdit.setStyleSheet("QLineEdit { background: rgb(255, 255, 255);}")
		self.depositionVoltageLineEdit.setStyleSheet("QLineEdit { background: rgb(255, 255, 255);}")
		self.depositionWaitLineEdit.setStyleSheet("QLineEdit { background: rgb(255, 255, 255);}")
		self.stripTimeLineEdit.setStyleSheet("QLineEdit { background: rgb(255, 255, 255);}")
		self.stripVoltageLineEdit.setStyleSheet("QLineEdit { background: rgb(255, 255, 255);}")
		self.stripWaitLineEdit.setStyleSheet("QLineEdit { background: rgb(255, 255, 255);}")
		self.cutOffDepositionILineEdit.setStyleSheet("QLineEdit { background: rgb(255, 255, 255);}")
		self.totalLoopsLineEdit.setStyleSheet("QLineEdit { background: rgb(255, 255, 255);}")
		self.initialWaitLineEdit.setStyleSheet("QLineEdit { background: rgb(255, 255, 255);}")

	def IvtToolbarClicked(self, event):
		print ('IVT toolbar clicked')
		self.stopIvtAutoscale()

	def startIvtAutoscale(self):
		self.myIvtAutoscale = True
		self.IvtPlay.setChecked(True)
		self.IvtStop.setChecked(False)
		print ('start ivt autoscale')

	def stopIvtAutoscale(self):
		self.myIvtAutoscale = False
		self.IvtPlay.setChecked(False)
		self.IvtStop.setChecked(True)
		print ('stop ivt autoscale')



	def QvtToolbarClicked(self, event):
		print ('QVT toolbar clicked')
		self.stopQvtAutoscale()

	def startQvtAutoscale(self):
		self.myQvtAutoscale = True
		self.QvtPlay.setChecked(True)
		self.QvtStop.setChecked(False)
		print ('start qvt autoscale')

	def stopQvtAutoscale(self):
		self.myQvtAutoscale = False
		self.QvtPlay.setChecked(False)
		self.QvtStop.setChecked(True)
		print ('stop qvt autoscale')

	def parametersEdited(self):
		if self.tabWidget.currentIndex() != 2:
			self.tabWidget.setCurrentIndex(2)
		
		initialWait = 0
		depositionTime = 0
		depositionWait = 0
		depositionVoltage = 0

		stripTime = 0
		stripWait = 0
		stripVoltage = 0

		try:
			self.initialWait = int(self.initialWaitLineEdit.text())
			self.totalLoops = int(self.totalLoopsLineEdit.text())
			self.depositionTime = int(self.depositionTimeLineEdit.text())
			self.depositionWait = int(self.depositionWaitLineEdit.text())
			self.stripTime = int(self.stripTimeLineEdit.text())
			self.stripWait = int(self.stripWaitLineEdit.text())

			self.loopTime = self.depositionTime + self.depositionWait + self.stripTime + self.stripWait
			self.totalTime = self.initialWait + self.totalLoops*self.loopTime

			self.totalIterations = 1000*self.totalTime//self.timeInterval
			# Convert Strings to Floats
			self.depositionVoltage = float(self.depositionVoltageLineEdit.text())
			self.stripVoltage = float(self.stripVoltageLineEdit.text())

			self.x0 = -self.initialWait
			self.x1 = self.depositionTime
			self.x2 = self.x1 + self.depositionWait
			self.x3 = self.x2 + self.stripTime
			self.x4 = self.x3 + self.stripWait

			self.y0 = self.depositionVoltage
			self.y1 = self.stripVoltage

			self.cycleProfileaxes.clear()
			self.cycleProfileaxes.set_title('Cycle Profile')
			self.cycleProfileaxes.set_xlabel('Time (seconds)')
			self.cycleProfileaxes.set_ylabel('Voltage (V)')
			self.cycleProfileaxes.axhline(0, c='k')
			self.cycleProfileaxes.axvline(0, c='k')
			self.cycleProfileaxes.plot([self.x0, 0, 0, self.x1, self.x1, self.x2, self.x2, self.x3, self.x3, self.x4],[0, 0, self.y0, self.y0, 0, 0 ,self.y1, self.y1, 0, 0], c='r', linewidth = 4)
			self.cycleProfileaxes.relim()
			# self.cycleProfileaxes.autoscale()
			self.cycleProfileaxes.set_ylim(-1.5,1.5)
			self.cycleProfilecanvas.draw()

			# Update ETA
			self.loopHours = self.loopTime//3600
			self.loopMinutes = (self.loopTime - 3600*self.loopHours)//60
			self.loopSeconds = self.loopTime - 3600*self.loopHours - 60*self.loopMinutes
			self.elapsedCycleTimeLineEdit.setText('00:00:00')
			self.totalCycleTimeLineEdit.setText(f'{self.loopHours:02}:{self.loopMinutes:02}:{self.loopSeconds:02}')
			self.remainingCycleTimeLineEdit.setText(f'{self.loopHours:02}:{self.loopMinutes:02}:{self.loopSeconds:02}')
			self.loopProgressBar.setMaximum(1000*self.loopTime//self.timeInterval)
			self.loopProgressBar.setValue(0)

			self.totalHours = self.totalTime//3600
			self.totalMinutes = (self.totalTime - 3600*self.totalHours)//60
			self.totalSeconds = self.totalTime - 3600*self.totalHours - 60*self.totalMinutes
			self.elapsedTimeLineEdit.setText('00:00:00')
			self.totalTimeLineEdit.setText(f'{self.totalHours:02}:{self.totalMinutes:02}:{self.totalSeconds:02}')
			self.remainingTimeLineEdit.setText(f'{self.totalHours:02}:{self.totalMinutes:02}:{self.totalSeconds:02}')
			self.totalProgressBar.setMaximum(self.totalIterations)
			self.totalProgressBar.setValue(0)
		except Exception as e: print(e)

	def stepIteration(self, n, rawData):
		self.activeVoltage = rawData[0]
		self.activeVoltageList.append(self.activeVoltage)
		self.activeVoltageLineEdit.setText(f'{self.activeVoltage:.3f}')

		self.activeCurrent = rawData[1]
		self.activeCurrentList.append(self.activeCurrent)
		self.activeCurrentLineEdit.setText(f'{self.activeCurrent:.3f}')

		self.activeTime = rawData[3] - self.initialWait
		self.activeTimeList.append(self.activeTime)

		if n == 0:
			self.changeCharge = 0
			self.cumulativeCharge = 0
		else:
			self.changeCharge = (self.activeCurrentList[-2] + self.activeCurrentList[-1])*(self.activeTimeList[-1] - self.activeTimeList[-2])/2
			self.cumulativeCharge = self.activeChargeList[-1] + self.changeCharge
		self.activeChargeLineEdit.setText(f'{self.cumulativeCharge:.3f}')
		self.activeChargeList.append(self.cumulativeCharge)

		self.elapsedCycleIterations = (max(0,n - 1000*self.initialWait//self.timeInterval))%(self.loopTime*1000//self.timeInterval)
		if n!= self.totalIterations:
			self.elapsedCycleTime = (self.elapsedCycleIterations*self.timeInterval//1000)
		else:
			self.elapsedCycleTime = self.loopTime
		self.elapsedCycleHours = self.elapsedCycleTime//3600
		self.elapsedCycleMinutes = (self.elapsedCycleTime - self.elapsedCycleHours*3600)//60
		self.elapsedCycleSeconds = self.elapsedCycleTime - self.elapsedCycleHours*3600 - self.elapsedCycleMinutes*60
		self.elapsedCycleTimeLineEdit.setText(f'{self.elapsedCycleHours:02}:{self.elapsedCycleMinutes:02}:{self.elapsedCycleSeconds:02}')
		
		self.remainingCycleTime = self.loopTime - self.elapsedCycleTime
		self.remainingCycleHours = self.remainingCycleTime//3600
		self.remainingCycleMinutes = (self.remainingCycleTime - self.remainingCycleHours*3600)//60
		self.remainingCycleSeconds = self.remainingCycleTime - self.remainingCycleHours*3600 - self.remainingCycleMinutes*60
		self.remainingCycleTimeLineEdit.setText(f'{self.remainingCycleHours:02}:{self.remainingCycleMinutes:02}:{self.remainingCycleSeconds:02}')

		self.elapsedTime = n*self.timeInterval//1000
		self.elapsedHours = self.elapsedTime//3600
		self.elapsedMinutes = (self.elapsedTime - self.elapsedHours*3600)//60
		self.elapsedSeconds = self.elapsedTime - self.elapsedHours*3600 - self.elapsedMinutes*60
		self.elapsedTimeLineEdit.setText(f'{self.elapsedHours:02}:{self.elapsedMinutes:02}:{self.elapsedSeconds:02}')
		
		self.remainingTime = self.totalTime - self.elapsedTime
		self.remainingHours = self.remainingTime//3600
		self.remainingMinutes = (self.remainingTime - self.remainingHours*3600)//60
		self.remainingSeconds = self.remainingTime - self.remainingHours*3600 - self.remainingMinutes*60
		self.remainingTimeLineEdit.setText(f'{self.remainingHours:02}:{self.remainingMinutes:02}:{self.remainingSeconds:02}')

		if self.loopTime == 0:
			self.currentLoop = 0
		else:
			self.currentLoop = min(self.totalLoops,max(0,1 + (n - 1000*self.initialWait//self.timeInterval)//(1000*self.loopTime//self.timeInterval)))
		self.currentLoopLineEdit.setText(str(self.currentLoop))
		self.loopProgressBar.setValue(self.elapsedCycleIterations)
		self.totalProgressBar.setValue(n)

		if n%(1000//self.timeInterval) == 0:
			if not self.myIvtAutoscale:
				self.Ivtaxis = self.Ivtaxes.axis()
			self.Ivtaxes.clear()
			self.Ivtaxes.set_title('I v t')
			self.Ivtaxes.set_xlabel('Time (seconds)')
			self.Ivtaxes.set_ylabel('Current (mA)')
			self.Ivtaxes.axhline(0,c='k')
			self.Ivtaxes.axvline(0,c='k')
			self.Ivtaxes.plot(self.activeTimeList, self.activeCurrentList)
			if not self.myIvtAutoscale:
				self.Ivtaxes.axis(self.Ivtaxis)
			self.Ivtcanvas.draw()

			if not self.myQvtAutoscale:
				self.Qvtaxis = self.Qvtaxes.axis()
			self.Qvtaxes.clear()
			self.Qvtaxes.set_title('Q v t')
			self.Qvtaxes.set_xlabel('Time (seconds)')
			self.Qvtaxes.set_ylabel('Charge (mC)')
			self.Qvtaxes.axhline(0,c='k')
			self.Qvtaxes.axvline(0,c='k')
			self.Qvtaxes.plot(self.activeTimeList, self.activeChargeList)
			if not self.myQvtAutoscale:
				self.Qvtaxes.axis(self.Qvtaxis)
			self.Qvtcanvas.draw()

		self.cycleProfileaxes.clear()
		self.cycleProfileaxes.set_title('Cycle Profile')
		self.cycleProfileaxes.set_xlabel('Time (seconds)')
		self.cycleProfileaxes.set_ylabel('Voltage (V)')
		self.cycleProfileaxes.axhline(0, c='k')
		self.cycleProfileaxes.axvline(0, c='k')
		self.cycleProfileaxes.plot([self.x0, 0, 0, self.x1, self.x1, self.x2, self.x2, self.x3, self.x3, self.x4],[0, 0, self.y0, self.y0, 0, 0 ,self.y1, self.y1, 0, 0], c='r', linewidth = 4)
		self.cycleProfileaxes.axvline(self.elapsedCycleIterations*self.timeInterval/1000, c='g')
		self.cycleProfileaxes.relim()
		# self.cycleProfileaxes.autoscale()
		self.cycleProfileaxes.set_ylim(-1.5,1.5)
		self.cycleProfilecanvas.draw()

	def closeEvent(self,event):
		app.exit()


if __name__ == '__main__':
	app = QtWidgets.QApplication(sys.argv)
	app.aboutToQuit.connect(app.deleteLater)
	window = Window()
	sys.exit(app.exec_())