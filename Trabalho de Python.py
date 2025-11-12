import tkinter as tk
from tkinter import filedialog, messagebox
import PyPDF2
import requests
import re

def escolher_pdf():
    caminho_pdf = filedialog.askopenfilename(filetypes=[("Arquivos PDF", "*.pdf")])
    if not caminho_pdf:
        return
    
    try:
        with open(caminho_pdf, "rb") as f:
            leitor = PyPDF2.PdfReader(f)
            texto = ""
            for pagina in leitor.pages:
                texto += pagina.extract_text()
    except Exception as e:
        messagebox.showerror("Erro", f"Não foi possível ler o PDF:\n{e}")
        return

    datas = re.findall(r"\d{4}-\d{2}-\d{2}", texto)
    if not datas:
        messagebox.showinfo("Aviso", "Nenhuma data encontrada no PDF.")
        return

    resultado = verificar_feriados(datas)
    exibir_resultado(resultado)

def verificar_feriados(datas):
    url = "https://date.nager.at/api/v3/PublicHolidays/2025/BR"
    try:
        resposta = requests.get(url)
        resposta.raise_for_status()
        feriados = resposta.json()
        feriados_lista = [f["date"] for f in feriados]
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao acessar a API:\n{e}")
        return {}

    resultado = {}
    for data in datas:
        resultado[data] = "Feriado" if data in feriados_lista else "Dia comum"
    return resultado

def exibir_resultado(resultado):
    texto_resultado.delete("1.0", tk.END)
    for data, status in resultado.items():
        texto_resultado.insert(tk.END, f"{data}: {status}\n")

# Interface principal
janela = tk.Tk()
janela.title("Verificador de Feriados")
janela.geometry("400x400")
janela.resizable(False, False)

titulo = tk.Label(janela, text="Selecione um arquivo PDF com datas", font=("Arial", 12))
titulo.pack(pady=10)

botao_pdf = tk.Button(janela, text="Escolher PDF", command=escolher_pdf, bg="#4CAF50", fg="white", width=20)
botao_pdf.pack(pady=10)

texto_resultado = tk.Text(janela, height=15, width=45)
texto_resultado.pack(pady=10)

janela.mainloop()
