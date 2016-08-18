#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
  IP handling library

  Get host from IP, ping host, get public IP range divided in any
  number of ranges, loop to call all IPs in specific IP range...
"""
__author__ = 'Quentin Comte-Gaz'
__email__ = "quentin@comte-gaz.com"
__license__ = "MIT License"
__copyright__ = "Copyright Quentin Comte-Gaz (2016)"
__python_version__ = "2.7+ and 3.+"
__version__ = "1.0 (2016/08/12)"
__status__ = "Usable for all projects"

import os
import platform
import socket
import struct
import subprocess
import shlex
import logging

def ipToInt(ip):
  """Transform a string IP into an integer (long)

  Keyword arguments:
    ip -- (string) IP as a string ("xxx.xxx.xxx.xxx")

  return: (long) IP number
  """
  return struct.unpack("!L", socket.inet_aton(ip))[0]

def intToIp(n):
  """Transform an integer into the related IP

  Keyword arguments:
    n -- (long) IP number

  return: (string) IP as a string ("xxx.xxx.xxx.xxx")
  """
  return socket.inet_ntoa(struct.pack('!I', n))

def getHostFromIp(ip):
  """Return the reverse DNS of the IP

  Keyword arguments:
    n -- (long) IP number

  return: (string) Hostname (empty if no hostname found)
  """
  host = ""
  str_ip = intToIp(ip)
  try:
    host = socket.gethostbyaddr(str_ip)[0]
  except socket.error as e:
    logging.error("No host found for IP "+str_ip+": "+str(e))
  return host

def getValidPublicIpRange():
  """Get list of all valid public IP range

  return: ([[long, long],  (...)]) List of IP range
  """
  # IP range taken from https://en.wikipedia.org/wiki/Reserved_IP_addresses
  return [[16777216, 167772159],   # 1.0.0.0 to 9.255.255.255
          [184549376, 1681915903], # 11.0.0.0 to 100.63.255.255
          [1686110208, 2130641151],# 100.128.0.0 to 126.255.255
          [2147483648, 2851995647],# 128.0.0.0 to 169.253.255.255
          [2852061184, 2886729727],# 169.255.0.0 to 172.15.255.255
          [2887778304, 3221225471],# 172.32.0.0 to 191.255.255.255
          [3221225728, 3221225983],# 192.0.1.0 to 192.0.1.255
          [3221226240, 3227017983],# 192.0.3.0 to 192.88.98.255
          [3227018240, 3232235519],# 192.88.100.0 to 192.167.255.255
          [3232301056, 3323068415],# 192.169.0.0 to 198.17.255.255
          [3323199488, 3325256703],# 198.20.0.0 to 198.51.99.255
          [3325256960, 3405803775],# 198.51.101.0 to 203.0.112.255
          [3405804032, 3744923903] # 203.0.114.0 to 223.55.255
         ]

def getNumberOfPublicIp():
  """Get the total number of public IP

  return: (long) Number of public IP
  """
  #No need to calculate this constant everytime
  return 3689020672
  # Real implementation:
  #ranges = getValidPublicIpRange()
  #number_of_ip = 0
  #for range in ranges:
  #  number_of_ip = number_of_ip + (range[1] - range[0] + 1)
  #return number_of_ip

def getValidPublicIps(ip_begin, ip_end):
  """Get a list of public IP range between 2 specific IPs

  Keyword arguments:
    ip_begin -- (long) First IP of the range
    ip_end -- (long) Last IP of the range

  return: ([[long, long], (...)]) List of public IP range between ip_begin and ip_end
  """
  valid_ip_ranges = []

  if ip_begin > ip_end:
    logging.error("Wrong IP range (IP "+intToIp(ip_end)+" should be before "+intToIp(ip_begin)+")")
    return valid_ip_ranges

  for public_range in getValidPublicIpRange():
    if public_range[0] <= ip_end and public_range[1] >= ip_begin:
      #IPs have at least one IP in common
      local_ip_begin = max(ip_begin, public_range[0])
      local_ip_end = min(ip_end, public_range[1])
      if local_ip_begin <= local_ip_end:
        valid_ip_ranges.append([local_ip_begin, local_ip_end])
  return valid_ip_ranges

def getDividedPublicIpRange(approximated_number_of_range):
  """Get approximately approximated_number_of_range ranges of full public IP of approximatelly the same size

  Keyword arguments:
    approximated_number_of_range -- (int) Approximate number of range the function should return
                                          (a value < 100 will not give optimal result)

  return: ([[long, long], (...)]) List of public IP range
  """
  public_ip_ranges = getValidPublicIpRange()
  if approximated_number_of_range <= len(public_ip_ranges):
    return public_ip_ranges

  ranges = []
  best_nbr_of_ip_per_range = getNumberOfPublicIp()/approximated_number_of_range
  for public_ip_range in public_ip_ranges:
    remaining_ip = public_ip_range[1] - public_ip_range[0] + 1
    while remaining_ip > 0:
      if remaining_ip >= best_nbr_of_ip_per_range:
        ranges.append([public_ip_range[1] - remaining_ip + 1,
                      public_ip_range[1] - remaining_ip + best_nbr_of_ip_per_range])
        remaining_ip = remaining_ip - best_nbr_of_ip_per_range
      else :
        ranges.append([public_ip_range[1] - remaining_ip + 1, public_ip_range[1]])
        remaining_ip = 0
  return ranges

def ping(host, timeout = 2):
  """Ping a server

  Keyword arguments:
    host -- (string) Host to ping
    timeout -- (int, optional) Maximum time in sec to wait an answer

  return: (bool) Ping successful
  """
  is_up = False

  #Ping parameters are function of the OS
  ping_cmd = "ping -n 1 -w "+str(1000 * timeout)+ " " \
             +host if platform.system().lower()=="windows" else \
             "ping -c 1 -W "+str(timeout)+ " "+host

  try:
    proc = subprocess.Popen(shlex.split(ping_cmd), stdout=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    is_up = (proc.returncode == 0)
  except Exception as e:
    logging.error("Unexpected error: "+str(e))

  return is_up

def ipLoop(ip_begin, ip_end, check_function):
  """Call a function for all IP in specific range

  Keyword arguments:
    ip_begin -- (long) First IP for the loop
    ip_end -- (long) Last IP for the loop
    check_function -- (function((long)current_ip, (int)count_loop-1)) Function to call for every IP

  return: (bool) Parameters are valid
  """
  char_ip_begin = intToIp(ip_begin)
  char_ip_end = intToIp(ip_end)
  count = 0

  if ip_begin > ip_end:
    logging.error("Wrong IP range (IP "+char_ip_begin+" should be before "+char_ip_end+")")
    return False

  logging.debug("Begin IP loop from "+char_ip_begin+" to "+char_ip_end)

  # xrange was renamed range in python3+
  try:
    xrange
  except NameError:
    xrange = range

  for ip in xrange(ip_begin, ip_end + 1):
    check_function(ip, count)
    count = count + 1
  logging.debug("Loop from "+char_ip_begin+" to "+char_ip_end+" done")

  return True

def main():
  """Demo of the IP utility functions"""

  logger = logging.getLogger()
  logger.setLevel(logging.DEBUG)

  print("\n----------------------------------------------------")
  print("-------------IP utility functions demo--------------")
  print("----------------------------------------------------")

  print("\n-------------Get valid public IP range--------------")
  print("List of public IP: "+str(getValidPublicIpRange()))

  print("\n---------------Number of public IPs-----------------")
  print("Number of public IPs: "+str(getNumberOfPublicIp()));

  print("\n---------------Transform IP to integer----------------")
  ip = "127.0.0.1"
  print(str(ip)+" (IP) -> "+str(ipToInt(ip))+" (long)")

  print("\n---------------Transform integer to IP----------------")
  ip_long = 2130706433
  print(str(ip_long)+" (long) -> "+str(intToIp(ip_long))+" (IP)")

  print("\n----------------Get hostname from IP------------------")
  ip = "8.8.8.8"
  print("Hostname of "+str(ip)+": "+str(getHostFromIp(ipToInt(ip))))

  print("\n--------Get public IPs from specific IP range---------")
  ip_begin = "171.30.0.0"
  ip_end = "192.88.97.255"
  print("List of public IPs between "+ip_begin+" and "+ip_end+": " \
        +str(getValidPublicIps(ipToInt(ip_begin), ipToInt(ip_end))))

  print("\n---Get public IPs ranges of approximately same size---")
  divided_number = 50
  print("Public IPs divided into approximately "+str(divided_number)+" ranges: " \
        +str(getDividedPublicIpRange(divided_number)))

  print("\n-------------------Ping IP or host--------------------")
  ips = ["127.0.0.1", "100.100.100.100", "google.com"]
  for ip in ips:
    print("Ping "+ip+": "+str(ping(ip, 2)))

  print("\n----------------Loop over an IP range-----------------")
  ip_begin = "11.0.0.250"
  ip_end = "11.0.1.5"
  def printTest(ip, count):
      print(str(count)+": "+str(intToIp(ip)))

  ipLoop(ipToInt(ip_begin), ipToInt(ip_end), printTest)

  print("\n----------------------------------------------------")
  print("-------------------End of demo----------------------")
  print("----------------------------------------------------\n")

if __name__ == "__main__":
  main()
