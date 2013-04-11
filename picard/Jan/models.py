from django.db import models

class Strategy(models.Model):
    strategy  = models.IntegerField()
    description = models.CharField(max_length=250)

    def __unicode__(self):
        return self.description


class Branch(models.Model):
    strategy = models.ForeignKey(Strategy)
    name = models.CharField(max_length=150)
    component = models.CharField(max_length=150)
    latest_delivered_revision = models.IntegerField()
    latest_fault_log_end = models.IntegerField()
    delivery_config = models.TextField()
    svn_log_parser_config_patterns = models.CharField(max_length=300)
    svn_log_parser_config_relax_field = models.CharField(max_length=300)
    svn_log_parser_config_obligatory_patterns_map = models.CharField(max_length=300)
    svn_log_parser_config_allowed_patterns_states = models.CharField(max_length=300)
    cb_database_alias = models.CharField(max_length=150, default='bts_trunk')
    cb_component_field_name = models.CharField(max_length=150, default='tupversion_fsmr3')

    def __unicode__(self):
        return self.name

class DeliveryLocation(models.Model):
    branch = models.ForeignKey(Branch)
    to_location = models.CharField(max_length=150)

    def __unicode__(self):
        return self.to_location

class Content(models.Model):
    content = models.TextField()
    location = models.CharField(max_length=150)
    revision = models.IntegerField()
    content_note_link = models.CharField(max_length=150)
    name = models.CharField(max_length=150)
    system = models.CharField(max_length=150)
    fault_log_location = models.CharField(max_length=300)
    fault_log_start = models.IntegerField()
    fault_log_end = models.IntegerField()
    compilation_date = models.DateTimeField()
    parsed = models.BooleanField(default=False)

    def __unicode__(self):
        return unicode(self.content_note_link)

class Fault(models.Model):
    content = models.ForeignKey(Content)
    pronto = models.CharField(max_length=150)
    revision = models.IntegerField()
    info = models.CharField(max_length=150)
    partial = models.BooleanField()
    description = models.CharField(max_length=400)
    module = models.CharField(max_length=150)

    def __unicode__(self):
        return unicode(self.pronto)


class Baseline(models.Model):
   content = models.ForeignKey(Content)
   baseline = models.CharField(max_length=250)

class External(models.Model):
   content = models.ForeignKey(Content)
   external = models.CharField(max_length=250)


class Build(models.Model):
    branch = models.ForeignKey(Branch)
    content = models.ForeignKey(Content)

class Queue(models.Model):
    build = models.ForeignKey(Build)
    place = models.IntegerField()
    release_date = models.DateTimeField()
    from_location = models.CharField(max_length=150)

    def __unicode__(self):
        return unicode(self.place)

class History(models.Model):
    build = models.ForeignKey(Build)
    place = models.IntegerField()
    release_date = models.DateTimeField()
    from_location = models.CharField(max_length=150)

    def __unicode__(self):
        return unicode(self.release_date)

class HistoryDeliveryLocation(models.Model):
    history = models.ForeignKey(History)
    to_location = models.CharField(max_length=150)

    def __unicode__(self):
        return self.to_location


class HistoryFault(models.Model):
    content = models.ForeignKey(Content)
    pronto = models.CharField(max_length=150)
    revision = models.IntegerField()
    info = models.CharField(max_length=150)
    partial = models.BooleanField()
    description = models.CharField(max_length=400)
    module = models.CharField(max_length=150)

    def __unicode__(self):
        return unicode(self.pronto)


