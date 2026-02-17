std_msgs/Header header
uint8   type          # Packet Type, 0xE2 = Sonar 8 Bit
uint32  time          # Ping time   [100 us]
uint8   frequency_id  # Freq Id, currently 0x00
float32 frequency
int16   gain
uint16  decimation
float32 max_duration  # Max travel time of outermost bins (s)
float32 baseline      #New field
float32 sound_velocity  #New field
uint8[] port_channel
uint8[] starboard_channel
float32[] port_channel_phase_difference #New field
float32[] starboard_channel_phase_difference #New field
float32[] port_channel_bearing #New field
float32[] starboard_channel_bearing #New field
uint8[] extra_channel
