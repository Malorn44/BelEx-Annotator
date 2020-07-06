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
	strength = models.IntegerField()
	valuation = models.IntegerField()

	verified = models.BooleanField(default=False)

	@property
	def strengthToText(self):
		return {
			1: 'Strongly Committed (true)',
			2: 'Committed (true)',
			3: 'Somewhat Committed (true)',
			4: 'Undecided',
			5: 'Somewhat Committed (false)',
			6: 'Committed (false)',
			7: 'Strongly Committed (false)',
		}[self.strength]

	@property
	def valuationToText(self):
		return {
			1: 'Strongly Positive',
			2: 'Positive',
			3: 'Somewhat Positive',
			4: 'Neutral',
			5: 'Somewhat Negative',
			6: 'Negative',
			7: 'Strongly Negative',
		}[self.valuation]
	
	