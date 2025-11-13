# Conversor de G-code

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux%20%7C%20Windows-lightgrey)

## 📋 Descrição

Conversor de G-code que lineariza ciclos enlatados (G73-G89) para instruções lineares básicas (G0/G1), ideal para máquinas CNC que não suportam ciclos enlatados complexos.

O programa converte automaticamente ciclos de furação, mandrilamento e rosqueamento em sequências de movimentos lineares simples e seguros, adicionando rotinas de inicialização e finalização seguras.

## ✨ Funcionalidades

### Ciclos G-code Suportados

O conversor lineariza os seguintes ciclos enlatados:

- **G73** - Furação pica-pau de alta velocidade
- **G76** - Mandrilamento fino com deslocamento
- **G81** - Furação simples
- **G82** - Furação com temporização (dwell)
- **G83** - Furação pica-pau (peck drilling)
- **G84** - Rosqueamento com macho
- **G85** - Mandrilamento/alargamento
- **G86** - Mandrilamento com parada orientada
- **G87** - Mandrilamento reverso
- **G88** - Mandrilamento com parada manual
- **G89** - Mandrilamento com temporização

### Rotinas de Segurança

#### 🚀 Inicialização Automática
- Configuração de modo métrico (G21)
- Posicionamento absoluto (G90)
- Definição do plano de trabalho (G17)
- Detecção e ativação automática do spindle com velocidade correta
- Pausa para estabilização

#### 🏠 Finalização Segura
- Elevação do eixo Z para altura segura
- Retorno para posição home (X0, Y0)
- Z permanece elevado para evitar colisões
- Desligamento do spindle (M5)
- Fim de programa (M30)

### Interface Gráfica

- **Dois campos de texto**: entrada (G-code original) e saída (G-code linearizado)
- **Carregar Arquivo**: Importa arquivos .nc, .gcode ou .txt
- **Converter**: Realiza a linearização dos ciclos
- **Salvar Arquivo**: Exporta o G-code convertido
- **Limpar**: Limpa ambos os campos

## 🎯 Casos de Uso

- Máquinas CNC que não suportam ciclos enlatados
- Conversão de programas gerados em CAM para controladores simples
- Auditoria e compreensão de ciclos complexos
- Adaptação de programas para diferentes controladores

## 🖼️ Capturas de Tela

A interface apresenta:
- Campo esquerdo: G-code original
- Campo direito: G-code convertido
- Botões intuitivos para operações
- Scrollbars para códigos longos

## 📊 Exemplo de Conversão

### Entrada (G-code com ciclo enlatado):
```gcode
G98
G83 X10.0 Y20.0 Z-15.0 R5.0 Q3.0 F100.0
```

### Saída (G-code linearizado):
```gcode
; --- Conversão G83 para X10.0 Y20.0 ---
G0 X10.000000 Y20.000000
G0 Z5.000000
G1 Z2.000000 F100.000000
G0 Z5.000000
G1 Z-1.000000 F100.000000
G0 Z5.000000
G1 Z-4.000000 F100.000000
G0 Z5.000000
G1 Z-7.000000 F100.000000
G0 Z5.000000
G1 Z-10.000000 F100.000000
G0 Z5.000000
G1 Z-13.000000 F100.000000
G0 Z5.000000
G1 Z-15.000000 F100.000000
G0 Z15.000000
; --- Fim da conversão G83 ---
```

## 🔧 Requisitos

Ver arquivo [INSTALL.md](INSTALL.md) para instruções completas de instalação.

### Requisitos Mínimos

- Python 3.10 ou superior
- Tkinter 8.6 ou superior
- macOS, Linux ou Windows

## 🚀 Instalação Rápida

### macOS (Recomendado)

```bash
# 1. Instalar Homebrew (se ainda não tiver)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. Instalar Python 3.11 com Tkinter
brew install python@3.11
brew install python-tk@3.11

# 3. Executar o conversor
/usr/local/bin/python3.11 conversor-gcode.py
```

### Linux

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.11 python3-tk

# Fedora
sudo dnf install python3.11 python3-tkinter

# Executar
python3.11 conversor-gcode.py
```

### Windows

```bash
# Baixar Python 3.11+ de python.org (já inclui Tkinter)
# Executar
python conversor-gcode.py
```

## 📖 Como Usar

1. **Iniciar o programa**:
   ```bash
   python3.11 conversor-gcode.py
   ```

2. **Carregar G-code**:
   - Cole diretamente no campo da esquerda, ou
   - Use o botão "Carregar Arquivo" para importar

3. **Converter**:
   - Clique no botão "CONVERTER"
   - O resultado aparece no campo da direita

4. **Salvar**:
   - Use o botão "Salvar Arquivo" para exportar
   - Escolha o local e nome do arquivo

5. **Limpar**:
   - Use o botão "Limpar" para resetar os campos

## 🛠️ Desenvolvimento

### Estrutura do Código

```
conversor-gcode/
├── conversor-gcode.py    # Programa principal
├── README.md             # Este arquivo
└── INSTALL.md           # Instruções de instalação
```

### Funções Principais

- `parse_gcode_params(line)`: Extrai parâmetros de uma linha G-code
- `convert_gcode_text(gcode_text)`: Converte o texto completo do G-code
- `GCodeConverterApp`: Classe da interface gráfica Tkinter

## 🐛 Resolução de Problemas

### Texto não aparece nos campos

**Problema**: Tkinter 8.5 (muito antigo)

**Solução**: Atualizar para Python com Tkinter 8.6:
```bash
# Verificar versão
python3 -c "import tkinter; print(tkinter.TkVersion)"

# Se for 8.5, instalar versão mais recente via Homebrew (macOS)
brew install python@3.11 python-tk@3.11
```

### Erro ao importar tkinter

**Linux**: 
```bash
sudo apt install python3-tk
```

**macOS**:
```bash
brew install python-tk@3.11
```

## 📝 Notas Técnicas

### Modos de Retração

O conversor respeita os modos de retração G98/G99:
- **G98**: Retorna para altura inicial (padrão)
- **G99**: Retorna para plano R

### Detecção Automática

- **Altura segura Z**: Detectada automaticamente do primeiro movimento G0 Z
- **Velocidade do spindle**: Detectada do primeiro parâmetro S encontrado
- **Padrões**: Z=15mm, S=1000 RPM se não detectados

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para:

1. Fazer fork do projeto
2. Criar uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abrir um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

## 👤 Autor

**Renato Oliveira**

- GitHub: [@Renatoyyz](https://github.com/Renatoyyz)

## 🙏 Agradecimentos

- Comunidade Python
- Projeto Tkinter
- Usuários de máquinas CNC que inspiraram este projeto

## 📮 Suporte

Para reportar bugs ou sugerir melhorias, abra uma [issue](https://github.com/Renatoyyz/conversor-gcode/issues) no GitHub.

---

⭐ Se este projeto foi útil, considere dar uma estrela no GitHub!
