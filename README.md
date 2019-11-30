# BTWifi-AutoLogin
Automatically sign in to BT Wifi hotspots across the UK

## Getting Started
### Manual Sign-In
Open the `BTWifiClient.py` file in a text editor, entering your BT Broadband username and password into the `var_username` and `var_password` variables. Run the script to sign-in.

### Automatic Sign-In
Create a soft link to `btwifi.sh` in the `/usr/bin` folder, then run `systemctl enable`, providing a full path to the `btwifi.service` file.

## Development
This implementation is based on [this gist](https://gist.github.com/sscarduzio/05ed0b41d6234530d724) and [this gist](https://gist.github.com/vaijab/3b3001cf70a7e8abe3f5).
