import django_tables2 as tables
from django_tables2.columns import TemplateColumn

from .models import Annotation

class AnnotationTable(tables.Table):

	modify = TemplateColumn(template_name='annotator/modify_button.html')
	delete = TemplateColumn(template_name='annotator/delete_button.html')

	class Meta:
		model = Annotation
		# row_attrs = {
		# 	'editing': lambda record: record.editing
		# }

		orderable = False
		fields = ('source', 'belief', 'target', 'strength', 'valuation', 'modify', 'delete')
		order_by = 'id'
