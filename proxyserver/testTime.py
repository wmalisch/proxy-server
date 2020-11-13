import datetime
import time
import os

print(os.path.isdir('localhost_8000'))
print(os.path.isdir('localhost_8080'))
print(os.path.isdir('localhost_8000/jpgs'))
print(os.path.isdir('localhost_8000/txts'))
print(os.path.isdir('localhost_8000/txts/not'))

strx = 'file/file.txt'
stry = 'fold/file/file.txt'
strz = 'file.txt'
file4 = 'localhost_9090/files/file1.txt'

# Last modified time in seconds from epoch
mod = os.stat(file4).st_mtime
print(mod)

# Current time in time structure
# now = time.gmtime()
# print(now)

# Current time in seconds from epoch
epoch_time = int(time.time())
print(epoch_time)

# Formatted time for last modified time
# v = time.ctime(os.path.getmtime(file4))
# print("last modified: %s" % v)

