import json, os

from qgis.PyQt.QtCore import (
    Qt, QObject,
    QUrl,
    pyqtSlot, pyqtSignal
)
from qgis.PyQt.QtWidgets import (
    QApplication,
    QDialog,
    QWidget, QDockWidget, QPushButton,
    QVBoxLayout
)


from qgis.core import (
    Qgis, QgsProject, QgsApplication,
    QgsNetworkContentFetcherTask,
    QgsCoordinateReferenceSystem, QgsCoordinateTransform,
    QgsVectorLayer, QgsFeature, QgsGeometry, QgsPointXY
)
from qgis.gui import QgsMessageBar

from .form import setForm as FORM_setForm


class DockWidgetCbers4a(QDockWidget):
    MESSAGE_TITLE = 'Cbers4a server'
    def __init__(self, iface):
        def setupWidget():
            wgtMain = QWidget( self )
            wgtMain.setAttribute(Qt.WA_DeleteOnClose)
            
            msgBar = QgsMessageBar( wgtMain )
            btnTest = QPushButton('test', wgtMain )
            btnCancel = QPushButton('CANCEL', wgtMain )

            layout = QVBoxLayout()
            layout.addWidget( msgBar )
            layout.addWidget( btnTest )
            layout.addWidget( btnCancel )
            wgtMain.setLayout( layout )

            return wgtMain, msgBar, btnTest, btnCancel

        super().__init__('Catalog Cbers4a', iface.mainWindow() )
        # GUI
        self.setObjectName('catalogcbers4a_dockwidget')
        wgtMain, self.msgBar, btnTest, btnCancel = setupWidget()
        self.setWidget( wgtMain )

        self.cc = CatalogCbers4a( iface)
        self.cc.init()
        btnTest.clicked.connect( self._onTest )
        btnCancel.clicked.connect( self._onCancel )
        self.cc.message.connect( self.message )

    def writeSetting(self):
        pass

    @pyqtSlot(bool)
    def _onTest(self, checked):
        args = {
            'collection': 'CBERS4A_WPM_L4_DN',
            's_date1': '2019-06-09',
            's_date2': '2020-11-03'
        }
        self.cc.search( **args )

    @pyqtSlot(bool)
    def _onCancel(self, checked):
        self.cc.cancel()

    @pyqtSlot(Qgis.MessageLevel, str)
    def message(self, level, message):
        funcs = {
            Qgis.Info: self.msgBar.pushInfo,
            Qgis.Warning: self.msgBar.pushWarning,
            Qgis.Critical: self.msgBar.pushCritical,
            Qgis.Success: self.msgBar.pushSuccess
        }
        if not level in funcs:
            return
        self.msgBar.popWidget()
        funcs[ level ]( self.MESSAGE_TITLE, message )


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
    message = pyqtSignal(Qgis.MessageLevel, str)
    def __init__(self, iface):
        super().__init__()
        self.mapCanvas = iface.mapCanvas()
        self.project = QgsProject.instance()
        self.layerTreeRoot = self.project.layerTreeRoot()
        self.styleFile = os.path.join( os.path.dirname( __file__ ), 'catalog.qml' )
        self.taskManager = QgsApplication.taskManager()

        self.catalog, self.catalog_id = None, None
        self.taskId = None
        self.requestData = {
            'item_type': None,
            'date1': None, 'date2': None,
            'limit': None
        }
        
    def init(self):
        self.message.emit( Qgis.Info, 'Checking server...')
        # Test server

    def search(self, collection, s_date1, s_date2):
        def closeTableAttribute():
            layer_id = self.catalog_id
            widgets = QApplication.instance().allWidgets()
            for tb in filter( lambda w: isinstance( w, QDialog ) and layer_id in w.objectName(),  widgets ):
                tb.close()

        def create():
            def setCatalog(item_type, date1, date2):
                self.catalog.setCustomProperty('item_type', item_type )
                self.catalog.setCustomProperty('date1', date1 )
                self.catalog.setCustomProperty('date2', date2 )
                self.catalog.loadNamedStyle( self.styleFile )

            l_fields = [ f"field={k}:{v}" for k,v in self.FIELDSDEF.items() ]
            l_fields.insert( 0, f"Multipolygon?crs={self.CRS.authid().lower()}" )
            l_fields.append( "index=yes" )
            uri = '&'.join( l_fields )
            arg = ( self.requestData['item_type'], self.requestData['date1'], self.requestData['date2'] )
            name = self.FORMAT_NAME.format( *arg )
            self.catalog = QgsVectorLayer( uri, name, 'memory' )
            setCatalog( *arg )
            FORM_setForm( self.catalog )
            # Exp: from_json("meta_json")['assets']['thumbnail']['href']
            #self.menuCatalog.setLayer( self.catalog )
            self.catalog_id = self.catalog.id()

        def populate():
            def update():
                item_type = self.catalog.customProperty('item_type')
                date1 = self.catalog.customProperty('date1')
                date2 = self.catalog.customProperty('date2')
                arg = ( item_type, date1, date2 )
                name = self.FORMAT_NAME.format( *arg )
                self.catalog.setName( name )
                self.catalog.triggerRepaint()
                ltl = self.layerTreeRoot.findLayer( self.catalog_id )
                for b in ( False, True ): ltl.setCustomProperty('showFeatureCount', b )

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

                    provider = self.catalog.dataProvider()
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

                self.taskId = None
                s_json = task.contentAsString()
                if not s_json:
                    self.message.emit( Qgis.Warning, 'Canceled by user' )
                    if existsCatalog: update()
                    return
                d_json = json.loads(  s_json )
                if not 'features' in d_json:
                    msg = f"Error server: {s_json}"
                    self.message.emit( Qgis.Critical, msg )
                    if existsCatalog: update()
                    return

                total = len( d_json['features'] )
                if total == 0:
                    self.message.emit( Qgis.Warning, 'Not found scenes' )
                    if existsCatalog: update()
                    return
                
                self.message.emit( Qgis.Info, f"Found {total} scenes" )
                addFeatures( d_json['features'] )

                # Add/Update layer
                if not existsCatalog:
                    self.project.addMapLayer( self.catalog, addToLegend=False )
                    self.layerTreeRoot.insertLayer( 0, self.catalog ).setCustomProperty('showFeatureCount', True)
                else:
                    update()

            def getUrlParams():
                def getBbox():
                    e = self.mapCanvas.extent()
                    crs = self.mapCanvas.mapSettings().destinationCrs()
                    if not self.CRS == crs:
                        ct = QgsCoordinateTransform( crs, self.CRS, self.project )
                        e = ct.transform( e )
                    return [ e.xMinimum(), e.yMinimum(), e.xMaximum(), e.yMaximum() ]
                    
                v_datetime = f"{self.requestData['date1']}T00:00:00/{self.requestData['date2']}T00:00:00"
                bbox = [ f"{v}" for v in getBbox() ]
                bbox = ','.join( bbox )
                d = {
                    'bbox': bbox,
                    'collections': self.requestData['item_type'],
                    'limit': self.LIMIT,
                    'datetime': v_datetime
                }
                params = [ f"{k}={v}" for k,v in d.items() ]
                params = '&'.join( params )
                url = f"{self.URLS['search']}?{params}"
                return QUrl( url )

            if self.taskId:
                return

            task = QgsNetworkContentFetcherTask( getUrlParams() )
            task.fetched.connect( fetched )
            existsCatalog = not self.catalog is None and not self.project.mapLayer( self.catalog_id ) is None
            if existsCatalog:
                task.setDependentLayers( [ self.catalog ] )
            self.taskId = self.taskManager.addTask( task )

        if self.mapCanvas.layerCount() == 0:
            msg = 'Need layer(s) in map'
            self.message.emit( Qgis.Critical, msg )
            return

        self.requestData['item_type'] = collection
        self.requestData['date1'], self.requestData['date2'] = s_date1, s_date2

        existsCatalog = not self.catalog is None and not self.project.mapLayer( self.catalog_id ) is None
        if not existsCatalog:
            create()            
        else:
            self.catalog.dataProvider().truncate() # Delete all features
            closeTableAttribute()
        
        self.message.emit( Qgis.Info, 'Searching scenes...' )
        populate()

    def cancel(self):
        if self.taskId:
            task = self.taskManager.task( self.taskId )
            task.cancel()
