import json
import boto3
import sys

table = ""

def main():
    global table
    db = boto3.resource('dynamodb', endpoint_url="http://localhost:8000")
    print("db: " + str(db))

    table = dyno_create_table(db)
    root = dyno_create_root()
    print("root: " + json.dumps(root))

    print("Table status:", table.table_status)

    desc = "i'm made of paper"
    guess = "are you a napkin"
    things = []
    t1 = dyno_new_thing(root, desc, guess, things)
    print("t1: " + json.dumps(t1))
    print("root: " + json.dumps(root))

    desc = "i'm made of plastic"
    guess = "are you an ashtray"
    things = []
    t2 = dyno_new_thing(root, desc, guess, things)
    print("t2: " + json.dumps(t2))
    print("root: " + json.dumps(root))

    desc = "i have a big nose"
    guess = "are you kevin"
    things = []
    t3 = dyno_new_thing(root, desc, guess, things)
    print("t3: " + json.dumps(t3))
    print("root: " + json.dumps(root))

    print("Before dump")
    dump_table()
    print("Past dump")

    # except:
    #     print(sys.exc_info())
    #     print(sys.exc_info()[0])
    #     print(sys.exc_info()[1])
    #     print(sys.exc_info()[2])


def dump_table():
    global table
    try:
        response = table.scan()
        #     KeyConditionExpression=Key('year').eq(1985)
        # )
        print("ITEMS: " + response['Items'])

        for i in response['Items']:
            print("ID: " + i['id'], "  GUESS:", i['guess'] + "  THINGS: " + i['things'])
    except:
        print("DUMP ERROR: " + sys.exc_info()[0])


def dyno_create_table(db):
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
                    'KeyType': 'HASH'  #Partition key
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
        return table
    except:
        table = db.Table('things')
        return table


def dyno_create_root():
    global table
    response = table.put_item(
        Item={
            'id': "root",
            'guess': "are you the cash register",
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


def dyno_new_thing(thing, desc, guess, things):
    new_thing = dyno_create_thing(desc, guess, things)
    thing["things"].append(desc)
    dyno_update_thing(thing)
    return new_thing


def dyno_update_thing(thing):
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


def dyno_create_thing(desc, guess, things):
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


def dyno_get_thing(desc):
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
