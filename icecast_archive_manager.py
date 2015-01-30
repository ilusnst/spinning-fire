#!/usr/bin/python
"""
Title: icecast_archive_manager.py (1.0)

Inception: Sept 9th 2011

Function: This program monitors an Icecast2 mp3 achive file, queries a name from the Icecast2 server, then renames the file and moves it to a predetermined directory.

Purpose: Automatically manage archives of live Icecast2 broadcasts such that consecutive broadcasts are not appended to the archive mp3 file.  This program should be added to your systems cron list. Recommend 60 second intervals.

Requires: Python: [os,sys,time, xml.dom.minidom, urllib]

User edited variables:
    In class, "get_live_title"
        if mount_point == "/YourLiveMountPoint":
        
        
    At "# Check for system arguments"
        Define the dictionary keys:
        my_dict = {
        'is_it_running':'"/path/to/your/log/files/log/is_it_running.txt"',
        'oldfile':'"/path/to/your/icecast/mountpoint/dumpfile/archive.mp3"',
        'newpath':'"/path/to/your/mp3/archive/"',
        'icecast_admin_url':'"http://admin:Your_Icecast2_AdminPassword@YourServer.com:8000/admin/stats"',
        'live_log':'"/path/to/your/log/files/log/live_log.txt"',
        'mylivemount':'/your-live-mount-point-name'
        }
        
Last update 1-29-2015

"""

#Get dependencies 
import os,sys,time, xml.dom.minidom, urllib
from sys import argv
from xml.dom.minidom import parse
from xml.dom.minidom import Node


# Get show title from Icecast server
def get_live_title(xml_source):
    if (my_dict['debug']):
        print "\nget_live_title' has begun..."
    doc = parse(urllib.urlopen(xml_source))    
    for node in doc.getElementsByTagName("source"):
        mount_point = node.getAttribute("mount")
        if (my_dict['debug']):
                print "Mount point is: ", mount_point
        if mount_point == my_dict['mylivemount']:
          L = node.getElementsByTagName("server_name")
          for node2 in L:
            title = ""
            for node3 in node2.childNodes:
              if node3.nodeType == Node.TEXT_NODE:
                title += node3.data            
            my_dict['mount_point'] = title
            if (my_dict['debug']):
                print "title is: ", title
            isitrunning = open(my_dict['is_it_running'], 'a')
            isitrunning.write("A Title has been chosen!")
        elif (my_dict['debug']):
                print "Mount point is not live."


#Module to wait for archive creation
def look_for_archive(waitBetweenSizeCheck):
    if (my_dict['debug']):
        print "'look_for_archive' has begun..."
    keepgoing = True
    got_title = False
    while keepgoing:
        try:
            a = os.path.getsize(my_dict['oldfile'])
            if got_title == False:                
                get_live_title(my_dict['icecast_admin_url'])
                got_title = True
                if (my_dict['debug']):
                    print "\nSleeping ",waitBetweenSizeCheck," seconds..."
            time.sleep(waitBetweenSizeCheck)
            b = os.path.getsize(my_dict['oldfile'])
            if (my_dict['debug']):
                print "\nFile sample size 'A' is: ", a,"\nFile sample size 'B' is: ",b
            if (a == b) and ( a > 0):
                if (my_dict['debug']):
                    print "File is done growing, time to move it..."
                keepgoing = False
                change_name()
        except OSError:
            if (my_dict['debug']):
                print "OSError has occurred, there is no archive file at ", my_dict['oldfile']
            keepgoing = False
            pass

# rename_archive():
def change_name():
    if (my_dict['debug']):
        print "\n'change_name' had begun..."
    endtime = time.localtime()    
    try:
        newfile = my_dict['newpath'] + my_dict['mount_point'] + "_" + str(endtime.tm_mon) + "-" + str(endtime.tm_mday) + "-" + str(endtime.tm_year) + "_" + str(endtime.tm_hour) + "-" + str(endtime.tm_min) + "-" + str(endtime.tm_sec) + ".mp3"        
        os.rename(my_dict['oldfile'], newfile)
        target = open(my_dict['live_log'], 'a')
        input = "\nMoved %r to %r\n" % (my_dict['oldfile'], newfile) + "-" * 30
        if (my_dict['debug']):
            print "\nMoved %r to %r\n" % (my_dict['oldfile'], newfile) + "-" * 30
        target.write(input)
        target.close()
        os.remove(my_dict['oldfile'])
        if (my_dict['debug']):
            print "File ",my_dict['oldfile']," has been deleted."
    except KeyError:
        if (my_dict['debug']):
            print "KeyError - naming archive 'Unknown'..."
        newfile = my_dict['newpath'] + "unknown_" + "_" + str(endtime.tm_mon) + "-" + str(endtime.tm_mday) + "-" + str(endtime.tm_year) + "_" + str(endtime.tm_hour) + "-" + str(endtime.tm_min) + "-" + str(endtime.tm_sec) + ".mp3"
        os.rename(my_dict['oldfile'], newfile)
        target = open(my_dict['oldfile'], 'a')
        input = "\nMoved %r to %r\n" % (my_dict['oldfile'], newfile) + "-" * 30
        if (my_dict['debug']):
            print "\nMoved %r to %r\n" % (my_dict['oldfile'], newfile) + "-" * 30
        target.write(input)
        target.close()
        os.remove(my_dict['oldfile'])
        if (my_dict['debug']):
            print "File ",my_dict['oldfile']," has been deleted."


# Check for system arguments
try:
    my_dict = {'mylivemount':'/live','is_it_running':'is_it_running':'"/path/to/your/log/files/log/is_it_running.txt','oldfile':'"/path/to/your/icecast/mountpoint/dumpfile/archive.mp3"','newpath':'"/path/to/your/mp3/archive/"','icecast_admin_url':'"http://admin:Your_Icecast2_AdminPassword@YourServer.com:8000/admin/stats"','live_log':'"/path/to/your/log/files/log/live_log.txt"','debug':0}
    if (str(sys.argv[1]) == ""):
        pass
    elif (str(sys.argv[1]) == "-h"):
        print "-h for help\n-d for debugging\nThis program is designed to monitor the archive dump file of an Icecast2 server for live broadcasts. \nFunction: This program monitors an Icecast2 mp3 achive file, queries a name from the Icecast2 server, then renames the file and moves it to a predetermined directory.\n\nWhen a live broadcast ends, this program renames the archive appropriately and moves the file to a specified directory. \nThis program should be added to your systems cron list. Recommend 60 second intervals.\nRequires: Python: [os,sys,time, xml.dom.minidom, urllib]\n\nIMPORTANT:\nYou must change the values in the dictionary, my_dict, to correspond to your system environment.\n\nCurrent Variable Settings:\n--------------------------\nIcecast Admin URL, name and password: ",my_dict['icecast_admin_url'],"\nPath to Icecast2 dump file: ",my_dict['oldfile'],"\nMy LIVE mount point: ",my_dict['mylivemount'],"\nPath to Archive directory: ",my_dict['newpath'],"\nPath to text file, 'is_it_running.txt': ",my_dict['is_it_running'],"\nPath to log file: ",my_dict['live_log']
        

        quit()
    elif (str(sys.argv[1]) == "-d"):
        print "Debugging is ON!"
        print "\nCurrent Variable Settings:\n--------------------------\nIcecast Admin URL, name and password: ",my_dict['icecast_admin_url'],"\nPath to Icecast2 dump file: ",my_dict['oldfile'],"\nPath to Archive directory: ",my_dict['newpath'],"\nPath to text file, 'is_it_running.txt': ",my_dict['is_it_running'],"\nPath to log file: ",my_dict['live_log']
        my_dict['debug'] = 1        
    else:
        print "-h for help\n-d for debugging"
        quit()    
except IndexError:
    pass


# Start Program

if (my_dict['debug']):
        print "***********************\n*                     *\n* Program is starting *\n*                     *\n***********************\n"  

isitrunning = os.path.getsize(my_dict['is_it_running'])
if (my_dict['debug']):
    print "Is it running = " , isitrunning
if (isitrunning == 0):
    keep_running = True
    while keep_running:
        look_for_archive(5)        
        keep_running = False
        isitrunning = open(my_dict['is_it_running'], 'w')
        isitrunning.write("")        
else:    
    pass
if (my_dict['debug']):
    print "Program End"