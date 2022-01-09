'''
    export group members id into a file
'''
from time import sleep
from telethon import TelegramClient, sync
from telethon.tl.types import (ChannelParticipantAdmin, ChannelParticipantCreator,
                               ChannelParticipantsBanned, ChannelParticipantsKicked)
from telethon.tl.functions.channels import GetParticipantsRequest, InviteToChannelRequest
from telethon.tl.types import ChannelParticipantsSearch, User
from telethon.tl.types.channels import ChannelParticipants
from telethon.errors import PeerFloodError, ChatAdminRequiredError, UserPrivacyRestrictedError
from telethon.tl.types import Channel
from telethon.errors import *
import json


class Export:

    def __init__(self, client, to_group):
        self.client = client
        self.to_group = to_group

    def export_non_banned(self):
        user_list = self.fetch_members(1)
        print(f"fetched non-banned users {len(user_list)} ")

        with open('added_id_list1.txt', 'w') as f:
            f.write(json.dumps(user_list))
            print("non-banned users successfully exported")
        print("successfully exported")

    def export_banned(self):
        user_list = self.fetch_members(0)
        print(f"fetched banned users: {len(user_list)} ")

        with open('banned_id_list1.txt', 'w') as f:
            f.write(json.dumps(user_list))
            print("banned users successfully exported")
        print("successfully exported")

    def fetch_members(self, flag):
        '''
        flag = 1 > fetch non-ban users
        flag = 0 > fetch ban users
        '''
        lis1 = []
        if flag == 0:
            print("featching banned members")
            participants = self.client.get_participants(
                self.to_group, filter=ChannelParticipantsKicked)
            sleep(20)

        elif flag == 1:
            print("featching non-banned members")
            participants = self.client.get_participants(self.to_group)
            sleep(20)
        else:
            pass

        for user in participants:
            if not isinstance(user, User) or user.is_self or user.deleted or user.bot:
                print("deleted or bot or is_self")
                continue

            lis1.append(user.id)

        return lis1
