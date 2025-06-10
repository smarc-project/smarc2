# This message is used to send a custom command to the vehicle
# through an arbitrary communication link.

# Time stamped by the topside modem when sending the command.
# The stamp is in UTC and in SECONDS [s].
uint32 sent_stamp
# Time stamped by the vehicle when the message was recieved.
# The stamp is in UTC and in SECONDS [s].
uint32 recv_stamp
# Command sent by the topside unit.
string cmd
