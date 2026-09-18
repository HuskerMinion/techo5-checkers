# Windows guide: back up your checkers and run the tests

For a 1st-gen Echo Show 5 (`checkers`) that already runs LineageOS. It takes about 30 minutes, most
of it waiting for the backup. Nothing here changes what's installed on the Show.

You'll do four things:

1. Install Python and Android's adb tool (once).
2. Download this kit.
3. Make a full backup of the Show, kept on your PC.
4. Run the tests and attach the results to [issue #1](https://github.com/HuskerMinion/techo5-checkers/issues/1).

Everything you type is shown in a box like this, and goes into **PowerShell** (step 3 shows how to
open it in the right folder):

```
python --version
```

---

## Step 1: Install Python

1. Go to <https://www.python.org/downloads/> and click the yellow **Download Python 3.x** button.
2. Run the file you downloaded.
3. On the first screen, **tick "Add python.exe to PATH"** at the bottom. This matters: without it,
   Windows can't find Python later.
4. Click **Install Now**, and **Close** when it's done.

To check: open the Start menu, type `powershell`, open **Windows PowerShell**, and type:

```
python --version
```

It should answer with something like `Python 3.13.1`. If the Microsoft Store opens instead, or it
says "not recognized", see [If something goes wrong](#if-something-goes-wrong).

## Step 2: Install adb (Android's platform-tools)

If you already used adb on this Show, you may have it. The kit looks for it on its own, and tells you
if it can't find it. If you need it:

1. Go to <https://developer.android.com/tools/releases/platform-tools> and click
   **Download SDK Platform-Tools for Windows**. Accept the terms to download the ZIP.
2. In your Downloads folder, right-click the ZIP and choose **Extract All...**
3. In the box, type `C:\` and click **Extract**. You'll end up with a folder `C:\platform-tools`
   holding `adb.exe`. The kit knows to look there.

## Step 3: Download the kit and open PowerShell in it

1. Go to <https://github.com/HuskerMinion/techo5-checkers> (sign in to GitHub first, since the
   repository is private).
2. Click the green **Code** button, then **Download ZIP**.
3. Right-click the ZIP in your Downloads folder, choose **Extract All...**, type `C:\` and click
   **Extract**. You'll get a folder like `C:\techo5-checkers-main`.
4. Open that folder in File Explorer. Click once in the **address bar** at the top (where it shows the
   folder's path), type `powershell` and press **Enter**. A PowerShell window opens, already in the
   kit's folder.

Keep this window open for the rest of the guide.

## Step 4: Connect the Show and check it

1. Plug the Show into the PC with the same USB cable you used for LineageOS.
2. On the Show, make sure **USB debugging** and **Rooted debugging** are on
   (Settings > System > Developer options). If you've used adb with it before, they are.
3. In PowerShell, type:

```
python tools\checkers-kit.py check
```

You should see:

```
Looking for the Show...
Found: checkers, running lineage_checkers-userdebug 11 ...
Root access: yes

All good. Next: python tools/checkers-kit.py backup
```

If the Show's screen asks **"Allow USB debugging?"**, tick **Always allow from this computer**, tap
**Allow**, and run the command again.

## Step 5: Back up the Show

This copies every part of the Show's storage to your PC and checks each copy against the Show, so
that whatever we try later can be undone. It needs about 3.5 GB of free space and takes 10 to 20
minutes.

```
python tools\checkers-kit.py backup
```

It shows each part as it goes (`[12/16] system (3.3 GB)...`, then `copied and checked`) and ends with
`Backup done`. The backup goes in a new folder in the kit's folder, named like
`checkers-backup-20260919-1030`.

- **Keep that folder safe.** A second copy on a USB stick is a good idea.
- **Keep it private.** It holds your Show's own serial number, network addresses and factory keys.
  Don't upload it, attach it to anything or share it with anyone, us included. We'll never ask for it.

It leaves out LineageOS's apps and settings (the `userdata` part), which aren't needed to get the Show
back. To include them anyway, add `--with-userdata` (about 4 GB more).

## Step 6: Run the tests

```
python tools\checkers-kit.py test
```

This takes about five minutes and asks you a few things as it goes. Answer `y` or `n` and press
Enter, or just press Enter when it asks you to do something first.

1. **Reading the hardware**: about a minute, nothing to do.
2. **The mute button**: it asks you to press the mute button on top of the Show a few times, and
   whether the red light comes on.
3. **Muting from software**: it switches the microphones off the way TECHO5 will, asks whether the
   red light came on, then asks you to press the mute button to switch them back on. (That's the
   point of the test: only the button should be able to undo it.)
4. **The camera**: slide the camera shutter open first. A camera app opens on the Show (allow it if
   it asks); say whether you see a picture and whether the colours look right.

At the end it tells you where it saved the results, a file like `checkers-results-20260919-1045.txt`
in the kit's folder. **The serial number, network addresses and other identifiers are already taken
out**, and you can open it in Notepad to look it over first.

## Step 7: Send the results

1. Go to [issue #1](https://github.com/HuskerMinion/techo5-checkers/issues/1).
2. Drag the `checkers-results-....txt` file into the comment box at the bottom (or click the box and
   use the paperclip to pick it).
3. Click **Comment**.

Only the results file. Never the backup folder.

That's it, thank you. The microphones should be back on at the end (no red light); if the red light
is on, press the mute button once.

---

## If something goes wrong

You can stop any step with **Ctrl+C**. Nothing is changed on the Show, and you can simply run it again.

**`python` opens the Microsoft Store, or says "not recognized"**
Python isn't installed, or wasn't added to PATH. Run the Python installer again and tick
**Add python.exe to PATH** (if it offers **Modify**, choose it, click Next, and tick **Add Python to
environment variables**). Close PowerShell and open it again from the kit's folder. Typing `py`
instead of `python` often works too.

**"adb was not found"**
Check that `C:\platform-tools\adb.exe` exists (step 2). If adb is somewhere else, tell the kit where:

```
python tools\checkers-kit.py --adb "C:\path\to\adb.exe" check
```

**"no device found"**
Unplug the Show and plug it back in, try another USB port (one directly on the PC, not a hub), and
check USB debugging is on (step 4). If it still isn't found, Windows may need the USB driver: open
Device Manager with the Show plugged in and look for an entry with a yellow warning sign.

**"the Show hasn't allowed this computer yet"**
Look at the Show's screen: tick **Always allow from this computer** and tap **Allow**.

**"adb root didn't work"**
On the Show: Settings > System > Developer options > **Rooted debugging**, on.

**The backup says a part "came across short" or "doesn't match"**
The copy was interrupted. Use another cable or USB port and run the backup again. It starts a fresh
folder each time; delete the incomplete one.

**Anything else**
Copy what PowerShell shows (select it with the mouse, then right-click to copy) into a comment on
[issue #1](https://github.com/HuskerMinion/techo5-checkers/issues/1). Check it for your serial number
first, since error messages aren't cleaned the way the results file is.

On a Mac, the same commands work in Terminal with `python3` and forward slashes
(`python3 tools/checkers-kit.py check`).
