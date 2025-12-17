# __README NOW IS UNDER ACTIVE REFACTORING__

# PRestic
PRestic is a profile manager and task scheduler for [Restic](https://restic.net/) CLI backup tool. It works on all
operating systems when you can run Python an Restic itself but GUI features and keyring functionality may vary by a platform. It can do anything that Restic can but in a way of a single-source planner with INI-style configuration. You can use it with or without GUI, for your a desktop, home server or VDS. 

![MacOS 15 build](./assets/screenshot.png)

# Installation

## Installing Restic CLI

You should [install Restic CLI](https://restic.readthedocs.io/en/stable/020_installation.html) before using PRestic. 
For this task you usually can use your package manager (apt, yum, pacman, brew, etc.) 

## Pip-package deploying
1. Install Python 3.10+ and [pip](https://pip.pypa.io/en/stable/installing/). 
2. Execute `pip install http://github.com/anmcarrow/prestic-ng/tarball/master#egg=prestic` in terminal.

_Note: On Ubuntu you need to [add ~/.local/bin to your path](https://bugs.launchpad.net/ubuntu/+source/bash/+bug/1588562)
 if needed and run `sudo apt install gir1.2-appindicator3-0.1` for the gui to work._

## File-based method
1. Install Python
2. Install `pystray` and `pillow` python packages
3. Get the content of [prestic](./prestic/) directory.
4. Execute the `prestic/prestic.py` script.

_Note: If you prefer you can also add `prestic.py`  in your PATH variable for faster execution._

## Static builds
TBD

## MacOS Usage
To have a notifications on MacOS you should allow the from-scripts-notifications in your security center (see [the thread here](https://forum.latenightsw.com/t/trying-to-use-terminal-for-display-notification/5068)). 

![Macos Script Notifications](./assets/macos_notify_settings.png)

### Start Prestic on login
- Windows: Put a link to `prestic-gui.exe` in your `Startup` folder (run `where prestic-gui` to locate it if needed)
- Linux: Add command `prestic --gui` to your startup applications (run `which prestic-gui` to locate it if needed)
- MacOS: TBD

# Usage
- Run profile-defined default command: `prestic -p profilename`
- Run any restic command on profile: `prestic -p profilename snapshots`
- Start gui and scheduler: `prestic --gui`
- Start scheduler only: `prestic --service`

## Keyring
The keyring allows you to let your operating system store repository passwords encrypted in your
user profile. This is the best password method if it is available to you.

To use, add `password-keyring = <name>` to your prestic profile, where `<name>` can be anything you
want to identify that password. Then to set a password run the following command:
`prestic --keyring set <name>`.


# Configuration file
Configuration is stored in $HOME/.prestic/config.ini. The file consists of profile blocks. You can use a
single block or split in multiple blocks through inheritance. For example one profile could contain
the repository configuration and then another one inherits from it and adds the backup command.

Lists can span multiple lines, as long as they are indented deeper than the first line of the value.

````ini
# default is the profile used when no -p is given (it is optional)
[default]
inherit = my-profile # A single inherit can be used as an alias

[my-profile]
# (string) human-redable description:
description =
# (list) inherit options from other profiles
inherit =
# (string) Run this profile periodically (will do nothing if command not set)
# Format is: `daily at 23:59` or `monthly at 23:59` or `mon,tue,wed at 23:59`. Hourly is also possible: `daily at *:30`
schedule =
# (bool) controls non-essential notifications (errors are always shown)
notifications = on
# (string) sets cpu priority (idle, low, normal, high)
cpu-priority =
# (string) sets disk io priority (idle, low, normal, high)
io-priority =
# (int) Time to wait and retry if the repository is locked (seconds)
wait-for-lock =

# (string) repository uri
repository = sftp:user@domain:folder
# (string) repository password (plain text)
password =
# (string) repository password (retrieve from file)
password-file =
# (string) repository password (retrieve from command)
password-command =
# (string) repository password (retrieve from OS keyring/locker)
password-keyring =
# (int) limits downloads to a maximum rate in KiB/s
limit-download =
# (int) limits uploads to a maximum rate in KiB/s
limit-upload =
# (string) path to restic executable (you may add global flags too)
executable = restic
# (string|list) default restic command to execute (if none provided):
command =
# (list) restic arguments for default command
args =
# (int) be verbose (specify level 0-3)
verbose =
# (regex) ignore lines matching this expression when writing log files
log-filter = ^unchanged\s/

# (string) set the cache directory
cache-dir =

# (string) environment variables can be set:
env.AWS_ACCESS_KEY_ID = VALUE
env.AWS_SECRET_ACCESS_KEY = VALUE

# (string) other flags can be set:
flag.json = true
flag.new-restic-flag = value

````

### Simple configuration example
````ini
[my-repo]
description = USB Storage
repository = /media/backup
password-keyring = my-repo

[my-backup]
description = Backup to USB Storage
inherit = my-repo
schedule = daily at 12:00

# prunning old job logs after N days
prune-logs-after = 14

command = backup
args =
    /home/user/folder1
    /home/user/folder2
    --iexclude="*.lock"

# Where the my-backup profile will run daily at 12:00
# You can also issue manual commands:
# prestic -p my-backup
# prestic -p my-repo list snapshots
# prestic -p my-backup list snapshots # this overrides my-backup's command/args but not global-flags
````
