# PRestic Architecture Documentation

## Overview

PRestic is a profile manager and task scheduler for the [Restic](https://restic.net/) backup tool. It provides a unified interface for managing multiple backup configurations, scheduling automated backups, and monitoring backup tasks through both CLI and GUI interfaces.

**Version:** 0.0.2  
**License:** MIT  
**Language:** Python 3.8+  
**Repository:** https://github.com/anmcarrow/prestic-ng

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        User Interface Layer                  │
├──────────────┬──────────────────┬────────────────────────────┤
│   CLI Mode   │   GUI Mode       │   Web Interface           │
│   (prestic)  │   (prestic-gui)  │   (http://localhost:8711) │
└──────────────┴──────────────────┴────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    Handler Layer                             │
├──────────────┬──────────────────┬────────────────────────────┤
│ CommandHandler│  ServiceHandler │   KeyringHandler          │
│  (one-shot)  │  (scheduler)     │   (password mgmt)         │
└──────────────┴──────────────────┴────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    Core Components                           │
├──────────────┬──────────────────┬────────────────────────────┤
│   Profile    │   BaseHandler    │   WebRequestHandler       │
│   Manager    │   (base class)   │   (HTTP server)           │
└──────────────┴──────────────────┴────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    Restic CLI Layer                          │
│            (subprocess calls to restic binary)               │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Profile System

The `Profile` class is the foundation of PRestic's configuration management.

**Purpose:**
- Encapsulates backup configuration (repository, passwords, commands, schedules)
- Supports inheritance for DRY configuration
- Type validation and data transformation
- Dynamic property access

**Key Features:**
- **Inheritance Chain:** Profiles can inherit from other profiles
- **Type System:** Automatic type conversion (bool, int, list, size, str)
- **Property Mapping:** Remaps config keys to environment variables or restic flags
- **Schedule Parsing:** Converts human-readable schedules to datetime objects

**Configuration Options:**
```python
_options = [
    ("inherit", "list", None, []),
    ("description", "str", None, "no description"),
    ("repository", "str", "flag.repo", None),
    ("password", "str", "env.RESTIC_PASSWORD", None),
    ("password-command", "str", "env.RESTIC_PASSWORD_COMMAND", None),
    ("password-file", "str", "env.RESTIC_PASSWORD_FILE", None),
    ("password-keyring", "str", None, None),
    ("executable", "list", None, ["restic"]),
    ("command", "list", None, []),
    ("args", "list", None, []),
    ("schedule", "str", None, None),
    ("notifications", "bool", None, True),
    ("wait-for-lock", "str", None, None),
    ("cpu-priority", "str", None, None),
    ("io-priority", "str", None, None),
    ("limit-upload", "size", None, None),
    ("limit-download", "size", None, None),
    ("verbose", "int", "flag.verbose", None),
    ("option", "list", "flag.option", None),
    ("cache-dir", "str", "env.RESTIC_CACHE_DIR", None),
]
```

### 2. Handler Architecture

All handlers inherit from `BaseHandler` and implement specific execution modes.

#### BaseHandler (Abstract Base)

**Responsibilities:**
- Configuration loading from `$HOME/.prestic/config.ini`
- Profile inheritance resolution
- Task identification (profiles with both `command` and `repository`)
- State persistence to `$HOME/.prestic/status.ini`

**Methods:**
- `load_config()`: Loads and processes INI configuration
- `save_state()`: Persists task status
- `run()`: Abstract method implemented by subclasses

#### CommandHandler

**Purpose:** Execute one-time restic commands

**Usage:**
```bash
prestic -p profile-name [restic-command] [args...]
```

**Flow:**
1. Load configuration
2. Build restic command from profile + CLI args
3. Execute command via subprocess
4. Return exit code

#### ServiceHandler

**Purpose:** Background service with task scheduler and GUI

**Features:**
- **Task Scheduling:** Cron-like schedule parsing and execution
- **System Tray GUI:** pystray integration with dynamic menu
- **Web UI:** Built-in HTTP server on port 8711
- **Notifications:** Desktop notifications for task completion
- **Log Management:** Automatic log rotation based on `prune-logs-after`
- **Process Priority Control:** CPU and I/O priority management

**Threads:**
- `proc_scheduler`: Task scheduling loop
- `proc_webui`: HTTP server thread
- `pystray.run()`: GUI event loop (main thread)

**Scheduling Algorithm:**
```python
# Parse schedule: "daily at 23:59", "monthly at 03:00", "mon,tue at 12:00"
# Calculate next_run datetime
# Sort tasks by next_run
# Sleep until next task
# Execute task
# Recalculate next_run
```

#### KeyringHandler

**Purpose:** Secure password storage using OS keyring

**Operations:**
- `get <name>`: Retrieve password from keyring
- `set <name>`: Store password in keyring
- `del <name>`: Remove password from keyring

**Integration:**
- Uses Python `keyring` library
- Stores under application name "prestic"
- Referenced in profiles via `password-keyring = name`

### 3. Web Interface

**Component:** `WebRequestHandler` (extends `BaseHTTPRequestHandler`)

**Endpoints:**
- `/` - Profile list
- `/profile/<name>` - Profile details
- `/profile/<name>/snapshots` - Snapshot browser
- `/profile/<name>/file/<snapshot>/<path>` - File viewer
- `/profile/<name>/diff/<snapshot>/<path>` - Diff viewer

**Features:**
- Read-only access to restic data
- Snapshot browsing with file tree
- File diff visualization
- No authentication (localhost only)

### 4. GUI System

**Technology:** pystray (system tray icon library)

**Components:**
- **Icon States:** normal, busy (black overlay), fail (red overlay)
- **Dynamic Menu:** Generated from active tasks
- **Menu Items:**
  - Task list with next/last run times
  - Run Now action per task
  - Open Web Interface
  - Open prestic folder
  - Reload config
  - Quit

**Platform Support:**
- **Linux:** AppIndicator3 required (`gir1.2-appindicator3-0.1`)
- **macOS:** Notification permissions required
- **Windows:** Native system tray support

## Data Flow

### Configuration Loading

```
config.ini
    ↓
ConfigParser.read()
    ↓
Profile objects created
    ↓
Inheritance resolution
    ↓
Task list generated (profiles with command + repository)
    ↓
Handler.run()
```

### Task Execution

```
Scheduler wake up
    ↓
Identify next task
    ↓
Build restic command
    ↓
Apply CPU/IO priority
    ↓
Execute subprocess
    ↓
Capture output to log file
    ↓
Monitor execution
    ↓
Update status.ini
    ↓
Send notification (if enabled)
    ↓
Prune old logs
    ↓
Calculate next run time
```

### Password Resolution

Priority order:
1. `password-keyring` → OS keyring
2. `password-command` → Execute command
3. `password-file` → Read from file
4. `password` → Plain text (not recommended)

## File Structure

```
$HOME/.prestic/
├── config.ini          # User configuration
├── status.ini          # Task state (last run, PIDs, etc.)
└── logs/              # Task execution logs
    └── YYYY.MM.DD_HH.MM-taskname.txt

/path/to/installation/
├── prestic/
│   ├── __init__.py
│   ├── prestic.py      # Main application
│   ├── icon.png        # Normal tray icon
│   └── icon-run.png    # Running tray icon
├── pyproject.toml      # Build configuration
└── README.md
```

## Configuration Format

INI-based configuration with inheritance support:

```ini
[base-profile]
repository = /path/to/repo
password-file = /path/to/password

[daily-backup]
inherit = base-profile
schedule = daily at 02:00
command = backup
args = /path/to/data
```

**Special Keys:**
- `inherit`: Single profile or list of profiles to inherit from
- `schedule`: Cron-like schedule string
- `command`: Default restic command to execute
- `args`: Arguments for the command (multi-line list)
- `env.*`: Environment variables passed to restic
- `flag.*`: Restic CLI flags

## Process Management

### Priority Control

**CPU Priority:**
- `idle`, `low`, `normal`, `high`
- Uses `nice` on Unix, `SetPriorityClass` on Windows

**I/O Priority:**
- `idle`, `low`, `normal`, `high`
- Uses `ionice` on Linux

### Lock Handling

**wait-for-lock:** Retry interval in seconds when repository is locked
- Implements exponential backoff
- Monitors lock age
- Can trigger `restic unlock` for stale locks

## Logging

**Log Files:**
- Location: `$HOME/.prestic/logs/`
- Format: `YYYY.MM.DD_HH.MM-taskname.txt`
- Content: Full restic output (stdout + stderr)

**Log Rotation:**
- Configured per-task via `prune-logs-after = N` (days)
- Automatic cleanup after task completion
- Keeps logs for failed tasks

## Security Considerations

1. **Password Storage:**
   - Keyring integration recommended
   - Password files should have restricted permissions (0600)
   - Plain text passwords in config not recommended

2. **Web Interface:**
   - Listens on localhost only (127.0.0.1)
   - No authentication
   - Read-only access

3. **File Permissions:**
   - Config directory: `$HOME/.prestic/` (user-only access)
   - Log files: readable by user only
   - Status file: tracks running PIDs (sensitive)

## Extension Points

### Adding New Handlers

Extend `BaseHandler` and implement:
```python
class CustomHandler(BaseHandler):
    def run(self, profile, args=[]):
        # Your logic here
        pass
```

### Adding New Profile Options

Add to `Profile._options`:
```python
("new-option", "datatype", "env.VAR_NAME", default_value)
```

### Custom Schedule Formats

Modify `Profile.parse_schedule()` to support new formats.

## Dependencies

**Required:**
- Python 3.8+
- `restic` binary (external)

**Optional:**
- `pystray` - System tray GUI
- `pillow` - Image processing for tray icons
- `keyring` - Secure password storage

## Build & Distribution

**Build System:** setuptools with PEP 517 support

**Entry Points:**
- `prestic` - CLI command (console_scripts)
- `prestic-gui` - GUI launcher (gui_scripts)

**Package Contents:**
- Python module: `prestic/`
- Icons: `icon.png`, `icon-run.png`
- Configuration: `pyproject.toml`

## Testing Strategy

**Manual Testing:**
1. Configuration validation
2. Schedule parsing
3. Task execution
4. GUI functionality
5. Web interface

**Future Improvements:**
- Unit tests for Profile class
- Integration tests for handlers
- Mock restic for testing
- Automated UI testing

## Performance Considerations

1. **Scheduler Sleep:** 1-second wake intervals for schedule checks
2. **Log Rotation:** Performed after each task completion
3. **Profile Inheritance:** Resolved once at startup
4. **Web UI:** Lazy-loaded restic data (no caching)

## Known Limitations

1. **No Parallel Execution:** Tasks run sequentially
2. **Single Repository per Task:** Can't backup to multiple repos in one task
3. **Static Configuration:** Requires restart for config changes (except via "Reload" in GUI)
4. **No Task Dependencies:** Can't specify task execution order
5. **Hourly Minimum:** Schedule granularity is 1 minute

## Future Development

Potential enhancements:
- Parallel task execution
- Task dependencies
- Configuration hot-reload
- Email notifications
- Backup verification checks
- Repository statistics dashboard
- Multi-repository tasks
- Plugin system for custom handlers

## Troubleshooting

**Common Issues:**

1. **GUI not appearing (Linux):**
   - Install `gir1.2-appindicator3-0.1`
   - Check `~/.local/bin` in PATH

2. **Tasks not running:**
   - Check `$HOME/.prestic/status.ini` for errors
   - Verify schedule format
   - Check log files in `$HOME/.prestic/logs/`

3. **Password not working:**
   - Verify keyring is set up: `prestic --keyring get <name>`
   - Check file permissions on password files
   - Test password-command manually

4. **Web UI not accessible:**
   - Verify port 8711 is not in use
   - Check firewall settings
   - Ensure service is running: check system tray icon

## Contributing

When contributing to PRestic, please:
1. Follow PEP 8 style guidelines
2. Add docstrings to new functions
3. Test on multiple platforms if possible
4. Update this documentation for architectural changes
5. Consider backward compatibility with existing configs

## License

MIT License - See LICENSE file for details
