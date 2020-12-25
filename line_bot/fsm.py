import datetime as dt
import requests as req
import pandas as pd
import matplotlib.pyplot as plt
from abc import ABC, abstractmethod
from transitions.extensions import GraphMachine
from django.conf import settings
from linebot import LineBotApi, WebhookParser
from linebot.models import MessageEvent, TextSendMessage, TextMessage, FlexSendMessage, ImageSendMessage
from pandas.plotting import table 
from .utils import send_text_message, send_image_url, send_flex_message, get_player_stat, get_team_stat, search_player, get_game_stat
from .msg_temp import show_pic, main_menu, table, show_team, choose_game_type, intro
class TocMachine(GraphMachine):
    def __init__(self, **machine_configs):
        self.machine = GraphMachine(model=self, **machine_configs)
        self.name = ''
        self.year = ''
        self.game_year = ''
        self.game_month = ''
        self.game_day = ''
        #self.
    def back_league(self, event):
        text = event.message.text
        print('back_league', text)
        return text.lower() == 'league'

    def back_team_year(self, event):
        text = event.message.text
        print('back_team_year', text)
        return True

    def back_team(self, event):
        text = event.message.text
        print('back_team', text)
        return text.lower() == 'team'

    def back_start(self, event):
        text = event.message.text
        print('back_start', text)
        return text.lower() == 'start'

    def back_player(self, event):
        text = event.message.text
        print('back_player', text)
        return True

    def back_player_name(self, event):
        text = event.message.text
        print('back_player_name', text)
        return True
    
    def back_player_year(self, event):
        text = event.message.text
        print('back_player_year', text)
        return True

    def going_intro(self, event):
        text = event.message.text
        return text.lower() == 'intro'

    def on_enter_intro(self, event):
        msg = intro()
        msg_to_rep = FlexSendMessage("介紹", msg)
        send_flex_message(event.reply_token, msg_to_rep)

    def on_enter_start(self, event):
        reply_token = event.reply_token
        msg = main_menu()
        msg_to_rep = FlexSendMessage('開啟主選單', msg)
        send_flex_message(reply_token, msg_to_rep)
        return True

    def going_fsm(self, event):
        text = event.message.text
        print('going_fsm', text)
        return text.lower() == 'fsm'

    def on_enter_fsm(self, event):
        reply_token = event.reply_token
        msg = show_pic()
        msg_to_rep = FlexSendMessage('fsm', msg)
        send_image_url(reply_token, msg_to_rep)
        return True
    
    def going_player(self, event):
        text = event.message.text
        print('going_player', text)
        return text.lower() == 'player' #如果input是 player 就 return Ture 代表可以進入

    def on_enter_player(self, event): #Input the player name
        send_text_message(event.reply_token, '請輸入球員名稱')
        return True

    def going_player_name(self, event):
        text = event.message.text
        print('going_player_name', text)
        return True

    def on_enter_player_name(self, event): #Input the player name
        text = event.message.text
        print('name: ', text)
        name = search_player(text)
        if(type(name)== int ):
            send_text_message(event.reply_token, '查無此人, 請輸入正確名稱!')
        else:
            self.name = text
            send_text_message(event.reply_token, '請輸入球季年份')
            return True

    def going_player_year(self, event):
        text = event.message.text
        print('going_player_year', text)
        if(self.name != ''):
            return True

    def on_enter_player_year(self, event): #Input the player name
        name = self.name
        year = event.message.text
        if(year.isdigit() == False or len(year)<4 ):
            send_text_message(event.reply_token, '年份錯誤, 請重新輸入!')
            return True
        else:
            ddd = (name, year) 
            print(ddd)
            stat_ = get_player_stat(name, year)
            message = table()
            out_box = {
                "type":"box",
                "layout": "horizontal",
                "margin": "md",
                "spacing": "sm",
                "contents": [],
                "flex" : 1
            }
            box = {
                "type": "box",
                "layout": "vertical",
                "margin": "sm",
                "contents": [],
                "flex" : 1
            }
            for col in range(1, len(stat_.columns)):
                data = {
                    "type": "text",
                    "text": stat_.columns[col],
                    "size": "md",
                    "color": "#555555",
                    "flex" : 1
                }
                box['contents'].append(data)
            out_box['contents'].append(box)
            for i in range(len(stat_.index)): # Iter row number time
                tmp_list = stat_.loc[i].tolist()
                box = {
                "type": "box",
                "layout": "vertical",
                "margin": "sm",
                "spacing": "sm",
                "contents": [],
                "flex" : 1
                }
                for j in range(1, len(tmp_list)):
                    data = {
                        "type": "text",
                        "text": tmp_list[j],
                        "size": "md",
                        "color": "#111111",
                        "flex" : 1
                    }
                    box['contents'].append(data)
                out_box['contents'].append(box)
            message["body"]["contents"][2]["contents"].append(out_box)
            msg_to_rep = FlexSendMessage(self.name + "數據", message)
            send_flex_message(event.reply_token, msg_to_rep)
    
    def going_player_stat(self, event):
        print('going_player_stat', text)
        if (self.year.isdigit() == True):# 可以往下
            return True

    def on_enter_player_stat(self, event): #Select player stats type
        text = event.message.text
        print('enter_player_stat', text)
        send_text_message(event.reply_token, text)
    
    def going_team(self, event):
        text = event.message.text
        print('enter_team', text)
        return text.lower() =='team'

    def on_enter_team(self, event): #Choose which year's stat
        send_text_message(event.reply_token, '請輸入球季年份')
        text = event.message.text 
        return text.lower() =='team'

    def going_team_year(self, event):
        text = event.message.text
        print('going_team_year', text)
        return True

    def on_enter_team_year(self, event): #Show team stat
        text = event.message.text
        print('enter_team_year', text)
        stat_ = get_team_stat(text) #Imgur Link
        if(type(stat_)== int and stat_ == 1):
            send_text_message(event.reply_token, '請輸入正確年份')
            return text.lower() == 'team_year'
        if(type(stat_)== int and stat_ == 2):
            send_text_message(event.reply_token, '查無資料, 請重新輸入!')
            return text.lower() == 'team_year'
        stat_.drop(['Rank', 'PCT', 'GB', 'Home', 'Away'], inplace = True,  axis=1)
        message = show_team()
        for i in range(4):
            tmp_list = stat_.loc[i].tolist()
            print(tmp_list)
            data = {
                "type": "box",
                "layout": "horizontal",
                "contents": []
             }
            for j in range(len(tmp_list)):
                detail_data = {
                    "type": "text",
                    "text": tmp_list[j],
                    "size": "sm",
                    "color": "#555555",
                    "flex": 1,
                    "margin": "md"
                } 
                data['contents'].append(detail_data)
            message["body"]["contents"][4]["contents"].append(data)
        msg_to_rep = FlexSendMessage("球隊戰績", message)
        send_flex_message(event.reply_token, msg_to_rep) 

    def going_league(self, event):
        text = event.message.text
        print('enter_league', text)
        return text.lower() == 'league' 

    def on_enter_league(self, event): #
        message = choose_game_type()
        print(message)
        msg_to_rep = FlexSendMessage("戰績選擇", message)
        send_flex_message(event.reply_token, msg_to_rep)    
    
    def going_league_ordinary(self, event):
        text = event.message.text
        print('going_ordinary', text)
        return text.lower() == 'league_ordinary'
    
    def on_enter_league_ordinary(self, event):
        text = event.message.text
        print('enter_ordinary', text)
        '''send_text_message(event.reply_token, '請輸入年份')'''
        '''send_text_message(event.reply_token, '請輸入月份')
        send_text_message(event.reply_token, '請輸入日')'''
        get_game_stat('yy')
        pass
    
    def going_league_yt(self, event):
        text = event.message.text
        print('enter_yt', text)
        return text.lower() == 'league_yt'
    
    def on_enter_league_yt(self, event):
        pass
    
    def going_league_stat(self, event):
        pass
    
    def on_enter_league_stat(self, event):
        pass
    