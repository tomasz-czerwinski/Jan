#!/usr/bin/env python
# -*- coding: utf-8 -*-  

"""
Features ideas:
    Notice about correction arriving
"""

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMultiAlternatives, send_mail, BadHeaderError
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Max
from django.db import connections
from datetime import datetime, timedelta
from ast import literal_eval
import logging

from picard.Jan.models import *
from picard.Jan.forms import *
import picard.Jan.svn
import picard.Jan.contentnote
import picard.Jan.api
import picard.Jan.delivery
from picard.Jan.xml_config_parser import TagParser
import picard.Jan.strategylogic

logger = logging.getLogger(__name__)
program_version = "Jan ver. 0.7 alfa"
context = dict()
context['program_version'] = program_version



def index(request):

    queue = Queue.objects.select_related().order_by('place')
    history = History.objects.all().order_by('-release_date')[:5]
    context['now'] = datetime.now()
    context['queue'] = queue 
    context['history'] = history
    return render_to_response('Jan/index.html', {'context': context, })


def history(request):

    history = History.objects.select_related().order_by('-release_date')
    queue = Queue.objects.select_related().order_by('place')[:5]
    paginator = Paginator(history, 15)  
    
    page = request.GET.get('page')
    try:
        history = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        history = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        history = paginator.page(paginator.num_pages)

    if request.method == 'POST':
        form = HistoryFilterForm(request.POST)
        if form.is_valid():
            #be more intuitive
            form.cleaned_data['to_date'] += timedelta(days=1)
            history = History.objects.select_related().filter(
                build__branch_id__exact=form.cleaned_data['branch'],
                release_date__gte=form.cleaned_data['from_date'],
                release_date__lte=form.cleaned_data['to_date']).order_by('-release_date')

    else:
        form = HistoryFilterForm()
   
    context['form'] = form
    context['now'] = datetime.now()
    context['queue'] = queue 
    context['history'] = history
    
    return render_to_response('Jan/history.html', {'context': context, }, context_instance=RequestContext(request))


def content(request, id):

    build = get_object_or_404(Build, pk=id)

    #give back info about queue item
    queue_items = Queue.objects.filter(build__exact=build.id).values()

    #retrive all build information from dependent tables
    faults = Fault.objects.filter(content__id__exact=build.content.id)
    baselines = Baseline.objects.filter(content__id__exact=build.content.id)
    externals = External.objects.filter(content__id__exact=build.content.id)
    delivery_locations = DeliveryLocation.objects.filter(branch__id__exact=build.branch.id)

    #build context
    context['now'] = datetime.now()
    context['queue_items'] = queue_items
    context['branch'] = build.branch
    context['content'] = build.content
    context['faults'] = faults 
    context['baselines'] = baselines
    context['externals'] = externals
    context['delivery_locations'] = delivery_locations 

    return render_to_response('Jan/content.html', {'context':context,})


def history_content(request, id):

    build = get_object_or_404(Build, pk=id)

    #give back info about history item
    history_items = History.objects.filter(build__exact=build.id).values()

    #retrive all build information from dependent tables
    faults = HistoryFault.objects.filter(content__id__exact=build.content.id)
    baselines = Baseline.objects.filter(content__id__exact=build.content.id)
    externals = External.objects.filter(content__id__exact=build.content.id)
    delivery_locations = HistoryDeliveryLocation.objects.filter(history__id__exact=history_items[0]['id'])

    #build context
    context['now'] = datetime.now()
    context['history_items'] = history_items
    context['branch'] = build.branch
    context['content'] = build.content
    context['faults'] = faults 
    context['baselines'] = baselines
    context['externals'] = externals
    context['delivery_locations'] = delivery_locations 

    return render_to_response('Jan/history_content.html', {'context': context, })


def mock(request):
    
    return render_to_response('Jan/mock.html', {})


#api methods:

def api(request):
 
    return render_to_response('Jan/mock.html', {})


def trigger(request):

    log = []

    queue = Queue.objects.select_related().order_by('place')

    for item in queue:
        #it is time for delivery?
        if item.release_date < datetime.now():
            log.append("Delivering for {branch}".format(branch=item.build.branch))
            log.append("Planned delivery date: {date}".format(date=item.release_date))
            log.append("Package has been taken from location: {location}".format(location=item.from_location))
            log.append("Package has been delivered to location(s):")

            #figure out delivery locations
            delivery_locations = DeliveryLocation.objects.filter(branch__id__exact=item.build.branch.id)
            for location in delivery_locations:
                destination = location.to_location + ','
            try:
                log.append(destination)
            except UnboundLocalError:
                raise Http404("Most probably branch does not have delivery location defined")

            config = TagParser(config=item.build.branch.delivery_config).parse()
            print config.location_transport
            config.location = item.from_location
            config.destination = destination

            #deliver package
            transport = picard.Jan.delivery.delivery(config, item.build.branch.name)
            transport.clean()
            transport.prepare_packages()
            transport.deliver_packages()
            
            #store delivered package in history of deliveries
            history = History(
                build=item.build,
                place=item.place,
                release_date=item.release_date,
                from_location=item.from_location
            )
            history.save()

            #store also delivery location(s)
            for location in DeliveryLocation.objects.filter(branch=history.build.branch):
                history_delivery_location = HistoryDeliveryLocation(
                    history=history,
                    to_location=location.to_location
                )
                history_delivery_location.save()

            #figure out and save faults
            if item.build.content.fault_log_end > item.build.branch.latest_fault_log_end: 
                subversion = picard.Jan.svn.SVN(item.build.content.fault_log_location)
                svnlog = subversion.log(item.build.content.fault_log_end, int(item.build.branch.latest_fault_log_end) + 1)
                contentNote = picard.Jan.contentnote.ContentNote(None)
                try:
                    patterns = literal_eval(item.build.branch.svn_log_parser_config_patterns)
                    relax_field = literal_eval(item.build.branch.svn_log_parser_config_relax_field)
                except ValueError, explanation:
                    raise Http404(explanation)
                faults = contentNote.faultLogAsListOfDictionaries(svnlog, patterns, relax_field)
                print faults
                for fault in faults:
                    history_fault = HistoryFault(
                        content=item.build.content,
                        pronto=fault['pronto'],
                        revision=fault['revision'],
                        info=fault['info'],
                        partial=fault['partial'],
                        description=fault['description'],
                        module="",
                    )
                    history_fault.save()
            #set start of fault range to latest end of fault log
            item.build.content.fault_log_start = int(item.build.branch.latest_fault_log_end) + 1
            item.build.content.save()
            #change latest delivered revision for branch and fault log
            item.build.branch.latest_delivered_revision = item.build.content.revision
            item.build.branch.latest_fault_log_end = item.build.content.fault_log_end
            item.build.branch.save()

            #and remove delivered item from queue
            item.delete()
            destination = []
    
    context['log'] = log

    return render_to_response('Jan/trigger.html', {'context':context,})


def schedule(request):
    
    #harvest all data
    api = picard.Jan.api.Api(request)
    data = api.get(['component', 'branch', 'note', 'artifacts', 'time'])
    if data:
        #TODO:
        #api.sanitize(data,'string','string','string','string','datetime')
        note = picard.Jan.contentnote.ContentNote(data['note'])
        raw_content = note.raw()
        if not raw_content:
            raise Http404(note.exception())
    else:
        raise Http404(api.exception())

    #build model objects
    #content:
    parsed_content = note.get()
    content = Content(
        content=raw_content,
        location=parsed_content['location'],
        revision=parsed_content['revision'],
        content_note_link=data['note'],
        name=parsed_content['name'],
        system=parsed_content['system'],
        fault_log_location=parsed_content['fault_log_location'],
        fault_log_start=parsed_content['fault_log_start'],
        fault_log_end=parsed_content['fault_log_end'],
        compilation_date=parsed_content['compilation_date'],
    )

    content.save()
    
    #faults for content
    for fault_dict in parsed_content['faults']:
        fault = Fault(
            content=content,
            pronto=fault_dict['pronto'],
            revision=fault_dict['revision'],
            info=fault_dict['info'],
            partial=fault_dict['partial'],
            description=fault_dict['description'],
            module=parsed_content['module'],
        )
        fault.save()

    #baselines for content
    for baseline_dict in parsed_content['baselines']:
        baseline = Baseline(
            content=content,
            baseline=baseline_dict['description'],
        )
        baseline.save()

    #externals for content
    for external_dict in parsed_content['externals']:
        external = External(
            content=content,
            external=external_dict['description'],
        )
        external.save()

    #match the proper branch (remark: returns lists)
    branches = Branch.objects.filter(component=data['component'], name=data['branch'])

    #construct and save the build:
    try:
        build = Build(content=content, branch=branches[0])
    except IndexError:
        raise Http404("Can not add compilation. Most probably there's no such branch defined you provided")
    build.save()

    #apply delivery strategy and place build in queue

    #figure out latest delivered build for appropriate branch
    history_items = History.objects.filter(build__branch__exact=branches[0]).order_by("-release_date")
    
    if history_items:
        latest_delivered_build = history_items[0].build
    else:
        latest_delivered_build = None

    strategy = picard.Jan.strategylogic.StrategyLogic(build_for_delivery=build,
                                                      latest_delivered_build=latest_delivered_build,
                                                      case=build.branch.strategy.strategy)
    release_date = strategy.execute()
    
    if release_date:
 
        #add to delivery queue

        place_dict = Queue.objects.all().aggregate(Max('place'))
        if place_dict['place__max']:
            place = place_dict['place__max'] + 1
        else:
            place = 1
        from_location = data['artifacts']

        queue = Queue(
            build=build,
            place=place,
            release_date=release_date,
            from_location=data['artifacts'],
        )
    
        queue.save()
    
    return render_to_response('Jan/schedule.html', {})


def faults(request):

    messages = []
    faults = []

    #harvest all data
    api = picard.Jan.api.Api(request)
    data = api.get(['branch', 'location', 'revision'])
    if data:
        #TODO:
        #api.sanitize(date,'string','string','integer')
        branch = Branch.objects.filter(name=data['branch'])[0]
        subversion = picard.Jan.svn.SVN(data['location'])
        if int(data['revision']) > int(branch.latest_fault_log_end) + 1:
            log = subversion.log(data['revision'], int(branch.latest_fault_log_end) + 1)
            for item in log:
                messages.append(unicode(item.message, 'utf-8', 'strict').encode('ascii', 'ignore'))

            contentNote = picard.Jan.contentnote.ContentNote(None)
            try:
                patterns = literal_eval(branch.svn_log_parser_config_patterns)
                relax_field = literal_eval(branch.svn_log_parser_config_relax_field)
            except SyntaxError, explanation:
                raise Http404(
                    "Error while evaluating SVN log parser config."
                    + "Most probably there are no patterns defined. {explanation}".format(explanation=explanation)
                )
            faults = contentNote.faultLogAsListOfDictionaries(log, patterns, relax_field)
    else:
        raise Http404(api.exception())

    context['messages'] = messages
    context['faults'] = faults
   
    return render_to_response('Jan/faults.html', {'context': context, })


def btsbuilds(request):

    builds = []
    #harvest all data from api
    api = picard.Jan.api.Api(request)
    data = api.get(['branch', 'name'])
 
    if data:
        #api.sanitize('string','string')
        branch = get_object_or_404(Branch, name=data['branch'])

        if branch:
            #select cursor for appropriate database
            cursor = connections[branch.cb_database_alias].cursor()
            cursor.execute("""
                        SELECT 
                            release_time,
                            packag_name, 
                            buildurl, 
                            build_configuration 
                        FROM central_build WHERE 
                            {component_field_name}=%s and 
                            lswbt_status='Released' 
                        ORDER BY release_time 
                        """.format(component_field_name=branch.cb_component_field_name), [data['name'], ])

            builds = cursor.fetchall()
    else:
        raise Http404(api.exception())

    context['builds'] = builds
   
    return render_to_response('Jan/btsbuilds.html', {'context': context, })

