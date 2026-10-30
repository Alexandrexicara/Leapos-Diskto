import os, shutil, subprocess, tarfile, tkinter as tk
from tkinter import ttk,messagebox,filedialog
from pathlib import Path
from .cleaner import analyze,clean_selected
H=Path.home()
class App(tk.Tk):
 def __init__(self):
  super().__init__(); self.title('LeapOS | Central do Sistema'); self.geometry('850x580'); self.minsize(680,460)
  self.tabs=ttk.Notebook(self); self.tabs.pack(fill='both',expand=True,padx=12,pady=12)
  self.clean_page(); self.monitor_page(); self.trash_page(); self.start_page(); self.backup_page()
 def page(self,title):
  f=ttk.Frame(self.tabs,padding=16); self.tabs.add(f,text=title); return f
 def clean_page(self):
  f=self.page('Limpeza'); ttk.Label(f,text='Limpeza segura de caches',font=('Arial',17,'bold')).pack(anchor='w')
  ttk.Label(f,text='Nao remove documentos, downloads, cookies, senhas, historico ou perfis.').pack(anchor='w',pady=8)
  self.lst=tk.Listbox(f,selectmode=tk.MULTIPLE); self.lst.pack(fill='both',expand=True,pady=8)
  ttk.Button(f,text='Analisar',command=self.refresh).pack(side='left'); ttk.Button(f,text='Limpar selecionados',command=self.clean).pack(side='right'); self.refresh()
 def refresh(self):
  self.lst.delete(0,tk.END); self.rows=analyze()
  for p,n in self.rows: self.lst.insert(tk.END,f'{p} — {n/1048576:.1f} MB')
 def clean(self):
  ids=self.lst.curselection()
  if not ids: return
  chosen=[self.rows[i][0] for i in ids]; estimate=sum(self.rows[i][1] for i in ids)
  if messagebox.askyesno('Confirmar',f'Ate {estimate/1048576:.1f} MB. Deseja limpar os caches?'):
   try: n=clean_selected(chosen); messagebox.showinfo('Concluido',f'{n/1048576:.1f} MB liberados')
   except Exception as e: messagebox.showerror('Cancelado',str(e))
  self.refresh()
 def monitor_page(self):
  f=self.page('Monitor'); ttk.Label(f,text='Informacoes do sistema',font=('Arial',17,'bold')).pack(anchor='w')
  self.info=tk.Text(f); self.info.pack(fill='both',expand=True,pady=8); ttk.Button(f,text='Atualizar',command=self.monitor).pack(anchor='e'); self.monitor()
 def monitor(self):
  d=shutil.disk_usage(H); lines=[f'CPU logica: {os.cpu_count()}',f'Disco livre: {d.free/1073741824:.1f} GB / {d.total/1073741824:.1f} GB']
  try: lines+=Path('/proc/meminfo').read_text().splitlines()[:5]
  except OSError: pass
  self.info.delete('1.0',tk.END); self.info.insert(tk.END,'\n'.join(lines))
 def trash_page(self):
  f=self.page('Lixeira'); ttk.Label(f,text='Lixeira do usuario',font=('Arial',17,'bold')).pack(anchor='w')
  ttk.Label(f,text='A lixeira e gerenciada pelo GVFS/Thunar. O LeapOS nao a esvazia automaticamente.').pack(anchor='w',pady=12)
  ttk.Button(f,text='Abrir lixeira',command=lambda:self.run(['xdg-open','trash:///'])).pack(anchor='w')
  ttk.Button(f,text='Abrir gerenciador de arquivos',command=lambda:self.run(['thunar'])).pack(anchor='w',pady=8)
 def start_page(self):
  f=self.page('Inicializacao'); ttk.Label(f,text='Inicializacao do usuario',font=('Arial',17,'bold')).pack(anchor='w')
  self.aut=H/'.config/autostart'; self.box=tk.Listbox(f); self.box.pack(fill='both',expand=True,pady=8)
  ttk.Button(f,text='Abrir pasta de inicializacao',command=lambda:self.open(self.aut)).pack(anchor='e'); self.aut.mkdir(parents=True,exist_ok=True)
  for p in self.aut.glob('*.desktop'): self.box.insert(tk.END,p.name)
 def backup_page(self):
  f=self.page('Backup'); ttk.Label(f,text='Backup de configuracoes',font=('Arial',17,'bold')).pack(anchor='w')
  ttk.Label(f,text='Exporta configuracoes do XFCE e Thunar, sem documentos ou credenciais.').pack(anchor='w',pady=8)
  ttk.Button(f,text='Exportar configuracoes',command=self.backup).pack(anchor='w')
 def backup(self):
  dest=filedialog.asksaveasfilename(defaultextension='.tar.gz',filetypes=[('Backup','*.tar.gz')])
  if not dest:return
  try:
   with tarfile.open(dest,'w:gz') as t:
    for p in [H/'.config/xfce4',H/'.config/Thunar',H/'.config/gtk-3.0']:
     if p.exists() and not p.is_symlink(): t.add(p,arcname=p.relative_to(H))
   messagebox.showinfo('Backup','Configuracoes exportadas')
  except Exception as e: messagebox.showerror('Erro',str(e))
 def open(self,p): p.mkdir(parents=True,exist_ok=True); self.run(['xdg-open',str(p)])
 def run(self,c):
  try: subprocess.Popen(c)
  except Exception as e: messagebox.showerror('Erro',str(e))
def main(): App().mainloop()
