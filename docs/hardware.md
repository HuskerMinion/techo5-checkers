# Echo Show 5 (1st gen, 2019) — `checkers`

Nothing below is confirmed yet. Fill this in from `tools/hwdump.sh` run on a real unit — see
[testing-checklist.md](testing-checklist.md). Compare against
[TECHO5's own hardware.md](https://github.com/HuskerMinion/techo5/blob/main/docs/hardware.md) (cronos,
2nd gen) once filled in: anything that matches can likely reuse cronos's code as-is; anything that
differs is where `checkers` will need its own build-tagged code, the way `dot` and `spot` do today.

## Board

| Item | Value |
|---|---|
| SoC | MediaTek MT8163 (confirmed — same as cronos) |
| GPU | *unconfirmed* |
| RAM | *unconfirmed* |
| Storage | *unconfirmed* |
| Display | *unconfirmed* — panel driver, resolution, orientation |
| Touch | *unconfirmed* — controller chip, I²C address |
| Audio in | *unconfirmed* — mic count/array, ADC chip |
| Audio out | *unconfirmed* — amp chip |
| Wi-Fi / BT | *unconfirmed* — combo chip |
| Sensors | *unconfirmed* |
| Camera | *unconfirmed* |
| Buttons | *unconfirmed* |
| Bootloader | Amazon LK, unlockable via [amonet's `mt8163-checkers` branch](https://github.com/R0rt1z2/amonet/tree/mt8163-checkers) |
| Kernel | *unconfirmed* — version, whether Bluetooth is present stock (cronos's isn't; TECHO5 rebuilds it) |
| Stock OS | Fire OS (version unconfirmed) |

## Partitions (eMMC)

*unconfirmed — likely similar layout to cronos, but sizes and exact partition names need confirming
from `cat /proc/partitions` and `ls -l /dev/block/*/by-name` in the hwdump output.*
