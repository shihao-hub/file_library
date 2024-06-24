# -*- coding: utf-8 -*-
import sys
import time
import traceback
from datetime import datetime
import pprint
import re
import unittest
import threading

# Form implementation generated from reading ui file 'demo.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QTimer, QDateTime, Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QMenu, QAction, QMessageBox, QFileDialog

from ui.demo import Ui_MainWindow

DEBUG = True


class MainWindow(Ui_MainWindow):
    def __init__(self, main_window):
        self.main_window = main_window
        self.setupUi(main_window)

        main_window.setWindowFlags(main_window.windowFlags() & ~Qt.WindowMaximizeButtonHint)

        self.text_collation_button.clicked.connect(self.text_collation)
        self.text_collation_button.setContextMenuPolicy(Qt.CustomContextMenu)
        self.text_collation_button.customContextMenuRequested.connect(self.set_menu_for_text_collation_button)

        self.text_rm_dup_button.clicked.connect(self.text_remove_duplicates)
        self.text_rm_dup_button.setContextMenuPolicy(Qt.CustomContextMenu)
        self.text_rm_dup_button.customContextMenuRequested.connect(self.set_menu_for_text_rm_dup_button)

        self.timer_for_current_time_label = QTimer()
        self.timer_for_current_time_label.timeout.connect(self.update_current_time)
        self.timer_for_current_time_label.start(1000)  # 设置定时器每秒更新一次
        self.current_time_label.setStyleSheet("color: black;")
        # self.current_time_label.setStyleSheet("background-color: white; color: black;")
        # self.current_time_label.setFixedHeight(40)
        self.current_time_label.setWordWrap(True)
        # self.current_time_label.setFont(QFont("微软雅黑", 10))
        # self.current_time_label.setVisible(True)
        self._set_current_time_for_current_time_label()

        self.md5_button.clicked.connect(self.callback_for_md5)

        self.input_clear_button.clicked.connect(lambda: self.input_text_edit.clear())
        self.input_clear_button.hide()
        self.output_clear_button.clicked.connect(lambda: self.output_text_edit.clear())
        self.output_clear_button.hide()
        self.log_clear_button.clicked.connect(lambda: self.log_text_edit.clear())

        self.actionTest.triggered.connect(self.callback_for_actionTest)

        self.actionOpen.setShortcut("Ctrl+H")
        self.actionOpen.triggered.connect(self.callback_for_actionOpen)

    def callback_for_md5(self):
        pass

    def callback_for_actionTest(self):
        def assert_equal(first, second, msg=None):
            if first != second:
                if isinstance(first, str):
                    first = first.replace("\r", r"\r")
                    first = first.replace("\n", r"\n")
                    first = first.replace("\t", r"\t")
                    second = second.replace("\r", r"\r")
                    second = second.replace("\n", r"\n")
                    second = second.replace("\t", r"\t")
                raise AssertionError(f'{first} != {second}{"" if not msg else " : " + msg}')

        write = sys.stderr.write
        time_s = time.time()
        count, max_count = 0, 1
        try:
            # 文本整理
            self.input_text_edit.setPlainText("我is李华")
            self.text_collation()
            output = self.output_text_edit.toPlainText()
            assert_equal(output, "我 is 李华", "text_collation error")
            count += 1  # 需要手动自增，这个不好，需要优化
            self.input_text_edit.clear()
            self.output_text_edit.clear()

            # 文本去重
            self.input_text_edit.setPlainText("abc\r\nabc\r\ndef")
            self.text_remove_duplicates()
            output = self.output_text_edit.toPlainText()
            assert_equal(output, "abc\ndef", "text_remove_duplicates error")
            count += 1
            self.input_text_edit.clear()
            self.output_text_edit.clear()
        except:
            write(traceback.format_exc())
            write("\n")

            write(f"Ran {count + 1} test in {(time.time() - time_s):.4f}s\n\n")
            write(f"FAILED (failures={max_count - count})\n\n")
        else:
            count = count  # 占个位置

            write(f"Ran {count} test in {(time.time() - time_s):.4f}s\n\n")
            write("OK\n\n")
        finally:
            pass

    def callback_for_actionOpen(self):
        filename, _ = QFileDialog.getSaveFileName(self.main_window,
                                                  'Save File',
                                                  '',
                                                  'Text Files (*.txt);;All Files (*)')

    def logger(self, msg: str, level=0):
        prefix = (" INFO", "DEBUG", "FATAL")[level]
        self.log_text_edit.appendPlainText("["
                                           + datetime.now().strftime(f"{'%Y-%m-%d %H:%M:%S'[0 if not DEBUG else 9:]}")
                                           + " "
                                           + prefix
                                           + "]:  "
                                           + msg)

    def set_menu_for_text_collation_button(self, position):
        menu = QMenu(self.text_collation_button)

        action1 = QAction("仅处理剪切板")
        action1.triggered.connect(lambda: self.text_collation(True))
        menu.addAction(action1)

        menu.exec_(self.text_collation_button.mapToGlobal(position))

    def set_menu_for_text_rm_dup_button(self, position):
        menu = QMenu(self.text_rm_dup_button)

        action1 = QAction("仅处理剪切板")
        action1.triggered.connect(lambda: self.text_remove_duplicates(True))
        menu.addAction(action1)

        menu.exec_(self.text_rm_dup_button.mapToGlobal(position))

    def update_current_time(self):
        self._set_current_time_for_current_time_label()

    def _set_current_time_for_current_time_label(self):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.current_time_label.setText(current_time)

    def text_collation(self, enable_clip=None):

        try:
            import pyperclip
            import pangu

            if enable_clip:
                # 剪切板上的 \n 会被存储为 \r\n 所以会多出字符来
                text = pyperclip.paste()
                res_len = len(text)
                pyperclip.copy(pangu.spacing_text(text))
                del text
            else:
                text = self.input_text_edit.toPlainText()
                res_len = len(text)
                self.output_text_edit.setPlainText(pangu.spacing_text(text))
                del text
        except:
            print(traceback.format_exc())
        else:
            msg = f"文本整理结束，共处理 {res_len} 个字符。"
            self.logger(msg)
            # QMessageBox.information(self.main_window, "通知", msg)

    def _dedup_for_text_remove_duplicates(self, lines):
        seen = set()
        for line in lines:
            if line not in seen:
                yield line
                seen.add(line)

    def text_remove_duplicates(self, enable_clip=None):
        try:
            import pyperclip
            if enable_clip:
                res = []
                text = pyperclip.paste()
                res_len = len(text)
                lines = re.compile(r"\r*\n").split(text)
                for line in self._dedup_for_text_remove_duplicates(lines):
                    res.append(line)
                # res_len = len(res) - 1 + sum(len(e) for e in res)
                pyperclip.copy("\n".join(res))
                del res, lines, text
            else:
                res = []
                text = pyperclip.paste()
                res_len = len(text)
                lines = re.compile(r"\r*\n").split(self.input_text_edit.toPlainText())
                for line in self._dedup_for_text_remove_duplicates(lines):
                    res.append(line)
                # res_len = len(res) - 1 + sum(len(e) for e in res)
                self.output_text_edit.setPlainText("\n".join(res))
                del res, lines, text
        except:
            print(traceback.format_exc())
        else:
            msg = f"文本去重结束，共处理 {res_len} 个字符。"
            self.logger(msg)
            # QMessageBox.information(self.main_window, "通知", msg)

    def pdf_merger(self, files, out_file):
        try:
            import PyPDF2

            # files = []
            # out_file = ""

            if not files or not out_file:
                return

            merger = PyPDF2.PdfMerger()
            for path in files:
                merger.append(path)

            merger.write(out_file)
            merger.close()
        except:
            print(traceback.format_exc())
        else:
            print("PDF 合并结束。")


class Ui_MainWindow_Test(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_for_all(self):
        pass

    def test_for_pdf_merger(self):
        self.assertEqual("1", "2")
        import PyPDF2

        in_files = [
            r"../resources/in0.pdf",
            r"../resources/in1.pdf",
            r"../resources/in2.pdf",
        ]

        out_file = r"../resources/out.pdf"

        Ui_MainWindow().pdf_merger(in_files, out_file)

        out_pdf = PyPDF2.PdfReader(out_file)
        self.assertEqual(len(out_pdf.pages), sum([(len(PyPDF2.PdfReader(e).pages)) for e in in_files]))


if __name__ == '__main__':
    unittest.main()
