#!/usr/bin/python3
# # -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Progress Bar 
Description          : Class for file progress bar with  cancel
Date                 : November, 2020
copyright            : (C) 2020 by Luiz Motta
email                : motta.luiz@gmail.com

 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.PyQt.QtCore import (
    pyqtSlot, pyqtSignal
)
from qgis.PyQt.QtWidgets import (
    QWidget, QProgressBar, QPushButton,
    QStyle,
    QVBoxLayout, QHBoxLayout,
)

class WidgetProgressFiles(QWidget):
    cancel = pyqtSignal()
    def __init__(self, parent):
        def setupUI():
            def createProgressBar(layout):
                pb = QProgressBar( self )
                pb.setRange(0,100)
                pb.setTextVisible(True)
                layout.addWidget( pb )
                return pb

            # Count(ProgressBar) and Cancel
            lytCountCancel = QHBoxLayout()
            self.__dict__['pb_count'] = createProgressBar( lytCountCancel )
            w = QPushButton('Cancel', self)
            w.setIcon( self.style().standardIcon( QStyle.SP_DialogCancelButton ) )
            w.clicked.connect( self._onCancel )
            lytCountCancel.addWidget( w )
            #
            lytMain = QVBoxLayout()
            lytMain.addLayout( lytCountCancel )
            self.__dict__['pb_file'] = createProgressBar( lytMain )
            self.setLayout( lytMain )

        super().__init__( parent )
        setupUI()
        self.currentFile = None
        self.count, self.total = None, None

    @pyqtSlot(bool)
    def _onCancel(self, checked):
        self.cancel.emit()
        self.hide()

    def setDownloadFilesTotal(self, total):
        self.total = total
        self.count = 0
        self.show()

    def setDownloadFileName(self, name):
        self.currentFile = name
        self.pb_file.reset()
        #
        self.count += 1
        percent = int( self.count / self.total * 100)
        msg = f"Files: {self.count}/{self.total} ( {percent:.2f}% )"
        self.pb_count.setValue(  percent )
        self.pb_count.setFormat( msg )
        #
        if self.count == self.total:
            self.hide()

    @pyqtSlot('qint64', 'qint64')
    def receivedBytesFile(self, part, total):
        if total == 0: return
        percent = int( part / total * 100)
        part /= 1048576 # bytes -> MB
        total /= 1048576 # bytes -> MB
        msg = f"{self.currentFile}: {part:.2f}/{total:.2f} MB ( {percent}% )"
        self.pb_file.setValue(  percent )
        self.pb_file.setFormat( msg )
