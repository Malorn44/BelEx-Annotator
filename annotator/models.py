from django.db import models

# Create your models here.

class Entry(models.Model):
	entry_text = models.CharField(max_length=1000)
	eID = models.IntegerField(default=1) # for use in page navigation

	def __str__(self):
		return self.entry_text

class Extraction(models.Model):
	entry = models.ForeignKey(Entry, on_delete=models.CASCADE)

	sub_text = models.CharField(max_length=1000)
	pred_text = models.CharField(max_length=1000)

class ExtArgument(models.Model):
	extraction = models.ForeignKey(Extraction, on_delete=models.CASCADE)

	arg_text = models.CharField(max_length=1000)

class Annotation(models.Model):
	entry = models.ForeignKey(Entry, on_delete=models.CASCADE)

	source = models.CharField(max_length=1000)
	belief = models.CharField(max_length=1000)
	target = models.CharField(max_length=1000)
	strength = models.CharField(max_length=1000)
	valuation = models.CharField(max_length=1000)
	