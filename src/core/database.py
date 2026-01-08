"""
Database de bloatwares conhecidos do Windows 10/11.
"""
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class RiskLevel(Enum):
    """Nível de risco ao remover o item."""
    SAFE = "safe"           # 🟢 Seguro - pode remover sem problemas
    CAUTION = "caution"     # 🟡 Cuidado - pode afetar algumas funcionalidades
    RISKY = "risky"         # 🔴 Arriscado - pode causar instabilidade


class Category(Enum):
    """Categorias de bloatware."""
    MICROSOFT_APPS = "Apps Microsoft"
    MANUFACTURER = "Apps do Fabricante"
    SERVICES = "Serviços"
    PROCESSES = "Processos"
    STARTUP = "Inicialização"


@dataclass
class BloatwareItem:
    """Representa um item de bloatware."""
    id: str                          # Identificador único
    name: str                        # Nome amigável
    description: str                 # Descrição do que faz
    category: Category               # Categoria
    risk_level: RiskLevel            # Nível de risco
    package_name: Optional[str]      # Nome do pacote AppX (se aplicável)
    process_name: Optional[str]      # Nome do processo (se aplicável)
    service_name: Optional[str]      # Nome do serviço (se aplicável)
    registry_keys: List[str]         # Chaves de registro relacionadas
    removal_commands: List[str]      # Comandos PowerShell para remoção
    can_reinstall: bool              # Se pode ser reinstalado facilmente


class BloatwareDatabase:
    """Database de bloatwares conhecidos."""

    def __init__(self):
        self.items: List[BloatwareItem] = []
        self._load_database()

    def _load_database(self):
        """Carrega a lista de bloatwares conhecidos."""

        # ===== APPS MICROSOFT =====
        self.items.extend([
            BloatwareItem(
                id="bing_search",
                name="Bing Search",
                description="Pesquisa Bing integrada ao Windows. Remove a busca web do menu Iniciar.",
                category=Category.MICROSOFT_APPS,
                risk_level=RiskLevel.SAFE,
                package_name="Microsoft.BingSearch",
                process_name="SearchHost",
                service_name=None,
                registry_keys=[
                    "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Search"
                ],
                removal_commands=[
                    "Get-AppxPackage -Name 'Microsoft.BingSearch' | Remove-AppxPackage"
                ],
                can_reinstall=True
            ),
            BloatwareItem(
                id="bing_weather",
                name="Clima (Weather)",
                description="App de previsão do tempo da Microsoft.",
                category=Category.MICROSOFT_APPS,
                risk_level=RiskLevel.SAFE,
                package_name="Microsoft.BingWeather",
                process_name=None,
                service_name=None,
                registry_keys=[],
                removal_commands=[
                    "Get-AppxPackage -Name 'Microsoft.BingWeather' | Remove-AppxPackage"
                ],
                can_reinstall=True
            ),
            BloatwareItem(
                id="cortana",
                name="Cortana",
                description="Assistente virtual da Microsoft. Não é mais essencial no Windows 11.",
                category=Category.MICROSOFT_APPS,
                risk_level=RiskLevel.SAFE,
                package_name="Microsoft.549981C3F5F10",
                process_name="Cortana",
                service_name=None,
                registry_keys=[
                    "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\Windows Search"
                ],
                removal_commands=[
                    "Get-AppxPackage -Name '*Cortana*' | Remove-AppxPackage"
                ],
                can_reinstall=True
            ),
            BloatwareItem(
                id="get_help",
                name="Obter Ajuda",
                description="App de ajuda da Microsoft. Raramente útil.",
                category=Category.MICROSOFT_APPS,
                risk_level=RiskLevel.SAFE,
                package_name="Microsoft.GetHelp",
                process_name=None,
                service_name=None,
                registry_keys=[],
                removal_commands=[
                    "Get-AppxPackage -Name 'Microsoft.GetHelp' | Remove-AppxPackage"
                ],
                can_reinstall=True
            ),
            BloatwareItem(
                id="mixed_reality",
                name="Portal de Realidade Mista",
                description="Para headsets VR/AR. Inútil se você não tem um.",
                category=Category.MICROSOFT_APPS,
                risk_level=RiskLevel.SAFE,
                package_name="Microsoft.MixedReality.Portal",
                process_name=None,
                service_name=None,
                registry_keys=[],
                removal_commands=[
                    "Get-AppxPackage -Name 'Microsoft.MixedReality.Portal' | Remove-AppxPackage"
                ],
                can_reinstall=True
            ),
            BloatwareItem(
                id="people",
                name="Pessoas",
                description="App de contatos integrado. Pouco usado.",
                category=Category.MICROSOFT_APPS,
                risk_level=RiskLevel.SAFE,
                package_name="Microsoft.People",
                process_name=None,
                service_name=None,
                registry_keys=[],
                removal_commands=[
                    "Get-AppxPackage -Name 'Microsoft.People' | Remove-AppxPackage"
                ],
                can_reinstall=True
            ),
            BloatwareItem(
                id="skype",
                name="Skype",
                description="App de videochamadas. Substituído pelo Teams em muitos casos.",
                category=Category.MICROSOFT_APPS,
                risk_level=RiskLevel.SAFE,
                package_name="Microsoft.SkypeApp",
                process_name="Skype",
                service_name=None,
                registry_keys=[],
                removal_commands=[
                    "Get-AppxPackage -Name 'Microsoft.SkypeApp' | Remove-AppxPackage"
                ],
                can_reinstall=True
            ),
            BloatwareItem(
                id="phone_link",
                name="Phone Link (Seu Telefone)",
                description="Conecta seu celular ao PC. Remove se não usa.",
                category=Category.MICROSOFT_APPS,
                risk_level=RiskLevel.SAFE,
                package_name="Microsoft.YourPhone",
                process_name="PhoneExperienceHost",
                service_name=None,
                registry_keys=[],
                removal_commands=[
                    "Get-AppxPackage -Name 'Microsoft.YourPhone' | Remove-AppxPackage"
                ],
                can_reinstall=True
            ),
            BloatwareItem(
                id="zune_music",
                name="Groove Music",
                description="Player de música da Microsoft. Alternativas melhores existem.",
                category=Category.MICROSOFT_APPS,
                risk_level=RiskLevel.SAFE,
                package_name="Microsoft.ZuneMusic",
                process_name=None,
                service_name=None,
                registry_keys=[],
                removal_commands=[
                    "Get-AppxPackage -Name 'Microsoft.ZuneMusic' | Remove-AppxPackage"
                ],
                can_reinstall=True
            ),
            BloatwareItem(
                id="zune_video",
                name="Filmes e TV",
                description="Player de vídeo da Microsoft. VLC é melhor.",
                category=Category.MICROSOFT_APPS,
                risk_level=RiskLevel.SAFE,
                package_name="Microsoft.ZuneVideo",
                process_name=None,
                service_name=None,
                registry_keys=[],
                removal_commands=[
                    "Get-AppxPackage -Name 'Microsoft.ZuneVideo' | Remove-AppxPackage"
                ],
                can_reinstall=True
            ),
            BloatwareItem(
                id="maps",
                name="Mapas",
                description="App de mapas offline. Google Maps é mais usado.",
                category=Category.MICROSOFT_APPS,
                risk_level=RiskLevel.SAFE,
                package_name="Microsoft.WindowsMaps",
                process_name=None,
                service_name=None,
                registry_keys=[],
                removal_commands=[
                    "Get-AppxPackage -Name 'Microsoft.WindowsMaps' | Remove-AppxPackage"
                ],
                can_reinstall=True
            ),
            BloatwareItem(
                id="feedback_hub",
                name="Hub de Feedback",
                description="Para enviar feedback à Microsoft. Raramente usado.",
                category=Category.MICROSOFT_APPS,
                risk_level=RiskLevel.SAFE,
                package_name="Microsoft.WindowsFeedbackHub",
                process_name=None,
                service_name=None,
                registry_keys=[],
                removal_commands=[
                    "Get-AppxPackage -Name 'Microsoft.WindowsFeedbackHub' | Remove-AppxPackage"
                ],
                can_reinstall=True
            ),
            BloatwareItem(
                id="sound_recorder",
                name="Gravador de Voz",
                description="Gravador de áudio simples.",
                category=Category.MICROSOFT_APPS,
                risk_level=RiskLevel.SAFE,
                package_name="Microsoft.WindowsSoundRecorder",
                process_name=None,
                service_name=None,
                registry_keys=[],
                removal_commands=[
                    "Get-AppxPackage -Name 'Microsoft.WindowsSoundRecorder' | Remove-AppxPackage"
                ],
                can_reinstall=True
            ),
            BloatwareItem(
                id="quick_assist",
                name="Assistência Rápida",
                description="Suporte remoto da Microsoft. Útil apenas para suporte técnico.",
                category=Category.MICROSOFT_APPS,
                risk_level=RiskLevel.SAFE,
                package_name="MicrosoftCorporationII.QuickAssist",
                process_name=None,
                service_name=None,
                registry_keys=[],
                removal_commands=[
                    "Get-AppxPackage -Name 'MicrosoftCorporationII.QuickAssist' | Remove-AppxPackage"
                ],
                can_reinstall=True
            ),
            BloatwareItem(
                id="dev_home",
                name="Dev Home",
                description="Hub para desenvolvedores. Inútil para usuários comuns.",
                category=Category.MICROSOFT_APPS,
                risk_level=RiskLevel.SAFE,
                package_name="Microsoft.Windows.DevHome",
                process_name=None,
                service_name=None,
                registry_keys=[],
                removal_commands=[
                    "Get-AppxPackage -Name 'Microsoft.Windows.DevHome' | Remove-AppxPackage"
                ],
                can_reinstall=True
            ),
            BloatwareItem(
                id="clipchamp",
                name="Clipchamp",
                description="Editor de vídeo da Microsoft. Alternativas melhores existem.",
                category=Category.MICROSOFT_APPS,
                risk_level=RiskLevel.SAFE,
                package_name="Clipchamp.Clipchamp",
                process_name=None,
                service_name=None,
                registry_keys=[],
                removal_commands=[
                    "Get-AppxPackage -Name 'Clipchamp.Clipchamp' | Remove-AppxPackage"
                ],
                can_reinstall=True
            ),
            BloatwareItem(
                id="onedrive",
                name="OneDrive",
                description="Armazenamento na nuvem. Remove se usa outra solução.",
                category=Category.MICROSOFT_APPS,
                risk_level=RiskLevel.CAUTION,
                package_name="Microsoft.OneDriveSync",
                process_name="OneDrive",
                service_name=None,
                registry_keys=[
                    "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run",
                    "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\OneDrive"
                ],
                removal_commands=[
                    "Stop-Process -Name 'OneDrive' -Force -ErrorAction SilentlyContinue",
                    "Start-Process -FilePath \"$env:SystemRoot\\SysWOW64\\OneDriveSetup.exe\" -ArgumentList '/uninstall' -Wait"
                ],
                can_reinstall=True
            ),
            BloatwareItem(
                id="teams",
                name="Microsoft Teams",
                description="App de comunicação. Remove se não usa para trabalho.",
                category=Category.MICROSOFT_APPS,
                risk_level=RiskLevel.SAFE,
                package_name="MicrosoftTeams",
                process_name="Teams",
                service_name=None,
                registry_keys=[],
                removal_commands=[
                    "Get-AppxPackage -Name '*Teams*' | Remove-AppxPackage"
                ],
                can_reinstall=True
            ),
            BloatwareItem(
                id="xbox_apps",
                name="Xbox Apps (Game Bar, etc)",
                description="Apps Xbox. Remove se não joga no PC.",
                category=Category.MICROSOFT_APPS,
                risk_level=RiskLevel.CAUTION,
                package_name="Microsoft.XboxGamingOverlay",
                process_name="GameBar",
                service_name=None,
                registry_keys=[],
                removal_commands=[
                    "Get-AppxPackage -Name '*Xbox*' | Remove-AppxPackage"
                ],
                can_reinstall=True
            ),
            BloatwareItem(
                id="news",
                name="Microsoft News",
                description="App de notícias. Consome recursos em segundo plano.",
                category=Category.MICROSOFT_APPS,
                risk_level=RiskLevel.SAFE,
                package_name="Microsoft.BingNews",
                process_name=None,
                service_name=None,
                registry_keys=[],
                removal_commands=[
                    "Get-AppxPackage -Name 'Microsoft.BingNews' | Remove-AppxPackage"
                ],
                can_reinstall=True
            ),
            BloatwareItem(
                id="todo",
                name="Microsoft To Do",
                description="App de tarefas. Remove se usa outras ferramentas.",
                category=Category.MICROSOFT_APPS,
                risk_level=RiskLevel.SAFE,
                package_name="Microsoft.Todos",
                process_name=None,
                service_name=None,
                registry_keys=[],
                removal_commands=[
                    "Get-AppxPackage -Name 'Microsoft.Todos' | Remove-AppxPackage"
                ],
                can_reinstall=True
            ),
            BloatwareItem(
                id="solitaire",
                name="Solitaire Collection",
                description="Jogos de paciência. Contém anúncios.",
                category=Category.MICROSOFT_APPS,
                risk_level=RiskLevel.SAFE,
                package_name="Microsoft.MicrosoftSolitaireCollection",
                process_name=None,
                service_name=None,
                registry_keys=[],
                removal_commands=[
                    "Get-AppxPackage -Name 'Microsoft.MicrosoftSolitaireCollection' | Remove-AppxPackage"
                ],
                can_reinstall=True
            ),
        ])

        # ===== SERVIÇOS =====
        self.items.extend([
            BloatwareItem(
                id="wsearch",
                name="Windows Search (Indexação)",
                description="Indexa arquivos para busca rápida. Consome RAM e disco.",
                category=Category.SERVICES,
                risk_level=RiskLevel.CAUTION,
                package_name=None,
                process_name="SearchIndexer",
                service_name="WSearch",
                registry_keys=[],
                removal_commands=[
                    "Stop-Service -Name 'WSearch' -Force",
                    "Set-Service -Name 'WSearch' -StartupType Disabled"
                ],
                can_reinstall=True
            ),
            BloatwareItem(
                id="sysmain",
                name="SysMain (Superfetch)",
                description="Pré-carrega apps na RAM. Pode ser pesado em SSDs.",
                category=Category.SERVICES,
                risk_level=RiskLevel.CAUTION,
                package_name=None,
                process_name=None,
                service_name="SysMain",
                registry_keys=[],
                removal_commands=[
                    "Stop-Service -Name 'SysMain' -Force",
                    "Set-Service -Name 'SysMain' -StartupType Disabled"
                ],
                can_reinstall=True
            ),
            BloatwareItem(
                id="diagtrack",
                name="Telemetria (DiagTrack)",
                description="Coleta dados para Microsoft. Privacidade questionável.",
                category=Category.SERVICES,
                risk_level=RiskLevel.SAFE,
                package_name=None,
                process_name=None,
                service_name="DiagTrack",
                registry_keys=[
                    "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection"
                ],
                removal_commands=[
                    "Stop-Service -Name 'DiagTrack' -Force",
                    "Set-Service -Name 'DiagTrack' -StartupType Disabled"
                ],
                can_reinstall=True
            ),
            BloatwareItem(
                id="dmwappushservice",
                name="Push de Diagnóstico",
                description="Envia dados de diagnóstico à Microsoft.",
                category=Category.SERVICES,
                risk_level=RiskLevel.SAFE,
                package_name=None,
                process_name=None,
                service_name="dmwappushservice",
                registry_keys=[],
                removal_commands=[
                    "Stop-Service -Name 'dmwappushservice' -Force",
                    "Set-Service -Name 'dmwappushservice' -StartupType Disabled"
                ],
                can_reinstall=True
            ),
            BloatwareItem(
                id="xbox_services",
                name="Serviços Xbox",
                description="Serviços para jogos Xbox. Remove se não joga.",
                category=Category.SERVICES,
                risk_level=RiskLevel.SAFE,
                package_name=None,
                process_name=None,
                service_name="XblAuthManager",
                registry_keys=[],
                removal_commands=[
                    "Get-Service -Name 'Xbl*' | Stop-Service -Force",
                    "Get-Service -Name 'Xbl*' | Set-Service -StartupType Disabled"
                ],
                can_reinstall=True
            ),
        ])

        # ===== PROCESSOS =====
        self.items.extend([
            BloatwareItem(
                id="edge_webview",
                name="Edge WebView2",
                description="Componente do Edge usado por alguns apps. Pode ser pesado.",
                category=Category.PROCESSES,
                risk_level=RiskLevel.RISKY,
                package_name=None,
                process_name="msedgewebview2",
                service_name=None,
                registry_keys=[
                    "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Image File Execution Options\\msedgewebview2.exe"
                ],
                removal_commands=[
                    "Stop-Process -Name 'msedgewebview2' -Force",
                    "New-Item -Path 'HKLM:\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Image File Execution Options\\msedgewebview2.exe' -Force",
                    "Set-ItemProperty -Path 'HKLM:\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Image File Execution Options\\msedgewebview2.exe' -Name 'Debugger' -Value 'systray.exe'"
                ],
                can_reinstall=True
            ),
            BloatwareItem(
                id="search_host",
                name="SearchHost",
                description="Interface de pesquisa do Windows. Usa Edge WebView.",
                category=Category.PROCESSES,
                risk_level=RiskLevel.RISKY,
                package_name=None,
                process_name="SearchHost",
                service_name=None,
                registry_keys=[
                    "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Image File Execution Options\\SearchHost.exe"
                ],
                removal_commands=[
                    "Stop-Process -Name 'SearchHost' -Force",
                    "New-Item -Path 'HKLM:\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Image File Execution Options\\SearchHost.exe' -Force",
                    "Set-ItemProperty -Path 'HKLM:\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Image File Execution Options\\SearchHost.exe' -Name 'Debugger' -Value 'systray.exe'"
                ],
                can_reinstall=True
            ),
            BloatwareItem(
                id="cross_device",
                name="CrossDevice (Sincronização)",
                description="Sincronização entre dispositivos Windows. Consome recursos.",
                category=Category.PROCESSES,
                risk_level=RiskLevel.SAFE,
                package_name=None,
                process_name="CrossDeviceResume",
                service_name="CrossDeviceExperienceHost",
                registry_keys=[
                    "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\CDP"
                ],
                removal_commands=[
                    "Stop-Process -Name 'CrossDeviceResume' -Force",
                    "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\CDP' -Name 'CdpSessionUserAuthzPolicy' -Value 0",
                    "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\CDP' -Name 'NearShareChannelUserAuthzPolicy' -Value 0"
                ],
                can_reinstall=True
            ),
        ])

        # ===== FABRICANTES =====
        self.items.extend([
            BloatwareItem(
                id="hp_bloat",
                name="HP Bloatware",
                description="Apps pré-instalados da HP. Geralmente inúteis.",
                category=Category.MANUFACTURER,
                risk_level=RiskLevel.SAFE,
                package_name="AD2F1837.HPPrinterControl",
                process_name=None,
                service_name=None,
                registry_keys=[],
                removal_commands=[
                    "Get-AppxPackage -Name '*HP*' | Remove-AppxPackage"
                ],
                can_reinstall=True
            ),
            BloatwareItem(
                id="dell_bloat",
                name="Dell Bloatware",
                description="Apps pré-instalados da Dell.",
                category=Category.MANUFACTURER,
                risk_level=RiskLevel.SAFE,
                package_name=None,
                process_name=None,
                service_name=None,
                registry_keys=[],
                removal_commands=[
                    "Get-AppxPackage -Name '*Dell*' | Remove-AppxPackage"
                ],
                can_reinstall=True
            ),
            BloatwareItem(
                id="lenovo_bloat",
                name="Lenovo Bloatware",
                description="Apps pré-instalados da Lenovo.",
                category=Category.MANUFACTURER,
                risk_level=RiskLevel.SAFE,
                package_name=None,
                process_name=None,
                service_name=None,
                registry_keys=[],
                removal_commands=[
                    "Get-AppxPackage -Name '*Lenovo*' | Remove-AppxPackage"
                ],
                can_reinstall=True
            ),
            BloatwareItem(
                id="acer_bloat",
                name="Acer Bloatware",
                description="Apps pré-instalados da Acer.",
                category=Category.MANUFACTURER,
                risk_level=RiskLevel.SAFE,
                package_name=None,
                process_name=None,
                service_name=None,
                registry_keys=[],
                removal_commands=[
                    "Get-AppxPackage -Name '*Acer*' | Remove-AppxPackage"
                ],
                can_reinstall=True
            ),
            BloatwareItem(
                id="asus_bloat",
                name="ASUS Bloatware",
                description="Apps pré-instalados da ASUS.",
                category=Category.MANUFACTURER,
                risk_level=RiskLevel.SAFE,
                package_name=None,
                process_name=None,
                service_name=None,
                registry_keys=[],
                removal_commands=[
                    "Get-AppxPackage -Name '*ASUS*' | Remove-AppxPackage"
                ],
                can_reinstall=True
            ),
        ])

    def get_all(self) -> List[BloatwareItem]:
        """Retorna todos os bloatwares."""
        return self.items

    def get_by_category(self, category: Category) -> List[BloatwareItem]:
        """Retorna bloatwares de uma categoria específica."""
        return [item for item in self.items if item.category == category]

    def get_by_risk(self, risk_level: RiskLevel) -> List[BloatwareItem]:
        """Retorna bloatwares de um nível de risco específico."""
        return [item for item in self.items if item.risk_level == risk_level]

    def get_safe_items(self) -> List[BloatwareItem]:
        """Retorna apenas itens seguros para remoção."""
        return self.get_by_risk(RiskLevel.SAFE)

    def get_by_id(self, item_id: str) -> Optional[BloatwareItem]:
        """Retorna um item pelo ID."""
        for item in self.items:
            if item.id == item_id:
                return item
        return None

    def search(self, query: str) -> List[BloatwareItem]:
        """Busca bloatwares por nome ou descrição."""
        query = query.lower()
        return [
            item for item in self.items
            if query in item.name.lower() or query in item.description.lower()
        ]
