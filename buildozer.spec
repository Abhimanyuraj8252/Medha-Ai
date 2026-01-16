[app]

# App title
title = Medha AI

# Package name
package.name = medhaai

# Package domain
package.domain = org.medhaai

# Source code location
source.dir = .

# Source include patterns
source.include_exts = py,png,jpg,kv,atlas,json,txt

# Version
version = 1.0

# Requirements
requirements = python3,kivy==2.2.1,requests,beautifulsoup4,pillow

# Orientation
orientation = portrait

# Permissions
android.permissions = INTERNET,RECORD_AUDIO,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# Android API
android.api = 33
android.minapi = 21
android.ndk = 25b

# Android architecture
android.archs = arm64-v8a,armeabi-v7a

# Icon
#icon.filename = %(source.dir)s/assets/icon.png

# Presplash
#presplash.filename = %(source.dir)s/assets/presplash.png

# Full screen
fullscreen = 0

# Buildozer settings
[buildozer]
log_level = 2
warn_on_root = 1
