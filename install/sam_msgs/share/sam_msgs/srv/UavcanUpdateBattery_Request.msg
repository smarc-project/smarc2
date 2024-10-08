#
# Update battery
#
uint8 node_id

uint8 IS_FULL     = 1 # Battery is full right now
uint8 WAS_FULL    = 2 # Battery was full when Sam started
uint8 ADD_CHARGE  = 3 # Add enclosed charge
uint8 ON_MAINS    = 4 # Powered externally
uint8 command

float32 charge  # Ah (can be negative)

