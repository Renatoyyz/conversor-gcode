import re
import tkinter as tk
from tkinter import filedialog, messagebox

def parse_gcode_params(line):
    """Extrai os parâmetros (X, Y, Z, R, F, Q) de uma linha de G-code."""
    params = {}
    matches = re.findall(r'([A-Z])(-?\d+\.?\d*)', line.upper())
    for match in matches:
        params[match[0]] = float(match[1])
    return params

def convert_gcode_for_mach3(gcode_text):
    """Converte G-code para Mach3: remove parâmetro K e adiciona rotinas de segurança."""
    output_lines = []
    lines = gcode_text.splitlines()
    
    initial_z = 15.0  # Altura Z segura padrão
    spindle_speed = 1000  # RPM padrão do spindle
    
    # Detecta velocidade do spindle no código original
    for line in lines:
        if 'S' in line.upper():
            params = parse_gcode_params(line)
            if 'S' in params:
                spindle_speed = int(params['S'])
                break
    
    # Detecta altura Z inicial
    for line in lines:
        line_upper = line.strip().upper()
        if line_upper.startswith('G0') and 'Z' in line_upper:
            params = parse_gcode_params(line_upper)
            if 'Z' in params:
                if 'X' not in params and 'Y' not in params:
                    initial_z = params['Z']
                    break
    
    # Adiciona rotina de inicialização segura
    output_lines.append("; ========================================\n")
    output_lines.append("; Rotina de Inicialização Mach3\n")
    output_lines.append("; ========================================\n")
    output_lines.append("G21 ; Modo métrico (mm)\n")
    output_lines.append("G90 ; Modo absoluto\n")
    output_lines.append("G94 ; Avanço em mm/min\n")
    output_lines.append("G17 ; Plano XY\n")
    output_lines.append(f"M3 S{spindle_speed} ; Liga spindle a {spindle_speed} RPM\n")
    output_lines.append("G4 P2.0 ; Aguarda 2 segundos para estabilizar\n")
    output_lines.append("; ========================================\n")
    output_lines.append("\n")
    
    # Processa cada linha removendo o parâmetro K
    for line in lines:
        line_stripped = line.strip()
        
        if not line_stripped:
            continue
        
        # Remove comentários de linha inteira
        if line_stripped.startswith('(') or line_stripped.startswith(';'):
            output_lines.append(line + '\n')
            continue
        
        line_upper = line_stripped.upper()
        
        # Verifica se é um comando de arco (G2 ou G3)
        if 'G2' in line_upper or 'G3' in line_upper:
            # Remove o parâmetro K da linha
            # Usa regex para encontrar e remover K seguido de número
            cleaned_line = re.sub(r'\s+K-?\d+\.?\d*', '', line_stripped, flags=re.IGNORECASE)
            output_lines.append(cleaned_line + '\n')
        else:
            output_lines.append(line + '\n')
    
    # Adiciona rotina de retorno seguro ao final
    output_lines.append("\n")
    output_lines.append("; ========================================\n")
    output_lines.append("; Rotina de Retorno Seguro para Home\n")
    output_lines.append("; ========================================\n")
    output_lines.append(f"G0 Z{initial_z:.6f} ; Sobe Z para altura segura\n")
    output_lines.append("G0 X0.000000 Y0.000000 ; Move para X0 Y0\n")
    output_lines.append("; Z permanece em altura segura para evitar colisão\n")
    output_lines.append("M5 ; Desliga fuso\n")
    output_lines.append("M30 ; Fim do programa\n")
    output_lines.append("; ========================================\n")
    
    return "".join(output_lines)

def convert_gcode_text(gcode_text):
    """Converte o texto do G-code, expandindo ciclos G73-G89."""
    output_lines = []
    lines = gcode_text.splitlines()
    
    retract_mode = 'G98'
    initial_z = 15.0  # Altura Z segura padrão
    spindle_speed = 1000  # RPM padrão do spindle
    
    # Adiciona rotina de inicialização segura
    output_lines.append("; ========================================\n")
    output_lines.append("; Rotina de Inicialização\n")
    output_lines.append("; ========================================\n")
    output_lines.append("G21 ; Modo métrico (mm)\n")
    output_lines.append("G90 ; Modo absoluto\n")
    output_lines.append("G94 ; Avanço em mm/min\n")
    output_lines.append("G17 ; Plano XY\n")
    
    # Detecta velocidade do spindle no código original
    for line in lines:
        if 'S' in line.upper():
            params = parse_gcode_params(line)
            if 'S' in params:
                spindle_speed = int(params['S'])
                break
    
    output_lines.append(f"M3 S{spindle_speed} ; Liga spindle a {spindle_speed} RPM\n")
    output_lines.append("G4 P2.0 ; Aguarda 2 segundos para estabilizar\n")
    output_lines.append("; ========================================\n")
    output_lines.append("\n")

    for line in lines:
        line_upper = line.strip().upper()

        if not line_upper:
            continue

        if 'G98' in line_upper:
            retract_mode = 'G98'
        elif 'G99' in line_upper:
            retract_mode = 'G99'
        
        # Tenta capturar a altura Z inicial segura
        if line_upper.startswith('G0') and 'Z' in line_upper:
            params = parse_gcode_params(line_upper)
            if 'Z' in params:
                # Considera como altura inicial se for um movimento Z isolado ou o primeiro
                if 'X' not in params and 'Y' not in params:
                    initial_z = params['Z']

        # --- Conversão do G73 (Furação Pica-Pau de Alta Velocidade) ---
        if line_upper.startswith('G73'):
            params = parse_gcode_params(line_upper)
            x, y, z, r, f, q = params.get('X'), params.get('Y'), params.get('Z'), params.get('R'), params.get('F'), params.get('Q', 1.0)
            
            output_lines.append(f"; --- Conversão G73 para X{x} Y{y} ---\n")
            output_lines.append(f"G0 X{x:.6f} Y{y:.6f}\n")
            
            current_depth = r
            while current_depth > z:
                next_peck_depth = max(current_depth - q, z)
                output_lines.append(f"G0 Z{current_depth + 1.0:.6f}\n")  # Retrai ligeiramente
                output_lines.append(f"G1 Z{next_peck_depth:.6f} F{f:.6f}\n")
                current_depth = next_peck_depth
            
            retract_z = initial_z if retract_mode == 'G98' else r
            output_lines.append(f"G0 Z{retract_z:.6f}\n")
            output_lines.append(f"; --- Fim da conversão G73 ---\n")

        # --- Conversão do G76 (Mandrilamento Fino) ---
        elif line_upper.startswith('G76'):
            params = parse_gcode_params(line_upper)
            x, y, z, r, f = params.get('X'), params.get('Y'), params.get('Z'), params.get('R'), params.get('F')
            q = params.get('Q', 0.5)  # Deslocamento do fuso
            
            output_lines.append(f"; --- Conversão G76 para X{x} Y{y} ---\n")
            output_lines.append(f"G0 X{x:.6f} Y{y:.6f}\n")
            output_lines.append(f"G0 Z{r:.6f}\n")
            output_lines.append(f"G1 Z{z:.6f} F{f:.6f}\n")
            output_lines.append(f"; M5 ; Parar fuso (orientado)\n")
            output_lines.append(f"G0 X{x + q:.6f} Y{y:.6f}\n")  # Deslocamento
            retract_z = initial_z if retract_mode == 'G98' else r
            output_lines.append(f"G0 Z{retract_z:.6f}\n")
            output_lines.append(f"G0 X{x:.6f} Y{y:.6f}\n")  # Retorna
            output_lines.append(f"; M3 ; Religar fuso\n")
            output_lines.append(f"; --- Fim da conversão G76 ---\n")

        # --- Conversão do G81 (Furação Simples) ---
        elif line_upper.startswith('G81'):
            params = parse_gcode_params(line_upper)
            x, y, z, r, f = params.get('X'), params.get('Y'), params.get('Z'), params.get('R'), params.get('F')

            output_lines.append(f"; --- Conversão G81 para X{x} Y{y} ---\n")
            output_lines.append(f"G0 X{x:.6f} Y{y:.6f}\n")
            output_lines.append(f"G0 Z{r:.6f}\n")
            output_lines.append(f"G1 Z{z:.6f} F{f:.6f}\n")
            retract_z = initial_z if retract_mode == 'G98' else r
            output_lines.append(f"G0 Z{retract_z:.6f}\n")
            output_lines.append(f"; --- Fim da conversão G81 ---\n")

        # --- Conversão do G82 (Furação com Temporização) ---
        elif line_upper.startswith('G82'):
            params = parse_gcode_params(line_upper)
            x, y, z, r, f = params.get('X'), params.get('Y'), params.get('Z'), params.get('R'), params.get('F')
            p = params.get('P', 0.0)  # Tempo de pausa em segundos
            
            output_lines.append(f"; --- Conversão G82 para X{x} Y{y} ---\n")
            output_lines.append(f"G0 X{x:.6f} Y{y:.6f}\n")
            output_lines.append(f"G0 Z{r:.6f}\n")
            output_lines.append(f"G1 Z{z:.6f} F{f:.6f}\n")
            if p > 0:
                output_lines.append(f"G4 P{p:.3f} ; Pausa de {p}s\n")
            retract_z = initial_z if retract_mode == 'G98' else r
            output_lines.append(f"G0 Z{retract_z:.6f}\n")
            output_lines.append(f"; --- Fim da conversão G82 ---\n")

        # --- Conversão do G83 (Furação Pica-Pau) ---
        elif line_upper.startswith('G83'):
            params = parse_gcode_params(line_upper)
            x, y, z, r, f, q = params.get('X'), params.get('Y'), params.get('Z'), params.get('R'), params.get('F'), params.get('Q')
            
            output_lines.append(f"; --- Conversão G83 para X{x} Y{y} ---\n")
            output_lines.append(f"G0 X{x:.6f} Y{y:.6f}\n")
            
            current_depth = r
            while current_depth > z:
                next_peck_depth = max(current_depth - q, z)
                output_lines.append(f"G0 Z{r:.6f}\n")  # Retorna ao plano R
                output_lines.append(f"G1 Z{next_peck_depth:.6f} F{f:.6f}\n")
                current_depth = next_peck_depth
            
            retract_z = initial_z if retract_mode == 'G98' else r
            output_lines.append(f"G0 Z{retract_z:.6f}\n")
            output_lines.append(f"; --- Fim da conversão G83 ---\n")

        # --- Conversão do G84 (Rosqueamento com Macho) ---
        elif line_upper.startswith('G84'):
            params = parse_gcode_params(line_upper)
            x, y, z, r, f = params.get('X'), params.get('Y'), params.get('Z'), params.get('R'), params.get('F')
            
            output_lines.append(f"; --- Conversão G84 para X{x} Y{y} ---\n")
            output_lines.append(f"G0 X{x:.6f} Y{y:.6f}\n")
            output_lines.append(f"G0 Z{r:.6f}\n")
            output_lines.append(f"; M3 ; Fuso horário\n")
            output_lines.append(f"G1 Z{z:.6f} F{f:.6f}\n")
            output_lines.append(f"; M4 ; Fuso anti-horário para retirada\n")
            output_lines.append(f"G1 Z{r:.6f} F{f:.6f}\n")
            output_lines.append(f"; M3 ; Fuso horário novamente\n")
            retract_z = initial_z if retract_mode == 'G98' else r
            output_lines.append(f"G0 Z{retract_z:.6f}\n")
            output_lines.append(f"; --- Fim da conversão G84 ---\n")

        # --- Conversão do G85 (Mandrilamento/Alargamento) ---
        elif line_upper.startswith('G85'):
            params = parse_gcode_params(line_upper)
            x, y, z, r, f = params.get('X'), params.get('Y'), params.get('Z'), params.get('R'), params.get('F')
            
            output_lines.append(f"; --- Conversão G85 para X{x} Y{y} ---\n")
            output_lines.append(f"G0 X{x:.6f} Y{y:.6f}\n")
            output_lines.append(f"G0 Z{r:.6f}\n")
            output_lines.append(f"G1 Z{z:.6f} F{f:.6f}\n")
            output_lines.append(f"G1 Z{r:.6f} F{f:.6f}\n")  # Retrai com avanço
            retract_z = initial_z if retract_mode == 'G98' else r
            output_lines.append(f"G0 Z{retract_z:.6f}\n")
            output_lines.append(f"; --- Fim da conversão G85 ---\n")

        # --- Conversão do G86 (Mandrilamento com Parada) ---
        elif line_upper.startswith('G86'):
            params = parse_gcode_params(line_upper)
            x, y, z, r, f = params.get('X'), params.get('Y'), params.get('Z'), params.get('R'), params.get('F')
            
            output_lines.append(f"; --- Conversão G86 para X{x} Y{y} ---\n")
            output_lines.append(f"G0 X{x:.6f} Y{y:.6f}\n")
            output_lines.append(f"G0 Z{r:.6f}\n")
            output_lines.append(f"G1 Z{z:.6f} F{f:.6f}\n")
            output_lines.append(f"; M5 ; Parar fuso\n")
            retract_z = initial_z if retract_mode == 'G98' else r
            output_lines.append(f"G0 Z{retract_z:.6f}\n")
            output_lines.append(f"; M3 ; Religar fuso\n")
            output_lines.append(f"; --- Fim da conversão G86 ---\n")

        # --- Conversão do G87 (Mandrilamento Reverso) ---
        elif line_upper.startswith('G87'):
            params = parse_gcode_params(line_upper)
            x, y, z, r, f = params.get('X'), params.get('Y'), params.get('Z'), params.get('R'), params.get('F')
            q = params.get('Q', 0.5)  # Deslocamento
            
            output_lines.append(f"; --- Conversão G87 para X{x} Y{y} ---\n")
            output_lines.append(f"G0 X{x:.6f} Y{y:.6f}\n")
            output_lines.append(f"G0 Z{r:.6f}\n")
            output_lines.append(f"; M4 ; Fuso anti-horário\n")
            output_lines.append(f"G1 Z{z:.6f} F{f:.6f}\n")
            output_lines.append(f"; M5 ; Parar fuso\n")
            output_lines.append(f"G0 X{x + q:.6f} Y{y:.6f}\n")  # Deslocamento
            output_lines.append(f"G0 Z{r:.6f}\n")
            output_lines.append(f"G0 X{x:.6f} Y{y:.6f}\n")
            output_lines.append(f"; M3 ; Fuso horário\n")
            retract_z = initial_z if retract_mode == 'G98' else r
            output_lines.append(f"G0 Z{retract_z:.6f}\n")
            output_lines.append(f"; --- Fim da conversão G87 ---\n")

        # --- Conversão do G88 (Mandrilamento com Parada Manual) ---
        elif line_upper.startswith('G88'):
            params = parse_gcode_params(line_upper)
            x, y, z, r, f = params.get('X'), params.get('Y'), params.get('Z'), params.get('R'), params.get('F')
            p = params.get('P', 0.0)
            
            output_lines.append(f"; --- Conversão G88 para X{x} Y{y} ---\n")
            output_lines.append(f"G0 X{x:.6f} Y{y:.6f}\n")
            output_lines.append(f"G0 Z{r:.6f}\n")
            output_lines.append(f"G1 Z{z:.6f} F{f:.6f}\n")
            if p > 0:
                output_lines.append(f"G4 P{p:.3f}\n")
            output_lines.append(f"; M0 ; Parada programada - retirar ferramenta manualmente\n")
            retract_z = initial_z if retract_mode == 'G98' else r
            output_lines.append(f"G0 Z{retract_z:.6f}\n")
            output_lines.append(f"; --- Fim da conversão G88 ---\n")

        # --- Conversão do G89 (Mandrilamento com Temporização) ---
        elif line_upper.startswith('G89'):
            params = parse_gcode_params(line_upper)
            x, y, z, r, f = params.get('X'), params.get('Y'), params.get('Z'), params.get('R'), params.get('F')
            p = params.get('P', 0.0)
            
            output_lines.append(f"; --- Conversão G89 para X{x} Y{y} ---\n")
            output_lines.append(f"G0 X{x:.6f} Y{y:.6f}\n")
            output_lines.append(f"G0 Z{r:.6f}\n")
            output_lines.append(f"G1 Z{z:.6f} F{f:.6f}\n")
            if p > 0:
                output_lines.append(f"G4 P{p:.3f}\n")
            output_lines.append(f"G1 Z{r:.6f} F{f:.6f}\n")  # Retrai com avanço
            retract_z = initial_z if retract_mode == 'G98' else r
            output_lines.append(f"G0 Z{retract_z:.6f}\n")
            output_lines.append(f"; --- Fim da conversão G89 ---\n")

        elif line_upper.startswith('G80'):
            output_lines.append("; G80 ignorado (ciclo cancelado manualmente)\n")
        
        else:
            output_lines.append(line + '\n')
    
    # Adiciona rotina de retorno seguro ao final
    output_lines.append("\n")
    output_lines.append("; ========================================\n")
    output_lines.append("; Rotina de Retorno Seguro para Home\n")
    output_lines.append("; ========================================\n")
    output_lines.append("G0 Z" + f"{initial_z:.6f}" + " ; Sobe Z para altura segura\n")
    output_lines.append("G0 X0.000000 Y0.000000 ; Move para X0 Y0\n")
    output_lines.append("; Z permanece em altura segura para evitar colisão\n")
    output_lines.append("M5 ; Desliga fuso\n")
    output_lines.append("M30 ; Fim do programa\n")
    output_lines.append("; ========================================\n")
            
    return "".join(output_lines)

# --- Interface Gráfica ---
class GCodeConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Conversor de G-code")
        
        # Frame superior para labels
        top_frame = tk.Frame(root)
        top_frame.pack(fill=tk.X, padx=10, pady=10)
        
        label_in = tk.Label(top_frame, text="G-code Original", 
                           font=('Helvetica', 14, 'bold'))
        label_in.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        label_out = tk.Label(top_frame, text="G-code Convertido", 
                            font=('Helvetica', 14, 'bold'))
        label_out.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        # Frame do meio para text widgets
        middle_frame = tk.Frame(root)
        middle_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Frame esquerdo com scrollbar
        left_frame = tk.Frame(middle_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        scroll_left = tk.Scrollbar(left_frame)
        scroll_left.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.text_in = tk.Text(left_frame, font=('Monaco', 11), 
                               yscrollcommand=scroll_left.set,
                               width=50, height=25)
        self.text_in.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_left.config(command=self.text_in.yview)
        
        # Frame direito com scrollbar
        right_frame = tk.Frame(middle_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        scroll_right = tk.Scrollbar(right_frame)
        scroll_right.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.text_out = tk.Text(right_frame, font=('Monaco', 11),
                                yscrollcommand=scroll_right.set,
                                width=50, height=25)
        self.text_out.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_right.config(command=self.text_out.yview)
        
        # Frame de botões - linha 1
        btn_frame1 = tk.Frame(root)
        btn_frame1.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        self.load_btn = tk.Button(btn_frame1, text="Carregar Arquivo", command=self.load_file, 
                                  font=('Helvetica', 11, 'bold'))
        self.load_btn.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
        
        self.save_btn = tk.Button(btn_frame1, text="Salvar Arquivo", command=self.save_file, 
                                  font=('Helvetica', 11, 'bold'))
        self.save_btn.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
        
        self.clear_btn = tk.Button(btn_frame1, text="Limpar", command=self.clear_fields, 
                                   font=('Helvetica', 11, 'bold'))
        self.clear_btn.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
        
        # Frame de botões - linha 2 (conversões)
        btn_frame2 = tk.Frame(root)
        btn_frame2.pack(fill=tk.X, padx=10, pady=(5, 10))
        
        # Label explicativo
        label_conv = tk.Label(btn_frame2, text="Escolha o tipo de conversão:", 
                             font=('Helvetica', 10))
        label_conv.pack(side=tk.TOP, pady=(0, 5))
        
        # Container para os botões de conversão
        btns_container = tk.Frame(btn_frame2)
        btns_container.pack(fill=tk.X)
        
        self.convert_linear_btn = tk.Button(btns_container, 
                                           text="CONVERTER LINEAR\n(Lineariza ciclos G73-G89)", 
                                           command=self.convert_linear, 
                                           font=('Helvetica', 10, 'bold'),
                                           bg='lightgreen',
                                           activebackground='#90EE90',
                                           relief=tk.RAISED,
                                           bd=3,
                                           height=3)
        self.convert_linear_btn.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.BOTH, expand=True)
        
        self.convert_mach3_btn = tk.Button(btns_container, 
                                          text="CONVERTER MACH3\n(Remove parâmetro K)", 
                                          command=self.convert_mach3, 
                                          font=('Helvetica', 10, 'bold'),
                                          bg='lightblue',
                                          activebackground='#87CEEB',
                                          relief=tk.RAISED,
                                          bd=3,
                                          height=3)
        self.convert_mach3_btn.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.BOTH, expand=True)

    def load_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("G-code files", "*.nc *.gcode *.txt"), ("All files", "*.*")])
        if not filepath:
            return
        with open(filepath, 'r') as f:
            self.text_in.delete('1.0', tk.END)
            self.text_in.insert('1.0', f.read())

    def convert_linear(self):
        """Converte G-code linearizando ciclos G8x."""
        input_text = self.text_in.get('1.0', tk.END)
        if not input_text.strip():
            messagebox.showwarning("Aviso", "A caixa de texto de entrada está vazia.")
            return
        output_text = convert_gcode_text(input_text)
        self.text_out.delete('1.0', tk.END)
        self.text_out.insert('1.0', output_text)
        messagebox.showinfo("Sucesso", "Conversão Linear concluída!\nCiclos G8x foram linearizados.")
    
    def convert_mach3(self):
        """Converte G-code para Mach3: remove parâmetro K e adiciona rotinas de segurança."""
        input_text = self.text_in.get('1.0', tk.END)
        if not input_text.strip():
            messagebox.showwarning("Aviso", "A caixa de texto de entrada está vazia.")
            return
        output_text = convert_gcode_for_mach3(input_text)
        self.text_out.delete('1.0', tk.END)
        self.text_out.insert('1.0', output_text)
        messagebox.showinfo("Sucesso", "Conversão Mach3 concluída!\nParâmetro K removido e rotinas de segurança adicionadas.")

    def save_file(self):
        output_text = self.text_out.get('1.0', tk.END)
        if not output_text.strip():
            messagebox.showwarning("Aviso", "A caixa de texto de saída está vazia. Converta primeiro.")
            return
        filepath = filedialog.asksaveasfilename(defaultextension=".nc", filetypes=[("G-code files", "*.nc"), ("All files", "*.*")])
        if not filepath:
            return
        with open(filepath, 'w') as f:
            f.write(output_text)
        messagebox.showinfo("Sucesso", f"Arquivo salvo em:\n{filepath}")

    def clear_fields(self):
        """Limpa os campos de entrada e saída."""
        self.text_in.delete('1.0', tk.END)
        self.text_out.delete('1.0', tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = GCodeConverterApp(root)
    root.mainloop()