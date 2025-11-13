import tkinter as tk

root = tk.Tk()
root.title("Teste Simples")

# Teste básico
text = tk.Text(root, height=10, width=40, bg='white', fg='black')
text.pack(padx=20, pady=20)
text.insert('1.0', 'Teste de texto\nLinha 2\nLinha 3')

# Botão para adicionar mais texto
def adicionar():
    text.insert('end', '\nTexto adicionado!')

btn = tk.Button(root, text="Adicionar Texto", command=adicionar)
btn.pack(pady=10)

root.mainloop()
