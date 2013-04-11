# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from ast import literal_eval

import picard.Jan.svn
import picard.Jan.contentnote

class StrategyLogic:

    """
    transparent : 0,
    one_per_day : 1,
    at_least_one_correction : 2 / needs svn connectivity
    on_demand : 3
    """

    def __init__(self, build_for_delivery, latest_delivered_build, case = 0, prio = 2):

        self.delivery_date = datetime.now() 
        self.case = case
        self.prio = prio
        self.build_for_delivery = build_for_delivery
        self.latest_delivered_build = latest_delivered_build

        # if there's no latest delivered build -> deliver immediately 
        if not self.latest_delivered_build:
            self.case = 0

    def transparent(self):
        return self.delivery_date

    def one_per_day(self):
        pass

    def at_least_one_correction(self):

        #skip queuing of the same software versions
        if int(self.latest_delivered_build.content.revision) == int(self.build_for_delivery.content.revision):
            return None
        
        subversion = picard.Jan.svn.SVN(self.build_for_delivery.content.location)
        log = subversion.log(self.build_for_delivery.content.revision, int(self.latest_delivered_build.content.revision)+1)
        contentNote = picard.Jan.contentnote.ContentNote(None)
        try:
            patterns = literal_eval(self.build_for_delivery.branch.svn_log_parser_config_patterns)
            relax_field = literal_eval(self.build_for_delivery.branch.svn_log_parser_config_relax_field)
        except ValueError,explanation:
            raise Http404(explanation)
        faults = contentNote.faultLogAsListOfDictionaries(log, patterns, relax_field)
        if len(faults) > 0:
            return self.delivery_date
        else:
            return None


    def on_demand(self):

        self.delivery_date += timedelta(days=365)
        return self.delivery_date

    def execute(self):
	
        if self.case == 0:
            return self.transparent()
        elif self.case == 1:
            return self.one_per_day()
        elif self.case == 2:
            return self.at_least_one_correction()
        elif self.case == 3:
            return self.on_demand()




