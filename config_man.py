#!/usr/bin/python
from pyexpat import ExpatError
from xml.dom import minidom
from xml.dom.minidom import parse
import xml.dom.minidom
import codecs


# The config is organized like this:
# <config>
#   <admin_role>admin role id</admin_role>
#   <category name="Category name", listeningChannel="channel ID", listeningMessage="message ID">
#       <role name="Role id" dispName="Role display name" emoji="Unicode emoji/Custom emoji name" usesCustomEmoji="true/false">Role Description</role>
#       <role>...
#   </category>
#   <category>...
# </config>




def save_config():
    file = codecs.open("config.xml", "w", "utf_8_sig")
    file.write(config.toxml(encoding="utf-8").decode("utf-8"))
    #config.writexml(file, addindent="\t", newl="\n", encoding="utf-8")
    file.close()
    get_categories()


# Sets the categories variable to a dict containing all categories as keys, and the channel/message IDs to listen on as values
def get_categories():
    global categories
    ret = {}

    configCategories = config.getElementsByTagName("category")  # First iterate through all the categories in the file...
    for category in configCategories:
        if category.hasAttribute("name"):  # Check if this category has a name
            if category.hasAttribute("listeningChannel") and category.hasAttribute("listeningMessage"):  # If it also has a channel/message to listen for, add them too
                ret[category.getAttribute("name")] = category.getAttribute("listeningChannel") + ";" + category.getAttribute("listeningMessage")
            else:  # Otherwise, set the channel/message fields to -1
                print("Category", category.getAttribute("name"), "doesn't have listeningMessage/Channel attributes (and thus can't track a message for reactions to assign these roles!)\nRun the role list command to generate a role list message to fix this!")
                ret[category.getAttribute("name")] = "-1;-1"
#            roles = ""
#            for role in category.getElementsByTagName("role"):
#                if role.hasAttribute("name"):
#                    roles += role.getAttribute("name") + ","
#                else:
#                    print("Config warning: Role in category ", category.getAttribute("name"), " has no name!")
#
#            if len(roles) > 1:  # Found at least one role, strip off the trailing comma
#                roles = roles[0:-1]
#            ret[category.getAttribute("name")] = roles
        else:
            print("Config warning: Category in config is missing a name and won't be loaded!")
    categories = ret


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
                    if configRole.hasAttribute("name") and configRole.hasAttribute("emoji") and configRole.hasAttribute("usesCustomEmoji"):
                        ret[configRole.getAttribute("name")] = [configRole.getAttribute("emoji"), configRole.getAttribute("usesCustomEmoji")]  # Grab this role from the config and its emoji (if it has both attributes), then add it to the dict to return
        return ret

    else:
        print("Error: Attempt to get roles from non-existent category \"", category, "\"")
        return False


# Adds a role (and category, if the specified one doesn't exist) to the config
def add_role(category, role, dispName, emoji, description, isCustomEmoji):
    ret = ""
    if category not in categories:  # Check if the specified category doesn't exist
        if add_category(category) is False:  # Try adding it! If that fails, the program is mega derped and we should return
            print("Failed to add role", role, ": Category \"", category, "\"doesn't exist and was unable to be added.\n\nThis probably shouldn't happen.")
            return "Failed to add role: Category \"", category, "\"doesn't exist and was unable to be added.\n\nThis probably shouldn't happen."

    for emote in get_roles_emoji(category).values():
        if emote[0] == emoji:
            print("Failed to add role: Emote " + emoji + " is already used for another role in this category!")
            return "Failed to add role: Emoji " + emoji + " is already used for another role in this category!"

    for category_element in config.getElementsByTagName("category"):  # Now go and add this role to the category
        category_name = category_element.getAttribute("name")
        if category_name is not None and category_name == category:
            config_role = dom.createElement("role")  # Create the role element (<role>)
            config_role.setAttribute("name", role)
            config_role.setAttribute("dispName", dispName)
            config_role.setAttribute("emoji", emoji)
            config_role.setAttribute("usesCustomEmoji", str(isCustomEmoji))
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
            for role_element in  category_element.getElementsByTagName("role"):
                if role_element.hasAttribute("name") and role_element.getAttribute("name") == role:  # Found the role to delete, delete it!
                    category_element.removeChild(role_element)
                    print("Removed role", str(role), "from category", category)
                    if not category_element.hasChildNodes():  # No other roles in this category, also remove the now-empty category
                        config.removeChild(category_element)
                        print("Removed now empty category " + category)
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


def sort_category(category):
    if category not in categories:  # The specified category doesn't exist
        print("Failed to sort category: Category \"", category, "\"doesn't exist!")
        return "Failed to sort category: Category \"", category, "\"doesn't exist!"

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


# Let's open our config:
try:
    dom = xml.dom.minidom.parse("config.xml")
except FileNotFoundError:  # No config file? Create one and set its root element
    dom = minidom.Document()
    root = dom.createElement("config")
    dom.appendChild(root)

config = dom.documentElement
categories = None  # Don't forget to initialize the category list, too!
get_categories()

#add_role("lamno", "R", "🤔", "Your mom is a kind soul")  # Addrole test

# Creates <category name="butts"><role>Your mom</role></category>
#category = dom.createElement("category")
#category.setAttribute("name", "butts")
#role = dom.createElement("role")
#role.appendChild(dom.createTextNode("Your mom"))
#category.appendChild(role)
#config.appendChild(category)

#category = dom.createElement("category")
#category.setAttribute("name", "bruhv")
#category.appendChild(dom.createElement("role"))
#config.appendChild(category)


for category in categories.keys():
    print(category, ":", categories[category])

save_config()
