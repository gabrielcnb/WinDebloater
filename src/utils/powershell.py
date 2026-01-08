"""
Wrapper para execução de comandos PowerShell.
"""
import subprocess
import json
from typing import Optional, Tuple, List, Any


class PowerShell:
    """Classe para executar comandos PowerShell de forma segura."""

    @staticmethod
    def run(command: str, timeout: int = 60, capture_output: bool = True) -> Tuple[bool, str, str]:
        """
        Executa um comando PowerShell.

        Args:
            command: Comando PowerShell a executar.
            timeout: Timeout em segundos.
            capture_output: Se deve capturar stdout/stderr.

        Returns:
            Tupla (sucesso, stdout, stderr)
        """
        try:
            # Constrói o comando completo
            full_command = [
                "powershell.exe",
                "-NoProfile",
                "-NonInteractive",
                "-ExecutionPolicy", "Bypass",
                "-Command", command
            ]

            result = subprocess.run(
                full_command,
                capture_output=capture_output,
                text=True,
                timeout=timeout,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            success = result.returncode == 0
            stdout = result.stdout.strip() if result.stdout else ""
            stderr = result.stderr.strip() if result.stderr else ""

            return success, stdout, stderr

        except subprocess.TimeoutExpired:
            return False, "", "Comando excedeu o tempo limite"
        except Exception as e:
            return False, "", str(e)

    @staticmethod
    def run_script(script_path: str, timeout: int = 120) -> Tuple[bool, str, str]:
        """
        Executa um script PowerShell de um arquivo.

        Args:
            script_path: Caminho do script .ps1
            timeout: Timeout em segundos.

        Returns:
            Tupla (sucesso, stdout, stderr)
        """
        command = f'& "{script_path}"'
        return PowerShell.run(command, timeout)

    @staticmethod
    def get_json(command: str, timeout: int = 60) -> Tuple[bool, Any]:
        """
        Executa comando que retorna JSON e faz parse.

        Args:
            command: Comando PowerShell que retorna JSON.
            timeout: Timeout em segundos.

        Returns:
            Tupla (sucesso, dados_parseados)
        """
        # Adiciona ConvertTo-Json se não tiver
        if "ConvertTo-Json" not in command:
            command = f"({command}) | ConvertTo-Json -Depth 10"

        success, stdout, stderr = PowerShell.run(command, timeout)

        if not success or not stdout:
            return False, None

        try:
            data = json.loads(stdout)
            return True, data
        except json.JSONDecodeError:
            return False, None

    @staticmethod
    def get_appx_packages() -> List[dict]:
        """Retorna lista de pacotes AppX instalados."""
        command = "Get-AppxPackage | Select-Object Name, PackageFullName, Version | ConvertTo-Json"
        success, data = PowerShell.get_json(command)

        if success and data:
            # Garante que é uma lista
            if isinstance(data, dict):
                return [data]
            return data
        return []

    @staticmethod
    def get_processes() -> List[dict]:
        """Retorna lista de processos em execução."""
        command = """
        Get-Process | Select-Object Name, Id,
            @{Name='RAM_MB';Expression={[math]::Round($_.WorkingSet64/1MB,1)}},
            @{Name='CPU_s';Expression={[math]::Round($_.CPU,1)}},
            Description | ConvertTo-Json
        """
        success, data = PowerShell.get_json(command, timeout=30)

        if success and data:
            if isinstance(data, dict):
                return [data]
            return data
        return []

    @staticmethod
    def get_services() -> List[dict]:
        """Retorna lista de serviços do Windows."""
        command = "Get-Service | Select-Object Name, DisplayName, Status, StartType | ConvertTo-Json"
        success, data = PowerShell.get_json(command)

        if success and data:
            if isinstance(data, dict):
                return [data]
            return data
        return []

    @staticmethod
    def get_startup_items() -> List[dict]:
        """Retorna itens de inicialização."""
        command = """
        $items = @()

        # Registro HKCU
        $hkcu = Get-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Run' -ErrorAction SilentlyContinue
        if ($hkcu) {
            $hkcu.PSObject.Properties | Where-Object { $_.Name -notlike 'PS*' } | ForEach-Object {
                $items += @{Name=$_.Name; Path=$_.Value; Location='HKCU'}
            }
        }

        # Registro HKLM
        $hklm = Get-ItemProperty -Path 'HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Run' -ErrorAction SilentlyContinue
        if ($hklm) {
            $hklm.PSObject.Properties | Where-Object { $_.Name -notlike 'PS*' } | ForEach-Object {
                $items += @{Name=$_.Name; Path=$_.Value; Location='HKLM'}
            }
        }

        $items | ConvertTo-Json
        """
        success, data = PowerShell.get_json(command)

        if success and data:
            if isinstance(data, dict):
                return [data]
            return data
        return []

    @staticmethod
    def remove_appx_package(package_name: str, all_users: bool = False) -> Tuple[bool, str]:
        """Remove um pacote AppX."""
        if all_users:
            command = f"Get-AppxPackage -Name '{package_name}' -AllUsers | Remove-AppxPackage -AllUsers"
        else:
            command = f"Get-AppxPackage -Name '{package_name}' | Remove-AppxPackage"

        success, stdout, stderr = PowerShell.run(command)
        return success, stderr if not success else "Removido com sucesso"

    @staticmethod
    def stop_process(process_name: str) -> Tuple[bool, str]:
        """Encerra um processo pelo nome."""
        command = f"Stop-Process -Name '{process_name}' -Force -ErrorAction SilentlyContinue"
        success, stdout, stderr = PowerShell.run(command)
        return success, stderr if not success else "Processo encerrado"

    @staticmethod
    def set_service_startup(service_name: str, startup_type: str = "Disabled") -> Tuple[bool, str]:
        """Altera o tipo de inicialização de um serviço."""
        command = f"Set-Service -Name '{service_name}' -StartupType {startup_type} -ErrorAction SilentlyContinue"
        success, stdout, stderr = PowerShell.run(command)
        return success, stderr if not success else f"Serviço configurado para {startup_type}"

    @staticmethod
    def stop_service(service_name: str) -> Tuple[bool, str]:
        """Para um serviço."""
        command = f"Stop-Service -Name '{service_name}' -Force -ErrorAction SilentlyContinue"
        success, stdout, stderr = PowerShell.run(command)
        return success, stderr if not success else "Serviço parado"
