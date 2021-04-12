import logging
from PySide2 import QtWidgets, QtCore
from shiboken2 import wrapInstance
import maya.OpenMayaUI as omui
import maya.cmds as cmds
import random
from PySide2.QtWidgets import QBoxLayout
from pymel.core.system import Path

log = logging.getLogger(__name__)


def maya_main_window():
    """
    Utility method to get the main maya parent window
    """
    main_window = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window), QtWidgets.QWidget)


class ScatterToolUI(QtWidgets.QDialog):

    scatter_layout: QBoxLayout

    def __init__(self, parent=maya_main_window()):
        super(ScatterToolUI, self).__init__(parent)

        self.setWindowTitle("Slab Scatter Tool")
        self.setMinimumWidth(600)
        self.setMaximumHeight(300)
        self.setWindowFlags(self.windowFlags() ^
                            QtCore.Qt.WindowContextHelpButtonHint)
        self.create_ui()
        self.create_connections()

    def create_ui(self):
        self.title_lbl = QtWidgets.QLabel("Scatter Base")
        self.title_lbl.setStyleSheet("font: bold 30px")
        self.scatter_layout = self._scatter_layout()
        self.vertex_layout = self._vert_plc_ui()
        self.ctrl_b_layout = self.create_cnl_btn_ui()
        self.m_layout = QtWidgets.QVBoxLayout
        self.m_layout.addLayout(self.scatter_layout)
        self.m_layout.addStretch()
        self.ui.load_surface_btn.clicked.connect(self.load_surface)
        self.ui.load_object_btn.clicked.connect(self.load_object)
        self.ui.do_scatter_btn.clicked.connect(self.do_scatter)
        self.m_layout.addLayout(self.vertex_layout)
        self.m_layout.addLayout(self.ctrl_b_layout)
        self.setLayout(self.m_layout)

        self.surface = None
        self.object = None

    def create_cnl_btn_ui(self):
        self.cancel_btn = QtWidgets.QPushButton("Cancel?")
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.cancel_btn)
        return layout

    def scatter_main(self):
        self.scatter_scl_lbel = QtWidgets.QLabel("Scaling Factor")
        self.scatter_scl_lbel.setStyleSheet("font: bold")
        layout = QtWidgets.QGridLayout()
        layout.addWidget(self.scatter_scl_lbel, 0, 0)
        return layout

    def _scatter_layout(self):
        layout = self.scatter_main()
        self.scatter_dbox_min = QtWidgets.QDoubleSpinBox()
        self.scatter_dbox_min.setMaximumWidth(200)
        self.scatter_dbox_min.setMinimum(1)
        self.scatter_dbox_max = QtWidgets.QDoubleSpinBox()
        self.scatter_dbox_max.setMaximumWidth(100)
        self.scatter_dbox_max.setMinimum(1)
        self.scatter_btn = QtWidgets.QPushButton("Scatter")
        layout.addWidget(self.scatter_dbox_min, 1, 0)
        layout.addWidget(self.scatter_dbox_max, 1, 1)
        layout.addWidget(self.scatter_btn, 2, 2)
        return layout

    def _vert_plc_header(self):
        self.scatter_scl_lbel = QtWidgets.QLabel("Scaling Factor")
        self.scatter_scl_lbel.setStyleSheet("font: bold")
        layout = QtWidgets.QGridLayout()
        layout.addWidget(self.scatter_scl_lbel, 0, 0)
        return layout

    def _vert_plc_ui(self):
        layout = self._vert_plc_header()
        self.scatter_vert_hdr_lbel = QtWidgets.QLabel("Vertex Placement")
        self.scatter_vert_hdr_lbel.setStyleSheet("font: bold")
        self.vert_scl_le_min = QtWidgets.QLineEdit("Min")
        self.vert_scl_le_min.setMinimumWidth(200)
        self.vert_scl_le_max = QtWidgets.QLineEdit("Max")
        self.vert_scl_le_max.setMinimumWidth(100)
        self.vertex_btn = QtWidgets.QPushButton("Vert Placement")
        layout.addWidget(self.vert_scl_le_min, 1, 0)
        layout.addWidget(self.vert_scl_le_max, 1, 1)
        layout.addWidget(self.vertex_btn, 1, 3)
        return layout

    def create_connections(self):
        "for tool signals"
        self.cancel_btn.clicked.connect(self.cancel)
        self.scatter_btn.clicked.connect(self._do_scatter)
        self.vertex_btn.clicked.connect(self._vertex_plc)
        self.scatter_dbox_min.valueChanged.connect(self.
                                                   set_dsbx_value_min)
        self.scatter_dbox_max.valueChanged.connect(self.
                                                   set_dsbx_value_max)

    def set_dsbx_value_min(self):
        _min = self.scatter_dbox_min.value()

        return _min

    def set_dsbx_value_max(self):
        _max = self.scatter_dbox_min.value()

        return _max

    @QtCore.Slot()
    def _vertex_plc(self):
        """save/incrementing the scene"""
        self.vert_placement = CreateVertObjects()

    @QtCore.Slot()
    def _do_scatter(self):
        self.scatter_now = Explode()

    @QtCore.Slot()
    def cancel(self):
        self.close()


class CreateVertObjects:
    def __init__(self):
        self.Vertex_Inst()

    def Vertex_Inst(self):
        random.seed(1998)
        result = cmds.ls(orderedSelection=True)
        vertex_name = cmds.filterExpand(expand=True, selectionMask=25)
        inst_obj = result[0]
        instance_group_name = cmds.group(empty=True,
                                         name=inst_obj +
                                          '_instance_grp#')
        cmds.xform(instance_group_name, centerPivots=True)
        if cmds.objectType(inst_obj) == 'transform':
            for vertex in vertex_name:
                instance_result = cmds.instance(inst_obj,
                                                name=inst_obj +
                                                    '_instance#')

                cmds.parent(instance_result, instance_group_name)
                self.rnd_rotation(instance_result)
                self.rnd_scaling(instance_result)
                x_ver, y_ver, z_ver = cmds.pointPosition(vertex)
                cmds.move(x_ver, y_ver, z_ver)

        else: print("Oops")

        cmds.hide(inst_obj)

    def random_rotation(self, instance_result):
        x_rot = random.uniform(0.360)
        y_rot = random.uniform(0,300)
        z_rot = random.uniform(0, 360)
        cmds.rotate(x_rot, y_rot, instance_result)

    def rnd_scaling(self, instance_result):
        min_value = ScatterToolUI().set_dsbx_value_min()
        max_value = ScatterToolUI().set_dsbx_value_max()
        print(max_value)
        scaling_factor = random.uniform(min_value, max_value)
        cmds.scale(scaling_factor, scaling_factor,
                    scaling_factor, instance_result)

class Explode:
    def __init__(self):
        self.scatter_shot()


    def scatter_shot(self):
        random.seed(1998)
        result = cmds.ls(orderedSelection=True)

        inst_obj = result[0]
        instance_group_name = cmds.group(empty=True,
                                         name=inst_obj + '_instance_grp')

        cmds.parent(instance_result, instance_group_name)



class SceneFile(object):

    def __init__(self):
        self.filename = None

    def _init_from_path(self, path):
        path = Path(path)
        self.folder_path = Path("C:\\test\\")
        self.filename = "my_maya_scene.ma"
        self.basename = Path("my_maya_scene.ma").stripext()

    def get_path(self):
        return self.folder_path / self.filename

    @property
    def path(self):
        return self.folder_path / self.filename


scene = SceneFile()
