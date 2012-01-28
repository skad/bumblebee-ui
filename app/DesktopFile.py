#!/usr/bin/python
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

#TODO Use inheritance of object programming language to simplify the code

import os
# A wonderful xdg support module that Lekensteyn introduce to me: the ui is now based on the xdg standards.
import xdg.Menu
#TODO : Find a better way to import xdg abilities
from xdg.DesktopEntry import *

# TODO : Get rid of all config except the one in model files and .cfg file
# TODO : Find the best way to configure desktop files : use MODEL desktop file to check the mode, and set the files.

import Config

data_dirs=xdg.BaseDirectory.xdg_data_dirs
data_home=xdg.BaseDirectory.xdg_data_home
modes=Config.mode_keys

class GetDesktop():
    def __init__(self, entry, category=None):
        self.desktop_file_id = list(entry.DesktopFileID.rsplit('.',1)) + [category]
        self.desktopEntry= entry.DesktopEntry

    #DESKTOP ENTRY PARSE TO DETERMINE STATES
    def isLocal(self):
        if data_home in self.desktopEntry.getFileName(): return True
    
    def isConfigured(self):
        """Function to check if the desktop file is configured for Bumblebee or not"""
        if self.isLocal() \
        and self.desktopEntry.get(key='X-Ayatana-Desktop-Shortcuts') \
        and self.desktopEntry.get(key='Exec', group='BumblebeeDisable Shortcut Group') \
        and self.desktopEntry.get(key='Exec', group='BumblebeeEnable Shortcut Group'):    
            return True
        else : return False

    #DESKTOP ENTRY VALUE PARSING
    def getConfiguredEntry(self):
        return [ self.desktopEntry.getName(), 
            self.desktopEntry.get(key='Exec',group='BumblebeeEnable Shortcut Group').split(' ')]
    
    def getInfo(self):
        self.entry_info=[self.desktopEntry.getName().encode("utf-8") , 
                         self.desktop_file_id[0].encode("utf-8") , 
                         self.desktop_file_id[2] , 
                         self.desktopEntry.getIcon().encode("utf-8")]
        if self.isConfigured(): 
            return self.entry_info + self.getConfiguredInfo()
        else : return self.entry_info + [True] + 4*[False] + ['default']

    def getConfiguredInfo(self):
        """Function to get configuration from a configured desktop entry : 
        Is Application, Configured, (Selected by default : unselected), Mode, Failsafe, Compression
        """
        entry_common = 3*[True]
        entry_exec= self.desktopEntry.getExec()
        shortcuts= self.desktopEntry.get(key='X-Ayatana-Desktop-Shortcuts')
        exec_config= self.getExecConfig(entry_exec)
        if 'optirun ' in entry_exec: 
            if ('BumblebeeEnable' in shortcuts and exec_config[0]):
                return entry_common + [modes['perf']] + exec_config[1:]
            elif ('BumblebeeDisable' in shortcuts and not exec_config[0]):
                return entry_common + [modes['eco']] + exec_config[1:]
        elif (not 'optirun ' in entry_exec and 'BumblebeeDisable' in shortcuts):
            exec_config=self.getExecConfig(self.desktopEntry.get(key='Exec', group='BumblebeeDisable Shortcut Group'))
            return entry_common + [modes['option']] + exec_config[1:]
        else : return entry_common + ['Unrecognized mode'] + exec_config[1:]
			
    def setTrue( arg, next_arg=None): return {arg:True}
    
    def getCompression( arg, next_arg=None, default=Config.default_compression): 
        if (next_arg in Config.compression_list and next_arg != default): return {arg:next_arg}
    
    def getExecConfig(self, Exec, i=-1, 
        case={'--failsafe':setTrue, '-f':setTrue, '-c':getCompression},
        skip=['optirun', 'ecoptirun', '-d', ':0', ':1', ':2'] + Config.compression_list):
        """Function to search for configuration inside optirun arguments in the desktop file object : 
        Force_eco, Failsafe, Compression"""
        arg_list=Exec.split(' ')	
        exec_config={'-f':False, '--failsafe':False, '-c':'default'}
        for arg in arg_list:
            i = i+1
            if arg in case: exec_config.update(case.get(arg)(arg,next_arg=arg_list[i+1]))
            elif arg in skip: continue
            else: break
        return [exec_config['-f']] + [exec_config['--failsafe']] + [exec_config['-c']]


class SetDesktop:
    def __init__(self, fileid):
        self.entry= DesktopEntry()
        filepath = '/applications/' + fileid + '.desktop'
        self.local_path=data_home+filepath
        #TODO Find a better way : but that is still standalone
        if os.path.exists(self.local_path):
            self.local=True
            self.entry.parse(self.local_path)
        else:
            self.local=False
            for data_dir in reversed(data_dirs):
                if os.path.exists(data_dir + filepath):
                    self.entry.parse(data_dir + filepath)
                    break


    #DESKTOP ENTRY BASE CONFIGURATION
    def setEntry(self):
        entry_name=self.entry.getName()
        if self.local:
            self.setShortcuts()
            print "User entry file configured for bumblebee : " + entry_name
        else : 
            self.setEntryComment()
            self.setShortcuts()
            print "File copied, tagged and configured for bumblebee : " + entry_name
        self.writeEntry()

    def setShortcuts(self):
        self.setShortcutKey('set')
        self.cmd=self.entry.get(key="Exec")
        self.setShortcutGroup('Launch without Bumblebee', self.cmd)
        self.setShortcutGroup('Launch with Bumblebee', \
                              "optirun -f " + self.cmd, \
                              "BumblebeeDisable")
    
    def setShortcutKey(self, operation, key='X-Ayatana-Desktop-Shortcuts', values=['BumblebeeDisable','BumblebeeEnable'] ):
        shortcuts=self.entry.get(key, list=True)
        clean_shortcuts=[ value for value in shortcuts if not value in values ]
        if operation=='set': clean_shortcuts.append(values[0])
        if len(clean_shortcuts)==0 and operation=='unset': self.entry.removeKey(key)
        else : self.entry.set(key, ';'.join(clean_shortcuts) + ';')    

    def setShortcutGroup(self, name, cmd, \
                                 shortcut="BumblebeeEnable"):
        group=self.getShortcutGroup(shortcut)
        self.entry.addGroup(group)
        self.entry.set("Name", name, group)
        self.entry.set("Exec", cmd, group)
        self.entry.set("TargetEnvironment", "Unity", group)
        
    def getShortcutGroup(self,shortcut):
        #return '{0} {1}'.format(shortcut,group))
        return "%s Shortcut Group" % shortcut
        
    def setEntryComment(self, tag="File created by bumblebee-ui"):
        comment_value= self.entry.get("Comment",locale=False)
        if comment_value : tagged_value= comment_value + "(%s)" % tag
        else : tagged_value=tag
        self.entry.set("Comment", tagged_value ,locale=False)
        
    def setOptirun(self, mode, failsafe, compression):
        option=list()
        if failsafe : option.append("--failsafe")
        if compression and not compression=='default' \
        and not compression==Config.default_compression:
            option.append("-c " + compression) 
        if mode == modes['perf']:
            self.setOptirunKeys(['optirun','-f'] + option, \
                                ['optirun','-f'] + option, \
                                ['BumblebeeEnable','BumblebeeDisable'])
        elif mode == modes['eco']:
            self.setOptirunKeys(['optirun'] + option, \
                                ['optirun','-f'] + option, \
                                ['BumblebeeDisable','BumblebeeEnable'])
        elif mode == modes['option']:
            self.setOptirunKeys([], 
                                ['optirun','-f'] + option, \
                                ['BumblebeeDisable','BumblebeeEnable'])
        self.writeEntry()

# FUNCTION TO GET THE LIST OF ARGUMENT FOR SUBPROCESS
    def get_exec_list(self):
        return re.split(' ',self.config.get('BumblebeeDisable Shortcut Group','Exec'))
		
# FUNCTIONS TO CONFIGURE THE FILES WITH SHORTCUTS
    def write_config_to_file(self,output_file_name):
        with open(output_file_name,'w') as file_object:
            self.config.write(file_object)
	
    def configure_file(self):
        """Function to configure the local or global desktop file"""
        if self.local == False:
            try : self.config.set('Desktop Entry', 'Comment', self.config.get('Desktop Entry','Comment') + ' (created for Bumblebee)')
            except ConfigParser.NoOptionError: 
                self.config.set('Desktop Entry', 'Comment', 'This file has been created for Bumblebee.')		
            self.add_shortcuts()
            os.chmod(Config.user_desktop_file_directory + self.file_name_with_extension,0755)
        elif self.local == True:
            self.add_shortcuts()
		
    def add_shortcuts(self):
        """Function to add shorcut section for bumblebee and add a shortcut to the desktop file object"""
        self.prepend_option('Desktop Entry', 'X-Ayatana-Desktop-Shortcuts', 'BumblebeeDisable')
        Exec = self.config.get('Desktop Entry', 'Exec')
        #TODO Check if this is really needed
        #self.config.set('Desktop Entry','OnlyShowIn','GNOME;Unity;")
        self.add_shortcut_section('BumblebeeDisable Shortcut Group', 'Launch with Bumblebee', 'optirun ' + Exec) #Default setting is optional and forced
        self.add_shortcut_section('BumblebeeEnable Shortcut Group', 'Launch without Bumblebee', Exec)
        self.write_config_to_file(Config.user_desktop_file_directory + self.file_name_with_extension)
        if self.local == False: os.chmod(Config.user_desktop_file_directory + self.file_name_with_extension,0755)

	
    def add_shortcut_section(self,Section_title,Section_name,Section_exec):
        self.config.add_section(Section_title)
        self.config.set(Section_title, 'Name', Section_name)
        self.config.set(Section_title, 'Exec', Section_exec)
        self.config.set(Section_title, 'TargetEnvironment', 'Unity')

    def prepend_option(self,section,option,value):
        """Function to prepend a value to an option inside section of a desktop file object"""
        if self.config.has_option(section,option) == True: self.config.set(section,option, value + ";" + self.config.get(section,option))
        else : self.config.set(section,option,value)
	
# FUNCTIONS TO UNCONFIGURE FILES OR REMOVE THEM
    def is_created(self):
        """Function to check if the file is tagged as created for Bumblebee or not"""
        try:  #FIXME Bumblebee Enable must not be set in comment but somewhere else 
            if 'created for Bumblebee' in self.config.get('Desktop Entry','Comment'): return True
            else : return False 
        except ConfigParser.NoOptionError: return False 

    def unconfigure_file(self):
        """Function to unconfigure a file configured for Bumblebee : remove the shortcuts or remove the file if it's tagged as created for Bumblebee"""
        if self.is_created():
            os.remove(self.file_path)
            return True
        else: 
            self.remove_shortcuts()
            return False
		
    def remove_shortcuts(self):
        """Function to remove shorcut section for bumblebee and remove the shortcuts to the desktop file object"""
        self.config.set('Desktop Entry','Exec',self.config.get('BumblebeeEnable Shortcut Group','Exec'))
        Shortcuts=self.config.get('Desktop Entry','X-Ayatana-Desktop-Shortcuts')
        if Shortcuts=='BumblebeeDisable' or Shortcuts=='BumblebeeEnable': self.config.remove_option('Desktop Entry','X-Ayatana-Desktop-Shortcuts')
        else : self.remove_prepend_option('Desktop Entry','X-Ayatana-Desktop-Shortcuts','BumblebeeDisable\;|BumblebeeEnable\;')
        self.config.remove_section('BumblebeeDisable Shortcut Group')
        self.config.remove_section('BumblebeeEnable Shortcut Group')
        self.write_config_to_file(self.file_path)

    def remove_prepend_option(self,section,option,value):
        """Function to remove a value from an option inside section of a desktop file object"""
        if self.config.has_option(section,option) == True: self.config.set(section,option,re.sub(value,'',self.config.get(section,option)))


# FUNCTIONS TO CONFIGURE THE EXECUTION OF THE APPLICATION		
	
    def set_exec_config(self, mode, failsafe, compression):
        """Function to set the option for optirun : default, failsafe, on battery, compression"""
        option=''
        if failsafe==True: option+='--failsafe '
        if not (compression == "default" or compression == Config.default_compression) : option+='-c '+ compression + ' '
        clean_exec= self.config.get('BumblebeeEnable Shortcut Group','Exec')
        self.config.set('BumblebeeDisable Shortcut Group','Exec','optirun ' + option + clean_exec)
        if mode == Config.mode_keys['perf']: 
            self.set_exec_config_default('optirun ' + option + clean_exec, 'BumblebeeDisable', 'BumblebeeEnable')
        elif mode == Config.mode_keys['eco']: 
            self.set_exec_config_default('optirun ' + option + clean_exec, 'BumblebeeEnable', 'BumblebeeDisable')
        else: 
            self.set_exec_config_default(clean_exec, 'BumblebeeEnable', 'BumblebeeDisable')
        self.write_config_to_file(self.file_path)

	
    def setOptirunKeys(self, Exec, ShortcutExec, ShortcutList):
        self.setExec(Exec)
        self.setShortcutKey('set', values=ShortcutList )
        self.setExec(ShortcutExec, self.getShortcutGroup('BumblebeeDisable'))

    def getCleanExec(self):
        #TODO This way of getting the exec without any optirun argument must be changed
        return self.entry.get("Exec", group=self.getShortcutGroup('BumblebeeEnable'), list=True)

    def setExec(self, values, shortcut=None):
        self.entry.set("Exec", " ".join(values + self.getCleanExec()), group=shortcut)

    def isCreated(self, tag="File created by bumblebee-ui"):
        try :
            if tag in self.entry.get("Comment",locale=False) : return True
        except : return False
        
    def unsetEntry(self):
		entry_name=self.entry.getName()
        if self.isCreated():
            os.remove(self.local_path)
            print "File created by bumblebee-ui removed : " + entry_name
        else : 
            self.setExec([])
            self.unsetShortcuts()
            self.writeEntry()
            print "Entry modified by bumblebee-ui unconfigured : " + entry_name

    def unsetShortcuts (self, shortcuts=['BumblebeeDisable','BumblebeeEnable']):
        self.setShortcutKey('unset')
        for shortcut in shortcuts : 
            self.entry.removeGroup(self.getShortcutGroup(shortcut))

    def writeEntry(self):     
        try : 
            self.entry.validate()
        except ValidationError, e:
            for error in e:
                if not ('ValidationError' or 'Group name' or 'TargetEnvironment') in error:
                    print 'The file to write is not valid according to XDG specifications: %s' % self.entry
                    print e
                else : pass
                #print "Some setted values are not fullfilling the XDG specifications but works on Ubuntu Natty" 
        except : 
            print "Some exceptions occurs during the validation of this desktop file the ui created: %s" % self.entry
            print "Please report this bug and join the desktop file created"
        finally : 
            self.entry.write(self.local_path)
            os.chmod(self.local_path,0755)
        

#TODO Write a new class : to get the configuration inside the MODEL desktop files
#class BumblebeeModelDesktop:
#    def __init__(self,filename):
#        self.model = 
