"""Central de ferramentas do LeapOS em portugues."""
import os
import shutil
import subprocess
import tarfile
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
from .cleaner import analyze, clean_selected

HOME = Path.home()

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("LeapOS | Central do Sistema")
        self.geometry("900x620")
        self.minsize(720, 500)
        self.configure(bg="#111c2e")
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background="#192941")
        style.configure("TLabel", background="#192941", foreground="#f4f7ff")
        style.configure("TButton", padding=8)
        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill="both", expand=True, padx=14, pady=14)
        self.build_clean()
        self.build_trash()
        self.build_monitor()
        self.build_startup()
        self.build_updates()
        self.build_backup()

    def page(self, title):
        frame = ttk.Frame(self.tabs, padding=18)
        self.tabs.add(frame, text=title)
        return frame

    def build_clean(self):
        f = self.page("Limpeza")
        ttk.Label(f, text="Central de limpeza segura", font=("Arial", 18, "bold")).pack(anchor="w")
        ttk.Label(f, text="Somente caches conhecidos. Documentos, downloads, senhas, cookies, historico e perfis ficam preservados.").pack(anchor="w", pady=8)
        self.cache = tk.Listbox(f, selectmode=tk.MULTIPLE, height=15)
        self.cache.pack(fill="both", expand=True, pady=8)
        ttk.Button(f, text="Analisar", command=self.refresh_cache).pack(side="left")
        ttk.Button(f, text="Limpar selecionados", command=self.clean_cache).pack(side="right")
        self.refresh_cache()

    def refresh_cache(self):
        self.cache.delete(0, tk.END)
        self.cache_rows = analyze()
        for path, size in self.cache_rows:
            self.cache.insert(tk.END, f"{path} — {size / 1048576:.1f} MB")

    def clean_cache(self):
        indexes = self.cache.curselection()
        if not indexes:
            messagebox.showinfo("LeapOS", "Selecione uma categoria.")
            return
        selected = [self.cache_rows[i][0] for i in indexes]
        estimate = sum(self.cache_rows[i][1] for i in indexes)
        if not messagebox.askyesno("Confirmar", f"Foram encontrados ate {estimate / 1048576:.1f} MB. Limpar os caches selecionados?"):
            return
        try:
            freed = clean_selected(selected)
            messagebox.showinfo("Limpeza concluida", f"Espaco liberado: {freed / 1048576:.1f} MB")
        except Exception as exc:
            messagebox.showerror("Limpeza cancelada", str(exc))
        self.refresh_cache()

    def build_trash(self):
        f = self.page("Lixeira")
        ttk.Label(f, text="Lixeira do usuario", font=("Arial", 18, "bold")).pack(anchor="w")
        ttk.Label(f, text="A lixeira usa o servico padrao do ambiente grafico. Restauracao e exclusao definitiva podem ser feitas no gerenciador de arquivos.").pack(anchor="w", pady=12)
        ttk.Button(f, text="Abrir lixeira", command=lambda: self.run(["xdg-open", "trash:///"])).pack(anchor="w", pady=6)
        ttk.Button(f, text="Abrir gerenciador de arquivos", command=lambda: self.run(["thunar"])).pack(anchor="w", pady=6)
        ttk.Label(f, text="A lixeira nao e esvaziada automaticamente pelo LeapOS.").pack(anchor="w", pady=12)

    def build_monitor(self):
        f = self.page("Monitor")
        ttk.Label(f, text="Informacoes do sistema", font=("Arial", 18, "bold")).pack(anchor="w")
        self.monitor = tk.Text(f, height=20, wrap="word")
        self.monitor.pack(fill="both", expand=True, pady=10)
        ttk.Button(f, text="Atualizar", command=self.refresh_monitor).pack(anchor="e")
        self.refresh_monitor()

    def refresh_monitor(self):
        lines = [f"Processadores logicos: {os.cpu_count() or 'indisponivel'}"]
        disk = shutil.disk_usage(HOME)
        lines.append(f"Disco da pasta pessoal: {disk.free / 1073741824:.1f} GB livres de {disk.total / 1073741824:.1f} GB")
        try:
            lines.extend(["", "Memoria:"] + Path("/proc/meminfo").read_text().splitlines()[:5])
        except OSError:
            pass
        try:
            import psutil
            lines += ["", f"CPU em uso: {psutil.cpu_percent(interval=0.3):.1f}%", f"RAM em uso: {psutil.virtual_memory().percent:.1f}%", "", "Processos ativos (PID | nome):"]
            lines += [f"{p.info['pid']} | {p.info.get('name')}" for p in psutil.process_iter(["pid", "name"])][:60]
        except Exception:
            lines.append("Instale python3-psutil para lista detalhada de processos.")
        self.monitor.delete("1.0", tk.END)
        self.monitor.insert(tk.END, "\n".join(lines))

    def build_startup(self):
        f = self.page("Inicializacao")
        ttk.Label(f, text="Aplicativos da inicializacao do usuario", font=("Arial", 18, "bold")).pack(anchor="w")
        self.autostart = HOME / ".config" / "autostart"
        self.start_list = tk.Listbox(f, height=16)
        self.start_list.pack(fill="both", expand=True, pady=10)
        ttk.Button(f, text="Atualizar lista", command=self.refresh_startup).pack(side="left")
        ttk.Button(f, text="Abrir pasta", command=lambda: self.open_path(self.autostart)).pack(side="right")
        self.refresh_startup()

    def refresh_startup(self):
        self.start_list.delete(0, tk.END)
        self.autostart.mkdir(parents=True, exist_ok=True)
        entries = list(self.autostart.glob("*.desktop"))
        for p in entries:
            self.start_list.insert(tk.END, p.name)
        if not entries:
            self.start_list.insert(tk.END, "Nenhum aplicativo personalizado.")

    def build_updates(self):
        f = self.page("Atualizacoes")
        ttk.Label(f, text="Atualizacoes do sistema", font=("Arial", 18, "bold")).pack(anchor="w")
        ttk.Label(f, text="O Debian solicita autorizacao administrativa antes de instalar atualizacoes.").pack(anchor="w", pady=10)
        ttk.Button(f, text="Abrir atualizador grafico", command=lambda: self.run(["pkexec", "xfce4-terminal", "--command", "apt update && apt upgrade"])).pack(anchor="w")
        ttk.Label(f, text="Se o atualizador nao estiver disponivel, use o gerenciador de atualizacoes do XFCE.").pack(anchor="w", pady=10)

    def build_backup(self):
        f = self.page("Backup")
        ttk.Label(f, text="Backup de configuracoes", font=("Arial", 18, "bold")).pack(anchor="w")
        ttk.Label(f, text="Exporta apenas configuracoes selecionadas do ambiente. Nao inclui documentos, senhas ou chaves privadas.").pack(anchor="w", pady=10)
        ttk.Button(f, text="Exportar configuracoes", command=self.backup).pack(anchor="w")

    def backup(self):
        destination = filedialog.asksaveasfilename(defaultextension=".tar.gz", filetypes=[("Backup compactado", "*.tar.gz")])
        if not destination:
            return
        folders = [HOME / ".config/xfce4", HOME / ".config/Thunar", HOME / ".config/gtk-3.0"]
        try:
            with tarfile.open(destination, "w:gz") as archive:
                for folder in folders:
                    if folder.exists() and not folder.is_symlink():
                        archive.add(folder, arcname=folder.relative_to(HOME))
            messagebox.showinfo("LeapOS", "Configuracoes exportadas.")
        except Exception as exc:
            messagebox.showerror("Erro no backup", str(exc))

    def open_path(self, path):
        path.mkdir(parents=True, exist_ok=True)
        self.run(["xdg-open", str(path)])

    def run(self, command):
        try:
            subprocess.Popen(command)
        except Exception as exc:
            messagebox.showerror("Nao foi possivel abrir", str(exc))

def main():
    App().mainloop()
