## Scoreboard Command Usage

Scoreboards are stored in individual config files under `scoreboards/` - one must be loaded for scoreboards to be functional!

*Formatting note: \<required argument> (optional argument) "Argument needs quotes"*

---

### General commands

 - `!scnew <"name"> (description...)` - Creates a scoreboard config
 - `!scload <"name">` - Loads a scoreboard config
 - `!scunload` - Unloads the current scoreboard config
 - `!scdisplayname <name...>` - Sets a scoreboard's display name
 - `!scdescription <desc...>` - Sets a scoreboard's description
 - `!scoreboard` - Sends the scoreboard message to the current channel - Any new fields, scores, etc will be edited into this new message!
 
---

### Field commands

Scoreboards are made up of configurable fields - these are individual goals/challenges for users to compete on!

 - `scfield <name> <type>` - Creates or updates a field (type argument is currently unused)
 - `scremovefield <name>` - Removes a field

---

### Score commands

TL;DR: Users submit scores with `!submit`, admins verify them with `!verify`

User-submitted scores are marked as unverified - they show up on the leaderboard with a ⚠ next to them.

Admins can verify a user-submitted score by running `!verify`.

Running any of these commands will (in the future) prompt the user to react to an emote to choose which field to submit their score under.

 - `!submit (score)` - Submits an unverified score for your username (can be run by non-admins)
 - `!verify <user> (score)` - If `score` is specified, `user`'s score will be set to that score. Otherwise, this command will verify their unverified score (if they have one)
 - `!scremoveentry <user>` - Removes `user`'s score from a field.