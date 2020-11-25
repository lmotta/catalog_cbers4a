# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Catalog Cbers4a
Description          : This plugin lets you get the catalog of Cbers4a
Date                 : December, 2020
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
__author__ = 'Luiz Motta'
__date__ = '2020-11-24'
__copyright__ = '(C) 2020, Luiz Motta'
__revision__ = '$Format:%H$'

import json, os
from collections import deque

from osgeo import gdal

from qgis.PyQt.QtCore import (
    Qt,
    QSettings,
    QObject,
    QUrl,
    QDate,
    QRegExp, QRegularExpression,
    pyqtSlot, pyqtSignal,
    QEventLoop
)
from qgis.PyQt.QtWidgets import (
    QApplication,
    QStyle, QSizePolicy,
    QDialog,
    QWidget, QLabel,
    QPushButton, QCheckBox,
    QDateEdit, QSpinBox, QLineEdit,
    QSpacerItem,
    QDockWidget, QComboBox, QGroupBox,
    QVBoxLayout, QHBoxLayout
)
from qgis.PyQt.QtGui import QRegularExpressionValidator

from qgis.core import (
    Qgis, QgsProject, QgsApplication,
    QgsTask,
    QgsNetworkContentFetcherTask,
    QgsFileDownloader,
    QgsCoordinateReferenceSystem, QgsCoordinateTransform,
    QgsMapLayer, QgsVectorLayer, QgsFeature, QgsGeometry, QgsPointXY,
    QgsMapLayerType
)
from qgis.gui import (
    QgsMessageBar,
    QgsFileWidget,
    QgsPasswordLineEdit
)

from .form import setForm as FORM_setForm
from .menulayer import MenuCatalog
from .widgetprogressfiles import WidgetProgressFiles

class DockWidgetCbers4a(QDockWidget):
    TITLE = 'Cbers4a'
    def __init__(self, iface):
        def getIcons():
            fIcon = self.style().standardIcon
            return {
                'apply': fIcon( QStyle.SP_DialogApplyButton ),
                'cancel': fIcon( QStyle.SP_DialogCancelButton )
            }

        def setupUI():
            def createDateEdit(name, layout, displayFormat, hasCalendar, parent):
                layout.addWidget( QLabel( name ) )
                w = QDateEdit( parent )
                w.setCalendarPopup( True )
                w.setDisplayFormat( displayFormat )
                w.setCalendarPopup( hasCalendar )
                layout.addWidget( w )
                return w

            def setSearch(wgtMain, lytMain):
                wgt = QWidget( wgtMain )
                layout = QHBoxLayout( wgt )
                # Assets
                w = QComboBox( wgt )
                w.setSizeAdjustPolicy( QComboBox.AdjustToContents )
                self.__dict__['assets'] = w
                layout.addWidget( w )
                # Dates
                lyt = QHBoxLayout()
                self.__dict__['fromDate'] = createDateEdit( 'From', lyt, 'yyyy-MM-dd', True, wgt )
                self.__dict__['toDate'] = createDateEdit( 'From', lyt, 'yyyy-MM-dd', True, wgt )
                layout.addLayout( lyt )
                # Days
                w = QSpinBox( wgt )
                self.__dict__['numDays'] = w
                w.setSingleStep( 1 )
                w.setSuffix(' Days')
                w.setRange( 1, 360000 )
                layout.addWidget( w )
                # Search
                w = QPushButton('Search', wgt )
                self.__dict__['search'] = w
                w.setIcon( self.icons['apply'] )
                w.clicked.connect( self._onSearch )
                layout.addWidget( w )
                # Spacer
                w = QSpacerItem( 10, 10, QSizePolicy.Expanding, QSizePolicy.Minimum )
                layout.addItem( w )
                #
                wgt.setLayout( layout )
                lytMain.addWidget( wgt )

            def setDownload(wgtMain, lytMain):
                wgt = QGroupBox('Download', wgtMain )
                self.__dict__['wgtDownload'] = wgt
                layout = QHBoxLayout( wgt )
                # Bands
                layoutBands = QHBoxLayout( wgt )
                self.__dict__['layoutBands'] = layoutBands
                layout.addLayout( layoutBands )
                # Download
                w = QgsFileWidget( wgt )
                self.__dict__['pathDownload'] = w
                w.setStorageMode( QgsFileWidget.GetDirectory )
                w.setDialogTitle('Select download path')
                w.setFileWidgetButtonVisible( True )
                layout.addWidget( w )
                # Key
                w = QgsPasswordLineEdit(wgt )
                self.__dict__['email'] = w
                w.setPlaceholderText('someone@somewhere.com')
                w.setToolTip('Email registered at http://www2.dgi.inpe.br/catalogo/explore')
                w.setEchoMode( QLineEdit.Password )
                rx = QRegularExpression(self.emailExpEdit, QRegularExpression.CaseInsensitiveOption )
                w.setValidator( QRegularExpressionValidator( rx ) )
                layout.addWidget( w )
                w = QPushButton('Clear register key', wgt )
                w.clicked.connect( self._onClearKey )
                layout.addWidget( w )
                # Spacer
                w = QSpacerItem( 10, 10, QSizePolicy.Expanding, QSizePolicy.Minimum )
                layout.addItem( w )
                #
                wgt.setLayout( layout )
                lytMain.addWidget( wgt )
                
            wgtMain = QWidget( self )
            wgtMain.setAttribute(Qt.WA_DeleteOnClose)
            lytMain = QVBoxLayout()
            #
            msgBar = QgsMessageBar( wgtMain )
            self.__dict__['msgBar'] = msgBar
            lytMain.addWidget( msgBar )
            #
            setSearch( wgtMain, lytMain )
            setDownload( wgtMain, lytMain )
            self.__dict__['progress_files'] = WidgetProgressFiles( wgtMain )
            lytMain.addWidget( self.__dict__['progress_files'] )
            # Spacer
            w = QSpacerItem( 10, 10, QSizePolicy.Expanding, QSizePolicy.Minimum )
            lytMain.addItem( w )
            #
            wgtMain.setLayout( lytMain )
            self.setWidget( wgtMain )

        def populateAssets():
            @pyqtSlot(str)
            def changeAsset(asset):
                # Clean
                for i in reversed( range( self.layoutBands.count() ) ): 
                    self.layoutBands.itemAt(i).widget().deleteLater()
                #
                for name in self.assets_bands[ asset ]:
                    w = QCheckBox( name, self.wgtDownload )
                    w.setChecked( True )
                    self.layoutBands.addWidget( w )
                self.layoutBands.addWidget( w )

            self.assets_bands = {
                'CBERS4A_MUX_L2_DN': ['blue', 'green', 'red', 'nir'],
                'CBERS4A_MUX_L4_DN': ['blue', 'green', 'red', 'nir'],
                'CBERS4A_WFI_L2_DN': ['blue', 'green', 'red', 'nir'],
                'CBERS4A_WFI_L4_DN': ['blue', 'green', 'red', 'nir'],
                'CBERS4A_WPM_L2_DN': ['pan', 'blue', 'green', 'red', 'nir'],
                'CBERS4A_WPM_L4_DN': ['pan', 'blue', 'green', 'red', 'nir']
            }
            for asset in self.assets_bands:
                self.assets_bands[ asset ].append( '_xml')
            self.assets.addItems( self.assets_bands.keys() )
            self.assets.setCurrentIndex(0)
            changeAsset( self.assets.currentText() )
            self.assets.currentTextChanged.connect( changeAsset )

        def populateDates():
            def setSpin(date1, date2):
                self.numDays.valueChanged.disconnect( changedNumDay )
                days = date1.daysTo( date2 )
                self.numDays.setValue( days )
                self.numDays.valueChanged.connect( changedNumDay )

            @pyqtSlot(QDate)
            def changedFromDate(date):
                self.toDate.setMinimumDate( date.addDays(+1) )
                setSpin( date, self.toDate.date() )

            @pyqtSlot(QDate)
            def changedToDate(date):
                self.fromDate.setMaximumDate( date.addDays(-1) )
                setSpin( self.fromDate.date(), date )

            @pyqtSlot(int)
            def changedNumDay(days):
                newDate = self.toDate.date().addDays( -1 * days )
                self.fromDate.dateChanged.disconnect( changedFromDate )
                self.fromDate.setDate( newDate )
                self.toDate.setMinimumDate( newDate.addDays(+1) )
                self.fromDate.dateChanged.connect( changedFromDate )

            d2 = QDate.currentDate()
            d1 = d2.addMonths( -1 )
            self.fromDate.setDate( d1 )
            self.fromDate.setMaximumDate( d2.addDays( -1 ) )
            self.toDate.setDate( d2 )
            self.toDate.setMinimumDate( d1.addDays( +1 ) )
            self.numDays.setValue( d1.daysTo( d2 ) )

            self.fromDate.dateChanged.connect( changedFromDate )
            self.toDate.dateChanged.connect( changedToDate )
            self.numDays.valueChanged.connect( changedNumDay )

        def getSetting():
            params = {}
            s = QSettings()
            for k in ('path', 'email'):
                params[ k ] = s.value( self.localSetting.format( k ), None )
            if params['path'] and not os.path.isdir( params['path'] ):
                params['path'] = None
            return params

        super().__init__(self.TITLE, iface.mainWindow() )
        self.setObjectName(f"{self.TITLE}_catalogcbers4a_dockwidget")
        self.emailExpEdit = '\\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\\.[A-Z]{2,4}\\b'
        self.emailExpMath = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
        self.icons = getIcons()
        self.textSearch = { 'apply': 'Search', 'cancel': 'Cancel'}
        setupUI()
        self.progress_files.hide()
        populateAssets()
        populateDates()
        # Register
        self.localSetting = "catalog_{}/{}".format( self.TITLE, '{}')
        p = getSetting()
        if p['path']:
            self.pathDownload.setFilePath( p['path'] )
        if p['email']:
            self.email.setText( p['email'] )
        #
        self.catalog = CatalogCbers4a( iface )
        self.catalog.changeAsset = self.changeAsset
        self.catalog.changeIconSearch = self.changeIconSearch
        self.catalog.getParamsDownload = self.getParamsDownload
        self.catalog.setDownloadFilesTotal = self.progress_files.setDownloadFilesTotal
        self.catalog.setDownloadFileName = self.progress_files.setDownloadFileName
        self.catalog.receivedBytesFile =  self.progress_files.receivedBytesFile

        self.catalog.message.connect( self.message )
        self.progress_files.cancel.connect( self.catalog.cancelDownload )

    @pyqtSlot(bool)
    def _onSearch(self, checked):
        self.catalog.search( {
        'asset': self.assets.currentText(),
        'fromDate': self.fromDate.date().toString( Qt.ISODate ),
        'toDate': self.toDate.date().toString( Qt.ISODate )
        } )

    @pyqtSlot(bool)
    def _onClearKey(self, checked): self.email.setText('')

    def changeAsset(self, asset):
        self.assets.setCurrentText( asset )

    def changeIconSearch(self, name):
        if not name in self.icons:
            return
        self.search.setText( self.textSearch[ name ] )
        self.search.setIcon( self.icons[ name] )

    def getParamsDownload(self):
        def isValidEmail(key):
            rx = QRegExp( self.emailExpMath )
            return rx.exactMatch( key )

        asset = self.assets.currentText()
        bands = []
        for i in range( self.layoutBands.count() ):
            band = self.layoutBands.itemAt(i).widget()
            if band.isChecked():
                bands.append( band.text() )
        s = QSettings()
        path_download = self.pathDownload.filePath()
        if not path_download or not os.path.isdir( path_download ):
            path_download = None
        else:
            s.setValue( self.localSetting.format('path'), path_download )
        email = self.email.text()
        isValid = isValidEmail( email )
        if isValid:
            s.setValue( self.localSetting.format('email'), email )
        return {
            'asset': asset,
            'bands': bands,
            'path_download': path_download,
            'key': { 'isValid': isValid, 'value': email }
        }

    @pyqtSlot(str, Qgis.MessageLevel)
    def message(self, message, level=Qgis.Info):
        funcs = {
            Qgis.Info: self.msgBar.pushInfo,
            Qgis.Warning: self.msgBar.pushWarning,
            Qgis.Critical: self.msgBar.pushCritical,
            Qgis.Success: self.msgBar.pushSuccess
        }
        if not level in funcs:
            return
        self.msgBar.popWidget()
        funcs[ level ]( self.TITLE, message )


class CatalogCbers4a(QObject):
    URLS = {
        'search': 'http://www2.dgi.inpe.br/inpe-stac/stac/search'
    }
    FIELDSDEF = {
        'item_id': 'string(25)',
        'date_time': 'string(20)',
        'meta_json': 'string(-1)',
        'meta_jsize': 'integer'
    }
    FORMAT_NAME = "{}({} .. {})"
    CRS = QgsCoordinateReferenceSystem('EPSG:4326')
    LIMIT = 1000000
    IMAGE_NAME_PREFIX = '_BAND'
    message = pyqtSignal(str, Qgis.MessageLevel)
    nextDownload = pyqtSignal(str)
    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        # Set by DockWidget
        self.changeAsset = None
        self.changeIconSearch = None
        self.getParamsDownload = None
        self.setDownloadFilesTotal = None
        self.setDownloadFileName = None
        #
        self.project = QgsProject.instance()
        self.layerTreeRoot = self.project.layerTreeRoot()
        self.styleFile = os.path.join( os.path.dirname( __file__ ), 'catalog.qml' )
        self.taskManager = QgsApplication.taskManager()
        # self.downloadImages
        self.fileDownload = None # QgsFileDownloader
        self.fileDownloadStatus = None # { 'cancelled': False, 'error': 0, 'success': 0 }
        self.urlsDownload = deque() # { 'url': QUrl, 'name'}
        self.initDownloads = False

        funcActions = {
            'addXYZtiles': self.addXYZtiles,
            'downloadImages': self.downloadImages
        }
        self.menuCatalog = MenuCatalog( DockWidgetCbers4a.TITLE, funcActions)

        self.taskId = None

        iface.currentLayerChanged.connect( self.changedLayer )

    def __del__(self):
        del self.menuCatalog

    @pyqtSlot(QgsMapLayer)
    def changedLayer(self, layer):
        if not layer:
            return
        if not layer.type() == QgsMapLayer.VectorLayer:
            return
        asset = layer.customProperty('asset')
        if asset:
            self.changeAsset( asset )

    @pyqtSlot()
    def cancelDownload(self):
        if self.fileDownload:
            self.fileDownload.cancelDownload()

    def search(self, requestData):
        def getLayerCatalog(asset):
            isCatalog = lambda l: l.type() == QgsMapLayerType.VectorLayer and l.customProperty('asset') == asset
            for ltl in self.layerTreeRoot.findLayers():
                layer = ltl.layer()
                if isCatalog( layer ): return layer
            return None

        def closeTableAttribute(id_object):
            widgets = QApplication.instance().activeWindow().findChildren(QDialog)
            for tb in [ w for w in widgets if id_object in w.objectName() ]:
                tb.close()

        def getNameCatalog():
            arg = ( requestData['asset'], requestData['fromDate'], requestData['toDate'] )
            return self.FORMAT_NAME.format( *arg )

        def create():
            def setCustomPropertyCatalog(layer):
                for key in ( 'asset', 'fromDate', 'toDate' ):
                    layer.setCustomProperty( key, requestData[ key] )
                layer.setCustomProperty("skipMemoryLayersCheck", 1 )
                layer.setCustomProperty('showFeatureCount', True )

            l_fields = [ f"field={k}:{v}" for k,v in self.FIELDSDEF.items() ]
            l_fields.insert( 0, f"Multipolygon?crs={self.CRS.authid().lower()}" )
            l_fields.append( "index=yes" )
            uri = '&'.join( l_fields )
            name = getNameCatalog()
            layer = QgsVectorLayer( uri, name, 'memory' )
            layer.loadNamedStyle( self.styleFile )
            setCustomPropertyCatalog( layer )
            FORM_setForm( layer )
            self.menuCatalog.setLayer( layer )
            return layer

        def populate(layer, exists):
            def fetched():
                def addFeatures(json_features):
                    def getGeometry(json_geometry):
                        def getPolygonPoints(coordinates):
                            polylines = []
                            for line in coordinates:
                                polyline = [ QgsPointXY( p[0], p[1] ) for p in line ]
                                polylines.append( polyline )
                            return polylines

                        if json_geometry['type'] == 'Polygon':
                            polygon = getPolygonPoints( json_geometry['coordinates'] )
                            return QgsGeometry.fromMultiPolygonXY( [ polygon ] )
                        elif json_geometry['type'] == 'MultiPolygon':
                            polygons= []
                            for polygon in geometry['coordinates']:
                                polygons.append( getPolygonPoints( polygon ) )
                            return QgsGeometry.fromMultiPolygonXY( polygons )

                        else:
                            None

                    provider = layer.dataProvider()
                    for feat in json_features:
                        f =  { }
                        f['item_id'] = feat['id']
                        f['date_time'] = feat['properties']['datetime']
                        meta_json = {
                            'path': feat['properties']['path'],
                            'row': feat['properties']['row'],
                            'cloud_cover': feat['properties']['cloud_cover'],
                            'assets': feat['assets'].copy()
                        }
                        f['meta_json'] = json.dumps( meta_json )
                        f['meta_jsize'] = len( f['meta_json'] )
                        atts = [ f[k] for k in self.FIELDSDEF ]
                        qfeat = QgsFeature()
                        qfeat.setAttributes( atts )
                        g = getGeometry( feat['geometry'])
                        if not g is None: qfeat.setGeometry( g )
                        provider.addFeature( qfeat )
                    layer.updateExtents()

                def updateShowFeatureCount():
                    ltl = self.layerTreeRoot.findLayer( layer.id() )
                    for b in (False, True): ltl.setCustomProperty('showFeatureCount', b)

                self.changeIconSearch('apply')
                self.taskId = None
                s_json = task.contentAsString()
                if not s_json:
                    self.message.emit('Canceled by user', Qgis.Warning )
                    return
                d_json = json.loads(  s_json )
                if not 'features' in d_json:
                    msg = f"Error '{self.URLS['search']}': {s_json}"
                    self.message.emit( msg, Qgis.Critical )
                    return

                total = len( d_json['features'] )
                if total == 0:
                    self.message.emit('Not found scenes', Qgis.Warning )
                    return
                
                self.message.emit(f"Found {total} scenes", Qgis.Info)
                addFeatures( d_json['features'] )
                if not exists:
                    self.project.addMapLayer( layer, addToLegend=False )
                    self.layerTreeRoot.insertLayer( 0, layer ).setCustomProperty('showFeatureCount', True)
                else:
                    updateShowFeatureCount()

                self.iface.setActiveLayer( layer )

            def getUrlParams():
                def getBbox():
                    mapCanvas = self.iface.mapCanvas()
                    e = mapCanvas.extent()
                    crs = mapCanvas.mapSettings().destinationCrs()
                    if not self.CRS == crs:
                        ct = QgsCoordinateTransform( crs, self.CRS, self.project )
                        e = ct.transform( e )
                    return [ e.xMinimum(), e.yMinimum(), e.xMaximum(), e.yMaximum() ]
                    
                v_datetime = f"{requestData['fromDate']}T00:00:00/{requestData['toDate']}T23:59:59"
                bbox = [ f"{v}" for v in getBbox() ]
                bbox = ','.join( bbox )
                d = {
                    'bbox': bbox,
                    'collections': requestData['asset'],
                    'limit': self.LIMIT,
                    'time': v_datetime
                }
                params = [ f"{k}={v}" for k,v in d.items() ]
                params = '&'.join( params )
                url = f"{self.URLS['search']}?{params}"
                return QUrl( url )

            self.changeIconSearch('cancel')
            task = QgsNetworkContentFetcherTask( getUrlParams() )
            task.fetched.connect( fetched )
            self.taskId = self.taskManager.addTask( task )

        if self.taskId:
            task = self.taskManager.task( self.taskId )
            task.cancel()
            return

        if self.initDownloads:
            self.message.emit('Downloading files, please wait.', Qgis.Warning )
            return

        if self.iface.mapCanvas().layerCount() == 0:
            self.message.emit('Need layer(s) in map', Qgis.Critical )
            return

        layer = getLayerCatalog( requestData['asset'] )
        if layer:
            closeTableAttribute( layer.id() )
            layer.dataProvider().truncate()
            layer.setName( getNameCatalog() )
            exists = True
        else:
            layer = create()
            exists = False
        self.message.emit('Searching scenes...', Qgis.Info)
        populate( layer, exists )

    def actionsForm(self, nameAction, feature_id=None):
        """
        Run action defined in layer, from self.styleFile(catalog.qml)

        :param nameAction: Name of action
        :params feature_id: Feature ID
        :meta_json: Value of JSON(dictionary) from name_exp_json
        """
        # Actions functions
        def addXYZtiles(feature=None):
            self.addXYZtiles()
            return { 'isOk': True }

        def downloadImages(feature=None):
            self.downloadImages()
            return { 'isOk': True }

        actionsFunc = {
            'addxyztiles': addXYZtiles,
            'downloadImages': downloadImages
        }
        if not nameAction in actionsFunc.keys():
            return { 'isOk': False, 'message': f"Missing action '{nameAction}'" }
        return actionsFunc[ nameAction ]( feature_id )

    def addXYZtiles(self):
        layerCatalog = self.iface.activeLayer()
        self.message.emit("Missing implemetation 'addXYZtiles'", Qgis.Warning )

    def downloadImages(self):
        def populateUrls(layerCatalog, asset, key, bands):
            def addUrls(item_id, band, url):
                d = {
                    'band': band,
                    'name': os.path.basename( url ),
                    'url': QUrl(f"{url}?email={key}&item_id={item_id}&collection={asset}")
                }
                self.urlsDownload.append( d )

            hasXml = False
            if '_xml' in bands:
                hasXml = True
                bands.remove('_xml')

            self.urlsDownload.clear()
            for feat in layerCatalog.getSelectedFeatures():
                d = json.loads( feat['meta_json'] )
                for b in bands:
                    url = d['assets'][ b ]['href']
                    addUrls( feat['item_id'], b, url )
                    if hasXml:
                        url = d['assets'][ f"{b}_xml" ]['href']

        def download(path_download):
            def finishedDownload():
                self.nextDownload.disconnect( download )
                msg = "Download"
                if self.fileDownloadStatus['cancelled']:
                    level = Qgis.Warning
                    msg = f"{msg}(Cancelled by user):"
                elif self.fileDownloadStatus['success'] + self.fileDownloadStatus['exists'] == 0:
                    msg = f"{msg}(no files):"
                    level = Qgis.Critical
                else:
                    msg = f"{msg}:"
                    level = Qgis.Info
                l = (
                    f"Exists ({self.fileDownloadStatus['exists']})",
                    f"Success ({self.fileDownloadStatus['success']})",
                    f"Erros ({self.fileDownloadStatus['error']})"
                )
                msg = f"{msg} {','.join( l )}"
                self.message.emit( msg, level )

            @pyqtSlot()
            def downloadCompleted(): self.fileDownloadStatus['success'] += 1
            @pyqtSlot()
            def downloadError(): self.fileDownloadStatus['error'] += 1
            @pyqtSlot()
            def downloadCanceled(): self.fileDownloadStatus['cancelled'] = True

            # Check finished download with exists file
            while True:
                if len( self.urlsDownload ) == 0:
                    finishedDownload()
                    return
                p = self.urlsDownload.pop()
                self.setDownloadFileName( p['name'] ) # Progress Bar
                filepath = os.path.join( path_download, p['name'] )
                if os.path.isfile( filepath ):
                    self.fileDownloadStatus['exists'] += 1
                else:
                    break

            loop = QEventLoop()
            self.fileDownload = QgsFileDownloader( p['url'], filepath, delayStart=True )
            self.fileDownload.downloadCompleted.connect( downloadCompleted )
            self.fileDownload.downloadCanceled.connect( downloadCanceled )
            self.fileDownload.downloadExited.connect( loop.quit )
            self.fileDownload.downloadError.connect( downloadError )
            self.fileDownload.downloadProgress.connect( self.receivedBytesFile )
            self.fileDownload.startDownload()
            loop.exec_()

            self.fileDownload = None
            finishedDownload() if self.fileDownloadStatus['cancelled'] else self.nextDownload.emit( path_download )

        def getLayersStack(path_download):
            layersStack = {}
            for item in self.urlsDownload:
                if item['band'] == 'pan': continue
                image = item['name']
                name = image[:image.index( self.IMAGE_NAME_PREFIX ) ]
                if not name in layersStack:
                    layersStack[ name ] = {}
                filepath = os.path.join( path_download, image)
                layersStack[ name ][ item['band'] ] = filepath
            return layersStack

        def addCanvasLayersStack( layersStack, path_download, bands):
            def finished(exception, dataResult=None):
                def getSourceRasterLayer():
                    isRaster = lambda ltl: ltl.layer().type() == QgsMapLayerType.RasterLayer
                    return [ ltl.layer().source() for ltl in self.layerTreeRoot.findLayers() if isRaster( ltl ) ]

                sources = getSourceRasterLayer()
                for item in dataResult:
                    ( filepath, name_ ) = item
                    if filepath in sources: continue
                    self.iface.addRasterLayer( *item )

            def run(task):
                filepaths = []
                prefix = '_'.join( [ b for b in bands if b != 'pan'] )
                for name, band_files in layersStack.items():
                    lyrName = f"{name}_{prefix}"
                    filepath = os.path.join( path_download, f"{lyrName}.vrt")
                    if not os.path.isfile( filepath ):
                        images = [ band_files[ b ] for b in bands ]
                        ds = gdal.BuildVRT( filepath, images, separate=True )
                        ds = None
                    filepaths.append( ( filepath, lyrName ) )
                return filepaths

            task = QgsTask.fromFunction('Catalog Cbers4a Task', run, on_finished=finished )
            self.taskManager.addTask( task )
            # r = task.run()
            # finished(None, r)

        if self.initDownloads:
            self.message.emit('Downloading files, please wait.', Qgis.Warning )
            return

        lyr = self.iface.activeLayer()
        totalFeats = lyr.selectedFeatureCount()
        if totalFeats == 0:
            self.message.emit("Need select features", Qgis.Warning )
            return
        p = self.getParamsDownload()
        if not p['path_download']:
            self.message.emit('Need download path', Qgis.Warning )
            return
        if not p['key']['isValid']:
            self.message.emit('Key is not valid', Qgis.Warning )
            return

        populateUrls( lyr, p['asset'], p['key']['value'], p['bands'] )
        layersStack = None
        if len( p['bands'] ) > 1:
            layersStack = getLayersStack( p['path_download'] ) # { 'image_id': { 'band': filepath, ...}, ..., }
        # Downloads
        self.fileDownloadStatus = { 'cancelled': False, 'error': 0, 'success': 0, 'exists': 0 }
        self.setDownloadFilesTotal( len( self.urlsDownload) ) # Progress Bar
        self.nextDownload.connect(  download ) # Recursive
        #
        self.initDownloads = True
        download(p['path_download'])
        self.initDownloads = False
        # Add Stack VRT
        existsFiles = self.fileDownloadStatus['success'] + self.fileDownloadStatus['exists'] > 0
        if not layersStack or self.fileDownloadStatus['cancelled'] or not existsFiles: return
        bands_stack = [ 'red', 'green', 'blue' ]
        total = 0
        for b in bands_stack: total += p['bands'].count( b )
        if total == 3:
            for b in p['bands']:
                if bands_stack .count( b ) == 0: bands_stack.append( b )
            addCanvasLayersStack( layersStack, p['path_download'], bands_stack )
        else:
            addCanvasLayersStack( layersStack, p['path_download'], p['bands'] )

        
