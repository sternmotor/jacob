# Chrome Debug Console

Parse POST requests for logging in to some web application - used for web scenario monitoring here.

Press `F12` key in chroe browser for entering the build in debugger, then
* network > headers > yes, preserve log
* login to web site, submit "login" command
* watch requests:
    * requesturi > first hop redirect 302
    * response > find location in response in list on left side of debugger (for example `index.php`), click entry
        * General > 200 OK
            * Request Method POST:
                * Form data > view source <<< thats it
* run "Clear" in chrome debugger toolbar after each analysis
