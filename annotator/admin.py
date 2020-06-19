from django.contrib import admin

from .models import Entry, Annotation, Extraction, ExtArgument


# Register your models here.

class AnnotationInline(admin.TabularInline):
	model = Annotation
	extra = 3

class ArgumentInline(admin.StackedInline):
	model = ExtArgument
	extra = 1

class ExtractionInline(admin.TabularInline):
	model = Extraction
	extra = 1

class ExtractionAdmin(admin.ModelAdmin):
	inlines = [ArgumentInline]
	list_display = ('sub_text', 'pred_text')

	search_fields = ['sub_text']

class EntryAdmin(admin.ModelAdmin):
	inlines = [ExtractionInline, AnnotationInline]

admin.site.register(Entry, EntryAdmin)
admin.site.register(Extraction, ExtractionAdmin)