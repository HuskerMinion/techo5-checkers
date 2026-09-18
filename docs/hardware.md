# Echo Show 5 (1st gen, 2019) — `checkers`

What's known so far comes from two places, both from Empty2k12 in
[TECHO5 pull request #2](https://github.com/HuskerMinion/techo5/pull/2): their reading of the kernel
source the LineageOS build for `checkers` is made from (`amazon-oss/android_kernel_amazon_mt8163`,
branch `cronos/lineage-18.1`, which carries both the 1st and 2nd gen device trees), and, since
2026-09-18, a `tools/hwdump.sh` dump and audio register readings from their own unit running
LineageOS 18.1, plus their work getting the speaker to play. See `docs/porting-checkers.md` there for
their full write-up.

**Confirmed** below means seen on a real `checkers`; anything else is from source only.

Compare against [TECHO5's own hardware.md](https://github.com/HuskerMinion/techo5/blob/main/docs/hardware.md)
(`cronos`, 2nd gen): whatever matches can reuse its code as it is.

## The short version

`checkers` is very close to `cronos`, far closer than the Dot or the Spot. Same SoC, panel, touch
controller, microphone path, Wi-Fi/Bluetooth chip, kernel commit and partition layout, all now seen
on a unit. **Four things differ**:

1. **The speaker** — a different codec and amplifier. **Now solved on a unit** (below).
2. **The mute switch** — a different driver, same behaviour.
3. **The kernel build** — its own config and device trees.
4. **The camera** — a smaller sensor.

## Board

| Item | `checkers` (1st gen, 2019) | vs `cronos` |
|---|---|---|
| SoC | MediaTek MT8163, 4 cores to 1.3 GHz, 32-bit userspace | same (confirmed) |
| Memory / storage | 1 GB RAM, 8 GB eMMC | same (confirmed) |
| Kernel | 4.9.337 arm64, `checkers_defconfig`; LineageOS's kernel is `4.9.337-g8d928c5176cc`, the same commit as cronos, so the vendor modules load | same commit (confirmed) |
| LineageOS | 18.1, `lineage-18.1-20260904-UNOFFICIAL-checkers` (R0rt1z2) | same build date |
| Unlock | amonet `mt8163-checkers`, same button combo and fastbrick flow | same method, own branch |
| Display | ST7701S, 960×480 landscape at 59.6 Hz (`lcm=1-st7701s_wsvga_dsi_vdo_checkers_st_inx`) | same (confirmed) |
| Touch | Goodix `gt9xx` at I²C 2-0x5d, input `goodix-ts`, X 0–480 and Y 0–960 (portrait frame) | same (confirmed) |
| Microphones | FPGA on SPI into `amzn-mt-spi-pcm`: 4 channels, S24_3LE, 16 kHz, `pcmC0D22c` ("TLV320AIC3101 Capture") | same (node confirmed) |
| Mic ADC | TI TLV320AIC3101 at I²C 0-0x18, enabled by GPIO `aic3101_enable` | same (confirmed) |
| Playback node | `pcmC0D23p` ("RT5616_Playback") | same node (confirmed) |
| **Speaker** | **Realtek RT5616 codec at I²C 2-0x1b, plus an external amplifier on `amp_gpio` (pio 35), active low** | **different** (cronos: MAX98396) |
| Wi-Fi / BT | MediaTek MT7668 SDIO, `mt76x8_wlan.ko` / `mt76x8_bt.ko` loaded, 5 GHz on | same (confirmed) |
| Buttons | `gpio-keys`: volume up / down, plus `SW_CAMERA_LENS_COVER`; the mute button is key 116 on an input device named `gating` | same codes (confirmed) |
| **Mute** | **`amazon-gating` driver** (`/sys/devices/platform/amazon-gating/`); no `SW_MUTE_DEVICE` switch | **different driver** (confirmed), same one-way latch (from source) |
| Light sensor | `alsps` at I²C 0-0x44 via MediaTek hwmsensor, input `m_alsps_input` | same interface, different chip |
| **Camera** | **OmniVision OV9734, 1 MP** (`camera_main` at I²C 0-0x2e, `camera_sub` at 0-0x21), power gate on GPIO `cam_pwr_gate_pin` | **different** (cronos: 2 MP OV02B10) |
| Partitions | MISC p8, boot p9, recovery p10 (16 MB), swdl p11, system p12, cache p13, userdata p16 | same (confirmed) |
| Recovery | p10; writing `boot-recovery` into MISC (p8) and rebooting lands in TWRP | same as cronos (confirmed — an earlier guess of p11 was wrong) |
| Red mute LED | not in `/sys/class/leds` (only `lcd-backlight` is) | how it's driven is still open |

## The speaker: how it was made to play

Worked out by Empty2k12 on their unit (2026-09-18), comparing against LineageOS with a ringtone
playing, and confirmed playing over the serial console. Three things were needed, and missing any one
of them gives silence:

1. **The amplifier switch is active low.** `Ext_Speaker_Amp_Switch` drives `amp_gpio` (pio 35), but the
   opposite way round from the Dot and the Spot: LineageOS plays with it **Off** (pin low) and leaves
   it On (pin high) when idle. Switching it On to play, as the Dot and Spot code does, silences the
   board. Set it Off once and leave it.
2. **The codec's routing has to be wired.** The kernel leaves the RT5616's DAC connected to nothing;
   Amazon's audio layer wires it once at boot. The path is DAC → `OUT MIX` → `OUTVOL` → line-out, not
   the headphone pins. The controls to turn on: `DAC MIXL INF1`, `DAC MIXR INF1`, the four
   `Stereo DAC MIX{L,R} DAC {L1,R1}` switches, `OUT MIXL DAC L1`, `OUT MIXR DAC R1`,
   `LOUT MIX OUTVOL L` and `LOUT MIX OUTVOL R`. (`HPO MIX` and `HP Playback` stay off.)
3. **There are two mutes, both in the same register (`LOUT_CTRL1`, reg 03).** `OUT Playback Switch`
   is the output mute and `OUT Channel Switch` is the volume stage's own; the chip comes out of reset
   with both on. Clearing only the first leaves everything *looking* right (the routing graph matches
   a playing LineageOS unit, the amplifier is enabled) and still silent. With both cleared reg 03 reads
   `0808` against Amazon's `0a0a` (two volume steps apart), and the speaker plays. On this chip, check
   reg 03 directly rather than trusting the routing graph.

Still to do: the volume curve is the 2nd gen's, tuned for a different amplifier, and needs retuning
by ear.

## The rest, in more detail

### Mute switch

Same one-way hardware latch as cronos (software can mute, only the button can unmute), but behind
Amazon's `amazon-gating` driver instead of `gpio-privacy`, with the same `state` / `enable` files.
There's no mute switch input device; the state comes from the `state` file, and the button comes
through as an ordinary key, so button handling needs nothing new.

### Kernel build

Its own `checkers_defconfig`, with five appended device trees instead of cronos's eleven, and only the
v193 FPGA bitstream. The Bluetooth options TECHO5 adds and the microphone downmix fix apply the same
way (all five trees carry `amzn,mic-downmix`).

### Camera

A 1 MP OV9734 instead of cronos's 2 MP sensor. The camera pipeline should carry over with only the
frame geometry changed (1280×720 is the sensor's nominal mode, not yet read off a unit). One thing to
watch: in the dump's boot log the camera driver reports "No imgsensor alive" on its first probes
before settling, which may just be the power gate or the lens cover. A first picture with TECHO5 will
tell whether the geometry and colour order are right.

## Known catch: Wi-Fi security

TECHO5's Wi-Fi (the pinned wpa_supplicant 2.9) **does not support WPA3**, and **won't join a network
that requires "protected management frames" (PMF)**. On either, it scans forever and never connects.
Use WPA2-Personal with PMF off or "optional". This applies to every TECHO5 device, not just
`checkers`; it was reported on a `checkers` unit in the same pull request.

## Open questions

- ~~Is `Ext_Speaker_Amp_Switch` safe to switch, and is it needed for sound?~~ Safe, and it must be
  **Off**: it's active low.
- ~~Is the LineageOS `checkers` kernel the same commit as its vendor modules?~~ Yes.
- ~~Is recovery p11?~~ No, p10, same as cronos.
- Does the mute latch cut the microphones and light the red indicator the same way, one-way? (The red
  LED isn't a normal LED device, so how it's driven needs a look.)
- Does the camera come up at 1280×720 with the same colour order?
- Does the boot slot take 64-bit kernels only, as on cronos?
- The speaker's volume curve, by ear.
