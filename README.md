# WinDebloater

Remove bloatware do Windows 10/11 com segurança e persistência.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Windows](https://img.shields.io/badge/Windows-10%2F11-0078D6.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## Screenshots

<p align="center">
  <img src="screenshots/main.png" alt="Tela Principal" width="800">
</p>

<p align="center">
  <img src="screenshots/removing.png" alt="Removendo Bloatwares" width="800">
</p>

## Funcionalidades

- **Scan automático** - Detecta bloatwares instalados, processos em execução e serviços
- **Remoção persistente** - Usa 8 técnicas diferentes para garantir remoção completa
- **Backup automático** - Cria backup antes de qualquer alteração
- **Restauração fácil** - Restaure itens removidos com um clique
- **Interface amigável** - Dark theme moderno e fácil de usar
- **Níveis de risco** - Identifica itens seguros, com cautela e arriscados

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

### Serviços
- Windows Search (Indexação)
- Telemetria (DiagTrack)
- SysMain (Superfetch)
- Serviços Xbox

### Processos
- Edge WebView2
- SearchHost
- CrossDevice

### Fabricantes
- HP, Dell, Lenovo, Acer, ASUS bloatware

## Instalação

### Requisitos
- Windows 10/11
- Python 3.10 ou superior
- Privilégios de administrador

### Instalação Rápida

1. Clone o repositório:
```bash
git clone https://github.com/gabrielcnb/WinDebloater.git
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
2. O programa pedirá privilégios de administrador
3. Clique em **Scan** para detectar bloatwares
4. Selecione os itens que deseja remover
5. Clique em **Remover**
6. Pronto!

### Níveis de Risco

| Ícone | Nível | Descrição |
|-------|-------|-----------|
| 🟢 | Seguro | Pode remover sem problemas |
| 🟡 | Cautela | Pode afetar algumas funcionalidades |
| 🔴 | Arriscado | Pode causar instabilidade |

## Técnicas de Remoção

O WinDebloater usa 8 técnicas em cascata para garantir remoção:

1. `Remove-AppxPackage` (usuário atual)
2. `Remove-AppxPackage -AllUsers` (todos usuários)
3. `Remove-AppxProvisionedPackage` (impede reinstalação)
4. Desativar serviço
5. Encerrar processo + remover do startup
6. Desativar tarefas agendadas
7. IFEO (Image File Execution Options)
8. Renomear executável (último recurso)

## Restauração

Se algo der errado:

1. Clique em **Restaurar**
2. Selecione um ponto de backup
3. Confirme a restauração

## Estrutura do Projeto

```
WinDebloater/
├── src/
│   ├── main.py           # Ponto de entrada
│   ├── ui/               # Interface gráfica
│   ├── core/             # Lógica principal
│   └── utils/            # Utilitários
├── assets/               # Ícones e recursos
├── backups/              # Backups automáticos
├── requirements.txt
├── setup.bat
└── run.bat
```

## Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/NovaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona NovaFeature'`)
4. Push para a branch (`git push origin feature/NovaFeature`)
5. Abra um Pull Request

## Aviso Legal

Use por sua conta e risco. O autor não se responsabiliza por danos causados pelo uso deste software. Sempre faça backup do sistema antes de usar.

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## Autor

Desenvolvido por Gabriel

---

Se este projeto foi útil, considere dar uma ⭐ no repositório!
