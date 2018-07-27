#!/usr/bin/python
import sys
import MySQLdb
from os import listdir
from os.path import isfile, join

def QueryVersion():
    # execute SQL query to get version.
    try:
	cursor.execute("SELECT version from versionTable;")
    except MySQLdb.Error as e:
	print "Data error: Is the table and column correct?"
	print (e)
	db.close()	
	exit()

    # Fetch a single row using fetchone() method.
    data = cursor.fetchone()
    print "Database version : %s" % data
    if len(data[0]) == 0:
	print "Version column is empty.."
	db.close()
	exit()
    global version
    version = data[0];

def UpdateVersion(newVersion):
    # update Version
    try:
	cursor.execute("UPDATE "+ dbname +" SET version='"+ str(newVersion)+"';")
    except MySQLdb.Error as e:
	print "Data error: Is the table and column correct?"
	print (e)
	db.close()	
	exit()
    # execute SQL query to get version.
    try:
	cursor.execute("SELECT version from versionTable;")
    except MySQLdb.Error as e:
	print "Data error: Is the table and column correct?"
	print (e)	
	db.close()
	exit()

    # Fetch a single row using fetchone() method.
    data = cursor.fetchone()
    if int(data[0]) != int(newVersion):
	print "ALERT! Version number in database not updated!!"	
	print "ALERT! Version number in database not updated!!"
	db.close()
	exit()
    else:
	print "Database version successfully updated to " + str(newVersion)

def ExecuteScripts(filename):
    # Open and read the file as a single buffer
    print 'Executing file: ' + str(filename)
    fd = open(directory+"/"+ filename, 'r')
    sqlFile = fd.read()
    fd.close()

    # all SQL commands (split on ';')
    sqlCommands = sqlFile.split(';')

    # Execute every command from the input file
    for command in sqlCommands:
        # This will skip and report errors
        # For example, if the tables do not yet exist, this will skip over
        # the DROP TABLE commands
        try:
            cursor.execute(command)
        except MySQLdb.Error as msg:
            print "Command skipped: ", msg

def FindSuitableScripts():
    for file in onlyfiles:
        try:
	    scriptNumber = int(''.join([n for n in str(file) if n.isdigit()]))
	    scriptVersionsList.append(scriptNumber)
	    if scriptNumber > int(version):
		fileList.append(file)
	    else:
		print "This script is outdated: " + str(file)
        except Exception as e:
	    print "This script is not valid: " + str(file)

##################################################################################################

#Provide instruction to run the script
if sys.argv[1] == '--help':
    print 'Arguments accepted: \n 1. <directory with .sql scripts>  \n 2. <username for the DB> \n 3. <DB host> \n 4. <DB name> \n 5. <DB password>'
    exit()

#Warn about incorrect arguments
if len(sys.argv[1:]) != 5:
    print 'Incorrect number of arguments provided'
    print '5 Arguments accepted: \n 1. <directory with .sql scripts>  \n 2. <username for the DB> \n 3. <DB host> \n 4. <DB name> \n 5. <DB password>'
    exit()

directory = sys.argv[1]

#check it's valid directory and get all files
onlyfiles = [f for f in listdir(directory) if isfile(join(directory, f))]
if len(onlyfiles) == 0:
    print "Script files at " + directory +" is empty.. exiting"
    exit()

username = sys.argv[2]
dbhost = sys.argv[3]
dbname = sys.argv[4]
dbpw = sys.argv[5]

scriptVersionsList=[];

# Open database connection
try:
    db = MySQLdb.connect(dbhost,username,dbpw,dbname )
except MySQLdb.Error as e:
    print "Database connection error.."
    print (e)
    exit()

# prepare a cursor object using cursor() method
cursor = db.cursor()

#query the version on database and save it on version variable
version = ''
QueryVersion()

#using the version info, find suitable scripts to run
fileList = []
FindSuitableScripts()

#run the scripts in fileList
fileList.sort()
for filename in fileList:
    ExecuteScripts(filename)

#update database to the highest numbered script version
UpdateVersion(max(scriptVersionsList))

# disconnect from server
db.close()
