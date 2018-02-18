import requests

#setup starts

def setup():
    global dev_key
    dev_key = "" #your key goes here
    global region
    region = input('Select a region from the following: br1 | na1 | eun1 | euw1 | jp1 | kr | la1 | la2 | na1 | oc1 | tr1 | ru | pbe 1 \n')
    global common_path
    common_path = "https://{}.api.riotgames.com".format(region)

#setup ends

#api functions

def get_summoner(summoners_name):
    r = requests.get("{}/lol/summoner/v3/summoners/by-name/{}?api_key={}".format(common_path, summoners_name, dev_key))
    data = r.json()
    while r.status_code != 200:
        if r.status_code == 404:
            print("Summoner not found. Try again! \n")
        else:
            print("Please try again")
        summoners_name = input('Please enter sumoners name: \n')
        r = requests.get("{}/lol/summoner/v3/summoners/by-name/{}?api_key={}".format(common_path, summoners_name, dev_key))
        data = r.json()
    return data

def get_rank(summoners_name):
    sum_id = get_summoner(summoners_name)['id']
    r = requests.get("{}/lol/league/v3/positions/by-summoner/{}?api_key={}".format(common_path,sum_id,dev_key))
    data = r.json()
    all_winrate = round((data[0]['wins']/(data[0]['losses']+data[0]['wins']))*100)
    return {"data":data,"all_winrate":all_winrate}

def get_recent_winrate(summoners_name, last_n_games=6):
    #Ranked Queue: int 420
    
    sum_data = get_summoner(summoners_name)
    acc_id = sum_data['accountId']
    sum_id = sum_data['id']
    data_ids = []
    match_data = []
    win_counter = 0

    r_matches = requests.get("{}/lol/match/v3/matchlists/by-account/{}?api_key={}".format(common_path, acc_id, dev_key),params={"beginIndex":0,"endIndex":last_n_games,"queue":[420]})
    data_matches = r_matches.json()

    for i in range(last_n_games):
        data_ids.append(data_matches['matches'][i]['gameId'])    
    for id_ in data_ids:
        r = requests.get("{}//lol/match/v3/matches/{}?api_key={}".format(common_path, id_, dev_key))
        match_data.append(r.json())
    for i in range(last_n_games):
        for j in range(10):
            if sum_id == match_data[i]['participantIdentities'][j]["player"]["summonerId"]:
                participantId = match_data[i]['participantIdentities'][j]["participantId"]
                if match_data[i]['participants'][participantId-1]['stats']['win']:
                    win_counter += 1
        
    winrate = round((win_counter/last_n_games)*100)
    return winrate

#end of api functions

def main():
    exit_var = False
    while exit_var == False:
        #declaring global scope variables with setup

        setup()

        #input block

        summoners_name = input('Please enter a summoners name: \n')
        last_n_games = int(input('Please select how much last ranked solo/duo games do you want to filter the win rates: \n'))

        #function calls block

        summoners_data = get_summoner(summoners_name)
        rank_data = get_rank(summoners_name)    
        winrate = get_recent_winrate(summoners_name, last_n_games)

        #output block

        print("Summoner's name: {name} | Summoner's level: {level}   \n".format(name=summoners_data['name'],level=summoners_data['summonerLevel']))
        print("Tier: {tier} {rank} {pdl} PDL   \n".format(tier=rank_data['data'][0]['tier'],rank=rank_data['data'][0]['rank'],pdl=rank_data['data'][0]['leaguePoints']))
        print("All games ranked winrate: {}%    \n".format(rank_data['all_winrate']))
        print("winrate on last {} ranked solo/duo games is {}%    \n".format(last_n_games, winrate))

        #exit condition

        if input('Type y + enter to exit, or press any other button + enter to continue \n') in 'yY':
            exit_var = True

if __name__ == '__main__':
    main()
