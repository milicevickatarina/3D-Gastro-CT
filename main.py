# -*- coding: utf-8 -*-
"""
Created on Sun May 23 11:29:58 2021

@author: Katarina Milicevic, School of Electrical Engineering
"""
from PyQt5 import QtCore, QtGui, QtWidgets

import os
import numpy as np
import SimpleITK as sitk
import matplotlib
matplotlib.use('QT5Agg')
import matplotlib.pylab as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from index_tracker import IndexTracker
import rendering


class MplCanvas(FigureCanvasQTAgg):
            def __init__(self, parent=None, width=5, height=4, dpi=100):
                self.fig = Figure(figsize=(width, height), dpi=dpi)
                self.axes = self.fig.add_subplot(111)
                super(MplCanvas, self).__init__(self.fig) 
                
def popup_message(self, text, inf = ""):
    msg = QtWidgets.QMessageBox()
    msg.setWindowTitle("Error")
    if inf!="":
        msg.setInformativeText(inf)
    msg.setText(text)
    msg.setIcon(QtWidgets.QMessageBox.Critical)
    x = msg.exec_()
                
# Window for selection of series and their preprocessing
class preprocWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Data Preprocessing")
        self.setFixedSize(400, 300)
        # self.resize(400, 300)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("./pictures/organs.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)
        
        lbl = QtWidgets.QLabel("Choose directory of portal vein phase CT series:", self)
        lbl.resize(400,30)
        lbl.move(30,40)
        btn = QtWidgets.QPushButton("Browse...", self)       
        btn.resize(120,30)
        btn.move(80,70)
        btn.clicked.connect(self.preproc)
        
        lbl2 = QtWidgets.QLabel("Choose directory of native phase CT series:", self)
        lbl2.resize(400,30)
        lbl2.move(30,130)                
        btn2 = QtWidgets.QPushButton("Browse...", self)
        btn2.resize(120,30)
        btn2.move(80,160)
        btn2.clicked.connect(self.preproc2)
        
        self.pushButton_close = QtWidgets.QPushButton('Close', self)
        self.pushButton_close.move(275, 235)
        self.pushButton_close.clicked.connect(self.close_preprocWindow)
        
        self.statusBar = QtWidgets.QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage('Choose appropriate abdominal CT series.')
        
        self.show()
        
    def preproc(self):
        import data_preprocessing
        fileDir = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Portal Vein Phase Directory")
        
        if fileDir!="":
            self.statusBar.showMessage('Processing has started. Please wait...')
        img_array, flag = data_preprocessing.main(fileDir, work_dir)
        
        if flag:
            self.statusBar.showMessage('Processing is done. First series is now ready for segmentation.')
            # Show resulting series
            fig, ax = plt.subplots(1, 1)
            fig.canvas.set_window_title('Series display')
            X_tran = np.transpose(img_array, (1,2,0))
            color_map='gray'
            title = 'Axial slices of preprocessed portal vein phase'
            self.tracker = IndexTracker(ax, X_tran, color_map, title)
            fig.canvas.mpl_connect('scroll_event', self.tracker.onscroll)
            plt.show() 
        else:
            popup_message(self, "Chosen directory is not appropriate!")
            self.statusBar.showMessage('Choose appropriate abdominal CT series.')

    def preproc2(self):

        if os.path.exists(work_dir + "/data/portal_vein_phase_preprocessed.mha"):
            import data_preprocessing2
            fileDir2 = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Native Phase Directory")
    
            if fileDir2!="":
                self.statusBar.showMessage('Processing has started. Please wait...')
            img_array, flag = data_preprocessing2.main(fileDir2, work_dir)
            
            if flag:
                self.statusBar.showMessage('Processing is done. Second series is now ready for segmentation.')
                # Show resulting series
                fig, ax = plt.subplots(1, 1)
                fig.canvas.set_window_title('Series display')
                X_tran = np.transpose(img_array, (1,2,0))
                color_map='gray'
                title = 'Axial slices of preprocessed native phase'
                self.tracker = IndexTracker(ax, X_tran, color_map, title)
                fig.canvas.mpl_connect('scroll_event', self.tracker.onscroll)
                plt.show() 
            else:
                popup_message(self, "Chosen directory is not appropriate!")
                self.statusBar.showMessage('Choose appropriate abdominal CT series.')
        else:
            popup_message(self, "Choose portal vein phase first!")
        
        
    def close_preprocWindow(self):
        self.close()
        
    def closeEvent(self, event):
        if os.path.exists(work_dir + "/data/portal_vein_phase_preprocessed.mha") & os.path.exists(work_dir + "/data/native_phase_preprocessed.mha"):
            MainWindow.statusBar().showMessage('You can now proceed to Segmentation.')
        else:
            MainWindow.statusBar().showMessage('Before Segmentation, you have to finish Data Processing.')
                
class heartSegmTab(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(heartSegmTab, self).__init__(parent)
        # self.lbl = QtWidgets.QLabel(self)
        # self.lbl.setText("Choose heart bounds on first slice and check if segmentation works properly. Then, choose heart\nborders "
        #                  "in whole volume, including last slice that contain heart (take first or second slice beneath).")
        # self.lbl.move(50, 40)
        
        self.lbl_xl = QtWidgets.QLabel(self)
        self.lbl_xl.setText('left border (x-axis)')
        self.lbl_xl.move(150, 365)
        self.xl = QtWidgets.QLineEdit(self)
        self.xl.setMaxLength(3)
        self.xl.setFixedWidth(50)
        self.xl.setText("0")
        self.xl.move(150, 380)
        
        self.lbl_xr = QtWidgets.QLabel(self)
        self.lbl_xr.setText('right border (x-axis)')
        self.lbl_xr.move(810, 365)
        self.xr = QtWidgets.QLineEdit(self)
        self.xr.setMaxLength(3)
        self.xr.setFixedWidth(50)
        self.xr.setText("0")
        self.xr.move(810, 380)
        
        self.lbl_yt = QtWidgets.QLabel(self)
        self.lbl_yt.setText('upper border (y-axis)')
        self.lbl_yt.move(475, 85)
        self.yt = QtWidgets.QLineEdit(self)
        self.yt.setMaxLength(3)
        self.yt.setFixedWidth(50)
        self.yt.setText("0")
        self.yt.move(475, 100)
        
        self.lbl_yb = QtWidgets.QLabel(self)
        self.lbl_yb.setText('lower border (y-axis)')
        self.lbl_yb.move(475, 645)
        self.yb = QtWidgets.QLineEdit(self)
        self.yb.setMaxLength(3)
        self.yb.setFixedWidth(50)
        self.yb.setText("0")
        self.yb.move(475, 660)
        
        self.lbl_bl = QtWidgets.QLabel(self)
        self.lbl_bl.setText('left border (x-axis)')
        self.lbl_bl.move(1000, 365)
        self.bl = QtWidgets.QLineEdit(self)
        self.bl.setMaxLength(3)
        self.bl.setFixedWidth(50)
        self.bl.setText("0")
        self.bl.move(1000, 380)
        
        self.lbl_br = QtWidgets.QLabel(self)
        self.lbl_br.setText('right border (x-axis)')
        self.lbl_br.move(1660, 365)
        self.br = QtWidgets.QLineEdit(self)
        self.br.setMaxLength(3)
        self.br.setFixedWidth(50)
        self.br.setText("0")
        self.br.move(1660, 380)
        
        self.lbl_bt = QtWidgets.QLabel(self)
        self.lbl_bt.setText('upper border (y-axis)')
        self.lbl_bt.move(1325, 85)
        self.bt = QtWidgets.QLineEdit(self)
        self.bt.setMaxLength(3)
        self.bt.setFixedWidth(50)
        self.bt.setText("0")
        self.bt.move(1325, 100)
        
        self.lbl_bb = QtWidgets.QLabel(self)
        self.lbl_bb.setText('lower border (y-axis)')
        self.lbl_bb.move(1325, 645)
        self.bb = QtWidgets.QLineEdit(self)
        self.bb.setMaxLength(3)
        self.bb.setFixedWidth(50)
        self.bb.setText("0")
        self.bb.move(1325, 660)
        
        self.lbl_bz = QtWidgets.QLabel(self)
        self.lbl_bz.setText('bottom slice number')
        self.lbl_bz.move(1660, 565)
        self.bz = QtWidgets.QLineEdit(self)
        self.bz.setMaxLength(3)
        self.bz.setFixedWidth(50)
        self.bz.setText("0")
        self.bz.move(1660, 580)
        
        # First slice picture
        img = sitk.ReadImage(work_dir + "/data/portal_vein_phase_preprocessed.mha")
        first_slice = img[:,:,0]
        sc = MplCanvas(self, width=5, height=4, dpi=100)
        sc.axes.imshow(sitk.GetArrayViewFromImage(first_slice), cmap='gray')
        sc.axes.set(xlabel='', ylabel='',
                title='First slice (choosing heart bounds)')
        toolbar = NavigationToolbar(sc, self)
        self.fixwidget = QtWidgets.QWidget(self)
        self.layout  = QtWidgets.QGridLayout()
        self.layout.addWidget(toolbar, 0, 0)
        self.layout.addWidget(sc)
        self.fixwidget.setLayout(self.layout) 
        height = self.fixwidget.sizeHint().height()
        width = self.fixwidget.sizeHint().width()
        xpos, ypos = 250, 150
        self.fixwidget.setGeometry(QtCore.QRect(xpos, ypos, width, height)) 
        
        # Whole series representation
        sc2 = MplCanvas(self, width=5, height=4, dpi=100)
        img_array = sitk.GetArrayFromImage(img)
        X_tran = np.transpose(img_array, (1,2,0))
        color_map='gray'
        title = 'Axial slices' #'Slices (choosing tridimensional heart region bounds)'
        self.tracker = IndexTracker(sc2.axes, X_tran, color_map, title)
        sc2.fig.canvas.mpl_connect('scroll_event', self.tracker.onscroll)
        toolbar2 = NavigationToolbar(sc2, self)
        self.fixwidget2 = QtWidgets.QWidget(self)
        self.layout2  = QtWidgets.QGridLayout()
        self.layout2.addWidget(toolbar2, 0, 0)
        self.layout2.addWidget(sc2) 
        self.fixwidget2.setLayout(self.layout2) 
        height2 = self.fixwidget2.sizeHint().height()
        width2 = self.fixwidget2.sizeHint().width()
        xpos2, ypos2 = 1100, 150
        self.fixwidget2.setGeometry(QtCore.QRect(xpos2, ypos2, width2, height2)) 
        
        self.pushButton_firstSliceSegm = QtWidgets.QPushButton("Check first slice segmentation", self)
        self.pushButton_firstSliceSegm.resize(200, 40)
        self.pushButton_firstSliceSegm.move(450, 850)
        
        self.pushButton_heartBox = QtWidgets.QPushButton("Check borders", self)
        self.pushButton_heartBox.resize(120, 30)
        self.pushButton_heartBox.move(1660, 660)
        
        self.pushButton_segm = QtWidgets.QPushButton("Segmentation...", self)
        self.pushButton_segm.resize(200, 40)
        self.pushButton_segm.move(1300, 850)
        
        self.pushButton_next = QtWidgets.QPushButton("next (Segmentation of bones)", self)
        self.pushButton_next.resize(210, 40)
        self.pushButton_next.move(1700, 950) #(1710, 955)
        

class bonesSegmTab(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(bonesSegmTab, self).__init__(parent)
        self.lbl = QtWidgets.QLabel(self)
        self.lbl.setText("For lower threshold choose value at the end of last (most right) peak\nand for upper choose some value close to 256 (e.g. 250).")
        self.lbl.move(50, 50)
        
        # Lower threshold
        self.lbl_lt = QtWidgets.QLabel(self)
        self.lbl_lt.setText('lower threshold')
        self.lbl_lt.move(300, 285)
        self.lt = QtWidgets.QLineEdit(self)
        self.lt.setMaxLength(3)
        self.lt.setFixedWidth(50)
        self.lt.setText("0")
        self.lt.move(300, 300)
        
        # Upper threshold
        self.lbl_ut = QtWidgets.QLabel(self)
        self.lbl_ut.setText('upper threshold')
        self.lbl_ut.move(1300, 285)
        self.ut = QtWidgets.QLineEdit(self)
        self.ut.setMaxLength(3)
        self.ut.setFixedWidth(50)
        self.ut.setText("250")
        self.ut.move(1300, 300)
        
        # Histogram picture       
        import bones_segm
        sc = MplCanvas(self, width=5, height=4, dpi=100)
        hist = bones_segm.show_hist(work_dir)
        sc.axes.plot(hist)
        sc.axes.set(xlabel='', ylabel='',
                title='Whole volume histogram (native phase)')
        toolbar = NavigationToolbar(sc, self)
        self.fixwidget = QtWidgets.QWidget(self)
        self.layout  = QtWidgets.QGridLayout()
        self.layout.addWidget(toolbar, 0, 0)
        self.layout.addWidget(sc)
        self.fixwidget.setLayout(self.layout)  
        height = self.fixwidget.sizeHint().height()
        width = self.fixwidget.sizeHint().width()
        xpos, ypos = 600, 100
        self.fixwidget.setGeometry(QtCore.QRect(xpos, ypos, width, height))
        
        self.pushButton_segm = QtWidgets.QPushButton("Segmentation...", self)
        self.pushButton_segm.resize(200, 40)
        self.pushButton_segm.move(775, 750)
        
        self.pushButton_next = QtWidgets.QPushButton('next (Segmentation of liver and spleen)', self)
        self.pushButton_next.resize(210, 40)
        self.pushButton_next.move(1700, 950)

class liverSegmTab(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(liverSegmTab, self).__init__(parent)
        self.lbl = QtWidgets.QLabel(self)
        self.lbl.setText("For thresholds choose values which precisely surround last peak.")
        self.lbl.move(50, 50)
        
        # Lower threshold
        self.lbl_lt = QtWidgets.QLabel(self)
        self.lbl_lt.setText('lower threshold')
        self.lbl_lt.move(300, 285)
        self.lt = QtWidgets.QLineEdit(self)
        self.lt.setMaxLength(3)
        self.lt.setFixedWidth(50)
        self.lt.setText("0")
        self.lt.move(300, 300)
        
        # Upper threshold
        self.lbl_ut = QtWidgets.QLabel(self)
        self.lbl_ut.setText('upper threshold')
        self.lbl_ut.move(1300, 285)
        self.ut = QtWidgets.QLineEdit(self)
        self.ut.setMaxLength(3)
        self.ut.setFixedWidth(50)
        self.ut.setText("0")
        self.ut.move(1300, 300)
        
        # Histogram picture
        import liver_segm
        sc = MplCanvas(self, width=5, height=4, dpi=100)

        hist = liver_segm.show_hist(work_dir)
        sc.axes.plot(hist)
        sc.axes.set(xlabel='', ylabel='',
                title='Whole volume histogram')
        toolbar = NavigationToolbar(sc, self)
        self.fixwidget = QtWidgets.QWidget(self)
        self.layout  = QtWidgets.QGridLayout()
        self.layout.addWidget(toolbar, 0, 0)
        self.layout.addWidget(sc)
        self.fixwidget.setLayout(self.layout) 
        height = self.fixwidget.sizeHint().height()
        width = self.fixwidget.sizeHint().width()
        xpos, ypos = 600, 100
        self.fixwidget.setGeometry(QtCore.QRect(xpos, ypos, width, height)) 
        
        self.pushButton_segm = QtWidgets.QPushButton("Segmentation...", self)
        self.pushButton_segm.resize(200, 40)
        self.pushButton_segm.move(775, 750)
        
        self.pushButton_next = QtWidgets.QPushButton('next (Segmentation of kidneys)', self)
        self.pushButton_next.resize(210, 40)
        self.pushButton_next.move(1700, 950)
        
class kidneysSegmTab(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(kidneysSegmTab, self).__init__(parent)
        # Right kidney (left on pictures)
        self.lbl = QtWidgets.QLabel(self)
        self.lbl.setText('Right kidney\n(left on pictures)')
        self.lbl.setFont(QtGui.QFont('Times New Roman', 12, weight=QtGui.QFont.Bold))
        self.lbl.move(70, 20)
        
        self.lbl_xl = QtWidgets.QLabel(self)
        self.lbl_xl.setText('left border (x-axis)')
        self.lbl_xl.move(135, 145)
        self.xl = QtWidgets.QLineEdit(self)
        self.xl.setMaxLength(3)
        self.xl.setFixedWidth(50)
        self.xl.setText("0")
        self.xl.move(135, 160)
        
        self.lbl_xr = QtWidgets.QLabel(self)
        self.lbl_xr.setText('right border (x-axis)')
        self.lbl_xr.move(365, 145)
        self.xr = QtWidgets.QLineEdit(self)
        self.xr.setMaxLength(3)
        self.xr.setFixedWidth(50)
        self.xr.setText("0")
        self.xr.move(365, 160)
        
        self.lbl_yt = QtWidgets.QLabel(self)
        self.lbl_yt.setText('upper border (y-axis)')
        self.lbl_yt.move(250, 45)
        self.yt = QtWidgets.QLineEdit(self)
        self.yt.setMaxLength(3)
        self.yt.setFixedWidth(50)
        self.yt.setText("0")
        self.yt.move(250, 60)
        
        self.lbl_yb = QtWidgets.QLabel(self)
        self.lbl_yb.setText('lower border (y-axis)')
        self.lbl_yb.move(250, 245)
        self.yb = QtWidgets.QLineEdit(self)
        self.yb.setMaxLength(3)
        self.yb.setFixedWidth(50)
        self.yb.setText("0")
        self.yb.move(250, 260)
        
        self.lbl_zt = QtWidgets.QLabel(self)
        self.lbl_zt.setText('top slice number')
        self.lbl_zt.move(480, 45)
        self.zt = QtWidgets.QLineEdit(self)
        self.zt.setMaxLength(3)
        self.zt.setFixedWidth(50)
        self.zt.setText("0")
        self.zt.move(480, 60)
        
        self.lbl_zb = QtWidgets.QLabel(self)
        self.lbl_zb.setText('bottom slice number')
        self.lbl_zb.move(480, 245)
        self.zb = QtWidgets.QLineEdit(self)
        self.zb.setMaxLength(3)
        self.zb.setFixedWidth(50)
        self.zb.setText("0")
        self.zb.move(480, 260)
        
        # Lower threshold
        self.lbl_lt = QtWidgets.QLabel(self)
        self.lbl_lt.setText('lower threshold')
        self.lbl_lt.move(60, 635)
        self.lt = QtWidgets.QLineEdit(self)
        self.lt.setMaxLength(3)
        self.lt.setFixedWidth(50)
        self.lt.setText("0")
        self.lt.move(60, 650)
        
        # Upper threshold
        self.lbl_ut = QtWidgets.QLabel(self)
        self.lbl_ut.setText('upper threshold')
        self.lbl_ut.move(710, 635)
        self.ut = QtWidgets.QLineEdit(self)
        self.ut.setMaxLength(3)
        self.ut.setFixedWidth(50)
        self.ut.setText("0")
        self.ut.move(710, 650)
        
        # Left kidney (right on pictures)
        self.lbl2 = QtWidgets.QLabel(self)
        self.lbl2.setText('Left kidney\n(right on pictures)')
        self.lbl2.setFont(QtGui.QFont('Times New Roman', 12, weight=QtGui.QFont.Bold))
        self.lbl2.move(1240, 20)
        
        self.lbl_xl2 = QtWidgets.QLabel(self)
        self.lbl_xl2.setText('left border (x-axis)')
        self.lbl_xl2.move(1285, 145)
        self.xl2 = QtWidgets.QLineEdit(self)
        self.xl2.setMaxLength(3)
        self.xl2.setFixedWidth(50)
        self.xl2.setText("0")
        self.xl2.move(1285, 160)
        
        self.lbl_xr2 = QtWidgets.QLabel(self)
        self.lbl_xr2.setText('right border (x-axis)')
        self.lbl_xr2.move(1515, 145)
        self.xr2 = QtWidgets.QLineEdit(self)
        self.xr2.setMaxLength(3)
        self.xr2.setFixedWidth(50)
        self.xr2.setText("0")
        self.xr2.move(1515, 160)
        
        self.lbl_yt2 = QtWidgets.QLabel(self)
        self.lbl_yt2.setText('upper border (y-axis)')
        self.lbl_yt2.move(1405, 45)
        self.yt2 = QtWidgets.QLineEdit(self)
        self.yt2.setMaxLength(3)
        self.yt2.setFixedWidth(50)
        self.yt2.setText("0")
        self.yt2.move(1405, 60)
        
        self.lbl_yb2 = QtWidgets.QLabel(self)
        self.lbl_yb2.setText('lower border (y-axis)')
        self.lbl_yb2.move(1400, 245)
        self.yb2 = QtWidgets.QLineEdit(self)
        self.yb2.setMaxLength(3)
        self.yb2.setFixedWidth(50)
        self.yb2.setText("0")
        self.yb2.move(1400, 260)
        
        self.lbl_zt2 = QtWidgets.QLabel(self)
        self.lbl_zt2.setText('top slice number')
        self.lbl_zt2.move(1630, 45)
        self.zt2 = QtWidgets.QLineEdit(self)
        self.zt2.setMaxLength(3)
        self.zt2.setFixedWidth(50)
        self.zt2.setText("0")
        self.zt2.move(1630, 60)
        
        self.lbl_zb2 = QtWidgets.QLabel(self)
        self.lbl_zb2.setText('bottom slice number')
        self.lbl_zb2.move(1630, 245)
        self.zb2 = QtWidgets.QLineEdit(self) 
        self.zb2.setMaxLength(3)
        self.zb2.setFixedWidth(50)
        self.zb2.setText("0")
        self.zb2.move(1630, 260)
        
        # Lower threshold
        self.lbl_lt2 = QtWidgets.QLabel(self)
        self.lbl_lt2.setText('lower threshold')
        self.lbl_lt2.move(1150, 635)
        self.lt2 = QtWidgets.QLineEdit(self)
        self.lt2.setMaxLength(3)
        self.lt2.setFixedWidth(50)
        self.lt2.setText("0")
        self.lt2.move(1150, 650)
        
        # Upper threshold
        self.lbl_ut2 = QtWidgets.QLabel(self)
        self.lbl_ut2.setText('upper threshold')
        self.lbl_ut2.move(1800, 635)
        self.ut2 = QtWidgets.QLineEdit(self)
        self.ut2.setMaxLength(3)
        self.ut2.setFixedWidth(50)
        self.ut2.setText("0")
        self.ut2.move(1800, 650)
        
        # self.lbl = QtWidgets.QLabel(self)
        # self.lbl.setText("For thresholds choose values which surround last peak.")
        # self.lbl.move(810, 530)
        
        # Whole series representation
        sc2 = MplCanvas(self, width=5, height=4, dpi=100)
        img = sitk.ReadImage(work_dir + "/data/portal_vein_phase_preprocessed.mha")
        img_array = sitk.GetArrayFromImage(img)
        X_tran = np.transpose(img_array, (1,2,0))
        color_map='gray'
        title = 'Axial slices' # 'Slices (choosing tridimensional kidneys regions bounds)'
        self.tracker = IndexTracker(sc2.axes, X_tran, color_map, title)
        sc2.fig.canvas.mpl_connect('scroll_event', self.tracker.onscroll)
        toolbar2 = NavigationToolbar(sc2, self)
        self.fixwidget2 = QtWidgets.QWidget(self)
        self.layout2  = QtWidgets.QGridLayout()
        self.layout2.addWidget(toolbar2, 0, 0)
        self.layout2.addWidget(sc2) 
        self.fixwidget2.setLayout(self.layout2) 
        height2 = self.fixwidget2.sizeHint().height()
        width2 = self.fixwidget2.sizeHint().width()
        xpos2, ypos2 = 700, 10
        self.fixwidget2.setGeometry(QtCore.QRect(xpos2, ypos2, width2, height2)) 
        
        # Histogram of right kidney
        self.sc = MplCanvas(self, width=5, height=4, dpi=100)
        self.sc.axes.set(xlabel='', ylabel='',
                title='Right kidney region histogram')
        self.toolbar = NavigationToolbar(self.sc, self)
        self.fixwidget = QtWidgets.QWidget(self)
        self.layout  = QtWidgets.QGridLayout()
        self.layout.addWidget(self.toolbar, 0, 0)
        self.layout.addWidget(self.sc)
        self.fixwidget.setLayout(self.layout) 
        height = self.fixwidget.sizeHint().height()
        width = self.fixwidget.sizeHint().width()
        xpos, ypos = 150, 420
        self.fixwidget.setGeometry(QtCore.QRect(xpos, ypos, width, height)) 
        
         # Histogram of left kidney
        self.sc3 = MplCanvas(self, width=5, height=4, dpi=100)
        self.sc3.axes.set(xlabel='', ylabel='',
                title='Left kidney region histogram')
        toolbar3 = NavigationToolbar(self.sc3, self)
        self.fixwidget3 = QtWidgets.QWidget(self)
        self.layout3  = QtWidgets.QGridLayout()
        self.layout3.addWidget(toolbar3, 0, 0)
        self.layout3.addWidget(self.sc3)
        self.fixwidget3.setLayout(self.layout3) 
        height3 = self.fixwidget3.sizeHint().height()
        width3 = self.fixwidget3.sizeHint().width()
        xpos3, ypos3 = 1250, 420
        self.fixwidget3.setGeometry(QtCore.QRect(xpos3, ypos3, width3, height3))
        
        self.pushButton_showHist = QtWidgets.QPushButton("Check borders and show histogram", self)
        self.pushButton_showHist.resize(190, 30)
        self.pushButton_showHist.move(280, 350)

        self.pushButton_showHist2 = QtWidgets.QPushButton("Check borders and show histogram", self)
        self.pushButton_showHist2.resize(190, 30)
        self.pushButton_showHist2.move(1380, 350) 
        
        self.pushButton_segm = QtWidgets.QPushButton("Right Kidney Segmentation...", self)
        self.pushButton_segm.resize(200, 40)
        self.pushButton_segm.move(325, 900)
        
        self.pushButton_segm2 = QtWidgets.QPushButton("Left Kidney Segmentation...", self)
        self.pushButton_segm2.resize(200, 40)
        self.pushButton_segm2.move(1425, 900)
        
        self.pushButton_next = QtWidgets.QPushButton('next (Segmentation of additional objects)', self)
        self.pushButton_next.resize(215, 40)
        self.pushButton_next.move(1695, 950)


class stoneSegmTab(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(stoneSegmTab, self).__init__(parent)
        self.lbl = QtWidgets.QLabel(self)
        self.lbl.setText("Choose appropriate lower and upper threshold to extract desired object\n"
                         "(for stone: leave upper threshold at 256 and change lower threshold if necessary).")
        self.lbl.move(50, 50)
        
        # Lower threshold
        self.lbl_lt = QtWidgets.QLabel(self)
        self.lbl_lt.setText('lower threshold')
        self.lbl_lt.move(300, 285)
        self.lt = QtWidgets.QLineEdit(self)
        self.lt.setMaxLength(3)
        self.lt.setFixedWidth(50)
        self.lt.setText("250")
        self.lt.move(300, 300)
        
        # Upper threshold
        self.lbl_ut = QtWidgets.QLabel(self)
        self.lbl_ut.setText('upper threshold')
        self.lbl_ut.move(1300, 285)
        self.ut = QtWidgets.QLineEdit(self)
        self.ut.setMaxLength(3)
        self.ut.setFixedWidth(50)
        self.ut.setText("256")
        self.ut.move(1300, 300)
        
        # Histogram picture
        import liver_segm
        sc = MplCanvas(self, width=5, height=4, dpi=100)
        hist = liver_segm.show_hist(work_dir)
        sc.axes.plot(hist)
        sc.axes.set(xlabel='', ylabel='',
                title='Whole volume histogram')
        toolbar = NavigationToolbar(sc, self)
        self.fixwidget = QtWidgets.QWidget(self)
        self.layout  = QtWidgets.QGridLayout()
        self.layout.addWidget(toolbar, 0, 0)
        self.layout.addWidget(sc)
        self.fixwidget.setLayout(self.layout)
        height = self.fixwidget.sizeHint().height()
        width = self.fixwidget.sizeHint().width()
        xpos, ypos = 600, 100
        self.fixwidget.setGeometry(QtCore.QRect(xpos, ypos, width, height))
        
        self.pushButton_segm = QtWidgets.QPushButton("Segmentation...", self)
        self.pushButton_segm.resize(200, 40)
        self.pushButton_segm.move(775, 750)
        
        self.pushButton_close = QtWidgets.QPushButton('Close', self)
        self.pushButton_close.resize(100, 40)
        self.pushButton_close.move(1800, 950)


# Window for entire segmentation process
class segmWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(segmWindow, self).__init__(parent)
        self.setWindowTitle("Segmentation")
        self.resize(800, 600)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("./pictures/organs.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)
        # self.setGeometry(50, 50, 400, 450)
        # self.setFixedSize(400, 450)
        
        self.statusBar = QtWidgets.QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage('Choose appropriate parameters to perform segmentation of the heart.')
        
        self.showMaximized()
        self.start_heart_segm()

    def start_heart_segm(self):
        self.ToolTab = heartSegmTab(self)
        self.setWindowTitle("Segmentation: Heart")
        self.setCentralWidget(self.ToolTab)

        self.ToolTab.pushButton_firstSliceSegm.clicked.connect(self.show_first_slice_segm)
        self.ToolTab.pushButton_heartBox.clicked.connect(self.show_heart_box)
        self.ToolTab.pushButton_segm.clicked.connect(self.heart_segm_starter)
        self.ToolTab.pushButton_next.clicked.connect(self.start_bones_segm)
        
        self.show()
    
    def show_first_slice_segm(self):
        import heart_segm
        try:
            a = int(self.ToolTab.xl.text())
            b = int(self.ToolTab.xr.text())
            c = int(self.ToolTab.yt.text())
            d = int(self.ToolTab.yb.text())
            heart_segm.first_slice_segm(work_dir, a, b, c, d)
        except:
            popup_message(self, "Parameters must be integers!")
   
    def show_heart_box(self):
        import heart_segm
        try:
            a = int(self.ToolTab.bl.text())
            b = int(self.ToolTab.br.text())
            c = int(self.ToolTab.bt.text())
            d = int(self.ToolTab.bb.text())
            e = int(self.ToolTab.bz.text())
            box = heart_segm.show_heart_box(work_dir, a, b, c, d, e)
        
            # Show box through slices
            fig, ax = plt.subplots(1, 1)
            fig.canvas.set_window_title('Figure')
            X_tran = np.transpose(box, (1,2,0))
            color_map='gray'
            title = 'Heart region (inside selected borders)'
            self.tracker = IndexTracker(ax, X_tran, color_map, title)
            fig.canvas.mpl_connect('scroll_event', self.tracker.onscroll)
            plt.show()  
        except:
            popup_message(self, "Parameters must be integers!")
             
    def heart_segm_starter(self):
        import heart_segm
        try:
            a = int(self.ToolTab.xl.text())
            b = int(self.ToolTab.xr.text())
            c = int(self.ToolTab.yt.text())
            d = int(self.ToolTab.yb.text())
            e = int(self.ToolTab.bl.text())
            f = int(self.ToolTab.br.text())
            g = int(self.ToolTab.bt.text())
            h = int(self.ToolTab.bb.text())
            i = int(self.ToolTab.bz.text())  
            self.statusBar.showMessage('Segmentation of the heart has started. Please wait...')
            heart_segm.main(work_dir, a, b, c, d, e, f, g, h, i)
            self.statusBar.showMessage('Segmentation of the heart is done. You can now proceed to segmentation of bones. '
                                       'If you are not satisfied with results, you can try repeating process with different parameters.')       
            rendering.main(work_dir + "/segmentation results/heart.mhd")
        except:
            popup_message(self, "Parameters must be integers!")

    def start_bones_segm(self):
        self.ToolTab = bonesSegmTab(self)
        self.setWindowTitle("Segmentation: Bones")
        self.setCentralWidget(self.ToolTab)
        
        self.Window.pushButton_segm.clicked.connect(self.bones_segm_starter)
        self.Window.pushButton_next.clicked.connect(self.start_liver_segm)
        
        self.statusBar.showMessage('Choose appropriate parameters to perform segmentation of bones.')
        
        self.show()
        
    def bones_segm_starter(self):
        import bones_segm
        try:
            a = int(self.Window.lt.text())
            b = int(self.Window.ut.text())
            self.statusBar.showMessage('Segmentation of bones has started. Please wait...')
            bones_segm.main(work_dir, a, b) 
            self.statusBar.showMessage('Segmentation of bones is done. You can now proceed to segmentation of liver and spleen. '
                                       'If you are not satisfied with results, you can try repeating process with different parameters.')
            rendering.main(work_dir + "/segmentation results/bones.mhd")  
        except:
            popup_message(self, "Parameters must be integers!")
       
    def start_liver_segm(self):
        self.ToolTab = liverSegmTab(self)
        self.setWindowTitle("Segmentation: Liver and spleen")
        self.setCentralWidget(self.ToolTab)
        
        self.ToolTab.pushButton_segm.clicked.connect(self.liver_segm_starter)
        self.ToolTab.pushButton_next.clicked.connect(self.start_kidneys_segm)
        
        self.statusBar.showMessage('Choose appropriate parameters to perform segmentation of liver and spleen.')
        
        self.show()
        
    def liver_segm_starter(self):
        import liver_segm
        try:
            a = int(self.ToolTab.lt.text())
            b = int(self.ToolTab.ut.text())
            self.statusBar.showMessage('Segmentation of liver and spleen has started. Please wait...')
            status = liver_segm.main(work_dir, a, b)
            if status:
                self.statusBar.showMessage('Segmentation of liver and spleen is done. You can now proceed to segmentation of kidneys. '
                                           'If you are not satisfied with results, you can try repeating process with different parameters.')
                rendering.main(work_dir + "/segmentation results/liver_and_spleen.mhd")
            else:
                popup_message(self, "Heart and bones must be first segmented!")
                self.statusBar.showMessage('Segmentation of liver and spleen failed.')
        except:
            popup_message(self, "Parameters must be integers!")
            
    def start_kidneys_segm(self):
        self.ToolTab = kidneysSegmTab(self)
        self.setWindowTitle("Segmentation: Kidneys")
        self.setCentralWidget(self.ToolTab)
        
        self.ToolTab.pushButton_showHist.clicked.connect(lambda: self.kidneys_segm_starter(0))
        self.ToolTab.pushButton_showHist2.clicked.connect(lambda: self.kidneys_segm_starter(1))
        self.ToolTab.pushButton_segm.clicked.connect(lambda: self.kidneys_segm_starter(2))
        self.ToolTab.pushButton_segm2.clicked.connect(lambda: self.kidneys_segm_starter(3))
        self.ToolTab.pushButton_next.clicked.connect(self.start_stone_segm)
        
        self.statusBar.showMessage('Choose appropriate parameters to perform segmentation of kidneys.')

        self.show()
        
    def kidneys_segm_starter(self, flag):
        import kidneys_segm
        try:
            if flag==2:
                print("Desni")
                a = int(self.ToolTab.lt.text())
                b = int(self.ToolTab.ut.text())
                c = int(self.ToolTab.xl.text())
                d = int(self.ToolTab.xr.text())
                e = int(self.ToolTab.yt.text())
                f = int(self.ToolTab.yb.text())
                g = int(self.ToolTab.zt.text())
                h = int(self.ToolTab.zb.text())
                self.statusBar.showMessage('Segmentation of right kidney has started. Please wait...')
                status = kidneys_segm.right_kidney(work_dir, a, b, c, d, e, f, g, h)
                if status:
                    self.statusBar.showMessage('Segmentation of right kidney is done. You can now proceed to segmentation of left kidney. '
                                               'If you are not satisfied with results, you can try repeating process with different parameters.')
                    rendering.main(work_dir + "/segmentation results/right_kidney.mhd")
                else:
                    popup_message(self, "Heart, bones, liver and spleen must be first segmented!")
                    self.statusBar.showMessage('Segmentation of right kidney failed.')
            elif flag==3:
                print("Levi")
                a = int(self.ToolTab.lt2.text())
                b = int(self.ToolTab.ut2.text())
                c = int(self.ToolTab.xl2.text())
                d = int(self.ToolTab.xr2.text())
                e = int(self.ToolTab.yt2.text())
                f = int(self.ToolTab.yb2.text())
                g = int(self.ToolTab.zt2.text())
                h = int(self.ToolTab.zb2.text())
                self.statusBar.showMessage('Segmentation of left kidney has started. Please wait...')
                status = kidneys_segm.left_kidney(work_dir, a, b, c, d, e, f, g, h)
                if status:
                    self.statusBar.showMessage('Segmentation of left kidney is done. You can now proceed to segmentation of additional objects. '
                                               'If you are not satisfied with results, you can try repeating process with different parameters.')
                    rendering.main(work_dir + "/segmentation results/left_kidney.mhd")
                else:
                    popup_message(self, "Heart, bones, liver and spleen must be first segmented!")
                    self.statusBar.showMessage('Segmentation of left kidney failed.')
            elif flag==0:
                print("Histogram")
                a = int(self.ToolTab.xl.text())
                b = int(self.ToolTab.xr.text())
                c = int(self.ToolTab.yt.text())
                d = int(self.ToolTab.yb.text())
                e = int(self.ToolTab.zt.text())
                f = int(self.ToolTab.zb.text())
                box, hist, status = kidneys_segm.show_hist(work_dir, a, b, c, d, e, f)
                if status:
                    self.ToolTab.sc.axes.figure.canvas.axes.clear()
                    self.ToolTab.sc.axes.plot(hist)
                    self.ToolTab.sc.axes.set(xlabel='', ylabel='',
                    title='Right kidney region histogram')
                    self.ToolTab.sc.axes.figure.canvas.draw()
                    fig, ax = plt.subplots(1, 1)
                    fig.canvas.set_window_title('Figure')
                    X_tran = np.transpose(box, (1,2,0))
                    color_map='gray'
                    title = 'Right kidney region (inside selected borders)'
                    self.tracker = IndexTracker(ax, X_tran, color_map, title)
                    fig.canvas.mpl_connect('scroll_event', self.tracker.onscroll)
                    plt.show()
                else:
                    popup_message(self, "Heart, bones and liver and spleen must be first segmented!")
            else:
                print("Histogram2")
                a = int(self.ToolTab.xl2.text())
                b = int(self.ToolTab.xr2.text())
                c = int(self.ToolTab.yt2.text())
                d = int(self.ToolTab.yb2.text())
                e = int(self.ToolTab.zt2.text())
                f = int(self.ToolTab.zb2.text())
                box, hist, status = kidneys_segm.show_hist(work_dir, a, b, c, d, e, f)
                if status:
                    self.ToolTab.sc3.axes.figure.canvas.axes.clear()
                    self.ToolTab.sc3.axes.plot(hist)
                    self.ToolTab.sc3.axes.set(xlabel='', ylabel='',
                    title='Left kidney region histogram')
                    self.ToolTab.sc3.axes.figure.canvas.draw()
                    fig, ax = plt.subplots(1, 1)
                    fig.canvas.set_window_title('Figure')
                    X_tran = np.transpose(box, (1,2,0))
                    color_map='gray'
                    title = 'Left kidney region (inside selected borders)'
                    self.tracker2 = IndexTracker(ax, X_tran, color_map, title)
                    fig.canvas.mpl_connect('scroll_event', self.tracker2.onscroll)
                    plt.show()
                else:
                    popup_message(self, "Heart, bones and liver and spleen must be first segmented!") 
        except:
                popup_message(self, "Parameters must be integers!")
    
    def start_stone_segm(self):
        self.ToolTab = stoneSegmTab(self)
        self.setWindowTitle("Segmentation: Stone")
        self.setCentralWidget(self.ToolTab)
        
        self.ToolTab.pushButton_segm.clicked.connect(self.stone_segm_starter)
        self.ToolTab.pushButton_close.clicked.connect(self.close_segmWin)
        
        self.statusBar.showMessage('Choose appropriate parameters to perform segmentation of calcifications or other objects.')
        
        self.show()
    
    def stone_segm_starter(self):
        import stone_segm
        try:
            a = int(self.ToolTab.lt.text())
            b = int(self.ToolTab.ut.text())
            self.statusBar.showMessage('Segmentation of stone/additional objects has started. Please wait...')
            stone_segm.main(work_dir, a, b)
            self.statusBar.showMessage('Segmentation of stone/additional objects is done. If you are not satisfied with results, '
                                       'you can try repeating process with different parameters.')
            rendering.main(work_dir + "/segmentation results/stone.mhd")
            
        except:
            popup_message(self, "Parameters must be integers!")
        
    def close_segmWin(self):
        self.close()
        
    def closeEvent(self, event):
        MainWindow.statusBar().showMessage('')
        if os.path.exists(work_dir + "/segmentation results"):
            MainWindow.statusBar().showMessage('You can now proceed to 3D View of Segmented Data.')
        else:
            MainWindow.statusBar().showMessage('No organ is segmented.')
        
class StartWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(StartWindow, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, 1)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("./pictures/organs.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)
        label = QtWidgets.QLabel(self)
        pixmap = QtGui.QPixmap("./pictures/introduction.png")
        label.setPixmap(pixmap)
        self.setCentralWidget(label)
        self.resize(pixmap.width(), pixmap.height())
        self.show()
        
    def close_startWin(self):
        QtCore.QTimer.singleShot(4000, self.close)

class Ui_MainWindow(QtWidgets.QMainWindow):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setFixedSize(800, 600)
        MainWindow.setAutoFillBackground(False)
        MainWindow.setAnimated(False)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("./pictures/organs.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        
        self.toolButton_read = QtWidgets.QToolButton(self.centralwidget)
        self.toolButton_read.setGeometry(QtCore.QRect(1, 0, 101, 61))
        self.toolButton_read.setStyleSheet('QToolButton {background-color: lightgrey; color: #35322f;}')
        self.toolButton_read.setCheckable(False)
        self.toolButton_read.setObjectName("toolButton_show")
        self.toolButton_read.clicked.connect(self.show_data)
        
        self.toolButton_chooseWorkDir = QtWidgets.QToolButton(self.centralwidget)
        self.toolButton_chooseWorkDir.setGeometry(QtCore.QRect(101, 0, 101, 61))
        self.toolButton_chooseWorkDir.setStyleSheet('QToolButton {background-color: lightgrey; color: #35322f;}')
        self.toolButton_chooseWorkDir.setCheckable(False)
        self.toolButton_chooseWorkDir.setObjectName("toolButton_choose")
        self.toolButton_chooseWorkDir.clicked.connect(self.choose_work_dir)
        
        self.toolButton_preproc = QtWidgets.QToolButton(self.centralwidget)
        self.toolButton_preproc.setGeometry(QtCore.QRect(201, 0, 101, 61))
        self.toolButton_preproc.setStyleSheet('QToolButton {background-color: lightgrey; color: #35322f;}')
        self.toolButton_preproc.setCheckable(False)
        self.toolButton_preproc.setObjectName("toolButton_preproc")
        self.toolButton_preproc.clicked.connect(self.start_preproc)
    
        self.toolButton_segm = QtWidgets.QToolButton(self.centralwidget)
        self.toolButton_segm.setGeometry(QtCore.QRect(301, 0, 101, 61))
        self.toolButton_segm.setStyleSheet('QToolButton {background-color: lightgrey; color: #35322f;}')
        self.toolButton_segm.setCheckable(False)
        self.toolButton_segm.setObjectName("toolButton_segm")
        self.toolButton_segm.clicked.connect(self.start_segm)
        
        self.toolButton_render = QtWidgets.QToolButton(self.centralwidget)
        self.toolButton_render.setGeometry(QtCore.QRect(401, 0, 101, 61))
        self.toolButton_render.setStyleSheet('QToolButton {background-color: lightgrey; color: #35322f;}')
        self.toolButton_render.setCheckable(False)
        self.toolButton_render.setObjectName("toolButton_render")
        self.toolButton_render.clicked.connect(self.start_render)
        
        MainWindow.setCentralWidget(self.centralwidget)
        
        # button_action = QtWidgets.QAction(QtGui.QIcon("icon.png"), "&Your button", self)
        button_action = QtWidgets.QAction("&GitHub", self) # Drugacije
        button_action.setStatusTip("Enter GitHub page of the program")
        button_action.triggered.connect(self.open_url)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 500, 800, 21))
        # self.menubar.setStyleSheet('QMenuBar {background-color: lightgrey; color: #35322f;}')
        # self.menubar.setStyleSheet('QMenuBar::item {background-color: lightgrey; color: #35322f;}')
        self.menubar.setObjectName("menubar")
        self.filemenu = self.menubar.addMenu("&Help")
        # self.filemenu.setStyleSheet('QMenu {background-color: lightgrey; color: #35322f;}')
        self.filemenu.addAction(button_action)
        MainWindow.setMenuBar(self.menubar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        MainWindow.statusBar().showMessage('This is main menu of the program. Before Data Preprocessing and Segmentation choose work directory.')
           
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "3D Gastro CT Tool"))
        self.toolButton_read.setText(_translate("MainWindow", "Show\n"
                                                "Data"))
        self.toolButton_read.setFont(QtGui.QFont('Times', 10))
        self.toolButton_preproc.setText(_translate("MainWindow", "Data\n"
                                                   "Preprocessing"))
        self.toolButton_preproc.setFont(QtGui.QFont('Times', 9))
        self.toolButton_chooseWorkDir.setText(_translate("MainWindow", "Choose Work\nDirectory"))
        self.toolButton_chooseWorkDir.setFont(QtGui.QFont('Times', 9))
        self.toolButton_segm.setText(_translate("MainWindow", "Segmentation"))
        self.toolButton_segm.setFont(QtGui.QFont('Times', 10))
        self.toolButton_render.setText(_translate("MainWindow", "3D View of\nSegmented Data"))
        self.toolButton_render.setFont(QtGui.QFont('Times', 10))

    def open_url(self):
        print("Opening")
        url = QtCore.QUrl('https://github.com/')
        if not QtGui.QDesktopServices.openUrl(url):
            QtGui.QMessageBox.warning(self, 'Open Url', 'Could not open url')
        
    def show_data(self):
        file, _ = QtWidgets.QFileDialog.getOpenFileName(self.centralwidget, "Select Image File")
        try:
            img = sitk.ReadImage(file)          
            img_array = sitk.GetArrayFromImage(img)
            # Show series
            fig, ax = plt.subplots(1, 1)
            fig.canvas.set_window_title('Series display')
            X_tran = np.transpose(img_array, (1,2,0))
            color_map='gray'
            title = 'Axial slices'
            self.tracker = IndexTracker(ax, X_tran, color_map, title)
            fig.canvas.mpl_connect('scroll_event', self.tracker.onscroll)
            fig.canvas.mpl_connect('close_event', self.tracker.on_close)
            plt.show()
        except:
            popup_message(self, "Chosen file is not appropriate!")
    
    def choose_work_dir(self):
        dir = QtWidgets.QFileDialog.getExistingDirectory(self.centralwidget, "Choose Work Directory")
        global work_dir
        work_dir = dir
        if dir!="":
            MainWindow.statusBar().showMessage('"' + work_dir + '" is chosen for work directory. You can now proceed to next steps.')
        
    def start_preproc(self):
        if work_dir!="":
            self.w = preprocWindow()
            MainWindow.statusBar().showMessage('Data Preprocessing...')
            self.w.show()
        else:
            popup_message(self, "You have to choose work directory!")
         
    def start_segm(self):
        if work_dir!="":
            if os.path.exists(work_dir + "/data/portal_vein_phase_preprocessed.mha") & os.path.exists(work_dir + "/data/native_phase_preprocessed.mha"):
                self.w = segmWindow() 
                MainWindow.statusBar().showMessage('Segmentation...')
                self.w.show()
            else:
                popup_message(self, "Before Segmentation, you have to finish Data Processing.")
        else:
            popup_message(self, "You have to choose work directory!")
        
    def start_render(self):
        if work_dir!="":
            if os.path.exists(work_dir + "/segmentation results"):
                import whole_segm
                MainWindow.statusBar().showMessage('Rendering...')
                whole_segm.main(work_dir)
                import rendering
                rendering.main(work_dir + "/segmentation results/whole_segmentation.mhd")
                MainWindow.statusBar().showMessage('')
            else:
                popup_message(self, "There is no segmented data!")
        else:
            popup_message(self, "You have to choose work directory!")
                  
    def closeEvent(self, event):
        self.QApplication.quit()

if __name__ == "__main__":
    import sys
    work_dir = ""
    app = QtWidgets.QApplication(sys.argv)
    startWin = StartWindow()
    startWin.show()
    startWin.close_startWin()
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    QtCore.QTimer.singleShot(4300, MainWindow.show)
    # sys.exit(app.exec_())
    sys.exit()