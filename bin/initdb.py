#!/usr/bin/python
#coding=utf-8
__author__ = 'phithon'
import pymongo, yaml, sys, time, bcrypt
try:
	input = raw_input
except NameError:
	pass

def createAdmin(db, config):
	username = input("input admin name: ")
	password = input("input admin password: ")
	password = bcrypt.hashpw(password, bcrypt.gensalt())
	user = {
		"username": username,
		"password": password,
		"power": 20,
		"money": config["global"]["init_money"],
		"time": time.time(),
		"bookmark": [],
		"email": "",
		"qq": "",
		"website": "",
		"address": "",
		"signal": u"太懒，没有留下任何个人说明",
		"openwebsite": 1,
		"openqq": 1,
		"openemail": 1,
		"allowemail": 1,
		"logintime": None,
		"loginip": None
	}
	member = db.member
	member.insert(user)

def create_index(db):
	db.member.create_index("username", unique = True)
	db.invite.create_index("code", unique = True)

if __name__ == "__main__":
	try:
		with open("config.yaml", "r") as fin:
			config = yaml.load(fin)
	except:
		print "cannot find config file"
		sys.exit(0)

	dbset = config["database"]
	client = pymongo.MongoClient(dbset["config"])
	db = client[dbset["db"]]
	isdo = input("create a admin user(Y/n): ")
	if isdo not in ("N", "n"):
		createAdmin(db, config)
	create_index(db)
