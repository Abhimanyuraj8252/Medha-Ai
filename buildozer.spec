[app]

# (str) Title of your application
title = Medha AI Assistant

# (str) Package name
package.name = medhaai

# (str) Package domain (needed for android/ios packaging)
package.domain = com.medhaai

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,jpeg,kv,atlas,json,txt,ttf,otf,md

# (list) Source files to exclude (let empty to not exclude anything)
#source.exclude_exts = spec

# (list) List of directory to exclude (let empty to not exclude anything)
source.exclude_dirs = tests, bin, venv, __pycache__, .git, .github, screenshots

# (list) List of exclusions using pattern matching
#source.exclude_patterns = license,images/*/*.jpg

# (str) Application versioning (method 1)
version = 2.0.0

# (str) Application versioning (method 2)
# version.regex = __version__ = ['"](.*)['"]
# version.filename = %(source.dir)s/main.py

# (list) Application requirements
# Flet requires these packages
requirements = python3==3.11.6,flet==0.25.2,groq==0.11.0,google-generativeai==0.8.3,requests,beautifulsoup4,pyttsx3,SpeechRecognition,pillow,duckduckgo-search

# (str) Supported orientation (landscape, portrait or all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
# Note: RECORD_AUDIO for voice, INTERNET for AI APIs
android.permissions = INTERNET,ACCESS_NETWORK_STATE,RECORD_AUDIO,MODIFY_AUDIO_SETTINGS,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,WAKE_LOCK

# (list) Android app features
android.features = android.hardware.microphone

# (int) Target Android API, should be as high as possible.
android.api = 34

# (int) Minimum API your APK will support.
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (bool) Use --private data storage (True) or --dir public storage (False)
android.private_storage = True

# (str) Android NDK directory (if empty, it will be automatically downloaded.)
#android.ndk_path =

# (str) Android SDK directory (if empty, it will be automatically downloaded.)
#android.sdk_path =

# (str) ANT directory (if empty, it will be automatically downloaded.)
#android.ant_path =

# (str) python-for-android git clone directory
#p4a.source_dir =

# (str) python-for-android branch to use (leave empty for master)
#p4a.branch = develop

# (list) python-for-android extra dependencies
# Flet requires these dependencies
p4a.extra_depends = libffi,openssl

# (str) The Android arch to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
# arm64-v8a is recommended for modern devices
android.archs = arm64-v8a

# (bool) enables Android auto backup feature (Android API >=23)
android.allow_backup = True

# (str) XML file for custom backup rules (leave empty for default)
#android.backup_rules =

# (str) The Android app theme, default is ok for Kivy-based app
#android.apptheme = "@android:style/Theme.NoTitleBar"

# (list) Android additionnal libraries to copy into libs/armeabi
#android.add_libs_armeabi = libs/android/*.so

# (list) Android additionnal libraries to copy into libs/arm64-v8a
#android.add_libs_arm64-v8a = libs/android-arm64/*.so

# (bool) Indicate whether the screen should stay on
# Don't go to sleep on long AI responses
android.wakelock = True

# (list) Android application meta-data to set
# Enable hardware acceleration for better performance
android.meta_data = com.google.android.gms.car.application=true

# (str) Android logcat filters to use
#android.logcat_filters = *:S python:D

# (bool) Copy library instead of making a libpymodules.so
#android.copy_libs = 1

# (str) The Android application icon. Adaptive icon in mipmap folder
# Uncomment and add your icon
#icon.filename = %(source.dir)s/assets/icon.png
#icon.adaptive_foreground.filename = %(source.dir)s/assets/icon_fg.png
#icon.adaptive_background.filename = %(source.dir)s/assets/icon_bg.png

# (str) Presplash of the application
# Uncomment to add splash screen
#presplash.filename = %(source.dir)s/assets/presplash.png

# (str) Presplash background color (for new android toolchain)
#presplash.color = #000000

# (str) Adaptive icon background color (for new android toolchain)
#icon.adaptive_background_color = #FFFFFF

# (list) Android additionnal adb arguments
#android.adb_args = -H host.docker.internal

# (bool) Enable AndroidX support
android.enable_androidx = True

# (bool) Enable Jetifier for AndroidX support
android.enable_jetifier = True

# (str) The gradle dependencies to add
# android.gradle_dependencies = com.google.android.material:material:1.6.0

# (str) Java files to add to the android project
#android.add_jars = foo.jar,bar.jar

# (list) Gradle repositories to add
#android.gradle_repositories = "mavenCentral()"

#
# iOS specific
#

# (str) Name of the certificate to use for signing the debug version
#ios.codesign.debug = "iPhone Developer: <lastname> <firstname> (<hexstring>)"

# (str) Name of the certificate to use for signing the release version
#ios.codesign.release = %(ios.codesign.debug)s


[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1

# (str) Path to build artifact storage, absolute or relative to spec file
# build_dir = ./.buildozer

# (str) Path to build output (i.e. .apk, .aab) storage
# bin_dir = ./bin
