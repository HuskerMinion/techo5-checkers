#!/usr/bin/env python3
"""TECHO5 checkers kit: check the connection, back up the Show, and run the tests, on a 1st-gen Echo
Show 5 (checkers) that runs LineageOS with adb root. Python 3 standard library only; the same on
Windows, macOS and Linux. The step-by-step for Windows is docs/windows-guide.md.

    python tools/checkers-kit.py check     is the Show connected, and is it a checkers?
    python tools/checkers-kit.py backup    copy every partition to this computer, checked
    python tools/checkers-kit.py test      the hardware dump and a few questions, for the issue

Nothing here writes to the Show's storage. The one change `test` makes is to switch the microphones
off with the mute latch, as the mute button does, and it asks you to press the button to switch them
back on.
"""

import argparse
import datetime
import hashlib
import os
import re
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
ISSUE = "https://github.com/HuskerMinion/techo5-checkers/issues/1"

# Partitions left out of the backup unless asked: userdata is the LineageOS apps and settings, and
# cache is scratch space.
SKIP_BY_DEFAULT = {"userdata", "cache"}


def say(msg=""):
    print(msg, flush=True)


def fail(msg):
    say()
    say("PROBLEM: " + msg)
    sys.exit(1)


def ask(question):
    """A yes/no question; returns True for yes."""
    while True:
        a = input(question + " (y/n): ").strip().lower()
        if a in ("y", "yes"):
            return True
        if a in ("n", "no"):
            return False


def wait_enter(prompt):
    input(prompt + " Then press Enter here. ")


# ---- adb ---------------------------------------------------------------------------------------

def find_adb(given):
    if given:
        if not os.path.exists(given):
            fail("no adb at " + given)
        return given
    found = shutil.which("adb")
    if found:
        return found
    exe = "adb.exe" if os.name == "nt" else "adb"
    home = os.path.expanduser("~")
    for d in (r"C:\platform-tools", os.path.join(home, "Downloads", "platform-tools"),
              os.path.join(home, "platform-tools"), os.path.join(REPO, "platform-tools")):
        p = os.path.join(d, exe)
        if os.path.exists(p):
            return p
    fail("adb was not found. Install Android's platform-tools (see docs/windows-guide.md, step 2), "
         "or pass its location: --adb C:\\platform-tools\\adb.exe")


class Adb:
    def __init__(self, path):
        self.path = path

    def run(self, *args, timeout=120, check=True):
        try:
            p = subprocess.run([self.path, *args], capture_output=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            fail("adb took too long to answer (" + " ".join(args) + ")")
        out = p.stdout.decode("utf-8", "replace").replace("\r\n", "\n")
        if check and p.returncode != 0:
            err = p.stderr.decode("utf-8", "replace").strip()
            fail("adb " + " ".join(args[:2]) + " failed: " + (err or out.strip()))
        return out

    def shell(self, cmd, timeout=120):
        return self.run("shell", cmd, timeout=timeout, check=False).strip()


def connect(adb):
    """Makes sure exactly one Show is connected, with root, and returns what it says it is."""
    lines = [l for l in adb.run("devices").splitlines()[1:] if l.strip()]
    if not lines:
        fail("no device found. Is the Show plugged in by USB, with USB debugging on? "
             "See docs/windows-guide.md, 'If something goes wrong'.")
    if len(lines) > 1:
        fail("more than one Android device is connected. Unplug the others and try again.")
    state = lines[0].split()[-1]
    if state == "unauthorized":
        fail("the Show hasn't allowed this computer yet. Look at its screen, tick 'Always allow' "
             "and tap Allow, then run this again.")
    if state != "device":
        fail("the Show is connected but says '" + state + "'. Unplug it, plug it back in and try again.")
    adb.run("root", check=False)
    adb.run("wait-for-device", timeout=60)
    time.sleep(1)
    if adb.shell("id -u") != "0":
        fail("adb root didn't work. This needs LineageOS's userdebug build, which allows it; under "
             "Settings > System > Developer options, set 'Rooted debugging' on.")
    return {
        "device": adb.shell("getprop ro.product.device"),
        "build": adb.shell("getprop ro.build.display.id"),
        "serials": [s for s in {adb.shell("getprop ro.serialno"), adb.shell("getprop ro.boot.serialno"),
                                adb.shell("cat /proc/idme/serial 2>/dev/null")} if len(s) >= 6],
    }


# ---- redaction ---------------------------------------------------------------------------------

MAC = re.compile(r"\b([0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}\b")
CID = re.compile(r"\b[0-9a-fA-F]{32}\b")
KEYED = re.compile(r"^((?:serial|mac_addr|bt_mac_addr|wifi_mac_addr)\s*=\s*).*$", re.M)
PROPS = re.compile(r"(\[(?:persist\.adb\.wifi\.guid|ro\.serialno|ro\.boot\.serialno|net\.hostname"
                   r"|persist\.sys\.device_name)\]:\s*\[)[^\]]*(\])")


def redact(text, serials):
    """Takes out what identifies this particular Show: its serial number, network and Bluetooth
    addresses, the storage chip's unique id and adb's pairing id. What's left describes the model."""
    for s in serials:
        text = text.replace(s, "<serial>")
    text = re.sub(r"(androidboot\.serialno=)\S+", r"\1<serial>", text)
    text = KEYED.sub(r"\1<removed>", text)
    text = PROPS.sub(r"\1<removed>\2", text)
    text = MAC.sub("<mac>", text)
    text = CID.sub("<id>", text)
    return text


# ---- check -------------------------------------------------------------------------------------

def cmd_check(args):
    adb = Adb(find_adb(args.adb))
    say("Looking for the Show...")
    info = connect(adb)
    say("Found: " + (info["device"] or "unknown") + ", running " + (info["build"] or "an unknown build"))
    if info["device"] != "checkers":
        fail("this doesn't say it's a checkers (1st-gen Echo Show 5). This kit is only for that model.")
    say("Root access: yes")
    say()
    say("All good. Next: python tools/checkers-kit.py backup")


# ---- backup ------------------------------------------------------------------------------------

def partitions(adb):
    """Every named partition, plus the two boot areas that hold the first-stage bootloader."""
    listing = adb.shell("ls /dev/block/platform/*/by-name 2>/dev/null || ls /dev/block/by-name")
    # The list also names the whole chip (mmcblk0), its secure area (mmcblk0rpmb, which a plain read
    # can hang on) and the two boot areas; the whole chip would copy everything twice, and the boot
    # areas are added once below.
    names = sorted(n for n in listing.split()
                   if re.fullmatch(r"[A-Za-z0-9_.-]+", n) and not n.startswith("mmcblk"))
    parts = [(n, "/dev/block/by-name/" + n) for n in names]
    if not adb.shell("ls /dev/block/by-name 2>/dev/null"):
        base = adb.shell("ls -d /dev/block/platform/*/by-name").split()[0]
        parts = [(n, base + "/" + n) for n in names]
    for extra in ("mmcblk0boot0", "mmcblk0boot1"):
        if adb.shell("ls /dev/block/" + extra + " 2>/dev/null"):
            parts.append((extra, "/dev/block/" + extra))
    return parts


def size_of(adb, dev):
    s = adb.shell("blockdev --getsize64 " + dev)
    return int(s) if s.isdigit() else 0


def human(n):
    if n >= 1e9:
        return "%.1f GB" % (n / 1e9)
    if n >= 1e7:
        return "%d MB" % (n / 1e6)
    return "%.1f MB" % (n / 1e6)


def cmd_backup(args):
    adb = Adb(find_adb(args.adb))
    info = connect(adb)
    if info["device"] != "checkers":
        fail("this doesn't say it's a checkers (1st-gen Echo Show 5).")

    parts = [(n, d) for n, d in partitions(adb) if args.with_userdata or n not in SKIP_BY_DEFAULT]
    sizes = {n: size_of(adb, d) for n, d in parts}
    total = sum(sizes.values())
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M")
    out = os.path.abspath(args.out or "checkers-backup-" + stamp)
    os.makedirs(out, exist_ok=True)
    free = shutil.disk_usage(out).free
    say("Backing up %d partitions, %s in all, to:" % (len(parts), human(total)))
    say("  " + out)
    if free < total + 500e6:
        fail("that drive has %s free, not enough. Free some space or pass --out on another drive."
             % human(free))
    if not args.with_userdata:
        say("(Leaving out userdata and cache: LineageOS's apps and settings, and scratch space. "
            "Add --with-userdata to include them.)")
    say()

    sums = []
    for i, (name, dev) in enumerate(parts, 1):
        want = sizes[name]
        say("[%d/%d] %s (%s)..." % (i, len(parts), name, human(want)))
        path = os.path.join(out, name + ".img")
        h = hashlib.sha256()
        got = 0
        with open(path, "wb") as f:
            p = subprocess.Popen([adb.path, "exec-out", "dd if=%s bs=1048576 2>/dev/null" % dev],
                                 stdout=subprocess.PIPE)
            while True:
                chunk = p.stdout.read(1 << 20)
                if not chunk:
                    break
                f.write(chunk)
                h.update(chunk)
                got += len(chunk)
            p.wait()
        if want and got != want:
            fail("%s came across short (%d of %d bytes). Check the cable and run backup again."
                 % (name, got, want))
        mine = h.hexdigest()
        theirs = adb.shell("sha256sum " + dev, timeout=900).split()
        if not theirs or theirs[0] != mine:
            fail("%s doesn't match the Show's own checksum. Check the cable and run backup again." % name)
        sums.append("%s  %s.img" % (mine, name))
        say("        copied and checked")

    with open(os.path.join(out, "SHA256SUMS"), "w") as f:
        f.write("\n".join(sums) + "\n")
    with open(os.path.join(out, "README.txt"), "w") as f:
        f.write(
            "Backup of a 1st-gen Echo Show 5 (checkers), " + stamp + ", made by TECHO5's checkers-kit.py.\n\n"
            "KEEP THIS PRIVATE. It holds this Show's own serial number, network addresses and\n"
            "factory keys. Never upload it, attach it to an issue or share it.\n\n"
            "Each partition is <name>.img; SHA256SUMS has the checksum each one was checked against.\n"
            "If you ever need to put it back, ask on the issue and we'll walk you through it.\n")
    say()
    say("Backup done: %d partitions, every one checked against the Show." % len(parts))
    say("Keep that folder somewhere safe (a second copy on a USB stick is a good idea).")
    say("It is PRIVATE: never upload or share it.")
    say()
    say("Next: python tools/checkers-kit.py test")


# ---- test --------------------------------------------------------------------------------------

GATING = "/sys/devices/platform/amazon-gating"


def cmd_test(args):
    adb = Adb(find_adb(args.adb))
    info = connect(adb)
    if info["device"] != "checkers":
        fail("this doesn't say it's a checkers (1st-gen Echo Show 5).")
    report = ["TECHO5 checkers test results, " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
              "device: " + info["device"] + ", build: " + info["build"]]

    def note(section, text):
        report.append("")
        report.append("===== " + section)
        report.append(text.rstrip())

    # 1. The hardware dump.
    say("1 of 4: reading the hardware (about a minute)...")
    dump = os.path.join(HERE, "hwdump.sh")
    if not os.path.exists(dump):
        fail("tools/hwdump.sh is missing. Download the whole repository as a ZIP (docs/windows-guide.md, step 3).")
    adb.run("push", dump, "/data/local/tmp/hwdump.sh")
    note("hardware dump", adb.shell("sh /data/local/tmp/hwdump.sh", timeout=300))
    adb.shell("rm /data/local/tmp/hwdump.sh")
    say("      done")

    # 2. The mute button and the red light.
    say()
    say("2 of 4: the mute button.")
    before = adb.shell("cat %s/state 2>&1" % GATING)
    say("      The microphones should be ON now (no red light). If the red light is on, press the")
    wait_enter("      mute button once so it goes off.")
    on = adb.shell("cat %s/state 2>&1" % GATING)
    wait_enter("      Now press the mute button once to switch the microphones OFF.")
    muted = adb.shell("cat %s/state 2>&1" % GATING)
    red = ask("      Is the red light on now?")
    wait_enter("      Press the mute button once more to switch the microphones back ON.")
    unmuted = adb.shell("cat %s/state 2>&1" % GATING)
    note("mute button", "state at start: %s\nstate with mics on: %s\nstate after pressing mute: %s\n"
                        "red light on when muted: %s\nstate after pressing again: %s"
         % (before, on, muted, "yes" if red else "no", unmuted))

    # 3. Muting from software, the way TECHO5 does, and whether only the button undoes it.
    say()
    say("3 of 4: muting from software.")
    say("      This switches the microphones off the way TECHO5 will, then checks that only the")
    say("      button can switch them back on.")
    ls = adb.shell("ls -l %s 2>&1" % GATING)
    adb.shell("printf 1 > %s/enable 2>&1" % GATING)  # what TECHO5 writes; the latch takes about a second
    time.sleep(2)
    soft = adb.shell("cat %s/state 2>&1" % GATING)
    soft_red = ask("      Is the red light on now?")
    if soft == on and not soft_red:
        # It didn't engage: the microphones are still on, so pressing the button now would mute them.
        say("      It didn't switch off from software. That's a useful answer too; moving on.")
        note("mute from software", "files: \n%s\nstate after writing 1 to enable: %s (unchanged)\n"
                                   "red light on: no\nsoftware mute did not engage" % (ls, soft))
    else:
        adb.shell("printf 0 > %s/enable 2>&1" % GATING)  # should do nothing: only the button unmutes
        time.sleep(2)
        still = adb.shell("cat %s/state 2>&1" % GATING)
        wait_enter("      Press the mute button once to switch the microphones back ON.")
        back = adb.shell("cat %s/state 2>&1" % GATING)
        back_red = ask("      Is the red light off now?")
        if not back_red:
            say("      If the red light is still on, press the mute button once more to switch the")
            say("      microphones back on.")
        note("mute from software", "files: \n%s\nstate after writing 1 to enable: %s\nred light on: %s\n"
                                   "state after writing 0 to enable (should still be muted): %s\n"
                                   "state after pressing the button: %s\nred light off after: %s"
             % (ls, soft, "yes" if soft_red else "no", still, back, "yes" if back_red else "no"))

    # 4. The camera.
    say()
    say("4 of 4: the camera.")
    wait_enter("      Make sure the camera shutter on top is OPEN (slid so the lens shows).")
    adb.shell("am start -a android.media.action.STILL_IMAGE_CAMERA")
    say("      A camera app should open on the Show (it may ask for permissions; allow them).")
    picture = ask("      Do you see a live picture from the camera?")
    colors = ask("      Do the colors look right (faces not blue, blue things not orange)?") if picture else False
    time.sleep(1)
    cam_log = adb.shell("dmesg 2>/dev/null | grep -iE 'ov9734|imgsensor|sensor_id|kd_sensorlist|seninf' | tail -40")
    adb.shell("input keyevent KEYCODE_HOME")
    note("camera", "live picture: %s\ncolours right: %s\nkernel log while the camera opened:\n%s"
         % ("yes" if picture else "no", "yes" if colors else ("n/a" if not picture else "no"), cam_log))

    text = redact("\n".join(report) + "\n", info["serials"])
    name = "checkers-results-" + datetime.datetime.now().strftime("%Y%m%d-%H%M") + ".txt"
    with open(name, "w", encoding="utf-8") as f:
        f.write(text)
    say()
    say("All done. Your results are in:")
    say("  " + os.path.abspath(name))
    say("The serial number, network addresses and other identifiers have been taken out.")
    say("Please attach that file to a comment on:")
    say("  " + ISSUE)


def main():
    ap = argparse.ArgumentParser(description="TECHO5 checkers kit (1st-gen Echo Show 5 on LineageOS).")
    ap.add_argument("--adb", help="where adb is, if it isn't found on its own")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check", help="is the Show connected, and is it a checkers?")
    b = sub.add_parser("backup", help="copy every partition to this computer, checked")
    b.add_argument("--out", help="folder to put the backup in (default: a new one here)")
    b.add_argument("--with-userdata", action="store_true", help="also back up LineageOS's apps and settings")
    sub.add_parser("test", help="the hardware dump and a few questions")
    args = ap.parse_args()
    try:
        {"check": cmd_check, "backup": cmd_backup, "test": cmd_test}[args.cmd](args)
    except KeyboardInterrupt:
        say()
        say("Stopped. Nothing was changed on the Show; you can run it again.")
        sys.exit(1)


if __name__ == "__main__":
    main()
