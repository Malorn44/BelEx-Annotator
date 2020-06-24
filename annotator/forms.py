from django import forms
from django.core.validators import FileExtensionValidator

from .validators import upload_db_validator

class AnnotatorForm(forms.Form):
	source = forms.CharField(label='Source', max_length=100)
	belief = forms.CharField(label='Belief', max_length=100)
	target = forms.CharField(label='Target', max_length=100)

	STRENGTH_CHOICES = (
		(1, 'Strongly Committed (true)'),
		(2, 'Committed (true)'),
		(3, 'Somewhat Committed (true)'),
		(4, 'Undecided'),
		(5, 'Somewhat Committed (false)'),
		(6, 'Committed (false)'),
		(7, 'Strongly Committed (false)')
	)

	VALUATION_CHOICES = (
		(1, 'Strongly Positive'),
		(2, 'Positive'),
		(3, 'Somewhat Positive'),
		(4, 'Neutral'),
		(5, 'Somewhat Negative'),
		(6, 'Negative'),
		(7, 'Strongly Negative')
	)

	strength = forms.ChoiceField(label='Strength', choices=STRENGTH_CHOICES, 
		widget=forms.Select(attrs={'class': 'custom-select'}))
	valuation = forms.ChoiceField(label='Valuation', choices=VALUATION_CHOICES, 
		widget=forms.Select(attrs={'class': 'custom-select'}))

	id = forms.IntegerField(widget=forms.HiddenInput, required=False)

class UploadFileForm(forms.Form):
	file = forms.FileField(label='Upload Database',
		validators=[FileExtensionValidator(['tsv'])])#, upload_db_validator])

class UploadAnnotationForm(forms.Form):
	file = forms.FileField(label='Upload Annotations',
		validators=[FileExtensionValidator(['tsv'])])
