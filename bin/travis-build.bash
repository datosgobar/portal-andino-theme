#!/usr/bin/env bash

THEME_PATH=$(pwd)
git clone "https://github.com/datosgobar/portal-andino"

cd portal-andino/
sudo ./dev.sh complete_up --theme_volume_src $THEME_PATH
