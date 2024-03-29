from datetime import datetime
from sys import maxsize, stdout, exit
import requests
import logging
from settings import *


logger = logging.getLogger() 

def get_matches():
    logging.info("Getting matches from fixture service")
    matches = requests.get("https://apigateway.beinsports.com.tr/api/fixture/rewriteid/current/super-lig")
    match_data = matches.json()["Data"]

    return match_data


def get_delta_hours(match):
    match_date = match.get("matchDate")
    if match_date == None:
        return maxsize
    try:
        delta = datetime.now() - datetime.fromisoformat(match_date)
        delta_hours = (delta.days * SECONDS_IN_DAY + delta.seconds)/3600
    except Exception as e:
        logging.exception("An error occured when caculating estimated time to match match id=%s " %match.get("id"))
        delta_hours = maxsize
    return delta_hours


def get_teams_id_of_match(match):
    home_team = match.get("homeTeam")
    home_team_id = None if home_team is None else home_team.get("id")

    away_team = match.get("awayTeam")
    away_team_id = None if away_team is None else away_team.get("id")

    return home_team_id, away_team_id


def check_incoming_matches():
    matches = get_matches()
    
    result = MATCH_NOT_EXIST
    for match in matches:
        delta_hours = get_delta_hours(match)
        if (delta_hours > -1*HOURS_INTERVAL["feature"] and delta_hours < 0) or (delta_hours < HOURS_INTERVAL["past"] and delta_hours > 0):
            home_team_id, away_team_id = get_teams_id_of_match(match)
            
            if home_team_id in BIG_TEAMS or away_team_id in BIG_TEAMS:
                logging.info("Crusial match found! Match id: %d" %match.get("id"))
                return CRUCIAL_MATCH_EXIST
            logging.info("Match found! Match id: %s" %match.get("id"))
            result = MATCH_EXIST
    return result


if __name__ == '__main__':
    handler = logging.StreamHandler(stdout)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # logger.setLevel(logging.DEBUG)
    # handler.setLevel(logging.DEBUG)
    # handler.setFormatter(formatter)
    # logger.addHandler(handler)

    print(check_incoming_matches())
