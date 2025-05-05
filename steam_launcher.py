import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk
import subprocess
import os
import json
import pexpect

# Configuration for all tabs
TAB_CONFIGS = {
    "Wine": {
        "enable_label": "Enable Wine",
        "enable_tooltip": "Enable Wine environment settings",
        "toggles": [
            ("WINEESYNC", "Enable explicit synchronization for Wine"),
            ("WINEFSYNC", "Enable frame synchronization for Wine"),
            ("WINELOADERDEBUG", "Enable Wine loader debugging"),
            ("WINELOADERNOEXEC", "Disable Wine loader execution"),
        ],
        "inputs": [
            ("WINEPREFIX", "Path to Wine prefix", "e.g., /path/to/prefix"),
            ("WINEARCH", "Set Wine architecture", "e.g., win32"),
            ("WINEDLLOVERRIDES", "Override specific DLLs", "e.g., dinput8=n,b"),
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
            ("CONFIG", "Path to custom MangoHud config file", "e.g., /path/to/config"),
            ("FPSAVERAGE", "Average FPS over frames", "e.g., 100"),
            ("FPS_LIMIT", "Set frame rate limit", "e.g., 60"),
            ("FPS_THRESHOLD", "Set FPS alert threshold", "e.g., 30"),
            ("COLOR", "Set overlay color", "e.g., #FF0000"),
            ("XOFFSET", "Adjust X offset of overlay", "e.g., 10"),
            ("YOFFSET", "Adjust Y offset of overlay", "e.g., 10"),
        ],
        "dropdowns": {
            "ALIGN": {
                "label": "ALIGN:",
                "options": ["bottom", "top", "left", "right"],
                "tooltip": "Align the MangoHud overlay",
                "default": "bottom",
            }
        },
        "software_requirement": "mangohud",
    },
    "vkBasalt": {
        "enable_label": "Enable vkBasalt",
        "enable_tooltip": "Enable vkBasalt effects",
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
            ("CONFIG", "Path to custom vkBasalt config file", "e.g., /path/to/config"),
            ("SHADERS", "Path to custom shaders", "e.g., /path/to/shaders"),
        ],
        "sliders": [
            ("SHARPEN_STRENGTH", "Sharpening strength", 0.0, 1.0),
            ("FXAA_STRENGTH", "FXAA strength", 0.0, 1.0),
            ("SMAA_STRENGTH", "SMAA strength", 0.0, 1.0),
            ("LUT_STRENGTH", "LUT strength", 0.0, 1.0),
            ("TONEMAP_STRENGTH", "Tonemapping strength", 0.0, 1.0),
            ("HDR_STRENGTH", "HDR strength", 0.0, 1.0),
            ("DITHER_STRENGTH", "Dithering strength", 0.0, 1.0),
            ("LUMINANCE_STRENGTH", "Luminance strength", 0.0, 1.0),
            ("COLOR_STRENGTH", "Color strength", 0.0, 1.0),
            ("BLOOM_STRENGTH", "Bloom strength", 0.0, 1.0),
            ("SSAO_STRENGTH", "SSAO strength", 0.0, 1.0),
            ("VIGNETTE_STRENGTH", "Vignette strength", 0.0, 1.0),
            ("CHROMATIC_ABER_STRENGTH", "Chromatic aberration strength", 0.0, 1.0),
            ("MOTION_BLUR_STRENGTH", "Motion blur strength", 0.0, 1.0),
            ("SHARPEN_RADIUS", "Sharpening radius", 0.0, 10.0),
            ("FXAA_RADIUS", "FXAA radius", 0.0, 10.0),
            ("SMAA_RADIUS", "SMAA radius", 0.0, 10.0),
            ("LUT_RADIUS", "LUT radius", 0.0, 10.0),
            ("TONEMAP_RADIUS", "Tonemapping radius", 0.0, 10.0),
            ("HDR_RADIUS", "HDR radius", 0.0, 10.0),
            ("DITHER_RADIUS", "Dithering radius", 0.0, 10.0),
            ("LUMINANCE_RADIUS", "Luminance radius", 0.0, 10.0),
            ("COLOR_RADIUS", "Color radius", 0.0, 10.0),
            ("BLOOM_RADIUS", "Bloom radius", 0.0, 10.0),
            ("SSAO_RADIUS", "SSAO radius", 0.0, 10.0),
            ("VIGNETTE_RADIUS", "Vignette radius", 0.0, 10.0),
            ("CHROMATIC_ABER_RADIUS", "Chromatic aberration radius", 0.0, 10.0),
            ("MOTION_BLUR_RADIUS", "Motion blur radius", 0.0, 10.0),
        ],
        "software_requirement": "vkbasalt",
    },
    "GameMode": {
        "enable_label": "Enable GameMode",
        "enable_tooltip": "Enable GameMode optimization",
        "toggles": [
            ("GAME_MODE", "Enable GameMode optimization"),
        ],
        "software_requirement": "gamemoded",
    },
    "Gamescope": {
        "enable_label": "Enable Gamescope",
        "enable_tooltip": "Enable Gamescope",
        "toggles": [
            ("f", "Force full screen mode"),
            ("b", "Enable borderless window mode"),
            ("n", "Disable the gamescope compositor"),
            ("c", "Enable VSync"),
            ("q", "Enable quiet mode"),
        ],
        "inputs": [
            ("W", "Set window width", "e.g., 1920"),
            ("H", "Set window height", "e.g., 1080"),
            ("r", "Set refresh rate", "e.g., 60"),
            ("s", "Set game width", "e.g., 1920"),
            ("t", "Set game height", "e.g., 1080"),
            ("d", "Specify display", "e.g., :0"),
            ("p", "Specify port", "e.g., 8080"),
            ("x", "Set X offset", "e.g., 10"),
            ("y", "Set Y offset", "e.g., 10"),
        ],
        "dropdowns": {
            "inputs": {
                "label": "Inputs:",
                "options": ["None", "Keyboard", "Mouse", "Gamepad", "All"],
                "tooltip": "Enable specific input types",
                "default": "None",
            }
        },
        "software_requirement": "gamescope",
    },
    "DXVK": {
        "enable_label": "Enable DXVK",
        "enable_tooltip": "Enable DXVK translation",
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
            ("HUD", "Specify HUD info", "e.g., fps,version"),
            ("STATE_CACHE_PATH", "Path to state cache", "e.g., /path/to/cache"),
            ("SHADER_CACHE_PATH", "Path to shader cache", "e.g., /path/to/cache"),
            ("LOG_LEVEL", "Set log level", "e.g., info"),
            ("MAX_FRAME_LATENCY", "Set max frame latency", "e.g., 2"),
            ("MAX_FRAMES_IN_FLIGHT", "Set max frames in flight", "e.g., 3"),
            ("FORCE_FEATURE_LEVEL", "Force feature level", "e.g., 11_0"),
            ("SHADER_MODEL", "Specify shader model", "e.g., 5"),
            ("MAX_SHADER_RESOURCE_GROUPS", "Set max shader resource groups", "e.g., 16"),
        ],
        "software_requirement": "dxvk",
    },
    "ProtonCustom": {
        "enable_label": "Enable ProtonCustom",
        "enable_tooltip": "Enable custom Proton settings",
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
        ],
        "inputs": [
            ("LOG_FILE", "Path to log file", "e.g., /path/to/log"),
            ("USE_WINEDEBUG", "Set Wine debug level", "e.g., +all"),
        ],
    },
    "MesaOverlay": {
        "enable_label": "Enable MesaOverlay",
        "enable_tooltip": "Enable Mesa overlay",
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
            ("CONFIG", "Path to custom Mesa overlay config file", "e.g., /path/to/config"),
            ("XOFFSET", "Adjust X offset of overlay", "e.g., 10"),
            ("YOFFSET", "Adjust Y offset of overlay", "e.g., 10"),
            ("COLOR", "Set overlay color", "e.g., #FF0000"),
            ("FONT_SIZE", "Set font size", "e.g., 12"),
            ("LOG_FILE", "Path to log file", "e.g., /path/to/log"),
            ("Transparency", "Set transparency level", "e.g., 0.5"),
        ],
        "dropdowns": {
            "ALIGN": {
                "label": "ALIGN:",
                "options": ["top", "bottom", "left", "right"],
                "tooltip": "Align the Mesa overlay",
                "default": "top",
            }
        },
    },
}

GENERAL_OPTIONS = [
    ("NoHLTV", "Disables HLTV functionality"),
    ("NoVid", "Skips the intro video"),
    ("Console", "Opens the game console"),
    ("Steam", "Forces Steam integration"),
    ("NoSteamController", "Disables Steam controller input"),
    ("NoJoy", "Disables joystick input"),
    ("NoSound", "Disables sound"),
    ("NoVSync", "Disables vertical sync"),
    ("Fullscreen", "Forces fullscreen mode"),
    ("Window", "Forces windowed mode"),
    ("NoBorder", "Removes window borders in windowed mode"),
    ("SafeMode", "Starts the game in safe mode"),
    ("High", "Sets high priority"),
    ("Low", "Sets low priority"),
    ("Mid", "Sets medium priority"),
    ("NoBenchmark", "Disables benchmarking"),
    ("NoSplash", "Disables the splash screen"),
    ("NoLogo", "Disables the logo screen"),
    ("NoIPX", "Disables IPX networking"),
    ("NoIP", "Disables IP networking"),
    ("NoVoice", "Disables voice chat"),
    ("NoCloud", "Disables Steam Cloud sync"),
    ("NoHTTP", "Disables HTTP networking"),
    ("NoSteamUpdate", "Disables Steam updates"),
    ("NoSoundInit", "Disables sound initialization"),
    ("NoCrashDialog", "Disables the crash dialog"),
    ("NoCrashDump", "Disables crash dumps"),
    ("NoAsserts", "Disables assertions"),
    ("NoHomeDirFixup", "Disables home directory fixup"),
    ("NoAutoCloud", "Disables automatic Steam Cloud sync"),
    ("NoAutoJoystick", "Disables automatic joystick detection"),
    ("NoMiniDumps", "Disables mini dumps"),
    ("NoCache", "Disables caching"),
    ("NoAsync", "Disables asynchronous operations"),
    ("NoHW", "Disables hardware rendering"),
    ("Soft", "Forces software rendering"),
    ("NoGrab", "Disables mouse grabbing"),
    ("NoGamepad", "Disables gamepad input"),
    ("NoXInput", "Disables XInput"),
    ("NoGPUWatch", "Disables GPU watch"),
    ("NoCursor", "Disables cursor"),
    ("NoHWCursor", "Disables hardware cursor"),
    ("NoGL", "Disables OpenGL"),
    ("NoD3D9", "Disables Direct3D 9"),
    ("NoD3D11", "Disables Direct3D 11"),
    ("NoMouse", "Disables mouse input"),
    ("NoKB", "Disables keyboard input"),
    ("NoLock", "Disables locking"),
    ("NoCommand", "Disables command execution"),
    ("NoLog", "Disables logging"),
    ("NoProfile", "Disables user profile loading"),
    ("NoRestart", "Disables automatic restart"),
    ("NoUpdate", "Disables automatic updates"),
    ("NoShip", "Disables ship mode"),
    ("NoShaderCache", "Disables shader cache"),
    ("NoShaderCompile", "Disables shader compilation"),
    ("NoShaderLoad", "Disables shader loading"),
    ("NoShaderPrecompile", "Disables shader precompilation"),
    ("NoShaderPrecache", "Disables shader precache"),
    ("NoShaderPreload", "Disables shader preload"),
    ("NoShaderPrewarm", "Disables shader prewarm"),
    ("NoShaderPreoptimize", "Disables shader preoptimize"),
    ("NoShaderPrecompileAll", "Disables shader precompile for all"),
    ("NoShaderPrecacheAll", "Disables shader precache for all"),
    ("NoShaderPreloadAll", "Disables shader preload for all"),
    ("NoShaderPrewarmAll", "Disables shader prewarm for all"),
    ("NoShaderPreoptimizeAll", "Disables shader preoptimize for all"),
]

GENERAL_INPUTS = [
    ("Width", "Sets the window width", "e.g., 1920"),
    ("Height", "Sets the window height", "e.g., 1080"),
    ("DXLevel", "Sets the DirectX level", "e.g., 95"),
    ("Particles", "Sets the particle effect quality", "e.g., 1"),
    ("Refresh", "Sets the refresh rate", "e.g., 60"),
]

DX_LEVEL_PRESETS = ["9.0", "9.0c", "10.0", "10.1", "11.0"]

class SteamLauncherWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Steam Game Launcher")
        self.set_border_width(10)
        self.set_default_size(1280, 720)

        # Main vertical box
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add(vbox)

        # Header label
        header = Gtk.Label(label="Steam Launch Options\nCustomize your game launch command with tabs for overlays and enhancements")
        header.set_justify(Gtk.Justification.CENTER)
        vbox.pack_start(header, False, False, 0)

        # Notebook for tabs
        self.notebook = Gtk.Notebook()
        vbox.pack_start(self.notebook, True, True, 0)

        # Tab 1: General Steam Options
        self.toggles = {}
        self.setup_general_tab(self.notebook)

        # Track which tabs have been checked for software
        self.software_checked = {tab: False for tab in TAB_CONFIGS if "software_requirement" in TAB_CONFIGS[tab]}

        # Setup tabs for overlay/enhancement tools
        self.tab_data = {}
        for tab_name in TAB_CONFIGS:
            self.setup_tab(self.notebook, tab_name)

        # Connect the switch-page signal to check software when a tab is selected
        self.notebook.connect("switch-page", self.on_tab_switched)

        # Load saved settings
        self.load_settings()

        # Buttons at the bottom
        hbox_buttons = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        vbox.pack_start(hbox_buttons, False, False, 0)

        save_button = Gtk.Button(label="Save Settings")
        save_button.connect("clicked", self.on_save_clicked)
        hbox_buttons.pack_start(save_button, True, True, 0)

        cancel_button = Gtk.Button(label="Cancel")
        cancel_button.connect("clicked", self.on_cancel_clicked)
        hbox_buttons.pack_start(cancel_button, True, True, 0)

        launch_button = Gtk.Button(label="Generate Launch Command")
        launch_button.connect("clicked", self.on_launch_clicked)
        hbox_buttons.pack_start(launch_button, True, True, 0)

        # Styling for better readability, including tooltip fix
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
            color: #ffffff;  /* Fixed tooltip text color to be visible */
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

    def check_software(self, software):
        try:
            subprocess.run(["which", software.lower()], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True
        except subprocess.CalledProcessError:
            return False

    def prompt_install(self, software):
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.QUESTION,
            text=f"{software} is required but not found. Would you like to install it?"
        )
        dialog.add_buttons("Yes", Gtk.ResponseType.YES, "No", Gtk.ResponseType.NO)
        response = dialog.run()
        dialog.destroy()
        if response == Gtk.ResponseType.YES:
            password_dialog = Gtk.Dialog(
                title="Enter Password",
                transient_for=self,
                flags=0
            )
            password_dialog.add_buttons("OK", Gtk.ResponseType.OK, "Cancel", Gtk.ResponseType.CANCEL)
            password_dialog.set_default_size(300, 100)
            vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
            password_dialog.get_content_area().add(vbox)
            label = Gtk.Label(label="Enter your password to install:")
            vbox.pack_start(label, False, False, 0)
            password_entry = Gtk.Entry()
            password_entry.set_visibility(False)
            vbox.pack_start(password_entry, False, False, 0)
            password_dialog.show_all()
            response = password_dialog.run()
            password = password_entry.get_text() if response == Gtk.ResponseType.OK else ""
            password_dialog.destroy()
            if password:
                try:
                    cmd = ["sudo", "apt", "install", "-y", software.lower()]
                    child = pexpect.spawn(" ".join(cmd))
                    i = child.expect(["[sudo] password for " + os.getlogin() + ":", pexpect.EOF, pexpect.TIMEOUT], timeout=5)
                    if i == 0:
                        child.sendline(password)
                        child.expect(pexpect.EOF)
                        output = child.before.decode()
                        if child.exitstatus == 0:
                            dialog = Gtk.MessageDialog(
                                transient_for=self,
                                flags=0,
                                message_type=Gtk.MessageType.INFO,
                                buttons=Gtk.ButtonsType.OK,
                                text=f"{software} installed successfully!"
                            )
                            dialog.run()
                            dialog.destroy()
                        else:
                            dialog = Gtk.MessageDialog(
                                transient_for=self,
                                flags=0,
                                message_type=Gtk.MessageType.ERROR,
                                buttons=Gtk.ButtonsType.OK,
                                text=f"Failed to install {software}: {output}"
                            )
                            dialog.run()
                            dialog.destroy()
                    else:
                        dialog = Gtk.MessageDialog(
                            transient_for=self,
                            flags=0,
                            message_type=Gtk.MessageType.ERROR,
                            buttons=Gtk.ButtonsType.OK,
                            text=f"Could not prompt for password or installation timed out."
                        )
                        dialog.run()
                        dialog.destroy()
                except Exception as e:
                    dialog = Gtk.MessageDialog(
                        transient_for=self,
                        flags=0,
                        message_type=Gtk.MessageType.ERROR,
                        buttons=Gtk.ButtonsType.OK,
                        text=f"Error during installation: {str(e)}"
                    )
                    dialog.run()
                    dialog.destroy()
            return response == Gtk.ResponseType.OK
        return False

    def on_tab_switched(self, notebook, page, page_num):
        # Adjust for General tab at index 0
        tab_index = page_num - 1
        tab_names = list(TAB_CONFIGS.keys())
        if tab_index >= 0 and tab_index < len(tab_names):
            tab_name = tab_names[tab_index]
            if tab_name in self.software_checked and not self.software_checked[tab_name]:
                self.software_checked[tab_name] = True
                config = TAB_CONFIGS[tab_name]
                if "software_requirement" in config and not self.check_software(config["software_requirement"]):
                    if self.prompt_install(tab_name):
                        pass
                    else:
                        label = Gtk.Label(label=f"{tab_name} is not installed. Please install it to use this tab.")
                        page.get_children()[0].pack_start(label, True, True, 0)
                        page.show_all()

    def setup_general_tab(self, notebook):
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)

        grid = Gtk.Grid()
        grid.set_column_spacing(20)
        grid.set_row_spacing(10)
        scrolled_window.add(grid)

        for i, (option, tooltip) in enumerate(GENERAL_OPTIONS):
            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            label = Gtk.Label(label=option)
            label.set_halign(Gtk.Align.START)
            toggle = Gtk.Switch()
            toggle.set_halign(Gtk.Align.END)
            toggle.set_tooltip_text(tooltip)
            hbox.pack_start(label, True, True, 0)
            hbox.pack_end(toggle, False, False, 0)
            self.toggles[option] = toggle
            col = i % 4
            row = i // 4
            grid.attach(hbox, col, row, 1, 1)

        self.inputs = {}
        input_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        for option, tooltip, placeholder in GENERAL_INPUTS:
            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
            label = Gtk.Label(label=f"{option}:")
            entry = Gtk.Entry()
            entry.set_placeholder_text(placeholder)
            entry.set_tooltip_text(tooltip)
            if option == "DXLevel":
                button = Gtk.Button(label="Presets")
                button.connect("clicked", self.on_dxlevel_preset_clicked, entry)
                hbox.pack_start(label, False, False, 0)
                hbox.pack_start(entry, True, True, 0)
                hbox.pack_start(button, False, False, 0)
            else:
                if "path" in tooltip.lower():
                    button = Gtk.Button(label="Browse")
                    button.connect("clicked", self.on_path_browse_clicked, entry)
                    hbox.pack_start(label, False, False, 0)
                    hbox.pack_start(entry, True, True, 0)
                    hbox.pack_start(button, False, False, 0)
                else:
                    hbox.pack_start(label, False, False, 0)
                    hbox.pack_start(entry, True, True, 0)
            input_box.pack_start(hbox, False, False, 0)
            self.inputs[option] = entry

        hbox_args = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        args_label = Gtk.Label(label="Custom Arguments:")
        self.args_entry = Gtk.Entry()
        self.args_entry.set_placeholder_text("e.g., -customoption value")
        hbox_args.pack_start(args_label, False, False, 0)
        hbox_args.pack_start(self.args_entry, True, True, 0)

        general_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        general_vbox.pack_start(scrolled_window, True, True, 0)
        general_vbox.pack_start(input_box, False, False, 0)
        general_vbox.pack_start(hbox_args, False, False, 0)

        notebook.append_page(general_vbox, Gtk.Label(label="General"))

    def setup_tab(self, notebook, tab_name):
        config = TAB_CONFIGS[tab_name]
        self.tab_data[tab_name] = {
            "toggles": {},
            "inputs": {},
            "dropdowns": {},
            "sliders": {},
            "slider_toggles": {},
        }

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

        # Master toggle with prominent styling
        hbox_enable = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        hbox_enable.set_margin_top(10)
        hbox_enable.set_margin_bottom(10)
        label = Gtk.Label(label=config["enable_label"])
        label.get_style_context().add_class("enable-label")
        enable_toggle = Gtk.Switch()
        enable_toggle.set_halign(Gtk.Align.END)
        enable_toggle.set_tooltip_text(config["enable_tooltip"])
        hbox_enable.pack_start(label, True, True, 0)
        hbox_enable.pack_end(enable_toggle, False, False, 0)
        vbox.pack_start(hbox_enable, False, False, 0)
        self.tab_data[tab_name]["enable_toggle"] = enable_toggle

        # Separator to make the enable toggle more distinct
        separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        vbox.pack_start(separator, False, False, 0)

        # Toggles
        if "toggles" in config:
            grid = Gtk.Grid()
            grid.set_column_spacing(20)
            grid.set_row_spacing(10)
            if tab_name == "vkBasalt":
                grid.get_style_context().add_class("vkbasalt-grid")
            scrolled_window = Gtk.ScrolledWindow()
            scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
            scrolled_window.add(grid)

            for i, (option, tooltip) in enumerate(config["toggles"]):
                hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
                label_text = option.replace(f"{tab_name.upper()}_", "") if tab_name != "Gamescope" else tooltip
                label = Gtk.Label(label=label_text)
                label.set_halign(Gtk.Align.START)
                toggle = Gtk.Switch()
                toggle.set_halign(Gtk.Align.END)
                toggle.set_tooltip_text(tooltip)
                hbox.pack_start(label, True, True, 0)
                hbox.pack_end(toggle, False, False, 0)
                self.tab_data[tab_name]["toggles"][option] = toggle
                col = i % 4
                row = i // 4
                grid.attach(hbox, col, row, 1, 1)

            vbox.pack_start(scrolled_window, True, True, 0)

        # Inputs
        if "inputs" in config:
            input_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
            for option, tooltip, placeholder in config["inputs"]:
                hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
                label = Gtk.Label(label=f"{option}:")
                entry = Gtk.Entry()
                entry.set_placeholder_text(placeholder)
                entry.set_tooltip_text(tooltip)
                if "path" in tooltip.lower():
                    button = Gtk.Button(label="Browse")
                    button.connect("clicked", self.on_path_browse_clicked, entry)
                    hbox.pack_start(label, False, False, 0)
                    hbox.pack_start(entry, True, True, 0)
                    hbox.pack_start(button, False, False, 0)
                else:
                    hbox.pack_start(label, False, False, 0)
                    hbox.pack_start(entry, True, True, 0)
                input_box.pack_start(hbox, False, False, 0)
                self.tab_data[tab_name]["inputs"][option] = entry
            vbox.pack_start(input_box, False, False, 0)

        # Dropdowns
        if "dropdowns" in config:
            for key, dropdown_config in config["dropdowns"].items():
                hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
                label = Gtk.Label(label=dropdown_config["label"])
                combo = Gtk.ComboBoxText()
                for option in dropdown_config["options"]:
                    combo.append_text(option)
                default_index = dropdown_config["options"].index(dropdown_config["default"]) if "default" in dropdown_config else 0
                combo.set_active(default_index)
                combo.set_tooltip_text(dropdown_config["tooltip"])
                hbox.pack_start(label, False, False, 0)
                hbox.pack_start(combo, True, True, 0)
                self.tab_data[tab_name]["dropdowns"][key] = combo
                vbox.pack_start(hbox, False, False, 0)

        # Sliders (for vkBasalt)
        if "sliders" in config and tab_name == "vkBasalt":
            # Create a grid for sliders
            slider_grid = Gtk.Grid()
            slider_grid.set_column_spacing(20)
            slider_grid.set_row_spacing(10)
            scrolled_window = Gtk.ScrolledWindow()
            scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
            scrolled_window.add(slider_grid)

            for i, (option, tooltip, min_val, max_val) in enumerate(config["sliders"]):
                hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
                toggle = Gtk.Switch()
                toggle.set_tooltip_text(f"Enable {tooltip.lower()}")
                toggle.connect("state-set", self.on_slider_toggle_changed, tab_name, option)
                label = Gtk.Label(label=f"{option}:")
                revealer = Gtk.Revealer()
                adjustment = Gtk.Adjustment(value=0.5 if max_val <= 1.0 else 5.0, lower=min_val, upper=max_val, step_increment=0.1)
                slider = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, min_val, max_val, 0.1)
                slider.set_adjustment(adjustment)
                slider.set_digits(1)
                slider.set_size_request(200, -1)  # Set a reasonable width for sliders
                slider.set_tooltip_text(tooltip)
                revealer.add(slider)
                hbox.pack_start(label, False, False, 0)
                hbox.pack_start(toggle, False, False, 0)
                hbox.pack_start(revealer, True, True, 0)
                col = i % 2  # Arrange in 2 columns
                row = i // 2
                slider_grid.attach(hbox, col, row, 1, 1)
                self.tab_data[tab_name]["slider_toggles"][option] = toggle
                self.tab_data[tab_name]["sliders"][option] = (revealer, slider)

            vbox.pack_start(scrolled_window, True, True, 0)

        notebook.append_page(vbox, Gtk.Label(label=tab_name))

    def on_slider_toggle_changed(self, switch, state, tab_name, option):
        revealer, _ = self.tab_data[tab_name]["sliders"][option]
        revealer.set_reveal_child(state)

    def save_settings(self):
        settings = {
            "general": {
                "toggles": {key: toggle.get_active() for key, toggle in self.toggles.items()},
                "inputs": {key: entry.get_text() for key, entry in self.inputs.items()},
                "args_entry": self.args_entry.get_text(),
            },
            "tabs": {}
        }

        for tab_name, data in self.tab_data.items():
            tab_settings = {
                "enable_toggle": data["enable_toggle"].get_active(),
                "toggles": {key: toggle.get_active() for key, toggle in data["toggles"].items()},
                "inputs": {key: entry.get_text() for key, entry in data["inputs"].items()},
                "dropdowns": {key: combo.get_active_text() for key, combo in data["dropdowns"].items()},
                "sliders": {},
                "slider_toggles": {key: toggle.get_active() for key, toggle in data["slider_toggles"].items()},
            }
            for key, (revealer, slider) in data["sliders"].items():
                tab_settings["sliders"][key] = slider.get_value()
            settings["tabs"][tab_name] = tab_settings

        with open("settings.json", "w") as f:
            json.dump(settings, f, indent=4)

    def load_settings(self):
        if not os.path.exists("settings.json"):
            return

        with open("settings.json", "r") as f:
            settings = json.load(f)

        # Load General tab settings
        general_settings = settings.get("general", {})
        for key, active in general_settings.get("toggles", {}).items():
            if key in self.toggles:
                self.toggles[key].set_active(active)
        for key, value in general_settings.get("inputs", {}).items():
            if key in self.inputs:
                self.inputs[key].set_text(value)
        self.args_entry.set_text(general_settings.get("args_entry", ""))

        # Load tab settings
        for tab_name, tab_settings in settings.get("tabs", {}).items():
            if tab_name not in self.tab_data:
                continue
            data = self.tab_data[tab_name]
            data["enable_toggle"].set_active(tab_settings.get("enable_toggle", False))
            for key, active in tab_settings.get("toggles", {}).items():
                if key in data["toggles"]:
                    data["toggles"][key].set_active(active)
            for key, value in tab_settings.get("inputs", {}).items():
                if key in data["inputs"]:
                    data["inputs"][key].set_text(value)
            for key, value in tab_settings.get("dropdowns", {}).items():
                if key in data["dropdowns"]:
                    combo = data["dropdowns"][key]
                    for i, option in enumerate(combo.get_model()):
                        if option[0] == value:
                            combo.set_active(i)
                            break
            for key, value in tab_settings.get("sliders", {}).items():
                if key in data["sliders"]:
                    _, slider = data["sliders"][key]
                    slider.set_value(value)
            for key, active in tab_settings.get("slider_toggles", {}).items():
                if key in data["slider_toggles"]:
                    toggle = data["slider_toggles"][key]
                    toggle.set_active(active)
                    revealer, _ = data["sliders"][key]
                    revealer.set_reveal_child(active)

    def on_save_clicked(self, button):
        self.save_settings()
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="Settings saved successfully!"
        )
        dialog.run()
        dialog.destroy()

    def on_destroy(self, widget):
        self.save_settings()
        Gtk.main_quit()

    def on_dxlevel_preset_clicked(self, button, entry):
        menu = Gtk.Menu()
        for preset in DX_LEVEL_PRESETS:
            item = Gtk.MenuItem(label=preset)
            item.connect("activate", self.on_dxlevel_preset_selected, entry, preset)
            menu.append(item)
        menu.show_all()
        menu.popup(None, None, None, None, button.get_pointer()[1], Gtk.get_current_event_time())

    def on_dxlevel_preset_selected(self, menuitem, entry, preset):
        entry.set_text(preset)

    def on_path_browse_clicked(self, button, entry):
        dialog = Gtk.FileChooserDialog(
            title="Select a File or Directory",
            transient_for=self,
            action=Gtk.FileChooserAction.SELECT_FOLDER if entry.get_placeholder_text().startswith("e.g., /path") else Gtk.FileChooserAction.OPEN,
            buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
        )
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            entry.set_text(dialog.get_filename())
        dialog.destroy()

    def on_launch_clicked(self, button):
        command = []

        # General Steam options
        toggle_mapping = {
            "NoHLTV": "-nohltv",
            "NoVid": "-novid",
            "Console": "-console",
            "Steam": "-steam",
            "NoSteamController": "-nosteamcontroller",
            "NoJoy": "-nojoy",
            "NoSound": "-nosound",
            "NoVSync": "-novsync",
            "Fullscreen": "-fullscreen",
            "Window": "-window",
            "NoBorder": "-noborder",
            "SafeMode": "-safe_mode",
            "High": "-high",
            "Low": "-low",
            "Mid": "-mid",
            "NoBenchmark": "-nobenchmark",
            "NoSplash": "-nosplash",
            "NoLogo": "-nologo",
            "NoIPX": "-noipx",
            "NoIP": "-noip",
            "NoVoice": "-novoice",
            "NoCloud": "-nocloud",
            "NoHTTP": "-nohttp",
            "NoSteamUpdate": "-nosteamupdate",
            "NoSoundInit": "-nosoundinit",
            "NoCrashDialog": "-nocrashdialog",
            "NoCrashDump": "-nocrashdump",
            "NoAsserts": "-noasserts",
            "NoHomeDirFixup": "-nohomedirfixup",
            "NoAutoCloud": "-noautocloud",
            "NoAutoJoystick": "-noautojoystick",
            "NoMiniDumps": "-nominidumps",
            "NoCache": "-nocache",
            "NoAsync": "-noasync",
            "NoHW": "-nohw",
            "Soft": "-soft",
            "NoGrab": "-nograb",
            "NoGamepad": "-nogamepad",
            "NoXInput": "-noxinput",
            "NoGPUWatch": "-nogpuwatch",
            "NoCursor": "-nocursor",
            "NoHWCursor": "-nohwcursor",
            "NoGL": "-nogl",
            "NoD3D9": "-nod3d9",
            "NoD3D11": "-nod3d11",
            "NoMouse": "-nomouse",
            "NoKB": "-nokb",
            "NoLock": "-nolock",
            "NoCommand": "-nocommand",
            "NoLog": "-nolog",
            "NoProfile": "-noprofile",
            "NoRestart": "-norestart",
            "NoUpdate": "-noupdate",
            "NoShip": "-noship",
            "NoShaderCache": "-noshadercache",
            "NoShaderCompile": "-noshadercompile",
            "NoShaderLoad": "-noshaderload",
            "NoShaderPrecompile": "-noshaderprecompile",
            "NoShaderPrecache": "-noshaderprecache",
            "NoShaderPreload": "-noshaderpreload",
            "NoShaderPrewarm": "-noshaderprewarm",
            "NoShaderPreoptimize": "-noshaderpreoptimize",
            "NoShaderPrecompileAll": "-noshaderprecompileall",
            "NoShaderPrecacheAll": "-noshaderprecacheall",
            "NoShaderPreloadAll": "-noshaderpreloadall",
            "NoShaderPrewarmAll": "-noshaderprewarmall",
            "NoShaderPreoptimizeAll": "-noshaderpreoptimizeall",
        }

        for option, toggle in self.toggles.items():
            if toggle.get_active():
                if option in toggle_mapping:
                    command.append(toggle_mapping[option])

        input_mapping = {
            "Width": "-width",
            "Height": "-height",
            "DXLevel": "-dxlevel",
            "Particles": "-particles",
            "Refresh": "-refresh",
        }

        for option, entry in self.inputs.items():
            value = entry.get_text().strip()
            if value:
                command.append(input_mapping[option])
                command.append(value)

        # Process each tab
        for tab_name, data in self.tab_data.items():
            if not data["enable_toggle"].get_active():
                continue

            # Wine
            if tab_name == "Wine":
                active_toggles = any(toggle.get_active() for toggle in data["toggles"].values())
                active_inputs = any(entry.get_text().strip() for entry in data["inputs"].values())
                if active_toggles or active_inputs:
                    options = []
                    for option, toggle in data["toggles"].items():
                        if toggle.get_active():
                            options.append(f"{option}=1")
                    for option in ["WINEPREFIX", "WINEARCH", "WINEDLLOVERRIDES", "WINEDEBUG", "WINELOGFILE", "WINESERVER", "WINELOADER", "WINEDLLPATH", "WINEBIN"]:
                        value = data["inputs"][option].get_text().strip()
                        if value:
                            if option == "WINEDEBUG" and value == "-all":
                                options.append("WINEDEBUG=-all")
                            else:
                                options.append(f"{option}={value}")
                    if options:
                        command.insert(0, " ".join(options))

            # MangoHud
            elif tab_name == "MangoHud":
                active_toggles = any(toggle.get_active() for toggle in data["toggles"].values())
                active_inputs = any(entry.get_text().strip() for entry in data["inputs"].values())
                active_dropdowns = any(combo.get_active_text() for combo in data["dropdowns"].values())
                if active_toggles or active_inputs or active_dropdowns:
                    options = ["mangohud"]
                    for option, toggle in data["toggles"].items():
                        if toggle.get_active():
                            options.append(f"{option}=1")
                    for option in ["CONFIG", "FPSAVERAGE", "FPS_LIMIT", "FPS_THRESHOLD", "COLOR", "XOFFSET", "YOFFSET"]:
                        value = data["inputs"][option].get_text().strip()
                        if value:
                            options.append(f"MANGOHUD_{option}={value}")
                    align = data["dropdowns"]["ALIGN"].get_active_text()
                    if align:
                        options.append(f"MANGOHUD_ALIGN={align}")
                    command.insert(0, " ".join(options))

            # vkBasalt
            elif tab_name == "vkBasalt":
                active_toggles = any(toggle.get_active() for toggle in data["toggles"].values())
                active_inputs = any(entry.get_text().strip() for entry in data["inputs"].values())
                active_sliders = any(toggle.get_active() for toggle in data["slider_toggles"].values())
                if active_toggles or active_inputs or active_sliders:
                    options = ["vkbasalt"]
                    for option, toggle in data["toggles"].items():
                        if toggle.get_active():
                            options.append(f"{option}=1")
                    for option in ["CONFIG", "SHADERS"]:
                        value = data["inputs"][option].get_text().strip()
                        if value:
                            options.append(f"VK_BASALT_{option}={value}")
                    for option in TAB_CONFIGS[tab_name]["sliders"]:
                        option_key = option[0]
                        if data["slider_toggles"].get(option_key, Gtk.Switch()).get_active():
                            _, slider = data["sliders"][option_key]
                            value = slider.get_value()
                            options.append(f"VK_BASALT_{option_key}={value}")
                    command.insert(0, " ".join(options))

            # GameMode
            elif tab_name == "GameMode":
                if data["toggles"]["GAME_MODE"].get_active():
                    command.insert(0, "gamemoderun")

            # Gamescope
            elif tab_name == "Gamescope":
                active_toggles = any(toggle.get_active() for toggle in data["toggles"].values())
                active_inputs = any(entry.get_text().strip() for entry in data["inputs"].values())
                active_dropdowns = any(combo.get_active_text() != "None" for combo in data["dropdowns"].values())
                if active_toggles or active_inputs or active_dropdowns:
                    options = ["gamescope"]
                    for option, toggle in data["toggles"].items():
                        if toggle.get_active():
                            options.append(f"-{option}")
                    for option in ["W", "H", "r", "s", "t", "d", "p", "x", "y"]:
                        value = data["inputs"][option].get_text().strip()
                        if value:
                            options.append(f"-{option} {value}")
                    input_type = data["dropdowns"]["inputs"].get_active_text()
                    if input_type != "None":
                        if input_type in ["Keyboard", "All"]:
                            options.append("-k")
                        if input_type in ["Mouse", "All"]:
                            options.append("-m")
                        if input_type in ["Gamepad", "All"]:
                            options.append("-g")
                    command.insert(0, " ".join(options))

            # DXVK
            elif tab_name == "DXVK":
                active_toggles = any(toggle.get_active() for toggle in data["toggles"].values())
                active_inputs = any(entry.get_text().strip() for entry in data["inputs"].values())
                if active_toggles or active_inputs:
                    options = []
                    for option, toggle in data["toggles"].items():
                        if toggle.get_active():
                            options.append(f"{option}=1")
                    for option in [
                        "HUD", "STATE_CACHE_PATH", "SHADER_CACHE_PATH", "LOG_LEVEL",
                        "MAX_FRAME_LATENCY", "MAX_FRAMES_IN_FLIGHT", "FORCE_FEATURE_LEVEL",
                        "SHADER_MODEL", "MAX_SHADER_RESOURCE_GROUPS"
                    ]:
                        value = data["inputs"][option].get_text().strip()
                        if value:
                            options.append(f"DXVK_{option}={value}")
                    if options:
                        command.insert(0, " ".join(options))

            # ProtonCustom
            elif tab_name == "ProtonCustom":
                active_toggles = any(toggle.get_active() for toggle in data["toggles"].values())
                active_inputs = any(entry.get_text().strip() for entry in data["inputs"].values())
                if active_toggles or active_inputs:
                    options = []
                    for option, toggle in data["toggles"].items():
                        if toggle.get_active():
                            options.append(f"{option}=1")
                    for option in ["LOG_FILE", "USE_WINEDEBUG"]:
                        value = data["inputs"][option].get_text().strip()
                        if value:
                            options.append(f"PROTON_{option}={value}")
                    if options:
                        command.insert(0, " ".join(options))

            # MesaOverlay
            elif tab_name == "MesaOverlay":
                active_toggles = any(toggle.get_active() for toggle in data["toggles"].values())
                active_inputs = any(entry.get_text().strip() for entry in data["inputs"].values())
                active_dropdowns = any(combo.get_active_text() for combo in data["dropdowns"].values())
                if active_toggles or active_inputs or active_dropdowns:
                    options = []
                    for option, toggle in data["toggles"].items():
                        if toggle.get_active():
                            options.append(f"{option}=1")
                    for option in ["CONFIG", "XOFFSET", "YOFFSET", "COLOR", "FONT_SIZE", "LOG_FILE", "Transparency"]:
                        value = data["inputs"][option].get_text().strip()
                        if value:
                            option_key = "TRANSPARENCY" if option == "Transparency" else option
                            options.append(f"MESA_OVERLAY_{option_key}={value}")
                    align = data["dropdowns"]["ALIGN"].get_active_text()
                    if align:
                        options.append(f"MESA_OVERLAY_ALIGN={align}")
                    if options:
                        command.insert(0, " ".join(options))

        # Add custom arguments
        custom_args = self.args_entry.get_text().strip()
        if custom_args:
            command.append(custom_args)

        # Generate the final command
        final_command = " ".join(command) + " %command%" if command else "%command%"

        dialog = Gtk.Dialog(
            title="Launch Command",
            transient_for=self,
            flags=0,
            border_width=10
        )
        dialog.set_default_size(600, 150)

        content_area = dialog.get_content_area()
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        content_area.add(vbox)

        label = Gtk.Label(label="Launch Command (select to copy):")
        vbox.pack_start(label, False, False, 0)

        textview = Gtk.TextView()
        textview.set_editable(False)
        textview.set_wrap_mode(Gtk.WrapMode.WORD)
        textbuffer = textview.get_buffer()
        textbuffer.set_text(final_command)
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.add(textview)
        scrolled_window.set_min_content_height(50)
        vbox.pack_start(scrolled_window, True, True, 0)

        hbox_buttons = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        vbox.pack_start(hbox_buttons, False, False, 0)

        copy_button = Gtk.Button(label="Copy to Clipboard")
        copy_button.connect("clicked", lambda btn: Gdk.Clipboard.get(Gdk.SELECTION_CLIPBOARD).set_text(final_command, -1))
        hbox_buttons.pack_start(copy_button, True, True, 0)

        ok_button = Gtk.Button(label="OK")
        ok_button.connect("clicked", lambda btn: dialog.destroy())
        hbox_buttons.pack_start(ok_button, True, True, 0)

        dialog.show_all()

    def on_cancel_clicked(self, button):
        self.save_settings()
        Gtk.main_quit()

def main():
    window = SteamLauncherWindow()
    window.connect("destroy", Gtk.main_quit)
    window.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()
