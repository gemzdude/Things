import re
import sys
import json
import urllib.request
from pprint import pprint
import datetime
import os
import pytz
from pytz import timezone
from pprint import pprint, pformat
import boto3
import logging
from random import randint


class Thing(object):

    def __init__(self, guess):
        self.guess = ""
        self.things = {}
        self.guess = guess.upper()

    def get_nodes(self):
        return list(self.things)


class Xform:
    encodes = {
        "I'M ": "A01",
        "I AM ": "A01",
        "I ": "B01",
        "MY ": "C01"
    }

    decodes = {
        "A01": "ARE YOU ",
        "B01": "DO YOU ",
        "C01": "M01 YOUR "
    }

    encodes_context = {
        "I'M": "X01",
        "I AM": "X02",
        " I ": "X03",
        " ME ": "X04",
        " ARE ": "Y01",
        " IS ": "Y02"
    }

    decodes_context = {
        "X01": "YOU'RE",
        "X02": "YOU ARE",
        "X03": " YOU ",
        "X04": " YOU ",
        "Y01": " ",
        "Y02": " "
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
        encode_txt = Xform.context_encode(encode_txt)
        encode_txt.replace(" ", "_")
        return encode_txt

    @staticmethod
    def decode(txt):
        decode_txt = Xform.xform(txt, Xform.decodes)
        if re.match("M01 ", decode_txt):
            if decode_txt.count("Y01"):
                decode_txt = decode_txt.replace("M01 ", "ARE ")
            if decode_txt.count("Y02"):
                decode_txt = decode_txt.replace("M01 ", "IS ")
        decode_txt = Xform.context_decode(decode_txt)
        decode_txt.replace("_", " ")
        return decode_txt

    @staticmethod
    def context_encode(txt):
        encode_txt = txt
        for eFrom, eTo in Xform.encodes_context.items():
            encode_txt = encode_txt.replace(eFrom, eTo)
        return encode_txt

    @staticmethod
    def context_decode(txt):
        decode_txt = txt
        for dFrom, dTo in Xform.decodes_context.items():
            decode_txt = decode_txt.replace(dFrom, dTo)
        return decode_txt

    @staticmethod
    def form_question(txt):
        return Xform.decode(Xform.encode(txt))

logLevel = logging.CRITICAL
myLevel = logging.CRITICAL  # set to INFO to just see my stuff
logger = logging.getLogger()
logger.setLevel(logLevel)
sj = logging.StreamHandler(sys.stdout)
sj.setLevel(myLevel)
logger.addHandler(sj)

state = "begin"
new_desc = ""
guess_list = ""
end_pnt = len(guess_list)
reprompt_text = "SAY READY TO BEGIN OR CANCEL TO END"
db = ""
table = ""
key = ""
long_key = ""
thing = ""  # dyno version of t2


def main():
    global db, table, thing
    db = boto3.resource('dynamodb', endpoint_url="http://localhost:8000")
    logger.info("db: " + str(db))

    create_table()
    root = get_root()

    logger.info("Table status:" + table.table_status)

    # desc = "I'M MADE OF PLASTIC"
    # guess = "ARE YOU AN ASHTRAY"
    # things = []
    # t2 = new_thing(root, desc, guess, things)
    # logger.info("root: " + json.dumps(root))
    #
    # desc = "I'M KNOWN AS THE BEER WHISPERER"
    # guess = "ARE YOU KEVIN"
    # things = []
    # t3 = new_thing(root, desc, guess, things)
    # logger.info("root: " + json.dumps(root))

    # logger.info("==== Before dump ====")
    # dump_table()
    # logger.info("==== Past dump ====")
    #
    # thing = root
    # start_node(thing)
    # logger.info("GUESS_LIST: " + str(guess_list))
    # logger.info("END_PNT: " + str(end_pnt))

    # logger.info("GUESS[0]: " + guess_list[0])
    # logger.info("GUESS[1]: " + guess_list[1])
    # logger.info("GUESS[2]: " + guess_list[2])
    # while(True):
    #     try:
    #         logger.info(form_question())
    #     except IndexError:
    #         logger.info("Out of guesses")
    #         break
# ===========================================
    intent = {'name': "Larry_Intent"}
    resp = handle_larrybus()
    print(get_speech(resp))
#
#     intent['name'] = 'AMAZON.YesIntent'
#     # resp = handle_question_response(intent)
#     resp = speaking_to_me(intent)
#     logger.info(get_speech(resp))
#
#     intent['name'] = 'AMAZON.YesIntent'
#     resp = speaking_to_me(intent)
#     logger.info(get_speech(resp))
#     logger.info("# ===========================================")
#     intent = {'name': "ReadyIntent"}
#     # resp = first_words(intent)
#     resp = speaking_to_me(intent)
#     logger.info(get_speech(resp))
#
#     intent['name'] = 'AMAZON.NoIntent'
#     resp = speaking_to_me(intent)
#     logger.info(get_speech(resp))
#
#     intent['name'] = 'AMAZON.NoIntent'
#     resp = speaking_to_me(intent)
#     logger.info(get_speech(resp))
#
#     intent['name'] = 'AMAZON.YesIntent'
#     resp = speaking_to_me(intent)
#     logger.info(get_speech(resp))
#
#     intent['name'] = 'AMAZON.YesIntent'
#     resp = speaking_to_me(intent)
#     logger.info(get_speech(resp))
# =============================================
#     intent = {'name': "ReadyIntent"}
#     resp = speaking_to_me(intent)
#     logger.info(get_speech(resp))
#
#     intent['name'] = 'AMAZON.YesIntent'
#     # resp = handle_question_response(intent)
#     resp = speaking_to_me(intent)
#     logger.info(get_speech(resp))
#
#     intent['name'] = 'AMAZON.NoIntent'
#     resp = speaking_to_me(intent)
#     logger.info(get_speech(resp))
#
#     # if intent['name'] == "I_am_Intent":   # I AM
#     # if intent['name'] == "I_Intent":    # I
#     # txt = "I AM " + intent['slots']['I_am_Description']['value'].upper()
#     # txt = "I " + intent['slots']['I_Description']['value'].upper()
#
#     # build describe intent x2 for tell me more, tell me what
#
#     # intent['name'] == "DescribePersonIntent"
#     intent = {'name': "I_am_Intent", 'slots': {'I_am_Description': {'value': "I AM RED"}}}
#     resp = speaking_to_me(intent)
#     logger.info(get_speech(resp))
#
#     # intent['name'] == "DescribePersonIntent"
#     intent = {'name': "I_am_Intent", 'slots': {'I_am_Description': {'value': "ARE YOU A STRAW"}}}
#     resp = speaking_to_me(intent)
#     logger.info(get_speech(resp))
#     logger.info("# ===========================================")
#
#     intent = {'name': "ReadyIntent"}
#     resp = speaking_to_me(intent)
#     logger.info(get_speech(resp))
#
#     intent['name'] = 'AMAZON.YesIntent'
#     resp = speaking_to_me(intent)
#     logger.info(get_speech(resp))
#
#     intent['name'] = 'AMAZON.YesIntent'
#     resp = speaking_to_me(intent)
#     logger.info(get_speech(resp))
#
#     intent['name'] = 'AMAZON.NoIntent'
#     resp = speaking_to_me(intent)
#     logger.info(get_speech(resp))
    # intent['name'] = 'AMAZON.YesIntent'
    # resp = speaking_to_me(intent)
    # logger.info(get_speech(resp))
    #
    # intent['name'] = 'AMAZON.NoIntent'
    # resp = speaking_to_me(intent)
    # logger.info(get_speech(resp))

    # intent['name'] = 'AMAZON.YesIntent'
    # resp = speaking_to_me(intent)
    # logger.info(get_speech(resp))
# ===========================================
#     logger.info("==== Before dump ====")
#     dump_table()
#     logger.info("==== Past dump ====")
    # except:
    #     logger.info(sys.exc_info())
    #     logger.info(sys.exc_info()[0])
    #     logger.info(sys.exc_info()[1])
    #     logger.info(sys.exc_info()[2])


def get_speech(resp):
    return "SPEECH IS: " + resp['response']['outputSpeech']['ssml']


def dump_table():
    global table
    try:
        response = table.scan()
        logger.info(pformat(response))
        # for i in response['Items']:
        #     logger.info("ID: " + i['id'], "  GUESS:", i['guess'] + "  THINGS: " + str(i['things']))
    except:
        logger.info("DUMP ERROR: " + sys.exc_info()[0])


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
    logger.info("INTENT_NAME: " + intent['name'])
    if intent['name'] == "AMAZON.CancelIntent" or intent['name'] == "AMAZON.StopIntent":
        return end_game()
    if intent['name'] == "AMAZON.HelpIntent":
        return say_help()
    if intent['name'] == "Larry_Intent":
        return handle_larrybus()

    # handle what was said depending on where we are in the game
    logger.info("entering with state: " + state)
    if state == "begin":
        return first_words(intent)
    if state == "ask":
        return handle_question_response(intent)
    if state == "about":
        return handle_describe_response(intent)
    if state == "what":
        return handle_reveal_response(intent)
    if state == "guess":
        return handle_guess_response(intent)

    # we are hopelessly lost, better just start over!
    return start_game()


def first_words(intent):
    """ Initial utterance handled here.  Only READY valid here."""
    global state, db, thing, guess_list, end_pnt, reprompt_text, long_key
    logger.info(pformat(intent))
    if intent['name'] == "ReadyIntent":
        state = "ask"
        if db == "":
            db = boto3.resource('dynamodb')
            table = db.Table('things')
        thing = get_root()
        start_node(thing)
        long_key = ""
        return next_question()
    session_attributes = {}
    speech_output = "say ready to begin or cancel to end"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        speech_output, should_end_session))


def next_question():
    try:
        guess_text = get_guess()
        return ask_question("", guess_text)
    except IndexError:
        return make_guess()


def ask_question(prolog_speech, question):
    global thing, state, reprompt_text
    state = "ask"
    session_attributes = {}
    logger.info("next_question trying to find next thing " + question)
    speech_output = prolog_speech + ", " + Xform.form_question(question)
    reprompt_text = "Please answer YES or NO, " + speech_output
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        speech_output, should_end_session))


def get_guess():
    global key, guess_list, end_pnt
    end_pnt = end_pnt - 1
    if end_pnt < 0:
        raise IndexError('No more guesses')
    logger.info("GET_GUESS GUESS_LIST: " + str(guess_list))
    logger.info("GET_GUESS END_PNT: " + str(end_pnt))
    q = randint(0, end_pnt)
    key = guess_list[q]  # should be random out of guess_list between 0 and end_pnt
    guess_list[q] = guess_list[end_pnt]
    return key


def drill_down():
    global thing, key, long_key
    long_key = long_key + key
    logger.info("DRILL_DOWN LONG_KEY: " + long_key)
    thing = get_thing(long_key)
    start_node(thing)


def handle_question_response(intent):
    """ They have replied to a question.  Should be YES or NO."""
    if intent['name'] == "AMAZON.YesIntent":
        drill_down()
        return next_question()
    if intent['name'] == "AMAZON.NoIntent":
        return next_question()
    return yes_or_no_please()


def make_guess():
    global thing, state, reprompt_text
    logger.info("MAKE_GUESS GUESS: " + thing['guess'])
    state = "guess"
    session_attributes = {}
    # txt = Xform.form_question(thing['guess'])
    txt = "ARE YOU " + thing['guess']
    speech_output = "I'll take a guess, " + txt + "?"
    reprompt_text = "Please answer YES or NO, " + txt  # i want yes/no here
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        speech_output, should_end_session))


def handle_describe_response(intent):
    """ I've asked them to tell me something about themselves."""
    global state, new_desc, reprompt_text
    session_attributes = {}
    new_desc = reform_utterance(intent)
    if new_desc in thing['things']:
        return ask_question("I think I've already asked you that", new_desc)
    logger.info("ABOUT DESCRIPTION: " + new_desc)
    state = "what"
    speech_output = "OK, so tell me what you are"
    reprompt_text = "Please tell what you are"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        speech_output, should_end_session))


def reform_utterance(intent):
    if intent['name'] == "I_am_Intent":
        txt = "I AM " + intent['slots']['I_am_Description']['value'].upper() + " "
        return txt
    if intent['name'] == "I_Intent":
        txt = "I " + intent['slots']['I_Description']['value'].upper() + " "
        return txt
    if intent['name'] == "My_Intent":
        txt = "MY " + intent['slots']['My_Description']['value'].upper() + " "
        return txt
    logger.info("UNKNOWN INTENT!")
    logger.info(pformat(intent))
    return "I AM " + "AN UNKNOWN THING"


def handle_reveal_response(intent):
    """ I've asked the to tell me what they are."""
    global thing, state, new_desc, reprompt_text
    session_attributes = {}
    # new_guess = reform_utterance(intent)
    new_guess = intent['slots']['I_am_Description']['value'].upper() + " "
    logger.info("REVEAL GUESS: " + new_guess)

    thing = new_thing(thing, new_desc, new_guess, [])

    state = "begin"
    speech_output = "Interesting, I guess I've learned something. " \
                    "Say READY to play again"
    reprompt_text = "Say READY to begin or CANCEL to end"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        speech_output, should_end_session))


def handle_guess_response(intent):
    """ I've made a guess at what they are.  Should be YES or NO."""
    if intent['name'] == "AMAZON.YesIntent":
        return i_thought_so()
    if intent['name'] == "AMAZON.NoIntent":
        return tell_me_about()
    return yes_or_no_please()


def tell_me_about():
    global state, reprompt_text
    session_attributes = {}
    state = "about"
    speech_output = "To help me learn, please tell me something about yourself."
    reprompt_text = "Please tell me something about yourself."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        speech_output, should_end_session))


def end_game():
    """ Ending game.  Say Good-bye"""
    global state, new_desc
    speech_output = "Thank you for playing Piedmont Things. " \
                    "Have a nice day! "
    state = "begin"
    new_desc = ""
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        speech_output, should_end_session))


def say_help():
    """ They've requested help.  Give it to them"""
    session_attributes = {}
    speech_output = "I will try to guess what you are by asking" \
                    " you a series of yes or no questions." \
                    " When I have run out of questions, I will make a guess" \
                    " at what you are,  If I am wrong, I will ask you to tell" \
                    " me something about yourself, so I can learn"
    should_end_session = False

    return build_response(session_attributes, build_speechlet_response(
        speech_output, should_end_session))


def i_thought_so():
    global state, reprompt_text
    session_attributes = {}
    speech_output = "I thought so!  Pretty smart don't you think? " \
                    "Say READY to play again"
    reprompt_text = "Say READY to play again or CANCEL to end"
    state = "begin"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        speech_output, should_end_session))


def yes_or_no_please():
    session_attributes = {}
    speech_output = "Please answer YES or NO"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        speech_output, should_end_session))


def just_launched():
    """ Launched app without utterance """
    global db, table
    db = boto3.resource('dynamodb')
    table = db.Table('things')
    logger.info("db: " + str(db))
    logger.info("Table status:" + str(table.table_status))
    return start_game()


def start_game():
    global state, reprompt_text, table, thing
    state = "begin"
    thing = get_root()
    session_attributes = {}
    speech_output = "Welcome to the Piedmont Things Alexa application. " \
                    "Think of yourself as a thing, " \
                    "and I will try to guess what you are. " \
                    "When you are ready to begin, say READY"
    # speech_output = "Hello, say READY to begin"
    reprompt_text = "Say READY to begin or CANCEL to end"
    should_end_session = False

    return build_response(session_attributes, build_speechlet_response(
        speech_output, should_end_session))


def session_ended():
    pass


def start_node(existing_thing):
    global guess_list, end_pnt
    guess_list = existing_thing['things']
    end_pnt = len(guess_list)


def build_speechlet_response(output, should_end_session):
    global reprompt_text

    return {
        "outputSpeech": {
            "type": "SSML",
            "ssml": "<speak>" + output + "</speak>"
        },
        # 'outputSpeech': {
        #     'type': 'PlainText',
        #     'text': output
        # },
        # 'card': {
        #     'type': 'Simple',
        #     'title': 'SessionSpeechlet - ' + title,
        #     'content': 'SessionSpeechlet - ' + output
        # },
        'reprompt': {
            'outputSpeech': {
                'type': 'SSML',
                'ssml': "<speak>" + reprompt_text + "</speak>"
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


def create_table():
    global db, table
    try:
        table = db.Table('things')
        table.delete()
    except:
        pass
    try:
        table = db.create_table(
            TableName='things',
            KeySchema=[
                {
                    'AttributeName': 'id',
                    'KeyType': 'HASH'  # Partition key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'id',
                    'AttributeType': 'S'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 1,
                'WriteCapacityUnits': 1
            }
        )
    except:
        table = db.Table('things')


def create_root():
    global db, table
    # db = boto3.resource('dynamodb')
    table = db.Table('things')
    try:
        response = table.put_item(
            Item={
                'id': "ROOT",
                'guess': "THE BAR TENDER",
                'things': []
            }
        )
    except:
        logger.info("CREATE OF ROOT FAILED.  MAY ALREADY EXIST." + str(sys.exc_info()[0]))

    item = get_root()
    return item


def get_root():
    global table
    # db = boto3.resource('dynamodb')
    table = db.Table('things')
    try:
        response = table.get_item(
            Key={
                'id': "ROOT"
            }
        )
        item = response['Item']
    except:
        item = create_root()

    return item


def new_thing(existing_thing, desc, guess, things):
    global long_key
    long_key = long_key + desc
    created_thing = create_thing(long_key, guess, things)
    existing_thing["things"].append(desc)
    update_thing(existing_thing)
    return created_thing


def update_thing(existing_thing):
    global table
    logger.info("UPDATE_THING LONG_KEY: " + existing_thing['id'] + " GUESS: " + existing_thing['guess'] + " THINGS: " + str(existing_thing['things']))
    response = table.update_item(
        Key={
            'id': existing_thing['id']
        },
        UpdateExpression="set guess=:g, things=:t",
        ExpressionAttributeValues={
            ':g': existing_thing['guess'],
            ':t': existing_thing['things']
        },
        ReturnValues="UPDATED_NEW"
    )

    response = table.get_item(
        Key={
            'id': existing_thing['id']
        }
    )
    item = response['Item']
    return item


def create_thing(id, guess, things):
    global table, long_key
    logger.info("CREATE_THING LONG_KEY: " + long_key + " GUESS: " + guess + " THINGS: " + str(things))
    response = table.put_item(
        Item={
            'id': long_key,
            'guess': guess,
            'things': things
        }
    )
    response = table.get_item(
        Key={
            'id': long_key
        }
    )
    item = response['Item']
    return item


def get_thing(id):
    global table
    logger.info("GET_THING ID: " + id)
    response = table.get_item(
        Key={
            'id': id
        }
    )
    item = response['Item']
    return item


def handle_larrybus():

    trimet = os.environ.get('TRIMET_APIKEY')
    trimet_url = "http://developer.trimet.org/ws/V2/arrivals"
    trimet_parms = "?json=true&appid=" + trimet + "&locIDs=93"
    session_attributes = {}
    should_end_session = False
    try:
        x = urllib.request.urlopen(trimet_url + trimet_parms)
        arr_info = json.loads(x.read())

        arr_list = arr_info["resultSet"]["arrival"]

        est, est_min, est_time, est_late, sch, sch_min, sch_time, sch_late = arrival_info(arr_list[0])
        if est is None:
            if sch is None:
                speech_output = "The buses are not running any more. "
            else:
                speech_output = "I don't have an estimate for the next bus, \
but it is scheduled to arrive in {0} minutes at ".format(sch_min) + sch_time + ". "
        else:
            if est_late:
                speech_output = "The bus should have been here {0} minutes ago at ".format(est_min) + est_time + ". "
            else:
                speech_output = "The next bus is due to arrive in {0} minutes at ".format(est_min) + est_time + ". "

        # print(arr_list[1])

        est, est_min, est_time, est_late, sch, sch_min, sch_time, sch_late = arrival_info(arr_list[1])
        if est is None:
            if sch is None:
                speech_output = speech_output + " I don't have any information for buses after that. "
            else:
                speech_output = speech_output + " I don't have an estimate for the bus after that, \
but it is scheduled to arrive in {0} minutes at ".format(sch_min) + sch_time + ". "
        else:
            speech_output = speech_output + "  The bus after that is due to arrive in {0} minutes at ".format(est_min) + est_time + ". "

        return build_response(session_attributes, build_speechlet_response(
            speech_output, should_end_session))
    except:
        logger.info("LARRY ERROR: " + sys.exc_info()[0])
        speech_output = "An error occurred attempting to contact Trimet."
        return build_response(session_attributes, build_speechlet_response(
            speech_output, should_end_session))


def arrival_info(arrival):

    try:
        est, est_min, est_time, est_late = time_info(arrival['estimated'])
    except KeyError:
        est = None
        est_min = None
        est_time = None
        est_late = None

    try:
        sch, sch_min, sch_time, sch_late = time_info(arrival['scheduled'])
    except KeyError:
        sch = None
        sch_min = None
        sch_time = None
        sch_late = None

    return est, est_min, est_time, est_late, sch, sch_min, sch_time, sch_late


def time_info(ticks):
    cur = datetime.datetime.now().astimezone(timezone('US/Pacific'))
    tim = datetime.datetime.fromtimestamp(ticks / 1000.0).astimezone(timezone('US/Pacific'))
    if tim > cur:
        tim_late = False
        diff = tim - cur
    else:
        tim_late = True
        diff = cur - tim
    tim_min, seconds = divmod(diff.seconds, 60)
    tim_hh = "{0:d}".format(int(tim.strftime("%I")))
    tim_mm = str(tim.strftime("%M"))
    tim_ampm = str(tim.strftime("%P"))
    tim_say = tim_hh + " " + tim_mm + " " + tim_ampm
    return tim, tim_min, tim_say, tim_late


if __name__ == "__main__":
    # execute only if run as a script
    main()
