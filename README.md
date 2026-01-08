# WinDebloater

Remove bloatware do Windows 10/11 com seguranca e persistencia.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Windows](https://img.shields.io/badge/Windows-10%2F11-0078D6.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## Funcionalidades

- **Scan automatico** - Detecta bloatwares instalados, processos em execucao e servicos
- **Remocao persistente** - Usa 8 tecnicas diferentes para garantir remocao completa
- **Backup automatico** - Cria backup antes de qualquer alteracao
- **Restauracao facil** - Restaure itens removidos com um clique
- **Interface amigavel** - Dark theme moderno e facil de usar
- **Niveis de risco** - Identifica itens seguros, com cautela e arriscados

## Bloatwares Suportados

### Apps Microsoft
- Bing Search, Weather, News
- Cortana
- OneDrive
- Skype, Teams
- Xbox Apps
- Groove Music, Filmes e TV
- Phone Link, People, Maps
- E mais...

### Servicos
- Windows Search (Indexacao)
- Telemetria (DiagTrack)
- SysMain (Superfetch)
- Servicos Xbox

### Processos
- Edge WebView2
- SearchHost
- CrossDevice

### Fabricantes
- HP, Dell, Lenovo, Acer, ASUS bloatware

## Instalacao

### Requisitos
- Windows 10/11
- Python 3.10 ou superior
- Privilegios de administrador

### Instalacao Rapida

1. Clone o repositorio:
```bash
git clone https://github.com/seu-usuario/WinDebloater.git
cd WinDebloater
```

2. Execute o instalador:
```bash
setup.bat
```

3. Ou instale manualmente:
```bash
pip install -r requirements.txt
python src/main.py
```

## Uso

1. Execute `run.bat` ou `python src/main.py`
2. O programa pedira privilegios de administrador
3. Clique em **Scan** para detectar bloatwares
4. Selecione os itens que deseja remover
5. Clique em **Remover**
6. Pronto!

### Niveis de Risco

| Icone | Nivel | Descricao |
|-------|-------|-----------|
| 🟢 | Seguro | Pode remover sem problemas |
| 🟡 | Cautela | Pode afetar algumas funcionalidades |
| 🔴 | Arriscado | Pode causar instabilidade |

## Tecnicas de Remocao

O WinDebloater usa 8 tecnicas em cascata para garantir remocao:

1. `Remove-AppxPackage` (usuario atual)
2. `Remove-AppxPackage -AllUsers` (todos usuarios)
3. `Remove-AppxProvisionedPackage` (impede reinstalacao)
4. Desativar servico
5. Encerrar processo + remover do startup
6. Desativar tarefas agendadas
7. IFEO (Image File Execution Options)
8. Renomear executavel (ultimo recurso)

## Restauracao

Se algo der errado:

1. Clique em **Restaurar**
2. Selecione um ponto de backup
3. Confirme a restauracao

## Estrutura do Projeto

```
WinDebloater/
├── src/
│   ├── main.py           # Ponto de entrada
│   ├── ui/               # Interface grafica
│   ├── core/             # Logica principal
│   └── utils/            # Utilitarios
├── assets/               # Icones e recursos
├── backups/              # Backups automaticos
├── requirements.txt
├── setup.bat
└── run.bat
```

## Contribuindo

Contribuicoes sao bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/NovaFeature`)
3. Commit suas mudancas (`git commit -m 'Adiciona NovaFeature'`)
4. Push para a branch (`git push origin feature/NovaFeature`)
5. Abra um Pull Request

## Aviso Legal

Use por sua conta e risco. O autor nao se responsabiliza por danos causados pelo uso deste software. Sempre faca backup do sistema antes de usar.

## Licenca

Este projeto esta licenciado sob a licenca MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## Autor

Desenvolvido por Gabriel

---

Se este projeto foi util, considere dar uma ⭐ no repositorio!
