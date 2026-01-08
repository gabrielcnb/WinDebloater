"""
Verificação e resolução de incompatibilidades do sistema.
"""
import subprocess
import platform
import sys
import os
from typing import List, Tuple, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.powershell import PowerShell


class Compatibility:
    """Classe para verificar e resolver incompatibilidades."""

    # Lista de antivírus conhecidos que podem interferir
    KNOWN_ANTIVIRUS = [
        "avast", "avg", "norton", "mcafee", "kaspersky",
        "bitdefender", "malwarebytes", "avira", "eset",
        "trend micro", "webroot", "sophos", "f-secure"
    ]

    # Processos que podem bloquear operações
    BLOCKING_PROCESSES = [
        "MsMpEng",  # Windows Defender
        "NisSrv",   # Windows Defender Network
    ]

    @staticmethod
    def get_windows_version() -> Tuple[str, int]:
        """
        Retorna versão do Windows.

        Returns:
            Tupla (nome_versao, build_number)
        """
        version = platform.version()
        release = platform.release()

        try:
            build = int(version.split('.')[2])
        except (IndexError, ValueError):
            build = 0

        return f"Windows {release}", build

    @staticmethod
    def is_windows_11() -> bool:
        """Verifica se é Windows 11."""
        _, build = Compatibility.get_windows_version()
        return build >= 22000

    @staticmethod
    def is_windows_10() -> bool:
        """Verifica se é Windows 10."""
        _, build = Compatibility.get_windows_version()
        return 10240 <= build < 22000

    @staticmethod
    def check_antivirus() -> List[str]:
        """
        Detecta antivírus instalados que podem interferir.

        Returns:
            Lista de nomes de antivírus detectados.
        """
        detected = []

        # Verifica via WMI
        command = """
        Get-CimInstance -Namespace root/SecurityCenter2 -ClassName AntivirusProduct |
        Select-Object displayName | ConvertTo-Json
        """
        success, data = PowerShell.get_json(command)

        if success and data:
            if isinstance(data, dict):
                data = [data]

            for av in data:
                name = av.get('displayName', '').lower()
                for known in Compatibility.KNOWN_ANTIVIRUS:
                    if known in name:
                        detected.append(av.get('displayName', known))
                        break

        return detected

    @staticmethod
    def check_defender_status() -> Tuple[bool, bool]:
        """
        Verifica status do Windows Defender.

        Returns:
            Tupla (defender_ativo, proteção_tempo_real)
        """
        command = """
        $status = Get-MpComputerStatus
        @{
            Enabled = $status.AntivirusEnabled
            RealTimeProtection = $status.RealTimeProtectionEnabled
        } | ConvertTo-Json
        """
        success, data = PowerShell.get_json(command)

        if success and data:
            return data.get('Enabled', True), data.get('RealTimeProtection', True)

        return True, True  # Assume ativo se não conseguir verificar

    @staticmethod
    def check_tamper_protection() -> bool:
        """Verifica se Tamper Protection está ativo."""
        command = """
        (Get-MpComputerStatus).IsTamperProtected
        """
        success, stdout, _ = PowerShell.run(command)
        return "True" in stdout if success else True

    @staticmethod
    def get_blocking_processes() -> List[dict]:
        """
        Retorna processos que podem bloquear operações.

        Returns:
            Lista de dicts com info dos processos.
        """
        blocking = []
        processes = PowerShell.get_processes()

        for proc in processes:
            name = proc.get('Name', '')
            if name in Compatibility.BLOCKING_PROCESSES:
                blocking.append(proc)

        return blocking

    @staticmethod
    def check_compatibility() -> List[Tuple[str, str, str]]:
        """
        Verifica todas as compatibilidades.

        Returns:
            Lista de tuplas (item, status, recomendação)
        """
        issues = []

        # Windows version
        version, build = Compatibility.get_windows_version()
        if build < 10240:
            issues.append((
                "Windows Version",
                f"{version} (Build {build})",
                "Requer Windows 10 ou superior"
            ))
        else:
            issues.append((
                "Windows Version",
                f"{version} (Build {build})",
                "OK"
            ))

        # Antivírus
        antivirus = Compatibility.check_antivirus()
        if antivirus:
            for av in antivirus:
                issues.append((
                    "Antivírus",
                    av,
                    "Pode interferir na remoção. Desative temporariamente se houver problemas."
                ))

        # Windows Defender
        defender_on, realtime_on = Compatibility.check_defender_status()
        if realtime_on:
            issues.append((
                "Windows Defender",
                "Proteção em tempo real ativa",
                "Pode bloquear algumas operações"
            ))

        # Tamper Protection
        if Compatibility.check_tamper_protection():
            issues.append((
                "Tamper Protection",
                "Ativo",
                "Impede desativação do Defender via script"
            ))

        return issues

    @staticmethod
    def temporarily_disable_defender() -> Tuple[bool, str]:
        """
        Tenta desativar temporariamente o Defender.
        NOTA: Requer que Tamper Protection esteja desativado manualmente.

        Returns:
            Tupla (sucesso, mensagem)
        """
        command = """
        Set-MpPreference -DisableRealtimeMonitoring $true
        """
        success, _, stderr = PowerShell.run(command)

        if success:
            return True, "Proteção em tempo real desativada temporariamente"
        else:
            return False, f"Não foi possível desativar: {stderr}"

    @staticmethod
    def enable_defender() -> Tuple[bool, str]:
        """Reativa o Windows Defender."""
        command = """
        Set-MpPreference -DisableRealtimeMonitoring $false
        """
        success, _, stderr = PowerShell.run(command)

        if success:
            return True, "Proteção em tempo real reativada"
        else:
            return False, f"Erro ao reativar: {stderr}"


def check_compatibility() -> List[Tuple[str, str, str]]:
    """Função wrapper para verificação de compatibilidade."""
    return Compatibility.check_compatibility()


def fix_compatibility(issue_type: str) -> Tuple[bool, str]:
    """
    Tenta corrigir um problema de compatibilidade.

    Args:
        issue_type: Tipo do problema (ex: "defender")

    Returns:
        Tupla (sucesso, mensagem)
    """
    if issue_type.lower() == "defender":
        return Compatibility.temporarily_disable_defender()

    return False, f"Correção automática não disponível para: {issue_type}"
