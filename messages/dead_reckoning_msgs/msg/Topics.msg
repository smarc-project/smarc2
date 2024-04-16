# This is a file that defines all the topics of dead reckoning.
# The goal is to have one location that all cpp/py scripts
# can easily access and thus avoid having 100 parameters for topics all
# over the place, repeated for all subs/pubs...
# It is assumed that the nodes will namespace as needed.

########################
# Dead reckoning topics
########################
# DR node
string DR_ODOM_TOPIC = 'dr/odom'
string DR_DEPTH_TOPIC = 'dr/depth'
string DR_GPS_ODOM_TOPIC = 'dr/gps_odom'
