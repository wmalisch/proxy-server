import datetime
import os

print(os.path.isdir('localhost_8000'))
print(os.path.isdir('localhost_8080'))
print(os.path.isdir('localhost_8000/jpgs'))
print(os.path.isdir('localhost_8000/txts'))
print(os.path.isdir('localhost_8000/txts/not'))

strx = 'file/file.txt'
stry = 'fold/file/file.txt'
strz = 'file.txt'
date = datetime.datetime.now()
date_string = 'Date: ' + date.strftime('%a, %d %b %Y %H:%M:%S EDT')
print(date_string)
print(os.path.getsize('505.html'))
# directory = 'localhost_9999/hey/how/are/ya/he'
# directoryArray = directory.split('/')
# print(directoryArray)
# temp = '.'

# for folder in directoryArray:
#     if(os.path.isdir(temp)):
#         temp = temp + '/' + folder
#     else:
#         os.mkdir(temp)
#         temp = temp + '/' + folder
# os.mkdir(temp)


