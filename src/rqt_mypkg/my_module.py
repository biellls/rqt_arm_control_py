import os
import rospy
import sys
from std_msgs.msg import String

from qt_gui.plugin import Plugin
from python_qt_binding import loadUi
from python_qt_binding.QtGui import QWidget
from PyQt4.QtGui import QFileDialog, QMessageBox


class MyPlugin(Plugin):
    def __init__(self, context):
        super(MyPlugin, self).__init__(context)
        # Give QObjects reasonable names
        self.setObjectName('MyPlugin')

        # Process standalone plugin command-line arguments
        from argparse import ArgumentParser
        parser = ArgumentParser()
        # Add argument(s) to the parser.
        parser.add_argument("-q", "--quiet", action="store_true",
                      dest="quiet",
                      help="Put plugin in silent mode")
        args, unknowns = parser.parse_known_args(context.argv())
        if not args.quiet:
            print 'arguments: ', args
            print 'unknowns: ', unknowns

        # Create QWidget
        self._widget = QWidget()
        # Get path to UI file which is a sibling of this file
        # in this example the .ui and .py file are in the same folder
        ui_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'MyPlugin.ui')
        # Extend the widget with all attributes and children from UI file
        loadUi(ui_file, self._widget)
        # Give QObjects reasonable names
        self._widget.setObjectName('MyPluginUi')
        # Show _widget.windowTitle on left-top of each plugin (when 
        # it's set in _widget). This is useful when you open multiple 
        # plugins at once. Also if you open multiple instances of your 
        # plugin at once, these lines add number to make it easy to 
        # tell from pane to pane.
        if context.serial_number() > 1:
            self._widget.setWindowTitle(self._widget.windowTitle() + (' (%d)' % context.serial_number()))
        # Add widget to the user interface
        context.add_widget(self._widget)
        
        # UI interaction
        self._widget.loadProgramButton.clicked.connect(self._loadProgram)
        self._widget.loadPointsButton.clicked.connect(self._loadPoints)
        self._widget.sendButton.clicked.connect(self._sendInstruction)
        self._widget.chooseProgramButton.clicked.connect(self._chooseProgram)
        self._widget.choosePointsButton.clicked.connect(self._choosePoints)
        self._widget.runButton.clicked.connect(self._runProgram)
        self.pub = rospy.Publisher('execute_instruction', String, queue_size=10)
        

    def publish_file(self, fname):
        try:
            with open(fname) as f:
                for line in f:
                    self.pub.publish(line.strip('\n'))
        except IOError:
            QMessageBox.warning(self._widget, "Error opening file", "Error opening file: %s"%fname)
            sys.stderr.write("Error opening file: %s \n"%fname)
        

    def _loadProgram(self):
        fname = self._widget.programPathTextEdit.toPlainText()
        if fname == "":
            sys.stderr.write("No file specified\n")
            QMessageBox.warning(self._widget, "Error loading program", "Please specify a file")
            return
            
        if not fname.endswith(".MB4"):
            sys.stderr.write("Please choose .MB4 file\n")
            QMessageBox.warning(self._widget, "Error loading program", "Wrong extension: Please choose .mb4 file")
            return

        self.pub.publish('---LOAD PROGRAM BEGIN---')
        self.publish_file(fname)
        self.pub.publish('---LOAD PROGRAM END---')


    def _loadPoints(self):
        fname = self._widget.pointsPathTextEdit.toPlainText()
        if fname == "":
            sys.stderr.write("No file specified\n")
            QMessageBox.warning(self._widget, "Error loading points", "Please specify a file")
            return
            
        if not fname.endswith(".POS"):
            sys.stderr.write("Please choose .POS file\n")
            QMessageBox.warning(self._widget, "Error loading points", "Wrong extension: Please choose .pos file")
            return

        self.pub.publish('---LOAD POINTS BEGIN---')
        self.publish_file(fname)
        self.pub.publish('---LOAD POINTS END---')
        
        
    def _runProgram(self):
        self.pub.publish('---RUN PROGRAM---')

    def _sendInstruction(self):
        self.pub.publish('---SINGLE INSTRUCTION---')
        self.pub.publish(self._widget.textEdit.toPlainText())
        

    def _chooseProgram(self):
        fname=QFileDialog.getOpenFileName()
        self._widget.programPathTextEdit.setText(fname[0])


    def _choosePoints(self):
        fname=QFileDialog.getOpenFileName()
        self._widget.pointsPathTextEdit.setText(fname[0])


    def shutdown_plugin(self):
        # TODO unregister all publishers here
        pass


    def save_settings(self, plugin_settings, instance_settings):
        # TODO save intrinsic configuration, usually using:
        # instance_settings.set_value(k, v)
        pass


    def restore_settings(self, plugin_settings, instance_settings):
        # TODO restore intrinsic configuration, usually using:
        # v = instance_settings.value(k)
        pass


    #def trigger_configuration(self):
        # Comment in to signal that the plugin has a way to configure
        # This will enable a setting button (gear icon) in each dock widget title bar
        # Usually used to open a modal configuration dialog
