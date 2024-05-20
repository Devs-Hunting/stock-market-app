#!/bin/sh

set -e

RED="\033[0;31m"
NC="\033[0m" # No colour

cd /app

printf "${RED}Be careful all data will be cleared and base fixtures will be reloaded.\nThis action cannot be undone.\n${NC}"
read -p "Do you wish to reset database data? (yes/no): " answer
case ${answer} in
  Yes|yes )
    echo yes | python manage.py flush > /dev/null
    echo Database cleared.
    echo Initialising administrator...
    python manage.py initadmin > /dev/null
    echo Loading fixtures...
    python manage.py load_fixtures > /dev/null
    echo Database has been reset successfully.
  ;;
  * )
    echo Action cancelled.
  ;;
esac
