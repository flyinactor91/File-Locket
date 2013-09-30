File Locket
=========
**v2.0.1a [2013-09-30]**

Simple file storage service to store, access, and delete files.

Created by Michael duPont ([flyinactor91.com](https://flyinactor91.com))

Python 2.7.5 - Unix

Found at [https://github.com/flyinactor91/File-Locket](https://github.com/flyinactor91/File-Locket)

-------------

Client
-------
Command prompt or terminal input

Saves username, sessionID, and user preferences between sessions

* User prefs: senddir , destdir , startalert

User can set different send and dest folders for files to/from server

* Defaults to curdir but saves send/dest between sessions

Server
--------
File encryption on the list to implement

Database stored as two dictionaries and saved between command loops

Server log is recorded into .txt (default) or to the terminal

Critical errors (problems with code, not user error) are tracked without causing server crash

Security
----------
Passwords are salted and hashed client side so server never sees the plain text

All password entry doesn't show text in terminal

User's sessionID changes upon new login

* User can only transmit new commands on one machine at a time

* Large file upload will continue even if user moves to new terminal changing sessionID

Admin tools
---------------
Client asked for admin password which must match encrypted server password

Admin can shut down server remotely

Adminclear saves a backup of database by renaming ~bin~ and making new blank bin folder

* Previous backup must be manually removed before next clear

Admin can send a messages to users using the notification system

* Can adapt into automatic alerts (ex. shared file, maintenance, storage cap)

Upgrades for future releases
------------------------------------
* Folder support

* Up arrow yields previous entries

* File encryption (user-held keys)

* User account support/authentication

* Optional GUI (much later)



Available commands
--------------------------
**send   -s** ---- Send files to the server

**get    -g** ---- Get files from the server

**view   -v** ---- View stored files

**del    -d** ---- Delete files on the server

**ver    -v** ---- File version options

**arc    -a** ---- Get all files on server

**set    -us** --- Change program settings

**stat   -st** --- Get info about about files

**notid  -n** ---- Notification options

**test   -t** ---- Test server connection

**login  -li** --- Login from terminal

**logout -lo** --- Logout and quit

**quit   -q** ---- Quit without logging out

*Admin Tools (requires server pw):*

**showusers  A-su** --- Returns all saved usernames

**serverstat A-ss** --- Returns server statistics

**sendnotif  A-sn** --- Send alert to users

**clear      A-cl** --- Clears all server lib data

**shutdown   A-sd** --- Shuts down server and saves data

Release Notes
------------------
1.0.0 [2013-03-28]

* Initial release

1.1.0 [2013-04-10]

* File versioning

* Source and destination directory control

* File transfer improvements

* Server improvements

1.1.1 [2013-07-23]

* User and server statistics

* Recieve file archive

* Client and Server improvements

1.2.0 [2013-07-17]

* Windows/NT support

* '#up' for directory control

* Signup verifies password

* More reliable file transfers

* Bug fixes

* Code reduction

1.3.0 [2013-08-07]

* Notification system

* Up/Download progress bar

* Check version on startup

* Checksum checks for all transfers

* Client and Server improvements

* Bug fixes

1.3.1 [2013-09-05]

* Send, get, del multiple files

* Admin send multi-user alert

* Bug fixes

* Code readability

2.0.0 [2013-09-27]

* Call from command line

* Completely reworked client architecture

* Command name changes and shortcuts

2.0.1a [2013-09-30]

* New setup file

* filelocket added to linux PATH

* Consolidated data to ~/.filelocket
