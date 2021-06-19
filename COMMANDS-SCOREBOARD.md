## Scoreboard Command Usage

**Scoreboards** store all the data for an overall event - all the scores on all the leaderboards. They're stored in individual config files under `scoreboards/` - one must be loaded for scoreboards to be functional!

Scoreboards divided into **divisions** - individual leaderboards with their own sets of fields players submit scores to (you would use these for multiple divisions in a tournament, like a harder song list for experienced players and an easier song list for novices.)

Each division has a number of **fields** for individual songs, games, etc. Players directly submit scores to these, and admins can later verify them.

*Formatting note: \<required argument> (optional argument) "Argument needs quotes"*

---

### General commands

 - `!scnew <"name"> (description...)` - Creates a scoreboard config
 - `!scload <"name">` - Loads a scoreboard config
 - `!scunload` - Unloads the current scoreboard config
 - `!scdisplayname <name...>` - Sets a scoreboard's display name
 - `!scdescription <desc...>` - Sets a scoreboard's description
 - `!scoreboard` - Sends the scoreboard messages to the current channel - Any new fields, scores, etc will be edited into this new message!
 
---

### Division commands

- `!scnewdiv <"name"> (description)` - Creates a new scoreboard division
- `!scremovediv <"name">` - Removes an existing scoreboard division

---

### Field commands

Scoreboards are made up of configurable fields - these are individual goals/challenges for users to compete on!

 - `scfield <"division"> <"name"> <type>` - Creates or updates a field (type argument is currently unused)
 - `scremovefield <"division"> <"name">` - Removes a field

---

### Score commands

TL;DR: Users submit scores with `!submit`, admins verify them with `!verify`

User-submitted scores are marked as unverified - they show up on the leaderboard with a ⚠ next to them.

Admins can verify a user-submitted score by running `!verify`.

Running any of these commands will (in the future) prompt the user to react to an emote to choose which field to submit their score under.

 - `!submit (score)` - Submits an unverified score for your username (can be run by non-admins)
 - `!verify <"division"> <"user"> (score)` - If `score` is specified, `user`'s score will be set to that score. Otherwise, this command will verify their unverified score (if they have one)
 - `!scremoveentry <"division"> <"user">` - Removes `user`'s score from a field.