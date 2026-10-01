[app]

title = My Learning Adventure

package.name = learningadventure

package.domain = org.sandip

source.dir = .

source.include_exts = py,png,jpg,jpeg,kv,atlas,json,db

version = 1.0

requirements = python3==3.11.9,hostpython3==3.11.9,kivy

orientation = portrait

fullscreen = 0


# Android settings

android.api = 35

android.minapi = 23

android.ndk = 27c

android.accept_sdk_license = True

android.archs = arm64-v8a


# Application permissions

android.permissions = INTERNET


# Presplash



# Icon




[buildozer]

log_level = 2

warn_on_root = 1