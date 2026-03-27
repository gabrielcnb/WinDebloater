# WinDebloater

Safely remove Windows 10/11 bloatware with persistence.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Windows](https://img.shields.io/badge/Windows-10%2F11-0078D6.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## Features

- **Automatic scanning** - Detects installed bloatware, running processes, and services
- **Persistent removal** - Uses 8 cascading techniques to ensure complete removal
- **Custom processes** - Add processes that keep coming back, with protection against removing critical system processes
- **Automatic backup** - Creates a backup before any changes are made
- **Easy restoration** - Restore removed items with a single click
- **User-friendly interface** - Modern dark theme, easy to use
- **Risk levels** - Identifies safe, cautionary, and risky items

## Supported Bloatware

### Microsoft Apps
- Bing Search, Weather, News
- Cortana
- OneDrive
- Skype, Teams
- Xbox Apps
- Groove Music, Movies & TV
- Phone Link, People, Maps
- And more...

### Services
- Windows Search (Indexing)
- Telemetry (DiagTrack)
- SysMain (Superfetch)
- Xbox Services

### Processes
- Edge WebView2
- SearchHost
- CrossDevice

### Manufacturer Bloatware
- HP, Dell, Lenovo, Acer, ASUS bloatware

## Installation

### Requirements
- Windows 10/11
- Python 3.10 or higher
- Administrator privileges

### Quick Installation

1. Clone the repository:
```bash
git clone https://github.com/gabrielcnb/WinDebloater.git
cd WinDebloater
```

2. Run the installer:
```bash
setup.bat
```

3. Or install manually:
```bash
pip install -r requirements.txt
python src/main.py
```

## Usage

1. Run `run.bat` or `python src/main.py`
2. The program will request administrator privileges
3. Click **Scan** to detect bloatware
4. Select the items you wish to remove
5. Click **Remove**
6. Done.

### Risk Levels

| Level | Description |
|-------|-------------|
| Safe | Can be removed without issues |
| Caution | May affect some functionality |
| Risky | May cause system instability |

### Adding Custom Processes

If a process keeps returning after removal:

1. Click **Add Process**
2. Enter the process name (without .exe)
3. The system validates automatically:
   - **Green** - Process can be safely removed
   - **Orange** - Attention required (common application)
   - **Red** - Blocked (critical Windows process)
4. Add an optional description
5. Confirm the addition

**Safety Protection**: The system automatically blocks critical Windows processes (explorer, svchost, csrss, etc.) to prevent system damage.

## Removal Techniques

WinDebloater uses 8 cascading techniques to ensure removal:

1. `Remove-AppxPackage` (current user)
2. `Remove-AppxPackage -AllUsers` (all users)
3. `Remove-AppxProvisionedPackage` (prevents reinstallation)
4. Disable service
5. Terminate process and remove from startup
6. Disable scheduled tasks
7. IFEO (Image File Execution Options)
8. Rename executable (last resort)

## Restoration

If something goes wrong:

1. Click **Restore**
2. Select a backup point
3. Confirm the restoration

## Project Structure

```
WinDebloater/
├── src/
│   ├── main.py           # Entry point
│   ├── ui/               # Graphical interface
│   ├── core/             # Core logic
│   └── utils/            # Utilities
├── assets/               # Icons and resources
├── backups/              # Automatic backups
├── requirements.txt
├── setup.bat
└── run.bat
```

## Contributing

Contributions are welcome. Please follow these steps:

1. Fork the project
2. Create a branch for your feature (`git checkout -b feature/NewFeature`)
3. Commit your changes (`git commit -m 'Add NewFeature'`)
4. Push to the branch (`git push origin feature/NewFeature`)
5. Open a Pull Request

## Disclaimer

Use at your own risk. The author is not responsible for any damage caused by the use of this software. Always back up your system before use.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
