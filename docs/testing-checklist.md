# What a tester needs to do (step 1)

This is the very first step, nothing more — establishing ground truth on real hardware. Nothing here
is destructive or requires unlocking anything yet.

## What you need

- An Echo Show 5, **1st generation** (2019, model **H23K37**) — check the model number on the bottom of
  the unit, or in Settings > Device Options on the device itself if it still runs stock Fire OS.
- A way to get root/adb access to run one read-only script. If the device is still stock and
  unrooted, see the
  [XDA unlock/root/TWRP thread for this device](https://xdaforums.com/t/unlock-root-twrp-unbrick-amazon-echo-show-5-1st-gen-2019-checkers.4762900/)
  first — that's the same community work TECHO5's own unlock is built on for the 2nd-gen model, just a
  different branch ([`mt8163-checkers`](https://github.com/R0rt1z2/amonet/tree/mt8163-checkers) instead
  of `mt8163-cronos`).
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

The dump gets compared field-by-field against cronos's (2nd-gen) hardware.md. Whatever matches can
likely reuse TECHO5's existing code as-is. Whatever differs — a different touch controller, a different
audio codec, a different Wi-Fi/BT chip — is where new, `checkers`-specific code gets written, the same
way `dot` and `spot` each needed their own adaptations for their own hardware.

## After that

Once the hardware picture is clear, the next steps (in order, each depending on the last actually
working) are:

1. Confirm the `mt8163-checkers` unlock and TWRP work as documented on XDA.
2. Get a minimal Linux environment booting at all (even without working display/audio yet).
3. Bring up the display, then audio in/out, then Wi-Fi/Bluetooth, one at a time.
4. Wire up `echod` against whatever's confirmed working, adding a `checkers` build tag only where the
   hardware genuinely differs from cronos.

Each of those is its own round of "try it, report back what happened" — there's no way to skip ahead
without a real device to test each step on.
