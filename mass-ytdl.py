#!/usr/bin/env python3

import os
import subprocess
import sys
import xlrd

def print_help():

	print("Usage: ./mass-mus-ydl <SPREADSHEET>")
	print("Make sure <SPREADSHEET> is a path to a valid spreadsheet.")

def download(data):

	data["Title"] = data["Title"].replace("/", "-")
	data["Artist"] = data["Artist"].replace("/", "-")
	output = f"output/{data['Artist']}/{data['Artist']} - {data['Title']}-R-.%(ext)s"

	process = subprocess.run(
		[
			"youtube-dl", "-x", "--audio-format", "vorbis",
			data["Target URL"],	"-o", output
		],
		stdout=open(os.devnull, "wb"),
		stderr=open(os.devnull, "wb")
	)

	if process.returncode != 0:
		return -1

	finput = f"output/{data['Artist']}/{data['Artist']} - {data['Title']}-R-.ogg"
	output = f"output/{data['Artist']}/{data['Artist']} - {data['Title']}.ogg"

	process = subprocess.run(
		[
			"ffmpeg", "-i", finput, "-acodec", "copy",
			"-metadata", f"title=\"{data['Title']}\"",
			"-metadata", f"artist=\"{data['Artist']}\"",
			"-metadata", f"album=\"{data['Album']}\"",
			"-metadata", f"track=\"{data['Track #']}/{data['out of']}\"",
			output
		],
		stdout=open(os.devnull, "wb"),
		stderr=open(os.devnull, "wb")
	)

	if process.returncode != 0:
		return -1

	process = subprocess.run(
		[
			"rm", "-f", finput
		],
		stdout=open(os.devnull, "wb"),
		stderr=open(os.devnull, "wb")
	)

	if process.returncode != 0:
		return -1

def main(args):

	# Argument checking.
	if len(args) != 1 or "-h" in args or "--help" in args:
		print_help()
		return -1
	else:
		fname = args[0]

	# Making sure the supplied path exists.
	try:
		assert os.path.exists(fname) and os.path.isfile(fname)
	except:
		print(f"Path {fname} is invalid.")
		return -1

	# Variables.
	data = []
	template = {}
	headers = {}
	spreadsheet = xlrd.open_workbook(fname).sheet_by_index(0)

	# Creating a template.
	for column in range(len(spreadsheet.row(0))):
		header = spreadsheet.row(0)[column].value
		template[header] = None
		headers[column] = header

	# Populating data.
	for row in range(1, spreadsheet.nrows):
		item = template.copy()
		for column in range(len(spreadsheet.row(row))):
			item[headers[column]] = spreadsheet.row(row)[column].value
		data.append(item)

	# Download the music from the video and set its metadata.
	for item in data:
		print(f"DL: {item['Artist']} - {item['Title']}.ogg")
		if download(item) == -1:
			print("^^^ ERROR OCCURRED. Writing to alerts.txt.")
			open("alerts.txt", "a+").write(str(item))

	print("Done.")

if __name__ == "__main__":
	main(sys.argv[1::])