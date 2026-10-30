"""Aplicativos integrados do desktop LeapOS."""
import ast,operator,subprocess,shutil
from pathlib import Path
from PyQt6.QtCore import QUrl
from PyQt6.QtWidgets import (QMainWindow,QWidget,QVBoxLayout,QHBoxLayout,QTextEdit,QLineEdit,QPushButton,QFileDialog,QMessageBox,QLabel,QListWidget,QSlider)
from PyQt6.QtMultimedia import QMediaPlayer,QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget
from .catalog import load_apps

class Notes(QMainWindow):
 def __init__(self):
  super().__init__(); self.path=None; self.setWindowTitle("Bloco de notas"); self.resize(760,520); self.edit=QTextEdit(); self.setCentralWidget(self.edit)
  bar=self.addToolBar("Arquivo")
  for label,fn in [("Novo",self.new),("Abrir",self.open),("Salvar",self.save)]:
   from PyQt6.QtGui import QAction
   a=QAction(label,self);a.triggered.connect(fn);bar.addAction(a)
 def new(self):
  if self.edit.document().isModified() and QMessageBox.question(self,"Salvar","Descartar alteracoes?")!=QMessageBox.StandardButton.Yes:return
  self.edit.clear();self.path=None
 def open(self):
  p,_=QFileDialog.getOpenFileName(self,"Abrir",str(Path.home()))
  if p:
   try:self.path=Path(p);self.edit.setPlainText(self.path.read_text(encoding="utf-8"));self.edit.document().setModified(False)
   except OSError as e:QMessageBox.warning(self,"Erro",str(e))
 def save(self):
  if not self.path:
   p,_=QFileDialog.getSaveFileName(self,"Salvar",str(Path.home()/"sem-titulo.txt"))
   if not p:return
   self.path=Path(p)
  try:self.path.write_text(self.edit.toPlainText(),encoding="utf-8");self.edit.document().setModified(False)
  except OSError as e:QMessageBox.warning(self,"Erro",str(e))

OPS={ast.Add:operator.add,ast.Sub:operator.sub,ast.Mult:operator.mul,ast.Div:operator.truediv,ast.Pow:operator.pow,ast.USub:operator.neg}
def safe_calc(expression):
 if len(expression)>100:raise ValueError("Expressao muito longa")
 def visit(n):
  if isinstance(n,ast.Expression):return visit(n.body)
  if isinstance(n,ast.Constant) and type(n.value) in (int,float):return n.value
  if isinstance(n,ast.UnaryOp) and type(n.op) in OPS:return OPS[type(n.op)](visit(n.operand))
  if isinstance(n,ast.BinOp) and type(n.op) in OPS:
   a,b=visit(n.left),visit(n.right)
   if isinstance(n.op,ast.Pow) and abs(b)>8:raise ValueError("Expoente muito alto")
   v=OPS[type(n.op)](a,b)
   if abs(v)>1e100:raise ValueError("Resultado fora do limite")
   return v
  raise ValueError("Operacao nao permitida")
 return visit(ast.parse(expression,mode="eval"))

class Calculator(QWidget):
 def __init__(self):
  super().__init__();self.setWindowTitle("Calculadora");l=QVBoxLayout(self);self.display=QLineEdit();l.addWidget(self.display)
  grid=QWidget();from PyQt6.QtWidgets import QGridLayout
  g=QGridLayout(grid);l.addWidget(grid)
  for i,k in enumerate(["7","8","9","/","4","5","6","*","1","2","3","-","0",".","C","+","(",")","**","="]):
   b=QPushButton(k);b.clicked.connect(lambda checked=False,key=k:self.press(key));g.addWidget(b,i//4,i%4)
 def press(self,k):
  if k=="C":self.display.clear()
  elif k=="=":
   try:self.display.setText(str(safe_calc(self.display.text())))
   except Exception as e:QMessageBox.warning(self,"Calculo",str(e))
  else:self.display.setText(self.display.text()+k)

class MediaWindow(QMainWindow):
 def __init__(self,kind):
  super().__init__();self.kind=kind;self.setWindowTitle({"music":"Musica","video":"Videos","photos":"Fotos"}[kind]);self.resize(780,540)
  root=QWidget();l=QVBoxLayout(root);self.setCentralWidget(root)
  self.info=QLabel("Abra arquivos locais do computador");l.addWidget(self.info)
  self.player=QMediaPlayer(self);self.audio=QAudioOutput(self);self.player.setAudioOutput(self.audio)
  if kind=="video":
   self.video=QVideoWidget();l.addWidget(self.video);self.player.setVideoOutput(self.video)
  if kind=="photos":
   from PyQt6.QtWidgets import QLabel as QL
   self.preview=QL("Nenhuma imagem selecionada");self.preview.setScaledContents(True);l.addWidget(self.preview)
  row=QHBoxLayout();l.addLayout(row)
  for label,fn in [("Abrir arquivo",self.open_file),("Reproduzir",self.player.play),("Pausar",self.player.pause),("Parar",self.player.stop)]:
   b=QPushButton(label);b.clicked.connect(fn);row.addWidget(b)
  volume=QSlider();volume.setOrientation(__import__("PyQt6.QtCore",fromlist=["Qt"]).Qt.Orientation.Horizontal);volume.setRange(0,100);volume.setValue(75);volume.valueChanged.connect(lambda v:self.audio.setVolume(v/100));l.addWidget(volume)
 def open_file(self):
  filt={"music":"Audio (*.mp3 *.wav *.ogg *.flac *.m4a)","video":"Video (*.mp4 *.mkv *.webm *.mov)","photos":"Imagens (*.png *.jpg *.jpeg *.webp *.bmp)"}[self.kind]
  p,_=QFileDialog.getOpenFileName(self,"Selecionar arquivo",str(Path.home()),filt)
  if not p:return
  self.info.setText(Path(p).name)
  if self.kind=="photos":
   from PyQt6.QtGui import QPixmap
   self.preview.setPixmap(QPixmap(p))
  else:self.player.setSource(QUrl.fromLocalFile(p));self.player.play()

class Files(QMainWindow):
 def __init__(self):
  super().__init__();self.setWindowTitle("Meus arquivos");self.resize(850,560);self.current=Path.home()
  root=QWidget();l=QVBoxLayout(root);self.setCentralWidget(root)
  row=QHBoxLayout();l.addLayout(row);self.path=QLineEdit(str(self.current));row.addWidget(self.path)
  for label,fn in [("Abrir",self.go),("Voltar",self.back),("Nova pasta",self.mkdir),("Excluir",self.delete)]:
   b=QPushButton(label);b.clicked.connect(fn);row.addWidget(b)
  self.list=QListWidget();l.addWidget(self.list);self.list.itemDoubleClicked.connect(self.enter);self.refresh()
 def refresh(self):
  self.path.setText(str(self.current));self.list.clear()
  try:
   for p in sorted(self.current.iterdir(),key=lambda x:(not x.is_dir(),x.name.lower())):self.list.addItem(("📁 " if p.is_dir() else "📄 ")+p.name)
  except OSError as e:QMessageBox.warning(self,"Arquivos",str(e))
 def go(self):
  p=Path(self.path.text()).expanduser()
  if p.is_dir():self.current=p.resolve();self.refresh()
 def back(self):
  if self.current.parent!=self.current:self.current=self.current.parent;self.refresh()
 def enter(self,item):
  name=item.text()[2:];p=self.current/name
  if p.is_dir():self.current=p;self.refresh()
  elif p.is_file():subprocess.Popen(["xdg-open",str(p)])
 def mkdir(self):
  from PyQt6.QtWidgets import QInputDialog
  name,ok=QInputDialog.getText(self,"Nova pasta","Nome:")
  if ok and name and "/" not in name and name not in (".",".."):
   try:(self.current/name).mkdir();self.refresh()
   except OSError as e:QMessageBox.warning(self,"Erro",str(e))
 def delete(self):
  item=self.list.currentItem()
  if not item:return
  p=self.current/item.text()[2:]
  if p.is_symlink() or p.resolve()==Path.home().resolve() or Path.home().resolve() not in p.resolve().parents:
   QMessageBox.warning(self,"Protecao","Este caminho nao pode ser excluido por aqui.");return
  if QMessageBox.question(self,"Enviar para lixeira",f"Enviar {p.name} para a lixeira?")!=QMessageBox.StandardButton.Yes:return
  subprocess.run(["gio","trash",str(p)],check=False);self.refresh()

class Browser(QMainWindow):
 def __init__(self):
  super().__init__();self.setWindowTitle("Navegador LeapOS");self.resize(1000,700)
  root=QWidget();l=QVBoxLayout(root);self.setCentralWidget(root);row=QHBoxLayout();l.addLayout(row)
  self.url=QLineEdit("https://www.google.com");row.addWidget(self.url);b=QPushButton("Abrir");b.clicked.connect(self.go);row.addWidget(b)
  try:
   from PyQt6.QtWebEngineWidgets import QWebEngineView
   self.view=QWebEngineView();l.addWidget(self.view);self.go()
  except ImportError:l.addWidget(QLabel("Componente WebEngine nao instalado. Use o navegador do sistema."));b.clicked.connect(lambda:subprocess.Popen(["xdg-open",self.url.text()]))
 def go(self):
  target=self.url.text().strip()
  if not target.startswith(("https://","http://")):target="https://"+target
  if hasattr(self,"view"):self.view.setUrl(QUrl(target))

class AppCatalog(QMainWindow):
 def __init__(self):
  super().__init__();self.setWindowTitle("Aplicativos LeapOS");self.resize(850,560);root=QWidget();l=QVBoxLayout(root);self.setCentralWidget(root)
  l.addWidget(QLabel("Aplicativos e serviços integrados ao LeapOS"))
  self.list=QListWidget();l.addWidget(self.list);self.apps=load_apps()
  for a in self.apps:self.list.addItem(f"{a['name']} — {a.get('description','')}")
  b=QPushButton("Abrir aplicativo selecionado");b.clicked.connect(self.open_selected);l.addWidget(b)
  self.list.itemDoubleClicked.connect(lambda _:self.open_selected())
 def open_selected(self):
  i=self.list.currentRow()
  if i<0:return
  app=self.apps[i];url=app["url"]
  try:
   from PyQt6.QtWebEngineWidgets import QWebEngineView
   w=QMainWindow();w.setWindowTitle("LeapOS — "+app["name"]);w.resize(1200,800);v=QWebEngineView();v.setUrl(QUrl(url));w.setCentralWidget(v);w.show();self._child=w
  except ImportError:subprocess.Popen(["xdg-open",url])
