builtin_interfaces/Time time

uint8 STATUS_INACTIVE = 0 # no robot or no valid fence
uint8 STATUS_INSIDE = 1 # valid fence, robot is inside
uint8 STATUS_OUTSIDE = 2 # valid fence, robot is outside
uint8 status

uint8 REASON_FENCE = 0 # horizontally outside
uint8 REASON_CEILING = 1 # altitude above ceiling altitude
uint8 REASON_FLOOR = 2 # altitude below floor altitude
uint8 REASON_ISLAND = 3 # point inside an island
uint8 outside_reason