<p align="center">
  <img src="https://raw.githubusercontent.com/HuskerMinion/techo5/main/logo/TECHO5_logo.png" alt="TECHO5" width="200">
</p>

<h1 align="center">TECHO5 Checkers</h1>

<h3 align="center">An experimental TECHO5 port for the Echo Show 5, 1st generation (2019, codename `checkers`)</h3>

<p align="center">
  <a href="https://github.com/HuskerMinion/techo5">TECHO5 for the Echo Show 5 (2nd gen)</a> ·
  <a href="https://github.com/HuskerMinion/techo5-dot">TECHO5 for the Echo Dot</a> ·
  <a href="https://github.com/HuskerMinion/techo5-spot">TECHO5 for the Echo Spot</a>
</p>

---

## Status: not started, needs a tester with real hardware

This repo is a starting point, not a working port. Nobody on this project currently owns a 1st-gen
Show 5 (`checkers`, model H23K37, 2019) to test on, so nothing here has been run against real hardware
yet. It exists so that someone who *does* have the device can help bring it up, the same way
[TECHO5 Dot](https://github.com/HuskerMinion/techo5-dot) and
[TECHO5 Spot](https://github.com/HuskerMinion/techo5-spot) were built: one person with the hardware,
one person who knows this codebase, working from real diagnostic output rather than guesses.

**What's promising:** `checkers` uses the same MediaTek MT8163 SoC as the 2nd-gen Show 5 TECHO5 already
targets, and the same unlock-tool author ([R0rt1z2/amonet](https://github.com/R0rt1z2/amonet)) already
maintains a working `mt8163-checkers` branch for this exact device, alongside the `mt8163-cronos`
branch TECHO5 itself is built on. There's also an existing
[XDA unlock/root/TWRP thread](https://xdaforums.com/t/unlock-root-twrp-unbrick-amazon-echo-show-5-1st-gen-2019-checkers.4762900/)
for it. So the bootloader unlock is very likely just a variant of what TECHO5 already does for cronos.

**What's known now:** reading the kernel source shows `checkers` is very close to the 2nd-gen Show 5 —
same panel, touch, microphones, Wi-Fi/Bluetooth chip and partitions — with four expected differences:
the speaker (a Realtek codec plus external amplifier, the one real piece of work), the mute switch
driver, the kernel build, and a smaller camera. Credit to Empty2k12, whose research in
[TECHO5 pull request #2](https://github.com/HuskerMinion/techo5/pull/2) this comes from. It still
needs confirming on a unit: see [docs/hardware.md](docs/hardware.md) for the details and open questions,
and [docs/testing-checklist.md](docs/testing-checklist.md) for how to help.

## How this will work

1. A tester with a spare/willing-to-experiment `checkers` unit runs [tools/hwdump.sh](tools/hwdump.sh)
   (read-only, doesn't touch audio, safe to run on a device already rooted some other way) and sends
   back the output.
2. That confirms or corrects `docs/hardware.md` with real values, the same way
   [TECHO5's own hardware.md](https://github.com/HuskerMinion/techo5/blob/main/docs/hardware.md) was
   built from a real cronos unit.
3. From there, the `checkers`-specific code covers only what genuinely differs (the speaker first);
   everything that matches the 2nd gen reuses TECHO5's existing code.
4. Each following step (unlock, boot to TWRP, kernel Bluetooth, rootfs, first boot) gets tested the same
   way: a change proposed here, tried on the real device, results reported back.

This stays private until the basics (unlock, boot, a first working image) are confirmed on real
hardware — no point publishing something unverified.
