#!/usr/bin/python3
import os, sys



# This is a script that scans all Topics.msg files
# in the smarc2 repo and generates a list of all
# the topics that are used in the system.


# Make sure we run in /smarc2
in_smarc2 = True
if(os.getcwd()[-6:] != "smarc2"):
    in_smarc2 = False
    print("Are you running this in scripts...?")
    if(os.getcwd()[-14:] == "smarc2/scripts"):
        print("Yes you are...")
        os.chdir("..")
        in_smarc2 = True

if(not in_smarc2): sys.exit(1)

print("We are in /smarc2, ready to roll")

# Get the list of all Topics.msg files
topics_msg_files = []
for root, dirs, files in os.walk("."):
    for file in files:
        if file.endswith("Topics.msg"):
            topics_msg_files.append(os.path.join(root, file))
            print("Found Topics.msg file: " + os.path.join(root, file))


# Now we need to parse each Topics.msg file and extract the topics
topics_in_file = {}
for topics_msg_file in topics_msg_files:
    with open(topics_msg_file, "r") as f:
        lines = f.readlines()
        topics_in_file[topics_msg_file] = {}
        for line in lines:
            if line.startswith("string "):
                # clear all whitespace
                line = line.strip()
                # skip the string keyword
                line = line[6:]
                # split the line by = and get the topic symbol and string
                topic_symbol = line.split("=")[0]
                topic_string = line.split("=")[1]
                # if any, separate the comments
                if topic_string.find("#") != -1:
                    topic_string = topic_string.split("#")[0]
                topics_in_file[topics_msg_file][topic_symbol] = topic_string
                print("Found topic: " + topic_symbol + " with string: " + topic_string + " in file: " + topics_msg_file)

filename = "All Topics.msg.md"

# Now generate a nice markdown file with the topics
with open(filename, "w") as f:
    f.write("# Topics in the system defined under all Topics.msg files\n")
    f.write("\n")
    for topics_msg_file, topics in topics_in_file.items():
        # create a link to the file
        topics_msg_file = topics_msg_file.replace("./", "")
        f.write("## Topics in file: [" + topics_msg_file + "](" + topics_msg_file + ")\n")
        f.write("\n")
        for topic_symbol, topic_string in topics.items():
            f.write("- " + topic_symbol + ": " + topic_string + "\n")

# generate a list of all duplicate topic strings
duplicates = {}
for topics_msg_file, topics in topics_in_file.items():
    for topic_symbol, topic_string in topics.items():
        if topic_string not in duplicates:
            duplicates[topic_string] = [(topic_symbol, topics_msg_file)]
        else:
            duplicates[topic_string].append((topic_symbol, topics_msg_file))

# append the duplicates to the markdown file
with open(filename, "a") as f:
    f.write("\n")
    f.write("# Duplicates\n")
    f.write("\n")
    for topic_string, topics in duplicates.items():
        if len(topics) > 1:
            f.write("- " + topic_string + ": \n")
            for topic_symbol, topics_msg_file in topics:
                # create a link to the file
                topics_msg_file = topics_msg_file.replace("./", "")
                f.write("    - [" + topic_symbol + "](" + topics_msg_file + ")\n")