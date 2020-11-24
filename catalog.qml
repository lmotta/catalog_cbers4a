<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis styleCategories="LayerConfiguration|Symbology|Symbology3D|Labeling|Fields|Forms|Actions|MapTips|Diagrams|AttributeTable|Rendering|GeometryOptions|Relations|Temporal|Legend" maxScale="0" minScale="100000000" simplifyLocal="1" simplifyMaxScale="1" simplifyDrawingHints="1" labelsEnabled="0" hasScaleBasedVisibilityFlag="0" version="3.16.0-Hannover" simplifyAlgorithm="0" readOnly="0" simplifyDrawingTol="1">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
  </flags>
  <temporal endExpression="" durationField="" mode="0" fixedDuration="0" startField="" startExpression="" accumulate="0" enabled="0" durationUnit="min" endField="">
    <fixedRange>
      <start></start>
      <end></end>
    </fixedRange>
  </temporal>
  <renderer-v2 forceraster="0" enableorderby="0" type="singleSymbol" symbollevels="0">
    <symbols>
      <symbol clip_to_extent="1" name="0" type="fill" force_rhr="0" alpha="0.344">
        <layer class="SimpleFill" pass="0" locked="0" enabled="1">
          <prop v="3x:0,0,0,0,0,0" k="border_width_map_unit_scale"/>
          <prop v="60,175,213,255" k="color"/>
          <prop v="bevel" k="joinstyle"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="35,35,35,255" k="outline_color"/>
          <prop v="solid" k="outline_style"/>
          <prop v="0.26" k="outline_width"/>
          <prop v="MM" k="outline_width_unit"/>
          <prop v="solid" k="style"/>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" value="" type="QString"/>
              <Option name="properties"/>
              <Option name="type" value="collection" type="QString"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
    </symbols>
    <rotation/>
    <sizescale/>
  </renderer-v2>
  <blendMode>0</blendMode>
  <featureBlendMode>0</featureBlendMode>
  <layerOpacity>1</layerOpacity>
  <SingleCategoryDiagramRenderer diagramType="Histogram" attributeLegend="1">
    <DiagramCategory rotationOffset="270" spacing="0" barWidth="5" lineSizeScale="3x:0,0,0,0,0,0" lineSizeType="MM" spacingUnit="MM" scaleBasedVisibility="0" sizeType="MM" penAlpha="255" spacingUnitScale="3x:0,0,0,0,0,0" width="15" sizeScale="3x:0,0,0,0,0,0" diagramOrientation="Up" scaleDependency="Area" opacity="1" minimumSize="0" maxScaleDenominator="1e+08" height="15" penColor="#000000" penWidth="0" backgroundColor="#ffffff" minScaleDenominator="0" backgroundAlpha="255" labelPlacementMethod="XHeight" direction="1" showAxis="0" enabled="0">
      <fontProperties description="Noto Sans,10,-1,0,50,0,0,0,0,0,Regular" style="Regular"/>
      <attribute field="" color="#000000" label=""/>
      <axisSymbol>
        <symbol clip_to_extent="1" name="" type="line" force_rhr="0" alpha="1">
          <layer class="SimpleLine" pass="0" locked="0" enabled="1">
            <prop v="0" k="align_dash_pattern"/>
            <prop v="square" k="capstyle"/>
            <prop v="5;2" k="customdash"/>
            <prop v="3x:0,0,0,0,0,0" k="customdash_map_unit_scale"/>
            <prop v="MM" k="customdash_unit"/>
            <prop v="0" k="dash_pattern_offset"/>
            <prop v="3x:0,0,0,0,0,0" k="dash_pattern_offset_map_unit_scale"/>
            <prop v="MM" k="dash_pattern_offset_unit"/>
            <prop v="0" k="draw_inside_polygon"/>
            <prop v="bevel" k="joinstyle"/>
            <prop v="35,35,35,255" k="line_color"/>
            <prop v="solid" k="line_style"/>
            <prop v="0.26" k="line_width"/>
            <prop v="MM" k="line_width_unit"/>
            <prop v="0" k="offset"/>
            <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
            <prop v="MM" k="offset_unit"/>
            <prop v="0" k="ring_filter"/>
            <prop v="0" k="tweak_dash_pattern_on_corners"/>
            <prop v="0" k="use_custom_dash"/>
            <prop v="3x:0,0,0,0,0,0" k="width_map_unit_scale"/>
            <data_defined_properties>
              <Option type="Map">
                <Option name="name" value="" type="QString"/>
                <Option name="properties"/>
                <Option name="type" value="collection" type="QString"/>
              </Option>
            </data_defined_properties>
          </layer>
        </symbol>
      </axisSymbol>
    </DiagramCategory>
  </SingleCategoryDiagramRenderer>
  <DiagramLayerSettings linePlacementFlags="18" zIndex="0" placement="1" obstacle="0" showAll="1" priority="0" dist="0">
    <properties>
      <Option type="Map">
        <Option name="name" value="" type="QString"/>
        <Option name="properties"/>
        <Option name="type" value="collection" type="QString"/>
      </Option>
    </properties>
  </DiagramLayerSettings>
  <geometryOptions removeDuplicateNodes="0" geometryPrecision="0">
    <activeChecks/>
    <checkConfiguration type="Map">
      <Option name="QgsGeometryGapCheck" type="Map">
        <Option name="allowedGapsBuffer" value="0" type="double"/>
        <Option name="allowedGapsEnabled" value="false" type="bool"/>
        <Option name="allowedGapsLayer" value="" type="QString"/>
      </Option>
    </checkConfiguration>
  </geometryOptions>
  <legend type="default-vector"/>
  <referencedLayers/>
  <fieldConfiguration>
    <field name="item_id" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option name="IsMultiline" value="false" type="bool"/>
            <Option name="UseHtml" value="false" type="bool"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="date_time" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="meta_json" configurationFlags="None">
      <editWidget type="Hidden">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="meta_jsize" configurationFlags="None">
      <editWidget type="Hidden">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
  </fieldConfiguration>
  <aliases>
    <alias name="" index="0" field="item_id"/>
    <alias name="" index="1" field="date_time"/>
    <alias name="" index="2" field="meta_json"/>
    <alias name="" index="3" field="meta_jsize"/>
  </aliases>
  <defaults>
    <default expression="" applyOnUpdate="0" field="item_id"/>
    <default expression="" applyOnUpdate="0" field="date_time"/>
    <default expression="" applyOnUpdate="0" field="meta_json"/>
    <default expression="" applyOnUpdate="0" field="meta_jsize"/>
  </defaults>
  <constraints>
    <constraint constraints="0" exp_strength="0" field="item_id" notnull_strength="0" unique_strength="0"/>
    <constraint constraints="0" exp_strength="0" field="date_time" notnull_strength="0" unique_strength="0"/>
    <constraint constraints="0" exp_strength="0" field="meta_json" notnull_strength="0" unique_strength="0"/>
    <constraint constraints="0" exp_strength="0" field="meta_jsize" notnull_strength="0" unique_strength="0"/>
  </constraints>
  <constraintExpressions>
    <constraint exp="" desc="" field="item_id"/>
    <constraint exp="" desc="" field="date_time"/>
    <constraint exp="" desc="" field="meta_json"/>
    <constraint exp="" desc="" field="meta_jsize"/>
  </constraintExpressions>
  <expressionfields/>
  <attributeactions>
    <defaultAction value="{00000000-0000-0000-0000-000000000000}" key="Canvas"/>
    <actionsetting capture="0" name="Add XYZ tiles" shortTitle="Add XYZ tiles" icon="" action="from qgis import utils as QgsUtils&#xa;&#xa;# Plugin:&#xa;# . __init__.py: Catalog.dock&#xa;# . catalog.py: DockWidget.catalog&#xa;&#xa;def getFunctionActionsForm(pluginName):&#xa;    &quot;&quot;&quot;&#xa;    Function from Plugin for actions Form&#xa;&#xa;    :param pluginName: Name of plugin&#xa;    &quot;&quot;&quot;&#xa;    getInstanceInPlugin = lambda plugin: plugin.dock # _init_.py: initGui()&#xa;    getActionsForm = lambda plugin: plugin.dock.catalog.actionsForm # class_instance.py: _init_()&#xa;    plugins = {}&#xa;    for name, obj in QgsUtils.plugins.items():&#xa;        plugins[ name ] = obj&#xa;    if not pluginName in plugins:&#xa;        return { 'isOk': False, 'message': &quot;Missing {name} Plugin.&quot;.format(name=pluginName) }&#xa;    if getInstanceInPlugin( plugins[ pluginName ] ) is None:&#xa;        return { 'isOk': False, 'message': &quot;Run the {name} Plugin.&quot;.format(name=pluginName) }&#xa;    return { 'isOk': True, 'function': getActionsForm( plugins[ pluginName ] ) }&#xa;&#xa;namePlugin = 'catalog_cbers4a'&#xa;title = 'Action Cbers4a'&#xa;nameAction = 'addxyztiles'&#xa;msgBar =  QgsUtils.iface.messageBar()&#xa;r = getFunctionActionsForm( namePlugin )&#xa;if r['isOk']:&#xa;    actionsForm = r['function']&#xa;    r = actionsForm( nameAction, [% $id %] )&#xa;    if not r['isOk']:&#xa;        msgBar.pushCritical( title, r['message'] )&#xa;else:&#xa;    msgBar.pushCritical( title, r['message'] )&#xa;" type="1" id="{84938174-b775-4c64-9576-006ce9a69c82}" notificationMessage="" isEnabledOnlyWhenEditable="0">
      <actionScope id="Layer"/>
    </actionsetting>
    <actionsetting capture="0" name="Downloads images" shortTitle="Downloads images" icon="" action="from qgis import utils as QgsUtils&#xa;&#xa;# Plugin:&#xa;# . __init__.py: Catalog.dock&#xa;# . catalog.py: DockWidget.catalog&#xa;&#xa;def getFunctionActionsForm(pluginName):&#xa;    &quot;&quot;&quot;&#xa;    Function from Plugin for actions Form&#xa;&#xa;    :param pluginName: Name of plugin&#xa;    &quot;&quot;&quot;&#xa;    getInstanceInPlugin = lambda plugin: plugin.dock # _init_.py: initGui()&#xa;    getActionsForm = lambda plugin: plugin.dock.catalog.actionsForm # class_instance.py: _init_()&#xa;    plugins = {}&#xa;    for name, obj in QgsUtils.plugins.items():&#xa;        plugins[ name ] = obj&#xa;    if not pluginName in plugins:&#xa;        return { 'isOk': False, 'message': &quot;Missing {name} Plugin.&quot;.format(name=pluginName) }&#xa;    if getInstanceInPlugin( plugins[ pluginName ] ) is None:&#xa;        return { 'isOk': False, 'message': &quot;Run the {name} Plugin.&quot;.format(name=pluginName) }&#xa;    return { 'isOk': True, 'function': getActionsForm( plugins[ pluginName ] ) }&#xa;&#xa;namePlugin = 'catalog_cbers4a'&#xa;title = 'Action Cbers4a'&#xa;nameAction = 'downloadImages'&#xa;msgBar =  QgsUtils.iface.messageBar()&#xa;r = getFunctionActionsForm( namePlugin )&#xa;if r['isOk']:&#xa;    actionsForm = r['function']&#xa;    r = actionsForm( nameAction, [% $id %] )&#xa;    if not r['isOk']:&#xa;        msgBar.pushCritical( title, r['message'] )&#xa;else:&#xa;    msgBar.pushCritical( title, r['message'] )&#xa;" type="1" id="{5585aa1f-b459-40ed-aae5-b31f14d2357a}" notificationMessage="" isEnabledOnlyWhenEditable="0">
      <actionScope id="Layer"/>
    </actionsetting>
  </attributeactions>
  <attributetableconfig sortOrder="1" sortExpression="&quot;date&quot;" actionWidgetStyle="dropDown">
    <columns>
      <column width="-1" name="item_id" hidden="0" type="field"/>
      <column width="-1" name="meta_json" hidden="0" type="field"/>
      <column width="-1" name="meta_jsize" hidden="0" type="field"/>
      <column width="-1" hidden="1" type="actions"/>
      <column width="-1" name="date_time" hidden="0" type="field"/>
    </columns>
  </attributetableconfig>
  <conditionalstyles>
    <rowstyles/>
    <fieldstyles/>
  </conditionalstyles>
  <storedexpressions/>
  <editform tolerant="1">/home/lmotta/.local/share/QGIS/QGIS3/profiles/default/python/plugins/catalog_cbers4a/form.ui</editform>
  <editforminit>loadForm</editforminit>
  <editforminitcodesource>1</editforminitcodesource>
  <editforminitfilepath>/home/lmotta/.local/share/QGIS/QGIS3/profiles/default/python/plugins/catalog_cbers4a/form.py</editforminitfilepath>
  <editforminitcode><![CDATA[# -*- código: utf-8 -*-
"""
Formas QGIS podem ter uma função Python que é chamada quando o formulário é
aberto.

Use esta função para adicionar lógica extra para seus formulários.

Digite o nome da função na "função Python Init"
campo.
Um exemplo a seguir:
"""
de qgis.PyQt.QtWidgets importar QWidget

def my_form_open(diálogo, camada, feição):
	geom = feature.geometry()
	control = dialog.findChild(QWidget, "MyLineEdit")
]]></editforminitcode>
  <featformsuppress>0</featformsuppress>
  <editorlayout>uifilelayout</editorlayout>
  <editable/>
  <labelOnTop/>
  <dataDefinedFieldProperties/>
  <widgets/>
  <previewExpression>"item_id"</previewExpression>
  <mapTip></mapTip>
  <layerGeometryType>2</layerGeometryType>
</qgis>
