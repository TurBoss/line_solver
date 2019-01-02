#!/usr/bin/env python
# -*- coding: utf-8 -*


from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QFileDialog, QTextEdit
from copy import copy
import numpy as np
from pygcode import Line, GCodeLinearMove, GCodeRapidMove


class LineSolverApp:

    def __init__(self):

        self.file_name = None

        self.previous_pos = [0, 0, 0]
        self.current_pos = [0, 0, 0]
        self.new_pos = [0, 0, 0]

        self.first_point = [0, 0, 0]
        self.second_point = [0, 0, 0]
        self.third_point = [0, 0, 0]

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

        self.test()
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

    def on_work_clicked(self):

        with open(self.file_name, 'r') as f:
            for line_text in f.readlines():
                line = Line(line_text)

                self.log_display.append("GCODE = {}\n".format(str(line.block)))

                # if len(line.block.gcodes):
                #     if isinstance(line.block.gcodes[0],
                #                   GCodeLinearMove) or isinstance(line.block.gcodes[0],
                #                                                  GCodeRapidMove):

                x_word = line.block.X
                y_word = line.block.Y
                z_word = line.block.Z

                if x_word is None:
                    self.current_pos[0] = self.previous_pos[0]
                    self.third_point[0] = self.previous_pos[0]
                else:
                    self.current_pos[0] = x_word.value
                    self.third_point[0] = x_word.value

                if y_word is None:
                    self.current_pos[1] = self.previous_pos[1]
                    self.third_point[1] = self.previous_pos[1]
                else:
                    self.current_pos[1] = y_word.value
                    self.third_point[1] = y_word.value

                if z_word is None:
                    self.current_pos[2] = self.previous_pos[2]
                    self.third_point[2] = self.previous_pos[2]
                else:
                    self.current_pos[2] = z_word.value
                    self.third_point[2] = z_word.value

                # print("previous:\t", self.previous_pos)
                # print("current:\t", self.current_pos)
                # print()

                self.log_display.append(
                    "first point =\t{}\nsecond point =\t{}\nthird point =\t{}".format(self.first_point,
                                                                                      self.second_point,
                                                                                      self.third_point)
                )

                self.first_point = copy(self.previous_pos)
                self.second_point = copy(self.current_pos)

                self.previous_pos = copy(self.current_pos)

                if not self.check_point(self.first_point, self.second_point, self.third_point):
                    self.log_display.append("Hurray!\n\n###################################\n")
                else:
                    self.log_display.append("xusta\n\n###################################\n")

    def check_point(self, p1, p2, cp):

        d = np.array(p1) - np.array(p2)

        l, m, n = d
        x1, y1, z1 = p1
        x, y, z = np.array(cp)

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
             [0, 0.1, 6])

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
    line_solver.exec()


if __name__ == "__main__":
    main()
