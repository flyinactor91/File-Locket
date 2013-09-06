File Locket
=========
**v1.3.1 [2013-09-05]**

Simple file storage service to store, access, and delete files.

Created by Michael duPont ([flyinactor91.com](https://flyinactor91.com))

Python 2.7.5 - Unix

Found at [https://github.com/flyinactor91/File-Locket](https://github.com/flyinactor91/File-Locket)

-------------

Client
-------
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
**sendfile** ---- Send a file to the server

**getfile** ------ Get a file from the server

**viewfiles** --- View stored files

**delfile** ------ Delete a file on the server

**versions** --- File version options

**archive** ---- Get all files on server (versions if true)

**set** ---------- Change program settings

**stats** -------- Get info about about files

**alerts** ------- Alert options

**test** --------- Test server connection

**logout** ----- Logout and quit

**quit** --------- Quit without logging out

*Admin Tools (requires server pw):*

**adminshowusers** --- Returns all saved usernames

**adminserverstats** --- Returns server statistics

**adminsendalert** ----- Send alert to users

**adminclear** ----------- Clears all server lib data

**adminshutdown** ---- Shuts down server and saves data

Typing #quit into a prompt exits that prompt

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
