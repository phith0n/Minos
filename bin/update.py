#!/usr/bin/python
__author__ = 'phithon'
import os, sys, hashlib, shutil

try:
	input = raw_input
except NameError:
	pass

def checksum_md5(filename):
	md5 = hashlib.md5()
	with open(filename,'rb') as f:
		for chunk in iter(lambda: f.read(8192), b''):
			md5.update(chunk)
	return md5.digest()

if not os.path.isdir(".git"):
	print("%s is not a git directory" % os.getcwd())
	sys.exit()

os.system("git stash && git pull https://github.com/phith0n/Minos.git")
www_dir = input("Input your www directory:")

generator = os.walk("./")
for (now_dir, _, file_list) in generator:
	for file in file_list:
		file = os.path.join(now_dir, file)
		remote_filename = os.path.abspath(os.path.join(www_dir, file))
		update = False
		if file.endswith(".py") or file.startswith("./templates/") or file.startswith("./static/assets/"):
			if not os.path.isfile(remote_filename):
				update = True
			else:
				if checksum_md5(file) != checksum_md5(remote_filename):
					update = True
		if update:
			(dir, _) = os.path.split(remote_filename)
			if not os.path.isdir(dir):
				os.makedirs(dir)
			print "[+] Update %s" % remote_filename
			shutil.copyfile(file, remote_filename)
