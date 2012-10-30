#!/usr/bin/python

import gtk,subprocess,os,gobject,pynotify

import Config
from AppSettings import Applications_settings, IconSet
from DesktopFile import DesktopFile, DesktopFileSet

class BumblebeeIndicator:
    def __init__(self):

        self.switch = gtk.CheckMenuItem()
        self.statusicon = gtk.StatusIcon()
        self.statusicon.set_from_file(IconSet().get_path("bumblebee-indicator")) 
        self.statusicon.connect("popup-menu", self.right_click_event)
        self.statusicon.set_tooltip("Bumblebee Indicator")
	self.statusicon.set_title("Bumblebee Indicator")
        self.card_state=False
        self.lock_file = "/tmp/.X%s-lock" % Config.vgl_display
        self.initial_state_checker()
        
    def right_click_event(self, icon, button, time):
        self.menu = gtk.Menu()

        self.initial_state_checker()

        self.switch.set_sensitive(False)
        self.menu.append(self.switch)

        self.build_menu_separator(self.menu)
                
        self.prefered_app_submenu = gtk.MenuItem("Preferred Apps")
        self.update_menu()
        self.prefered_app_submenu.connect('activate', self.update_menu)
        self.menu.append(self.prefered_app_submenu)
        
        item2 = gtk.MenuItem("Configure Apps")
        item2.connect("activate", self.app_configure)
        self.menu.append(item2)
 
	    
        self.build_menu_separator(self.menu)

        quit = gtk.ImageMenuItem(gtk.STOCK_QUIT)
        quit.connect("activate", self.quit)
        self.menu.append(quit)

        self.menu.show_all()      
        self.menu.popup(None, None, gtk.status_icon_position_menu, button, time, self.statusicon)

    def build_menu_separator(self, menu):
    	separator = gtk.SeparatorMenuItem()
    	separator.show()
        menu.append(separator)

# FUNCTIONS TO BUILD THE "PREFERRED APP" MENU FROM THE LOCAL DESKTOP FILES
    def update_menu(self, widget=None):	
        pref_menu=gtk.Menu()
        self.add_submenu_items( pref_menu, Config.default_preferred_apps )
    	self.build_menu_separator( pref_menu )
        self.add_submenu_items( pref_menu, DesktopFileSet().get_configured_from_check() )
        pref_menu.show()
        self.prefered_app_submenu.set_submenu(pref_menu)

    def add_submenu_items(self, submenu, items_list):
        for Name, Exec_list in items_list : 
            subitem = gtk.MenuItem(label=Name)
            subitem.connect("activate", self.call_app, Exec_list)
            subitem.show()
            submenu.append( subitem )

    def notify_state(self, title, msg, icon_name):
        pynotify.init("Bumblebee notification")
        self.notification= pynotify.Notification(title, msg, IconSet().get_uri(icon_name,48))
        self.notification.set_urgency(pynotify.URGENCY_NORMAL)
        self.notification.show()

# FUNCTIONS TO CHECK FOR THE STATE OF THE INDICATOR
    def initial_state_checker(self):
        if self.attention_state_condition(): self.set_attention_state(notify=False)
        else : self.set_active_state(notify=False)

    def state_checker(self):
        if self.attention_state_condition():
            if self.card_state == False : self.set_attention_state()
        elif self.card_state == True: self.set_active_state()	
        return True
	
    def attention_state_condition(self):
        if os.path.exists(self.lock_file): return True
        else: return False

# FUNCTIONS TO SET THE STATE OF THE INDICATOR AND LAUNCH NOTIFICATION
    def set_attention_state(self, notify=True):
        self.set_status(True, Config.attention_label,
                        Config.attention_comment,
                        "bumblebee-indicator-active", notify)

    def set_active_state(self, notify=True):
        self.set_status(False, Config.active_label,
                        Config.active_comment,
                        "bumblebee-indicator", notify)

    def set_status(self, status, label, comment, icon, notify):
        self.card_state = status
	self.statusicon.set_from_file(IconSet().get_path(icon)) 
        if notify == True: self.notify_state(label, comment, icon)
        self.switch.set_label(label)
        self.switch.set_active(status)

# FUNCTION TO DEFINE THE APPLICATIONS SETTING LINK IN THE INDICATOR

    def app_configure(self,widget):
        Applications_settings()

# FUNCTION TO LAUNCH THE APPS WITHIN THE INDICATOR
    def call_app(self, widget, app_exec):
#FIXME There is a problem when closing the launched app and when the indicator has been closed: the indicator is still running : What a daemon!!
        subprocess.Popen(app_exec,shell=False)

    def quit(self, widget, data=None):
        gtk.main_quit()
# MAIN LOOP LAUNCHING A STATE CHECK EVERY TWO SECONDS
    def main(self):
        self.state_checker()
#FIXME It would be nice to avoid this loop : Maybe by using a signal emitted by the system
        #gtk.timeout_add(2000,self.state_checker)
        gobject.timeout_add_seconds(2, self.state_checker)
        gtk.main()

if __name__ == "__main__":
    indicator = BumblebeeIndicator()
    indicator.main()
