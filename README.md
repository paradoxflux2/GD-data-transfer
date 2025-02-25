# GD-data-transfer
A tool to transfer your Geometry Dash save files, without saving to RobTop's servers first.

[screenshot](assets/gddtss.png)

# Before using it

**Enable USB Debugging:**
1. Go to Android settings, and select "About".
2. Tap on "Build number" seven times.
3. Go back. Then select "Developer options"
4. Scroll down, and check the "Android debugging" or "USB debugging" entry under "Debugging".

Now plug your device into a computer. You'll receive a prompt asking if you want to authorize USB debugging for that computer. Check "always allow" and tap OK to confirm

# Download

You can download it [here](https://github.com/paradoxflux2/GD-data-transfer/releases)

# How does it work?

It's pretty simple - it uses the ADB pull and push commands to transfer both CCGameManager.dat and CCLocalLevels.dat to the destination.

Unfortunately, because of this, **it cannot transfer files in a non-rooted Android device IF Geode is not installed on it**. 
Vanilla Geometry Dash stores its save files in /data/data/com.robtopx.geometryjump/, which is inaccesible without root.
While Geode stores its save files in /storage/emulated/0/Android/media/com.geode.launcher/save/, which *is* accessible without a rooted device.

