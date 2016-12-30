
import stravabot

def handler(event, context):
    print event
    print context
    # check strava for new rides
    # filter out rides already recorded in dynamodb
    # record rides in dynamodb
    # filter rides based on config criteria
    # send rides to slack
    
    rides = stravabot.get_new_rides_for_club()
    filteredrides = stravabot.filter_rides(rides)
    for ride in filteredrides:
        if stravabot.is_new_ride(ride):
            stravabot.record_ride(ride)
            stravabot.slack_ride(ride)
    return {'result': "success"}

def test_slack():
    rides = stravabot.get_new_rides_for_club()
    filteredrides = stravabot.filter_rides(rides)
    for ride in filteredrides:
        stravabot.slack_ride(ride)
    return
