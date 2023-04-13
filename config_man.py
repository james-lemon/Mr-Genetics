#!/usr/bin/python

# --
# config_man.py - Rolelist configuration-related functions
# --


from pyexpat import ExpatError
from xml.dom import minidom
from xml.dom.minidom import parse
import xml.dom.minidom
import codecs
import sys


# The config is organized like this:
# <config>
#   <admin_role>admin role id</admin_role>
#   <scoreboard>Default scoreboard to load</scoreboard>
#   <category name="Category name", listeningChannel="channel ID", listeningMessage="message ID", altChannel="channel ID", altMessage="message ID", altRole="Role id", description="optional description">
#       <role name="Role id" dispName="Role display name" emoji="Unicode emoji/Custom emoji name" usesCustomEmoji="True/False", assignable="True/False">Role Description</role>
#       <role>...
#   </category>
#   <category>...
# </config>

print("Initializing config_man...")


def save_config():
    file = codecs.open("config.xml", "w", "utf_8_sig")
    file.write(config.toxml(encoding="utf-8").decode("utf-8"))
    #config.writexml(file, addindent="\t", newl="\n", encoding="utf-8")
    file.close()
    get_categories()


# Sets the categories variable to a dict containing all categories as keys, and the channel/message IDs to listen on as values
def get_categories():
    global categories, categoriesAlt
    ret = {}  # Why?
    retAlt = {}

    configCategories = config.getElementsByTagName("category")  # First iterate through all the categories in the file...
    for category in configCategories:
        if category.hasAttribute("name"):  # Check if this category has a name
            if category.hasAttribute("listeningChannel") and category.hasAttribute("listeningMessage"):  # If it also has a channel/message to listen for, add them too
                ret[category.getAttribute("name")] = category.getAttribute("listeningChannel") + ";" + category.getAttribute("listeningMessage")

                if category.hasAttribute("altChannel") and category.hasAttribute("altMessage"):  # If this category also has an alt message specified, add it to the alt categories as well
                    retAlt[category.getAttribute("name")] = category.getAttribute("altChannel") + ";" + category.getAttribute("altMessage")

            else:  # Otherwise, set the channel/message fields to -1
                print("Category", category.getAttribute("name"), "doesn't have listeningMessage/Channel attributes (and thus can't track a message for reactions to assign these roles!)\nRun the role list command to generate a role list message to fix this!")
                ret[category.getAttribute("name")] = "-1;-1"
        else:
            print("Config warning: Category in config is missing a name and won't be loaded!")
    categories = ret
    categoriesAlt = retAlt


# Returns a dict with all of the categories in the config and their descriptions (or some placeholder text, if they don't have one)
def get_category_descriptions():
    global categories
    ret = {}

    configCategories = config.getElementsByTagName("category")  # First iterate through all the categories in the file...
    for category in configCategories:
        if category.hasAttribute("name"):  # Check if this category has a name
            if category.hasAttribute("description"):  # Now check if it has a description
                desc = category.getAttribute("description")  # Categories with blank descriptions should use placeholder text, otherwise just return the description
                ret[category.getAttribute("name")] = desc if desc != "" else "React with these emotes to get roles!"
            else:  # No description attribute in the config? Also use some placeholder text
                ret[category.getAttribute("name")] = "React with these emotes to get roles!"
    return ret


# Returns a dict of all roles in a category and their descriptions
def get_roles(category):
    global categories
    ret = {}
    if category in categories:  # If the category we're requesting is in our valid categories list, find that category in the config
        for configCategory in config.getElementsByTagName("category"):
            if configCategory.hasAttribute("name") and configCategory.getAttribute("name") == category:  # Found the category element, now grab the roles from it
                for configRole in configCategory.getElementsByTagName("role"):
                    ret[configRole.getAttribute("name")] = configRole.firstChild.nodeValue if configRole.hasChildNodes() else ""  # Grab this role from the config and its description (or "" if no description is saved), then add it to the dict to return
        return ret

    else:
        print("Error: Attempt to get roles from non-existent category \"", category, "\"")
        return False


# Alternate version of get_roles to grab the emojis used for each role
def get_roles_emoji(category):
    global categories
    ret = {}
    if category in categories:  # If the category we're requesting is in our valid categories list, find that category in the config
        for configCategory in config.getElementsByTagName("category"):
            if configCategory.hasAttribute("name") and configCategory.getAttribute("name") == category:  # Found the category element, now grab the roles from it

                for configRole in configCategory.getElementsByTagName("role"):
                    if configRole.hasAttribute("name") and configRole.hasAttribute("emoji") and configRole.hasAttribute("usesCustomEmoji") and configRole.hasAttribute("assignable") and configRole.getAttribute("assignable") == "True":  # Only add roles with a name, emoji and assignable="True" set
                        ret[configRole.getAttribute("name")] = [configRole.getAttribute("emoji"), configRole.getAttribute("usesCustomEmoji")]  # Grab this role from the config and its emoji (if it has both attributes), then add it to the dict to return
        return ret

    else:
        print("Error: Attempt to get roles from non-existent category \"", category, "\"")
        return False


# Alternate version of get_roles_emoji to grab the emoji used the role for a category's alt message
def get_alt_role_emoji(category):
    global categoriesAlt
    ret = {}
    if category in categories:  # If the category we're requesting is in our valid categories list, find that category in the config
        for configCategory in config.getElementsByTagName("category"):
            if configCategory.hasAttribute("name") and configCategory.getAttribute("name") == category and configCategory.hasAttribute("altRole"):  # Found the category element, now grab the roles from it

                for configRole in configCategory.getElementsByTagName("role"):
                    if configRole.hasAttribute("name") and configRole.getAttribute("name") == configCategory.getAttribute("altRole") and configRole.hasAttribute("emoji") and configRole.hasAttribute("usesCustomEmoji") and configRole.hasAttribute("assignable") and configRole.getAttribute("assignable") == "True":  # Only add roles with a name, emoji and assignable="True" set
                        ret[configRole.getAttribute("name")] = [configRole.getAttribute("emoji"), configRole.getAttribute("usesCustomEmoji")]  # Grab this role from the config and its emoji (if it has both attributes), then add it to the dict to return
        return ret

    else:
        print("Error: Attempt to get alt role from non-existent alt category \"", category, "\" - does this category have an alt message/role set?")
        return False


# Returns whether a role can be assigned via reactions
def is_role_assignable(category, role):
    global categories
    if category in categories:  # If the category we're requesting is in our valid categories list, find that category in the config
        for configCategory in config.getElementsByTagName("category"):
            if configCategory.hasAttribute("name") and configCategory.getAttribute("name") == category:  # Found the category element, now grab the roles from it

                for configRole in configCategory.getElementsByTagName("role"):
                    if configRole.hasAttribute("name") and configRole.getAttribute("name") == str(role):  # Found le role
                        return configRole.hasAttribute("assignable") and configRole.getAttribute("assignable") == "True"  # Return whether this role both has the "assignable" attribute and if that attribute is true

    else:
        print("Error: Attempt to get role from non-existent category \"", category, "\"")
        return False


# Adds a role (and category, if the specified one doesn't exist) to the config
def add_role(category, role, dispName, emoji, description, isCustomEmoji, assignable):
    if category not in categories:  # Check if the specified category doesn't exist
        if add_category(category) is False:  # Try adding it! If that fails, the program is mega derped and we should return
            print("Failed to add role", role, ": Category \"", category, "\"doesn't exist and was unable to be added.\n\nThis probably shouldn't happen.")
            return "Failed to add role: Category \"", category, "\"doesn't exist and was unable to be added.\n\nThis probably shouldn't happen."

    for emote in get_roles_emoji(category).values():
        if emote[0] == emoji and assignable:
            print("Failed to add role: Emote " + emoji + " is already used for another role in this category!")
            return "Failed to add role: Emoji " + emoji + " is already used for another role in this category!"

    for category_element in config.getElementsByTagName("category"):  # Now go and add this role to the category
        category_name = category_element.getAttribute("name")
        if category_name is not None and category_name == category:
            config_role = dom.createElement("role")  # Create the role element (<role>)
            config_role.setAttribute("name", role)
            config_role.setAttribute("dispName", dispName)
            config_role.setAttribute("emoji", emoji if assignable else "")
            config_role.setAttribute("usesCustomEmoji", str(isCustomEmoji))
            config_role.setAttribute("assignable", str(assignable))
            config_role.appendChild(dom.createTextNode(description))  # Finally, set the text for it (the description)
            category_element.appendChild(config_role)  # Then add it to the category (should at this point be <role name="role name", emoji="emoji name">description</role>
            save_config()
            print("Added role", str(role), "to category", category, "(emoji:", emoji, ", desc: \"", description, "\")")
            return True

    print("Failed to add role", str(role), "to category", category, ": Unable to find category to add role to. This should never happen.")
    return "Unable to find category to add role to.\n\nThe category should've been automagically added, so this should never happen."


# Removes a role from the config
def remove_role(category, role):
    if category not in categories:  # The specified category doesn't exist
        print("Failed to remove role \"", role, "\": Category \"", category, "\"doesn't exist!")
        return "Failed to remove role: Category \"", category, "\"doesn't exist!"

    for category_element in config.getElementsByTagName("category"):  # Now go and add this role to the category
        category_name = category_element.getAttribute("name")
        if category_name is not None and category_name == category:
            for role_element in category_element.getElementsByTagName("role"):
                if role_element.hasAttribute("name") and role_element.getAttribute("name") == role:  # Found the role to delete, delete it!
                    category_element.removeChild(role_element)
                    print("Removed role", str(role), "from category", category)
                    if len(category_element.getElementsByTagName("role")) < 1:  # No other roles in this category, also remove the now-empty category
                        ret = [-1, -1]
                        if category_element.hasAttribute("listeningChannel") and category_element.hasAttribute("listeningMessage"):  # Did this category get assigned a rolelist message?
                            ret[0] = int(category_element.getAttribute("listeningChannel"))
                            ret[1] = int(category_element.getAttribute("listeningMessage"))
                        else:  # No message, set the message id to return to -1
                            ret[0] = -1
                            ret[1] = -1
                        config.removeChild(category_element)
                        print("Removed now empty category " + category)
                        save_config()
                        return ret
                    save_config()
                    return True

    print("Failed to remove role", str(role), "from category", category, ": Unable to find category or role.")
    return "Failed to remove role: Unable to find role or category in config."


# Adds a category to the config if it doesn't already exist
def add_category(category):
    for category_element in config.getElementsByTagName("category"):  # Check for duplicate categories
        category_name = category_element.getAttribute("name")
        if category_name is not None and category == category_name:
            print("Duplicate category", category, "could not be added")
            return False

    config_category = dom.createElement("category")
    config_category.setAttribute("name", category)
    config.appendChild(config_category)
    get_categories()  # Don't forget to refresh the category/message dict!
    print("Created category", category)
    return True


# Sets the message and channel ids for a category in the config
def set_category_message(category, channel_id, message_id):
    global categories
    categories[category] = channel_id + ';' + message_id
    for configCategory in config.getElementsByTagName("category"):
        if configCategory.hasAttribute("name") and configCategory.getAttribute("name") == category:
            configCategory.setAttribute("listeningChannel", channel_id)
            configCategory.setAttribute("listeningMessage", message_id)
    # Note: Config saving isn't done here, but instead in the rolelist command handler (since we're probably gonna be updating multiple config entries at once)


# Sets the description of a category
def set_category_description(category, description):
    global categories
    if category in categories:
        for configCategory in config.getElementsByTagName("category"):
            if configCategory.hasAttribute("name") and configCategory.getAttribute("name") == category:
                configCategory.setAttribute("description", description)
                print("Set description of category \"" + category + "\" to \"" + description + "\"")
                return "Set description of category \"" + category + "\" to \"" + description + "\""
    else:
        print("Failed to set category description: Category \"", category, "\"doesn't exist!")
        return "Failed to set category description: Category \"", category, "\"doesn't exist!"

    save_config()


# Sets the message and channel ids for a category in the config
def set_category_alt_message(category, channel_id, message_id, role):
    global categoriesAlt
    categoriesAlt[category] = channel_id + ';' + message_id
    for configCategory in config.getElementsByTagName("category"):
        if configCategory.hasAttribute("name") and configCategory.getAttribute("name") == category:
            configCategory.setAttribute("altChannel", str(channel_id))
            configCategory.setAttribute("altMessage", str(message_id))
            configCategory.setAttribute("altRole", str(role.id))
            save_config()
            print("Set category \"" + category + "\"'s alt rolelist message for role\"" + role.name + "\"")
            return "Set category \"" + category + "\"'s alt rolelist message for role\"" + role.name + "\""
    print("Failed to set category alt rolelist message: Category \"", category, "\"doesn't exist!")
    return "Failed to set category alt rolelist message: Category \"", category, "\"doesn't exist!"


# Sorts roles in a category by alphabetical order
def sort_category(category):
    if category in categories:  # Find this category in the config
        for configCategory in config.getElementsByTagName("category"):
            if configCategory.hasAttribute("name") and configCategory.getAttribute("name") == category:  # Now sort the roles from the category: Janky-style because documentation wasn't easy to find!
                configRoles = configCategory.getElementsByTagName("role")  # First: Grab the roles and sort them alphabetically based on the role's display name
                configRoles.sort(key=lambda x: str(x.attributes["dispName"].value))
                for node in configCategory.childNodes:  # Then, remove this category's child nodes in the config...
                    configCategory.removeChild(node)

                for role in configRoles:  # Finally, re-add the sorted roles and save the config
                    configCategory.appendChild(role)
                save_config()
        return "Sorted category \"" + category + "\" by alphabetical order"
    else:
        print("Failed to sort category: Category \"", category, "\"doesn't exist!")
        return "Failed to sort category: Category \"" + category + "\"doesn't exist!"


# Returns text inside the first "admin_role" element
def get_admin_role():
    elements = config.getElementsByTagName("admin_role")
    if len(elements) >= 1:
        role = elements[0].firstChild.nodeValue
        if role is not None:
            return int(role)
    print("\nWarning: Call to get_admin_role() returned None - has a role been specified in the config?\n\nRun 'setAdminRole' within discord to set this!\n")
    return None


# Sets the admin_role element in the config
def set_admin_role(role_id):
    admin_roles = config.getElementsByTagName("admin_role")
    admin_role = None
    if len(admin_roles) == 0:  # First: Create the admin_role tag if it doesn't exist
        admin_role = dom.createElement("admin_role")
        config.appendChild(admin_role)
    else:
        admin_role = admin_roles[0]

    if admin_role.hasChildNodes():  # If there's old children nodes, remove them all
        for child in admin_role.childNodes:
            admin_role.removeChild(child)
    admin_role.appendChild(dom.createTextNode(role_id))

    save_config()
    return True


# Returns text inside the first "scoreboard" element
def get_default_scoreboard():
    elements = config.getElementsByTagName("scoreboard")
    if len(elements) >= 1:
        scoreboard = elements[0].firstChild
        if scoreboard is not None and scoreboard.nodeValue is not None:
            return scoreboard.nodeValue
    return None


# Sets the scoreboard element in the config
def set_default_scoreboard(scrbrd):
    scoreboard_elements = config.getElementsByTagName("scoreboard")
    scoreboard = None
    if len(scoreboard_elements) == 0:  # First: Create the scoreboard tag if it doesn't exist
        scoreboard = dom.createElement("scoreboard")
        config.appendChild(scoreboard)
    else:
        scoreboard = scoreboard_elements[0]

    if scoreboard.hasChildNodes():  # If there's old children nodes, remove them all
        for child in scoreboard.childNodes:
            scoreboard.removeChild(child)
    scoreboard.appendChild(dom.createTextNode(scrbrd))

    save_config()
    return True



# Gets the duckboard channel
def get_duckboard_channel():
    elements = config.getElementsByTagName("duckboard")
    if len(elements) >= 1:
        duckboard = elements[0].firstChild
        if duckboard is not None and duckboard.nodeValue is not None:
            return duckboard.nodeValue
    return None



# Sets the duckboard channel
def set_duckboard_channel(id):
    duckboard_elements = config.getElementsByTagName("duckboard")
    duckboard = None
    if len(duckboard_elements) == 0:  # First: Create the duckboard tag if it doesn't exist
        duckboard = dom.createElement("duckboard")
        config.appendChild(duckboard)
    else:
        duckboard = duckboard_elements[0]

    if duckboard.hasChildNodes():  # If there's old children nodes, remove them all
        for child in duckboard.childNodes:
            duckboard.removeChild(child)
    duckboard.appendChild(dom.createTextNode(str(id)))

    save_config()
    return True



# Gets the duckboard reaction count
def get_duckboard_count():
    elements = config.getElementsByTagName("duckboardcount")
    if len(elements) >= 1:
        duckboardc = elements[0].firstChild
        if duckboardc is not None and duckboardc.nodeValue is not None:
            return duckboardc.nodeValue
    return None



# Sets the duckboard reaction count
def set_duckboard_count(count):
    duckboardc_elements = config.getElementsByTagName("duckboardcount")
    duckboardc = None
    if len(duckboardc_elements) == 0:  # First: Create the duckboard tag if it doesn't exist
        duckboardc = dom.createElement("duckboardcount")
        config.appendChild(duckboardc)
    else:
        duckboardc = duckboardc_elements[0]

    if duckboardc.hasChildNodes():  # If there's old children nodes, remove them all
        for child in duckboardc.childNodes:
            duckboardc.removeChild(child)
    duckboardc.appendChild(dom.createTextNode(str(count)))

    save_config()
    return True



# Gets the list of color roles
def get_color_roles():
    global colorRoles
    colorRoles = {}
    colors = config.getElementsByTagName("colors")  # First grab the "colors" element where all the colors are stored
    if len(colors) >= 1:
        colorList = colors[0]
        if colorList is not None:

            configColors = colorList.getElementsByTagName("color")  # Grab all the colors we've defined
            for color in configColors:
                if color.hasAttribute("name") and color.hasAttribute("roleid"):  # Check if this color has a name and role assigned correctly
                    colorRoles[color.getAttribute("roleid")] = category.getAttribute("name")
                else:
                    print("Config warning: Color in config is missing a name or role and won't be loaded!")



# Sets the list of color roles
def set_color_roles():
    global colorRoles
    colors = config.getElementsByTagName("colors")  # First grab the "colors" element where all the colors are stored
    if len(colors) == 0:  # Create the colors element if it doesn't exist
        colorList = dom.createElement("colors")
        config.appendChild(colorList)
    else:
        colorList = colors[0]

    if colorList.hasChildNodes():  # Nuke the color list and make a new one, easy modo >:)
        for child in colorList.childNodes:
            colorList.removeChild(child)

    for color in colorRoles:
        colore = dom.createElement("color")
        colore.setAttribute("name", color[1])
        colore.setAttribute("roleid", color[0])
        colorList.appendChild()

    save_config()



# Let's open our config:
try:
    dom = xml.dom.minidom.parse("config.xml")
except FileNotFoundError:  # No config file? Create one and set its root element
    dom = minidom.Document()
    root = dom.createElement("config")
    dom.appendChild(root)
except ExpatError as e:  # Our formatting is screwed
    print("Error parsing config.xml, your config formatting is corrupted.\n\nExpatError: " + str(e))
    sys.exit(2)


config = dom.documentElement
categories = None  # Don't forget to initialize the category list, too!
categoriesAlt = None
get_categories()


print("Loaded categories:")
for category in categories.keys():
    print(category, ":", categories[category])

save_config()
