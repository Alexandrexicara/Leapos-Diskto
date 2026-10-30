"""Assistente LeapOS com NVIDIA NIM e fala ElevenLabs."""
import os,requests,subprocess,shutil,tempfile
from pathlib import Path
from dotenv import load_dotenv
from PyQt6.QtCore import QThread,pyqtSignal
from PyQt6.QtWidgets import QMainWindow,QWidget,QVBoxLayout,QHBoxLayout,QTextEdit,QLineEdit,QPushButton,QLabel,QMessageBox
ROOT=Path(__file__).resolve().parents[2]
load_dotenv(ROOT/".env")
class Worker(QThread):
 done=pyqtSignal(str);fail=pyqtSignal(str)
 def __init__(self,messages):super().__init__();self.messages=messages
 def run(self):
  key=os.getenv("NVIDIA_API_KEY","").strip();model=os.getenv("NVIDIA_MODEL","openai/gpt-oss-20b").strip()
  if not key:self.fail.emit("Configure NVIDIA_API_KEY no arquivo .env.");return
  try:
   r=requests.post(os.getenv("NVIDIA_BASE_URL","https://integrate.api.nvidia.com/v1").rstrip("/")+"/chat/completions",headers={"Authorization":"Bearer "+key,"Content-Type":"application/json"},json={"model":model,"messages":self.messages,"temperature":0.3,"max_tokens":1000},timeout=(10,60));r.raise_for_status()
   answer=r.json()["choices"][0]["message"]["content"]
   if not isinstance(answer,str) or not answer.strip():raise ValueError()
   self.done.emit(answer.strip())
  except requests.Timeout:self.fail.emit("A NVIDIA demorou para responder.")
  except requests.RequestException as e:self.fail.emit(f"Falha na NVIDIA (HTTP {getattr(e.response,'status_code','rede')}). Verifique modelo, chave e conexao.")
  except Exception:self.fail.emit("Resposta inesperada da NVIDIA.")
class Assistant(QMainWindow):
 def __init__(self):
  super().__init__();self.setWindowTitle("Assistente Leap");self.resize(760,600);self.history=[{"role":"system","content":"Voce e o Assistente LeapOS. Responda em portugues brasileiro. Seja claro, seguro e honesto; nao diga que executou acoes no computador."}];root=QWidget();l=QVBoxLayout(root);self.setCentralWidget(root)
  self.status=QLabel("Assistente LeapOS · NVIDIA NIM");l.addWidget(self.status);self.chat=QTextEdit();self.chat.setReadOnly(True);l.addWidget(self.chat)
  row=QHBoxLayout();l.addLayout(row);self.prompt=QLineEdit();self.prompt.setPlaceholderText("Pergunte ao Assistente Leap...");self.prompt.returnPressed.connect(self.send);row.addWidget(self.prompt)
  b=QPushButton("Enviar");b.clicked.connect(self.send);row.addWidget(b);self.send_button=b
  v=QPushButton("Ouvir ultima resposta");v.clicked.connect(self.speak);l.addWidget(v);self.last=""
 def send(self):
  q=self.prompt.text().strip()
  if not q:return
  self.prompt.clear();self.history.append({"role":"user","content":q});self.chat.append("Voce: "+q);self.send_button.setEnabled(False);self.status.setText("Consultando NVIDIA...")
  self.worker=Worker(self.history[-17:]);self.worker.done.connect(self.answer);self.worker.fail.connect(self.error);self.worker.start()
 def answer(self,a):
  self.last=a;self.history.append({"role":"assistant","content":a});self.chat.append("Leap: "+a+"\n");self.status.setText("Pronto");self.send_button.setEnabled(True)
 def error(self,e):self.chat.append("Leap: "+e);self.status.setText("Aguardando");self.send_button.setEnabled(True)
 def speak(self):
  key=os.getenv("ELEVENLABS_API_KEY","");voice=os.getenv("ELEVENLABS_VOICE_ID","")
  if not self.last:QMessageBox.information(self,"Voz","Ainda nao ha resposta.");return
  if not key or not voice:QMessageBox.information(self,"Voz","Configure ELEVENLABS_API_KEY e ELEVENLABS_VOICE_ID no .env.");return
  try:
   r=requests.post(f"https://api.elevenlabs.io/v1/text-to-speech/{voice}",headers={"xi-api-key":key,"Content-Type":"application/json"},json={"text":self.last[:4000],"model_id":"eleven_multilingual_v2"},timeout=45);r.raise_for_status()
   player=shutil.which("ffplay")
   if not player:raise RuntimeError("Instale ffmpeg para reproduzir o audio.")
   with tempfile.NamedTemporaryFile(suffix=".mp3",delete=False) as f:f.write(r.content);p=f.name
   try:subprocess.run([player,"-nodisp","-autoexit","-loglevel","error",p],timeout=90,check=False)
   finally:Path(p).unlink(missing_ok=True)
  except Exception as e:QMessageBox.warning(self,"Voz",str(e))
