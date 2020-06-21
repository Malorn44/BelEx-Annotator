from django.shortcuts import render

from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.detail import DetailView
from django.urls import reverse

from .forms import AnnotatorForm, UploadFileForm, UploadAnnotationForm
from .tables import AnnotationTable
from .models import Entry, Annotation, Extraction, ExtArgument

import datetime
import csv

# Create your views here.

def home(request):
	if request.POST:
		if '_export' in request.POST:
			return export_annotations(request)
		elif '_delete' in request.POST:
			delete_annotations(request)

	entries = Entry.objects.order_by('eID')
	dbForm = UploadFileForm()
	annotationForm = UploadAnnotationForm()

	db_upload_warning = ("WARNING. Uploading a new database will delete all objects currently stored "
		"including any annotations you may have made. If you want to save a copy of your annotations "
		"you can use the \"Export Annotations\" button. Are you sure you want to upload a new database?")
	annotation_upload_warning = ("WARNING. You are about to upload annotations. This will append all "
		"annotations from your uploaded file to your current annotations (ignoring annotations that can not "
		"be matched to any sentences in the database) and can not be undone. You can use the \"Export "
		"Annotations\" button to make a backup of your annotations. Are you sure you want to upload annotations?")
	delete_annotations_warning = ("WARNING. You are about to delete all annotations. This action can not be "
		"undone. You can use the \"Export Annotations\" button to make a backup of your annotations. Are you "
		"sure you want to delete all annotations?")

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

def annotation_upload(request):
	form = UploadAnnotationForm(request.POST, request.FILES)

	if form.is_valid():

		f = request.FILES['file']
		for line in f.readlines():

			args = list(map(str.strip, line.decode().split('\t')))

			try:
				entry = Entry.objects.get(entry_text__exact=args[0])
				entry.save()
			except Entry.DoesNotExist:
				continue

			annotation = Annotation(source = args[1], belief = args[2], target = args[3],
				strength = args[4], valuation = args[5], entry=entry)
			annotation.save()

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
	filename = "belex_annotations_"+str(datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S"))
	response['Content-Disposition'] = 'attachment; filename='+filename
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

def delete_annotations(request):
	delete_all_objects(Annotation)
