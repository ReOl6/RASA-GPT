from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

import openai


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
                engine="text-davinci-003",
                prompt= pmt,
                max_tokens=1024,
                n=1,
                stop=None,
                temperature=0.5
            ).choices[0].text
        
        
        dispatcher.utter_message(response.replace('Bot:', ''))
        hist_slot = hist_slot + "\nBot: "+response

        return [SlotSet("hist_slot", hist_slot)]
