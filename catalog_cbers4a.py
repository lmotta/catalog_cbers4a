import json, os

from qgis.PyQt.QtCore import (
    Qt,
    QObject,
    QUrl,
    pyqtSlot, pyqtSignal
)
from qgis.PyQt.QtWidgets import (
    QApplication,
    QDialog,
    QWidget, QDockWidget, QPushButton,
    QVBoxLayout
)
from qgis.PyQt.QtNetwork import QNetworkRequest

from qgis.core import (
    Qgis, QgsProject,
    QgsBlockingNetworkRequest,
    QgsCoordinateReferenceSystem, QgsCoordinateTransform,
    QgsVectorLayer, QgsFeature, QgsGeometry, QgsPointXY
)
from qgis.gui import QgsMessageBar

from .form import setForm as FORM_setForm

# Verificar 
# . QgsBlockingNetworkRequest
# .. https://qgis.org/api/classQgsBlockingNetworkRequest.html
# .. downloadFinished, downloadProgress
# . QgsNetworkContentFetcher
# .. https://qgis.org/api/classQgsNetworkContentFetcher.html

class DockWidgetCbers4a(QDockWidget):
    MESSAGE_TITLE = 'Cbers4a server'
    def __init__(self, iface):
        def setupWidget():
            wgtMain = QWidget( self )
            wgtMain.setAttribute(Qt.WA_DeleteOnClose)
            
            msgBar = QgsMessageBar( wgtMain )
            btnTest = QPushButton('test', wgtMain )

            layout = QVBoxLayout()
            layout.addWidget( msgBar )
            layout.addWidget( btnTest )
            wgtMain.setLayout( layout )

            return wgtMain, msgBar, btnTest

        super().__init__('Catalog Cbers4a', iface.mainWindow() )

        # GUI
        self.setObjectName('catalogcbers4a_dockwidget')
        wgtMain, self.msgBar, btnTest = setupWidget()
        self.setWidget( wgtMain )

        self.cc = CatalogCbers4a( iface)
        self.cc.init()
        collection, s_date1, s_date2, cloud_cover = 'CBERS4A_WPM_L4_DN', '2019-06-09', '2020-11-03', 20
        self.cc.setDataSearch( collection, s_date1, s_date2, cloud_cover )

        btnTest.clicked.connect( self._onTest )
        self.cc.message.connect( self.message )

    def writeSetting(self):
        pass

    @pyqtSlot(bool)
    def _onTest(self, checked):
        self.cc.search()

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
        self.mapCanvas = iface.mapCanvas()
        self.project = QgsProject.instance()
        self.layerTreeRoot = self.project.layerTreeRoot()
        self.styleFile = os.path.join( os.path.dirname( __file__ ), 'catalog.qml' )
        self.styleFile = '/home/lmotta/data/catalog_cbers4a/py/catalog.qml'
        super().__init__()
        self.catalog, self.catalog_id = None, None
        self.requestSearch = None
        self.requestData = {
            'item_type': None,
            'date1': None, 'date2': None,
            'limit': None
        }

    def _setPropertyCatalog(self, item_type, date1, date2):
        self.catalog.setCustomProperty('item_type', item_type )
        self.catalog.setCustomProperty('date1', date1 )
        self.catalog.setCustomProperty('date2', date2 )

    def _setRequestSearch(self):
        url = QUrl( self.URLS['search'] )
        self.requestSearch = QNetworkRequest( url )
        self.requestSearch.setHeader( QNetworkRequest.ContentTypeHeader, 'application/json' )

        
    def _create(self):
        l_fields = [ f"field={k}:{v}" for k,v in self.FIELDSDEF.items() ]
        l_fields.insert( 0, f"Multipolygon?crs={self.CRS.authid().lower()}" )
        l_fields.append( "index=yes" )
        uri = '&'.join( l_fields )
        arg = ( self.requestData['item_type'], self.requestData['date1'], self.requestData['date2'] )
        name = self.FORMAT_NAME.format( *arg )
        self.catalog = QgsVectorLayer( uri, name, 'memory' )
        self._setPropertyCatalog( *arg )
        self.catalog.loadNamedStyle( self.styleFile )
        FORM_setForm( self.catalog )
        # Exp: from_json("meta_json")['assets']['thumbnail']['href']
        #self.menuCatalog.setLayer( self.catalog )
        self.catalog_id = self.catalog.id()

    def _populate(self, existsCatalog):
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

        def search():
            def getData():
                def getBbox():
                    e = self.mapCanvas.extent()
                    crs = self.mapCanvas.mapSettings().destinationCrs()
                    if not self.CRS == crs:
                        ct = QgsCoordinateTransform( crs, self.CRS, self.project )
                        e = ct.transform( e )
                    return [ e.xMinimum(), e.yMinimum(), e.xMaximum(), e.yMaximum() ]
                    
                v_datetime = f"{self.requestData['date1']}T00:00:00/{self.requestData['date2']}T00:00:00"
                d_json = {
                    'bbox': getBbox(),
                    'collections': [ self.requestData['item_type'] ],
                    'query': { "cloud_cover": {"lte": self.requestData['cloud_cover']} },
                    'limit': self.LIMIT,
                    'datetime': v_datetime
                }
                s_json = json.dumps( d_json )
                return s_json.encode()

            req = QgsBlockingNetworkRequest()
            err = req.post( self.requestSearch, getData() )
            if err > 0:
                return { 'isOk': False, 'message': req.errorMessage() }
            r = req.reply()
            c = r.content()
            d_json = json.loads( c.data() )
            return { 'isOk': True, 'json': d_json }

        self.message.emit( Qgis.Info, 'Request scenes in server' )
        r = search()
        if not r['isOk']:
            self.message.emit( Qgis.Critical, r['message'] )
            if existsCatalog: update()
            return
        data = r['json']
        if len( data['features'] ) == 0:
            self.message.emit( Qgis.Warning, 'Not found scenes' )
            if existsCatalog: update()
            return
        addFeatures( data['features'] )
        # Add/Update layer
        if not existsCatalog:
            self.project.addMapLayer( self.catalog, addToLegend=False )
            self.layerTreeRoot.insertLayer( 0, self.catalog ).setCustomProperty('showFeatureCount', True)
        else:
            update()

    def init(self):
        self.message.emit( Qgis.Info, 'Checking server...')
        # Test server
        self._setRequestSearch()

    def setDataSearch(self, collection, s_date1, s_date2, cloud_cover):
        self.requestData['item_type'] = collection
        self.requestData['date1'], self.requestData['date2'] = s_date1, s_date2
        self.requestData['cloud_cover'] = cloud_cover

    def search(self):
        def closeTableAttribute():
            layer_id = self.catalog_id
            widgets = QApplication.instance().allWidgets()
            for tb in filter( lambda w: isinstance( w, QDialog ) and layer_id in w.objectName(),  widgets ):
                tb.close()

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

        if self.mapCanvas.layerCount() == 0:
            msg = 'Need layer(s) in map'
            self.message.emit( Qgis.Critical, msg )
            return

        existsCatalog = not self.catalog is None and not self.project.mapLayer( self.catalog_id ) is None
        if not existsCatalog:
            self._create()            
        else:
            self.catalog.dataProvider().truncate() # Delete all features
            closeTableAttribute()
        
        self._populate( existsCatalog )


# cc = CatalogCbers4a( iface )
# cc.init()

# collection, s_date1, s_date2, cloud_cover = 'CBERS4A_WPM_L4_DN', '2019-06-09', '2020-11-03', 20
# cc.setDataSearch( collection, s_date1, s_date2, cloud_cover )
# #cc.search()


# def copy2clipboard(d_json):
#     clipboard = QApplication.clipboard()
#     clipboard.setText( json.dumps( d_json ) )

# def saveResult(filepath, result):
#     with open( filepath, 'w') as f:
#         f.write( json.dumps( result['json'] ) )


# Data
# crsCatalog = QgsCoordinateReferenceSystem('EPSG:4326')
# e = getExtentMapcanvas( crsCatalog )
# bbox = [ e.xMinimum(), e.yMinimum(), e.xMaximum(), e.yMaximum() ]
# args = {
#     'bbox': bbox,
#     'collection': 'CBERS4A_WPM_L4_DN',
#     's_datetime1': '2019-06-09T00:00:00',
#     's_datetime2': '2020-11-03T23:59:00',
#     'cloud_cover': 20,
#     'limit': 1000000
# }
# data = getData( **args )
# #
# req = getRequestCbers4()
# result = searchPost( req, data )

# if not result['isOk']:
#     print( result['message'] )
# else:
#     filepath = '/home/lmotta/work/response.json'
#     saveResult( filepath, result )

# copy2clipboard( result['json'] )
