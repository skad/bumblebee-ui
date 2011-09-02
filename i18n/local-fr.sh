#!/bin/bash
here=`dirname "$(cd ${0%/*} && echo $PWD/${0##*/})"`
cd $here
msgfmt messages.po
mv -f messages.mo ./fr_FR/LC_MESSAGES/bumblebee-ui.mo