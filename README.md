# BTWifi-AutoLogin
Automatically sign in to BT Wifi hotspots across the UK

Code in this repository is based on [this gist](https://gist.github.com/sscarduzio/05ed0b41d6234530d724) and [this gist](https://gist.github.com/vaijab/3b3001cf70a7e8abe3f5).

## Getting Started
### Manual Sign-In
Open the `btwifi.sh` file in a text editor, entering your BT Broadband username and password into the USER and PASS variables. Run the script to sign-in.

### Automatic Sign-In
Create a soft link to `btwifi.sh` in the `/usr/bin` folder, then run `systemctl enable`, providing a full path to the `btwifi.service` file.
