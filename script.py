from pprint import pprint
from espn_api import EspnApi
import sys

print(sys.argv[1])


def password(user):
    with open(user + "_pass.txt", "w+") as pass_file:
        return pass_file.read()


username = sys.argv[1]
password = password(username)

api = EspnApi(username, password)


url = "http://fantasy.espn.com/apis/v3/games/flb/seasons/2019/segments/0/leagues/56491263?" \
      "view=mLiveScoring&view=mMatchupScore&view=mPendingTransactions&view=mPositionalRatings&view=mSettings" \
      "&view=mTeam"

less_data_url = "http://fantasy.espn.com/apis/v3/games/flb/seasons/2019/segments/0/leagues/56491263?" \
      "view=mTeam"

resp = api.espn_request(less_data_url)

pprint(resp.json())
