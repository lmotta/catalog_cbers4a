#!/usr/bin/python3
# # -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Load Form
Description          : Script for populate From from UI file
Date                 : March, 2019
copyright            : (C) 2019 by Luiz Motta
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
import json, os

from qgis.PyQt.QtCore import (
    Qt,
    pyqtSlot,
    QUrl
)
from qgis.PyQt.QtNetwork import QNetworkRequest
from qgis.PyQt.QtWidgets import (
    QApplication,
    QLabel, QWidget,
    QTreeWidget, QTreeWidgetItem
)
from qgis.PyQt.QtGui import QPixmap

from qgis.core import (
    QgsNetworkAccessManager,
    QgsBlockingNetworkRequest,
    QgsEditFormConfig
)

import qgis.utils as QgsUtils


widgets = None

def setForm(layer):
    """
    Set layer with Form

    :param layer: QgsVectorLayer
    """
    config = QgsEditFormConfig()
    vfile = os.path.join( os.path.dirname( __file__ ), 'form.ui' )
    config.setUiForm( vfile)
    config.setInitCodeSource( QgsEditFormConfig.CodeSourceFile )
    config.setInitFunction('loadForm')
    vfile = os.path.join( os.path.dirname( __file__ ), 'form.py' )
    config.setInitFilePath( vfile)
    layer.setEditFormConfig(config)        

def populateForm(feature):
    """
    :param widgets: List of widgets
    :feature: Feature from open table(Form) in QGIS
    """
    def printStatus(message='', color='black'):
        widgets['message_status'].setStyleSheet(f"color: {color}")
        widgets['message_status'].setText( message )

    def populateThumbnail():
        def fetched():
            r = QgsNetworkAccessManager.blockingGet( request )
            if r is None:
                printStatus( 'Invalid request', 'red' )
                return
            c = r.content()
            pixmap = QPixmap()
            if not pixmap.loadFromData( c.data() ):
                printStatus( 'Invalid image from server', 'red' )
                return
            widgets['thumbnail'].setPixmap( pixmap )
            printStatus()

        printStatus('Fetching thumbnail...', 'blue')
        url = QUrl( f"{meta_json['assets']['thumbnail']['href']}" )
        request = QNetworkRequest( url )
        cf = QgsNetworkContentFetcherTask( request )
        cf.fetched.connect( fetched )
        cf.run()

    def fill_item(item, value):
        if not isinstance( value, ( dict, list ) ):
            item.setData( 1, Qt.DisplayRole, value )
            return
        if isinstance( value, dict ):
            for key, val in value.items():
                child = QTreeWidgetItem()
                child.setText( 0, key )
                item.addChild( child )
                fill_item( child, val )
            return
        if isinstance( value, list ):
            for val in value:
                if not isinstance( val, ( dict, list ) ):
                    item.setData( 1, Qt.DisplayRole, val )
                else:
                    child = QTreeWidgetItem()
                    item.addChild( child )
                    text = '[dict]' if isinstance( value, dict ) else '[list]'
                    child.setText( 0, text )
                    fill_item( child , val )
                        
    global widgets
    meta_json = json.loads( feature['meta_json'] )

    # Clean
    printStatus()
    widgets['thumbnail'].setText('')
    msg = "* Double click copy item to clipboard. Inside 'key' item = Expression, otherwise, value"
    widgets['message_clip'].setStyleSheet('color: black')
    widgets['message_clip'].setText( msg )

    # Populate 'item_id', 'date_time
    [ widgets[ name ].setText( feature[ name ] ) for name in ('item_id', 'date_time') ]

    # Populate Tree Metadata
    widgets['twMetadata'].clear()
    item = widgets['twMetadata'].invisibleRootItem()
    item.setDisabled( False )
    fill_item( item, meta_json )

    populateThumbnail()

def loadForm(dialog, layer, feature):
    @pyqtSlot('QTreeWidgetItem*', int)
    def itemDoubleClicked(item, col):
        def getExpression(keys, field_json):
            # Keys = [ child, parent, parent, ...]
            # from_json("field_json")['assets']['thumbnail']['href']
            l_key = keys.copy()
            l_key.reverse()
            l_key = [ f"['{k}']" for k in l_key ]
            l_key = ''.join(l_key)
            exp = f"from_json(\"{field_json}\"){l_key}"
            return exp

        def addKey(item, keys):
            if item is None:
                return
            keys.append( item.text(0) )
            addKey( item.parent(), keys )

        global widgets
        value = item.data( 1, Qt.DisplayRole )
        if value is None:
            return
        if col == 0:
            keys = []
            addKey(item, keys)
            msg = getExpression( keys, 'meta_json')
        else:
            msg = str( value )
        QApplication.clipboard().setText( msg )
        msg = f"Copied to clipboard: {msg}"
        widgets['message_clip'].setText( msg )
        widgets['message_clip'].setStyleSheet('color: blue')

    global widgets
    if feature.fieldNameIndex('item_id') == -1:
        return

    if widgets is None:
        widgets = {
            'item_id': dialog.findChild( QLabel, 'item_id'),
            'date_time': dialog.findChild( QLabel, 'date_time'),
            'thumbnail': dialog.findChild( QLabel, 'thumbnail'),
            'tabMetadata': dialog.findChild( QWidget, 'tabMetadata'),
            'message_clip': dialog.findChild( QLabel, 'message_clip'),
            'message_status': dialog.findChild( QLabel, 'message_status')
        }
        widgets['twMetadata'] = widgets['tabMetadata'].findChild( QTreeWidget, 'twMetadata' )
        widgets['twMetadata'].itemDoubleClicked.connect( itemDoubleClicked )
        widgets['twMetadata'].setHeaderHidden( False )

    populateForm( feature )
