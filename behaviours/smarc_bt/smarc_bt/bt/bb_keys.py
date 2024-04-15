#!/usr/bin/python3

import enum

class BBKeys(str, enum.Enum):
    MIN_ALTITUDE = 'min_alt'
    MAX_DEPTH = 'max_depth'

    def __str__(self):
        return self.name

# copied from old version
# ABORT = 'abort'

# MISSION_PLAN_OBJ = 'misison_plan'
# MANEUVER_ACTIONS = 'maneuver_actions'

# CURRENT_PLAN_ACTION = 'current_plan_action'
# LAST_PLAN_ACTION_FEEDBACK = 'last_plan_action_feedback'
# # set this from any action that might return RUNNING.
# # useful for feedback purposes
# CURRENTLY_RUNNING_ACTION = 'currently_running_action'

# # feedback really, set outside a tick
# TREE_TIP = "tree_tip"
# LAST_HEARTBEAT_TIME = "last_heartbeat_time"

# # to set once the BT is 'DONE' done. LIke, it wont want to
# # set new waypoints or anything, and is just there chillin
# # and handling stuff like neptus etc.
# MISSION_FINALIZED = 'mission_finalized'

# # coverage stuffs
# # these are in the BB becse they could be dynamic
# SWATH = 'swath'
# LOCALIZATION_ERROR_GROWTH = 'loc_err_growth'

# # Algae farm
# ALGAE_FOLLOW_ENABLE = 'algea_enable'
# ALGAE_FOLLOW_WP = 'algae_follow_wp'

# # live-wp that can be updated continually
# LIVE_WP_ENABLE = 'live_wp_enable'
# LIVE_WP = 'live_wp'

# # gui-wp that can be updated continually
# GUI_WP_ENABLE = 'gui_wp_enable'
# GUI_WP = 'gui_wp'

# LLTOUTM_SERVICE_NAME = 'll2utm_service'
# UTMTOLL_SERVICE_NAME = 'utm2ll_service'