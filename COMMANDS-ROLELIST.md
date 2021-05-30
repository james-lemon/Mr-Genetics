## Rolelist Command Usage:

### !addrole "Category" "Role" Description
Adds a role to the role list config that can be obtained by ANYONE!

Users can react using this role's emote (set after running the command) to get that role - **DO NOT add roles using !addrole with permissions you don't want normal users to have!**
  - Category: The category to put this role under, in quotes. Will be created if it doesn't exist.
  - Role: The role to assign, in quotes. Must be a role that already exists on the server.
  - Description: The role's description (no quotes!), to be displayed on the role list. This is optional.
  
After running this command, a message is sent to confirm the addition. To confirm, react with the emote to associate with the role!

Limitations:
  - The role used for this bot's "admin" commands can't be added to the assignable role list, nor can the server's admin roles (for these, use !adddisprole)
  - Discord limits reactions to 20 per message (afaik). Since one message is used per category in the role list, a category can't have more than 20 roles in it.
  - Any standard (unicode) emoji or any custom emoji *the bot has access to* can be used as a role emote - go wild!
  - Any individual role or emoji can't be added twice in the same category
  - Don't forget, roles in the role list can be gained by ANY server member! Don't add your moderation roles to it!

---

### !adddisprole "Category" "Role" Description
Adds a display role - These roles show up in the role list (like with addrole), but CANNOT BE OBTAINED using reactions!

Useful if you want your admin roles displayed in the role list, but don't want users to be able to get free admin by adding a reaction :P

Limitations are the same as with !addrole, with the exception that server and bot admin roles can be used.

---

### !editrole "Category" "Role" Description
Removes and re-adds an existing role entry with new values, like a shortcut to... manually removing and re-adding a role.

---

### !removerole "Category" "Role"
Like addrole, but it uhh, removes roles. Category and Role must be in quotes, like with addrole.

After sending, react to the bot's confirmation message using ❌ to confirm removal.

Note: If you remove the last role in a category, that category is automatically removed as well.

---

### !rolelist
Sends/updates the "role list" to whatever channel you run this command in.

  - Each category is printed as a message, react with a role's emote to get that role!
  - If a category's message already exists, that message is edited with the current roles/reactions for that category
  - If a category's message doesn't exist, a new one is sent in the channel you run this command in
  - Sending messages/reactions using !rolelist is intentionally slowed to appease the Discord API's rate limits

---

### !newrolelist
Deletes the old role list messages and sends new ones to whatever channel you run this command in.

---

### !altrolemsg "Category" "Role" "Message ID"
Each category can have an extra "rolelist" message associated with it, where reactions for roles are listened to.
This is useful for integrating "react for role" functionality into messages not created by the duck.
To use: Shift + Right click a message in discord -> Copy ID. Use this string for the "Message ID" argument.

---

### !sortcategory "Category"
Sorts the roles in "Category" by alphabetical order - Perfect for organizing your last-minute role additions!

(By default, roles are displayed on the role list in the order you added them in)

---

### !setcategorydescription "Category" Description
Sets a category's description. Note that the category's name is in quotes, and the description isn't.

This field is optional, and placeholder text is used if this isn't set (or is set to a blank value)