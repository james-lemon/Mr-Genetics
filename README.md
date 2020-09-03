# Mr-Genetics
 The discord bot to blame when you realize you have terrible genes

 It also allows for discord server members to self-assign roles you configure by reacting to a message the bot sends... how neat is that?

# Command Usage:

**Note: Running any command requires you have the "admin" role! See !setadminrole for details**

## !help
DMs you a brief list of commands and how to use them

## !addrole "Category" "Role" Description
Adds a role to the role list config.
  - Category: The category to put this role under, in quotes. Will be created if it doesn't exist.
  - Role: The role to assign, in quotes. Must be a role that already exists on the server.
  - Description: The role's description (no quotes!), to be displayed on the role list. This is optional.
  
After running this command, a message is sent to confirm the addition. To confirm, react with the emote to associate with the role!

Limitations:
  - The role used for this bot's "admin" commands can't be added to the role list, nor can the server's admin roles
  - Discord limits reactions to 20 per message (afaik). Since one message is used per category in the role list, a category can't have more than 20 roles in it.
  - Any standard (unicode) emoji or any custom emoji *the bot has access to* can be used as a role emote - go wild!
  - Any individual role or emoji can't be added twice in the same category
  - Don't forget, roles in the role list can be gained by ANY server member! Don't add your moderation roles to it!


## !removerole "Category" "Role"
Like addrole, but it uhh, removes roles. Category and Role must be in quotes, like with addrole.

After sending, react to the bot's confirmation message using ❌ to confirm removal.

## !rolelist
Sends the "role list" to whatever channel you run this command in.

  - Each category is printed as a message, react with a role's emote to get that role!
  - This bot self-deletes any old role list messages, to prevent user confusion
  - Sending messages/reactions using !rolelist is intentionally slowed to appease the Discord API's rate limits

## !setadminrole "Role"
Sets the "admin" role for this bot to the specified role.

  - If this is set, users without this role can't run ANY bot commands and can only gain roles from reactions.
  - Once set, this restriction can't be removed without editing the config.
  - The bot will send a confirmation message - *Make sure you have this admin role* and confirm by reacting to it with 🔒.

## !sortcategory "Category"
Sorts the roles in "Category" by alphabetical order - Perfect for organizing your last-minute role additions!

(By default, roles are displayed on the role list in the order you added them in)


### Other notes
 - This bot doesn't ship with a bot access token (obviously), place yours in `secret-token.txt` in the same folder as `bot.py`!
 - This bot's activity message randomly cycles every 6 hours, customize them via `playing_messages.py`
