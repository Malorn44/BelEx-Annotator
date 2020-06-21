from django.shortcuts import render

from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.detail import DetailView
from django.urls import reverse

from .forms import AnnotatorForm, UploadFileForm
from .tables import AnnotationTable
from .models import Entry, Annotation, Extraction, ExtArgument

import csv

# Create your views here.

def home(request):
	if request.POST:
		if '_export' in request.POST:
			return export_annotations(request)

	entries = Entry.objects.order_by('eID')
	fileForm = UploadFileForm()

	return render(request, 'annotator/home.html', locals())

def index(request, entry_pk=1):
	if request.POST:
		if '_export' in request.POST:
			return export_annotations(request)

	try:
		entry = Entry.objects.get(eID=entry_pk)
	except:
		return HttpResponseRedirect(reverse('annotator:index', args=(1,)))
	else:
		form = AnnotatorForm()

		annotations = Annotation.objects.filter(entry=entry)
		table = AnnotationTable(annotations)
		
		num_entries = Entry.objects.count()
		num_annotations = annotations.count()

		return render(request, 'annotator/index.html', locals())
	
def submit_belief(request, entry_pk):
	entry = Entry.objects.get(eID=entry_pk)

	form = AnnotatorForm(request.POST)
	if form.is_valid():
		data = form.cleaned_data
		annotation = Annotation.objects.create(
			entry = entry,
			source = data['source'],
			belief = data['belief'],
			target = data['target'],
			strength = data['strength'],
			valuation = data['valuation'])

	return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def change_view(request, entry_pk):
	form = request.POST
	return HttpResponseRedirect(reverse('annotator:index', args=(form['sindex'],)))

def delete_all_objects(model):
	model.objects.all().delete()

# TODO: Upload database (might replace with something else later idk)
def db_upload(request):
	form = UploadFileForm(request.POST, request.FILES)
	if form.is_valid():

		delete_all_objects(ExtArgument)
		delete_all_objects(Extraction)
		delete_all_objects(Annotation)
		delete_all_objects(Entry)

		f = request.FILES['file']
		for line in f.readlines():

			args = list(map(str.strip, line.decode().split('\t')))

			try:
				entry = Entry.objects.get(entry_text__exact=args[0])
				entry.save()
			except Entry.DoesNotExist:
				entry = Entry(entry_text = args[0], eID=Entry.objects.count()+1)
				entry.save()

			extraction = Extraction(sub_text = args[2], pred_text = args[1], entry=entry)
			extraction.save()
			for i in range(3, len(args)):
				argument = ExtArgument(arg_text = args[i], extraction=extraction)
				argument.save()

	return HttpResponseRedirect(reverse('annotator:home'))

# TODO: This kindof works but not well
# the url always gets set to have entry_pk 1 but it stays on the page if
# it isn't 1. This is because I can't figure out how to pass arguments
# correctly in the delete_button.html
def delete_item(request, entry_pk, item_pk):
	entry_pk = Annotation.objects.get(pk=item_pk).entry.eID
	Annotation.objects.filter(pk=item_pk).delete()

	return HttpResponseRedirect(reverse('annotator:index', args=(entry_pk,)))

def export_annotations(request):

	response = HttpResponse(content_type='text/tsv')
	response['Content-Disposition'] = 'attachment; filename="test.tsv"'
	tsv_writer = csv.writer(response, delimiter='\t')

	# not very efficient but should be fine
	for entry in Entry.objects.all():
		for annotation in entry.annotation_set.all():
			tsv_writer.writerow([
				entry.entry_text,
				annotation.source,
				annotation.belief,
				annotation.target,
				annotation.strength,
				annotation.valuation])

	return response
