import re
import logging


class Thing(object):

    def __init__(self, guess):
        self.guess = ""
        self.things = {}
        self.guess = guess.upper()

    def get_guess(self):
        return Xform.guess_decode(self.guess)
#        return Xform.guess_decode(self.guess)

    def add_thing(self, new_question, new_thing):
        # new_key = Xform.encode(new_question.upper())
        self.things[new_question] = new_thing
        pass

    def get_nodes(self):
        return list(self.things)


class Xform:

    encodes = {
        "I'M ": "A01",
        "I AM ": "A01",
        "I ": "B01"
    }

    decodes = {
        "A01": "ARE YOU ",
        "B01": "DO YOU "
    }

    guess_decodes = {
        # "A01": "THAT YOU ARE ",
        # "B01": "THAT YOU ARE "
        "A01": "ARE YOU ",
        "B01": "ARE YOU "
    }

    encodes_context = {
        "I'M": "X01",
        "I AM": "X02",
        " I ": "X03"
    }

    decodes_context = {
        "X01": "YOU'RE",
        "X02": "YOU ARE",
        "X03": " YOU "
    }

    @staticmethod
    def xform(txt, haystack):
        for k, v in haystack.items():
            if re.match(k, txt):
                return v + txt[len(k):]
        return ""

    @staticmethod
    def encode(txt):
        encode_txt = Xform.xform(txt, Xform.encodes)
        for eFrom, eTo in Xform.encodes_context.items():
            encode_txt = encode_txt.replace(eFrom, eTo)
        encode_txt.replace(" ", "_")
        return encode_txt

    @staticmethod
    def decode(txt):
        decode_txt = Xform.xform(txt, Xform.decodes)
        for dFrom, dTo in Xform.decodes_context.items():
            decode_txt = decode_txt.replace(dFrom, dTo)
        decode_txt.replace("_", " ")
        return decode_txt

    @staticmethod
    def guess_decode(txt):
        decode_txt = Xform.xform(txt, Xform.guess_decodes)
        for dFrom, dTo in Xform.decodes_context.items():
            decode_txt = decode_txt.replace(dFrom, dTo)
        decode_txt.replace("_", " ")
        return decode_txt


logger = logging.getLogger()
logger.setLevel(logging.INFO)

t = Thing(Xform.encode("I'M THE CASH REGISTER"))
t2 = t
q = 0
state = "begin"
new_desc = ""
guess_list = t2.get_nodes()


def lambda_handler(event, context):
    if event['request']['type'] == "IntentRequest":
        return speaking_to_me(event['request']['intent'])
    if event['request']['type'] == "LaunchRequest":
        return just_launched()
    if event['request']['type'] == "SessionEndedRequest":
        return session_ended()


def speaking_to_me(intent):
    # these are handled the same no matter the state
    global state
    if intent['name'] == "AMAZON.CancelIntent" or intent['name'] == "AMAZON.StopIntent":
        return end_game()
    if intent['name'] == "AMAZON.HelpIntent":
        return say_help()

    # handle what was said depending on where we are in the game
    logger.info("entering with state: " + state)
    if state == "begin":
        return first_words(intent)
    if state == "ask":
        return handle_question_response(intent)
    if state == "more":
        return handle_describe_response(intent)
    if state == "what":
        return handle_reveal_response(intent)
    if state == "guess":
        return handle_guess_response(intent)

    # we are hopelessly lost, better just start over!
    return starting_over()


def first_words(intent):
    """ Initial utterance handled here.  Only READY valid here."""
    global state, t, t2, q, guess_list
    if intent['name'] == "ReadyIntent":
        state = "ask"
        t2 = t
        guess_list = t2.get_nodes()
        q = 0
        return ask_question()
    session_attributes = {}
    card_title = "Guessing"
    speech_output = "say ready to begin or cancel to end"
    reprompt_text = "Please answer YES or NO"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def ask_question():
    global t2, q, state
    state = "ask"
    session_attributes = {}
    card_title = "Asking"
    try:
        guess_text = get_guess()
        logger.info("trying to find next thing " + guess_text)
        logger.info("asking: " + Xform.decode(guess_text))
        speech_output = Xform.decode(guess_text)
        reprompt_text = "Please answer YES or NO"
        should_end_session = False
        return build_response(session_attributes, build_speechlet_response(
            card_title, speech_output, reprompt_text, should_end_session))
    except IndexError:
        return make_guess()


def get_guess():
    global t2, q, guess_list
    # txt = list(t2.things.keys())[q]
    txt = guess_list[q]
    return txt


def drill_down():
    global t2, q, guess_list
    key = guess_list[q]
    t2 = t2.things[key]
    guess_list = t2.get_nodes()
    q = 0


def next_node():
    global q
    q = q + 1


def handle_question_response(intent):
    """ They have replied to a question.  Should be YES or NO."""
    global t2, q
    if intent['name'] == "AMAZON.YesIntent":
        drill_down()
        return ask_question()
    if intent['name'] == "AMAZON.NoIntent":
        next_node()
        return ask_question()
    return yes_or_no_please()


def make_guess():
    global t2, state
    logger.info("Making guess " + t2.guess)
    state = "guess"
    session_attributes = {}
    card_title = "Guessing"
    speech_output = "I give up, " + t2.get_guess()
    logger.info(speech_output)
    reprompt_text = "Please answer YES or NO"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_describe_response(intent):
    """ I've asked them to tell me something about themselves."""
    if intent['name'] == "DescribePersonIntent":
        return described_thing(intent)
    if intent['name'] == "DescribeThingIntent":
        return described_thing(intent)


def described_thing(intent):
    global state, new_desc
    session_attributes = {}
    card_title = "Describe"
    new_desc = encode_description(intent)
    logger.info("description: " + new_desc)
    state = "what"
    speech_output = "OK, so tell me what you are"
    reprompt_text = "Please tell what you are"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def encode_description(intent):
    if intent['name'] == "DescribePersonIntent":
        return person_description(intent)
    if intent['name'] == "DescribeThingIntent":
        return thing_description(intent)
    return "B01" + "unknown thing"


def person_description(intent):
    txt = "I AM " + intent['slots']['PersonDescription']['value'].upper()
    txt = Xform.encode(txt)
    return txt


def thing_description(intent):
    txt = "I " + intent['slots']['ThingDescription']['value'].upper()
    txt = Xform.encode(txt)
    return txt


def handle_reveal_response(intent):
    """ I've asked the to tell me what they are."""
    global t2, q, state, new_desc
    session_attributes = {}
    card_title = "Reveal"
    new_guess = encode_description(intent)
    logger.info("creating new thing: q: " + str(q) + " newg: " + new_guess + " newd: " + new_desc)
    new_thing = Thing(new_guess)
    t2.things[new_desc] = new_thing
    state = "begin"
    speech_output = "Interesting, I guess I've learned something. " \
                    "Say READY to play again"
    reprompt_text = "Say READY to begin or CANCEL to end"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_guess_response(intent):
    """ I've made a guess at what they are.  Should be YES or NO."""
    if intent['name'] == "AMAZON.YesIntent":
        return i_thought_so()
    if intent['name'] == "AMAZON.NoIntent":
        return tell_me_more()
    return yes_or_no_please()


def starting_over():
    """ Somehow we've lost track of the game state.  Bail out and start over."""
    pass


def tell_me_more():
    global state
    session_attributes = {}
    card_title = "Tell me more"
    state = "more"
    speech_output = "To help me learn, please tell me something about yourself."
    reprompt_text = "Please tell me something about yourself."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def end_game():
    """ Ending game.  Say Good-bye"""
    global t, t2, q, state, new_desc
    card_title = "Good-bye!"
    speech_output = "Thank you for playing Piedmont Things. " \
                    "Have a nice day! "
    t = Thing(Xform.encode("I'M THE CASH REGISTER"))
    t2 = t
    q = 0
    state = "begin"
    new_desc = ""
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))


def say_help():
    """ They've requested help.  Give it to them"""
    session_attributes = {}
    card_title = "Help"
    speech_output = "I will try to guess what you are by asking" \
                    " you a series of yes or no questions." \
                    " When I have run out of questions, I will make a guess" \
                    " at what you are,  If I am wrong, I will ask you to tell" \
                    " me something about yourself, so I can learn"
    reprompt_text = "Say READY to begin or CANCEL to end"
    should_end_session = False

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def i_thought_so():
    global state
    session_attributes = {}
    card_title = "Got it!"
    speech_output = "I thought so!  Pretty smart don't you think? " \
                    "Say READY to play again"
    reprompt_text = "Say READY to play again or CANCEL to end"
    state = "begin"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def yes_or_no_please():
    session_attributes = {}
    card_title = "Yes or No"
    speech_output = "Please answer YES or NO"
    reprompt_text = "Please answer YES or NO"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def just_launched():
    """ Launched app without utterance """
    global state
    state = "begin"

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to the Piedmont Things Alexa application. " \
                    "Think of yourself as a thing, " \
                    "and I will try to guess WHAT you are. " \
                    "When you are ready to begin, say READY"
    # speech_output = "Hello, say READY to begin"
    reprompt_text = "Say READY to begin or CANCEL to end"
    should_end_session = False

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def session_ended():
    pass


def build_speechlet_response(title, output, reprompt_text, should_end_session):

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
    response = {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }

    return response
