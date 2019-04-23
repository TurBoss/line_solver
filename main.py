#!/usr/bin/env python
# -*- coding: utf-8 -*
import os
import cffi

from qtpy.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QFileDialog, QTextEdit
import numpy as np
from pygcode import Line, GCodeLinearMove, GCodeRapidMove, Word


ffi = cffi.FFI()
ffi.cdef("void cffi_check_point(double *p1, double *p2, double *p3);")
C = ffi.dlopen("./liblinesolver.so")


class GCodePoint:
    def __init__(self, point, gcode_line):
        self._point = point  # list
        self._gcode_line = gcode_line  # string

    @property
    def point(self):
        return self._point

    @point.setter
    def point(self, point):
        self._point = point

    @property
    def gcode_line(self):
        return self._gcode_line

    @gcode_line.setter
    def gcode_line(self, gcode_line):
        self._gcode_line = gcode_line


class LineSolverApp:

    def __init__(self):

        self.file_name = None

        self.result_vector = list()
        self.app = QApplication([])

        self.window = QWidget()

        self.window.setWindowTitle('Gcode simplification tool')
        self.window.setFixedWidth(400)
        self.window.setFixedHeight(320)

        self.open_dialog = QFileDialog()

        self.layout = QVBoxLayout()

        self.load_button = QPushButton('Open')

        self.work_button = QPushButton('Work')
        self.work_button.setEnabled(False)

        self.log_display = QTextEdit()
        self.log_display.setPlainText("TurBo Line Equation Solver 3000")
        self.log_display.setReadOnly(True)

        self.layout.addWidget(self.load_button)
        self.layout.addWidget(self.work_button)
        self.layout.addWidget(self.log_display)

        self.load_button.clicked.connect(self.on_load_clicked)
        self.work_button.clicked.connect(self.on_work_clicked)

        self.window.setLayout(self.layout)

    def exec(self):
        self.window.show()
        self.app.exec_()

    def on_load_clicked(self):
        options = QFileDialog.Options() | QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getOpenFileName(self.open_dialog,
                                                   "QFileDialog.getOpenFileName()",
                                                   "",
                                                   "All Files (*)",
                                                   options=options)
        if file_name:
            self.file_name = file_name
            self.work_button.setEnabled(True)
            self.log_display.append("file loaded.")

    def save_point(self, point):
        self.result_vector.append(point)

    def log_gcode_point_vector(self, vector):
        for point in vector:
            point_to_save = point.point
            if point_to_save:
                string_to_save = 'X{} Y{} Z{}'.format(point_to_save[0], point_to_save[1], point_to_save[2])
                self.log_display.append(string_to_save + ' | ' + point.gcode_line)
            else:
                self.log_display.append(point.gcode_line)

    @staticmethod
    def update_gcode_coord(coord_word, coord_word_pre):
        if coord_word is None:
            return coord_word_pre, coord_word_pre
        else:
            return coord_word, coord_word

    @staticmethod
    def save_gcode_point_vector(vector, file_name):
        file_name = 'mod_' + os.path.basename(file_name)
        with open(file_name, 'w') as f:
            for point in vector:
                f.write(point.gcode_line + '\n')

    def parse_gcode_file(self, file_name):
        vector = []

        with open(file_name, 'r') as f:
            x_word_pre = Word('X0')
            y_word_pre = Word('Y0')
            z_word_pre = Word('Z0')

            for line_text in f.readlines():
                line = Line(line_text)

                self.log_display.append("GCODE = {}\n".format(str(line.block)))

                x_word = line.block.X
                y_word = line.block.Y
                z_word = line.block.Z

                if x_word is None and y_word is None and z_word is None:
                    vector.append(GCodePoint(None, str(line.block)))
                    continue

                x_word, x_word_pre = self.update_gcode_coord(x_word, x_word_pre)
                y_word, y_word_pre = self.update_gcode_coord(y_word, y_word_pre)
                z_word, z_word_pre = self.update_gcode_coord(z_word, z_word_pre)

                point = [x_word.value, y_word.value, z_word.value]
                self.log_display.append('parse point {}'.format(point))

                vector.append(GCodePoint(point, str(line.block)))

        return vector

    @staticmethod
    def get_point_from_vector(vector, index):
        return vector[index-2], vector[index-1], vector[index]

    def on_work_clicked(self):
        vector = self.parse_gcode_file(self.file_name)

        index = 2
        p1, p2, p3 = self.get_point_from_vector(vector, index)
        self.save_point(p1)

        for index in range(3, len(vector), 1):

            if p1.point is None and p2.point is None and p3.point is None:
                self.save_point(vector[len(vector) - 1])

            if self.check_point(p1.point, p2.point, p3.point):
                p3 = vector[index]
            else:
                self.save_point(vector[index-2])
                p1, p2, p3 = self.get_point_from_vector(vector, index)

        self.save_point(vector[len(vector) - 2])
        self.save_point(vector[len(vector) - 1])
        self.log_gcode_point_vector(self.result_vector)
        self.save_gcode_point_vector(self.result_vector, 'mod_' + self.file_name)

    def check_point(self, p1, p2, cp):
        result = C.cffi_check_point(p1, p2, cp)
        print(result)
        return result

    def check_point_origin(self, p1, p2, cp):

        d = np.array(p2) - np.array(p1)

        l, m, n = d
        x1, y1, z1 = p1
        x, y, z = np.array(cp)

        if l == 0:
            if x != x1:
                return False
            elif n * y - n * y1 == m * z - m * z1:
                return True
            else:
                return False

        if m == 0:
            if y != y1:
                return False
            elif n * x - n * x1 == l * z - l * z1:
                return True
            else:
                return False

        if n == 0:
            if z != z1:
                return False
            elif m * x - m * x1 == l * y - l * y1:
                return True
            else:
                return False

        if (n * y - m * z + (m * z1 - n * y1)) == 0 and (m * x - l * y + (l * y1 - m * x1)) == 0:
            return True
        else:
            return False

    def test(self):

        a = ([81.606, -315.75, -7.965],
             [81.906, -315.75, -0.965],
             [82.006, -315.75, -0.965])

        b = ([0, 0, 1],
             [0, 0, 2],
             [0, 0, 6])

        self.log_display.append(str(a))

        if self.check_point(a[0], a[1], a[2]):  # Fixme: should return false
            self.log_display.append("TEST OK")
        else:
            self.log_display.append("TEST NO")

        self.log_display.append(str(b))

        if self.check_point(b[0], b[1], b[2]):
            self.log_display.append("TEST OK")
        else:
            self.log_display.append("TEST NO")


def main():
    line_solver = LineSolverApp()
    line_solver.test()
    line_solver.exec()


if __name__ == "__main__":
    main()
