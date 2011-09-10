#!/bin/bash
#This is a small script to internationalize bumblebee-ui in different language
#This script take only one argument : the folder name of the created language files
if [ -n "$1" ]; then
	LOCALE_DIR="$1/LC_MESSAGES"
	if [ -f "$LOCALE_DIR/bumblebee-ui.po" ]; then
		msgfmt -o "$LOCALE_DIR/bumblebee-ui.mo" "$LOCALE_DIR/bumblebee-ui.po"
		echo "The compiled language file has been created"
	else
		echo "You need to create a bumblebee-ui.po file by copying bumblebee-ui.pot in $1/LC_MESSAGES folder"
		echo "Then you have to write you're own translation string in this file."
		exit
	fi
else
	echo "This script need one argument corresponding to the language folder, by sample fr_FR."
	echo "The language folder must be named like this using language code and land code : language_LAND"
fi
