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
	errors = []

	if request.POST:
		if '_export' in request.POST:
			return export_annotations(request)
		elif '_delete' in request.POST:
			delete_annotations(request)
		elif '_db_upload' in request.POST:
			errors += db_upload(request)
		elif '_annotation_upload' in request.POST:
			errors += annotation_upload(request)

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
	def_form_vals = []
	error = False

	if request.POST:
		if '_export' in request.POST:
			return export_annotations(request)
		elif '_submit_annotation' in request.POST:
			if not submit_belief(request, entry_pk):
				def_form_vals = invalid_form_prep(request, entry_pk)
				error = True
		elif '_openIE_copy' in request.POST:
			copy_openIE_to_annotations(request, entry_pk)
		elif '_delete_annotation' in request.POST:
			delete_item(request, request.POST['_delete_annotation'])
		elif '_modify_annotation' in request.POST:
			def_form_vals = edit_item_prep(request, request.POST['_modify_annotation'])
			print(def_form_vals)
		elif '_verify_annotation' in request.POST:
			if not verify_item(request, request.POST['_verify_annotation']):
				error = True

	try:
		entry = Entry.objects.get(eID=entry_pk)
	except:
		return HttpResponseRedirect(reverse('annotator:index', args=(1,)))
	else:
		form = AnnotatorForm(initial=def_form_vals)
		editing_id = 0
		if (def_form_vals):
			editing_id = def_form_vals['id']

		annotations = Annotation.objects.filter(entry=entry)
		table = AnnotationTable(annotations)
		
		num_entries = Entry.objects.count()
		num_annotations = annotations.count()

		return render(request, 'annotator/index.html', locals())

# adds annotation making sure there are no duplicates
def add_annotation(request, entry, args, verified):
	annotations = Annotation.objects.filter(entry=entry)

	for annotation in annotations:
		if (annotation.source == args[0] and
			annotation.belief == args[1] and
			annotation.target == args[2] and
			str(annotation.strength) == args[3] and
			str(annotation.valuation) == args[4]):

			return

	annotation = Annotation(source = args[0], belief = args[1], target = args[2],
		strength = args[3], valuation = args[4], verified = verified, entry=entry)
	annotation.save()

def modify_annotation(request, args):
	annotation = Annotation.objects.get(pk=args[5])

	annotation.source = args[0]
	annotation.belief = args[1]
	annotation.target = args[2]
	annotation.strength = args[3]
	annotation.valuation = args[4]

	annotation.verified = True

	annotation.save()

def form_valid(request, data, entry_text):
	match_found = False
	source_is_author = data[0].lower() == 'author'
	entry_text = ' ' + entry_text + ' ' #for the purpose of avoiding out of bounds error
	print(entry_text)

	for i in range(3):
		print('[STEP 1]', i)
		if match_found: break
		# start checking with source, then belief than target
		if ((i==0 and not source_is_author) or i!=0):
			start_index_i = entry_text.find(data[i])
			print(start_index_i, start_index_i+len(data[i]))
			if (start_index_i == -1 or entry_text[start_index_i+len(data[i])].isalnum()
				or entry_text[start_index_i-1].isalnum()):
				print('Not Found')
				return False

			entry_minus_i = ' ' + entry_text[:start_index_i] + entry_text[start_index_i+len(data[i]):-1] + ' '
		else: 
			entry_minus_i = entry_text

		print(entry_minus_i)

		for j in range(3):
			print('[STEP 2]', j)
			if match_found: break
			# source, belief, target ignore if j==i
			if j==i: continue

			if ((j==0 and not source_is_author) or j!=0):
				start_index_j = entry_minus_i.find(data[j])
				print(start_index_j, start_index_j+len(data[j]))
				if (start_index_j == -1 or entry_minus_i[start_index_j+len(data[j])].isalnum()
					or entry_minus_i[start_index_j-1].isalnum()):
					print('Not Found')
					continue

				entry_minus_j = ' ' + entry_minus_i[:start_index_j] + entry_minus_i[start_index_j+len(data[j]):-1] + ' '
			else:
				entry_minus_j = entry_minus_i

			print(entry_minus_j)

			for k in range(3):
				print('[STEP 3]', k)
				#source, belief, target ignore if k==i or k==j
				if k==i or k==j: continue

				if ((k==0 and not source_is_author) or k!=0):
					start_index_k = entry_minus_j.find(data[k])
					if (start_index_k == -1 or entry_minus_j[start_index_k+len(data[k])].isalnum()
						or entry_minus_j[start_index_k-1].isalnum()):
						print('Not Found')
						continue
				match_found = True
				print('Match Found')
				break

	return match_found

def invalid_form_prep(request, entry_pk):
	form = AnnotatorForm(request.POST)
	if form.is_valid():
		data = [item[1] for item in form.cleaned_data.items()]
		return {'_state': None, 'id': data[5], 'source': data[0],
			'belief': data[1], 'target': data[2], 'strength': data[3],
			'valuation': data[4], 'verified': True}

def submit_belief(request, entry_pk):
	entry = Entry.objects.get(eID=entry_pk)

	form = AnnotatorForm(request.POST)
	if form.is_valid():

		
		data = [item[1] for item in form.cleaned_data.items()]

		# Check if form matches has matches in entry text
		if form_valid(request, data, entry.entry_text):  
			if data[5] is None:
				# we can verify annotations that are handwritten
				add_annotation(request, entry, data, True)
			else:
				modify_annotation(request, data)
		else:
			return False

	return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def copy_openIE_to_annotations(request, entry_pk):
	entry = Entry.objects.get(eID=entry_pk)

	extractions = Extraction.objects.filter(entry=entry)

	for extraction in extractions:
		ext_args = ExtArgument.objects.filter(extraction=extraction)

		args = []
		args.append("Author")

		belief = extraction.pred_text
		if ext_args:
			belief += ' ' + ext_args[0].arg_text

		args.append(belief)
		args.append(extraction.sub_text)
		args.append('4')
		args.append('4')

		# annotations added on the fly shouldn't be verified by default
		add_annotation(request, entry, args, False)

def change_view(request, entry_pk):
	form = request.POST
	return HttpResponseRedirect(reverse('annotator:index', args=(form['sindex'],)))

def delete_all_objects(model):
	model.objects.all().delete()

def db_upload(request):
	form = UploadFileForm(request.POST, request.FILES)
	errors = []
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
	else:
		errors += [form.errors.get_json_data(escape_html=False)['file'][0]['message']]

	return errors

def annotation_upload(request):
	form = UploadAnnotationForm(request.POST, request.FILES)
	errors = []
	if form.is_valid():

		f = request.FILES['file']
		for line in f.readlines():

			args = list(map(str.strip, line.decode().split('\t')))

			try:
				entry = Entry.objects.get(entry_text__exact=args[0])
				entry.save()
			except Entry.DoesNotExist:
				continue

			add_annotation(request, entry, args[1:], True)
	else:
		errors += [form.errors.get_json_data(escape_html=False)['file'][0]['message']]

	return errors

def delete_item(request, item_pk):
	try:
		annotation = Annotation.objects.get(pk=item_pk)
	except Annotation.DoesNotExist:
		return
	else:
		annotation.delete()

def edit_item_prep(request, item_pk):
	try:
		annotation = Annotation.objects.get(pk=item_pk)
	except Annotation.DoesNotExist:
		return []
	else:
		return annotation.__dict__

def verify_item(request, item_pk):
	try:
		annotation = Annotation.objects.get(pk=item_pk)
	except Annotation.DoesNotExist:
		return False
	else:
		if form_valid(request, [annotation.source, annotation.belief, annotation.target], 
				annotation.entry.entry_text):
			annotation.verified = True
			annotation.save()
			return True
		return False

def export_annotations(request):

	response = HttpResponse(content_type='text/tsv')
	filename = "belex_annotations_"+str(datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S"))+".tsv"
	response['Content-Disposition'] = 'attachment; filename='+filename
	tsv_writer = csv.writer(response, delimiter='\t')

	# not very efficient but should be fine
	for entry in Entry.objects.all():
		for annotation in entry.annotation_set.all():
			# only save verified annotations
			if annotation.verified:
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
