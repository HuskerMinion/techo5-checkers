# What a tester needs to do (step 1)

This is the very first step, nothing more — establishing ground truth on real hardware. Nothing here
is destructive or requires unlocking anything yet.

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

1. Download [`tools/hwdump.sh`](../tools/hwdump.sh) from this repo.
2. With the device connected over USB and adb root access:
   ```
   adb root
   adb push hwdump.sh /data/local/tmp/
   adb shell sh /data/local/tmp/hwdump.sh > checkers-dump.txt
   ```
3. Send back `checkers-dump.txt`.

That's it for step one. The script is read-only — it doesn't modify anything, doesn't open any audio
device, and doesn't touch the bootloader. It just reads out what the device's kernel and drivers report
about themselves (CPU, display panel, touch controller, audio chips, Wi-Fi/BT chip, sensors, buttons),
the same way it was used to build
[TECHO5's own hardware.md](https://github.com/HuskerMinion/techo5/blob/main/docs/hardware.md) for the
2nd-gen Show 5.

## What happens with it

Much of the hardware is already known from the kernel source (see [hardware.md](hardware.md)): it's
very close to the 2nd-gen Show 5, with four expected differences — the speaker, the mute switch
driver, the kernel build and the camera. The dump confirms or corrects that, and settles the questions
only a real unit can answer:

- **Speaker**: the audio mixer controls (does the RT5616 codec show up, and is there an
  `Ext_Speaker_Amp_Switch`?) — the one part that needs real new work.
- **Kernel**: the exact kernel version and commit (`uname -a`), which decides whether TECHO5's rebuilt
  Bluetooth kernel can be matched to it.
- **Mute switch**: whether `/sys/devices/platform/amazon-gating` is there, as expected.
- **Camera**: which sensor the kernel reports.
- **Partitions**: whether recovery is p11 on this model.

Whatever matches the 2nd gen reuses TECHO5's existing code as it is; whatever differs is where new
`checkers` code gets written.

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
