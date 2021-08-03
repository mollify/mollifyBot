# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"


from typing import Dict, Text, List, Optional, Any

from rasa_sdk import Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormValidationAction, FormAction
from rasa_sdk.executor import CollectingDispatcher, Action
from rasa_sdk.events import AllSlotsReset, SlotSet
from rasa_sdk.events import SlotSet, EventType
from rasa_sdk.types import DomainDict
from utility.utility import grounding_slots,grounding_questions


class ActionAskName(Action):

    def name(self) -> Text:
        return "action_remember_name"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        text = tracker.latest_message["text"]

        dispatcher.utter_message(text=f"Nice name {text}")

        return [SlotSet("name", text)]
#

# class ActionSayName(Action):
#
#     def name(self) -> Text:
#         return "action_say_name"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#         name = tracker.get_slot("name")
#         if not name:
#             dispatcher.utter_message(text="you have not mention your name yet")
#         else:
#             dispatcher.utter_message(text=f"Its good to meet you {name}")
#
#         return []
#
# class ActionActivity(Action):
#     def name(self) -> Text:
#         return "action_activity"
#
#     def run(
#         self,
#         dispatcher: "CollectingDispatcher",
#         tracker: Tracker,
#         domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

class ValidateFeelingForm(FormValidationAction):
    def __init__(self):
        self.feeling_list = []

    def name(self) -> Text:
        return "validate_feelings_form"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:

        value = tracker.latest_message.get("text")
        slot_to_fill = tracker.get_slot("requested_slot")
        intent = tracker.latest_message.get("intent", {}).get("name")

        if slot_to_fill == "validation_string":
            if intent == "end":
                feelings = tracker.get_slot("feelings_list")
                dispatcher.utter_message(text="you are have these feelings ")
                for ele in feelings:
                    dispatcher.utter_message(text=f"{ele}")
                return [SlotSet("validation_string", True)]

            else:
                dispatcher.utter_message(response="utter_anything_else")
                SlotSet("share_feelings", value)
                self.feeling_list.append(value)
                print(self.feeling_list)

                return [SlotSet("validation_string", None), SlotSet("share_feelings", value),
                        SlotSet("feelings_list", self.feeling_list)]
        elif slot_to_fill == "share_feelings":
            self.feeling_list.append(value)
            dispatcher.utter_message(response="utter_anything_else")

        return []

    def validate_share_feelings(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate slot value."""
        print("share_feelings func")
        if not slot_value:
            return {"share_feelings": None}
        else:
            return {"share_feelings": slot_value}

    def validate_validation_string(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate slot value."""
        print("validation_string func")
        if not slot_value:
            return {"validation_string": None}
        else:
            return {"validation_string": slot_value}

    def validate(
            self,
            dispatcher: "CollectingDispatcher",
            tracker: "Tracker",
            domain: "DomainDict",
    ) -> List[EventType]:
        value = tracker.latest_message.get("text")
        slot_to_fill = tracker.get_slot("requested_slot")
        intent = tracker.latest_message.get("intent", {}).get("name")
        print("inside validate")
        if slot_to_fill == "validation_string":
            if intent == "affirm":
                return [SlotSet("validation_string", value)]
            else:
                dispatcher.utter_message("utter_anything_else")
                return [SlotSet("validation_string", None)]
        return []

    def submit(self, dispatcher: CollectingDispatcher,
               tracker: Tracker,
               domain: Dict[Text, Any]) -> List[Dict]:

        return [SlotSet("validation_string", None), SlotSet("share_feelings", None)]


class ActionResetAllButFewSlots(Action):
    def name(self):
        return "action_reset_all_but_few_slots"

    def run(self, dispatcher, tracker, domain):
        bank = tracker.get_slot('bank')
        return [AllSlotsReset()]


class ActionSubmitFeelingsForm(Action):
    def name(self) -> Text:
        return "action_submit_feelings_form"

    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> List[EventType]:
        """Once we have all the information, attempt to add it to the
        Google Drive database"""

        import datetime

        share_feeling = tracker.get_slot("share_feelings")

        feelings = [share_feeling]

        dispatcher.utter_message(template="utter_confirm_salesrequest")
        return []


class ValidateGroundingForm(FormValidationAction):
    def __init__(self):
        self.grounding_list = []
    def name(self) -> Text:
        return "validate_grounding_form"

    # def run(
    #         self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    # ) -> List[EventType]:
    #     # print("inside run {}".format(tracker.__dict__))
    #
    #     value = tracker.latest_message.get("text")
    #     slot_to_fill = tracker.get_slot("requested_slot")
    #     intent = tracker.latest_message.get("intent", {}).get("name")
    #     print(slot_to_fill)
    #     if intent != "end" or "deny" or "affirm" or "nlu_fallback":
    #         print(tracker.get_slot(grounding_slots[0]))
    #         return [SlotSet(grounding_slots[0], value)]
    #
    #     else:
    #         dispatcher.utter_message(response="utter_anything_else")
    #         # SlotSet("share_feelings", value)
    #         # tracker.slots["share_feelings"].append(value)
    #
    #
    #         return [SlotSet("validation_string", None), SlotSet("share_feelings", value)]
    #     # elif slot_to_fill == "share_feelings":
    #     #     feeling_list.append(value)
    #     #     dispatcher.utter_message(response="utter_anything_else")



    def validate_can_see(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate slot value."""
        if not slot_value:
            return {grounding_slots[0]: None}
        else:
            if len(slot_value) < 5:
                self.grounding_list.append(slot_value.slpit(" "))
                dispatcher.utter_message(f"please complete {5-len(slot_value)} more values")
            else:
                values = self.grounding_list
                self.grounding_list.clear()
                return {grounding_slots[0]: values}

    def validate_can_feel(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate slot value."""
        print("share_feelings func")
        if not slot_value:
            return {grounding_slots[1]: None}
        else:
            return {grounding_slots[1]: slot_value}

    def validate_can_hear(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate slot value."""
        print("share_feelings func")
        if not slot_value:
            return {grounding_slots[2]: None}
        else:
            return {grounding_slots[2]: slot_value}

    def validate_can_smell(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate slot value."""
        print("share_feelings func")
        if not slot_value:
            return {grounding_slots[3]: None}
        else:
            return {grounding_slots[3]: slot_value}

    def validate_can_taste(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate slot value."""
        print("share_feelings func")
        if not slot_value:
            return {grounding_slots[4]: None}
        else:
            return {grounding_slots[4]: slot_value}




#
#
# a = "https://forum.rasa.com/t/store-array-in-form-slot/31302/3"
