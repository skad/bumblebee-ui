#!/usr/bin/python2
# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
### BEGIN LICENSE
#
# This file is part of bumblebee-ui.
#
# bumblebee-ui is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# bumblebee-ui is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with bumblebee-ui. If not, see <http://www.gnu.org/licenses/>.
#
### END LICENSE

import os
import gtk

### APPLICATIONS MENU CONFIG ###

#BUMBLEBEE DEFAULT CONFIGURATION
config_file_path='/etc/bumblebee/bumblebee.conf'

#ICONS FILE PATH
icon_file_directory = '/usr/share/bumblebee-ui/icons/'

#ACCEPTED COMPRESSION
compression_list=['jpeg','proxy','rgb','yuv','xv']

#MODE LIST
mode_keys={'perf':"Performance",
    'eco':"Power Save",
    'option':"Optional"}

#ICON FILES THEME
icon_size=24
default_icon_name='application-x-executable'

#APP SETTINGS COLOR THEME
configured_color='#00FF33'
to_configure_color='#FFFF33'
to_unconfigure_color='#FF0033'

#GET BUMBLEBEE CONFIGURATION VALUE
def get_config_value(variable_name):
    """Function to get configuration value inside a shell script"""
    for line in open(config_file_path):
        if variable_name in line:
            return line.split('=',1)[1].replace("\n","")

default_compression= get_config_value('VGL_COMPRESS')
vgl_display= get_config_value('VGL_DISPLAY').replace(":","")

### INDICATOR SETTINGS ###
#DEFAULT APPLICATIONS IN THE PREFERRED APP MENU :
applications_setting_path='app/AppSettings.py'
default_preferred_apps =[ ['Glxgears', ['optirun', 'glxgears']] , 
                        ['Glxspheres', ['optirun', 'glxspheres']] ]

#NOTIFICATION MESSAGES :
#TODO Revert when the possibility to turn off the card is back
attention_label="Bumblebee : ON"
attention_comment="Bumblebee is in use"
active_label="Bumblebee : OFF"
active_comment="Bumblebee is not used anymore"

#FIXME There must be a better way to store config using MODEL desktop file

if __name__=="__main__" : 
    print "Config.py can't run as a standalone application"
    quit()

