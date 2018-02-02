import re
import json
import boto3
import logging
from random import randint


class Thing(object):

    def __init__(self, guess):
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


class NewThing(object):

    def __init__(self, guess):
        self.guess = guess.upper()
        self.things = []

    def get_guess(self):
        return Xform.guess_decode(self.guess)

    def add_thing(self, new_thing):
        self.things.append(new_thing)
        pass

    def get_nodes(self):
        return self.things


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
root = NewThing(Xform.encode("I'M THE CASH REGISTER"))
t2 = t
x2 = root
q = 0
z = 0
state = "begin"
new_desc = ""
guess_list = t2.get_nodes()
new_list = x2.get_nodes()
end_pnt = len(guess_list)
new_pnt = len(new_list)
reprompt_text = "SAY READY TO BEGIN OR CANCEL TO END"
table = ""


def show_new():
    global table, root, x2, z, new_list, new_pnt

    print("ROOT GUESS:" + root.guess + " ROOT THINGS: " + str(root.things))
    print("X2 GUESS:" + x2.guess + " X2 THINGS: " + str(x2.things))
    print("NEW_LIST: " + str(new_list))
    print("NEW_PNT: " + str(new_pnt))


def main():
    show_new()
    print("++++++++++++++++++++++++++++++++++")
    just_launched()
    intent = {'name': "ReadyIntent"}
    speaking_to_me(intent)
    intent['name'] = "AMAZON.YesIntent"
    speaking_to_me(intent)
    intent = {'name': "ReadyIntent"}
    speaking_to_me(intent)
    intent['name'] = "AMAZON.NoIntent"
    speaking_to_me(intent)

    intent = {'name': "DescribePersonIntent", 'slots': {'PersonDescription': {'value': "made of plastic"}}}  # i am
    speaking_to_me(intent)
    intent = {'name': "DescribePersonIntent", 'slots': {'PersonDescription': {'value': "an ashtray"}}}  # i am
    speaking_to_me(intent)

    intent = {'name': "ReadyIntent"}  # will ask new info (made of plastic)
    speaking_to_me(intent)
    intent['name'] = "AMAZON.YesIntent"
    speaking_to_me(intent)
    intent['name'] = "AMAZON.YesIntent"
    speaking_to_me(intent)

    # intent = {'name': "DescribeThingIntent"}   # i
    # intent['slots']['ThingDescription']['value'] = "have a big nose"

    print("++++++++++++++++++++++++++++++++++")
    show_new()
    exit(1)

    db = boto3.resource('dynamodb', endpoint_url="http://localhost:8000")
    print("db: " + str(db))

    create_table(db)
    root = create_root()
    print("root: " + json.dumps(root))

    print("Table status:", table.table_status)

    desc = "i'm made of paper"
    guess = "are you a napkin"
    things = []
    t1 = new_thing(root, desc, guess, things)
    print("t1: " + json.dumps(t1))
    print("root: " + json.dumps(root))

    desc = "i'm made of plastic"
    guess = "are you an ashtray"
    things = []
    t2 = new_thing(root, desc, guess, things)
    print("t2: " + json.dumps(t2))
    print("root: " + json.dumps(root))

    desc = "i have a big nose"
    guess = "are you kevin"
    things = []
    t3 = new_thing(root, desc, guess, things)
    print("t3: " + json.dumps(t3))
    print("root: " + json.dumps(root))


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
    if state == "about":
        return handle_describe_response(intent)
    if state == "what":
        return handle_reveal_response(intent)
    if state == "guess":
        return handle_guess_response(intent)

    # we are hopelessly lost, better just start over!
    return starting_over()


def new_node(thing):
    global guess_list, end_pnt
    guess_list = thing.get_nodes()
    end_pnt = len(guess_list)


def start_new_node_x(thing):
    global new_list, new_pnt, new_guess
    new_list = x2.get_nodes()
    new_pnt = len(new_list)


def first_words(intent):
    """ Initial utterance handled here.  Only READY valid here."""
    global state, t, t2, q, guess_list, end_pnt, reprompt_text, root, x2
    if intent['name'] == "ReadyIntent":
        state = "ask"
        t2 = t
        new_node(t2)
        x2 = root
        start_new_node_x(x2)
        next_question_x()
        return next_question()
    session_attributes = {}
    card_title = "Guessing"
    speech_output = "say ready to begin or cancel to end"
    # reprompt_text = "Please answer YES or NO"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def next_question():
    global t2, q, state, reprompt_text
    state = "ask"
    session_attributes = {}
    card_title = "Asking"
    try:
        guess_text = get_guess()
        logger.info("trying to find next thing " + guess_text)
        logger.info("asking: " + Xform.decode(guess_text))
        speech_output = Xform.decode(guess_text)
        reprompt_text = "Please answer YES or NO, " + speech_output
        should_end_session = False
        return build_response(session_attributes, build_speechlet_response(
            card_title, speech_output, reprompt_text, should_end_session))
    except IndexError:
        return make_guess()


def get_guess():
    global t2, q, guess_list, end_pnt
    # txt = list(t2.things.keys())[q]
    end_pnt = end_pnt - 1
    if end_pnt < 0:
        raise IndexError('No more guesses')
    q = randint(0, end_pnt)
    txt = guess_list[q]  # should be random out of guess_list between 0 and end_pnt
    guess_list[q] = guess_list[end_pnt]
    return txt


def next_question_x():
    global x2, q, state, reprompt_text
    state = "ask"
    session_attributes = {}
    card_title = "Asking"
    print("ASKING NEXT QUESTION X: " + str(z))
    try:
        guess_text = get_guess_x()
        print("NEXT GUESS X " + guess_text)
        print("ASKING X: " + Xform.decode(guess_text))
        speech_output = Xform.decode(guess_text)
        reprompt_text = "Please answer YES or NO, " + speech_output
        should_end_session = False
        # return build_response(session_attributes, build_speechlet_response(
        #     card_title, speech_output, reprompt_text, should_end_session))
    except IndexError:
        print("CAUGHT X: ")
        make_guess_x()

    return


def get_guess_x():
    global x2, z, new_list, new_pnt
    # txt = list(t2.things.keys())[q]
    new_pnt = new_pnt - 1
    print("GETTING GUESS X: " + str(new_pnt))
    if new_pnt < 0:
        print("RAISING X: ")
        raise IndexError('No more guesses')
    z = randint(0, new_pnt)
    txt = new_list[z]  # should be random out of guess_list between 0 and end_pnt
    new_list[z] = new_list[new_pnt]
    return txt


def make_guess_x():
    global x2, state, reprompt_text
    print("MAKING GUESS X: " + x2.guess)
    state = "guess"
    session_attributes = {}
    card_title = "Guessing"
    speech_output = "I give up, " + x2.get_guess()
    logger.info("X2: " + speech_output)
    reprompt_text = "Please answer YES or NO, " + x2.get_guess()  # i want yes/no here
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def drill_down():
    global t2, q, guess_list, end_pnt
    key = guess_list[q]
    t2 = t2.things[key]
    new_node(t2)


def drill_down_x():
    global x2, z, new_list, new_pnt, new_desc
    print("DRILLING DOWN TO X: " + new_desc)
    key = new_list[z]
    #    x2 = x2.things[z]   # go to database to thing
    start_new_node_x(new_desc)


def handle_question_response(intent):
    """ They have replied to a question.  Should be YES or NO."""
    global t2, q
    if intent['name'] == "AMAZON.YesIntent":
        drill_down_x()
        drill_down()
        return next_question()
    if intent['name'] == "AMAZON.NoIntent":
        next_question_x()
        return next_question()
    return yes_or_no_please()


def make_guess():
    global t2, state, reprompt_text
    logger.info("Making guess " + t2.guess)
    state = "guess"
    session_attributes = {}
    card_title = "Guessing"
    speech_output = "I give up, " + t2.get_guess()
    logger.info(speech_output)
    reprompt_text = "Please answer YES or NO, " + t2.get_guess()  # i want yes/no here
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_describe_response(intent):
    """ I've asked them to tell me something about themselves."""
    if intent['name'] == "DescribePersonIntent":
        return described_thing(intent)
    if intent['name'] == "DescribeThingIntent":
        return described_thing(intent)
    session_attributes = {}
    card_title = "Tell me more"
    speech_output = reprompt_text
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def described_thing(intent):
    global state, new_desc, reprompt_text
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
    global t2, q, state, new_desc, reprompt_text

    handle_reveal_response_x(intent)

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


def handle_reveal_response_x(intent):
    """ I've asked the to tell me what they are."""
    global x2, z, state, new_desc, reprompt_text
    session_attributes = {}
    card_title = "Reveal"
    new_guess = encode_description(intent)
    print("CREATING NEW THING X: z: " + str(z) + " newg: " + new_guess + " newd: " + new_desc)
    new_thing = NewThing(new_guess)
    x2.things.append(new_desc)  # store in database here (not in x2 thing)
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
        return tell_me_about()
    return yes_or_no_please()


def starting_over():
    """ Somehow we've lost track of the game state.  Bail out and start over."""
    pass


def tell_me_about():
    global state, reprompt_text
    print("ASKING FOR MORE X")
    session_attributes = {}
    card_title = "Tell me more"
    state = "about"
    speech_output = "To help me learn, please tell me something about yourself."
    reprompt_text = "Please tell me something about yourself."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def end_game():
    """ Ending game.  Say Good-bye"""
    global t, t2, q, state, new_desc, root, x2, z
    card_title = "Good-bye!"
    speech_output = "Thank you for playing Piedmont Things. " \
                    "Have a nice day! "
    t = Thing(Xform.encode("I'M THE CASH REGISTER"))
    root = NewThing(Xform.encode("I'M THE CASH REGISTER"))
    t2 = t
    x2 = root
    q = 0
    z = 0
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
    should_end_session = False

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def i_thought_so():
    global state, reprompt_text
    print("GUESSED IT X")
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
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def just_launched():
    """ Launched app without utterance """
    global state, reprompt_text
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


def build_speechlet_response(title, output, passed_reprompt, should_end_session):
    global reprompt_text

    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        # 'card': {
        #     'type': 'Simple',
        #     'title': 'SessionSpeechlet - ' + title,
        #     'content': 'SessionSpeechlet - ' + output
        # },
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


def get_table():
    global table
    try:
        db = boto3.resource('dynamodb')
        table = db.Table('things')
    except:
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
            logger.info("unable to connect to dynamodb")


def create_table(db):
    global table
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
    global table
    response = table.put_item(
        Item={
            'id': "root",
            'guess': "are you the bartender",
            'things': []
        }
    )
    response = table.get_item(
        Key={
            'id': "root"
        }
    )
    item = response['Item']
    return item


def new_thing(thing, desc, guess, things):
    new_thing = create_thing(desc, guess, things)
    thing["things"].append(desc)
    update_thing(thing)
    return new_thing


def update_thing(thing):
    global table
    response = table.update_item(
        Key={
            'id': thing["id"]
        },
        UpdateExpression="set guess=:g, things=:t",
        ExpressionAttributeValues={
            ':g': thing["guess"],
            ':t': thing["things"]
        },
        ReturnValues="UPDATED_NEW"
    )

    response = table.get_item(
        Key={
            'id': thing["id"]
        }
    )
    item = response['Item']
    return item


def create_thing(desc, guess, things):
    global table
    response = table.put_item(
        Item={
            'id': desc,
            'guess': guess,
            'things': things
        }
    )
    response = table.get_item(
        Key={
            'id': desc
        }
    )
    item = response['Item']
    return item


def get_thing(desc):
    global table
    response = table.get_item(
        Key={
            'id': desc
        }
    )
    item = response['Item']
    return item


if __name__ == "__main__":
    # execute only if run as a script
    main()
