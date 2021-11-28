import os
import sys
import cv2
import glob
import time
import uuid
import random
import numpy as np
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

class Gui(QMainWindow):

	cancelelapse = pyqtSignal()
	cancelecal = pyqtSignal()
	timelapsing = False

	def __init__(self):
		super().__init__()
		self.initUI()

	def initUI(self):
		self.label = QLabel('타임랩서'); self.label.setStyleSheet("font-size: 35px;")
		self.timelapser = QPushButton('동영상 만들기')

		self.timelapser.clicked.connect(self.timelapse)

		widget = QWidget(self)
		layout = QGridLayout()

		layout.addWidget(self.label,0,0)
		layout.addWidget(self.timelapser,1,0)

		widget.setLayout(layout)
		self.setCentralWidget(widget)

		quit = QAction("나가기", self)
		quit.triggered.connect(self.closeEvent)

		self.setWindowTitle('타임랩서')
		self.statusBar().showMessage('v2.5')
		#
		# 1.0 - 초기 버전
		# 1.1 - 취소 기능 개선
		# 2.0 - 남은 시간 예측
		# 2.1 - 남은 시간 평균 개선
		# 2.2 - 남은 시간 예측 알고리즘 변경
		# 2.3 - 남은 시간 예측 소폭 개선
		# 2.4 - 남은 시간 예측 알고리즘 소폭 변경 및 개선
		# 2.5 - 취소 기능 오류 해결
		#
		self.setWindowIcon(QIcon('images/time.png'))
		self.resize(300, 500)
		self.center()
		self.show()

	def canceled(self):
		QMessageBox.question(self, '안내창', '취소되었습니다.', QMessageBox.Yes)
		self.timelapser.setEnabled(True)

	def timelapse(self):
		self.timelapser.setEnabled(False)
		QMessageBox.question(self, '안내창', '사진들이 있는 폴더를 지정해주세요.', QMessageBox.Yes)
		input_path = QFileDialog.getExistingDirectory(self, self.tr("Open Data files"), './', QFileDialog.ShowDirsOnly)
		if len(input_path) == 0:
			self.canceled()
			return
		outname, ok = QInputDialog.getText(self, '입력창', '저장할 이름을 입력해주세요(확장자 없이):')
		if ok:
			if outname == '':
				QMessageBox.question(self, '안내창', '유효한 값을 입력해주세요.', QMessageBox.Yes)
				self.timelapser.setEnabled(True)
				return
			if os.path.exists(input_path+'\\'+outname+'.mp4'):
				QMessageBox.question(self, '안내창', '이미 파일이 존재합니다.', QMessageBox.Yes)
				self.timelapser.setEnabled(True)
				return
		else:
			self.canceled()
			return
		fps, ok = QInputDialog.getInt(self, '입력창', 'fps를 입력해주세요:')
		if ok:
			if fps == 0:
				QMessageBox.question(self, '안내창', '유효한 값을 입력해주세요.', QMessageBox.Yes)
				self.timelapser.setEnabled(True)
				return
		else:
			self.canceled()
			return
		outname = outname+'.mp4'

		thread = TimeLapser(self,input_path,outname,fps)
		thread.lapsedone.connect(self.lapsedone)
		thread.canceldone.connect(self.diacanceled)
		thread.bar.connect(self.barc)
		thread.rt.connect(self.rt)

		self.cancelelapse.connect(thread.cancel)
		self.PB_dialogue()
		thread.start()
		self.timelapsing = True

	def rt(self,val):
		h = val // 3600
		val = val - h*3600
		mi = val // 60
		ss = val - mi*60
			
		if h == 0:
			if mi == 0:
				if ss <= 1:
					text = '완료중..'
				else:
					text = '약 '+str(ss)+'초'
			else:
				text = '약 '+str(mi)+'분 '+str(ss)+'초'
		else:
			text = '약 '+str(h)+'시간 '+str(mi)+'분 '+str(ss)+'초'
		self.retime.setText('남은 시간 : '+text)

	def barc(self,value):
		self.bar.setValue(value)

	def PB_dialogue(self):
		self.timedialog = QDialog()

		widget = QWidget(self.timedialog)
		vbox = QVBoxLayout(self.timedialog)

		bar_hbox = QHBoxLayout()
		retime_hbox = QHBoxLayout()
		cancel_hbox = QHBoxLayout()

		self.bar = QProgressBar(self.timedialog)
		self.bar.setGeometry(10, 10, 200, 30)
		self.bar.setValue(0)
		self.bar.setAlignment(Qt.AlignCenter)
		self.bar.resetFormat()

		self.retime = QLabel('남은 시간 : 계산중..', self.timedialog)
		self.retime.move(70, 50)

		btn = QPushButton('작업 취소하기', self.timedialog)
		btn.move(70, 70)
		btn.clicked.connect(self.canceleelapse)

		bar_hbox.addStretch(1)
		bar_hbox.addWidget(self.bar)
		bar_hbox.addStretch(1)

		retime_hbox.addStretch(1)
		retime_hbox.addWidget(self.retime)
		retime_hbox.addStretch(1)

		cancel_hbox.addStretch(1)
		cancel_hbox.addWidget(btn)
		cancel_hbox.addStretch(1)

		vbox.addLayout(bar_hbox)
		vbox.addStretch(1)
		vbox.addLayout(retime_hbox)
		vbox.addStretch(1)
		vbox.addLayout(cancel_hbox)

		self.timedialog.setLayout(vbox)
		self.timedialog.setWindowIcon(QIcon('images/time.png'))
		self.timedialog.setWindowTitle('진행률')
		self.timedialog.setWindowModality(Qt.ApplicationModal)
		self.timedialog.resize(220, 100)
		self.timedialog.show()

	def canceleelapse(self):
		self.cancelelapse.emit()
		self.cancelecal.emit()

	def lapsedone(self):
		self.timelapsing = False
		self.timedialog.reject()
		self.statusBar().showMessage('준비')
		QMessageBox.question(self, '안내창', '동영상 작업이 완료되었습니다.', QMessageBox.Yes)
		self.timelapser.setEnabled(True)

	def diacanceled(self):
		self.timelapsing = False
		self.timedialog.reject()
		self.statusBar().showMessage('준비')
		QMessageBox.question(self, '안내창', '취소되었습니다.', QMessageBox.Yes)
		self.timelapser.setEnabled(True)

	def closeEvent(self,event):
		if self.timelapsing == True:
			QMessageBox.question(self, '안내창', '현재 진행중인 작업이 끝난 뒤에 종료해주세요.', QMessageBox.Yes)
			event.ignore()

	def center(self):
		qr = self.frameGeometry()
		cp = QDesktopWidget().availableGeometry().center()
		qr.moveCenter(cp)
		self.move(qr.topLeft())

class TimeLapser(QThread):

	lapsedone = pyqtSignal()
	canceldone = pyqtSignal()
	bar = pyqtSignal(int)
	rt = pyqtSignal(int)

	def __init__(self,parent,inpath,outname,fps):
		super().__init__(parent)
		self.parent = parent
		self.inpath = inpath
		self.outname = outname
		self.fps = fps
		self.canceled = False
		self.last_times = []

	def get_remaining_time(self, i, total, time):
		self.last_times.append(time)
		len_last_t = len(self.last_times)
		mean_t = sum(self.last_times) / len_last_t 
		remain = int(mean_t * (total - i + 1))
		return remain

	def run(self):
		paths = sorted(glob.glob(self.inpath + '\\*.jpg'))
		paths = [os.path.join(self.inpath, path) for path in paths]

		total = len(paths)
		if total == 0:
			self.parent.statusBar().showMessage('준비')
			self.lapsedone.emit()
			return
		pb = 1
		frame_array = []
		for idx, path in enumerate(paths): 
			if self.canceled == True:
				self.canceldone.emit()
				return
			start = time.time()
			ff = np.fromfile(path, np.uint8)
			print(path)
			img = cv2.imdecode(ff,1)
			height, width, layers = img.shape
			size = (width, height)

			self.parent.statusBar().showMessage(os.path.basename(path)+' 작업중..')
			frame_array.append(img)
			self.parent.statusBar().showMessage(os.path.basename(path)+' 작업끝')
			pbper = (pb * 100) / (total*2)
			self.bar.emit(round(pbper))
			art = self.get_remaining_time(pb, total, time.time()-start)
			self.rt.emit(int(art+0.06*total))
			pb += 1
		out = cv2.VideoWriter(self.inpath+'\\'+self.outname, cv2.VideoWriter_fourcc(*'mp4v'), int(self.fps), size)
		self.last_times = []
		j = 1
		for i in range(len(frame_array)):
			if self.canceled == True:
				out.release()
				self.parent.statusBar().showMessage('취소중..')
				for tempn in pre_names:
					if os.path.exists(self.inpath+'\\'+tempn):
						os.remove(self.inpath+'\\'+tempn)
				if os.path.exists(self.inpath+'\\'+self.outname):
					os.remove(self.inpath+'\\'+self.outname)
				self.canceldone.emit()
				return
			start = time.time()
			# self.parent.statusBar().showMessage(os.path.basename(paths[i])+' 작업중..')
			out.write(frame_array[i])
			# self.parent.statusBar().showMessage(os.path.basename(paths[i])+' 작업끝')
			art = self.get_remaining_time(j, total, time.time()-start)
			pbper = (pb * 100) / (total*2)
			self.bar.emit(round(pbper))
			self.rt.emit(art)
			j += 1
			pb += 1
		out.release()
		self.lapsedone.emit()

	def cancel(self):
		self.canceled = True

if __name__ == '__main__':

	try:
		os.chdir(sys._MEIPASS)
		print(sys._MEIPASS)
	except:
		os.chdir(os.getcwd())

	app = QApplication(sys.argv)
	ex = Gui()
	sys.exit(app.exec_())