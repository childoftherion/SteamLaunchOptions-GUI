"""
Constants used throughout the SteamLauncherGUI application.
"""

# File paths
SETTINGS_FILE = "steam_launcher_settings.json"
LOG_FILE = 'steam_launcher.log'

# DirectX level presets
DX_LEVEL_PRESETS = [
    "50", "70", "80", "81", "90", "95", "98",
    "100", "110", "120",
]

# General options (flags without values)
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

# General inputs (flags with values)
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