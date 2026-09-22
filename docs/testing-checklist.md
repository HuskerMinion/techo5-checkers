# What a tester needs to do

The port is done and TECHO5 installs on this generation from the
[main repository](https://github.com/HuskerMinion/techo5). This is the check that came before it, and
it is still what to run on a unit that behaves oddly or on one you want ground truth from: the
hardware dump, the backup, and a short set of questions. Nothing here is destructive or requires
unlocking anything.

## What you need

- An Echo Show 5, **1st generation** (2019, model **H23K37**).
- Root/adb access. If it's already unlocked with LineageOS on it, you're already past this — `adb root`
  should just work. (If starting from scratch instead, the
  [XDA unlock/root/TWRP thread for this device](https://xdaforums.com/t/unlock-root-twrp-unbrick-amazon-echo-show-5-1st-gen-2019-checkers.4762900/)
  is the same community work TECHO5's own unlock is built on for the 2nd-gen model, just a different
  branch — [`mt8163-checkers`](https://github.com/R0rt1z2/amonet/tree/mt8163-checkers) instead of
  `mt8163-cronos`.)
- A computer with `adb` installed (part of Android's platform-tools).

## What to run

**On Windows, follow [windows-guide.md](windows-guide.md)**: every step, from installing Python to
sending the results. It uses [`tools/checkers-kit.py`](../tools/checkers-kit.py), which also makes a
full, checked backup of the Show first and takes the serial number and network addresses out of the
results for you.

On a Mac or Linux, the same kit: `python3 tools/checkers-kit.py check`, then `backup`, then `test`.

Just the hardware dump, by hand:

```
adb root
adb push tools/hwdump.sh /data/local/tmp/
adb shell sh /data/local/tmp/hwdump.sh > checkers-dump.txt
```

(Remove the serial number and MAC addresses from it before sending it.)

That's it for step one. The script is read-only — it doesn't modify anything, doesn't open any audio
device, and doesn't touch the bootloader. It just reads out what the device's kernel and drivers report
about themselves (CPU, display panel, touch controller, audio chips, Wi-Fi/BT chip, sensors, buttons),
the same way it was used to build
[TECHO5's own hardware.md](https://github.com/HuskerMinion/techo5/blob/main/docs/hardware.md) for the
2nd-gen Show 5.

## What happens with it

A first dump, from Empty2k12's unit, already confirmed most of the hardware (see
[hardware.md](hardware.md)), and their work got the speaker playing. The kit's tests go after what's
still open, and a second unit's dump shows whether units differ (board revisions sometimes do):

- **Mute**: does the button light the red indicator, and can software switch the microphones off but
  never back on, the way TECHO5 relies on?
- **Camera**: does the OV9734 give a picture in LineageOS, with the right colors?
- **Your unit's hardware**: does it match the first dump?

## Wi-Fi: use WPA2

When the time comes to try a TECHO5 build on the unit: it **can't join WPA3 networks, or networks that
require "protected management frames" (PMF)** — it scans and never connects. Use a WPA2-Personal
network with PMF off or set to "optional" (a guest network works well for this).

## After that

Once the hardware picture is clear, the next steps (in order, each depending on the last actually
working) are:

1. ~~Confirm the `mt8163-checkers` unlock and TWRP work as documented on XDA.~~ Already done.
2. Build the `checkers` kernel (its own config, with TECHO5's Bluetooth options) and boot image.
3. Get the TECHO5 Linux image booting; the screen, touch, microphones and Wi-Fi are expected to work
   unchanged since they match the 2nd gen.
4. The speaker: switch the amplifier on safely, then tune the volume by ear.
5. The mute switch and the camera, then everything else as a smoke test (wake word, alarms, updates).

Each of those is its own round of "try it, report back what happened" — there's no way to skip ahead
without a real device to test each step on.
