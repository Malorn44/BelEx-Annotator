import django_tables2 as tables
from django_tables2.columns import LinkColumn, TemplateColumn
from django_tables2.utils import A # alias for Accessor

from .models import Annotation

class AnnotationTable(tables.Table):
	# delete = tables.LinkColumn('annotator:delete_item', args=[A('pk')], 
	# 	attrs={'a': {'class': 'btn'}}, empty_values=())

	modify = TemplateColumn(template_name='annotator/modify_button.html')
	delete = TemplateColumn(template_name='annotator/delete_button.html')

	class Meta:
		model = Annotation
		orderable = False
		fields = ('source', 'belief', 'target', 'strength', 'valuation', 'modify', 'delete')
		order_by = 'id'
