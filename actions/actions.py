from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, EventType
from rasa_sdk.types import DomainDict
import pandas as pd

import openai


course = pd.read_csv('Course.csv')
years = ','.join(pd.unique(course.copy()['Year']).astype(str))
itf = pd.read_csv('06026100.csv')

def searhingcouseofyear(year, course):
    coursey = course[course['Year'] == year]
    df = coursey[['course_id','course_name']]
    return df.to_string()

    

class ValidateCourseForm(FormValidationAction):
    def name(self) -> Text:
        return 'validate_show_course'
    
    def validate_year(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate Year"""
        if str(slot_value.lower()) not in years:
            dispatcher.utter_message(text=f'We have only {years} year.')
            return {'year': None}
        dispatcher.utter_message(text=f'OK! This is courses of {slot_value} year.\n{searhingcouseofyear(slot_value, course)}')
        return

class ActionFallback(Action):

    def name(self) -> Text:
        return "action_echo"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        openai.api_key = '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'


        prompt = """ 
            You duty is answer questions
            ---
            If the user doesn't know about any word please give them the words meaning and then return back to where you stopped the conversation 
            ---
            Reply only to the last message of the user
            --- 
            dont say 'Hey there' or 'hi there'
            ---
            send only the bot's response, dont say 'bot:' and then response
            ---
            following is the chat history 
            """


        question = "\n\n user: "+tracker.latest_message["text"][0:]
        hist_slot = " "
        hist_slot = str(tracker.slots.get('hist_slot'))+question
        #hist_slot stores the history fo the conversation

        #pmt is the ffinal prompt to send to open ai
        pmt  = prompt + hist_slot + " \n ---\n reply to only this text :"+question

        response = openai.Completion.create(
                engine="gpt-3.5-turbo-instruct",
                prompt= pmt,
                max_tokens=1024,
                n=1,
                stop=None,
                temperature=0.5
            ).choices[0].text
        
        
        dispatcher.utter_message(response.replace('Bot:', ''))
        hist_slot = hist_slot + "\nBot: "+response

        return [SlotSet("hist_slot", hist_slot)]

# class ActionNLUFallback(Action):
#     def name(self) -> Text:
#         return "action_default_fallback"

#     def run(
#         self,
#         dispatcher: CollectingDispatcher,
#         tracker: Tracker,
#         domain: Dict[Text, Any],
#     ) -> List[EventType]:
#         action_events = [e for e in tracker.events if e["event"] == "action"]
#         if len(action_events) > 1 and action_events[-2].get("name") == "action_default_fallback":
#               dispatcher.utter_message(template="utter_goodbye")
#         else:
#               dispatcher.utter_message(template="utter_default")
