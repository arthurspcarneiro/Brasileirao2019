import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime


class championship:
    
    def __init__(self,update_time):
        self.update_time = update_time
        self.matches = self.get_matches()
        self.teams = self.get_teams()

    def get_matches(self):
        url = "https://www.cbf.com.br/futebol-brasileiro/competicoes/campeonato-brasileiro-serie-a"
        r = requests.get(url)
        data = r.text
        soup = BeautifulSoup(data)

        matches = soup.find("aside").find_all("li")#,attrs={'class':'swiper-wrapper'})
        data = []
        for match in matches:
            date = match.find("span",
                            attrs={'class':'partida-desc text-1 color-lightgray p-b-15 block uppercase text-center'}).text.strip()[5:21]
            if date[0].isdigit():
                date = datetime.strptime(date,'%d/%m/%Y %H:%M')
            else:
                date = None
                
            home_team,away_team = match.find_all("span",attrs={'class':'time-sigla'})
            home_team,away_team = home_team.text,away_team.text
            local = match.find("span",
                            attrs={'class':'partida-desc text-1 color-lightgray block uppercase text-center'}).text.strip().split("\n")[0]
            score = match.find("span",attrs={'class':'bg-blue color-white label-2'})
            home_score,away_score = None,None
            if score:
                home_score,away_score = [int(x.strip()) for x in match.find("span",
                                                                    attrs={'class':'bg-blue color-white label-2'}).text.split("x")]
            
            data.append([home_team,home_score,away_team,away_score,local,date])
        
        columns = ["home_team","home_score","away_team","away_score","local","date"]
        df = pd.DataFrame(data,columns=columns)
        df["update_time"] = self.update_time
        df["home_score"] = pd.to_numeric(df["home_score"])
        df["away_score"] = pd.to_numeric(df["away_score"])
        #df["away_score"] = df["away_score"].astype(np.int64)
        #df["home_score"] = df["home_score"].astype(np.int64)
        
        return df
    
    def get_teams(self):
        teams_data = self.matches["home_team"].unique()
        teams_data.sort()
        return pd.DataFrame(teams_data,columns=["short_name_team"])
    
    def classify(self,table=None):
        if table == None:
            table = self.matches.dropna()
        table[["home_points","away_points"]] = table.apply(lambda x: pd.Series([1,1]) 
                                                           if (x["home_score"] == x["away_score"]) 
                                                           else (pd.Series([3,0]) 
                                                                 if (x["home_score"] > x["away_score"]) 
                                                                 else pd.Series([0,3])), axis=1)
        table_home = pd.DataFrame(table.groupby(["home_team"])['home_score', 'away_score', 'home_points'].sum())
        table_home.columns = ["gols_for","gols_against","home_points"]
        table_home.index.name = "team"
        table_away = pd.DataFrame(table.groupby(["away_team"])['home_score', 'away_score', 'away_points'].sum())
        table_away.columns = ["gols_against","gols_for","away_points"]
        table_away.index.name = "team"
        won_home = pd.DataFrame(table[table["home_points"]==3].groupby(["home_team"])["home_points"].count())
        won_home.columns = ["won"]
        won_home.index.name = "team"
        won_away = pd.DataFrame(table[table["away_points"]==3].groupby(["away_team"])["away_points"].count())
        won_away.columns = ["won"]
        won_away.index.name = "team"
        table_home = pd.merge(table_home,won_home,on="team",how="outer")
        table_away = pd.merge(table_away,won_away,on="team",how="outer")
        stats = pd.merge(table_home,table_away,on="team",how="outer",suffixes=('_home', '_away')).fillna(value=0)
        stats[["won","gols_dif","gols_for","points"]] = stats.apply(lambda x: pd.Series([x["won_home"]+x["won_away"],#won_counter
                                                                                x["gols_for_home"]+x["gols_for_away"]-
                                                                                x["gols_against_home"]-x["gols_against_away"], #gol difference
                                                                                x["gols_for_home"]+x["gols_for_away"], #gols for
                                                                                x["home_points"]+x["away_points"] #total points        
                                                                               ]) 
                                                                                , axis=1)
        stats = stats.sort_values(["points","won","gols_dif","gols_for"],ascending=[0,0,0,0])
        stats = stats.reset_index()
        
        return stats