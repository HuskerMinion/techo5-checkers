<p align="center">
  <img src="https://raw.githubusercontent.com/HuskerMinion/techo5/main/logo/TECHO5_logo.png" alt="TECHO5" width="200">
</p>

<h1 align="center">TECHO5 Checkers</h1>

<h3 align="center">The hardware notes behind TECHO5 on the Echo Show 5, 1st generation (2019, codename <code>checkers</code>)</h3>

<p align="center">
  <a href="https://github.com/HuskerMinion/techo5">TECHO5 for the Echo Show 5</a> ·
  <a href="https://github.com/HuskerMinion/techo5-dot">TECHO5 for the Echo Dot</a> ·
  <a href="https://github.com/HuskerMinion/techo5-spot">TECHO5 for the Echo Spot</a>
</p>

---

## The port is done. Install it from [TECHO5](https://github.com/HuskerMinion/techo5).

The 1st gen Show 5 runs TECHO5: Alpine Linux in place of Fire OS, one daemon, a Home Assistant voice
satellite with its own screen. There is nothing to install from this repository. One build serves both
generations of the Show 5 and works out at run time which one it is on, and the installer takes that
unit's boot image straight from the release:

```
git clone https://github.com/HuskerMinion/techo5
cd techo5
python3 tools/install-show.py --serial <adb serial> --name "Kitchen"
```

Start at [Getting started](https://github.com/HuskerMinion/techo5/blob/main/docs/getting-started.md),
which covers the unlock, LineageOS and the install for both generations.

**What was tested on a unit:** screen, touch, speaker, the microphones, wake word, camera, the mute
button, and voice with spoken replies — over 2026-09-19 and 20. Everything else is the same code that
runs on the 2nd gen, but it has not been put through its paces on this generation, and one unit for two
days is not much mileage. Treat it accordingly: keep your backups.

## What this repository is for

The notes. Four things on `checkers` are not what they are on the 2nd gen, and each one cost real
work to find:

- **The speaker** is a Realtek RT5616 codec with an external amplifier, not the 2nd gen's arrangement.
- **The mute switch** uses a different driver (`amazon-gating`), and its button only signals: the
  software has to do the muting. Worse, the latch cuts power to the microphone path, and releasing it
  does not always bring the path back — which needed a kernel patch, now in TECHO5's own build.
- **The camera** is an OV9734 at 1280×720 with the Bayer order the other way round from the 2nd gen's
  OV02B10.
- **The kernel** is built for this device, from the same Amazon GPL source.

[docs/hardware.md](docs/hardware.md) has all of it, with what was confirmed on real hardware and what
is still read from source only. [docs/testing-checklist.md](docs/testing-checklist.md) is how a unit
gets checked; [docs/windows-guide.md](docs/windows-guide.md) is the same ground from Windows.
[tools/hwdump.sh](tools/hwdump.sh) and [tools/checkers-kit.py](tools/checkers-kit.py) are the
read-only diagnostic scripts the notes were built from — useful on any unit that behaves oddly.

## Credits

[@Empty2k12](https://github.com/Empty2k12) did the first hardware dump, read the kernel source and got
the speaker playing, in [TECHO5 pull request #2](https://github.com/HuskerMinion/techo5/pull/2).
[@JonGilmore](https://github.com/JonGilmore) tested every build on a real unit over two days
([issue #1](https://github.com/HuskerMinion/techo5-checkers/issues/1)); the microphones, the mute
latch, the camera and the spoken replies were all found or confirmed from what he reported. The
bootloader unlock is [R0rt1z2](https://github.com/R0rt1z2)'s amonet, branch `mt8163-checkers`, with the
[XDA thread](https://xdaforums.com/t/unlock-root-twrp-unbrick-amazon-echo-show-5-1st-gen-2019-checkers.4762900/)
for it, and LineageOS 18.1 for `checkers` is theirs too.

## License

MIT, as TECHO5 is. See [LICENSE](LICENSE) and [NOTICE](NOTICE).

TECHO5 isn't affiliated with Amazon. Echo and Alexa are trademarks of Amazon.com, Inc.
