#!/usr/bin/python3
import os, subprocess, sys, time, signal, json

####
# This is a linear script that calls some ros2 functions
# after crawling the smarc2 repository.
# It collects info about packages, launchfiles and their nodes.
# Also the info of each node.
####

robot_name = "test_robot"

def rosnodelist():
    res = subprocess.run(["ros2", "node", "list"], stdout=subprocess.PIPE)
    node_list = res.stdout.decode().split("\n")
    node_list = [n for n in node_list if n != ""]
    return node_list

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

# keep the whole info dump in a dictionary to be formatted later
structure = {}


# We want to find all launch files that matter
# Colcon already knows this, so we ask it...
res = subprocess.run(["colcon", "list"], stdout=subprocess.PIPE)
packages_lines = res.stdout.decode().split("\n")
packages = []
for p in packages_lines:
    parts = p.split("\t")
    if(len(parts) > 1):
        p_name, path = parts[:2]
        packages.append((p_name, path))
        print(f"Found package: {p_name} in path {path}")
        structure[p_name] = {"path":path,
                             "launchfiles":{}}


# packages = [(package_name, package_path), ...]
# now find all the launch files in this package
packages_launches = []
for p_name, p_path in packages:
    launchfiles = []
    # ros2 allows different kinds of launchfiles
    # a *.launch* would find all of them, but it might also find 
    # other stuff, so we explicitly define the ones we want
    launchfile_extensions = [".launch", ".launch.py", ".launch.xml", ".launch.yaml"]
    for e in launchfile_extensions:
        res = subprocess.run(["find", p_path, "-name", f"*{e}"], stdout=subprocess.PIPE)
        launches_lines = res.stdout.decode().split("\n")
        launchfiles.extend([l for l in launches_lines if l != ''])
    
    # some very fun people dont put .launch in their launchfiles
    # and simply rely on the py, or whatever file being in the "launch" directory...
    # we need those too
    annoying_extensions = [".py", ".xml", ".yaml"]
    for e in annoying_extensions:
        launch_folder = os.path.join(p_path, "launch")
        res = subprocess.run(["find", launch_folder, "-name", f"*{e}"], stdout=subprocess.PIPE)
        launches_lines = res.stdout.decode().split("\n")
        launchfiles.extend([l for l in launches_lines if l != '' and l not in launchfiles])
    
    
    if(len(launchfiles) != 0):
        packages_launches.append((p_name, launchfiles))


# packages_launches = [(package_name, [..launch, ..launch]), ...]
# to launch these one by one, and then run some ros commands for each package
for p_name, launchfiles in packages_launches:
    print(f"Found {len(launchfiles)} launchfile(s) in package {p_name}")
    print(f"Launching them one by one...")

    for launchfile in launchfiles:
        structure[p_name]["launchfiles"][launchfile] = {"nodes":{}}

        print(f">> Launching launchfile {launchfile}")
        # we want these in the BG and killable
        launched = subprocess.Popen(["ros2", "launch", launchfile, f"robot_name:={robot_name}"], stdout=subprocess.DEVNULL)
        # wait a little for all the stuff to run...
        wait_seconds = 1
        print(f">> Waiting for launch to launch for {wait_seconds}s\n")
        time.sleep(wait_seconds)

        # then we run ros2 node list to get all the nodes this launch file runs
        node_list = rosnodelist()
        print(f">> {launchfile} launches these nodes:")
        for node in node_list: 
            print(f">> >> {node}")

        for node in node_list:
            # mimic the output of `ros2 node info`
            node_info_dict = {
                "Subscribers":[],
                "Publishers":[],
                "Service Servers":[],
                "Service Clients":[],
                "Action Servers":[],
                "Action Clients":[]
                }
            res = subprocess.run(["ros2", "node", "info", node], stdout=subprocess.PIPE)
            node_info_str = res.stdout.decode()
            # we know the this string, so imma just
            # iterate over its lines and collect the info i want
            node_info_lines = node_info_str.split("\n")

            current_part = ""
            for line in node_info_lines:
                # info first writes the name of the node, skip that
                if line == node: continue
                if len(line) == 0: continue
                # then it starts to list subs pubs etc
                # "  Subscribers:" -> "Subscribers"
                clean_line = line.strip()[:-1]
                if clean_line in node_info_dict.keys():
                    current_part = clean_line
                    continue
                # the other lines are like "   /topic: type/of/topic"
                topic, topic_type = line.split(":")
                node_info_dict[current_part].append((topic.strip(), topic_type.strip()))

            structure[p_name]["launchfiles"][launchfile]["nodes"][node] = node_info_dict
            

        # and then finally we kill that launch process
        # dont want random nodes chilling around
        # between different launches...
        while(True):
            print(">> SIGINT-ing")
            launched.send_signal(signal.SIGINT)
            launched.wait(timeout=30)
            print(">> SIGTERM-ing for good measure")
            launched.send_signal(signal.SIGTERM)
            launched.wait(timeout=30)
            node_list = rosnodelist()
            # some nodes take a bit to die, wait for them
            # if need be. We wanna make sure they dont
            # leak to other launches.
            if(len(node_list) == 0):
                print(">> All nodes killed, we good")
                break
            else:
                print(f">> These are still alive: {node_list}")
                print(">> Waiting a bit for them to die too...")
                time.sleep(1)

        launched.kill()
        print(">> Launchfile done")
        

# finally, export the findings as JSON for later rendering with a different script
with open("smarc2_structure.json", "w") as f:
    # we also want to keep track of the git commit hash to avoid running this long
    # script if the head is on the same commit
    res = subprocess.run(["git", "log", "-1"], stdout=subprocess.PIPE)
    # output is like
    # commit <hash> (stuff)
    # Author: ...
    # Date: ...
    # so the hash is line 0, word 1
    commit_hash = res.stdout.decode().split("\n")[0].split(" ")[1]
    file = {"hash":commit_hash,
            "created":int(time.time()),
            "robot_name":robot_name,
            "structure":structure}
    json.dump(file, f)
