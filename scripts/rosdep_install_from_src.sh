#!/bin/bash
rosdep install -i --from-path src --rosdistro humble -y --skip-keys sam_* --skip-keys lolo_* --skip-keys smarc_*
