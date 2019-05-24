import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime


class championship:
    
    def __init__(self,update_time):
        self.update_time = update_time
        self.matches = self.create_matches()

    def create_matches(self):
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
                home_score,away_score = [x.strip() for x in match.find("span",
                                                                    attrs={'class':'bg-blue color-white label-2'}).text.split("x")]
            
            data.append([home_team,home_score,away_team,away_score,local,date])
        
        columns = ["home_team","home_score","away_team","away_score","local","date"]
        df = pd.DataFrame(data,columns=columns)
        df["update_time"] = self.update_time
        
        return df