import csv

from django.core.exceptions import ValidationError

def upload_db_validator(doc):
	print("test")
	try:
		dialect = csv.Sniffer().sniff(doc.read(1024), delimiters='\t')
	except:
		print("Not valid TSV file")
		raise ValidationError(u'Not a valid TSV file')
		