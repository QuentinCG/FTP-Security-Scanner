# FTP scanner

## What is it?

This python tool library is designed to check if a FTP(S) server is secured or not
and the kind of information and rights you have with or without credentials.

It can also check the FTP(S) server security of a wide IP range (even the full IPv4 network).

It is multi-platform and compatible with python 2.7+ and 3+.

IMPORTANT NOTE: This scanner is working only for unique IP at the moment.


<img src="ftp.png" width="200">


## Examples

<a target="_blank" href="https://github.com/QuentinCG/FTP-Security-Scanner/blob/master/utils/ftp.py">Scan one IP with a specific port:</a>
<img src="example_one_ip.jpg" width="400">


More examples will come soon.


## How to install

This tool does not need any additional library.

1) Download this repository
2) Launch the Python file that matches your needs:
   - If you need to check only one FTP server: <a target="_blank" href="https://github.com/QuentinCG/FTP-Security-Scanner/blob/master/utils/ftp.py">ftp.py</a>
   - If you need to check a wide IP range: No implemented yet


## What is check with this tool?

For every scanned IP:
 - Is FTP port open?
 - Is it possible to log in the FTP server as anonymous user (or with specific login and password)?
 - If connected:
   * Grab the welcome banner (can contain information of deprecated FTP(s) servers)
 - If logged in:
   * Grab full or partial list of accessible files and folders in the server
   * Check write/read rights on file/folder
   * Check Unix permissions on root folders and files (000 to 777)


##TODO list

  - [CRITICAL] Implement the wide IP range scanner (with threads)
  - [CRITICAL] Add possibility to store all data found in wide IP range scan
  - [ENHANCEMENT] Better handle exceptions in <a target="_blank" href="https://github.com/QuentinCG/FTP-Security-Scanner/blob/master/utils/ftp.py">ftp.py</a> in order to be more robust when commincating with bad FTP servers.


## License

This project is under MIT license. This means you can use it as you want (just don't delete the library header).


## Contribute

If you want to add more examples or improve the library, just create a pull request with proper commit message and right wrapping.
