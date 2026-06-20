[app]
title = REZ AI
package.name = rezai
package.domain = org.rez.bossjid
source.dir = .
source.include_exts = py,png,jpg,ttf
version = 2.0

requirements = python3,kivy,pyttsx3,speechrecognition,pyaudio,requests
android.permissions = RECORD_AUDIO, INTERNET, WAKE_LOCK
android.api = 33
android.ndk = 25b
android.arch = arm64-v8a, armeabi-v7a
android.enable_androidx = True
android.meta_data = com.google.android.gms.vision.DEPENDENCIES=ocr

[buildozer]
log_level = 2
warn_on_root = 1
