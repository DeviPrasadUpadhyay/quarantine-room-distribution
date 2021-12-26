# Module to connect the mysql server to python 
import mysql.connector
import math 

# Inbuilt fun as a utility to departure date 
from datetime import datetime, timedelta
from random import choice

# Create a connection with MySQL
conn = mysql.connector.connect(host = "localhost", user = "root", passwd = "new_password")

# Cursor class beautifies mysql functionalies with useful utility functions like execute fetch executemany etc 
cur = conn.cursor()

# Info regarding the rooms 
# room [0] corresponds to GroundFloor, room [1] for firstFloor , room [2] for SecondFloor 
room = [[] for _ in range(3)]

r = 1000 
while ( r < 2251 ) : 
	floor = ( r // 100 ) % 10 
	room [floor].append (r) 
	if ( r == 1250 ) : 
		r += 750 
	else :
		r += 1 
		
# Utility function to set up the database and generates the table required alongwith it . 
def SetupDatabase():
	
	# Create this database only if not present already 
	qry = "CREATE DATABASE IF NOT EXISTS dbms_project"
	cur.execute(qry)
	
	# To import the database in current program 
	qry = "USE dbms_project"
	cur.execute(qry)
	
	
	# Create 4 tables for personal info , contact , address & room of the patient 
	
	# Personal Info of the Patient 
	qry = "CREATE TABLE IF NOT EXISTS PATIENT_INFO ( Pat_ID INT PRIMARY KEY NOT NULL auto_increment, Name VARCHAR(255), Aadhar_Num VARCHAR(12) UNIQUE, Age INT, Admission_Date DATE, Discharge_Date DATE, Arrived_From VARCHAR(255), Leaving_To VARCHAR(255)) "
	cur.execute(qry)
	
	# Info regarding the address of Patient 
	qry = "CREATE TABLE IF NOT EXISTS PATIENT_ADDRESS (  Pat_ID INT REFERENCES PATIENT_INFO(Pat_ID) ON DELETE CASCADE, House_Num VARCHAR(255), Street VARCHAR(255), Area VARCHAR(255), City VARCHAR(255), Pincode INT, State VARCHAR(255), Country VARCHAR(255)) "
	cur.execute(qry)


	
	# Info regarding the contact to patient 
	qry = "CREATE TABLE IF NOT EXISTS PATIENT_CONTACT ( Pat_ID INT REFERENCES PATIENT_INFO(Pat_ID) ON DELETE CASCADE, Phone_Num VARCHAR(255)) "
	cur.execute(qry)

	# Admission and Discharge Date 
	qry = "CREATE TABLE IF NOT EXISTS ADM_PERIOD ( " \
		  "Pat_ID INT REFERENCES PATIENT_INFO(Pat_ID) ON DELETE CASCADE, " \
		  "Adm_Date DATE, " \
		  "Dis_Date DATE) "
	cur.execute(qry)
	
	# Info regarding the patients room 
	qry = "CREATE TABLE IF NOT EXISTS ROOM_INFO ( Pat_ID INT REFERENCES PATIENT_INFO(Pat_ID) ON DELETE CASCADE, Hostel_Num INT, Floor_Num INT, Room_Num INT) "
	cur.execute(qry)	

	conn.commit()
	


# Utility functio to help in enrolling a new patient details in database
def EnrollPatient():
		# Plz insert the Basic info regarding the Patient 
		qry = "INSERT INTO PATIENT_INFO (NAME, Age, Arrived_From, Leaving_To) VALUES (%s, %s, %s, %s)"
		
		name = input("Enter Patient Name : ")
		age = int(input("Enter Age : "))
		arr_frm = input("From where did you come? ")
		lev_to = input("Where will you be heading to? ")		
		cur.execute(qry, (name, age, arr_frm, lev_to))		
		conn.commit()
		
		# Insert Phone Numbers
		qry = "INSERT INTO PATIENT_CONTACT (Pat_ID, Phone_Num) VALUES (%s, %s) "
		phone_num = [int(x) for x in input("Enter Phone Numbers separated by space : ").split()]
		data = []
		
		getqry = "SELECT LAST_INSERT_ID() "
		cur.execute(getqry) 
		pat_id = 0
		for x in cur:
			for id in x:
				pat_id = id
		
		for num in phone_num:
			data.append((pat_id, num))
			
		cur.executemany(qry, data)
		
		# Insert Patient Address
		qry = "INSERT INTO PATIENT_ADDRESS (Pat_ID, House_Num, Street, Area, City, Pincode, State, Country) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) "
		
		house_num = input("Enter House Number : ")
		street = input("Enter Street Name : ")
		area = input("Enter Area Name : ")
		city = input("Enter City Name : ")
		pincode = int(input("Enter Area's Pincode : "))
		state = input("Enter State : ")
		country = input("Enter Country : ")
		
		cur.execute(qry, (pat_id, house_num, street, area, city, pincode, state, country))
		
		# Insert Room Info
		qry = "INSERT INTO ROOM_INFO (Pat_ID, Hostel_Num, Floor_Num, Room_Num) VALUES (%s, %s, %s, %s) "
		
		room_num = 0;
		
		if age >= 60:
			room_num = choice(room[0])
			room[0].remove(room_num)
		elif age >= 40:
			room_num = choice(room[1])
			room[1].remove(room_num)
		else:
			room_num = choice(room[2])
			room[2].remove(room_num)
		
		floor_num = (room_num // 100) % 10
		hostel_num = room_num // 1000
		room_num %= 100
		
		
		cur.execute(qry, (pat_id, hostel_num, floor_num, room_num))
		
		conn.commit()
		
		# Details regarding assigned Room to the patient
		print("Enrolled Patient has been alloted \n Hostel " + str(hostel_num) + " Floor " + str(floor_num) + " Room " + str(room_num) + " to Patient " + str(name) + " (ID : " + str(pat_id) + ")")
		print("")



def getData(id):

	# This function creates a dictionary by gathering data from
	# all the 5 tables where Pat_ID = id
	curData = {}
	
	qry = "SELECT * FROM PATIENT_INFO WHERE Pat_ID = %s "
	cur.execute(qry, (id, ))

	for x in cur:
		curData["pat_id"] = x[0]
		curData["name"] = x[1]
		curData["age"] = x[2]
		curData["com_frm"] = x[3]
		curData["lev_to"] = x[4]
	
	qry = "SELECT * FROM ADM_PERIOD WHERE Pat_ID = %s "
	cur.execute(qry, (id, ))
	
	for x in cur:
		curData["adm_date"] = x[1]
		curData["dis_date"] = x[2]
	
	qry = "SELECT Phone_Num FROM PATIENT_CONTACT WHERE Pat_ID = %s "
	cur.execute(qry, (id, ))
	
	curData["phn"] = []
	for x in cur:
		for num in x:
			curData["phn"].append(num)
			
	qry = "SELECT * FROM PATIENT_ADDRESS WHERE Pat_ID = %s "
	cur.execute(qry, (id, ))
	
	for x in cur:
		curData["house_num"] = x[1]
		curData["street"] = x[2]
		curData["area"] = x[3]
		curData["city"] = x[4]
		curData["pincode"] = x[5]
		curData["state"] = x[6]
		curData["country"] = x[7]
		
	qry = "SELECT * FROM ROOM_INFO WHERE Pat_id = %s "
	cur.execute(qry, (id, ))
	
	for x in cur:
		curData["hostel_num"] = x[1]
		curData["floor_num"] = x[2]
		curData["room_num"] = x[3]
	
	return curData

# Utility function to print the patient info 
def showData(info ):

	# Using the python dictionary to print the information of patient in proper manner . 
	print("")
	print("Patient Id : " + str(info ["pat_id"]))
	print("Name : " + str(info ["name"]))
	print("Age : " + str(info ["age"]))
	print("Coming From : " + str(info ["com_frm"]))
	print("Leaving To : " + str(info ["lev_to"]))

	print("Admission Date : " + str(info ["adm_date"]))
	print("Discharge Date : " + str(info ["dis_date"]))
	print("Address : " + str(info ["house_num"]) + " " + str(info ["street"]) + " " + str(info ["area"]) + ", " + str(info ["city"]) + ", " + str(info ["state"]) + ", " + str(info ["country"]))
	
	print("PinCode : " + str(info ["pincode"]))
	print("Phone Numbers :", *info ["phn"])
	print("Hostel : " + str(info ["hostel_num"]) + ", Floor : " + str(info ["floor_num"]) + ", Room : " + str(info ["room_num"]))
	print("")	
	print("---------------------------------------------------------------------")

# Utility function to print the entire database .
def DisplayDB():
	
	# Extract data from tables using getData fun and subsequently showData fun helps us to present it to user
	qry = "SELECT Pat_ID from PATIENT_INFO "
	cur.execute(qry)
	pat_id = []
	print (cur) 
	for x in cur:
		print (x) 
		for id in x:
			print (id)
			pat_id.append(id)
			
	pat_id.sort()
			
	if len(pat_id) == 0:
		print(" No records for the time being . ")
	else:
		data = []
		
		for id in pat_id:
			info  = getData(id)
			data.append(info )
			
		for info  in data:
			showData(info )	
	print("")		

# Utility function to search for a patient in the  Database 
def LookupFor():

	# This function is to print the data of a particular patient, either 
	# by id or by name. It then uses getData and showData functions to 
	# get and print the data
	c = int(input("How would you like to search for patient ?  \n1 Via Patient ID  \n2 Via Name \n "))
	pat_id = []
	if(c == 1):
		x = int(input("Tell the Patient ID : "))
		
		getqry = "SELECT Pat_ID FROM PATIENT_INFO WHERE Pat_ID = %s "
		cur.execute(getqry, (x, ))
		
		for x in cur:
			pat_id.append(int(x[0]))
		
	else:
		name = input("Tell the Patient Name : ")
		
		getqry = "SELECT Pat_ID FROM PATIENT_INFO WHERE Name = %s "
		cur.execute(getqry, (name, ))
		
		for x in cur:
			for id in x:
				pat_id.append(int(id))
		
	data = []		
	for id in pat_id:
		info  = getData(id)
		data.append(info )
		
	if len(data) == 0:
		print("There is no such patient in our Database.")
	else:
		for info  in data:
			showData(info )
	print("")


def Removal():
	 
	# For removal part , we will remove the data from our 5 tables first & then dictate the room as free in rooms list. 
	pat_id = input("Plz insert the Patient ID to remove  ")
	
	qry = "SELECT Hostel_num, Floor_Num, Room_Num from ROOM_INFO "
	cur.execute(qry)
	
	room_num, floor_num, hostel_num = 0, 0, 0
	
	for x in cur:
		hostel_num = x[0]
		floor_num = x[1]
		room_num = x[2]
		
	if hostel_num == 0:
		return
	
	room_num = int(hostel_num) * 1000 + int(floor_num) * 100 + int(room_num)
	
	room[floor_num].append(room_num)
	
	# Remove every instance of the given data from each of our tables . 
	qry = "DELETE FROM PATIENT_INFO WHERE Pat_ID = %s "
	cur.execute(qry, (pat_id, ))
	
	qry = "DELETE FROM PATIENT_ADDRESS WHERE Pat_ID = %s "
	cur.execute(qry, (pat_id, ))
	
	qry = "DELETE FROM PATIENT_CONTACT WHERE Pat_ID = %s "
	cur.execute(qry, (pat_id, ))
	
	qry = "DELETE FROM ROOM_INFO WHERE Pat_ID = %s "
	cur.execute(qry, (pat_id, ))
	
	qry = "DELETE FROM ADM_PERIOD WHERE Pat_id = %s "
	cur.execute(qry, (pat_id, ))
	
	conn.commit()
	
	print("Congrats ! Entered patient details removed Successfully .")
	print("")


def Triggers():
	
	# Creation of a function to capitalize the beginning letter of they very word of the string it got 
	qry = "DROP FUNCTION IF EXISTS camelcase "
	cur.execute(qry)

	# Upon iterating the i/p string in left to  right fashion , whenever a punctuation is encountered , the first letter get capitalized of the very next word .
	qry = "CREATE FUNCTION `camelcase`( str VARCHAR(255) ) RETURNS VARCHAR(255) CHARSET utf8 DETERMINISTIC  BEGIN    DECLARE c CHAR(1);    DECLARE s VARCHAR(255);    DECLARE i INT DEFAULT 1;    DECLARE bool INT DEFAULT 1;  DECLARE punct CHAR(17) DEFAULT ' ()[]{},.-_!@;:?/';    SET s = LCASE( str );    WHILE i < LENGTH( str ) DO       BEGIN         SET c = SUBSTRING( s, i, 1 );         IF LOCATE( c, punct ) > 0 THEN          SET bool = 1;        ELSEIF bool=1 THEN          BEGIN            IF c >= 'a' AND c <= 'z' THEN               BEGIN                 SET s = CONCAT(LEFT(s,i-1),UCASE(c),SUBSTRING(s,i+1));                 SET bool = 0;               END;             ELSEIF c >= '0' AND c <= '9' THEN              SET bool = 0;            END IF;          END;      END IF;        SET i = i+1;      END;    END WHILE;    RETURN s;  END"
	cur.execute(qry)

	# commit to ensure the actual saving data in Database properly .
	conn.commit()

	# Creating a trigger to convert name to camel case when inserting a record
	qry = "DROP TRIGGER IF EXISTS cap_on_insert "
	cur.execute(qry) 

	qry = "CREATE TRIGGER cap_on_insert BEFORE INSERT ON PATIENT_INFO FOR EACH ROW BEGIN SET NEW.Name = camelcase(NEW.Name); END; "
	cur.execute(qry)

	# Subsequently implement another trigger to convert address data ie street , area , city and country to Camelcase when enrolling a tuple  
	qry = "DROP TRIGGER IF EXISTS cap_address "
	cur.execute(qry)
	
	qry = "CREATE TRIGGER cap_address BEFORE INSERT ON PATIENT_ADDRESS FOR EACH ROW BEGIN SET NEW.Country = camelcase(NEW.Country), NEW.State = camelcase(NEW.State), NEW.city = camelcase(NEW.city), NEW.area = camelcase(NEW.area), NEW.street = camelcase(NEW.street); END; "
	cur.execute(qry)
	
	# Whenever a new enrollment occur in the Patient Details table , make sure to insert admission & discharge date to admission period table in this fashion 
	qry = "DROP TRIGGER IF EXISTS ins_adm_period "
	cur.execute(qry)
	
	qry = "CREATE TRIGGER ins_adm_period AFTER INSERT ON PATIENT_INFO FOR EACH ROW BEGIN INSERT INTO ADM_PERIOD(Pat_Id, Adm_Date, Dis_Date) VALUES (NEW.Pat_ID, CURDATE(), DATE_ADD(CURDATE(), INTERVAL 14 DAy)); END; "
	cur.execute(qry)

	# Final commiting to implement all the triggers changes to database too . 
	conn.commit()

SetupDatabase ()
# Set the triggeres 
Triggers()

# Remove the alloted rooms from the lists of rooms
# Whenever a room get alloted to a newly enrolled patient , it makes obvious deletion of room in this list too .
qry = "SELECT Hostel_Num, Floor_Num, Room_Num from ROOM_INFO "
cur.execute(qry)

for x in cur :
	room[x[1]].remove(int(x[0]) * 1000 + int(x[1]) * 100 + int(x[2]))

# We are all set to go tackle user queries . 
while 1 :
	# Flow Statements for user to make him choose his query in a Smart manner .
	c = int(input(" Plz proceed with your Query ! \n1 Enroll a new patient \n2 Display entire Records \n3 Lookup for a speicific Patient \n4 Remove a specific patient \n5 Quit for now !! \n "))
	if c == 1:
		EnrollPatient()
	elif c == 2:
		DisplayDB()
	elif c == 3:
		LookupFor()
	elif c == 4:
		Removal()
	else:
		break
		
cur.close()
conn.close()
