#!/usr/bin/python

# --
# scoreboard_config_man.py - its like config-man but for events
# --


import os
import sys
from pyexpat import ExpatError
from xml.dom import minidom
from xml.dom.minidom import parse
import xml.dom.minidom
import codecs


# The scoreboard config is organized like this - each individual event has it's own config file so you can save old scoreboards for posterity.
# (Note: The event name is inferred from the config file's name)
# <scoreboard>
#   <submit_enabled>True/False</submit_enabled>
#   <display_name>name</display_name>
#   <description>event description</description>
#   <scoreboard_message channel="" message=""/>
#   <field name="Field name" type="Field type">
#       <entry player="Player name" verified="True/False">Entry value</role>
#       <entry>...
#   </field>
#   <category>...
# </scoreboard>

class ScoreboardConfig:
    def __init__(self):
        print("Initializing scoreboard_config_man...")
        self.sc_dom = None
        self.sc_config = None
        self.sc_name = None

        # Create our scoreboard config directory if it doesn't exist
        if not os.path.exists("scoreboards"):
            try:
                os.mkdir("scoreboards")
            except Exception as e:
                print("Error creating scoreboard config directory: " + str(e))
                sys.exit(1)

    # Checks if a scoreboard config file exists
    def sc_config_exists(self, name):
        return os.path.exists("scoreboards/" + name + ".xml")



    # Attempts to load a scoreboard config with the given name, optionally creating a new one if it doesn't exist
    def load_sc_config(self, name, allow_create, desc=""):
        print("Attempting load of scoreboard config \"scoreboards/" + name + ".xml\"...")
        try:
            self.sc_dom = xml.dom.minidom.parse("scoreboards/" + name + ".xml")
            self.sc_config = self.sc_dom.documentElement
            self.sc_name = name
            print("Loaded!")
            return 0
        except FileNotFoundError:  # No config file? Make one boi
            if allow_create:
                print("Scoreboard config not found, but creation of a new config is enabled. Attempting creation...")
                self.sc_dom = minidom.Document()
                root = self.sc_dom.createElement("scoreboard")
                self.sc_dom.appendChild(root)
                self.sc_config = self.sc_dom.documentElement
                self.sc_name = name
                return 1
            else:
                print("Error: Scoreboard config file not found!")
                self.sc_dom = None
                self.sc_config = None
                self.sc_name = None
                return -1


    def is_scoreboard_loaded(self):
        return self.sc_config is not None and self.sc_name is not None  # At a minimum our config object shouldn't be broken (our config name should match up with this too)



    # Saves the currently loaded scoreboard config to file
    def save_sc_config(self):
        if self.sc_config is not None:
            print("Saving scoreboard config \"scoreboards/" + self.sc_name + ".xml\"...")
            file = codecs.open("scoreboards/" + self.sc_name + ".xml", "w", "utf_8_sig")
            file.write(self.sc_config.toxml(encoding="utf-8").decode("utf-8"))
            #config.writexml(file, addindent="\t", newl="\n", encoding="utf-8")
            file.close()




    # Gets the scoreboard's display name, or it's filename if the display name isn't set
    def get_disp_name(self):
        if self.sc_config is not None:
            elements = self.sc_config.getElementsByTagName("display_name")
            if len(elements) >= 1 and elements[0].firstChild.nodeValue is not None:
                return elements[0].firstChild.nodeValue
            else:
                return self.sc_name
        return None



    # Sets the scoreboard's display name
    def set_disp_name(self, name):
        if self.sc_config is not None:
            disp_name_elems = self.sc_config.getElementsByTagName("display_name")  # Try to get the display_name element - if it doesn't exist, make one
            disp_name = None
            if len(disp_name_elems) == 0:
                disp_name = self.sc_dom.createElement("display_name")
                self.sc_config.appendChild(disp_name)
            else:
                disp_name = disp_name_elems[0]

            if disp_name.hasChildNodes():
                for child in disp_name.childNodes:
                    disp_name.removeChild(child)
            disp_name.appendChild(self.sc_dom.createTextNode(name))

            print("Set scoreboard display name to \"" + name + "\"")
            self.save_sc_config()



    # Gets the scoreboard's description
    def get_desc(self):
        if self.sc_config is not None:
            elements = self.sc_config.getElementsByTagName("description")
            if len(elements) >= 1 and elements[0].firstChild.nodeValue is not None:
                return elements[0].firstChild.nodeValue
        return ""



    # Sets the scoreboard's description
    def set_desc(self, description):
        if self.sc_config is not None:
            desc_elems = self.sc_config.getElementsByTagName("description")  # Try to get the desc element - if it doesn't exist, make one
            desc = None
            if len(desc_elems) == 0:
                desc = self.sc_dom.createElement("description")
                self.sc_config.appendChild(desc)
            else:
                desc = desc_elems[0]

            if desc.hasChildNodes():
                for child in desc.childNodes:
                    desc.removeChild(child)
            desc.appendChild(self.sc_dom.createTextNode(description))

            print("Set scoreboard description to \"" + description + "\"")
            self.save_sc_config()



    # Gets the channel/message ID of the scoreboard message
    def get_scoreboard_msg(self):
        if self.sc_config is not None:
            msgs = self.sc_config.getElementsByTagName("scoreboard_message")
            if len(msgs) >= 1:
                msg = msgs[0]
                if msg.hasAttribute("channel") and msg.hasAttribute("message"):
                    return [int(msg.getAttribute("channel")), int(msg.getAttribute("message"))]
        return None


    # Sets the channel/message ID the scoreboard message is in
    def set_scoreboard_msg(self, channel, message):
        if self.sc_config is not None:
            msgs = self.sc_config.getElementsByTagName("scoreboard_message")
            msg = None
            if len(msgs) == 0:
                msg = self.sc_dom.createElement("scoreboard_message")
                self.sc_config.appendChild(msg)
            else:
                msg = msgs[0]

            msg.setAttribute("channel", str(channel))
            msg.setAttribute("message", str(message))
            print("Scoreboard message set to ID " + str(message))
            self.save_sc_config()

