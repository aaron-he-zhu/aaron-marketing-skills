# Scheduled Runs — episodic cadence for always-on disciplines

The L2 channel disciplines are "always-on", but the bundle itself runs only when a
host session runs it. This page is the bridge: OS-level schedulers that wake an
agent session on a cadence, run one monitoring-class skill, and leave durable truth
as **proposals** for the next owner ritual. Nothing here grants new authority —
a scheduled session is still an agent session:

- registry writes stay `operation: propose`; canonical acceptance remains the
  owner-run terminal step in [registry-event-protocol.md](registry-event-protocol.md);
- auditors return `NOT_SCORED` when the deterministic runtime is unavailable;
- network-mutating connectors (`resend.py`, `indexpush.py`) stay dry-run unless `--live`
  is deliberately configured — never put `--live` into an unattended schedule.

## What to schedule (and what not to)

Schedule **monitoring/evaluate-class** skills — read-mostly, proposal-producing:

| Cadence | Example skills |
|---------|----------------|
| Daily | `inbox-placement-monitor`, `budget-pacing-monitor`, `deliverability-qa` |
| Weekly | `rank-tracker`, `performance-monitor`, `social-pulse-monitor`, `competitor-tracker` |
| Monthly | `domain-authority-auditor`, `content-quality-auditor` (gates), `memory-management` archive review |

Do **not** schedule builders (publication-shaped output), registry owners (owner
ritual is human), or anything whose first action is an external side effect. A
scheduled run that hits an authority boundary stops and surfaces `NEEDS_INPUT` —
that is the contract working, not a failure.

## Cron (Linux / macOS)

Create the private log directory once before installing either scheduler. Pre-create
the files at mode `0600`, and keep the scheduler umasks below so deleted or rotated
files are also recreated privately:

```bash
install -d -m 700 "$HOME/.local/log"
touch "$HOME/.local/log/aaron-rank-tracker.log" \
  "$HOME/.local/log/aaron-monitor.log" \
  "$HOME/.local/log/aaron-monitor.err"
chmod 600 "$HOME/.local/log"/aaron-*.log
```

```cron
# Weekly rank tracking, Mondays 07:30 — proposals only, log to a private file.
30 7 * * 1  umask 077 && cd /path/to/project && /usr/local/bin/claude -p \
  "Run rank-tracker for our priority keywords; save results as a WARM artifact and submit any durable truth as registry proposals." \
  >> "$HOME/.local/log/aaron-rank-tracker.log" 2>&1
```

## launchd (macOS)

`~/Library/LaunchAgents/com.aaron.marketing.weekly-monitor.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>com.aaron.marketing.weekly-monitor</string>
  <key>ProgramArguments</key>
  <array>
    <string>/usr/local/bin/claude</string>
    <string>-p</string>
    <string>Run performance-monitor on the last 7 days; save a WARM artifact; proposals only.</string>
  </array>
  <key>WorkingDirectory</key><string>/path/to/project</string>
  <!-- launchd uses decimal integers: 63 is octal 077. -->
  <key>Umask</key><integer>63</integer>
  <key>StartCalendarInterval</key>
  <dict><key>Weekday</key><integer>1</integer><key>Hour</key><integer>7</integer><key>Minute</key><integer>45</integer></dict>
  <key>StandardOutPath</key><string>/Users/you/.local/log/aaron-monitor.log</string>
  <key>StandardErrorPath</key><string>/Users/you/.local/log/aaron-monitor.err</string>
</dict>
</plist>
```

```bash
launchctl load ~/Library/LaunchAgents/com.aaron.marketing.weekly-monitor.plist
```

## The loop closes in the next interactive session

Scheduled runs produce proposals; the owner ritual resolves them. Two existing
signals keep that queue visible instead of silently stalling:

- the SessionStart hook reports **pending-proposal intake age** (nudges when the
  oldest verifiable pending proposal exceeds 14 days), **projection health**
  (behind/missing/invalid/ahead), and unverifiable event streams;
- `python3 "$AARON_SKILLS_ROOT/scripts/registry-events.py" pending` gives the same
  report on demand, per registry, read-only (resolve `AARON_SKILLS_ROOT` per
  [runtime-invocation.md](runtime-invocation.md)).

A healthy cadence is therefore: scheduled monitors propose → next session surfaces
the queue → owner ritual accepts/rejects → projections rebuild → the next monitor
reads fresh state.

If a validated FIX audit is tracked by [`audit-loop.py`](../scripts/audit-loop.py), a scheduler may perform only read-only verification or retry bookkeeping already authorized by the loop protocol. It must not synthesize owner approval, perform the proposed intervention, attach unobserved evidence, or run with an external-mutation capability. `retry_not_before` is a scheduling hint, not permission; owner review and intervention remain explicit inputs, and re-audit must validate a new artifact before the loop can converge. A missing event-anchored step is recovered only by replaying the same original mutation request; the public `run-events.py loop-step` command is verification-only. When a scheduled run pauses, waiting/needs-input/blocked envelopes require exact selected-ancestry loop coverage and may retain active loops; failed/aborted unresolved closure preserves bounded failure evidence only, while the final event slot remains reserved for terminal sealing.
