import stravabot

def test_slack():
    rides = stravabot.get_new_rides_for_club()
    filteredrides = stravabot.filter_rides(rides)
    for ride in filteredrides:
        stravabot.slack_ride(ride)
    return