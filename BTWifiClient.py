#!/usr/bin/python3
import datetime;
import enum;
import time;
from urllib import request, parse;

VERSION = "0.1.0";


class Enums:
    """Contains all enum type classes used in the script"""
    class BtPortalStatus(enum.Enum):
        """Enums representing the current state of the BT Portal"""
        USER_LOGGED_IN = 0;
        USER_LOGGED_OUT = 1;
        UNKNOWN = 2;

    class BtPortalLogonProviders(enum.Enum):
        """Enums representing available BT Portal logon providers"""
        # https://gist.github.com/itay-grudev/d3d4eb0dc4e239d96c84#gistcomment-1825319
        BT_BROADBAND = "tbb";
        BT_BUSINESS_BROADBAND = "business";
        BT_WIFI = "btoz";
        FON = "fon";
        UNSET = None;


class BtPortalResponseObject:
    """Returned by the BtPortalProvider containing the result of a http request"""

    def __init__(self, url: str, status: Enums.BtPortalStatus, response_html: str):
        self.url = url;
        self.status = status;
        self.response_html = response_html;


class BtPortalProvider:
    """Simplifies interaction with the BT Wifi web portal"""

    def __init__(self, portal_address: str, debug_enabled=False):
        self.__portal_base_address = portal_address if portal_address[len(
            portal_address)-1:] == "/" else portal_address + "/";
        self.__debug_enabled = debug_enabled;
        self.__debug_str = "BtPortalProvider DEBUG: ";

    def get_portal_page(self, path: str, data_dictionary=None) -> BtPortalResponseObject:
        """Retrieves a page from the BT Wifi Portal. Throws exception if portal status is unknown."""
        get_portal_homepage_result = self.__http_request_handler(self.__portal_base_address);
        if get_portal_homepage_result.status is Enums.BtPortalStatus.UNKNOWN:
            raise Exception("Portal status unknown - it may have been updated!");
        elif path is None:
            return get_portal_homepage_result;
        else:
            return self.__http_request_handler("%s%s" % (self.__portal_base_address, path), data_dictionary);

    def __http_request_handler(self, url: str, data_dictionary=None) -> BtPortalResponseObject:
        """Internal handler HTTP requests to the portal. Throws exception if portal appears ingenuine."""
        try:
            url, status_code, html_body = self.__http_request_send(url, data_dictionary);
            if status_code != 200:
                raise Exception("HTTP Response code was %s" % status_code);
            elif "BT Wi-fi" not in html_body and "btwifi.com" not in html_body:
                raise Exception("Page does not appear to be a BT Wifi Portal!");
            else:
                portal_status = Enums.BtPortalStatus.UNKNOWN;
                if "<!-- Hack for BT WIFI app to find bt wifi logoff page. -->" in html_body:
                    portal_status = Enums.BtPortalStatus.USER_LOGGED_IN;
                elif "tbb_logon_form" in html_body:
                    portal_status = Enums.BtPortalStatus.USER_LOGGED_OUT;
                if self.__debug_enabled:
                    print("%surl=%s, portal_status=%s, len(html_body)=%s, data_dictionary is None=%s" %
                          (self.__debug_str, url, portal_status, len(html_body), data_dictionary is None));
                return BtPortalResponseObject(url, portal_status, html_body);
        except Exception as ex:
            raise Exception("Failed to access BT Portal! Error: %s" % ex);

    def __http_request_send(self, url: str, data_dictionary=None) -> tuple:
        """Abstraction method for a HTTP library to perform a HTTP request"""
        post_data = None if data_dictionary is None else bytes(parse.urlencode(data_dictionary).encode());
        if self.__debug_enabled:
            print("%surl=%s" % (self.__debug_str, url));
        response = request.urlopen(url, post_data, 5);
        return (url, response.getcode(), bytes(response.read()).decode("utf8"));


class Session:
    """Handles a BT Wifi user session"""

    def __init__(self, bt_portal_provider: BtPortalProvider, debug_enabled=False):
        self.__bt_portal_provider = bt_portal_provider;
        self.__username = str();
        self.__password = str();
        self.__provider_type = Enums.BtPortalLogonProviders.UNSET;
        self.__debug_enabled = debug_enabled;
        self.__debug_str = "Session DEBUG: ";
        pass;

    @property
    def is_logged_in(self) -> bool:
        """Returns True if the current session is logged in, otherwise returns False"""
        portal_response = self.__bt_portal_provider.get_portal_page(None);
        if portal_response.status is Enums.BtPortalStatus.USER_LOGGED_IN:
            return True;
        elif portal_response.status is Enums.BtPortalStatus.USER_LOGGED_OUT:
            return False;
        else:
            return False;

    def start_session(self, provider_type: Enums.BtPortalLogonProviders, username: str, password: str) -> Enums.BtPortalStatus:
        """Performs a login request with the parameters given. A session is considered 'started' if the login is successful"""
        if self.__debug_enabled:
            print("%sprovider_type=%s, username=%s, password=%s" %
                  (self.__debug_str, provider_type.value, username, password));
        user_details_dict = {"username": username, "password": password, "provider": provider_type.value};
        logon_result = self.__bt_portal_provider.get_portal_page("tbbLogon", user_details_dict);

        if logon_result.status is Enums.BtPortalStatus.USER_LOGGED_IN:
            self.__username = username;
            self.__password = password;
            self.__provider_type = provider_type;

        return logon_result.status;

    def try_logout(self) -> bool:
        """Logs out the current session"""
        if self.is_logged_in:
            _ = self.__bt_portal_provider.get_portal_page("accountLogoff/home?confirmed=true");
            return not self.is_logged_in;
        else:
            return True;
        return False;

    def restart_session(self) -> Enums.BtPortalStatus:
        """Calls start_session with previously provided parameters. Raises exception if session_start has not previously started a session"""
        if self.__provider_type is not None and self.__username != "" and self.__password != "":
            return self.start_session(self.__provider_type, self.__username, self.__password);
        else:
            raise Exception("Attempted to restart a session without user credentials");
        pass;


if __name__ == "__main__":
    """Small console app using the BtPortalProvider and Session classes to handle a BT Wifi session"""
    var_provider = Enums.BtPortalLogonProviders.UNSET;  # Your logon provider
    var_username = "";                                  # Your BT Wifi username
    var_password = "";                                  # Your BT Wifi password

    def printx(output: str) -> None:
        print("%s: %s" % (datetime.datetime.now(), output));

    def keep_session_active(session: Session):
        while(True):
            try:
                printx("Checking current session");
                if session.is_logged_in:
                    printx("Already logged in");
                else:
                    printx("Not logged in, restarting session");
                    session.restart_session();
                time.sleep(20);
            except KeyboardInterrupt:
                raise KeyboardInterrupt();
            except Exception as ex:
                printx("Caught exception: %s" % ex);

    def main():
        printx("Starting BTWifiClient %s" % VERSION);
        try:
            printx("Setting up");
            bt_portal_provider = BtPortalProvider("https://www.btopenzone.com:8443", debug_enabled=False);
            session = Session(bt_portal_provider, debug_enabled=False);
            if session.is_logged_in:
                printx("Already logged in");
                keep_session_active(session);
            else:
                printx("Logging in");
                session_logon_status = session.start_session(var_provider, var_username, var_password);
                if session_logon_status is Enums.BtPortalStatus.USER_LOGGED_IN:
                    keep_session_active(session);
                else:
                    raise Exception("Logon failed");
        except KeyboardInterrupt:
            printx("Signing out (KeyboardInterrupt)");
            printx("Signed out sucessfully" if session.try_logout() is True else "Signing out failed");
        except Exception as ex:
            printx("Exception occured: %s" % ex);
        printx("Exiting");

    main();
