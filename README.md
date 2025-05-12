# SteamLaunchOptions-GUI (Enhanced Proton Support)

This is a fork of [TimeFlex1's SteamLaunchOptions-GUI](https://github.com/TimeFlex1/SteamLaunchOptions-GUI) with enhanced Proton detection and UI improvements.

## Improvements in this Fork

1. **Enhanced Proton Detection**
   - Improved detection of Proton-GE (GloriousEggroll) versions
   - Added support for more installation paths
   - Better handling of nested directory structures
   - Improved error handling for permissions issues

2. **UI Improvements**
   - Moved the "Launch with Proton" section to the bottom of the UI for better organization
   - Added a checkbox to use the generated command options when launching games
   - Enhanced refresh functionality with better feedback
   - Fixed SteamID display issues

3. **Code Improvements**
   - Better logging for debugging
   - More robust error handling
   - Improved parsing of Steam configuration files

## Original Description

A GUI for configuring Steam launch options, with a focus on Linux gaming with Proton.

This tool helps you:
- Configure Steam launch options with an easy-to-use interface
- Detect and use Proton versions, including custom ones like Proton-GE
- Save and load launch option profiles
- Launch games directly with specific Proton versions

## Requirements

- Python 3.6+
- GTK 3.0
- Steam installed on your system

## Installation

### Recommended Method: Portable Script

1. Clone this repository:
   ```
   git clone https://github.com/childoftherion/SteamLaunchOptions-GUI.git
   ```

2. Make the portable script executable:
   ```
   chmod +x RunPortable.sh
   ```

3. Run the application using the portable script:
   ```
   ./RunPortable.sh
   ```

The portable script automatically sets up a virtual environment, installs dependencies, and launches the application.

### Alternative Method: Manual Installation

1. Clone this repository:
   ```
   git clone https://github.com/childoftherion/SteamLaunchOptions-GUI.git
   ```

2. Install the requirements:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   python steam_launcher.py
   ```

## License

This project is licensed under the same license as the original project by TimeFlex1.
