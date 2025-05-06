print("Starting Steam Launcher...")
# Import necessary libraries
import gi
# Ensure Gtk 3.0 is available
try:
    gi.require_version("Gtk", "3.0")
    from gi.repository import Gtk, Gdk, GLib  # Added GLib for idle_add
except ValueError as e:
    print(f"Error importing GTK 3.0: {e}")
    print("Please ensure you have the GTK 3.0 development libraries installed.")
    print("On Debian/Ubuntu: sudo apt-get install libgtk-3-dev python3-gi python3-gi-cairo gir1.2-gtk-3.0")
    print("On Fedora: sudo dnf install gtk3-devel python3-gobject python3-cairo")
    print("On Arch Linux: sudo pacman -S gtk3 python-gobject")
    exit(1)

import subprocess
import os
import json
import shlex  # For parsing custom arguments
import pexpect  # User's original code uses pexpect for sudo password
import logging  # For debugging
from collections import defaultdict
import uuid

# SECTION: CONSTANTS
SETTINGS_FILE = "steam_launcher_settings.json"
LOG_FILE = 'steam_launcher.log'

# SECTION: LOGGING SETUP
# Configure logging to debug issues with detection
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logging.info("Steam Launcher application started.")

# SECTION: TAB CONFIGURATIONS
# Define configuration for all tabs (e.g., Wine, MangoHud, etc.)
TAB_CONFIGS = {
    "Wine": {
        "enable_label": "Enable Wine",
        "enable_tooltip": "Enable Wine environment settings",
        "env_prefix": "",  # Wine env vars don't have a common prefix like WINE_
        "toggles": [
            ("WINEESYNC", "Enable explicit synchronization for Wine"),
            ("WINEFSYNC", "Enable frame synchronization for Wine"),
            ("WINELOADERDEBUG", "Enable Wine loader debugging"),
            ("WINELOADERNOEXEC", "Disable Wine loader execution"),
        ],
        "inputs": [
            ("WINEPREFIX", "Path to Wine prefix", "e.g., /path/to/prefix"),
            ("WINEARCH", "Set Wine architecture", "e.g., win32"),
            ("WINEDLLOVERRIDES", "Override specific DLLs", "e.g., dxgi=n,b"),
            ("WINEDEBUG", "Set Wine debug level", "e.g., +relay"),
            ("WINELOGFILE", "Path to Wine log file", "e.g., /path/to/logfile"),
            ("WINESERVER", "Path to wineserver binary", "e.g., /path/to/wineserver"),
            ("WINELOADER", "Path to Wine loader", "e.g., /path/to/wine"),
            ("WINEDLLPATH", "Path to DLL directory", "e.g., /path/to/dlls"),
            ("WINEBIN", "Path to Wine binary", "e.g., /path/to/wine"),
        ],
    },
    "MangoHud": {
        "enable_label": "Enable MangoHud",
        "enable_tooltip": "Enable MangoHud overlay",
        "env_prefix": "",  # MangoHud env vars don't have a common prefix like MANGOHUD_
        "command_prefix": "mangohud",  # Command to prepend
        "toggles": [
            ("MANGOHUD", "Enable MangoHud overlay"),
            ("MANGOHUD_DLSYM", "Use dlsym to load MangoHud"),
            ("MANGOHUD_GAMEPAD", "Enable gamepad support in MangoHud"),
            ("MANGOHUD_LOG", "Enable logging for MangoHud"),
            ("MANGOHUD_HWINFO", "Display hardware information in MangoHud"),
            ("MANGOHUD_SHORT", "Display a shorter overlay in MangoHud"),
            ("MANGOHUD_FPS", "Display FPS in MangoHud"),
            ("MANGOHUD_GPU", "Display GPU usage in MangoHud"),
            ("MANGOHUD_CPU", "Display CPU usage in MangoHud"),
            ("MANGOHUD_VK", "Display Vulkan-specific information in MangoHud"),
            ("MANGOHUD_GL", "Display OpenGL-specific information in MangoHud"),
            ("MANGOHUD_MEMORY", "Display memory usage in MangoHud"),
            ("MANGOHUD_TEMP", "Display GPU temperature in MangoHud"),
            ("MANGOHUD_POWER", "Display GPU power usage in MangoHud"),
        ],
        "inputs": [
            ("MANGOHUD_CONFIG", "Path to custom MangoHud config file", "e.g., /path/to/config"),
            ("MANGOHUD_FPSAVERAGE", "Average FPS over frames", "e.g., 100"),
            ("MANGOHUD_FPS_LIMIT", "Set frame rate limit", "e.g., 60"),
            ("MANGOHUD_FPS_THRESHOLD", "Set FPS alert threshold", "e.g., 30"),
            ("MANGOHUD_COLOR", "Set overlay color", "e.g., #FF0000"),
            ("MANGOHUD_XOFFSET", "Adjust X offset of overlay", "e.g., 10"),
            ("MANGOHUD_YOFFSET", "Adjust Y offset of overlay", "e.g., 10"),
        ],
        "dropdowns": {
            "MANGOHUD_ALIGN": {
                "label": "ALIGN:",
                "options": ["bottom", "top", "left", "right"],
                "tooltip": "Align the MangoHud overlay",
                "default": "top",
            }
        },
        "software_requirement": "mangohud",
    },
    "vkBasalt": {
        "enable_label": "Enable vkBasalt",
        "enable_tooltip": "Enable vkBasalt effects",
        "env_prefix": "",  # vkBasalt env vars don't have a common prefix like VK_BASALT_
        "toggles": [
            ("VK_BASALT_DISABLE", "Disable vkBasalt effects"),
            ("VK_BASALT_SHARPEN", "Enable sharpening effect"),
            ("VK_BASALT_FXAA", "Enable fast approximate anti-aliasing"),
            ("VK_BASALT_SMAA", "Enable subpixel morphological anti-aliasing"),
            ("VK_BASALT_LUT", "Enable lookup table (LUT) color grading"),
            ("VK_BASALT_TONEMAP", "Enable tonemapping"),
            ("VK_BASALT_HDR", "Enable HDR support"),
            ("VK_BASALT_DITHER", "Enable dithering"),
            ("VK_BASALT_LUMINANCE", "Enable luminance adjustment"),
            ("VK_BASALT_COLOR", "Enable color adjustment"),
            ("VK_BASALT_BLOOM", "Enable bloom effect"),
            ("VK_BASALT_SSAO", "Enable screen-space ambient occlusion"),
            ("VK_BASALT_VIGNETTE", "Enable vignette effect"),
            ("VK_BASALT_CHROMATIC_ABER", "Enable chromatic aberration"),
            ("VK_BASALT_MOTION_BLUR", "Enable motion blur"),
        ],
        "inputs": [
            ("VK_BASALT_CONFIG", "Path to custom vkBasalt config file", "e.g., /path/to/config"),
            ("VK_BASALT_SHADERS", "Path to custom shaders", "e.g., /path/to/shaders"),
            ("AMD_VULKAN_ICD", "Force specific AMD Vulkan ICD", "e.g., RADV"),
            ("RADV_PERFTEST", "Set RADV performance tests", "e.g., rt,gpl"),
            ("RADV_DEBUG", "Set RADV debug options", "e.g., shader"),
            ("VKD3D_CONFIG", "Set VKD3D config options", "e.g., dxr12"),
        ],
        "sliders": [
            ("VK_BASALT_SHARPEN_STRENGTH", "Sharpening strength", 0.0, 1.0),
            ("VK_BASALT_FXAA_STRENGTH", "FXAA strength", 0.0, 1.0),
            ("VK_BASALT_SMAA_STRENGTH", "SMAA strength", 0.0, 1.0),
            ("VK_BASALT_LUT_STRENGTH", "LUT strength", 0.0, 1.0),
            ("VK_BASALT_TONEMAP_STRENGTH", "Tonemapping strength", 0.0, 1.0),
            ("VK_BASALT_HDR_STRENGTH", "HDR strength", 0.0, 1.0),
            ("VK_BASALT_DITHER_STRENGTH", "Dithering strength", 0.0, 1.0),
            ("VK_BASALT_LUMINANCE_STRENGTH", "Luminance strength", 0.0, 1.0),
            ("VK_BASALT_COLOR_STRENGTH", "Color strength", 0.0, 1.0),
            ("VK_BASALT_BLOOM_STRENGTH", "Bloom strength", 0.0, 1.0),
            ("VK_BASALT_SSAO_STRENGTH", "SSAO strength", 0.0, 1.0),
            ("VK_BASALT_VIGNETTE_STRENGTH", "Vignette strength", 0.0, 1.0),
            ("VK_BASALT_CHROMATIC_ABER_STRENGTH", "Chromatic aberration strength", 0.0, 1.0),
            ("VK_BASALT_MOTION_BLUR_STRENGTH", "Motion blur strength", 0.0, 1.0),
            ("VK_BASALT_SHARPEN_RADIUS", "Sharpening radius", 0.0, 10.0),
            ("VK_BASALT_FXAA_RADIUS", "FXAA radius", 0.0, 10.0),
            ("VK_BASALT_SMAA_RADIUS", "SMAA radius", 0.0, 10.0),
            ("VK_BASALT_LUT_RADIUS", "LUT radius", 0.0, 10.0),
            ("VK_BASALT_TONEMAP_RADIUS", "Tonemapping radius", 0.0, 10.0),
            ("VK_BASALT_HDR_RADIUS", "HDR radius", 0.0, 10.0),
            ("VK_BASALT_DITHER_RADIUS", "Dithering radius", 0.0, 10.0),
            ("VK_BASALT_LUMINANCE_RADIUS", "Luminance radius", 0.0, 10.0),
            ("VK_BASALT_COLOR_RADIUS", "Color radius", 0.0, 10.0),
            ("VK_BASALT_BLOOM_RADIUS", "Bloom radius", 0.0, 10.0),
            ("VK_BASALT_SSAO_RADIUS", "SSAO radius", 0.0, 10.0),
            ("VK_BASALT_VIGNETTE_RADIUS", "Vignette radius", 0.0, 10.0),
            ("VK_BASALT_CHROMATIC_ABER_RADIUS", "Chromatic aberration radius", 0.0, 10.0),
            ("VK_BASALT_MOTION_BLUR_RADIUS", "Motion blur radius", 0.0, 10.0),
        ],
        "software_requirement": "vkbasalt",
    },
    "GameMode": {
        "enable_label": "Enable GameMode",
        "enable_tooltip": "Enable GameMode optimization",
        "command_prefix": "gamemoderun",
        "toggles": [
            ("GAME_MODE", "Enable GameMode optimization"),
        ],
        "inputs": [],
        "software_requirement": "gamemoded",
    },
    "Gamescope": {
        "enable_label": "Enable Gamescope",
        "enable_tooltip": "Enable Gamescope",
        "command_prefix": "gamescope",
        "command_suffix": "--",
        "toggles": [
            ("-f", "Force full screen mode"),
            ("-b", "Enable borderless window mode"),
            ("-n", "Disable the gamescope compositor"),
            ("-c", "Enable VSync"),
            ("-q", "Enable quiet mode"),
        ],
        "inputs": [
            ("-W", "Set window width", "e.g., 1920"),
            ("-H", "Set window height", "e.g., 1080"),
            ("-r", "Set refresh rate", "e.g., 60"),
            ("-w", "Set game width", "e.g., 1920"),
            ("-h", "Set game height", "e.g., 1080"),
            ("-d", "Specify display", "e.g., :0"),
            ("-p", "Specify port", "e.g., 8080"),
            ("-x", "Set X offset", "e.g., 10"),
            ("-y", "Set Y offset", "e.g., 10"),
            ("--prefer-vk-device", "Prefer specific Vulkan device", "e.g., 0"),
            ("--steam", "Enable Steam integration features", ""),
        ],
        "dropdowns": {},
        "software_requirement": "gamescope",
    },
    "DXVK": {
        "enable_label": "Enable DXVK",
        "enable_tooltip": "Enable DXVK translation",
        "env_prefix": "",
        "toggles": [
            ("DXVK_HUD", "Enable DXVK HUD"),
            ("DXVK_ASYNC", "Enable asynchronous shader compilation"),
            ("DXVK_ENABLE_SHADER_CACHE", "Enable shader cache"),
            ("DXVK_SHADER_LOG", "Enable shader logging"),
            ("DXVK_DEBUG_SHADERS", "Enable shader debugging"),
            ("DXVK_ENABLE_SHADER_DEBUG_INFO", "Enable shader debug information"),
            ("DXVK_USE_D3D11_SWITCHABLE_GFX", "Enable D3D11 switchable graphics"),
            ("DXVK_USE_LINEAR_ALLOCATION", "Enable linear allocation"),
            ("DXVK_USE_STAGING_BUFFERS", "Enable staging buffers"),
            ("DXVK_USE_NONBLOCKING_THREADS", "Enable non-blocking threads"),
            ("DXVK_USE_ASYNC_PRESENT", "Enable asynchronous presentation"),
            ("DXVK_USE_SHADER_GFX9", "Enable shader compilation for GFX9"),
            ("DXVK_USE_SHADER_GFX10", "Enable shader compilation for GFX10"),
            ("DXVK_USE_SHADER_GFX10_3", "Enable shader compilation for GFX10.3"),
            ("DXVK_USE_SHADER_GFX11", "Enable shader compilation for GFX11"),
            ("DXVK_ENABLE_SHADER_OPTIMIZATIONS", "Enable shader optimizations"),
            ("DXVK_ENABLE_SHADER_PRECOMPILATION", "Enable shader precompilation"),
            ("DXVK_ENABLE_SHADER_PRECACHE", "Enable shader precache"),
            ("DXVK_ENABLE_SHADER_PRELOAD", "Enable shader preload"),
            ("DXVK_ENABLE_SHADER_PREWARM", "Enable shader prewarm"),
            ("DXVK_ENABLE_SHADER_PREOPTIMIZE", "Enable shader preoptimize"),
            ("DXVK_ENABLE_SHADER_PRECOMPILEALL", "Enable shader precompile for all"),
            ("DXVK_ENABLE_SHADER_PRECACHEALL", "Enable shader precache for all"),
            ("DXVK_ENABLE_SHADER_PRELOADALL", "Enable shader preload for all"),
            ("DXVK_ENABLE_SHADER_PREWARMALL", "Enable shader prewarm for all"),
            ("DXVK_ENABLE_SHADER_PREOPTIMIZEALL", "Enable shader preoptimize for all"),
        ],
        "inputs": [
            ("DXVK_HUD", "Specify HUD info", "e.g., fps,version"),
            ("DXVK_STATE_CACHE_PATH", "Path to state cache", "e.g., /path/to/cache"),
            ("DXVK_SHADER_CACHE_PATH", "Path to shader cache", "e.g., /path/to/cache"),
            ("DXVK_LOG_LEVEL", "Set log level", "e.g., info"),
            ("DXVK_MAX_FRAME_LATENCY", "Set max frame latency", "e.g., 2"),
            ("DXVK_MAX_FRAMES_IN_FLIGHT", "Set max frames in flight", "e.g., 3"),
            ("DXVK_FORCE_FEATURE_LEVEL", "Force feature level", "e.g., 11_0"),
            ("DXVK_SHADER_MODEL", "Specify shader model", "e.g., 5"),
            ("DXVK_MAX_SHADER_RESOURCE_GROUPS", "Set max shader resource groups", "e.g., 16"),
        ],
        "software_requirement": "dxvk",
    },
    "ProtonCustom": {
        "enable_label": "Enable ProtonCustom",
        "enable_tooltip": "Enable custom Proton settings",
        "env_prefix": "",
        "toggles": [
            ("PROTON_USE_WINED3D", "Force use of WineD3D"),
            ("PROTON_NO_ESYNC", "Disable explicit synchronization"),
            ("PROTON_NO_FSYNC", "Disable frame synchronization"),
            ("PROTON_USE_SECCOMP", "Enable seccomp sandboxing"),
            ("PROTON_USE_WINETRICKS", "Enable use of Winetricks"),
            ("PROTON_LOG", "Enable Proton logging"),
            ("PROTON_DISABLE_D3D11", "Disable Direct3D 11 support"),
            ("PROTON_DISABLE_D3D10", "Disable Direct3D 10 support"),
            ("PROTON_USE_WINED3D11", "Force WineD3D for D3D11"),
            ("PROTON_USE_WINED3D10", "Force WineD3D for D3D10"),
            ("PROTON_USE_WINED3D9", "Force WineD3D for D3D9"),
            ("PROTON_USE_D3D9EX", "Enable Direct3D 9Ex support"),
            ("PROTON_USE_D3D10LAYER", "Enable Direct3D 10 layer"),
            ("PROTON_USE_D3D11LAYER", "Enable Direct3D 11 layer"),
            ("PROTON_USE_D3D10MULTITHREADING", "Enable D3D10 multithreading"),
            ("PROTON_USE_D3D11MULTITHREADING", "Enable D3D11 multithreading"),
            ("PROTON_USE_VULKAN", "Force use of Vulkan"),
            ("PROTON_USE_OPENGL", "Force use of OpenGL"),
            ("PROTON_ENABLE_NVAPI", "Enable NVAPI support"),
            ("PROTON_DISABLE_NVAPI", "Disable NVAPI support"),
            ("PROTON_USE_STAGING", "Use staging branch of Wine"),
            ("PROTON_USE_PULSEAUDIO", "Force use of PulseAudio"),
            ("PROTON_USE_PIPEWIRE", "Force use of PipeWire"),
            ("PROTON_USE_ALSA", "Force use of ALSA"),
            ("PROTON_USE_JACK", "Force use of JACK"),
            ("PROTON_USE_XAUDIO2", "Force use of XAudio2"),
            ("PROTON_USE_FMOD", "Force use of FMOD"),
            ("PROTON_USE_DSOUND", "Force use of DirectSound"),
            ("PROTON_USE_WASAPI", "Force use of WASAPI"),
            ("PROTON_USE_DSOUND_HRTF", "Enable HRTF in DirectSound"),
            ("PROTON_USE_DSOUND_EFX", "Enable EFX in DirectSound"),
            ("PROTON_USE_DSOUND_REVERB", "Enable reverb in DirectSound"),
            ("PROTON_USE_DSOUND_3D", "Enable 3D audio in DirectSound"),
            ("PROTON_USE_DSOUND_EAX", "Enable EAX in DirectSound"),
            ("PROTON_USE_DSOUND_ALC", "Enable ALC in DirectSound"),
            ("PROTON_USE_DSOUND_ALC_HRTF", "Enable HRTF in DirectSound ALC"),
            ("PROTON_USE_DSOUND_ALC_EFX", "Enable EFX in DirectSound ALC"),
            ("PROTON_USE_DSOUND_ALC_REVERB", "Enable reverb in DirectSound ALC"),
            ("PROTON_USE_DSOUND_ALC_3D", "Enable 3D audio in DirectSound ALC"),
            ("PROTON_USE_DSOUND_ALC_EAX", "Enable EAX in DirectSound ALC"),
            ("PROTON_FORCE_VKLAYER_ENABLES", "Force Vulkan layer enables"),
            ("PROTON_WAIT_FOR_PLAY", "Wait for steam 'Play' press"),
        ],
        "inputs": [
            ("PROTON_LOG_DIR", "Path to log directory", "e.g., /path/to/log"),
            ("PROTON_DUMP_DEBUG_COMMANDS", "Path to dump debug commands", "e.g., /tmp/proton_debug"),
            ("PROTON_WINE_DEBUG", "Set Wine debug level (e.g., +steam)", "e.g., +steam,+rpc"),
        ],
    },
    "MesaOverlay": {
        "enable_label": "Enable MesaOverlay",
        "enable_tooltip": "Enable Mesa overlay",
        "env_prefix": "",
        "toggles": [
            ("MESA_OVERLAY", "Enable Mesa overlay"),
            ("MESA_OVERLAY_FPS", "Display FPS in Mesa overlay"),
            ("MESA_OVERLAY_GPU", "Display GPU usage in Mesa overlay"),
            ("MESA_OVERLAY_CPU", "Display CPU usage in Mesa overlay"),
            ("MESA_OVERLAY_MEMORY", "Display memory usage in Mesa overlay"),
            ("MESA_OVERLAY_TEMP", "Display GPU temperature in Mesa overlay"),
            ("MESA_OVERLAY_POWER", "Display GPU power usage in Mesa overlay"),
            ("MESA_OVERLAY_LOG", "Enable logging for Mesa overlay"),
            ("MESA_OVERLAY_SHORT", "Display a shorter overlay in Mesa"),
            ("MESA_OVERLAY_FULL", "Display a full overlay in Mesa"),
            ("MESA_OVERLAY_NOBACKGROUND", "Disable overlay background"),
            ("MESA_OVERLAY_TRANSPARENT", "Make overlay transparent"),
        ],
        "inputs": [
            ("MESA_OVERLAY_CONFIG", "Path to custom Mesa overlay config file", "e.g., /path/to/config"),
            ("MESA_OVERLAY_XOFFSET", "Adjust X offset of overlay", "e.g., 10"),
            ("MESA_OVERLAY_YOFFSET", "Adjust Y offset of overlay", "e.g., 10"),
            ("MESA_OVERLAY_COLOR", "Set overlay color", "e.g., #FF0000"),
            ("MESA_OVERLAY_FONT_SIZE", "Set font size", "e.g., 12"),
            ("MESA_OVERLAY_LOG_FILE", "Path to log file", "e.g., /path/to/log"),
            ("MESA_OVERLAY_TRANSPARENCY", "Set transparency level", "e.g., 0.5"),
        ],
        "dropdowns": {
            "MESA_OVERLAY_ALIGN": {
                "label": "ALIGN:",
                "options": ["top", "bottom", "left", "right"],
                "tooltip": "Align the Mesa overlay",
                "default": "top",
            }
        },
    },
}

# SECTION: GENERAL OPTIONS
# Define options specific to the General tab (These are command-line flags starting with -)
GENERAL_OPTIONS = [
    ("-nohltv", "Disables HLTV functionality"),
    ("-novid", "Skips the intro video"),
    ("-console", "Opens the game console"),
    ("-steam", "Forces Steam integration"),
    ("-nosteamcontroller", "Disables Steam controller input"),
    ("-nojoy", "Disables joystick input"),
    ("-nosound", "Disables sound"),
    ("-novsync", "Disables vertical sync"),
    ("-fullscreen", "Forces fullscreen mode"),
    ("-windowed", "Forces windowed mode"),
    ("-noborder", "Removes window borders in windowed mode"),
    ("-safe", "Starts the game in safe mode"),
    ("-high", "Sets high priority"),
    ("-low", "Sets low priority"),
    ("-mid", "Sets medium priority"),
    ("-nobenchmark", "Disables benchmarking"),
    ("-nosplash", "Disables the splash screen"),
    ("-nologo", "Disables the logo screen"),
    ("-noipx", "Disables IPX networking"),
    ("-noip", "Disables IP networking"),
    ("-novoice", "Disables voice chat"),
    ("-nocloud", "Disables Steam Cloud sync"),
    ("-nohttp", "Disables HTTP networking"),
    ("-nosteamupdate", "Disables Steam updates"),
    ("-nosoundinit", "Disables sound initialization"),
    ("-nocrashdialog", "Disables the crash dialog"),
    ("-nocrashdump", "Disables crash dumps"),
    ("-noasserts", "Disables assertions"),
    ("-nohomedirfixup", "Disables home directory fixup"),
    ("-noautocloud", "Disables automatic Steam Cloud sync"),
    ("-noautojoystick", "Disables automatic joystick detection"),
    ("-nominidumps", "Disables mini dumps"),
    ("-nocache", "Disables caching"),
    ("-noasync", "Disables asynchronous operations"),
    ("-nohw", "Disables hardware rendering"),
    ("-soft", "Forces software rendering"),
    ("-nograb", "Disables mouse grabbing"),
    ("-nogamepad", "Disables gamepad input"),
    ("-noxinput", "Disables XInput"),
    ("-nogpuwatch", "Disables GPU watch"),
    ("-nocursor", "Disables cursor"),
    ("-nohwcursor", "Disables hardware cursor"),
    ("-nogl", "Disables OpenGL"),
    ("-nod3d9", "Disables Direct3D 9"),
    ("-nod3d11", "Disables Direct3D 11"),
    ("-nomouse", "Disables mouse input"),
    ("-nokb", "Disables keyboard input"),
    ("-nolock", "Disables locking"),
    ("-nocommand", "Disables command execution"),
    ("-nolog", "Disables logging"),
    ("-noprofile", "Disables user profile loading"),
    ("-norestart", "Disables automatic restart"),
    ("-noupdate", "Disables automatic updates"),
    ("-noship", "Disables ship mode"),
    ("-noshadercache", "Disables shader cache"),
    ("-noshadercompile", "Disables shader compilation"),
    ("-noshaderload", "Disables shader loading"),
    ("-noshaderprecompile", "Disables shader precompilation"),
    ("-noshaderprecache", "Disables shader precache"),
    ("-noshaderpreload", "Disables shader preload"),
    ("-noshaderprewarm", "Disables shader prewarm"),
    ("-noshaderpreoptimize", "Disables shader preoptimize"),
    ("-noshaderprecompileall", "Disables shader precompile for all"),
    ("-noshaderprecacheall", "Disables shader precache for all"),
    ("-noshaderpreloadall", "Disables shader preload for all"),
    ("-noshaderprewarmall", "Disables shader prewarm for all"),
    ("-noshaderpreoptimizeall", "Disables shader preoptimize for all"),
]

# SECTION: GENERAL INPUTS
# Define input fields specific to the General tab (These are command-line flags with values)
GENERAL_INPUTS = [
    ("-width", "Sets the window width", "e.g., 1920"),
    ("-height", "Sets the window height", "e.g., 1080"),
    ("-dxlevel", "Sets the DirectX level", "e.g., 95"),  # Handled specially with toggle
    ("-particles", "Sets the particle effect quality", "e.g., 1"),
    ("-refresh", "Sets the refresh rate", "e.g., 60"),
    ("-heapsize", "Sets heapsize in KB", "e.g., 524288"),
]

# SECTION: DX LEVEL PRESETS
# Define preset options for DXLevel (expanded)
DX_LEVEL_PRESETS = [
    "80", "81", "90", "95", "98",
    "9.0", "9.0c", "10.0", "10.1", "11.0",
    "12.0",
]

# SECTION: MAIN WINDOW CLASS
# Define the main window class for the Steam Launcher
class SteamLauncherWindow(Gtk.Window):
    # SECTION: INITIALIZATION
    # Initialize the main window and set up UI components
    def __init__(self):
        try:
            super().__init__(title="Steam Game Launcher")
            print("Initializing Steam Launcher...")
            self.set_border_width(10)
            self.set_default_size(1000, 700)

            # Main vertical box to hold all content
            vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
            self.add(vbox)

            # Header label with title and description
            header = Gtk.Label(label="Steam Launch Options\nCustomize your game launch command with tabs for overlays and enhancements")
            header.set_justify(Gtk.Justification.CENTER)
            vbox.pack_start(header, False, False, 0)

            # --- Detect Section ---
            hbox_detect = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
            vbox.pack_start(hbox_detect, False, False, 5)
            detect_label = Gtk.Label(label="Paste Command:")
            hbox_detect.pack_start(detect_label, False, False, 0)
            self.detect_entry = Gtk.Entry()
            self.detect_entry.set_placeholder_text("Paste existing Steam launch options here (e.g., ENV_VAR=value command -flag --arg value %command%)")
            self.detect_entry.set_hexpand(True)
            hbox_detect.pack_start(self.detect_entry, True, True, 0)
            detect_button = Gtk.Button(label="Parse Command")
            detect_button.connect("clicked", self.on_detect_clicked)
            hbox_detect.pack_start(detect_button, False, False, 0)

            # Notebook to manage multiple tabs
            self.notebook = Gtk.Notebook()
            vbox.pack_start(self.notebook, True, True, 0)

            # Tab 1: General Steam Options
            self.toggles = {}  # Store toggle switches for General tab
            self.inputs = {}   # Store input entries for General tab
            self.general_dropdowns = {}  # Store general dropdowns (like dxlevel)
            self.dxlevel_toggle = None  # Store dxlevel enable toggle
            self.setup_general_tab(self.notebook)

            # Track which tabs have been checked for software
            self.software_checked = {tab: False for tab in TAB_CONFIGS if "software_requirement" in TAB_CONFIGS[tab]}

            # Setup tabs for overlay/enhancement tools
            self.tab_data = defaultdict(lambda: {
                "toggles": {},
                "inputs": {},
                "dropdowns": {},
                "sliders": {},
                "slider_values": {},
                "content_box": None,
                "enable_toggle": None,
                "install_button": None
            })
            for tab_name in TAB_CONFIGS:
                self.setup_tab(self.notebook, tab_name)

            # Connect tab switch signal (no longer checking software on switch)
            self.notebook.connect("switch-page", self.on_tab_switched)

            # Create mappings for detection
            # Defer building mappings and loading settings until UI is fully built
            GLib.idle_add(self.build_detection_mappings)
            GLib.idle_add(self.load_settings)

            # Buttons at the bottom
            hbox_buttons = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            vbox.pack_start(hbox_buttons, False, False, 0)

            save_button = Gtk.Button(label="Save Settings")
            save_button.connect("clicked", self.on_save_clicked)
            hbox_buttons.pack_start(save_button, True, True, 0)

            reset_button = Gtk.Button(label="Reset All")
            reset_button.connect("clicked", self.on_reset_clicked)
            hbox_buttons.pack_start(reset_button, True, True, 0)

            launch_button = Gtk.Button(label="Generate Launch Command")
            launch_button.connect("clicked", self.on_launch_clicked)
            hbox_buttons.pack_start(launch_button, True, True, 0)

            # --- Generated Command Output ---
            hbox_output = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
            vbox.pack_start(hbox_output, False, False, 5)
            output_label = Gtk.Label(label="Generated Command:")
            output_label.set_xalign(0)
            hbox_output.pack_start(output_label, False, False, 0)
            self.generated_command_entry = Gtk.Entry()
            self.generated_command_entry.set_placeholder_text("Generated launch command will appear here")
            self.generated_command_entry.set_editable(False)
            self.generated_command_entry.set_hexpand(True)
            hbox_output.pack_start(self.generated_command_entry, True, True, 0)

            # Styling for better readability
            css = """
            window, dialog {
                background-color: #353535;
            }
            label, button {
                color: #e0e0e0;
            }
            button {
                background-color: #4a4a4a;
                border: 1px solid #707070;
                border-radius: 5px;
            }
            button:hover {
                background-color: #606060;
            }
            entry, textview text {
                background-color: #404040;
                color: #e0e0e0;
                border: 1px solid #707070;
                border-radius: 5px;
            }
            switch {
                background-color: #404040;
            }
            switch slider {
                background-color: #808080;
                border-radius: 10px;
            }
            switch:checked slider {
                background-color: #00aaff;
            }
            tooltip {
                background-color: #000000;
                color: #ffffff;
                border: 1px solid #a0a0a0;
                border-radius: 5px;
                padding: 4px;
            }
            .enable-label {
                font-weight: bold;
                font-size: 14px;
                color: #00aaff;
            }
            .vkbasalt-grid {
                margin: 10px;
                padding: 10px;
            }
            .vkbasalt-slider-box {
                margin: 5px 0;
                padding: 5px;
            }
            """
            css_provider = Gtk.CssProvider()
            css_provider.load_from_data(css.encode())
            Gtk.StyleContext.add_provider_for_screen(
                Gdk.Screen.get_default(),
                css_provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )

            # Save settings on window close
            self.connect("destroy", self.on_destroy)
        except Exception as e:
            print(f"Error initializing application: {e}")
            raise

    # SECTION: UI SETUP HELPERS
    def _create_toggle(self, label, tooltip):
        """Helper to create a toggle switch (CheckButton)."""
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        toggle = Gtk.CheckButton()
        lbl = Gtk.Label(label=label)
        lbl.set_tooltip_text(tooltip)
        lbl.set_xalign(0.0)
        hbox.pack_start(toggle, False, False, 0)
        hbox.pack_start(lbl, True, True, 0)
        hbox.set_tooltip_text(tooltip)
        return hbox, toggle

    def _create_input(self, label, tooltip, placeholder):
        """Helper to create a label and text entry."""
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        lbl = Gtk.Label(label=f"{label}:")
        lbl.set_tooltip_text(tooltip)
        lbl.set_xalign(0.0)
        entry = Gtk.Entry()
        entry.set_placeholder_text(placeholder)
        entry.set_tooltip_text(tooltip)
        entry.set_hexpand(True)
        hbox.pack_start(lbl, False, False, 0)
        hbox.pack_start(entry, True, True, 0)
        hbox.set_tooltip_text(tooltip)
        return hbox, entry

    def _create_dropdown(self, label, options, default, tooltip):
        """Helper to create a label and dropdown (ComboBoxText)."""
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        lbl = Gtk.Label(label=f"{label}:")
        lbl.set_tooltip_text(tooltip)
        lbl.set_xalign(0.0)
        combo = Gtk.ComboBoxText()
        combo.set_tooltip_text(tooltip)
        for i, option in enumerate(options):
            combo.append(str(i), option)
        try:
            if default is not None and default in options:
                default_index = options.index(default)
                combo.set_active(default_index)
            elif options:
                combo.set_active(0)
            else:
                combo.set_active(-1)
        except ValueError:
            if options:
                combo.set_active(0)
            else:
                combo.set_active(-1)
        hbox.pack_start(lbl, False, False, 0)
        hbox.pack_start(combo, True, True, 0)
        hbox.set_tooltip_text(tooltip)
        return hbox, combo

    def _create_slider(self, label, min_val, max_val, tooltip):
        """Helper to create a label, slider (Scale), and value label."""
        hbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
        lbl = Gtk.Label(label=f"{label}:")
        lbl.set_tooltip_text(tooltip)
        lbl.set_xalign(0.0)
        hbox.pack_start(lbl, False, False, 0)

        hbox_slider = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        adj = Gtk.Adjustment(
            value=0,
            lower=min_val,
            upper=max_val,
            step_increment=0.01,
            page_increment=0.1,
            page_size=0.1
        )
        scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=adj)
        scale.set_digits(2)
        scale.set_hexpand(True)
        scale.set_tooltip_text(tooltip)

        value_label = Gtk.Label(label="0.00")
        scale.connect("value-changed", lambda slider, lbl=value_label: lbl.set_text(f"{slider.get_value():.2f}"))

        hbox_slider.pack_start(scale, True, True, 0)
        hbox_slider.pack_start(value_label, False, False, 0)

        hbox.pack_start(hbox_slider, True, True, 0)
        hbox.set_tooltip_text(tooltip)
        return hbox, scale

    # SECTION: TAB SETUP
    # Setup the General tab in the notebook
    def setup_general_tab(self, notebook):
        tab_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        tab_vbox.set_border_width(10)
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.add(tab_vbox)

        # General Toggles
        toggles_frame = Gtk.Frame(label="Common Launch Flags")
        tab_vbox.pack_start(toggles_frame, False, False, 0)
        toggles_grid = Gtk.Grid(column_spacing=20, row_spacing=10)
        toggles_grid.set_border_width(10)
        toggles_frame.add(toggles_grid)

        col, row = 0, 0
        max_cols = 3
        for flag, tooltip in GENERAL_OPTIONS:
            label_text = flag.lstrip('-').replace('_', ' ').title()
            hbox, toggle = self._create_toggle(label_text, f"{tooltip} ({flag})")
            toggles_grid.attach(hbox, col, row, 1, 1)
            self.toggles[flag] = toggle
            col += 1
            if col >= max_cols:
                col = 0
                row += 1

        # General Inputs
        inputs_frame = Gtk.Frame(label="Common Launch Arguments")
        tab_vbox.pack_start(inputs_frame, False, False, 10)
        inputs_grid = Gtk.Grid(column_spacing=10, row_spacing=10)
        inputs_grid.set_border_width(10)
        inputs_frame.add(inputs_grid)

        row = 0
        for flag, label, placeholder in GENERAL_INPUTS:
            if flag == "-dxlevel":
                # Create toggle for enabling/disabling dxlevel
                dx_toggle_hbox, dx_toggle = self._create_toggle("Enable DirectX Level", f"Enable DirectX Level ({flag})")
                self.dxlevel_toggle = dx_toggle
                inputs_grid.attach(dx_toggle_hbox, 0, row, 1, 1)
                row += 1

                # Create dropdown for dxlevel
                dx_options = DX_LEVEL_PRESETS
                dx_tooltip = f"{label} ({flag})"
                hbox_dx, combo_dx = self._create_dropdown("DirectX Level", dx_options, None, dx_tooltip)
                inputs_grid.attach(hbox_dx, 0, row, 1, 1)
                self.general_dropdowns[flag] = combo_dx
                # Initially disable dropdown unless toggle is active
                hbox_dx.set_sensitive(False)
                dx_toggle.connect("toggled", self.on_dxlevel_toggle, hbox_dx)
            else:
                label_text = label
                hbox, entry = self._create_input(label_text, f"{label} ({flag})", placeholder)
                inputs_grid.attach(hbox, 0, row, 1, 1)
                self.inputs[flag] = entry
            row += 1

        notebook.append_page(scrolled_window, Gtk.Label(label="General"))

    def on_dxlevel_toggle(self, toggle, dxlevel_hbox):
        """Enable or disable the dxlevel dropdown based on toggle state."""
        is_active = toggle.get_active()
        dxlevel_hbox.set_sensitive(is_active)
        logging.debug(f"DirectX Level dropdown sensitivity set to {is_active}")

    # Setup a tab for a specific tool (e.g., Wine, MangoHud)
    def setup_tab(self, notebook, tab_name):
        config = TAB_CONFIGS.get(tab_name)
        if not config:
            logging.warning(f"No configuration found for tab: {tab_name}")
            return

        tab_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        tab_vbox.set_border_width(10)
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.add(tab_vbox)

        # Enable Toggle for the tab
        enable_toggle = Gtk.CheckButton(label=config.get("enable_label", f"Enable {tab_name}"))
        enable_toggle.set_tooltip_text(config.get("enable_tooltip", f"Enable {tab_name} options"))
        tab_vbox.pack_start(enable_toggle, False, False, 0)
        self.tab_data[tab_name]['enable_toggle'] = enable_toggle

        # Content box to be enabled/disabled
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        content_box.set_border_width(5)
        tab_vbox.pack_start(content_box, True, True, 0)
        self.tab_data[tab_name]['content_box'] = content_box
        enable_toggle.connect("toggled", self.on_enable_toggle, tab_name)

        # Install Software Button (except for vkBasalt)
        if "software_requirement" in config and config["software_requirement"] != "vkbasalt":
            software = config["software_requirement"]
            install_button = Gtk.Button(label=f"Install {software}")
            install_button.set_tooltip_text(f"Install {software} using apt")
            install_button.connect("clicked", self.on_install_software_clicked, tab_name, software)
            content_box.pack_start(install_button, False, False, 0)
            self.tab_data[tab_name]['install_button'] = install_button
            # Check if software is installed and hide button if it is
            if self.check_software(software):
                install_button.set_visible(False)
                self.software_checked[tab_name] = True

        # Set initial sensitivity based on toggle state
        content_box.set_sensitive(enable_toggle.get_active())

        # Toggles for the tab
        if "toggles" in config:
            toggles_frame = Gtk.Frame(label="Options / Flags")
            content_box.pack_start(toggles_frame, False, False, 0)
            toggles_grid = Gtk.Grid(column_spacing=20, row_spacing=10)
            toggles_grid.set_border_width(10)
            toggles_frame.add(toggles_grid)

            col, row = 0, 0
            max_cols = 2
            for option, tooltip in config["toggles"]:
                label_text = option.replace('_', ' ').title()
                hbox, toggle = self._create_toggle(label_text, tooltip)
                toggles_grid.attach(hbox, col, row, 1, 1)
                self.tab_data[tab_name]['toggles'][option] = toggle
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1

        # Inputs for the tab
        if "inputs" in config:
            inputs_frame = Gtk.Frame(label="Settings / Paths")
            content_box.pack_start(inputs_frame, False, False, 10)
            inputs_grid = Gtk.Grid(column_spacing=10, row_spacing=10)
            inputs_grid.set_border_width(10)
            inputs_frame.add(inputs_grid)
            row = 0
            for option, label, placeholder in config["inputs"]:
                input_label = label if label else option.replace('_', ' ').title()
                hbox, entry = self._create_input(input_label, placeholder, placeholder)
                inputs_grid.attach(hbox, 0, row, 1, 1)
                self.tab_data[tab_name]['inputs'][option] = entry
                row += 1

        # Dropdowns for the tab
        if "dropdowns" in config:
            dropdowns_frame = Gtk.Frame(label="Choices")
            content_box.pack_start(dropdowns_frame, False, False, 10)
            dropdowns_grid = Gtk.Grid(column_spacing=10, row_spacing=10)
            dropdowns_grid.set_border_width(10)
            dropdowns_frame.add(dropdowns_grid)
            row = 0
            for key, dd_config in config["dropdowns"].items():
                dropdown_label = dd_config.get("label", key.replace('_', ' ').title())
                hbox, combo = self._create_dropdown(
                    dropdown_label,
                    dd_config.get("options", []),
                    dd_config.get("default", None),
                    dd_config.get("tooltip", "")
                )
                dropdowns_grid.attach(hbox, 0, row, 1, 1)
                self.tab_data[tab_name]['dropdowns'][key] = combo
                row += 1

        # Sliders for the tab
        if "sliders" in config:
            sliders_frame = Gtk.Frame(label="Strength / Radius")
            content_box.pack_start(sliders_frame, False, False, 10)
            sliders_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
            sliders_vbox.set_border_width(10)
            sliders_frame.add(sliders_vbox)
            for option, label, min_val, max_val in config["sliders"]:
                slider_label = label if label else option.replace('_', ' ').title()
                hbox, slider = self._create_slider(slider_label, min_val, max_val, f"{label} ({option})")
                sliders_vbox.pack_start(hbox, False, False, 0)
                self.tab_data[tab_name]['sliders'][option] = slider

        notebook.append_page(scrolled_window, Gtk.Label(label=tab_name))

    # SECTION: DETECTION MAPPINGS
    # Create mappings to link command parts/env vars to GUI elements
    def build_detection_mappings(self):
        self.flag_to_toggle = {}
        self.flag_to_input = {}
        self.env_to_gui = {}
        self.command_prefixes = {}

        logging.debug("Building detection mappings...")

        # General flags (Toggles)
        for flag, toggle in self.toggles.items():
            self.flag_to_toggle[flag] = {"widget": toggle}

        # General inputs (Flags with values)
        for flag, entry in self.inputs.items():
            self.flag_to_input[flag] = {"widget": entry}

        # General dropdowns (Flags with values from dropdown)
        for flag, combo in self.general_dropdowns.items():
            self.flag_to_input[flag] = {
                "widget": combo,
                "type": "combo",
                "options": [combo.get_model()[i][0] for i in range(len(combo.get_model()))]
            }

        # Tab-specific mappings
        for tab_name, config in TAB_CONFIGS.items():
            tab_widgets = self.tab_data[tab_name]

            # Command Prefixes
            if "command_prefix" in config:
                self.command_prefixes[config["command_prefix"]] = tab_name

            # Environment Variables (Toggles)
            if "toggles" in config:
                for option, _ in config["toggles"]:
                    env_var_name = option
                    self.env_to_gui[env_var_name] = {
                        "widget": tab_widgets['toggles'][option],
                        "type": "toggle",
                        "tab": tab_name,
                        "option": option
                    }

            # Environment Variables (Inputs)
            if "inputs" in config:
                for option, _, _ in config["inputs"]:
                    env_var_name = option
                    self.env_to_gui[env_var_name] = {
                        "widget": tab_widgets['inputs'][option],
                        "type": "input",
                        "tab": tab_name,
                        "option": option
                    }

            # Environment Variables (Dropdowns)
            if "dropdowns" in config:
                for key, dd_config in config["dropdowns"].items():
                    env_var_name = key
                    combo = tab_widgets['dropdowns'][key]
                    options = [combo.get_model()[i][0] for i in range(len(combo.get_model()))]
                    self.env_to_gui[env_var_name] = {
                        "widget": combo,
                        "type": "dropdown",
                        "tab": tab_name,
                        "option": key,
                        "options": options
                    }

            # Environment Variables (Sliders)
            if "sliders" in config:
                for option, _, _, _ in config["sliders"]:
                    env_var_name = option
                    self.env_to_gui[env_var_name] = {
                        "widget": tab_widgets['sliders'][option],
                        "type": "slider",
                        "tab": tab_name,
                        "option": option
                    }

            # Gamescope specific flags (handled as command-line flags, not env vars)
            if tab_name == "Gamescope":
                if "toggles" in config:
                    for flag, _ in config["toggles"]:
                        self.flag_to_toggle[flag] = {"widget": tab_widgets['toggles'][flag], "tab": tab_name}
                if "inputs" in config:
                    for flag, _, _ in config["inputs"]:
                        if flag == "--steam":
                            self.flag_to_input[flag] = {
                                "widget": tab_widgets['inputs'][flag],
                                "tab": tab_name,
                                "type": "flag_present"
                            }
                        else:
                            self.flag_to_input[flag] = {
                                "widget": tab_widgets['inputs'][flag],
                                "tab": tab_name,
                                "type": "input"
                            }

        logging.debug(f"Detection mappings built. Env keys: {list(self.env_to_gui.keys())}, "
                      f"Flag Toggles: {list(self.flag_to_toggle.keys())}, "
                      f"Flag Inputs: {list(self.flag_to_input.keys())}, "
                      f"Command Prefixes: {list(self.command_prefixes.keys())}")

    # SECTION: EVENT HANDLERS
    def on_enable_toggle(self, toggle, tab_name):
        """Called when an enable toggle for a tab is clicked."""
        is_active = toggle.get_active()
        if tab_name in self.tab_data and self.tab_data[tab_name]['content_box']:
            self.tab_data[tab_name]['content_box'].set_sensitive(is_active)
            logging.debug(f"Tab '{tab_name}' content sensitivity set to {is_active}")

    def on_tab_switched(self, notebook, page, page_num):
        """Handle tab switching (no software checks here anymore)."""
        tab_widget = notebook.get_nth_page(page_num)
        tab_label_widget = notebook.get_tab_label(tab_widget)
        if tab_label_widget:
            tab_name = tab_label_widget.get_text()
            logging.debug(f"Switched to tab: {tab_name}")

    def on_save_clicked(self, widget):
        settings = {"general": {}, "tabs": {}}

        # Save General tab settings
        for flag, toggle in self.toggles.items():
            settings["general"][flag] = toggle.get_active()
        for flag, entry in self.inputs.items():
            settings["general"][flag] = entry.get_text()
        for flag, combo in self.general_dropdowns.items():
            settings["general"][flag] = combo.get_active_text()
        settings["general"]["dxlevel_enabled"] = self.dxlevel_toggle.get_active()

        # Save Tab settings
        for tab_name, data in self.tab_data.items():
            tab_settings = {}
            if data["enable_toggle"]:
                tab_settings["enabled"] = data["enable_toggle"].get_active()
            tab_settings["toggles"] = {key: toggle.get_active() for key, toggle in data["toggles"].items()}
            tab_settings["inputs"] = {key: entry.get_text() for key, entry in data["inputs"].items()}
            tab_settings["dropdowns"] = {key: combo.get_active_text() for key, combo in data["dropdowns"].items()}
            tab_settings["sliders"] = {key: slider.get_value() for key, slider in data["sliders"].items()}
            settings["tabs"][tab_name] = tab_settings

        try:
            with open("steam_launcher_settings.json", "w") as f:
                json.dump(settings, f, indent=4)
            logging.info("Settings saved successfully.")
            self.show_info_dialog("Settings Saved", "Configuration saved successfully.")
        except Exception as e:
            logging.error(f"Failed to save settings: {e}")
            self.show_error_dialog("Save Error", f"Could not save settings.\nError: {e}")

    def on_reset_clicked(self, widget):
        """Handle the Reset All button click."""
        self.reset_uiarea()
        logging.info("All settings reset to default.")
        self.show_info_dialog("Settings Reset", "All options have been reset to their default states.")

    def on_launch_clicked(self, widget):
        command_parts = []
        env_vars = {}

        tab_order = TAB_CONFIGS.keys()
        command_prefixes = []
        gamescope_flags = []
        command_suffix = ""

        for tab_name in tab_order:
            if tab_name in self.tab_data and self.tab_data[tab_name]["enable_toggle"].get_active():
                config = TAB_CONFIGS[tab_name]
                data = self.tab_data[tab_name]

                if "command_prefix" in config:
                    command_prefixes.append(config["command_prefix"])
                if "command_suffix" in config:
                    command_suffix = config["command_suffix"]

                if "toggles" in config:
                    for option, _ in config["toggles"]:
                        if data["toggles"][option].get_active():
                            env_vars[option] = "1"

                if "inputs" in config:
                    for option, _, _ in config["inputs"]:
                        value = data["inputs"][option].get_text().strip()
                        if value:
                            env_vars[option] = value

                if "dropdowns" in config:
                    for key, dd_config in config["dropdowns"].items():
                        value = data["dropdowns"][key].get_active_text()
                        if value is not None:
                            env_vars[key] = value

                if "sliders" in config:
                    for option, _, _, _ in config["sliders"]:
                        value = data["sliders"][option].get_value()
                        # Skip vkBasalt sliders with value 0
                        if tab_name == "vkBasalt" and value == 0:
                            continue
                        env_vars[option] = str(value)

                if tab_name == "Gamescope":
                    if "toggles" in config:
                        for flag, _ in config["toggles"]:
                            if data["toggles"][flag].get_active():
                                gamescope_flags.append(flag)
                    if "inputs" in config:
                        for flag, _, _ in config["inputs"]:
                            value = data["inputs"][flag].get_text().strip()
                            if value or flag == "--steam":
                                if flag == "--steam" and not value:
                                    gamescope_flags.append(flag)
                                elif value:
                                    gamescope_flags.extend([flag, shlex.quote(value)])

        env_string_parts = []
        for key, value in env_vars.items():
            env_string_parts.append(f"{key}={shlex.quote(value)}")
        env_string = " ".join(env_string_parts)

        if env_string:
            command_parts.append(env_string)

        command_parts.extend(command_prefixes)

        if "gamescope" in command_prefixes:
            command_parts.extend(gamescope_flags)
            if command_suffix:
                command_parts.append(command_suffix)

        for flag, toggle in self.toggles.items():
            if toggle.get_active():
                command_parts.append(flag)

        for flag, entry in self.inputs.items():
            value = entry.get_text().strip()
            if value:
                command_parts.extend([flag, shlex.quote(value)])

        # Only include dxlevel if toggle is active
        if self.dxlevel_toggle.get_active():
            for flag, combo in self.general_dropdowns.items():
                value = combo.get_active_text()
                if value is not None:
                    command_parts.extend([flag, shlex.quote(value)])

        command_parts.append("%command%")

        final_command = " ".join(command_parts)
        logging.info(f"Generated command: {final_command}")
        self.generated_command_entry.set_text(final_command)
        self.show_info_dialog("Command Generated", "The launch command has been generated and appears below.\n\n" + final_command)

    def on_detect_clicked(self, widget):
        """Parses the command string and updates the UI."""
        command_string = self.detect_entry.get_text().strip()
        if not command_string or "%command%" not in command_string:
            self.show_error_dialog("Invalid Command", "Please paste a valid Steam launch command string containing '%command%'.")
            return

        logging.info(f"Parsing command: {command_string}")

        self.reset_uiarea()

        try:
            parts = shlex.split(command_string, posix=True)
        except ValueError as e:
            logging.error(f"Failed to parse command string with shlex: {e}")
            self.show_error_dialog("Parsing Error", f"Could not parse the command string.\nError: {e}")
            return

        env_vars = {}
        command_and_args = []
        is_env_section = True

        for part in parts:
            if is_env_section and '=' in part and not part.startswith('-') and part.split('=')[0].replace('_', '').isalnum():
                try:
                    key, value = part.split('=', 1)
                    env_vars[key] = value
                    logging.debug(f"Parsed env var: {key}={value}")
                except ValueError:
                    logging.warning(f"Skipping invalid env var part: {part}")
                    command_and_args.append(part)
                    is_env_section = False
            else:
                command_and_args.append(part)
                is_env_section = False

        logging.debug(f"Parsed command and args: {command_and_args}")
        logging.debug(f"Parsed env vars: {env_vars}")

        active_tabs_from_env = set()
        for env_key, env_value in env_vars.items():
            if env_key in self.env_to_gui:
                mapping = self.env_to_gui[env_key]
                widget = mapping["widget"]
                widget_type = mapping["type"]
                tab_name = mapping.get("tab")

                logging.debug(f"Matching env var '{env_key}' to widget type '{widget_type}' in tab '{tab_name}'")

                if tab_name and tab_name in self.tab_data and self.tab_data[tab_name]["enable_toggle"]:
                    self.tab_data[tab_name]["enable_toggle"].set_active(True)
                    active_tabs_from_env.add(tab_name)

                if widget_type == "toggle":
                    if env_key in env_vars:
                        widget.set_active(True)
                elif widget_type == "input":
                    widget.set_text(env_value)
                elif widget_type == "dropdown":
                    options = mapping.get("options", [])
                    try:
                        index = options.index(env_value)
                        widget.set_active(index)
                    except ValueError:
                        logging.warning(f"Value '{env_value}' not found in options for env var '{env_key}'")
                elif widget_type == "slider":
                    try:
                        slider_value = float(env_value)
                        widget.set_value(slider_value)
                        if isinstance(widget.get_parent(), Gtk.Box) and len(widget.get_parent().get_children()) > 1:
                            value_label = widget.get_parent().get_children()[1]
                            if isinstance(value_label, Gtk.Label):
                                value_label.set_text(f"{slider_value:.2f}")
                    except (ValueError, TypeError):
                        logging.warning(f"Could not convert env var value '{env_value}' to float for slider '{env_key}'")

        active_tabs_from_command = set()
        processed_gamescope_flags = False

        i = 0
        while i < len(command_and_args):
            part = command_and_args[i]

            if part in self.command_prefixes:
                tab_name = self.command_prefixes[part]
                if tab_name in self.tab_data and self.tab_data[tab_name]["enable_toggle"]:
                    self.tab_data[tab_name]["enable_toggle"].set_active(True)
                    active_tabs_from_command.add(tab_name)
                    logging.debug(f"Detected command prefix '{part}', enabling tab '{tab_name}'")

                if tab_name == "Gamescope" and not processed_gamescope_flags:
                    gamescope_config = TAB_CONFIGS.get("Gamescope", {})
                    gamescope_suffix = gamescope_config.get("command_suffix", "--")
                    j = i + 1
                    while j < len(command_and_args) and command_and_args[j] != gamescope_suffix and command_and_args[j] != "%command%":
                        gamescope_part = command_and_args[j]
                        if gamescope_part in self.flag_to_toggle:
                            mapping = self.flag_to_toggle[gamescope_part]
                            widget = mapping["widget"]
                            widget.set_active(True)
                            logging.debug(f"Matching Gamescope toggle flag '{gamescope_part}'")
                        elif gamescope_part in self.flag_to_input:
                            mapping = self.flag_to_input[gamescope_part]
                            widget = mapping["widget"]
                            widget_type = mapping.get("type", "input")
                            if widget_type == "input" and j + 1 < len(command_and_args):
                                value = command_and_args[j + 1]
                                widget.set_text(value)
                                logging.debug(f"Matching Gamescope input flag '{gamescope_part}' with value '{value}'")
                                j += 1
                            elif widget_type == "flag_present":
                                widget.set_text(gamescope_part)
                                logging.debug(f"Matching Gamescope presence flag '{gamescope_part}'")
                            else:
                                logging.warning(f"Gamescope input flag '{gamescope_part}' found but no value provided.")
                        j += 1
                    i = j - 1
                    processed_gamescope_flags = True

            elif part in self.flag_to_toggle:
                mapping = self.flag_to_toggle[part]
                widget = mapping["widget"]
                widget.set_active(True)
                logging.debug(f"Matching general toggle flag '{part}'")

            elif part in self.flag_to_input:
                mapping = self.flag_to_input[part]
                widget = mapping["widget"]
                widget_type = mapping.get("type", "input")
                if widget_type == "input" and i + 1 < len(command_and_args):
                    value = command_and_args[i + 1]
                    widget.set_text(value)
                    logging.debug(f"Matching general input flag '{part}' with value '{value}'")
                    i += 1
                elif widget_type == "combo" and i + 1 < len(command_and_args):
                    value = command_and_args[i + 1]
                    options = mapping.get("options", [])
                    try:
                        index = options.index(value)
                        widget.set_active(index)
                        logging.debug(f"Matching general dropdown flag '{part}' with value '{value}'")
                        if part == "-dxlevel":
                            self.dxlevel_toggle.set_active(True)
                    except ValueError:
                        logging.warning(f"Value '{value}' not found in options for flag '{part}'")
                    i += 1
                elif widget_type == "flag_present":
                    widget.set_text(part)
                    logging.debug(f"Matching general presence flag '{part}'")
                else:
                    logging.warning(f"General input flag '{part}' found but no value provided.")

            elif part == "%command%":
                logging.debug("Found %command% placeholder. Stopping command parsing.")
                break

            else:
                logging.debug(f"Unrecognized command part: '{part}'")

            i += 1

        for tab_name in active_tabs_from_env.union(active_tabs_from_command):
            if tab_name in self.tab_data and self.tab_data[tab_name]['content_box']:
                self.tab_data[tab_name]['content_box'].set_sensitive(True)

        self.show_info_dialog("Parsing Complete", "Attempted to parse the command and update settings.")

    def reset_uiarea(self):
        """Resets all UI elements to their default/inactive state."""
        logging.debug("Resetting UI...")

        for toggle in self.toggles.values():
            toggle.set_active(False)
        for entry in self.inputs.values():
            entry.set_text("")
        for combo in self.general_dropdowns.values():
            if combo.get_model() and combo.get_model().get_iter_first():
                combo.set_active(0)
            else:
                combo.set_active(-1)
        self.dxlevel_toggle.set_active(False)

        for tab_name, data in self.tab_data.items():
            if data["enable_toggle"]:
                data["enable_toggle"].set_active(False)
            if data['content_box']:
                data['content_box'].set_sensitive(False)

            for toggle in data["toggles"].values():
                toggle.set_active(False)
            for entry in data["inputs"].values():
                entry.set_text("")
            for combo in data["dropdowns"].values():
                if combo.get_model() and combo.get_model().get_iter_first():
                    combo.set_active(0)
                else:
                    combo.set_active(-1)
            for slider in data["sliders"].values():
                adjustment = slider.get_adjustment()
                adjustment.set_value(adjustment.get_lower())
                if isinstance(slider.get_parent(), Gtk.Box) and len(slider.get_parent().get_children()) > 1:
                    value_label = slider.get_parent().get_children()[1]
                    if isinstance(value_label, Gtk.Label):
                        value_label.set_text(f"{adjustment.get_lower():.2f}")

        self.generated_command_entry.set_text("")
        self.detect_entry.set_text("")
        logging.debug("UI reset complete.")

    # SECTION: SOFTWARE CHECKING AND INSTALLATION
    def check_software(self, software):
        """Check if the specified software is installed."""
        try:
            subprocess.run(["which", software], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            logging.info(f"Software '{software}' found.")
            return True
        except subprocess.CalledProcessError:
            logging.warning(f"Software '{software}' not found in PATH.")
            return False

    def on_install_software_clicked(self, button, tab_name, software):
        """Handle the Install Software button click."""
        logging.debug(f"Install button clicked for software '{software}' in tab '{tab_name}'")

        # Create password dialog
        password_dialog = Gtk.Dialog(
            title=f"Install {software}",
            transient_for=self,
            flags=Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT
        )
        password_dialog.add_buttons(
            "_OK", Gtk.ResponseType.OK,
            "_Cancel", Gtk.ResponseType.CANCEL
        )

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vbox.set_border_width(10)
        password_dialog.get_content_area().pack_start(vbox, True, True, 0)

        label = Gtk.Label(label=f"Enter your sudo password to install {software}:")
        vbox.pack_start(label, False, False, 0)
        password_entry = Gtk.Entry()
        password_entry.set_visibility(False)
        password_entry.set_invisible_char("*")
        vbox.pack_start(password_entry, False, False, 0)

        password_dialog.show_all()
        password_entry.grab_focus()

        response = password_dialog.run()
        password = password_entry.get_text() if response == Gtk.ResponseType.OK else ""
        password_dialog.destroy()

        if password:
            try:
                # Use pexpect to run the apt install command
                cmd = f"sudo -S apt-get install -y {software}"
                child = pexpect.spawn(cmd, encoding='utf-8', logfile=open(LOG_FILE, 'a'))
                child.expect(['password', pexpect.EOF])
                child.sendline(password)
                child.expect(pexpect.EOF, timeout=300)
                child.close()

                if child.exitstatus == 0:
                    logging.info(f"Successfully installed {software}")
                    self.show_info_dialog("Installation Successful", f"{software} was installed successfully.")
                    # Hide the install button
                    if self.tab_data[tab_name]['install_button']:
                        self.tab_data[tab_name]['install_button'].set_visible(False)
                    self.software_checked[tab_name] = True
                else:
                    logging.error(f"Installation of {software} failed with exit status {child.exitstatus}")
                    self.show_error_dialog("Installation Failed", f"Failed to install {software}. Check the log for details.")
            except pexpect.exceptions.ExceptionPexpect as e:
                logging.error(f"Error installing {software}: {e}")
                self.show_error_dialog("Installation Error", f"Error installing {software}: {e}")
        else:
            logging.debug(f"Installation of {software} cancelled by user")
            self.show_info_dialog("Installation Cancelled", f"Installation of {software} was cancelled.")

    # SECTION: DIALOGS
    def show_info_dialog(self, title, message):
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text=title,
        )
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()

    def show_error_dialog(self, title, message):
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text=title,
        )
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()

    # SECTION: SETTINGS LOADING
    def load_settings(self):
        try:
            if os.path.exists("steam_launcher_settings.json"):
                with open("steam_launcher_settings.json", "r") as f:
                    settings = json.load(f)

                # Load General tab settings
                general = settings.get("general", {})
                for flag, value in general.items():
                    if flag == "dxlevel_enabled":
                        self.dxlevel_toggle.set_active(value)
                        if "-dxlevel" in self.general_dropdowns:
                            self.general_dropdowns["-dxlevel"].get_parent().set_sensitive(value)
                    elif flag in self.toggles:
                        self.toggles[flag].set_active(value)
                    elif flag in self.inputs:
                        self.inputs[flag].set_text(value or "")
                    elif flag in self.general_dropdowns:
                        combo = self.general_dropdowns[flag]
                        options = [combo.get_model()[i][0] for i in range(len(combo.get_model()))]
                        try:
                            if value in options:
                                index = options.index(value)
                                combo.set_active(index)
                        except ValueError:
                            pass

                # Load Tab settings
                for tab_name, tab_settings in settings.get("tabs", {}).items():
                    if tab_name in self.tab_data:
                        data = self.tab_data[tab_name]
                        if data["enable_toggle"] and "enabled" in tab_settings:
                            data["enable_toggle"].set_active(tab_settings["enabled"])
                            if data['content_box']:
                                data['content_box'].set_sensitive(tab_settings["enabled"])

                        for key, value in tab_settings.get("toggles", {}).items():
                            if key in data["toggles"]:
                                data["toggles"][key].set_active(value)

                        for key, value in tab_settings.get("inputs", {}).items():
                            if key in data["inputs"]:
                                data["inputs"][key].set_text(value or "")

                        for key, value in tab_settings.get("dropdowns", {}).items():
                            if key in data["dropdowns"]:
                                combo = data["dropdowns"][key]
                                options = [combo.get_model()[i][0] for i in range(len(combo.get_model()))]
                                try:
                                    if value in options:
                                        index = options.index(value)
                                        combo.set_active(index)
                                except ValueError:
                                    pass

                        for key, value in tab_settings.get("sliders", {}).items():
                            if key in data["sliders"]:
                                data["sliders"][key].set_value(value)
                                if isinstance(data["sliders"][key].get_parent(), Gtk.Box) and len(data["sliders"][key].get_parent().get_children()) > 1:
                                    value_label = data["sliders"][key].get_parent().get_children()[1]
                                    if isinstance(value_label, Gtk.Label):
                                        value_label.set_text(f"{value:.2f}")

                logging.info("Settings loaded successfully.")
            else:
                logging.info("No settings file found.")
        except Exception as e:
            logging.error(f"Failed to load settings: {e}")
            self.show_error_dialog("Load Error", f"Could not load settings.\nError: {e}")

    def on_destroy(self, widget):
        self.on_save_clicked(None)
        Gtk.main_quit()

# SECTION: MAIN FUNCTION
def main():
    try:
        win = SteamLauncherWindow()
        win.show_all()
        Gtk.main()
    except Exception as e:
        print(f"Error in main: {e}")
        logging.error(f"Application failed to start: {e}")

if __name__ == "__main__":
    main()
