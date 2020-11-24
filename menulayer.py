#!/usr/bin/python3
# # -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Menu Layer
Description          : Classes for add Menu in layer
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

from qgis.PyQt.QtCore import QObject, pyqtSlot
from qgis.PyQt.QtWidgets import QApplication, QAction

from qgis.core import (
    QgsProject,
    QgsMapLayer,
    QgsGeometry,
    QgsFeature, QgsFeatureRequest
)
import qgis.utils as QgsUtils

class MenuCatalog(QObject):
    def __init__(self, menuName, funcActions):
        def initMenuLayer(menuName):
            self.menuLayer = [
            {
                'menu': u"Add XYZ tiles",
                'slot': self.addXYZtiles,
                'action': None
            },
            {
                'menu': u"Download images",
                'slot': self.downloadImages,
                'action': None
            }
            ]
            for item in self.menuLayer:
                item['action'] = QAction( item['menu'], None )
                item['action'].triggered.connect( item['slot'] )
                QgsUtils.iface.addCustomActionForLayerType( item['action'], menuName, QgsMapLayer.VectorLayer, False )

        super().__init__()
        initMenuLayer( menuName )
        self.funcActions = funcActions

    def __del__(self):
        for item in self.menuLayer:
            QgsUtils.iface.removeCustomActionForLayerType( item['action'] )

    def setLayer(self, layer):
        for item in self.menuLayer:
            QgsUtils.iface.addCustomActionForLayer( item['action'],  layer )

    @pyqtSlot(bool)
    def addXYZtiles(self, checked):
        self.funcActions['addXYZtiles']()

    @pyqtSlot(bool)
    def downloadImages(self, checked):
        self.funcActions['downloadImages']()
