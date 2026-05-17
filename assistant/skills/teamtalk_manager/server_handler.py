# skills/teamtalk_manager/server_handler.py
import TeamTalk5
import time
import os
import random
import pygame

SKILL_DIR = os.path.dirname(os.path.abspath(__file__))

class ServerHandler(TeamTalk5.TeamTalk):
    def __init__(self, assistant, server_config):
        super().__init__()
        self.assistant = assistant
        self.config = server_config
        self._is_running = True

    def _play_sound(self, sound_name):
        soundpack = self.config.get('soundpack', 'default')
        path = os.path.join(SKILL_DIR, 'sounds', soundpack, f'{sound_name}.wav')
        if os.path.exists(path):
            try: pygame.mixer.Sound(path).play()
            except Exception as e: print(f"Error playing sound ({path}): {e}")
        else: print(f"Warning: Sound file not found: {path}")

    def _get_random_line(self, filename):
        path = os.path.join(SKILL_DIR, 'text', f'{filename}.txt')
        if not os.path.exists(path):
            print(f"Warning: Text file not found: {path}")
            return ""
        with open(path, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]
        return random.choice(lines) if lines else ""

    def _output(self, response_key, **kwargs):
        kwargs['server_name'] = self.config['server_name']
        text_to_speak = self.assistant.get_response(response_key, **kwargs)
        if self.config.get('speech', 'true').lower() == 'true':
            self.assistant.speak(text_to_speak)
        if self.config.get('log', 'true').lower() == 'true':
            log_dir = "logs"
            if not os.path.exists(log_dir): os.makedirs(log_dir)
            with open(os.path.join(log_dir, f"{self.config['server_name']}.log"), 'a', encoding='utf-8') as f:
                f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {text_to_speak}\n")
    
    def onConnectSuccess(self):
        self._output("tt_connected")
        self.doLogin(
            TeamTalk5.ttstr(self.config.get('nickname')),
            TeamTalk5.ttstr(self.config.get('username', '')),
            TeamTalk5.ttstr(self.config.get('password', '')),
            "Dora Assistant"
        )

    def onCmdMyselfLoggedIn(self, cmdId, useraccount):
        self._output("tt_login_success")
        channel_path = self.config.get('channel', '/')
        channel_id = self.getChannelIDFromPath(TeamTalk5.ttstr(channel_path))
        if channel_id:
            self.doJoinChannelByID(channel_id, TeamTalk5.ttstr(""))
            self.doSubscribe(channel_id, TeamTalk5.Subscription.SUBSCRIBE_CHANNEL_MSG)
        else:
            print(f"Warning: Channel '{channel_path}' not found.")
            root_id = self.getRootChannelID()
            self.doJoinChannelByID(root_id, TeamTalk5.ttstr(""))
            self.doSubscribe(root_id, TeamTalk5.Subscription.SUBSCRIBE_CHANNEL_MSG)

    def onCmdUserLoggedIn(self, user):
        if user.nUserID == self.getMyUserID(): return
        nickname = TeamTalk5.ttstr(user.szNickname)
        username = TeamTalk5.ttstr(user.szUsername)
        self._play_sound('in')
        self._output("tt_new_user", nickname=nickname, username=username)

    def onCmdUserLoggedOut(self, user):
        nickname = TeamTalk5.ttstr(user.szNickname)
        username = TeamTalk5.ttstr(user.szUsername)
        random_text = self._get_random_line('logouts')
        self._play_sound('out')
        self._output("tt_user_logged_out", nickname=nickname, username=username, random_text=random_text)

    def onCmdUserJoinedChannel(self, user):
        if user.nUserID == self.getMyUserID(): return
        channel = self.getChannel(user.nChannelID)
        channel_name = TeamTalk5.ttstr(channel.szName) if channel else "unknown channel"
        nickname = TeamTalk5.ttstr(user.szNickname)
        username = TeamTalk5.ttstr(user.szUsername)
        self._play_sound('join')
        self._output("tt_event_user_joined_channel", nickname=nickname, username=username, channel=channel_name)
        
    def onCmdUserLeftChannel(self, channelid, user):
        channel = self.getChannel(channelid)
        channel_name = TeamTalk5.ttstr(channel.szName) if channel else "unknown channel"
        nickname = TeamTalk5.ttstr(user.szNickname)
        username = TeamTalk5.ttstr(user.szUsername)
        self._play_sound('leave')
        self._output("tt_event_user_left_channel", nickname=nickname, username=username, channel=channel_name)
        
    def onCmdUserTextMessage(self, textmessage):
        nickname = TeamTalk5.ttstr(textmessage.szFromUsername)
        content = TeamTalk5.ttstr(textmessage.szMessage)
        if textmessage.nMsgType == TeamTalk5.TextMsgType.MSGTYPE_CHANNEL:
            self._play_sound('channel')
            self._output("tt_event_user_msg_channel", nickname=nickname, content=content)
        elif textmessage.nMsgType == TeamTalk5.TextMsgType.MSGTYPE_USER:
            self._play_sound('user')
            self._output("tt_event_user_msg_private", nickname=nickname, content=content)

    def start(self):
        try:
            self.connect(
                TeamTalk5.ttstr(self.config['host']),
                int(self.config['tcpport']),
                int(self.config.get('udpport', self.config['tcpport']))
            )
            while self._is_running:
                self.runEventLoop(200)
        except Exception as e:
            print(f"Error running '{self.config['server_name']}' bot: {e}")
        finally:
            self.disconnect()
            self.closeTeamTalk()

    def stop(self):
        self._is_running = False

    def execute_kick(self, nickname_to_kick):
        users = self.getServerUsers()
        for user in users:
            if TeamTalk5.ttstr(user.szNickname).lower() == nickname_to_kick.lower():
                self.doKickUser(user.nUserID, user.nChannelID)
                return True
        return False

    def get_users_in_channel_text(self):
        users_in_channel = self.getChannelUsers(self.getMyChannelID())
        nicknames = [TeamTalk5.ttstr(user.szNickname) for user in users_in_channel if user.nUserID != self.getMyUserID()]
        return ", ".join(nicknames) if nicknames else ""

    def get_users_in_channel(self):
        users_in_channel = self.getChannelUsers(self.getMyChannelID())
        return [user for user in users_in_channel if user.nUserID != self.getMyUserID()]

    def send_pm(self, recipient_nickname, message_text):
        users = self.getServerUsers()
        for user in users:
            if TeamTalk5.ttstr(user.szNickname).lower() == recipient_nickname.lower():
                pm = TeamTalk5.TextMessage()
                pm.nMsgType = TeamTalk5.TextMsgType.MSGTYPE_USER
                pm.nToUserID = user.nUserID
                pm.szMessage = TeamTalk5.ttstr(message_text)
                self.doTextMessage(pm)
                return True
        return False

    def send_cm(self, message_text):
        cm = TeamTalk5.TextMessage()
        cm.nMsgType = TeamTalk5.TextMsgType.MSGTYPE_CHANNEL
        cm.nChannelID = self.getMyChannelID()
        cm.szMessage = TeamTalk5.ttstr(message_text)
        self.doTextMessage(cm)

    def send_bm(self, message_text):
        bm = TeamTalk5.TextMessage()
        bm.nMsgType = TeamTalk5.TextMsgType.MSGTYPE_BROADCAST
        bm.szMessage = TeamTalk5.ttstr(message_text)
        self.doTextMessage(bm)