#!/usr/bin/env python

import re
import sys
import copy
from datetime import datetime
from datetime import timedelta


#Note to grader - I have used my own code from assignment 2 as a reference for bits 
#                 and pieces of this assignment.

class process_cal:
    def __init__(self, filename):
        self.filename=filename
    
    #getter method
    def get_filename(self):
        return self.filename

    #open, read and close file. Get all content onto a string.
    def read_file(self):
        file_content = ""
        f = open(self.filename, "r")
        while (True):
            line = f.readline()
            if not line:
                break
            file_content += line
        f.close()
        return file_content
    
    #parse the given string into a list of object events
    def parse_into_events(self, file_content):
        
        #the final list to populate:
        ical_events = []
        
        #create new event object to populate
        ev = event(None, None, None, None, None)
        for line in file_content.split("\n"):
            
            #splitting each line on a colon using RegEx
            line_list = re.split(":", line)
            
            #the following is in case value is an empty string
            if len(line_list)>1:
                value = line_list[1]
            else:
                value = ""
            key = line_list[0]
            
            #if key is any of the following then populate the parameter of the object event
            if key in ["DTSTART", "DTEND", "RRULE", "LOCATION", "SUMMARY"]:
                if key == "DTSTART":
                    ev.set_dtstart(value)
                elif key == "DTEND":
                    ev.set_dtend(value)
                elif key == "RRULE":
                    ev.set_rrule(value)
                elif key == "LOCATION":
                    ev.set_location(value)
                else:
                    ev.set_summary(value)
                
            elif (key == "END" and value == "VEVENT"):
                #we have entered all data. Append ev to ical_events
                ical_events.append(copy.deepcopy(ev)) 
                #setting rrule to null such that we can use the blueprint for event again
                ev.set_rrule(None)
            else:
                continue
            
        for ev in ical_events:
            ev.set_dtstart(datetime.strptime(ev.get_dtstart(), "%Y%m%dT%H%M%S"))
            ev.set_dtend(datetime.strptime(ev.get_dtend(), "%Y%m%dT%H%M%S"))
        return ical_events
    
    #The following method is to explode the events that are recurring. It only looks
    #at the rrule expiry date of each event. Any further date restritrictions (such as those 
    # specified by a user) are not regarded in this method.
    def explode_events(self, ical_events):
        ev = event(None, None, None, None, None)

        for e in ical_events:
            #we only want to look at the events that have data in the rrule
            if (e.get_rrule() != "" and e.get_rrule() != None):
                e_copy = copy.deepcopy(e)

                #get the expiry datetime from rrule using RegEx:
                expiry_date = datetime.strptime(re.split('[LB]', str(e_copy.get_rrule()))[2], "=%Y%m%dT%H%M%S;")
                e_copy.set_rrule(None)

                #we want to grab next week's recurrence of this event as this week's is already in the ical list
                e_copy.set_dtstart(e_copy.get_dtstart() + timedelta(days=7))
                e_copy.set_dtend(e_copy.get_dtend()+ timedelta(days=7))
                
                while (expiry_date >= e_copy.get_dtstart()):
               
                    #populate ev since all data is the same
                    ev.set_dtstart(e_copy.get_dtstart())               
                    ev.set_dtend(e_copy.get_dtend())
                    ev.set_location(e_copy.get_location())
                    ev.set_summary(e_copy.get_summary())
                    
                    #update times to next week
                    e_copy.set_dtstart(e_copy.get_dtstart()+ timedelta(days=7))
                    e_copy.set_dtend(e_copy.get_dtend()+ timedelta(days=7))
        
                    ical_events.append(copy.deepcopy(ev))
                      
            else:
                continue
        return ical_events

    #this method sorts list of events by dtstart
    def sort(self, ical_events):
        ical_events = sorted(ical_events, key = lambda x: x.get_dtstart())
        return ical_events       

    #grab all events on a specific day
    def get_all_on_date(self, ical_events, today):
        return [e for e in ical_events if e.dtstart >= today and e.dtstart <=today+timedelta(hours=24)]

    #helper method to format date into the desired form
    def format_date(self, datetime_date):
        return datetime.strftime(datetime_date, "%B %d, %Y (%a)")

    #this method gets all the events on a specific day and formats them into a string
    #to be returned
    def get_events_for_day(self, today):

        file_content = self.read_file()
        events = self.parse_into_events(file_content)
        events = self.explode_events(events)
        events = self.sort(events)
        events = self.get_all_on_date(events, today)
        
        pretty_ev = ""
        print("size of events is: " + str(len(events)))
        if (len(events) >0):
            pretty_ev += self.format_date(today) + "\n" + "-"* len(self.format_date(today))
        for e in events:
            pretty_ev += "\n" + e.get_formatted_summary()
        
        return pretty_ev

class event:
    def __init__(self, dtstart, dtend, rrule, location, summary):
        self.dtstart = dtstart
        self.dtend = dtend
        self.rrule = rrule
        self.location = location
        self.summary = summary

    #the following are setters
    def set_dtstart(self, dtstart):
        self.dtstart = dtstart
    def set_dtend(self, dtend):
        self.dtend = dtend
    def set_rrule(self, rrule):
        self.rrule = rrule
    def set_location(self, location):
        self.location = location
    def set_summary(self, summary):
        self.summary = summary

    #the following are getters
    def get_dtstart(self):
        return self.dtstart
    def get_dtend(self):
        return self.dtend
    def get_rrule(self):
        return self.rrule
    def get_location(self):
        return self.location
    def get_summary(self):
        return self.summary

    #this method formats the summary as is desired. 
    def get_formatted_summary(self):

        #creating a string variable called 'space_padded_start' & 'end' in case hours start with a 0
        #the 0 will be replaced with a space
        space_padded_start = datetime.strftime(self.get_dtstart(),"%I")
        if '0' == space_padded_start[0]:
            space_padded_start = ' ' + space_padded_start[1:]
        space_padded_end = datetime.strftime(self.get_dtend(),"%I")
        if '0' == space_padded_end[0]:
            space_padded_end = ' ' + space_padded_end[1:]


        return space_padded_start + ":" + datetime.strftime(self.get_dtstart(),"%M %p") \
            + " to " + space_padded_end + ":" + datetime.strftime(self.get_dtend(), "%M %p: ")+\
                 self.get_summary() + ' {{'+ self.get_location()+'}}'

    