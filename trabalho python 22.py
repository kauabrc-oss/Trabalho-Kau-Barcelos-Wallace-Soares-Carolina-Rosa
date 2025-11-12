import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import requests
import PyPDF2
import re
from datetime import datetime

class PDFHolidayChecker:
    def __init__(self, root):
        self.root = root
        self.root.title("Verificador de Feriados em PDF")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Frame principal
        main_frame = tk.Frame(root, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = tk.Label(main_frame, text="Verificador de Feriados em PDF", 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Botão para selecionar arquivo
        self.select_button = tk.Button(main_frame, text="Selecionar Arquivo PDF", 
                                      command=self.select_pdf_file,
                                      font=("Arial", 12), bg="#4CAF50", fg="white")
        self.select_button.pack(pady=10)
        
        # Label para mostrar arquivo selecionado
        self.file_label = tk.Label(main_frame, text="Nenhum arquivo selecionado", 
                                  font=("Arial", 10), wraplength=500)
        self.file_label.pack(pady=5)
        
        # Área de texto para resultados
        self.result_text = scrolledtext.ScrolledText(main_frame, height=15, 
                                                   font=("Arial", 10),
                                                   state=tk.DISABLED)
        self.result_text.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Frame para botões
        button_frame = tk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        # Botão para processar
        self.process_button = tk.Button(button_frame, text="Verificar Feriados", 
                                       command=self.process_pdf,
                                       font=("Arial", 12), bg="#2196F3", fg="white",
                                       state=tk.DISABLED)
        self.process_button.pack(side=tk.LEFT, padx=5)
        
        # Botão para limpar
        self.clear_button = tk.Button(button_frame, text="Limpar", 
                                     command=self.clear_results,
                                     font=("Arial", 12), bg="#FF9800", fg="white")
        self.clear_button.pack(side=tk.LEFT, padx=5)
        
        self.selected_file = None
        self.holidays_cache = {}  # Cache para feriados por ano

    def select_pdf_file(self):
        """Seleciona um arquivo PDF"""
        file_path = filedialog.askopenfilename(
            title="Selecione um arquivo PDF",
            filetypes=[("PDF files", "*.pdf"), ("Todos os arquivos", "*.*")]
        )
        
        if file_path:
            self.selected_file = file_path
            self.file_label.config(text=f"Arquivo selecionado: {file_path}")
            self.process_button.config(state=tk.NORMAL)
            self.clear_results()

    def clear_results(self):
        """Limpa os resultados"""
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.result_text.config(state=tk.DISABLED)

    def extract_dates_from_text(self, text):
        """Extrai datas do texto usando expressões regulares"""
        # Padrões de data (dd/mm/aaaa, dd-mm-aaaa, etc.)
        date_patterns = [
            r'\b\d{1,2}/\d{1,2}/\d{4}\b',  # dd/mm/aaaa
            r'\b\d{1,2}-\d{1,2}-\d{4}\b',  # dd-mm-aaaa
            r'\b\d{4}-\d{1,2}-\d{1,2}\b',  # aaaa-mm-dd
        ]
        
        dates = []
        for pattern in date_patterns:
            found_dates = re.findall(pattern, text)
            dates.extend(found_dates)
        
        return list(set(dates))  # Remove duplicatas

    def normalize_date(self, date_str):
        """Normaliza a data para o formato aaaa-mm-dd"""
        try:
            # Tenta diferentes formatos
            formats = ['%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d']
            
            for fmt in formats:
                try:
                    date_obj = datetime.strptime(date_str, fmt)
                    return date_obj.strftime('%Y-%m-%d')
                except ValueError:
                    continue
        except:
            pass
        
        return None

    def get_holidays_for_year(self, year):
        """Obtém feriados para um ano específico da API"""
        if year in self.holidays_cache:
            return self.holidays_cache[year]
        
        try:
            url = f"https://date.nager.at/api/v3/PublicHolidays/{year}/BR"
            response = requests.get(url, headers={'accept': 'application/json'})
            
            if response.status_code == 200:
                holidays = response.json()
                self.holidays_cache[year] = holidays
                return holidays
            else:
                messagebox.showerror("Erro", f"Erro ao buscar feriados: {response.status_code}")
                return []
        except Exception as e:
            messagebox.showerror("Erro", f"Erro na conexão: {str(e)}")
            return []

    def process_pdf(self):
        """Processa o PDF e verifica feriados"""
        if not self.selected_file:
            messagebox.showwarning("Aviso", "Por favor, selecione um arquivo PDF primeiro.")
            return
        
        try:
            # Limpa resultados anteriores
            self.clear_results()
            
            # Lê o PDF
            reader = PyPDF2.PdfReader(self.selected_file)
            full_text = ""
            
            for page in reader.pages:
                full_text += page.extract_text()
            
            # Extrai datas
            dates = self.extract_dates_from_text(full_text)
            
            if not dates:
                self.display_result("Nenhuma data encontrada no PDF.")
                return
            
            # Verifica quais datas são feriados
            holiday_dates = []
            
            for date_str in dates:
                normalized_date = self.normalize_date(date_str)
                if normalized_date:
                    year = normalized_date.split('-')[0]
                    holidays = self.get_holidays_for_year(year)
                    
                    for holiday in holidays:
                        if holiday['date'] == normalized_date:
                            holiday_dates.append({
                                'original_date': date_str,
                                'normalized_date': normalized_date,
                                'holiday_name': holiday['name']
                            })
                            break
            
            # Exibe resultados
            self.display_results(dates, holiday_dates)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao processar PDF: {str(e)}")

    def display_result(self, message):
        """Exibe uma mensagem simples"""
        self.result_text.config(state=tk.NORMAL)
        self.result_text.insert(tk.END, message + "\n")
        self.result_text.config(state=tk.DISABLED)

    def display_results(self, all_dates, holiday_dates):
        """Exibe os resultados da verificação"""
        self.result_text.config(state=tk.NORMAL)
        
        self.result_text.insert(tk.END, "=== RESULTADOS DA VERIFICAÇÃO ===\n\n")
        
        self.result_text.insert(tk.END, f"Total de datas encontradas no PDF: {len(all_dates)}\n")
        self.result_text.insert(tk.END, f"Datas que são feriados: {len(holiday_dates)}\n\n")
        
        if holiday_dates:
            self.result_text.insert(tk.END, "FERIADOS ENCONTRADOS:\n")
            self.result_text.insert(tk.END, "-" * 50 + "\n")
            
            for holiday in holiday_dates:
                self.result_text.insert(tk.END, 
                    f"Data: {holiday['original_date']} → {holiday['holiday_name']}\n")
        
        self.result_text.insert(tk.END, "\n" + "=" * 50 + "\n")
        self.result_text.insert(tk.END, "\nTodas as datas encontradas:\n")
        for date in all_dates:
            self.result_text.insert(tk.END, f"- {date}\n")
        
        self.result_text.config(state=tk.DISABLED)

def main():
    root = tk.Tk()
    app = PDFHolidayChecker(root)
    root.mainloop()

if __name__ == "__main__":
    main()
