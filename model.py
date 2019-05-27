import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
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
        self.table = self.classify()
        
        
    
    def get_matches(self,year=2019):
        url = "https://www.cbf.com.br/futebol-brasileiro/competicoes/campeonato-brasileiro-serie-a/"+str(year)
        #url = "https://www.cbf.com.br/futebol-brasileiro/competicoes/campeonato-brasileiro-serie-a/2018"
        r = requests.get(url)
        data = r.text
        soup = BeautifulSoup(data)

        matches = soup.find("aside").find_all("li")
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
        
        return df
    
    def get_teams(self):
        teams_data = self.matches["home_team"].unique()
        teams_data.sort()
        r = np.array(range(len(t)))
        return pd.DataFrame(r,columns=["index"],index=teams_data)
    
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
        table = pd.merge(table_home,table_away,on="team",how="outer",suffixes=('_home', '_away')).fillna(value=0)
        table[["won","gols_dif","gols_for","points"]] = table.apply(lambda x: pd.Series([x["won_home"]+x["won_away"],#won_counter
                                                                                x["gols_for_home"]+x["gols_for_away"]-
                                                                                x["gols_against_home"]-x["gols_against_away"], #gol difference
                                                                                x["gols_for_home"]+x["gols_for_away"], #gols for
                                                                                x["home_points"]+x["away_points"] #total points        
                                                                               ]) 
                                                                                , axis=1)
        table = table.sort_values(["points","won","gols_dif","gols_for"],ascending=[0,0,0,0])
        #table = stats.reset_index()
        #self.table = table
        
        return table
    
    def team_position(self,team):
        if team is self.teams.values:
            return cl[cl["team"]==team].index[0]
        else:
            print("There is no "+team+ " team!")
    
    def team_index(self,team):
        return self.teams.loc[team][0]
       
    def get_parameters(self,fator = 1):

        table = self.matches.dropna()
        n_teams = len(self.teams)

        ngmarcc = [0.0 for i in range(n_teams)]
        ngmarcf = [0.0 for i in range(n_teams)]
        ngsofrc = [0.0 for i in range(n_teams)]
        ngsofrf = [0.0 for i in range(n_teams)]
        betac = [1.0 for i in range(n_teams)]
        betaf = [1.0 for i in range(n_teams)]
        alfac = [1.0 for i in range(n_teams)]
        alfaf = [1.0 for i in range(n_teams)]

        beta_ant = [0.0 for i in range(2*n_teams)]
        beta_atual = betac + betaf
        alfa_ant = [0.0 for i in range(2*n_teams)]
        alfa_atual = alfac + alfaf
        cresc = (float(fator))**(1.0/(2*n_teams-2))
        w = 1.0
        tol = 0.000001
        
        for i in table.index:
            w = (cresc)**(int(i/10)+1)
            t1 = self.team_index(table.loc[i].home_team)
            t2 = self.team_index(table.loc[i].away_team)
            ngmarcc[t1] += w*table.loc[i].home_score
            ngmarcf[t2] += w*table.loc[i].away_score
            ngsofrc[t1] += w*table.loc[i].away_score
            ngsofrf[t2] += w*table.loc[i].home_score

        ngsofrc = [x if x!=0 else 1/np.max(ngsofrc) for x in ngsofrc]

        while (np.linalg.norm(np.array(beta_atual)-np.array(beta_ant))> tol):
         
            salfac = [0.0 for i in range(n_teams)]
            salfaf = [0.0 for i in range(n_teams)]
            sbetac = [0.0 for i in range(n_teams)]
            sbetaf = [0.0 for i in range(n_teams)]

            for i in range(n_teams):
                beta_ant[i] = betac[i]
                beta_ant[n_teams+i] = betaf[i]
                alfa_ant[i] = alfac[i]
                alfa_ant[n_teams+i] = alfaf[i]

            for i in table.index:
                w = (cresc)**(int(i/10)+1)
                t1 = self.team_index(table.loc[i].home_team)
                t2 = self.team_index(table.loc[i].away_team)

                sbetaf[t1]  += w/betaf[t2]
                salfaf[t1]  += w*alfaf[t2]
                #ngmarcc[t1] += w*table.loc[i].home_score

                sbetac[t2]  += w/betac[t1]
                salfac[t2]  += w*alfac[t1]
                #ngmarcf[t2] += w*table.loc[i].away_score

            for i in range(n_teams):
                alfac[i] = ngmarcc[i]/sbetaf[i]
                alfaf[i] = ngmarcf[i]/sbetac[i]
                betac[i] = salfaf[i]/ngsofrc[i]            
                betaf[i] = salfac[i]/ngsofrf[i]

            #for i in table.index:
            #    w = (cresc)**(int(i/10)+1)
            #    t1 = self.team_index(table.loc[i].home_team)
            #    t2 = self.team_index(table.loc[i].away_team)

            #    salfaf[t1]  += w*alfaf[t2]
            #    #ngsofrc[t1] += w*table.loc[i].away_score

            #    salfac[t2]  += w*alfac[t1]
            #    #ngsofrf[t2] += w*table.loc[i].home_score                


            #for i in range(n_teams):
            #    #print(table.loc[i])
            #    betac[i] = salfaf[i]/ngsofrc[i]            
            #    betaf[i] = salfac[i]/ngsofrf[i]

            mean = np.mean(betac)
            for i in range(n_teams):
                betac[i] /= mean

            mean = np.mean(betaf)
            for i in range(n_teams):
                betaf[i] /= mean

            beta_atual = betac + betaf
            alfa_atual = alfac + alfaf

        p = [alfac, betac, alfaf, betaf]
        df = pd.DataFrame(p,columns=self.teams.index,index=["alfac","betac","alfaf","betaf"]).T
        df["home"] = df["alfac"]*df["betac"] 
        df["away"] = df["alfaf"]*df["betaf"] 
        df = df.sort_values(["home"],ascending=[0])
        self.parameters_strength = df
        
        return df