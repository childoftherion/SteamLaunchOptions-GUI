print("Starting Steam Launcher...")
# Import necessary libraries
import gi
# Ensure Gtk 3.0 is available
try:
    gi.require_version("Gtk", "3.0")
    from gi.repository import Gtk, Gdk, GLib
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
import shlex
import pexpect
import logging
from collections import defaultdict
import uuid

# SECTION: CONSTANTS
SETTINGS_FILE = "steam_launcher_settings.json"
LOG_FILE = 'steam_launcher.log'

# SECTION: LOGGING SETUP
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logging.info("Steam Launcher application started.")

# SECTION: TAB CONFIGURATIONS
TAB_CONFIGS = {
    "Wine": {
        "enable_label": "Enable Wine",
        "enable_tooltip": "Enable Wine environment settings",
        "env_prefix": "",
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
        "env_prefix": "",
        "command_prefix": "mangohud",
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
        "env_prefix": "",
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
GENERAL_OPTIONS = [
    # Display and Windowing
    ("-fullscreen", "Forces the game to run in fullscreen mode"),
    ("-windowed", "Forces the game to run in windowed mode"),
    ("-nofullscreen", "Forces the game to run in windowed mode (alternative to -windowed)"),
    ("-noborder", "Forces the game to run in borderless windowed mode"),
    # Performance and Graphics
    ("-background", "Forces the game to run in background priority"),
    ("-high", "Forces the game to run in high priority"),
    ("-low", "Forces the game to run in low priority"),
    ("-veryhigh", "Forces the game to run in very high priority"),
    ("-lowmemory", "Forces the game to use less memory"),
    ("-lowbandwidth", "Forces the game to use less bandwidth"),
    ("-nocursor", "Disables the cursor"),
    ("-nod3d9ex", "Disables D3D9Ex mode"),
    ("-noforcemspd", "Disables forced mouse speed"),
    ("-nograbinput", "Disables input grabbing"),
    ("-nohwcursor", "Disables hardware cursor"),
    ("-noipx", "Disables IPX protocol"),
    ("-noreflect", "Disables reflections"),
    ("-noshadow", "Disables shadows"),
    ("-nothreads", "Disables multithreading"),
    ("-nothreading", "Disables threading"),
    ("-novsync", "Disables vertical sync"),
    ("-force-glcore", "Forces the game to use OpenGL core profile"),
    ("-vulkan", "Forces the game to use Vulkan"),
    ("-soft", "Forces software rendering"),
    ("-nojoy", "Disables joystick support"),
    ("-nohltv", "Disables the in-game TV"),
    # Input and Hardware
    ("-nogamepad", "Disables gamepad input"),
    ("-nojoystick", "Disables joystick support"),
    ("-nokb", "Disables keyboard input"),
    ("-nomouse", "Disables mouse input"),
    ("-nomouseaccel", "Disables mouse acceleration"),
    ("-nomouseborder", "Disables mouse border in windowed mode"),
    ("-nohmd", "Disables VR support"),
    # Networking
    ("-insecure", "Allows the game to connect to insecure servers"),
    ("-secure", "Forces the game to connect only to secure servers"),
    ("-lan", "Forces the game to use LAN mode (1 for LAN, 0 for internet)"),
    ("-nolobby", "Disables the lobby"),
    ("-nolobbychat", "Disables lobby chat"),
    ("-nolobbyinvites", "Disables lobby invites"),
    ("-nolobbyjoin", "Disables joining lobbies"),
    ("-nolobbyleave", "Disables leaving lobbies"),
    ("-nolobbysearch", "Disables lobby search"),
    ("-noserverbrowser", "Disables the server browser"),
    # Debugging and Troubleshooting
    ("-console", "Opens the in-game console"),
    ("-debug", "Enables debug mode"),
    ("-nocrashdialog", "Suppresses the crash dialog if the game crashes"),
    ("-nogamestats", "Disables game statistics"),
    ("-nointro", "Skips the game's intro video"),
    ("-nologo", "Skips the company logos"),
    ("-nostartupmovie", "Skips the startup movie"),
    ("-noupdate", "Disables automatic updates"),
    ("-validate", "Validates the game files (useful for troubleshooting)"),
    # Audio
    ("-nosound", "Disables sound"),
    ("-noaudio", "Disables audio"),
    ("-nosoundbuffering", "Disables sound buffering"),
    ("-nosounddevice", "Disables the sound device"),
    ("-nosoundinit", "Disables sound initialization"),
    ("-nosoundasync", "Disables asynchronous sound"),
    ("-nosound3d", "Disables 3D sound"),
    ("-nosoundhardware", "Disables hardware sound"),
    ("-nosoundsoftware", "Disables software sound"),
    ("-nosounddriver", "Disables the sound driver"),
    # Additional Audio Options
    ("-nosoundcard", "Disables the sound card"),
    ("-nosoundoutput", "Disables sound output"),
    ("-nosoundinput", "Disables sound input"),
    ("-nosoundmixer", "Disables the sound mixer"),
    ("-nosoundeffects", "Disables sound effects"),
    ("-nosoundmusic", "Disables music"),
    ("-nosoundvoice", "Disables voice chat"),
    ("-nosoundloop", "Disables sound looping"),
    ("-nosoundstreaming", "Disables sound streaming"),
    ("-nosoundcompression", "Disables sound compression"),
    ("-nosoundfiltering", "Disables sound filtering"),
    ("-nosoundreverb", "Disables sound reverb"),
    ("-nosoundecho", "Disables sound echo"),
    ("-nosounddoppler", "Disables sound Doppler effect"),
    ("-nosounddistortion", "Disables sound distortion"),
    ("-nosoundattenuation", "Disables sound attenuation"),
    ("-nosoundocclusion", "Disables sound occlusion"),
    ("-nosoundpanning", "Disables sound panning"),
    ("-nosoundvolume", "Disables sound volume control"),
    ("-nosoundbalance", "Disables sound balance control"),
    ("-nosoundbass", "Disables sound bass control"),
    ("-nosoundtreble", "Disables sound treble control"),
    ("-nosoundsurround", "Disables surround sound"),
    ("-nosoundstereo", "Disables stereo sound"),
]

# SECTION: GENERAL INPUTS
GENERAL_INPUTS = [
    # Display and Windowing
    ("-w", "Sets the game window width", "e.g., 1920"),
    ("-h", "Sets the game window height", "e.g., 1080"),
    ("-fullscreen_width", "Sets the fullscreen width", "e.g., 1920"),
    ("-fullscreen_height", "Sets the fullscreen height", "e.g., 1080"),
    # Performance and Graphics
    ("-dxlevel", "Forces a specific DirectX level (e.g., -dxlevel 90 for DirectX 9)", "e.g., 90"),
    ("-CpuCount", "Specifies the number of CPU cores to use for the game", "e.g., 4"),
    ("-forcemspd", "Forces a specific mouse speed", "e.g., 500"),
    ("+r_rootlod", "Adjusts model detail (0 for high, 1 for medium, 2 for low)", "e.g., 1"),
    ("+mat_picmip", "Adjusts texture detail (0 for high, 1 for medium, 2 for low)", "e.g., 1"),
    ("+mat_reducefillrate", "Adjusts shader detail (0 for high, 1 for low)", "e.g., 1"),
    ("+r_shadowrendertotexture", "Adjusts shadow detail (0 for low, 1 for high)", "e.g., 1"),
    ("+r_waterforceexpensive", "Adjusts water detail (0 for low, 1 for high)", "e.g., 1"),
    ("+r_waterforcereflectentities", "Adjusts water reflectiveness (0 for low, 1 for high)", "e.g., 1"),
    # Networking
    ("-ip", "Specifies the IP address to bind to", "e.g., 192.168.1.100"),
    ("-port", "Specifies the port to use", "e.g., 27015"),
    # Debugging and Troubleshooting
    ("-debug_file", "Writes debug information to a file", "e.g., /path/to/debug.log"),
    # Audio
    ("-soundbuffer", "Sets the sound buffer size", "e.g., 1024"),
]

# SECTION: DX LEVEL PRESETS
DX_LEVEL_PRESETS = [
    "50", "70", "80", "81", "90", "95", "98",
    "100", "110", "120",
]

# SECTION: MAIN WINDOW CLASS
class SteamLauncherWindow(Gtk.Window):
    def __init__(self):
        try:
            super().__init__(title="Steam Game Launcher")
            print("Initializing Steam Launcher...")
            self.set_border_width(10)
            self.set_default_size(1000, 700)

            # Main vertical box
            vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
            self.add(vbox)

            # Header
            header = Gtk.Label(label="Steam Launch Options\nCustomize your game launch command with tabs for overlays and enhancements")
            header.set_justify(Gtk.Justification.CENTER)
            vbox.pack_start(header, False, False, 0)

            # Detect Section
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

            # Notebook
            self.notebook = Gtk.Notebook()
            vbox.pack_start(self.notebook, True, True, 0)

            # General Tab
            self.toggles = {}
            self.inputs = {}
            self.general_dropdowns = {}
            self.dxlevel_toggle = None
            self.setup_general_tab(self.notebook)

            # Software Checks
            self.software_checked = {tab: False for tab in TAB_CONFIGS if "software_requirement" in TAB_CONFIGS[tab]}

            # Other Tabs
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

            self.notebook.connect("switch-page", self.on_tab_switched)

            # Summary Section
            summary_frame = Gtk.Frame(label="Selected Options Summary")
            summary_scrolled = Gtk.ScrolledWindow()
            summary_scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
            summary_scrolled.set_min_content_height(150)
            self.summary_textview = Gtk.TextView()
            self.summary_textview.set_editable(False)
            self.summary_textview.set_wrap_mode(Gtk.WrapMode.WORD)
            self.summary_buffer = self.summary_textview.get_buffer()
            summary_scrolled.add(self.summary_textview)
            summary_frame.add(summary_scrolled)
            vbox.pack_start(summary_frame, False, True, 5)
            self.summary_buffer.set_text("No options selected.")

            # Buttons
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

            # Generated Command Output
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

            # Styling
            css = """
            window, dialog { background-color: #353535; }
            label, button { color: #e0e0e0; }
            button { background-color: #4a4a4a; border: 1px solid #707070; border-radius: 5px; }
            button:hover { background-color: #606060; }
            entry, textview text { background-color: #404040; color: #e0e0e0; border: 1px solid #707070; border-radius: 5px; }
            switch { background-color: #404040; }
            switch slider { background-color: #808080; border-radius: 10px; }
            switch:checked slider { background-color: #00aaff; }
            tooltip { background-color: #000000; color: #ffffff; border: 1px solid #a0a0a0; border-radius: 5px; padding: 4px; }
            .enable-label { font-weight: bold; font-size: 14px; color: #00aaff; }
            .vkbasalt-grid { margin: 10px; padding: 10px; }
            .vkbasalt-slider-box { margin: 5px 0; padding: 5px; }
            """
            css_provider = Gtk.CssProvider()
            css_provider.load_from_data(css.encode())
            Gtk.StyleContext.add_provider_for_screen(
                Gdk.Screen.get_default(),
                css_provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )

            self.connect("destroy", self.on_destroy)
            GLib.idle_add(self.build_detection_mappings)
            GLib.idle_add(self.load_settings)
        except Exception as e:
            print(f"Error initializing application: {e}")
            raise

    # SECTION: UI SETUP HELPERS
    def _create_toggle(self, label, tooltip):
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

    # SECTION: SUMMARY METHODS
    def update_summary(self, *args):
        summary_data = self.collect_summary_data()
        summary_text = self.format_summary(summary_data)
        self.summary_buffer.set_text(summary_text)

    def collect_summary_data(self):
        summary_data = defaultdict(list)

        # General Tab - Toggles
        for flag, toggle in self.toggles.items():
            if toggle.get_active():
                description = next((desc for f, desc in GENERAL_OPTIONS if f == flag), flag)
                summary_data[self.get_general_category(flag)].append((flag, description))

        # General Tab - Inputs
        for flag, entry in self.inputs.items():
            value = entry.get_text().strip()
            if value:
                description = next((desc for f, desc, _ in GENERAL_INPUTS if f == flag), flag)
                summary_data[self.get_general_category(flag)].append((f"{flag} {value}", description))

        # General Tab - Dropdowns (dxlevel)
        if self.dxlevel_toggle.get_active():
            for flag, combo in self.general_dropdowns.items():
                value = combo.get_active_text()
                if value is not None:
                    description = next((desc for f, desc, _ in GENERAL_INPUTS if f == flag), flag)
                    summary_data["Performance and Graphics"].append((f"{flag} {value}", description))

        # Other Tabs
        for tab_name, data in self.tab_data.items():
            if data["enable_toggle"] and data["enable_toggle"].get_active():
                config = TAB_CONFIGS[tab_name]

                # Toggles
                if "toggles" in config:
                    for option, desc in config["toggles"]:
                        if data["toggles"][option].get_active():
                            summary_data[tab_name].append((option, desc))

                # Inputs
                if "inputs" in config:
                    for option, desc, _ in config["inputs"]:
                        value = data["inputs"][option].get_text().strip()
                        if value:
                            summary_data[tab_name].append((f"{option}={value}", desc))

                # Dropdowns
                if "dropdowns" in config:
                    for key, dd_config in config["dropdowns"].items():
                        value = data["dropdowns"][key].get_active_text()
                        if value is not None:
                            summary_data[tab_name].append((f"{key}={value}", dd_config.get("tooltip", key)))

                # Sliders
                if "sliders" in config:
                    for option, desc, _, _ in config["sliders"]:
                        value = data["sliders"][option].get_value()
                        if value != 0:
                            summary_data[tab_name].append((f"{option}={value:.2f}", desc))

        return summary_data

    def format_summary(self, summary_data):
            lines = []
            if not summary_data:
                return "No options selected."
            for category, options in sorted(summary_data.items()):
                lines.append(f"**{category}**")
                for flag, desc in sorted(options):
                    lines.append(f"- {flag}: {desc}")
                lines.append("")
            return "\n".join(lines)

    def get_general_category(self, flag):
        categories = [
            ("Display and Windowing", [
                ("-fullscreen", "Forces the game to run in fullscreen mode"),
                ("-windowed", "Forces the game to run in windowed mode"),
                ("-nofullscreen", "Forces the game to run in windowed mode (alternative to -windowed)"),
                ("-noborder", "Forces the game to run in borderless windowed mode"),
            ], [
                ("-w", "Sets the game window width", "e.g., 1920"),
                ("-h", "Sets the game window height", "e.g., 1080"),
                ("-fullscreen_width", "Sets the fullscreen width", "e.g., 1920"),
                ("-fullscreen_height", "Sets the fullscreen height", "e.g., 1080"),
            ]),
            ("Performance and Graphics", [
                ("-background", "Forces the game to run in background priority"),
                ("-high", "Forces the game to run in high priority"),
                ("-low", "Forces the game to run in low priority"),
                ("-veryhigh", "Forces the game to run in very high priority"),
                ("-lowmemory", "Forces the game to use less memory"),
                ("-lowbandwidth", "Forces the game to use less bandwidth"),
                ("-nocursor", "Disables the cursor"),
                ("-nod3d9ex", "Disables D3D9Ex mode"),
                ("-noforcemspd", "Disables forced mouse speed"),
                ("-nograbinput", "Disables input grabbing"),
                ("-nohwcursor", "Disables hardware cursor"),
                ("-noipx", "Disables IPX protocol"),
                ("-noreflect", "Disables reflections"),
                ("-noshadow", "Disables shadows"),
                ("-nothreads", "Disables multithreading"),
                ("-nothreading", "Disables threading"),
                ("-novsync", "Disables vertical sync"),
                ("-force-glcore", "Forces the game to use OpenGL core profile"),
                ("-vulkan", "Forces the game to use Vulkan"),
                ("-soft", "Forces software rendering"),
                ("-nojoy", "Disables joystick support"),
                ("-nohltv", "Disables the in-game TV"),
            ], [
                ("-dxlevel", "Forces a specific DirectX level (e.g., -dxlevel 90 for DirectX 9)", "e.g., 90"),
                ("-CpuCount", "Specifies the number of CPU cores to use for the game", "e.g., 4"),
                ("-forcemspd", "Forces a specific mouse speed", "e.g., 500"),
                ("+r_rootlod", "Adjusts model detail (0 for high, 1 for medium, 2 for low)", "e.g., 1"),
                ("+mat_picmip", "Adjusts texture detail (0 for high, 1 for medium, 2 for low)", "e.g., 1"),
                ("+mat_reducefillrate", "Adjusts shader detail (0 for high, 1 for low)", "e.g., 1"),
                ("+r_shadowrendertotexture", "Adjusts shadow detail (0 for low, 1 for high)", "e.g., 1"),
                ("+r_waterforceexpensive", "Adjusts water detail (0 for low, 1 for high)", "e.g., 1"),
                ("+r_waterforcereflectentities", "Adjusts water reflectiveness (0 for low, 1 for high)", "e.g., 1"),
            ]),
            ("Input and Hardware", [
                ("-nogamepad", "Disables gamepad input"),
                ("-nojoystick", "Disables joystick support"),
                ("-nokb", "Disables keyboard input"),
                ("-nomouse", "Disables mouse input"),
                ("-nomouseaccel", "Disables mouse acceleration"),
                ("-nomouseborder", "Disables mouse border in windowed mode"),
                ("-nohmd", "Disables VR support"),
            ], []),
            ("Networking", [
                ("-insecure", "Allows the game to connect to insecure servers"),
                ("-secure", "Forces the game to connect only to secure servers"),
                ("-lan", "Forces the game to use LAN mode (1 for LAN, 0 for internet)"),
                ("-nolobby", "Disables the lobby"),
                ("-nolobbychat", "Disables lobby chat"),
                ("-nolobbyinvites", "Disables lobby invites"),
                ("-nolobbyjoin", "Disables joining lobbies"),
                ("-nolobbyleave", "Disables leaving lobbies"),
                ("-nolobbysearch", "Disables lobby search"),
                ("-noserverbrowser", "Disables the server browser"),
            ], [
                ("-ip", "Specifies the IP address to bind to", "e.g., 192.168.1.100"),
                ("-port", "Specifies the port to use", "e.g., 27015"),
            ]),
            ("Debugging and Troubleshooting", [
                ("-console", "Opens the in-game console"),
                ("-debug", "Enables debug mode"),
                ("-nocrashdialog", "Suppresses the crash dialog if the game crashes"),
                ("-nogamestats", "Disables game statistics"),
                ("-nointro", "Skips the game's intro video"),
                ("-nologo", "Skips the company logos"),
                ("-nostartupmovie", "Skips the startup movie"),
                ("-noupdate", "Disables automatic updates"),
                ("-validate", "Validates the game files (useful for troubleshooting)"),
            ], [
                ("-debug_file", "Writes debug information to a file", "e.g., /path/to/debug.log"),
            ]),
            ("Audio", [
                ("-nosound", "Disables sound"),
                ("-noaudio", "Disables audio"),
                ("-nosoundbuffering", "Disables sound buffering"),
                ("-nosounddevice", "Disables the sound device"),
                ("-nosoundinit", "Disables sound initialization"),
                ("-nosoundasync", "Disables asynchronous sound"),
                ("-nosound3d", "Disables 3D sound"),
                ("-nosoundhardware", "Disables hardware sound"),
                ("-nosoundsoftware", "Disables software sound"),
                ("-nosounddriver", "Disables the sound driver"),
            ], [
                ("-soundbuffer", "Sets the sound buffer size", "e.g., 1024"),
            ]),
            ("Additional Audio Options", [
                ("-nosoundcard", "Disables the sound card"),
                ("-nosoundoutput", "Disables sound output"),
                ("-nosoundinput", "Disables sound input"),
                ("-nosoundmixer", "Disables the sound mixer"),
                ("-nosoundeffects", "Disables sound effects"),
                ("-nosoundmusic", "Disables music"),
                ("-nosoundvoice", "Disables voice chat"),
                ("-nosoundloop", "Disables sound looping"),
                ("-nosoundstreaming", "Disables sound streaming"),
                ("-nosoundcompression", "Disables sound compression"),
                ("-nosoundfiltering", "Disables sound filtering"),
                ("-nosoundreverb", "Disables sound reverb"),
                ("-nosoundecho", "Disables sound echo"),
                ("-nosounddoppler", "Disables sound Doppler effect"),
                ("-nosounddistortion", "Disables sound distortion"),
                ("-nosoundattenuation", "Disables sound attenuation"),
                ("-nosoundocclusion", "Disables sound occlusion"),
                ("-nosoundpanning", "Disables sound panning"),
                ("-nosoundvolume", "Disables sound volume control"),
                ("-nosoundbalance", "Disables sound balance control"),
                ("-nosoundbass", "Disables sound bass control"),
                ("-nosoundtreble", "Disables sound treble control"),
                ("-nosoundsurround", "Disables surround sound"),
                ("-nosoundstereo", "Disables stereo sound"),
            ], []),
        ]
        for category, toggles, inputs in categories:
            if any(flag == f for f, _ in toggles) or any(flag == f for f, _, _ in inputs):
                return category
        return "General"

    # SECTION: TAB SETUP
    def setup_general_tab(self, notebook):
        tab_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        tab_vbox.set_border_width(10)
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.add(tab_vbox)

        categories = [
            ("Display and Windowing", [
                ("-fullscreen", "Forces the game to run in fullscreen mode"),
                ("-windowed", "Forces the game to run in windowed mode"),
                ("-nofullscreen", "Forces the game to run in windowed mode (alternative to -windowed)"),
                ("-noborder", "Forces the game to run in borderless windowed mode"),
            ], [
                ("-w", "Sets the game window width", "e.g., 1920"),
                ("-h", "Sets the game window height", "e.g., 1080"),
                ("-fullscreen_width", "Sets the fullscreen width", "e.g., 1920"),
                ("-fullscreen_height", "Sets the fullscreen height", "e.g., 1080"),
            ]),
            ("Performance and Graphics", [
                ("-background", "Forces the game to run in background priority"),
                ("-high", "Forces the game to run in high priority"),
                ("-low", "Forces the game to run in low priority"),
                ("-veryhigh", "Forces the game to run in very high priority"),
                ("-lowmemory", "Forces the game to use less memory"),
                ("-lowbandwidth", "Forces the game to use less bandwidth"),
                ("-nocursor", "Disables the cursor"),
                ("-nod3d9ex", "Disables D3D9Ex mode"),
                ("-noforcemspd", "Disables forced mouse speed"),
                ("-nograbinput", "Disables input grabbing"),
                ("-nohwcursor", "Disables hardware cursor"),
                ("-noipx", "Disables IPX protocol"),
                ("-noreflect", "Disables reflections"),
                ("-noshadow", "Disables shadows"),
                ("-nothreads", "Disables multithreading"),
                ("-nothreading", "Disables threading"),
                ("-novsync", "Disables vertical sync"),
                ("-force-glcore", "Forces the game to use OpenGL core profile"),
                ("-vulkan", "Forces the game to use Vulkan"),
                ("-soft", "Forces software rendering"),
                ("-nojoy", "Disables joystick support"),
                ("-nohltv", "Disables the in-game TV"),
            ], [
                ("-dxlevel", "Forces a specific DirectX level (e.g., -dxlevel 90 for DirectX 9)", "e.g., 90"),
                ("-CpuCount", "Specifies the number of CPU cores to use for the game", "e.g., 4"),
                ("-forcemspd", "Forces a specific mouse speed", "e.g., 500"),
                ("+r_rootlod", "Adjusts model detail (0 for high, 1 for medium, 2 for low)", "e.g., 1"),
                ("+mat_picmip", "Adjusts texture detail (0 for high, 1 for medium, 2 for low)", "e.g., 1"),
                ("+mat_reducefillrate", "Adjusts shader detail (0 for high, 1 for low)", "e.g., 1"),
                ("+r_shadowrendertotexture", "Adjusts shadow detail (0 for low, 1 for high)", "e.g., 1"),
                ("+r_waterforceexpensive", "Adjusts water detail (0 for low, 1 for high)", "e.g., 1"),
                ("+r_waterforcereflectentities", "Adjusts water reflectiveness (0 for low, 1 for high)", "e.g., 1"),
            ]),
            ("Input and Hardware", [
                ("-nogamepad", "Disables gamepad input"),
                ("-nojoystick", "Disables joystick support"),
                ("-nokb", "Disables keyboard input"),
                ("-nomouse", "Disables mouse input"),
                ("-nomouseaccel", "Disables mouse acceleration"),
                ("-nomouseborder", "Disables mouse border in windowed mode"),
                ("-nohmd", "Disables VR support"),
            ], []),
            ("Networking", [
                ("-insecure", "Allows the game to connect to insecure servers"),
                ("-secure", "Forces the game to connect only to secure servers"),
                ("-lan", "Forces the game to use LAN mode (1 for LAN, 0 for internet)"),
                ("-nolobby", "Disables the lobby"),
                ("-nolobbychat", "Disables lobby chat"),
                ("-nolobbyinvites", "Disables lobby invites"),
                ("-nolobbyjoin", "Disables joining lobbies"),
                ("-nolobbyleave", "Disables leaving lobbies"),
                ("-nolobbysearch", "Disables lobby search"),
                ("-noserverbrowser", "Disables the server browser"),
            ], [
                ("-ip", "Specifies the IP address to bind to", "e.g., 192.168.1.100"),
                ("-port", "Specifies the port to use", "e.g., 27015"),
            ]),
            ("Debugging and Troubleshooting", [
                ("-console", "Opens the in-game console"),
                ("-debug", "Enables debug mode"),
                ("-nocrashdialog", "Suppresses the crash dialog if the game crashes"),
                ("-nogamestats", "Disables game statistics"),
                ("-nointro", "Skips the game's intro video"),
                ("-nologo", "Skips the company logos"),
                ("-nostartupmovie", "Skips the startup movie"),
                ("-noupdate", "Disables automatic updates"),
                ("-validate", "Validates the game files (useful for troubleshooting)"),
            ], [
                ("-debug_file", "Writes debug information to a file", "e.g., /path/to/debug.log"),
            ]),
            ("Audio", [
                ("-nosound", "Disables sound"),
                ("-noaudio", "Disables audio"),
                ("-nosoundbuffering", "Disables sound buffering"),
                ("-nosounddevice", "Disables the sound device"),
                ("-nosoundinit", "Disables sound initialization"),
                ("-nosoundasync", "Disables asynchronous sound"),
                ("-nosound3d", "Disables 3D sound"),
                ("-nosoundhardware", "Disables hardware sound"),
                ("-nosoundsoftware", "Disables software sound"),
                ("-nosounddriver", "Disables the sound driver"),
            ], [
                ("-soundbuffer", "Sets the sound buffer size", "e.g., 1024"),
            ]),
            ("Additional Audio Options", [
                ("-nosoundcard", "Disables the sound card"),
                ("-nosoundoutput", "Disables sound output"),
                ("-nosoundinput", "Disables sound input"),
                ("-nosoundmixer", "Disables the sound mixer"),
                ("-nosoundeffects", "Disables sound effects"),
                ("-nosoundmusic", "Disables music"),
                ("-nosoundvoice", "Disables voice chat"),
                ("-nosoundloop", "Disables sound looping"),
                ("-nosoundstreaming", "Disables sound streaming"),
                ("-nosoundcompression", "Disables sound compression"),
                ("-nosoundfiltering", "Disables sound filtering"),
                ("-nosoundreverb", "Disables sound reverb"),
                ("-nosoundecho", "Disables sound echo"),
                ("-nosounddoppler", "Disables sound Doppler effect"),
                ("-nosounddistortion", "Disables sound distortion"),
                ("-nosoundattenuation", "Disables sound attenuation"),
                ("-nosoundocclusion", "Disables sound occlusion"),
                ("-nosoundpanning", "Disables sound panning"),
                ("-nosoundvolume", "Disables sound volume control"),
                ("-nosoundbalance", "Disables sound balance control"),
                ("-nosoundbass", "Disables sound bass control"),
                ("-nosoundtreble", "Disables sound treble control"),
                ("-nosoundsurround", "Disables surround sound"),
                ("-nosoundstereo", "Disables stereo sound"),
            ], []),
        ]

        for category_name, toggles_list, inputs_list in categories:
            if toggles_list:
                toggles_frame = Gtk.Frame(label=category_name)
                tab_vbox.pack_start(toggles_frame, False, False, 5)
                toggles_grid = Gtk.Grid(column_spacing=20, row_spacing=10)
                toggles_grid.set_border_width(10)
                toggles_frame.add(toggles_grid)
                col, row = 0, 0
                max_cols = 2
                for flag, tooltip in toggles_list:
                    label_text = flag.lstrip('-').replace('_', ' ').title()
                    hbox, toggle = self._create_toggle(label_text, f"{tooltip} ({flag})")
                    toggles_grid.attach(hbox, col, row, 1, 1)
                    self.toggles[flag] = toggle
                    toggle.connect("toggled", self.update_summary)
                    col += 1
                    if col >= max_cols:
                        col = 0
                        row += 1

            if inputs_list or (category_name == "Performance and Graphics" and "-dxlevel" in [flag for flag, _, _ in inputs_list]):
                inputs_frame = Gtk.Frame(label=f"{category_name} Settings")
                tab_vbox.pack_start(inputs_frame, False, False, 5)
                inputs_grid = Gtk.Grid(column_spacing=10, row_spacing=10)
                inputs_grid.set_border_width(10)
                inputs_frame.add(inputs_grid)
                row = 0
                for flag, label, placeholder in inputs_list:
                    if flag == "-dxlevel":
                        dx_toggle_hbox, dx_toggle = self._create_toggle("Enable DirectX Level", f"Enable DirectX Level ({flag})")
                        self.dxlevel_toggle = dx_toggle
                        inputs_grid.attach(dx_toggle_hbox, 0, row, 1, 1)
                        dx_toggle.connect("toggled", self.update_summary)
                        row += 1
                        dx_options = DX_LEVEL_PRESETS
                        dx_tooltip = f"{label} ({flag})"
                        hbox_dx, combo_dx = self._create_dropdown("DirectX Level", dx_options, None, dx_tooltip)
                        inputs_grid.attach(hbox_dx, 0, row, 1, 1)
                        self.general_dropdowns[flag] = combo_dx
                        combo_dx.connect("changed", self.update_summary)
                        hbox_dx.set_sensitive(False)
                        dx_toggle.connect("toggled", self.on_dxlevel_toggle, hbox_dx)
                    else:
                        label_text = label
                        hbox, entry = self._create_input(label_text, f"{label} ({flag})", placeholder)
                        inputs_grid.attach(hbox, 0, row, 1, 1)
                        self.inputs[flag] = entry
                        entry.connect("changed", self.update_summary)
                    row += 1

        notebook.append_page(scrolled_window, Gtk.Label(label="General"))

    def on_dxlevel_toggle(self, toggle, dxlevel_hbox):
        is_active = toggle.get_active()
        dxlevel_hbox.set_sensitive(is_active)
        logging.debug(f"DirectX Level dropdown sensitivity set to {is_active}")
        self.update_summary()

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

        # Enable Toggle
        enable_toggle = Gtk.CheckButton(label=config.get("enable_label", f"Enable {tab_name}"))
        enable_toggle.set_tooltip_text(config.get("enable_tooltip", f"Enable {tab_name} options"))
        tab_vbox.pack_start(enable_toggle, False, False, 0)
        self.tab_data[tab_name]['enable_toggle'] = enable_toggle
        enable_toggle.connect("toggled", self.on_enable_toggle, tab_name)
        enable_toggle.connect("toggled", self.update_summary)

        # Content Box
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        content_box.set_border_width(5)
        tab_vbox.pack_start(content_box, True, True, 0)
        self.tab_data[tab_name]['content_box'] = content_box

        # Install Button
        if "software_requirement" in config and config["software_requirement"] != "vkbasalt":
            software = config["software_requirement"]
            install_button = Gtk.Button(label=f"Install {software}")
            install_button.set_tooltip_text(f"Install {software} using apt")
            install_button.connect("clicked", self.on_install_software_clicked, tab_name, software)
            content_box.pack_start(install_button, False, False, 0)
            self.tab_data[tab_name]['install_button'] = install_button
            if self.check_software(software):
                install_button.set_visible(False)
                self.software_checked[tab_name] = True

        content_box.set_sensitive(enable_toggle.get_active())

        # Toggles
        if "toggles" in config:
            toggles_frame = Gtk.Frame(label="Options / Flags")
            content_box.pack_start(toggles_frame, False, False, 0)
            toggles_grid = Gtk.Grid(column_spacing=20, row_spacing=10)
            toggles_grid.set_border_width(10)
            if tab_name == "vkBasalt":
                toggles_grid.get_style_context().add_class("vkbasalt-grid")
            toggles_frame.add(toggles_grid)
            col, row = 0, 0
            max_cols = 2
            for option, tooltip in config["toggles"]:
                label_text = option.replace('_', ' ').title()
                hbox, toggle = self._create_toggle(label_text, tooltip)
                toggles_grid.attach(hbox, col, row, 1, 1)
                self.tab_data[tab_name]['toggles'][option] = toggle
                toggle.connect("toggled", self.update_summary)
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1

        # Inputs
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
                entry.connect("changed", self.update_summary)
                row += 1

        # Dropdowns
        if "dropdowns" in config:
            dropdowns_frame = Gtk.Frame(label="Choices")
            content_box.pack_start(dropdowns_frame, False, False, 10)
            dropdowns_grid = Gtk.Grid(column_spacing=10, row_spacing=10)
            dropdowns_grid.set_border_width(10)
            dropdowns_frame.add(dropdowns_grid)
            row = 0
            for key, dd_config in config["dropdowns"].items():
                hbox, combo = self._create_dropdown(
                    dd_config["label"],
                    dd_config["options"],
                    dd_config.get("default"),
                    dd_config["tooltip"]
                )
                dropdowns_grid.attach(hbox, 0, row, 1, 1)
                self.tab_data[tab_name]['dropdowns'][key] = combo
                combo.connect("changed", self.update_summary)
                row += 1

        # Sliders
        if "sliders" in config:
            sliders_frame = Gtk.Frame(label="Adjustments")
            content_box.pack_start(sliders_frame, False, False, 10)
            sliders_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
            sliders_box.set_border_width(10)
            if tab_name == "vkBasalt":
                sliders_box.get_style_context().add_class("vkbasalt-slider-box")
            sliders_frame.add(sliders_box)
            for option, label, min_val, max_val in config["sliders"]:
                hbox, scale = self._create_slider(label, min_val, max_val, label)
                sliders_box.pack_start(hbox, False, False, 0)
                self.tab_data[tab_name]['sliders'][option] = scale
                scale.connect("value-changed", self.update_summary)

        notebook.append_page(scrolled_window, Gtk.Label(label=tab_name))

    def on_enable_toggle(self, toggle, tab_name):
        self.tab_data[tab_name]['content_box'].set_sensitive(toggle.get_active())
        self.update_summary()

    def on_install_software_clicked(self, button, tab_name, software):
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text=f"Install {software}?",
        )
        dialog.format_secondary_text(f"This will run 'sudo apt install {software}'.")
        response = dialog.run()
        dialog.destroy()

        if response == Gtk.ResponseType.YES:
            try:
                child = pexpect.spawn(f"sudo apt install {software}")
                child.expect(".*password.*:")
                child.sendline("your_password")  # Replace with secure password handling
                child.expect(pexpect.EOF)
                if child.exitstatus == 0:
                    self.tab_data[tab_name]['install_button'].set_visible(False)
                    self.software_checked[tab_name] = True
                    dialog = Gtk.MessageDialog(
                        transient_for=self,
                        flags=0,
                        message_type=Gtk.MessageType.INFO,
                        buttons=Gtk.ButtonsType.OK,
                        text=f"{software} installed successfully."
                    )
                    dialog.run()
                    dialog.destroy()
                else:
                    dialog = Gtk.MessageDialog(
                        transient_for=self,
                        flags=0,
                        message_type=Gtk.MessageType.ERROR,
                        buttons=Gtk.ButtonsType.OK,
                        text=f"Failed to install {software}."
                    )
                    dialog.run()
                    dialog.destroy()
            except Exception as e:
                logging.error(f"Error installing {software}: {e}")
                dialog = Gtk.MessageDialog(
                    transient_for=self,
                    flags=0,
                    message_type=Gtk.MessageType.ERROR,
                    buttons=Gtk.ButtonsType.OK,
                    text=f"Error installing {software}: {str(e)}"
                )
                dialog.run()
                dialog.destroy()

    def check_software(self, software):
        try:
            result = subprocess.run(['which', software], capture_output=True, text=True)
            return result.returncode == 0
        except Exception as e:
            logging.error(f"Error checking software {software}: {e}")
            return False

    def on_tab_switched(self, notebook, page, page_num):
        pass  # No software checks as per original code

    def build_detection_mappings(self):
        self.toggle_mappings = {flag: flag for flag, _ in GENERAL_OPTIONS}
        self.input_mappings = {flag: flag for flag, _, _ in GENERAL_INPUTS}
        self.tab_toggle_mappings = {}
        self.tab_input_mappings = {}
        self.tab_dropdown_mappings = {}
        self.tab_slider_mappings = {}
        for tab_name, config in TAB_CONFIGS.items():
            if "toggles" in config:
                for option, _ in config["toggles"]:
                    self.tab_toggle_mappings[option] = (tab_name, option)
            if "inputs" in config:
                for option, _, _ in config["inputs"]:
                    self.tab_input_mappings[option] = (tab_name, option)
            if "dropdowns" in config:
                for key in config["dropdowns"]:
                    self.tab_dropdown_mappings[key] = (tab_name, key)
            if "sliders" in config:
                for option, _, _, _ in config["sliders"]:
                    self.tab_slider_mappings[option] = (tab_name, option)

    def load_settings(self):
        try:
            if os.path.exists(SETTINGS_FILE):
                with open(SETTINGS_FILE, 'r') as f:
                    settings = json.load(f)
                
                # General tab toggles
                for flag, value in settings.get('general_toggles', {}).items():
                    if flag in self.toggles:
                        self.toggles[flag].set_active(value)
                
                # General tab inputs
                for flag, value in settings.get('general_inputs', {}).items():
                    if flag in self.inputs:
                        self.inputs[flag].set_text(value)
                
                # General tab dropdowns (dxlevel)
                if 'dxlevel_toggle' in settings:
                    self.dxlevel_toggle.set_active(settings['dxlevel_toggle'])
                for flag, value in settings.get('general_dropdowns', {}).items():
                    if flag in self.general_dropdowns:
                        combo = self.general_dropdowns[flag]
                        for i in range(combo.get_model().iter_n_children(None)):
                            if combo.get_active_text() == value:
                                combo.set_active(i)
                                break
                
                # Other tabs
                for tab_name in self.tab_data:
                    tab_settings = settings.get(tab_name, {})
                    # Enable toggle
                    if 'enable' in tab_settings:
                        self.tab_data[tab_name]['enable_toggle'].set_active(tab_settings['enable'])
                    # Toggles
                    for option, value in tab_settings.get('toggles', {}).items():
                        if option in self.tab_data[tab_name]['toggles']:
                            self.tab_data[tab_name]['toggles'][option].set_active(value)
                    # Inputs
                    for option, value in tab_settings.get('inputs', {}).items():
                        if option in self.tab_data[tab_name]['inputs']:
                            self.tab_data[tab_name]['inputs'][option].set_text(value)
                    # Dropdowns
                    for key, value in tab_settings.get('dropdowns', {}).items():
                        if key in self.tab_data[tab_name]['dropdowns']:
                            combo = self.tab_data[tab_name]['dropdowns'][key]
                            for i in range(combo.get_model().iter_n_children(None)):
                                if combo.get_model()[i][0] == value:
                                    combo.set_active(i)
                                    break
                    # Sliders
                    for option, value in tab_settings.get('sliders', {}).items():
                        if option in self.tab_data[tab_name]['sliders']:
                            self.tab_data[tab_name]['sliders'][option].set_value(value)
                
                logging.info("Settings loaded successfully")
                self.update_summary()
        except Exception as e:
            logging.error(f"Error loading settings: {e}")

    def on_save_clicked(self, button):
        settings = {
            'general_toggles': {flag: toggle.get_active() for flag, toggle in self.toggles.items()},
            'general_inputs': {flag: entry.get_text().strip() for flag, entry in self.inputs.items()},
            'general_dropdowns': {flag: combo.get_active_text() for flag, combo in self.general_dropdowns.items() if combo.get_active_text()},
            'dxlevel_toggle': self.dxlevel_toggle.get_active()
        }
        
        for tab_name, data in self.tab_data.items():
            settings[tab_name] = {
                'enable': data['enable_toggle'].get_active(),
                'toggles': {option: toggle.get_active() for option, toggle in data['toggles'].items()},
                'inputs': {option: entry.get_text().strip() for option, entry in data['inputs'].items()},
                'dropdowns': {key: combo.get_active_text() for key, combo in data['dropdowns'].items() if combo.get_active_text()},
                'sliders': {option: scale.get_value() for option, scale in data['sliders'].items()}
            }
        
        try:
            with open(SETTINGS_FILE, 'w') as f:
                json.dump(settings, f, indent=4)
            logging.info("Settings saved successfully")
            dialog = Gtk.MessageDialog(
                transient_for=self,
                flags=0,
                message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.OK,
                text="Settings saved successfully."
            )
            dialog.run()
            dialog.destroy()
        except Exception as e:
            logging.error(f"Error saving settings: {e}")
            dialog = Gtk.MessageDialog(
                transient_for=self,
                flags=0,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text=f"Error saving settings: {str(e)}"
            )
            dialog.run()
            dialog.destroy()

    def on_reset_clicked(self, button):
        # Reset general tab
        for toggle in self.toggles.values():
            toggle.set_active(False)
        for entry in self.inputs.values():
            entry.set_text("")
        for combo in self.general_dropdowns.values():
            if combo.get_model().iter_n_children(None) > 0:
                combo.set_active(0)
        self.dxlevel_toggle.set_active(False)
        
        # Reset other tabs
        for tab_name, data in self.tab_data.items():
            data['enable_toggle'].set_active(False)
            for toggle in data['toggles'].values():
                toggle.set_active(False)
            for entry in data['inputs'].values():
                entry.set_text("")
            for combo in data['dropdowns'].values():
                if combo.get_model().iter_n_children(None) > 0:
                    combo.set_active(0)
            for scale in data['sliders'].values():
                scale.set_value(0.0)
        
        self.update_summary()
        logging.info("All settings reset")

    def on_launch_clicked(self, button):
        command_parts = []
        env_vars = []
        
        # General tab toggles
        for flag, toggle in self.toggles.items():
            if toggle.get_active():
                command_parts.append(flag)
        
        # General tab inputs
        for flag, entry in self.inputs.items():
            value = entry.get_text().strip()
            if value:
                command_parts.append(f"{flag} {value}")
        
        # General tab dropdowns (dxlevel)
        if self.dxlevel_toggle.get_active():
            for flag, combo in self.general_dropdowns.items():
                value = combo.get_active_text()
                if value:
                    command_parts.append(f"{flag} {value}")
        
        # Other tabs
        for tab_name, data in self.tab_data.items():
            if data['enable_toggle'].get_active():
                config = TAB_CONFIGS[tab_name]
                
                # Command prefix
                if "command_prefix" in config:
                    command_parts.insert(0, config["command_prefix"])
                
                # Toggles
                for option, toggle in data['toggles'].items():
                    if toggle.get_active():
                        if option.startswith('-'):
                            command_parts.append(option)
                        else:
                            env_vars.append(f"{option}=1")
                
                # Inputs
                for option, entry in data['inputs'].items():
                    value = entry.get_text().strip()
                    if value:
                        env_vars.append(f"{option}={value}")
                
                # Dropdowns
                for key, combo in data['dropdowns'].items():
                    value = combo.get_active_text()
                    if value:
                        env_vars.append(f"{key}={value}")
                
                # Sliders
                for option, scale in data['sliders'].items():
                    value = scale.get_value()
                    if value != 0:
                        env_vars.append(f"{option}={value:.2f}")
                
                # Command suffix
                if "command_suffix" in config:
                    command_parts.append(config["command_suffix"])
        
        # Build final command
        command = ""
        if env_vars:
            command += " ".join(env_vars) + " "
        command += " ".join(command_parts)
        if command:
            command += " %command%"
        
        self.generated_command_entry.set_text(command.strip())
        logging.info(f"Generated command: {command}")
        self.update_summary()

    def on_destroy(self, widget):
        self.on_save_clicked(None)
        Gtk.main_quit()

    def on_detect_clicked(self, button):
        command = self.detect_entry.get_text().strip()
        if not command:
            return
        
        try:
            # Reset all settings before parsing
            self.on_reset_clicked(None)
            
            # Split command, preserving quoted strings
            parts = shlex.split(command.replace('%command%', ''))
            env_vars = {}
            flags = []
            current_env = []
            
            for part in parts:
                if '=' in part and not part.startswith('-'):
                    # Handle environment variables
                    key, value = part.split('=', 1)
                    env_vars[key] = value
                elif part in TAB_CONFIGS.get("Gamescope", {}).get("command_suffix", ""):
                    continue
                else:
                    # Handle flags and command prefixes
                    flags.append(part)
            
            # Process environment variables
            for key, value in env_vars.items():
                if key in self.tab_toggle_mappings:
                    tab_name, option = self.tab_toggle_mappings[key]
                    if value == "1":
                        self.tab_data[tab_name]['toggles'][option].set_active(True)
                        self.tab_data[tab_name]['enable_toggle'].set_active(True)
                elif key in self.tab_input_mappings:
                    tab_name, option = self.tab_input_mappings[key]
                    self.tab_data[tab_name]['inputs'][option].set_text(value)
                    self.tab_data[tab_name]['enable_toggle'].set_active(True)
                elif key in self.tab_dropdown_mappings:
                    tab_name, key = self.tab_dropdown_mappings[key]
                    combo = self.tab_data[tab_name]['dropdowns'][key]
                    for i in range(combo.get_model().iter_n_children(None)):
                        if combo.get_model()[i][0] == value:
                            combo.set_active(i)
                            self.tab_data[tab_name]['enable_toggle'].set_active(True)
                            break
                elif key in self.tab_slider_mappings:
                    tab_name, option = self.tab_slider_mappings[key]
                    try:
                        self.tab_data[tab_name]['sliders'][option].set_value(float(value))
                        self.tab_data[tab_name]['enable_toggle'].set_active(True)
                    except ValueError:
                        pass
            
            # Process flags
            for flag in flags:
                if flag in self.toggle_mappings:
                    self.toggles[flag].set_active(True)
                elif flag in self.input_mappings:
                    # Handle inputs that require a value
                    try:
                        idx = flags.index(flag)
                        if idx + 1 < len(flags):
                            self.inputs[flag].set_text(flags[idx + 1])
                    except ValueError:
                        pass
                elif flag == "-dxlevel":
                    self.dxlevel_toggle.set_active(True)
                    try:
                        idx = flags.index(flag)
                        if idx + 1 < len(flags):
                            value = flags[idx + 1]
                            combo = self.general_dropdowns["-dxlevel"]
                            for i in range(combo.get_model().iter_n_children(None)):
                                if combo.get_model()[i][0] == value:
                                    combo.set_active(i)
                                    break
                    except ValueError:
                        pass
                else:
                    # Check for command prefixes
                    for tab_name, config in TAB_CONFIGS.items():
                        if "command_prefix" in config and flag == config["command_prefix"]:
                            self.tab_data[tab_name]['enable_toggle'].set_active(True)
            
            self.update_summary()
            logging.info(f"Parsed command: {command}")
        except Exception as e:
            logging.error(f"Error parsing command: {e}")
            dialog = Gtk.MessageDialog(
                transient_for=self,
                flags=0,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text=f"Error parsing command: {str(e)}"
            )
            dialog.run()
            dialog.destroy()

# SECTION: MAIN
if __name__ == "__main__":
    try:
        win = SteamLauncherWindow()
        win.show_all()
        Gtk.main()
    except Exception as e:
        logging.error(f"Application error: {e}")
        print(f"Application error: {e}")
