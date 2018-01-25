import pickle
import re
import json
import logging

import sys

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class Thing(object):

    def __init__(self, guess):
        self.guess = ""
        self.things = {}
        self.guess = Xform.encode(guess.upper())

    def getGuess(self):
        return Xform.decode(self.guess)

    def addThing(self, newQuestion, newThing):
        newKey = Xform.encode(newQuestion.upper())
        self.things[newKey] = newThing
        pass


class Xform:

    encodes = {
        "I'M ": "a01",
        "I AM ": "a01",
        "I ": "b01"
    }

    decodes = {
        "a01": "ARE YOU ",
        "b01": "DO YOU "
    }

    encodes_context = {
        "I'M": "x01",
        "I AM": "x02"
    }

    decodes_context = {
        "x01": "THAT YOU'RE",
        "x02": "THAT YOU ARE "
    }

    @staticmethod
    def xform(txt, haystack):
        for k, v in haystack.items():
            if re.match(k, txt):
                return v + txt[len(k):]
        return ""

    @staticmethod
    def encode(txt):
        etxt = Xform.xform(txt, Xform.encodes)
        for eFrom, eTo in Xform.encodes_context.items():
            etxt = etxt.replace(eFrom, eTo)
        etxt.replace(" ", "_")
        return etxt

    @staticmethod
    def decode(txt):
        dtxt = Xform.xform(txt, Xform.decodes)
        for dFrom, dTo in Xform.decodes_context.items():
            dtxt = dtxt.replace(dFrom, dTo)
        dtxt.replace("_", " ")
        return dtxt


t = Thing("I am Brian")
t2 = t
q = 0
session_state = "begin"
new_desc = ""
new_guess = ""
speech_prefix = ""


def newThing(here):
    newQuestion = input("TELL ME SOMETHING ABOUT YOURSELF: ").upper()
    newGuess = input("OK, WHAT ARE YOU?: ").upper()

    newThing = Thing(newGuess)
    here.addThing(newQuestion, newThing)


def investigate(here):
    for question, thing in here.things.items():
        if yes_or_no(Xform.decode(question)):
            investigate(thing)
            return
    print("I GIVE UP...")
    if yes_or_no(here.getGuess()):
        print("I THOUGHT SO!")
    else:
        newThing(here)


def yes_or_no(question):
    while "the answer is invalid":
        reply = str(input(question+'? (Y/N): ')).lower().strip().upper()
        if not reply:
            continue
        if reply[0] == 'Y':
            return True
        if reply[0] == 'N':
            return False


def lambda_handler(event, context):
#    print("event.session.application.applicationId=" +
#          event['session']['application']['applicationId'])
#    logger.info("SAJ event: " + json.dumps(event))
    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
#    if (event['session']['application']['applicationId'] !=
#            "amzn1.echo-sdk-ams.app.[ amzn1.ask.skill.1c056782-3d7b-4610-bfc1-4aa89d86a266]"):
#        raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])


def on_intent(intent_request, session):
    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "ReadyIntent":
        return said_ready(intent, session)
    elif intent_name == "DescribePersonIntent":
        return described_person(intent, session, "a01")
    elif intent_name == "DescribeThingIntent":
        return described_thing(intent, session, "b01")
    elif intent_name == "AMAZON.YesIntent":
        return said_yes(intent, session)
    elif intent_name == "AMAZON.NoIntent":
        return said_no(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return said_cancel()
    else:
        raise ValueError("Invalid intent")


def said_ready(intent, session):
    global t, t2, q, session_state, speech_prefix
    logger.info("Hit ready entry point: " + session_state)
    if session_state == "begin":
        t2 = t
        q = 0
        session_state = "ask"
        return ask_question(intent, session)
    else:
        session_state = "begin"
        t2 = t
        q = 0
        speech_prefix = "OK, let's begin again."
        return ask_question(intent, session)


def described_person(intent, session, thing_type):
    speech_text = thing_type + intent['slots']['PersonDescription']['value'].upper()
    logger.info("description: " + speech_text)
    return new_description(intent, session, speech_text)


def described_thing(intent, session, thing_type):
    speech_text = thing_type + intent['slots']['ThingDescription']['value'].upper()
    logger.info("description: " + speech_text)
    return new_description(intent, session, speech_text)


def new_description(intent, session, speech_text):
    global t2, q, session_state, new_desc, new_guess
    session_attributes = {}
    card_title = "Describe"
    if session_state == "more":
        logger.info("new desc: " + speech_text)
        new_desc = speech_text
        session_state = "what"
        speech_output = "OK, so tell me, what are you"
        reprompt_text = "Please tell what you are"
        should_end_session = False
        return build_response(session_attributes, build_speechlet_response(
            card_title, speech_output, reprompt_text, should_end_session))
    elif session_state == "what":
        new_guess = speech_text
        logger.info("creating new thing: q: " + str(q) + "new: " + new_guess)
        new_thing = Thing(new_guess)
        t2.things[new_desc] = new_thing
        q = 0
        session_state = "begin"
        speech_output = "Interesting, I guess I've learned something. " \
            "Say READY to play again"
        reprompt_text = "Say READY to begin or CANCEL to end"
        should_end_session = False
        return build_response(session_attributes, build_speechlet_response(
            card_title, speech_output, reprompt_text, should_end_session))

    speech_output = "Please reply YES or NO"
    reprompt_text = "You can say CANCEL any time to quit playing"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def said_yes(intent, session):
    global t2, q, session_state
    session_attributes = {}
    card_title = "Warmer"
    if session_state == "ask":
        try:
            key = list(t2.things)[q]
            t2 = t2.things[key]
            q = 0
            return ask_question(intent, session)
        except:
            session_state = "guess"
            return make_guess(intent, session)

    else:
        if session_state == "guess":
            speech_output = "I thought so! " \
                "Say READY to play again or CANCEL to end"
            reprompt_text = "Say READY to play again"
            should_end_session = False
            return build_response(session_attributes, build_speechlet_response(
                card_title, speech_output, reprompt_text, should_end_session))


def ask_question(intent, session):
    global t2, q, session_state
    session_attributes = {}
    card_title = "Guessing"
    try:
        logger.info("trying to find next thing " + str(q) + list(t2.things.keys())[q])
        speech_output = Xform.decode(list(t2.things.keys())[q])
        reprompt_text = "Please answer YES or NO"
        should_end_session = False
        return build_response(session_attributes, build_speechlet_response(
            card_title, speech_output, reprompt_text, should_end_session))
    except IndexError:
        session_state = "guess"
        return make_guess(intent, session)
    except:
        logger.info(sys.exc_info()[0])
        logger.info(sys.exc_info()[1])
        logger.info(sys.exc_info()[2])


def make_guess(intent, session):
    global t2, q, session_state
    logger.info("Making guess")
    session_attributes = {}
    card_title = "Guessing"
    speech_output = "I'll guess " + t2.getGuess()
    logger.info(speech_output)
    reprompt_text = "Please answer YES or NO"
    should_end_session = False
    dict = build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))
    return dict


def said_no(intent, session):
    global t2, q, session_state
    session_attributes = {}
    card_title = "Colder"
    if session_state == "ask":
        q = q+1
        return ask_question()
    elif session_state == "guess":
        session_state = "more"
        speech_output = "To help me learn please tell me something about yourself."
        reprompt_text = "Please tell me something about yourself."
        should_end_session = False
        return build_response(session_attributes, build_speechlet_response(
            card_title, speech_output, reprompt_text, should_end_session))
    # elif session_state == "more":
    #     session_state = "what"
    #     speech_output = "OK, so tell me, what are you."
    #     reprompt_text = "Please tell me what you are."
    #     should_end_session = False
    #     return build_response(session_attributes, build_speechlet_response(
    #         card_title, speech_output, reprompt_text, should_end_session))


# --------------- Functions that control the skill's behavior ------------------


def get_welcome_response():

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to the Piedmont Things Alexa application. " \
                    "Think of yourself as a thing, " \
                    "and I will try to guess what you are. " \
                    "When you are ready to begin, say READY"
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Say READY to begin or CANCEL to end"

    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def said_cancel():
    card_title = "Session Ended"
    speech_output = "Thank you for playing Piedmont Things. " \
                    "Have a nice day! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))


def build_speechlet_response(title, output, reprompt_text, should_end_session):
    global speech_prefix
    the_output = speech_prefix + output
    speech_prefix = ""
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': 'SessionSpeechlet - ' + title,
            'content': 'SessionSpeechlet - ' + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    dict = {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }

    return dict


def on_session_started(session_started_request, session):
    pass


def on_launch(launch_request, session):
    return get_welcome_response()


def on_session_ended(session_ended_request, session):
    pass


#t = Thing("I am Brian")
#t1 = Thing("t1")
#t.addThing("q1", t1)
#t2 = Thing("t2")
#t.addThing("q2", t2)
#print(t.things[0])
#x = pickle.dumps(t)
#print(type(x))
#t2 = pickle.loads(x)
#print(t2==t)
#print(t2 is t)
#while True:
#    investigate(t)
#    if not yes_or_no("Play again"):
#        break

#s = json.dumps(t)
#print(s)

#exit()


