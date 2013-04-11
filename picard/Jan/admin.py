from django.contrib import admin
from picard.Jan.models import Branch, Fault, Baseline, External, Content, Build, Queue, History, DeliveryLocation, HistoryDeliveryLocation, Strategy

admin.site.register(Branch)
admin.site.register(Fault)
admin.site.register(Baseline)
admin.site.register(External)
admin.site.register(Content)
admin.site.register(Build)
admin.site.register(Queue)
admin.site.register(History)
admin.site.register(DeliveryLocation)
admin.site.register(HistoryDeliveryLocation)
admin.site.register(Strategy)