# -*- coding: utf-8 -*-

#
#  nanohdrviewer : A simple HDR image viewer
#
#  Copyright (C) 2014 Hisanari Otsu
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import os
import array
import numpy as np
import cv2
from PyQt5.QtCore import QDir, Qt, pyqtSignal, QMimeData, QFileSystemWatcher
from PyQt5.QtGui import QImage, QPixmap, QPalette
from PyQt5.QtWidgets import (
	QWidget, QApplication, QMainWindow, QAction, QLabel, QMenu,
	QFileDialog, QMessageBox, QSizePolicy, QScrollArea, QVBoxLayout)


class ImageLabel(QLabel):

	sizeChanged = pyqtSignal(int, int)

	def __init__(self, parent=None):
		super(ImageLabel, self).__init__(parent)
		self.setBackgroundRole(QPalette.Base)
		self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
		self.setScaledContents(True)
		self.setAcceptDrops(True)
		self.setAlignment(Qt.AlignCenter)

	def dragEnterEvent(self, event):
		self.setBackgroundRole(QPalette.Highlight)
		event.acceptProposedAction()

	def dragMoveEvent(self, event):
		event.acceptProposedAction()

	def dropEvent(self, event):
		# Get path of dropped file
		mimeData = event.mimeData()
		if mimeData.hasUrls():
			filename = mimeData.urls()[0].toLocalFile()
			self.load(filename)
		event.acceptProposedAction()

	def dragLeaveEvent(self, event):
		self.clear()
		event.accept()

	def load(self, filename):
		# Load HDR image with FreeImage
		image = self.loadHDRImage(filename)
		if image is None:
			return False

		# Change window size
		self.sizeChanged.emit(image.width(), image.height())

		# Set the image to imageLabel
		self.setPixmap(QPixmap.fromImage(image))
		self.adjustSize()

		# Begin to watch modification
		self.watcher = QFileSystemWatcher()
		self.watcher.addPath(filename)
		self.watcher.fileChanged.connect(self.onFileChanged)

		return True

	def loadHDRImage(self, filename):
		# Load image
		img = cv2.imread(filename)
		if img is None:
			return None
		
		# HDR compression
		imageArray_RGB8 = (np.clip(np.power(img, 1/2.2), 0, 1) * 255).astype(np.uint8)

		# Convert to QImage
		return QImage(imageArray_RGB8.tostring(), img.shape[1], img.shape[0], QImage.Format_RGB888)

	def onFileChanged(self, path):
		if os.path.isfile(path):
			self.load(path)
		else:
			self.clear()
			self.sizeChanged.emit(200, 200)

class HDRImageViewer(QMainWindow):
	def __init__(self, parent=None):
		super(HDRImageViewer, self).__init__(parent)

		# Label for image
		self.imageLabel = ImageLabel()
		self.imageLabel.sizeChanged.connect(self.setFixedSize)

		# Layout
		mainLayout = QVBoxLayout()
		mainLayout.setContentsMargins(0, 0, 0, 0)
		mainLayout.addWidget(self.imageLabel)
		mainWidget = QWidget()
		mainWidget.setLayout(mainLayout)
		self.setCentralWidget(mainWidget)

		# Create actions
		self.openAction = QAction("&Open...", self, shortcut="Ctrl+O", triggered=self.open)
		self.exitAction = QAction("E&xit", self, triggered=self.close)

		# Create menus
		self.fileMenu = QMenu("&File", self)
		self.fileMenu.addAction(self.openAction)
		self.fileMenu.addSeparator()
		self.fileMenu.addAction(self.exitAction)
		self.menuBar().addMenu(self.fileMenu)

		# Title and initial window size
		self.setWindowTitle("hdrviewer")
		self.setFixedSize(200, 200)
		self.setWindowFlags(Qt.WindowStaysOnTopHint)

	def open(self):
		filename, _ = QFileDialog.getOpenFileName(self, "Open File", QDir.currentPath(), "HDR Image (*.hdr, *.exr)")
		if filename:
			if not self.imageLabel.load(filename):
				QMessageBox.information(self, "hdrviewer", "Failed to load %s" % filename)

if __name__ == '__main__':
	import sys
	app = QApplication(sys.argv)
	viewer = HDRImageViewer()
	viewer.show()
	sys.exit(app.exec_())
