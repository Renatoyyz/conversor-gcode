# Guia de Instalação - Conversor de G-code

Este guia fornece instruções detalhadas para instalar e configurar o ambiente necessário para executar o Conversor de G-code.

## 📋 Índice

- [Requisitos do Sistema](#requisitos-do-sistema)
- [Instalação por Sistema Operacional](#instalação-por-sistema-operacional)
  - [macOS](#macos)
  - [Linux](#linux)
  - [Windows](#windows)
- [Configuração de Ambiente Virtual](#configuração-de-ambiente-virtual)
- [Verificação da Instalação](#verificação-da-instalação)
- [Resolução de Problemas](#resolução-de-problemas)

## 📦 Requisitos do Sistema

### Requisitos Mínimos

- **Python**: 3.10 ou superior (recomendado 3.11+)
- **Tkinter**: 8.6 ou superior
- **Memória RAM**: 512 MB
- **Espaço em disco**: 100 MB
- **Sistema Operacional**: macOS 10.14+, Linux (kernel 4.x+), Windows 10+

### Dependências

O projeto utiliza apenas bibliotecas padrão do Python:
- `tkinter` - Interface gráfica (já incluído no Python)
- `re` - Expressões regulares (biblioteca padrão)

**Não são necessárias dependências externas via pip!**

---

## 🍎 macOS

### Método 1: Homebrew (Recomendado)

Este é o método mais simples e confiável para macOS.

#### 1. Instalar Homebrew

Se você ainda não tem o Homebrew instalado:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Após a instalação, adicione ao PATH (se necessário):

```bash
# Para Intel Mac
echo 'eval "$(/usr/local/bin/brew shellenv)"' >> ~/.zshrc

# Para Apple Silicon (M1/M2/M3)
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zshrc

# Recarregar o terminal
source ~/.zshrc
```

#### 2. Instalar Python 3.11 com Tkinter

```bash
# Instalar Python 3.11
brew install python@3.11

# Instalar Tkinter para Python 3.11
brew install python-tk@3.11
```

#### 3. Verificar a instalação

```bash
# Verificar versão do Python
/usr/local/bin/python3.11 --version

# Verificar Tkinter (deve retornar 8.6)
/usr/local/bin/python3.11 -c "import tkinter; print('Tkinter version:', tkinter.TkVersion)"
```

#### 4. Executar o conversor

```bash
cd /caminho/para/conversor-gcode
/usr/local/bin/python3.11 conversor-gcode.py
```

### Método 2: Python.org

1. Baixar Python 3.11+ de [python.org](https://www.python.org/downloads/macos/)
2. Instalar o pacote .pkg
3. O Tkinter já vem incluído
4. Executar: `python3 conversor-gcode.py`

### Método 3: pyenv (Para desenvolvedores)

```bash
# Instalar pyenv
brew install pyenv

# Instalar tcl-tk
brew install tcl-tk

# Instalar Python com Tkinter
env PYTHON_CONFIGURE_OPTS="--with-tcltk-includes='-I/usr/local/opt/tcl-tk/include' --with-tcltk-libs='-L/usr/local/opt/tcl-tk/lib -ltcl8.6 -ltk8.6'" pyenv install 3.11.7

# Definir como global
pyenv global 3.11.7
```

---

## 🐧 Linux

### Ubuntu / Debian

```bash
# Atualizar repositórios
sudo apt update

# Instalar Python 3.11 e Tkinter
sudo apt install python3.11 python3.11-tk

# Verificar instalação
python3.11 --version
python3.11 -c "import tkinter; print('Tkinter version:', tkinter.TkVersion)"

# Executar
python3.11 conversor-gcode.py
```

### Fedora / RHEL / CentOS

```bash
# Instalar Python e Tkinter
sudo dnf install python3.11 python3-tkinter

# Verificar
python3.11 --version

# Executar
python3.11 conversor-gcode.py
```

### Arch Linux

```bash
# Instalar Python (Tkinter já incluído)
sudo pacman -S python

# Verificar
python --version

# Executar
python conversor-gcode.py
```

### openSUSE

```bash
sudo zypper install python311 python311-tk
```

---

## 🪟 Windows

### Método 1: Instalador Oficial (Recomendado)

1. **Baixar Python**:
   - Visite [python.org/downloads](https://www.python.org/downloads/)
   - Baixe Python 3.11 ou superior

2. **Instalar**:
   - Execute o instalador
   - ✅ **IMPORTANTE**: Marque "Add Python to PATH"
   - Clique em "Install Now"

3. **Verificar**:
   ```cmd
   python --version
   python -c "import tkinter; print('Tkinter OK')"
   ```

4. **Executar**:
   ```cmd
   cd caminho\para\conversor-gcode
   python conversor-gcode.py
   ```

### Método 2: Microsoft Store

1. Abrir Microsoft Store
2. Buscar "Python 3.11"
3. Instalar
4. Tkinter já vem incluído

### Método 3: Chocolatey

```powershell
# Instalar Chocolatey (como administrador)
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Instalar Python
choco install python311
```

---

## 🔧 Configuração de Ambiente Virtual (Opcional)

Embora não seja necessário para este projeto (não tem dependências externas), você pode usar um ambiente virtual:

### Criar ambiente virtual

```bash
# Criar venv
python3.11 -m venv venv

# Ativar (macOS/Linux)
source venv/bin/activate

# Ativar (Windows)
venv\Scripts\activate

# Executar
python conversor-gcode.py

# Desativar
deactivate
```

---

## ✅ Verificação da Instalação

Execute o seguinte script de teste:

```bash
python3.11 -c "
import sys
import tkinter as tk

print('✓ Python version:', sys.version)
print('✓ Tkinter version:', tk.TkVersion)

if tk.TkVersion >= 8.6:
    print('✓ Tkinter OK - versão adequada')
else:
    print('✗ Tkinter muito antigo, atualize para 8.6+')

# Teste de interface
root = tk.Tk()
root.title('Teste')
label = tk.Label(root, text='Tkinter funcionando!')
label.pack()
print('✓ Interface gráfica OK')
root.destroy()

print('\n🎉 Sistema pronto para executar o conversor!')
"
```

Saída esperada:
```
✓ Python version: 3.11.x
✓ Tkinter version: 8.6
✓ Tkinter OK - versão adequada
✓ Interface gráfica OK

🎉 Sistema pronto para executar o conversor!
```

---

## 🐛 Resolução de Problemas

### Problema: "No module named 'tkinter'"

**Linux**:
```bash
sudo apt install python3-tk  # Ubuntu/Debian
sudo dnf install python3-tkinter  # Fedora
```

**macOS**:
```bash
brew install python-tk@3.11
```

**Windows**: Reinstale o Python marcando "tcl/tk and IDLE"

### Problema: Tkinter versão 8.5

**Sintoma**: Texto não aparece nos campos

**Solução**:
```bash
# Verificar versão
python3 -c "import tkinter; print(tkinter.TkVersion)"

# Se retornar 8.5, instalar versão mais recente
# macOS
brew install python@3.11 python-tk@3.11

# Linux
sudo apt install python3.11-tk
```

### Problema: "python: command not found"

**Linux/macOS**: Use `python3` ou `python3.11` ao invés de `python`

**Windows**: Python não foi adicionado ao PATH durante instalação
- Solução: Reinstalar marcando "Add to PATH"

### Problema: Permissão negada (Linux/macOS)

```bash
chmod +x conversor-gcode.py
```

### Problema: Display não encontrado (SSH/Remote)

```bash
# Habilitar X11 forwarding
ssh -X usuario@servidor

# Ou usar Xvfb (headless)
sudo apt install xvfb
xvfb-run python3.11 conversor-gcode.py
```

---

## 🚀 Executando o Conversor

### Linha de comando

```bash
# macOS/Linux
python3.11 conversor-gcode.py

# Windows
python conversor-gcode.py
```

### Criar atalho (macOS)

```bash
echo '#!/bin/bash
/usr/local/bin/python3.11 /caminho/completo/conversor-gcode.py' > ~/Desktop/Conversor.command
chmod +x ~/Desktop/Conversor.command
```

### Criar atalho (Windows)

1. Botão direito no desktop → Novo → Atalho
2. Local: `python C:\caminho\completo\conversor-gcode.py`
3. Nome: "Conversor G-code"

### Criar atalho (Linux)

```bash
cat > ~/.local/share/applications/conversor-gcode.desktop << EOF
[Desktop Entry]
Type=Application
Name=Conversor G-code
Exec=python3.11 /caminho/completo/conversor-gcode.py
Icon=utilities-terminal
Terminal=false
Categories=Utility;Development;
EOF
```

---

## 📞 Suporte

Se encontrar problemas:

1. Verifique a seção [Resolução de Problemas](#resolução-de-problemas)
2. Consulte o [README.md](README.md)
3. Abra uma [issue no GitHub](https://github.com/Renatoyyz/conversor-gcode/issues)

---

## 🎓 Recursos Adicionais

- [Documentação Python](https://docs.python.org/3/)
- [Documentação Tkinter](https://docs.python.org/3/library/tkinter.html)
- [Homebrew](https://brew.sh/)
- [Python no Windows](https://docs.python.org/3/using/windows.html)

---

✨ **Instalação concluída!** Agora você está pronto para usar o Conversor de G-code.
