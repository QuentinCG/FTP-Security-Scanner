#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
  FTP(S) security test class

   - Connect with specific ip+port
   - Grab welcome banner
   - Login with optional login+password
   - Get full list of accessible folders and files
   - Check folder & file creation & deletion rights
   - Check maximum rights in root folder (000 -> 777)
"""
__author__ = 'Quentin Comte-Gaz'
__email__ = "quentin@comte-gaz.com"
__license__ = "MIT License"
__copyright__ = "Copyright Quentin Comte-Gaz (2016)"
__python_version__ = "2.7+ and 3.+"
__version__ = "0.1 (2016/08/18)"
__status__ = "Usable for all projects"

import ftplib
import logging
import time

import random

# Import StringIO (compatible with 2.7+ and 3.+)
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


class ftpSecurityTest:
  """FTP security test class
  """
  def __init__(self):
    self.ftp_instance = ftplib.FTP()
    self.ip = "127.0.0.1"
    self.port = 21


  def __getContent(self, max_depth = -1, max_files = -1, optimized = True,
                   count = -1, depth = 0):
    """Get list of content from the FTP server (recursive)

    Keyword arguments:
      max_depth -- (int, optional) Maximum depth before stopping the scan (-1 for no limit)
      max_files -- (int, optional) Maximum number of file to scan before stopping the scan (-1 for no limit)
      optimized -- (bool, optional) Use optimized algorithm to be faster and less suspicious (but some folders not be scanned)
      count -- (int, optional) Internal value (number of files already found)
      depth -- (int, optional) Internal value (current depth)

    return: ({string: {...}}) Recursive dictionary containing all scanned files with folders as keys (files are keys of empty elements)
    """
    # TODO: Improve error handling
    if max_files >= 0:
      count = count + 1
      if count >= max_files:
        return '+'
    if max_depth >= 0 and depth > max_depth:
      return '+'

    level = {}
    #try:
    for entry in (path for path in self.ftp_instance.nlst() if path not in ('.', '..')):
      entry_split = entry.split("/")
      name = entry_split[len(entry_split) - 1]
      try:
        # Try to do go in the supposed folder only if the name doesn't seems
        # to be a file (First char is a dot or no dot at all -> is most likely a folder)
        # THIS IS NOT A PERFECT SOLUTION since the script may miss folders BUT
        # it prevents numerous useless calls to the ftp server AND there is no
        # fast, clean and universal way to check if the specific element is a
        # file or a folder.
        # This will HIGHLY optimize the time to grab elements and will make the
        # script less suspicious from server point of view.
        if name.find(".") <= 0 or (not optimized):
          self.ftp_instance.cwd(entry)
          level[name] = self.__getContent(max_depth, max_files, count, depth + 1)
          self.ftp_instance.cwd('..')
        else:
          level[name] = ''
      except (ftplib.error_perm, ftplib.error_temp, ftplib.error_reply, ftplib.error_proto):
        level[name] = ''
    #except (ftplib.error_perm, ftplib.error_temp, ftplib.error_reply, ftplib.error_proto):
    #  pass

    return level


  def connect(self, ip, port = 21, timeout = 5):
    """Connect to the FTP server

    Note: This will first disconnect from current FTP server

    Keyword arguments:
      ip -- (string) Server IP
      port -- (int, optional) Port for FTP protocol
      timeout -- (int, optional) Maximum time to wait server to answer connexion query

    return: (bool) Connected to FTP server
    """
    self.ip = ip
    self.port = port

    # Quit previous instance (if connect() was already called)
    self.quit()

    # Check if the FTP server is active
    try:
      self.ftp_instance.connect(ip, port, timeout)
    except Exception:
      # FTP server not responding
      return False

    # The FTP server is responding
    return True


  def quit(self):
    """Disconnect from the FTP server"""
    try:
      self.ftp_instance.quit()
    except Exception:
      # Whatever happens is not really important since communication is terminated with the server
      pass


  def login(self, login = "anonymous", password = "anonymous@"):
    """Login to the FTP server (by default, login on public FTP server)

    Note: connect() must be called first

    Keyword arguments:
      login -- (string, optional) Login associated with {password} to connect to the FTP server
      password -- (string, optional) Password associated with {login} to connect to the FTP server

    return: (bool) Logged to FTP server
    """
    try:
      #Check if the FTP server is secured
      self.ftp_instance.login(login, password)
    except Exception:
      # Not logged in
      return False

    # Logged in FTP server
    return True


  def getWelcomeBanner(self):
    """Get the welcome banner from the server

    Note: connect() must be called first

    return: (string) Welcome banner
    """
    return self.ftp_instance.getwelcome()


  def getContent(self, max_depth = -1, max_files = -1):
    """Get list of content (files and folders) from the FTP server

    Note: connect() and login() must be called first

    Keyword arguments:
      max_depth -- (int, optional) Maximum depth before stopping the scan (-1 for no limit)
      max_files -- (int, optional) Maximum number of file to scan before stopping the scan (-1 for no limit)

    return: ({string: {string:string, ...}, ...) Dictionary containing all scanned files with files and folders as keys and sub-files and sub-folders as content (recursive logic)
    """
    return self.__getContent(max_depth, max_files)


  def checkWriteAndDeleteAccess(self, dir_name="folder_to_delete_"+str(random.randrange(100000000, 900000000)),
                                filename="file_to_delete_"+str(random.randrange(100000000, 900000000))):
    """Check write & delete access of files and folders in root directory

    Note: connect() and login() must be called first

    Keyword arguments:
      dir_name -- (string, optional) Name of the directory to create and delete
      filename -- (string, optional) Name of empty file to create and delete

    return: (bool, bool, bool, bool) Can create/upload dir, Can delete dir, Can create/upload file, Can delete file
    """
    can_create_dir = False
    can_delete_dir = False
    can_upload_file = False
    can_delete_file = False

    # Test directory creation and deletion
    try:
      self.ftp_instance.mkd(dir_name)
    except ftplib.error_perm:
      pass
    else:
      can_create_dir = True
      try:
        self.ftp_instance.rmd(dir_name)
      except ftplib.error_perm:
        pass
      else:
        can_delete_dir = True

    # Test file upload and deletion
    try:
      self.ftp_instance.storbinary("STOR "+filename, StringIO(''))
    except ftplib.error_perm:
      pass
    else:
      can_upload_file = True
      try:
        self.ftp_instance.delete(filename)
      except ftplib.error_perm:
        pass
      else:
        can_delete_file = True

    result = [can_create_dir, can_delete_dir, can_upload_file, can_delete_file]
    return result


  def getMaxRights(self):
    """Get the maximum Unix rights for file and folder in in root directory

    Note: connect() and login() must be called first

    return: (int, int) Dir rights, File rights (-1 if server does not contain
            folder/file or does not accept 'DIR' cmd, else: value between 000 and 777)
    """
    data = []
    is_valid_dir = False
    is_valid_file = False

    try:
      # Get the list of files and dir in the directory
      self.ftp_instance.dir(data.append)
    except ftplib.error_perm:
      return -1, -1

    if len(data) <= 0:
      return -1, -1

    # Extract right information (000->777) from all lines
    result_dir = [False, False, False, False, False, False, False, False, False]
    result_file = [False, False, False, False, False, False, False, False, False]
    for line in data:
      if len(line) > 10:
        # Be sure the element to check is a file ('-') or a folder ('d') and not a link
        # (A link will always have "full right" even if it means 'nothing')
        if line[0] == '-' or line[0] == 'd':
          if line[0] == 'd':
            is_valid_dir = True
          else:
            is_valid_file = True
          for i in range(1, 10):
            element = line[i]
            right_type = i%3
            if (element == 'r' and right_type == 1) or \
               (element == 'w' and right_type == 2) or \
               ((element == 'x' or element == 'X' or element == 's') and right_type == 0):
              if line[0] == 'd':
                result_dir[i - 1] = True
              else:
                result_file[i - 1] = True

    if is_valid_dir == False and is_valid_file == False:
      return -1, -1

    # Transform the table of right into integer between "000" and "777" (right)
    if is_valid_dir:
      rights_dir = 0
      if result_dir[0] == True:
        rights_dir = rights_dir + 400
      if result_dir[1] == True:
        rights_dir = rights_dir + 200
      if result_dir[2] == True:
        rights_dir = rights_dir + 100

      if result_dir[3] == True:
        rights_dir = rights_dir + 40
      if result_dir[4] == True:
        rights_dir = rights_dir + 20
      if result_dir[5] == True:
        rights_dir = rights_dir + 10

      if result_dir[6] == True:
        rights_dir = rights_dir + 4
      if result_dir[7] == True:
        rights_dir = rights_dir + 2
      if result_dir[8] == True:
        rights_dir = rights_dir + 1
    else:
      rights_dir = -1

    if is_valid_file:
      rights_file = 0
      if result_file[0] == True:
        rights_file = rights_file + 400
      if result_file[1] == True:
        rights_file = rights_file + 200
      if result_file[2] == True:
        rights_file = rights_file + 100

      if result_file[3] == True:
        rights_file = rights_file + 40
      if result_file[4] == True:
        rights_file = rights_file + 20
      if result_file[5] == True:
        rights_file = rights_file + 10

      if result_file[6] == True:
        rights_file = rights_file + 4
      if result_file[7] == True:
        rights_file = rights_file + 2
      if result_file[8] == True:
        rights_file = rights_file + 1
    else:
      rights_file = -1

    return rights_dir, rights_file

# Have input() function compatible with python 2+ and 3+
try:
  input = raw_input
except NameError:
  pass

def main():
  """Demo of the IP utility functions"""

  logger = logging.getLogger()
  logger.setLevel(logging.DEBUG)

  print("\n----------------------------------------------------")
  print("-----------FTP security test class demo-------------")
  print("----------------------------------------------------")

  ftp_test = ftpSecurityTest()
  ip = str(input("IP: "))
  port = int(input("Port: "))
  timeout = 5

  print("\n----------------Connect to FTP server---------------")
  is_connected = ftp_test.connect(str(ip), int(port), timeout)
  print("Connected to "+ip+" (port "+str(port)+"): "+str(is_connected))

  is_logged = False
  if is_connected:
    print("\n-----------------Grab Welcome Banner----------------")
    print("Welcome banner:\n"+str(ftp_test.getWelcomeBanner()))

    print("\n-----------------------Login------------------------")
    login = input("Username (empty for anonymous):")
    if login == "":
      is_logged = ftp_test.login()
    else:
      password = input("Password:")
      is_logged = ftp_test.login(login, password)
    print("Logged: "+str(is_logged))

  if is_logged:
    print("\n-Check file and folder creation and deletion rights-")
    operation_ok = True
    try:
      create_folder, delete_folder, create_file, delete_file = ftp_test.checkWriteAndDeleteAccess()
    except ftplib.all_errors as e:
      print("An error occurred ('"+str(e)+"'), trying again...")
      # The error may be due to socket not released, a small delay is needed
      time.sleep(1)
      try:
        create_folder, delete_folder, create_file, delete_file = ftp_test.checkWriteAndDeleteAccess()
      except ftplib.all_errors as e:
        operation_ok = False
        print("Impossible to get the creation/deletion rights of the FTP server ('"+str(e)+"')...")

    if operation_ok:
      print("Can create folder: "+str(create_folder))
      print("Can delete folder: "+str(delete_folder))
      print("Can create file: "+str(create_file))
      print("Can delete file: "+str(delete_file))

    print("\n--Check max right of all files/folders in root folder--")
    operation_ok = True
    try:
      max_rights_dir, max_rights_file = ftp_test.getMaxRights()
    except ftplib.all_errors as e:
      print("An error occurred ('"+str(e)+"'), trying again...")
      # The error may be due to socket not released, a small delay is needed
      time.sleep(1)
      try:
        max_rights_dir, max_rights_file = ftp_test.getMaxRights()
      except ftplib.all_errors as e:
        operation_ok = False
        print("Impossible to get the max rights of the FTP server ('"+str(e)+"')...")

    if operation_ok:
      if max_rights_dir < 0:
        print("Max rights (folders): Server does not contain folders or operation not allowed")
      else:
        print("Max rights (folders): "+str(max_rights_dir))

      if max_rights_file < 0:
        print("Max rights (files): Server does not contain files or operation not allowed")
      else:
        print("Max rights (files): "+str(max_rights_file))

    print("\n----Get list of all accessible files and folders----")
    operation_ok = True
    try:
      content = ftp_test.getContent()
    except ftplib.all_errors as e:
      print("An error occurred ('"+str(e)+"'), trying again...")
      # The error may be due to socket not released, a small delay is needed
      time.sleep(1)
      try:

        content = ftp_test.getContent()
      except ftplib.all_errors as e:
        operation_ok = False
        print("Impossible to get the content of the FTP server ('"+str(e)+"')...")

    if operation_ok:
      print(content)

  print("\n----------------------------------------------------")
  print("-------------------End of demo----------------------")
  print("----------------------------------------------------\n")

if __name__ == "__main__":
  main()
