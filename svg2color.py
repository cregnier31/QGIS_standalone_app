# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SVG2ColoR
                                 A QGIS plugin
 Generates color-ramp styles from SVG files.  It also compatible with CPT-CITY styles.
 SVG2ColoR improves your color-ramp library, by the way your maps look better.
                              -------------------
        begin                : 2014-10-17
		version				 : 0.9
        copyright            : (C) 2014 by Mehmet Selim BILGIN
        email                : mselimbilgin@yahoo.com
		web					 : http://cbsuygulama.wordpress.com/svg2color
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
from xml.dom import minidom
import codecs
import os

##def loadFromFile(self):
##	##File browsing.
##	browseDlg = QFileDialog.getOpenFileName(self.dlg, 'Choose SVG File...', self.dlg.lineEdit.text(), 'SVG file (*.svg)')
##	if browseDlg:
##		self.dlg.lineEdit.setText(browseDlg)
##		try:
##			with codecs.open(browseDlg, encoding='utf-8', mode='r') as readFile:
##				self.isLinearGrad(readFile.read())
##		except Exception as readError:
##			QMessageBox.critical(None, "Information", ("An error has occured: " + str(readError)))
##			
##def isLinearGrad(self, svgDocument):
##	##Checking SVG document for XML syntax.
##	try:
##		svgDoc = minidom.parseString(svgDocument)
##		self.firstNode = svgDoc.getElementsByTagName('linearGradient')
##		#Checking SVG document for containing linearGradient tag.
##		if len(self.firstNode) == 0:
##			QMessageBox.critical(None, "Information", 'The SVG file does not contain <b>linearGradient</b> tag. Please choose a proper SVG document. You can find lots of samples in <a href="http://soliton.vm.bytemark.co.uk/pub/cpt-city/">CPT-CITY webpage</a>')
##			self.graphicRenderer(open(os.path.dirname(os.path.realpath(__file__)) + os.sep + 'error.svg', 'r').read())
##		else:				
##			try:
##				self.colorList = list()
##				for i in self.firstNode[0].getElementsByTagName('stop'):
##					#Some SVG files contain hex values for defining colors. It must be converted to values. This issue is handled in here.
##					if i.attributes['stop-color'].value[0] == '#':
##						self.colorList.append([self.hexToRgb(i.attributes['stop-color'].value), float(i.attributes['offset'].value[:-1])/100])
##					else:
##						self.colorList.append([i.attributes['stop-color'].value[4:-1], float(i.attributes['offset'].value[:-1])/100])
##				self.sampleSvg(self.firstNode[0])
##				
##			except Exception as linearGradError:
##				QMessageBox.critical(None, "Information", 'Cannot read the color values. Please choose a proper SVG document. You can find lots of samples in <a href="http://soliton.vm.bytemark.co.uk/pub/cpt-city/">CPT-CITY webpage</a>')
##				self.graphicRenderer(open(os.path.dirname(os.path.realpath(__file__)) + os.sep + 'error.svg', 'r').read())
##def hexToRgb(self, hexademical): #Thanks for dan_waterworth from http://stackoverflow.com/questions/4296249/how-do-i-convert-a-hex-triplet-to-an-rgb-tuple-and-back
##	num = str(hexademical[1:])
##	#Sometimes hex codes can be shortand (3 digits). Here is the solution...
##	if len(num) == 3:
##		num = num[:1]*2 + num[1:2]*2 + num[2:3]*2
##	
##	return (str(int(num[:2], 16)) + ',' + str(int(num[2:4], 16)) + ',' + str(int(num[4:6], 16)))
##
##def sampleSvg(self, linearGradientTag):
##	#Loading sample SVG documents for visualisation.
##	sampleSVG = minidom.Document()
##	svgBase = sampleSVG.createElement('svg')
##	svgBase.setAttribute('xmlns', 'http://www.w3.org/2000/svg')
##	svgBase.setAttribute('version', '1.1')
##	svgBase.setAttribute('width', '600px')
##	svgBase.setAttribute('height', '110px')
##	sampleSVG.appendChild(svgBase)
##	
##	defs = sampleSVG.createElement('defs')
##	svgBase.appendChild(defs)		
##	defs.appendChild(linearGradientTag)
##	
##	rectangle = sampleSVG.createElement('rect')
##	rectangle.setAttribute('x', '1')
##	rectangle.setAttribute('y', '1')
##	rectangle.setAttribute('width', '493')
##	rectangle.setAttribute('height', '93')
##	rectangle.setAttribute('stroke-width', '1')
##	rectangle.setAttribute('stroke', 'black')
##	rectangle.setAttribute('fill', 'url(#' + linearGradientTag.attributes['id'].value + ')')
##	svgBase.appendChild(rectangle)
##	self.graphicRenderer(sampleSVG.toprettyxml(indent="    ", encoding="utf-8"))
##	
##def graphicRenderer(self, svgInput):
##	#Graphics rendering.
##	scene = QGraphicsScene()
##	self.dlg.graphicsView.setScene(scene)
##	webview = QGraphicsWebView()
##	webview.setContent(svgInput, 'image/svg+xml')
##	scene.addItem(webview)		
##	
