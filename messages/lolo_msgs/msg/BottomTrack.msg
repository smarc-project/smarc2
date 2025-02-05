uint8 version
uint8 offsetOfData
uint32 serialNumber
uint8 year #Trigger time
uint8 month
uint8 day
uint8 hour
uint8 minute
uint8 seconds
uint16 microSeconds100
uint16 nBeams
uint32 error
uint32 status
float32 soundSpeed     # [m/s]
float32 temperature    # [Celsius]
float32 pressure       # [Bar]

# Beam data
float32 velBeam0        #Velocities for each beam. [m/s]
float32 velBeam1        #Velocities for each beam. [m/s]
float32 velBeam2        #Velocities for each beam. [m/s]
float32 velBeam3        #Velocities for each beam. [m/s]

float32 distBeam0       #Distances for each beam. [m ]
float32 distBeam1       #Distances for each beam. [m ]
float32 distBeam2       #Distances for each beam. [m ]
float32 distBeam3       #Distances for each beam. [m ]

float32 fomBeam0        #FOM for each beam.
float32 fomBeam1        #FOM for each beam.
float32 fomBeam2        #FOM for each beam.
float32 fomBeam3        #FOM for each beam.

float32 timeDiff1Beam0      #DT1 for each beam. [s ]
float32 timeDiff1Beam1      #DT1 for each beam. [s ]
float32 timeDiff1Beam2      #DT1 for each beam. [s ]
float32 timeDiff1Beam3      #DT1 for each beam. [s ]

float32 timeDiff2Beam0      #DT2 for each beam. [s ]
float32 timeDiff2Beam1      #DT2 for each beam. [s ]
float32 timeDiff2Beam2      #DT2 for each beam. [s ]
float32 timeDiff2Beam3      #DT2 for each beam. [s ]

float32 timeVelEstBeam0     #Duration of velocity estimate for each beam. [s ]
float32 timeVelEstBeam1     #Duration of velocity estimate for each beam. [s ]
float32 timeVelEstBeam2     #Duration of velocity estimate for each beam. [s ]
float32 timeVelEstBeam3     #Duration of velocity estimate for each beam. [s ]

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