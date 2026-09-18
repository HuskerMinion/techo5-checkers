# Echo Show 5 (1st gen, 2019) — `checkers`

What's known so far comes from reading the kernel source the LineageOS build for `checkers` is made
from (`amazon-oss/android_kernel_amazon_mt8163`, branch `cronos/lineage-18.1`, which carries both
the 1st and 2nd gen device trees), gathered by Empty2k12 in
[TECHO5 pull request #2](https://github.com/HuskerMinion/techo5/pull/2) (see `docs/porting-checkers.md`
there for their full write-up). Almost none of it has been checked on a unit by this project yet:
**Confirmed** means seen on a real `checkers`; everything else is from source and waits on
`tools/hwdump.sh` output ([testing-checklist.md](testing-checklist.md)).

Compare against [TECHO5's own hardware.md](https://github.com/HuskerMinion/techo5/blob/main/docs/hardware.md)
(`cronos`, 2nd gen): whatever matches can reuse its code as it is.

## The short version

`checkers` is very close to `cronos`, far closer than the Dot or the Spot. Same SoC, panel, touch
controller, microphone path, Wi-Fi/Bluetooth chip and partition layout. **Four things differ**, and
only the first is real work:

1. **The speaker** — a different codec and amplifier (below).
2. **The mute switch** — a different driver, same behaviour.
3. **The kernel build** — its own config and device trees.
4. **The camera** — a smaller sensor.

## Board

| Item | `checkers` (1st gen, 2019) | vs `cronos` |
|---|---|---|
| SoC | MediaTek MT8163, 32-bit userspace | same (confirmed) |
| Kernel | 4.9.337 arm64, `checkers_defconfig`, same tree and branch as cronos | same tree; own config |
| LineageOS | 18.1, `lineage-18.1-20260904-UNOFFICIAL-checkers` (R0rt1z2) | same build date |
| Unlock | amonet `mt8163-checkers`, same button combo and fastbrick flow | same method, own branch |
| Display | ST7701S, 480×960 portrait, 63×125 mm (`st7701s_wsvga_dsi_vdo_checkers`) | same |
| Touch | Goodix `gt9xx`, I²C 2-0x5d | same |
| Microphones | FPGA on SPI into `amzn-mt-spi-pcm`: 4 channels, S24_3LE, 16 kHz, `pcmC0D22c`; averages two mics into both slots (same `amzn,mic-downmix` fix as cronos) | same |
| Mic ADC | TI TLV320AIC3101, I²C 0-0x18 | same |
| Playback node | `pcmC0D23p` | same |
| **Speaker** | **Realtek RT5616 codec, I²C 2-0x1b, plus an external amplifier on GPIO 35** | **different** (cronos: MAX98396) |
| Wi-Fi / BT | MediaTek MT7668 SDIO (`mt76x8_wlan.ko` / `mt76x8_bt.ko`, `/dev/stpbt`) | same |
| Buttons | key codes 114 / 115 / 116, plus the camera lens cover switch | same |
| **Mute** | **`amazon-gating` driver** (`/sys/devices/platform/amazon-gating/`), button arrives as key 116 on an input device named `gating` | **different driver**, same one-way latch |
| Light sensor | `alsps` via MediaTek hwmsensor, chip `jsa1214` | same interface, different chip |
| **Camera** | **OmniVision OV9734, 1 MP, 1280×720**, one-lane MIPI RAW10 | **different** (cronos: 2 MP OV02B10) |
| Partitions | MISC p8, boot p9, system p12, userdata p16 | same |
| Recovery | p11 (32 MB) | differs (cronos: p10) — *to confirm* |

## What differs, in more detail

### Speaker (the real work)

The speaker path is a Realtek RT5616 with an external amplifier switched by a GPIO. So none of
cronos's speaker setup applies: there's no "Speaker Safe Mode" to clear, and the mixer controls have
different names (`HP Playback Switch`, `OUT Playback Switch`, `DAC1 Playback Volume`, …).
`Ext_Speaker_Amp_Switch` is probably a real amplifier on/off here, the way it is on the Dot and the
Spot — whereas on cronos it's wired to the amplifier's reset and must never be touched. **This is the
first thing to test carefully**, and the volume curve will need retuning by ear for this amplifier.

### Mute switch

Same one-way hardware latch as cronos (software can mute, only the button can unmute), but behind
Amazon's `amazon-gating` driver instead of `gpio-privacy`, with the same `state` / `enable` files. The
button comes through as an ordinary key, so button handling needs nothing new.

### Kernel build

Its own `checkers_defconfig`, with five appended device trees instead of cronos's eleven, and only the
v193 FPGA bitstream. The Bluetooth options TECHO5 adds and the microphone downmix fix apply the same
way. Whether the LineageOS `checkers` kernel is the same commit the vendor modules were built against
is one of the things `uname -a` in the hwdump settles.

### Camera

A 1 MP OV9734 (1280×720) instead of cronos's 2 MP sensor. The camera pipeline carries over; only the
frame geometry differs. A first picture tells whether the colour order matches (red and blue swapped
is unmistakable).

## Known catch: Wi-Fi security

TECHO5's Wi-Fi (the pinned wpa_supplicant 2.9) **does not support WPA3**, and **won't join a network
that requires "protected management frames" (PMF)**. On either, it scans forever and never connects.
Use WPA2-Personal with PMF off or "optional". This applies to every TECHO5 device, not just
`checkers`; it was reported on a `checkers` unit in the same pull request.

## Open questions only a unit can answer

- Is `Ext_Speaker_Amp_Switch` safe to switch here, and is it needed for sound?
- Is the LineageOS `checkers` kernel the same commit as its vendor modules?
- Does the mute latch cut the microphones and light the red indicator the same way, one-way?
- Does the camera come up at 1280×720 with the same colour order?
- Is recovery really p11 here, and does the boot slot take 64-bit kernels only, as on cronos?
