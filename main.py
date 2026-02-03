import csv
import customtkinter as ctk
from tkinter import messagebox
from datetime import date

# Configurações de Aparência
ctk.set_appearance_mode("System")  # Segue o tema do Windows (Dark ou Light)
ctk.set_default_color_theme("blue")

PERGUNTAS_FILE = "perguntas.csv"
RESPOSTAS_FILE = "respostas.csv"

class RelatorioApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Relatório Diário do Gerente")
        self.geometry("800x700")

        self.perguntas = []
        self.entradas = {}

        self.carregar_perguntas()
        self.criar_layout()

    def carregar_perguntas(self):
        # Fallback caso o arquivo não exista para teste
        try:
            with open(PERGUNTAS_FILE, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                self.perguntas = list(reader)
        except FileNotFoundError:
            self.perguntas = [{"id": "0", "pergunta": "Exemplo: Como foi o movimento?"}]

    def criar_layout(self):
        # Grid layout para a janela principal
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Cabeçalho
        self.header_frame = ctk.CTkFrame(self, corner_radius=0, height=80)
        self.header_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        
        self.label_titulo = ctk.CTkLabel(
            self.header_frame, 
            text="📋 Relatório Diário do Gerente", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.label_titulo.pack(pady=20)

        # Container Principal com Scroll nativo do CustomTkinter
        self.scrollable_frame = ctk.CTkScrollableFrame(self, label_text="Formulário de Respostas")
        self.scrollable_frame.grid(row=1, column=0, padx=20, pady=(10, 0), sticky="nsew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        self.criar_formulario()

        # Botão de Ação (Footer)
        self.btn_salvar = ctk.CTkButton(
            self,
            text="SALVAR E GERAR WHATSAPP",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=50,
            command=self.salvar
        )
        self.btn_salvar.grid(row=2, column=0, padx=20, pady=20, sticky="ew")

    def criar_formulario(self):
        for p in self.perguntas:
            # Container de cada pergunta
            bloco = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
            bloco.pack(fill="x", pady=10, padx=5)

            label = ctk.CTkLabel(
                bloco,
                text=p["pergunta"],
                font=ctk.CTkFont(size=13, weight="bold"),
                wraplength=700,
                justify="left"
            )
            label.pack(anchor="w", pady=(0, 5))

            # Usando TextBox para respostas longas ou Entry para curtas
            entry = ctk.CTkEntry(
                bloco, 
                placeholder_text="Digite sua resposta aqui...",
                height=35
            )
            entry.pack(fill="x")

            self.entradas[p["id"]] = entry

    def salvar(self):
        hoje = date.today().isoformat()
        respostas = {"Data": hoje}

        for p in self.perguntas:
            respostas[p["pergunta"]] = self.entradas[p["id"]].get()

        # Lógica de CSV mantida
        try:
            arquivo_existe = False
            try:
                with open(RESPOSTAS_FILE, "r", encoding="utf-8"): arquivo_existe = True
            except FileNotFoundError: pass

            with open(RESPOSTAS_FILE, "a", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=respostas.keys())
                if not arquivo_existe:
                    writer.writeheader()
                writer.writerow(respostas)

            texto_wa = self.gerar_texto_whatsapp(respostas)
            self.abrir_janela_sucesso(texto_wa)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar: {e}")

    def gerar_texto_whatsapp(self, r):
        texto = f"*📋 Relatório Diário – {r['Data']}*\n\n"
        for chave, valor in r.items():
            if chave != "Data":
                texto += f"• *{chave}:* {valor}\n"
        return texto

    def abrir_janela_sucesso(self, texto):
        # Janela popup moderna
        janela = ctk.CTkToplevel(self)
        janela.title("Relatório Gerado")
        janela.geometry("500x550")
        janela.attributes("-topmost", True) # Ficar na frente

        lbl = ctk.CTkLabel(janela, text="Texto para WhatsApp:", font=ctk.CTkFont(weight="bold"))
        lbl.pack(pady=(20, 5))

        txt_box = ctk.CTkTextbox(janela, width=450, height=350)
        txt_box.pack(padx=20, pady=10)
        txt_box.insert("1.0", texto)

        def copiar():
            self.clipboard_clear()
            self.clipboard_append(texto)
            messagebox.showinfo("Copiado", "Texto copiado para o WhatsApp!")

        btn_copy = ctk.CTkButton(janela, text="COPIAR TEXTO", fg_color="#25D366", hover_color="#128C7E", command=copiar)
        btn_copy.pack(pady=20)

if __name__ == "__main__":
    app = RelatorioApp()
    app.mainloop()