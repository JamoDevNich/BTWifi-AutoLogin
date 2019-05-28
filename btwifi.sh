#!/bin/bash

# CONF

APP='btwifi'
DBG=true
USER=''
PASS=''

# END CONF

IS_LOGGED_IN=$(wget 'https://www.btopenzone.com:8443/home' --timeout 30 -O - 2>/dev/null | grep 'accountLogoff')

if [ "$IS_LOGGED_IN" ]
then
  exit 0 #[[ $DBG ]] && logger -t $APP -s 'Already logged in'

else
  [[ $DBG ]] && logger -t $APP -s 'Signing in to network'
  OUT=$(wget -qO - --post-data "username=$USER&password=$PASS&provider=tbb" 'https://www.btopenzone.com:8443/tbbLogon')
  ONLINE=$(echo $OUT | grep "accountLogoff" )
  if [ "$ONLINE" ]
  then
    [[ $DBG ]] && logger -t $APP -s 'Sign-in completed successfully'
  else
    [[ $DBG ]] && logger -t $APP -s 'Sign-in failed'
  fi
fi
