from stravalib.client import Client
import boto3
from boto3.dynamodb.conditions import Key
from slackclient import SlackClient
import json
import re
import os
import csv

with open('config.json') as data_file:
    config = json.load(data_file)
    for key, value in config.iteritems():
        if(os.environ.has_key(key)):
            if(type(value) is int):
                config[key] = os.environ[key]
            if(type(value) is list):
                config[key] = list(csv.reader(os.environ[key]))
            else:
                config[key] = os.environ[key]

dynamodbTable = boto3.resource('dynamodb').Table(config["dynamodb_table"])
token = config["slack_token"]
sc = SlackClient(token)


def get_new_rides_for_club():
    client = Client()
    client.access_token=config["strava_access_token"]
    rides=client.get_club_activities(club_id=config["strava_club_id"],limit=config["strava_ride_limit"])
    return rides


def filter_rides(rides):
    min_distance=config["min_distance"]
    blacklist=config["blacklist"]
    whitelist = config["whitelist"]
    blacklistridenames = config["blacklistridenames"]
    blregex = "^Zwift"
    filtered_rides=[]
    for ride in rides:
        if (
            (
            (ride.distance._num>min_distance)
            and
            ((ride.athlete.firstname+" "+ride.athlete.lastname) not in blacklist)
            and
            (ride.athlete.lastname not in blacklist)
            and
            (ride.athlete.id not in blacklist)
            and
            (ride.name not in blacklistridenames)
            and
            (re.match(blregex,ride.name) is None))
            or ride.athlete.lastname in whitelist): 
                filtered_rides.append(ride)
    return filtered_rides

    
def slack_ride(ride):
    msg='<https://www.strava.com/activities/'+str(ride.id)+'|'+ride.athlete.firstname+' '+ride.athlete.lastname+': '+ride.name+'>';
    sc.api_call("chat.postMessage",
                channel=config["slack_channel"],
                text=msg,
                username=config["slack_username"],
                icon_emoji=config["slack_icon_emoji"],
                unfurl_links=True,
                unfurl_media=True)
    return

    
def is_new_ride(ride):
        # lookup ride in dynamo
        response = dynamodbTable.query(
            KeyConditionExpression = Key('lastname').eq(ride.athlete.lastname) & Key('title').eq(ride.name+str(ride.id))
        )
        items = response['Items']
        if len(items)==0:
            return True
        else:
            return False


def record_ride(ride):
    #save ride to dynamo
    response = dynamodbTable.put_item(
        Item={
            "lastname": ride.athlete.lastname,
            "title": (ride.name+str(ride.id))
        }
    )
    return

    
def has_not_ridden():
    #determines who has been slacking
    response = dynamodbTable.query(
            KeyConditionExpression = Key('lastname').eq(ride.athlete.lastname)
        )
    return

