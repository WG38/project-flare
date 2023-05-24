
import binascii
import gzip
import os
import time
import PyQt5.QtCore
import sys

from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel,  QWidget, QPushButton, QCheckBox, QLineEdit
from PyQt5.QtCore import pyqtSlot
from PIL import Image

class App(QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'Image to Map Converter'
        self.setWindowIcon(QtGui.QIcon('MapNew.png'))
        self.left = 1000
        self.top = 500
        self.width = 600
        self.height = 300
        self.initUI()
        self.img = ""
        self.preserve_ratio = "N"
        self.w_name = ""
        self.m_number = ""
    
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        
        image_select = QPushButton('Select Image', self)
        #button.setToolTip('This is an example button')
        image_select.move(0,70)
        image_select.clicked.connect(self.img_select)
        
        aspect_select = QCheckBox("Preserve Apect Ratio?",self)
        aspect_select.move(0,110)
        aspect_select.toggled.connect(self.asp_select)

        self.world_name = QLineEdit(self,placeholderText="World Name")
        self.world_name.move(0, 140)
        self.world_name.resize(280,40)
        #self.w_name = world_name.text()

        self.map_number = QLineEdit(self,placeholderText="Map Number")
        self.map_number.move(0, 190)
        self.map_number.resize(280,40)
        #self.m_number = map_number.text()


        start_program = QPushButton("Start Image->Map Conversion",self)
        start_program.move(0,250)
        start_program.clicked.connect(self.mainProgram)
        
        
        self.show()

    @pyqtSlot()
    def img_select(self):
        self.img = QtWidgets.QFileDialog.getOpenFileNames(None, 'Select project folder:', 'F:\\')
        #mg2.save("Success.png")

    def asp_select(self):
        cbutton = self.sender()
        if cbutton.isChecked() == True:
            self.preserve_ratio = "Y"
        else:
            self.preserve_ratio = "N"
    def mainProgram(self):
        #print(self.img)
        #print(self.preserve_ratio)
        #preload all data#
        try:
             imgPath = self.img[0][0]
             img2 = Image.open(imgPath)
        except:
            image_error = QtWidgets.QMessageBox()
            image_error.setIcon(QtWidgets.QMessageBox.Critical)
            image_error.setText("Conversion Error")
            image_error.setInformativeText('Invalid Image File. Please input a valid image file')
            image_error.setWindowTitle("Conversion Error")
            image_error.exec_()
            return
        mode_switch = self.preserve_ratio
        save_name = self.world_name.text()
        map_number2 = self.map_number.text()
        img2 = img2.convert("RGB")
    
        if mode_switch == "N":
            img2 = img2.resize((128,128),Image.ANTIALIAS)
        if mode_switch == "Y":
            width,height = img2.size
            while width >= 128 or height >= 128:
                width = int(width/1.1)
                height = int(height/1.1)
            img2 = img2.resize((width,height),Image.ANTIALIAS)
            bcg = Image.new("RGB",(128,128),(255,255,255))
            bcg.paste(img2, ((128-width)//2,
                      (128-height)//2))
            img2 = bcg
        
        
        # list of avalible colors in the map#
        list_of_colors = [(127, 178, 56),(247, 233, 163),(199, 199, 199),(255, 0, 0),(160, 160, 255),(167, 167, 167),(0, 124, 0),(255, 255, 255),(164, 168, 184),(151, 109, 77),(112, 112, 112),
(64, 64, 255),(143, 119, 72),(255, 252, 245),(216, 127, 51),(178, 76, 216),(102, 153, 216),(229, 229, 51),(127, 204, 25),(242, 127, 165),(76, 76, 76),(153, 153, 153),(76, 127, 153),(127, 63, 178),(51, 76, 178),(102, 76, 51),(102, 127, 51),(153, 51, 51),(25, 25, 25),(250, 238, 77),(92, 219, 213),(74, 128, 255),(0, 217, 58),(129, 86, 49),(112, 2, 0),(209, 177, 161),(159, 82, 36),(149, 87, 108),(112, 108, 138),(186, 133, 36),(103, 117, 53),(160, 77, 78),(57, 41, 35),(135, 107, 98),(87, 92, 92),(122, 73, 88),(76, 62, 92),(76, 50, 35),(76, 82, 42),(142, 60, 46),(37, 22, 16),(189, 48, 49),(148, 63, 97),(92, 25, 29),(22, 126, 134),(58, 142, 140),(86, 44, 62),(20, 180, 133)]
                                                                                                              
        # rgb to mc squizzer#
        pix_list = img2.load()
        width,height = img2.size
        export_img = Image.new("RGB",(128,128),(255,255,255))
        ex_img_list = export_img.load()
        for i in range(0,width):
            for j in range(0,height):
                px = pix_list[i,j]
                dst_list = []
                for clr in list_of_colors:
                    curr_distance = ((clr[0] - px[0])**2 + (clr[1] - px[1])**2 + (clr[2] - px[2])**2)**0.5
                    dst_list.append(curr_distance)
                new_px = list_of_colors[dst_list.index(min(dst_list))]
                ex_img_list[i,j] = new_px

        

        map_file = open("hexified","wb")

        #tables#
        header_str = ["0A00000A0004646174610300077A43656E74657200000000010011756E6C696D69746564547261636B696E6700010010747261636B696E67506F736974696F6E000900066672616D657300000000000100057363616C65000100066C6F636B65640108000964696D656E73696F6E00136D696E6563726166743A6F766572776F726C6409000762616E6E65727300000000000300077843656E74657200000000070006636F6C6F727300004000"]
        butter_str = ["0003000B4461746156657273696F6E00000A1400"]

        color_table = [(127, 178, 56),(247, 233, 163),(199, 199, 199),(255, 0, 0),(160, 160, 255),(167, 167, 167),(0, 124, 0),(255, 255, 255),(164, 168, 184),(151, 109, 77),(112, 112, 112),(64, 64, 255),(143, 119, 72),(255, 252, 245),(216, 127, 51),(178, 76, 216),(102, 153, 216),(229, 229, 51),(127, 204, 25),(242, 127, 165),(76, 76, 76),(153, 153, 153),(76, 127, 153),(127, 63, 178),(51, 76, 178),(102, 76, 51),(102, 127, 51),(153, 51, 51),(25, 25, 25),(250, 238, 77),(92, 219, 213),(74, 128, 255),(0, 217, 58),(129, 86, 49),(112, 2, 0),(209, 177, 161),(159, 82, 36),(149, 87, 108),(112, 108, 138),(186, 133, 36),(103, 117, 53),(160, 77, 78),(57, 41, 35),(135, 107, 98),(87, 92, 92),(122, 73, 88),(76, 62, 92),(76, 50, 35),(76, 82, 42),(142, 60, 46),(37, 22, 16),(189, 48, 49),(148, 63, 97),(92, 25, 29),(22, 126, 134),(58, 142, 140),(86, 44, 62),(20, 180, 133)]
        hex_table = ["05","09","0d","11","15","19","1d","21","25","29","2d","32","35","39","3d","41","45","49","4d","51","55","59","5d","61","65","69","6d",
        "71","75","79","7d","81","85","89","8d","91","95","99","9d","a1","a5","a9","ad","b1","b5","b9","bd","c1","c5","c9","cd","d1","d5","d9","dd","e1","e5","e9","2c"]

        #header loading# 
        for i in header_str:
            map_file.write(binascii.unhexlify(i))


        #main pixel body#
        for i in range(0,width):
            for j in range(0,height):
                curr_hex = 0
                curr_pix = ex_img_list[j,i]
                for k in range(0,len(color_table)):
                    if curr_pix == color_table[k]:
                        try:
                            curr_hex = hex_table[k]
                        except IndexError:
                            curr_hex = hex_table[0]
                        map_file.write(binascii.unhexlify(curr_hex))

        #butt-er loading#
        for w in butter_str:
            map_file.write(binascii.unhexlify(w))


        map_file.close()

        # file compress&shuttle to .minecraft #
        directory = "~\AppData\Roaming\.minecraft\saves\\" + save_name + "\data"
        abs_directory = os.path.expanduser(directory)
        full_dir = abs_directory + "\\map_" + str(map_number2) + ".dat"
        try:
            os.remove(full_dir)
        except FileNotFoundError:
            pass 
        print("Compressing the file...")
        try:
            f = open(full_dir, 'wb')
        except:
            world_error = QtWidgets.QMessageBox()
            world_error.setIcon(QtWidgets.QMessageBox.Critical)
            world_error.setText("Conversion Error")
            world_error.setInformativeText('Invalid World Name')
            world_error.setWindowTitle("Conversion Error")
            world_error.exec_()
            os.remove("hexified")
            return
        f_in = open('hexified','rb')
        gz = gzip.GzipFile('', 'wb', 8, f, 0.)

        for ln in f_in:
            gz.write(ln)
        gz.close()
        f.close()
        f_in.close()
        print("Moving the file to .minecraft...")
        time.sleep(2)
        os.remove("hexified")
        completion_message = QtWidgets.QMessageBox()
        completion_message.setIcon(QtWidgets.QMessageBox.Information)
        completion_message.setText("Conversion Completed")
        completion_message.setInformativeText('Succesfully completed image->map conversion')
        completion_message.setWindowTitle("Conversion Completed")
        completion_message.exec_()
        









if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
input()
