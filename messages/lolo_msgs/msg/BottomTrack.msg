uint8 version
uint8 data_offset  # OfData #
uint32 serial_number
uint8 year #Trigger time
uint8 month
uint8 day
uint8 hour
uint8 minute
uint8 seconds
uint16 micro_seconds_100
uint16 n_beams
uint32 error
uint32 status
float32 sound_speed     # [m/s]
float32 temperature    # [Celsius]
float32 pressure       # [Bar]

# Beam data
float32 vel_beam0        #Velocities for each beam. [m/s]
float32 vel_beam1        #Velocities for each beam. [m/s]
float32 vel_beam2        #Velocities for each beam. [m/s]
float32 vel_beam3        #Velocities for each beam. [m/s]

float32 dist_beam0       #Distances for each beam. [m ]
float32 dist_beam1       #Distances for each beam. [m ]
float32 dist_beam2       #Distances for each beam. [m ]
float32 dist_beam3       #Distances for each beam. [m ]

float32 fom_beam0        #FOM for each beam.
float32 fom_beam1        #FOM for each beam.
float32 fom_beam2        #FOM for each beam.
float32 fom_beam3        #FOM for each beam.

float32 time_diff1_beam0      #DT1 for each beam. [s ]
float32 time_diff1_beam1      #DT1 for each beam. [s ]
float32 time_diff1_beam2      #DT1 for each beam. [s ]
float32 time_diff1_beam3      #DT1 for each beam. [s ]

float32 time_diff2_beam0      #DT2 for each beam. [s ]
float32 time_diff2_beam1      #DT2 for each beam. [s ]
float32 time_diff2_beam2      #DT2 for each beam. [s ]
float32 time_diff2_beam3      #DT2 for each beam. [s ]

float32 time_vel_est_beam0     #Duration of velocity estimate for each beam. [s ]
float32 time_vel_est_beam1     #Duration of velocity estimate for each beam. [s ]
float32 time_vel_est_beam2     #Duration of velocity estimate for each beam. [s ]
float32 time_vel_est_beam3     #Duration of velocity estimate for each beam. [s ]

# XYZ data
#float velX # Velocity X. [m/s]
#float velY # Velocity Y. [m/s]
#float velZ1 # Velocity Z1. [m/s]
#float velZ2 # Velocity Z2. [m/s]
#float fomX # FOM X.
#float fomY # FOM Y.
#float fomZ1 # FOM Z1.
#float fomZ2 # FOM Z2.
#float timeDiff1X # DT1 X. [s ]
#float timeDiff1Y # DT1 Y. [s ]
#float timeDiff1Z1 # DT1 Z1. [s ]
#float timeDiff1Z2 # DT1 Z2. [s ]
#float timeDiff2X # DT2 X. [s ]
#float timeDiff2Y # DT2 Y. [s ]
#float timeDiff2Z1 # DT2 Z1. [s ]
#float timeDiff2Z2 # DT2 Z2. [s ]
#float timeVelEstX # Duration of velocity estimate for each component. [s ]
#float timeVelEstY # Duration of velocity estimate for each component. [s ]
#float timeVelEstZ1 # Duration of velocity estimate for each component. [s ]
#float timeVelEstZ2 # Duration of velocity estimate for each component. [