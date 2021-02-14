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

from matplotlib.figure import Figure
######################################################################################################
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib
matplotlib.use("Qt5Agg")

class Window(QtWidgets.QMainWindow):
	def __init__(self,parent=None):
		QtWidgets.QMainWindow.__init__(self)
		QtWidgets.QApplication.setStyle(QtWidgets.QStyleFactory.create("Fusion"))

		self.title = 'Windows Cycling'
		self.initUI()

	def initUI(self):
		self.setWindowTitle(self.title)
		self.setWindowIcon(QtGui.QIcon('simple_icon.png'))
		self.resize(1280,720)
		# Define the parent widget
		self.mainWidget = QtWidgets.QWidget(self)
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
		self.Ivtaxes.autoscale(True)

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
		self.Qvtaxes.plot([0,10],[1,10])
		self.Qvtcanvas.draw()
		self.Qvtaxes.autoscale(False)
		self.Qvtaxes.plot([2,20],[1,10])
		self.Qvtcanvas.draw()

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
		self.startScienceButton.setText('Science Bitch!')
		self.stopScienceButton = QtWidgets.QPushButton(self.mainWidget)
		self.stopScienceButton.setText("Hol' Up!")

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
		self.gridLayout.addWidget(self.tabWidget, 1,2,3,1)
		self.gridLayout.addWidget(self.startScienceButton, 2,0,1,2)
		self.gridLayout.addWidget(self.stopScienceButton, 3,0,1,2)

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
		self.activeChargeLabel.setText('Q (C)')

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

		# Create Line Edits
		self.depositionTimeLineEdit = QtWidgets.QLineEdit()
		self.depositionTimeLineEdit.setText('20')
		self.depositionVoltageLineEdit = QtWidgets.QLineEdit()
		self.depositionVoltageLineEdit.setText('-0.7')
		self.depositionWaitLineEdit = QtWidgets.QLineEdit()
		self.depositionWaitLineEdit.setText('2')
		self.stripTimeLineEdit = QtWidgets.QLineEdit()
		self.stripTimeLineEdit.setText('60')
		self.stripVoltageLineEdit = QtWidgets.QLineEdit()
		self.stripVoltageLineEdit.setText('1')
		self.stripWaitLineEdit = QtWidgets.QLineEdit()
		self.stripWaitLineEdit.setText('2')
		self.cutOffDepositionILineEdit = QtWidgets.QLineEdit()
		self.cutOffDepositionILineEdit.setText('1')
		self.totalLoopsLineEdit = QtWidgets.QLineEdit()
		self.totalLoopsLineEdit.setText('10')
		self.initialWaitLineEdit = QtWidgets.QLineEdit()
		self.initialWaitLineEdit.setText('4')

		self.activeVoltageLineEdit = QtWidgets.QLineEdit()
		self.activeVoltageLineEdit.setReadOnly(True)
		self.activeCurrentLineEdit = QtWidgets.QLineEdit()
		self.activeCurrentLineEdit.setReadOnly(True)
		self.activeChargeLineEdit = QtWidgets.QLineEdit()
		self.activeChargeLineEdit.setReadOnly(True)

		# Add Validators the Line Edits
		self.intValidator = QtGui.QIntValidator()
		self.floatValidator = QtGui.QDoubleValidator()

		self.depositionTimeLineEdit.setValidator(self.floatValidator)
		self.depositionVoltageLineEdit.setValidator(self.floatValidator)
		self.depositionWaitLineEdit.setValidator(self.floatValidator)
		self.stripTimeLineEdit.setValidator(self.floatValidator)
		self.stripVoltageLineEdit.setValidator(self.floatValidator)
		self.stripWaitLineEdit.setValidator(self.floatValidator)
		self.cutOffDepositionILineEdit.setValidator(self.floatValidator)
		self.totalLoopsLineEdit.setValidator(self.intValidator)
		self.initialWaitLineEdit.setValidator(self.floatValidator)

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

		# Set Font Properties
		self.font = QtGui.QFont()
		self.font.setFamily("Arial")
		self.font.setPointSize(30)

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

		self.activeVoltageLineEdit.setFont(self.font)
		self.activeCurrentLineEdit.setFont(self.font)
		self.activeChargeLineEdit.setFont(self.font)

		self.saveLocationLineEdit.setStyleSheet("QLineEdit { background: rgb(223, 223, 223);}")
		self.activeVoltageLineEdit.setStyleSheet("QLineEdit { background: rgb(223, 223, 223);}")
		self.activeCurrentLineEdit.setStyleSheet("QLineEdit { background: rgb(223, 223, 223);}")
		self.activeChargeLineEdit.setStyleSheet("QLineEdit { background: rgb(223, 223, 223);}")

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

		# Connect Signals
		self.cdPushButton.clicked.connect(self.setSaveLocation)
		self.startScienceButton.clicked.connect(self.startScience)
		self.stopScienceButton.clicked.connect(self.stopScience)
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
		if self.saveLocationLineEdit.text() == '':
			status = self.setSaveLocation()
			if status == 'canceled':
				return


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

		if self.tabWidget.currentIndex() == 2:
			self.tabWidget.setCurrentIndex(0)
		self.startCycles()
		print ('Science Started')

	def stopScience(self):
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
		print ('IVT zoom clicked')
		self.stopIvtAutoscale()

	def startIvtAutoscale(self):
		self.Ivtaxes.autoscale(True)
		self.IvtPlay.setChecked(True)
		self.IvtStop.setChecked(False)
		print ('start ivt autoscale')

	def stopIvtAutoscale(self):
		self.Ivtaxes.autoscale(False)
		self.IvtPlay.setChecked(False)
		self.IvtStop.setChecked(True)
		print ('stop ivt autoscale')



	def QvtToolbarClicked(self, event):
		print ('QVT zoom clicked')
		self.stopQvtAutoscale()

	def startQvtAutoscale(self):
		self.Qvtaxes.autoscale(True)
		self.QvtPlay.setChecked(True)
		self.QvtStop.setChecked(False)
		print ('start qvt autoscale')

	def stopQvtAutoscale(self):
		self.Qvtaxes.autoscale(False)
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
			# Convert Strings to Floats
			initialWait = float(self.initialWaitLineEdit.text())
			depositionTime = float(self.depositionTimeLineEdit.text())
			depositionWait = float(self.depositionWaitLineEdit.text())
			stripTime = float(self.stripTimeLineEdit.text())
			stripWait = float(self.stripWaitLineEdit.text())
			depositionVoltage = float(self.depositionVoltageLineEdit.text())
			stripVoltage = float(self.stripVoltageLineEdit.text())

			x0 = -initialWait
			x1 = depositionTime
			x2 = x1 + depositionWait
			x3 = x2 + stripTime
			x4 = x3 + stripWait

			y0 = depositionVoltage
			y1 = stripVoltage

			self.cycleProfileaxes.clear()
			self.cycleProfileaxes.set_title('Cycle Profile')
			self.cycleProfileaxes.set_xlabel('Time (seconds)')
			self.cycleProfileaxes.set_ylabel('Voltage (V)')
			self.cycleProfileaxes.axhline(0, c='k')
			self.cycleProfileaxes.axvline(0, c='k')
			self.cycleProfileaxes.plot([x0, 0, 0, x1, x1, x2, x2, x3, x3, x4],[0, 0, y0, y0, 0, 0 ,y1, y1, 0, 0], c='r', linewidth = 4)
			self.cycleProfileaxes.relim()
			self.cycleProfileaxes.autoscale()
			self.cycleProfileaxes.set_ylim(-1.5,1.5)
			self.cycleProfilecanvas.draw()
		except Exception as e: print(e)


	def closeEvent(self,event):
		app.exit()


if __name__ == '__main__':
	app = QtWidgets.QApplication(sys.argv)
	app.aboutToQuit.connect(app.deleteLater)
	window = Window()
	sys.exit(app.exec_())