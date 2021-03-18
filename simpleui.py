import maya.OpenMayaUI as omui
from PySide2 import QtWidgets
from shiboken2 import wrapInstance


def maya_main_window():
    """return the maya main window widget"""
    main_window = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window), QtWidgets.QWidget)


class SimpleUI(QtWidgets.QDialog):
    """Simple UI Class"""

    def __init__(self):
        """Constructor"""
        # passing SimpleUI as an argument to super()
        # makes the line python 2 and 1 compatible
        super(SimpleUI, self).__init__(parent=maya_main_window())
        self.setWindowTitle("A simple UI")
