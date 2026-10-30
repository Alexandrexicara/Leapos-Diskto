"""Desktop principal PyQt6 do LeapOS."""
import sys,subprocess
from pathlib import Path
from datetime import datetime
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QApplication,QMainWindow,QWidget,QVBoxLayout,QGridLayout,QLabel,QPushButton,QMessageBox
from .apps import Notes,Calculator,MediaWindow,Files,Browser,AppCatalog
from .assistant import Assistant
class Desktop(QMainWindow):
 def __init__(self):
  super().__init__();self.children=[];self.setWindowTitle("LeapOS");self.resize(1200,760)
  self.setStyleSheet("QMainWindow,QWidget{background:#111b2b;color:#edf4f8;font-size:14px} QPushButton{background:#243750;border:1px solid #40566e;border-radius:10px;padding:16px;text-align:left} QPushButton:hover{border-color:#76e4bd;background:#2b435e}")
  root=QWidget();v=QVBoxLayout(root);v.setContentsMargins(30,24,30,14);self.setCentralWidget(root)
  h=QLabel("LeapOS");h.setStyleSheet("font-size:36px;font-weight:700;color:#83e8c3");v.addWidget(h);v.addWidget(QLabel("Seu computador. Seu espaco de trabalho."))
  grid=QGridLayout();v.addLayout(grid)
  entries=[("Arquivos","files"),("Navegador","browser"),("Bloco de notas","notes"),("Calculadora","calc"),("Fotos","photos"),("Videos","video"),("Musica","music"),("Aplicativos","catalog"),("Assistente Leap","assistant"),("Downloads","downloads"),("Lixeira","trash"),("Configuracoes","settings")]
  menu=self.menuBar().addMenu("Iniciar")
  for i,(label,key) in enumerate(entries):
   b=QPushButton(label);b.setMinimumHeight(82);b.clicked.connect(lambda checked=False,k=key:self.launch(k));grid.addWidget(b,i//4,i%4)
   a=QAction(label,self);a.triggered.connect(lambda checked=False,k=key:self.launch(k));menu.addAction(a)
  self.clock=QLabel();self.statusBar().addPermanentWidget(self.clock);self.timer=QTimer(self);self.timer.timeout.connect(lambda:self.clock.setText(datetime.now().strftime("%d/%m/%Y  %H:%M:%S")));self.timer.start(1000)
 def launch(self,key):
  try:
   if key=="files":w=Files()
   elif key=="browser":w=Browser()
   elif key=="notes":w=Notes()
   elif key=="calc":w=Calculator()
   elif key in ("photos","video","music"):w=MediaWindow(key)
   elif key=="catalog":w=AppCatalog()
   elif key=="assistant":w=Assistant()
   elif key=="downloads":subprocess.Popen(["xdg-open",str(Path.home()/"Downloads")]);return
   elif key=="trash":subprocess.Popen(["xdg-open","trash:///"]);return
   elif key=="settings":subprocess.Popen(["xfce4-settings-manager"]);return
   else:return
   self.children.append(w);w.show()
  except Exception as e:QMessageBox.warning(self,"LeapOS",f"Nao foi possivel abrir o aplicativo: {e}")
def main():
 app=QApplication(sys.argv);app.setApplicationName("LeapOS");window=Desktop();window.showFullScreen();sys.exit(app.exec())
if __name__=="__main__":main()
