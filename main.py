from time import sleep
from telethon import TelegramClient, sync
from telethon.tl.types import (
    ChannelParticipantAdmin, ChannelParticipantCreator)
from telethon.tl.functions.channels import GetParticipantsRequest, InviteToChannelRequest
from telethon.tl.types import ChannelParticipantsSearch, User
from telethon.tl.types.channels import ChannelParticipants
from telethon.errors import PeerFloodError, ChatAdminRequiredError, UserPrivacyRestrictedError
from telethon.tl.types import Channel
from telethon.errors import *
import json
from export import Export as E
import threading
import asyncio
import yaml


class Bot():
    added_id_list = []
    banned_id_list = []
    skip = tuple([ChannelParticipantAdmin, ChannelParticipantCreator])
    first = None
    lock = asyncio.Lock()
    start_ = 0
    count_ = 0

    def __init__(self, api_id, api_hash, phone, session_name, from_group_link, to_group_link):
        self.client = TelegramClient(session_name, api_id, api_hash).start()

        sleep(10)
        if not self.client.is_user_authorized():
            self.client.send_code_request(phone)
            self.client.sign_in(phone, input(
                'Enter code for {}: '.format(phone)))

        self.me = self.client.get_me()
        sleep(10)
        self.fetched_users = []
        self.from_group = self.client.get_entity(from_group_link)
        sleep(10)
        self.to_group = self.client.get_entity(to_group_link)
        sleep(10)

        # one time initialization

        if Bot.first is None:
            self.export = E(self.client, self.to_group)
            self.export.export_banned()
            self.export.export_non_banned()
            Bot.initialize()
            Bot.first = "123123"
        self.fetch_user()

    def fetch_user(self):
        print(f"{ self.me.first_name } starts featching members")

        participants = self.client.get_participants(self.from_group)
        sleep(20)
        for user in participants:
            if not isinstance(user, User) or user.is_self or user.deleted or user.bot:
                print("deleted or bot or is_self")
                continue
            skip_u = False

            skip_u = isinstance(user.participant, Bot.skip)

            if skip_u:
                print(f"{user.first_name } is an admin")
                continue

            if user.id in Bot.added_id_list or user.id in Bot.banned_id_list:
                print(f"{user.first_name} already exists.")
                continue

            self.fetched_users.append(user)
        print(f"{len(self.fetched_users)} users fetched")

    async def invite_user(self):
        Bot.count_ = len(self.fetched_users)//4
        self.start = Bot.start_
        self.end = Bot.start_ + Bot.count_
        Bot.start_ = self.end
        print(
            f"start{self.start} : end {self.end} | count_{Bot.count_} : start_{Bot.start_}")

        print(f"{self.me.first_name} starts inviting users")
        added_list = []
        count = 0
        users = [v for i, v in enumerate(
            self.fetched_users) if self.start <= i < self.end]
        print(f"i have {len(users)} users")
        for user in users:
            await Bot.lock.acquire()
            try:
                if user.id in Bot.added_id_list or user.id in Bot.banned_id_list:
                    print(f"{user.first_name} already exist")
                    Bot.lock.release()
                    continue
                print(f"{self.me.first_name} >>>>>>> {user.first_name}")

                await self.client(InviteToChannelRequest(self.to_group, [user]))
                added_list.append(user.id)
                Bot.added_id_list.append(user.id)
                await asyncio.sleep(40)
                Bot.lock.release()
            except PeerFloodError:
                print("End script")
                count += 1
                print(
                    f"{self.me.first_name} ( {count} ) I'll try again in 1 hour, added users ( {len(added_list)})")
                Bot.lock.release()
                await asyncio.sleep(3600)
            except UserPrivacyRestrictedError:
                print("Private user")
                Bot.lock.release()
            except ChatAdminRequiredError:
                print("You are not an admin in destination channel...")
                Bot.lock.release()
                exit()
            except Exception as e:
                print(e)
                Bot.lock.release()
        print(f"client {self.me.first_name} added {len(added_list)} users ")
        try:
            await self.client.send_message('@', f'client {self.me.first_name} added {len(added_list)} users and exists, change the link')
        except:
            pass

    @classmethod
    def initialize(cls):
        print("********* intializing added_id_list and banned_id_list ***************")
        with open('added_id_list1.txt', 'r') as f:
            cls.added_id_list = json.loads(f.read())

        with open('banned_id_list1.txt', 'r') as f:
            cls.banned_id_list = json.loads(f.read())

        print("*********    done   *******************************")


def get_clients(path):
    ''' return dict of clients '''
    with open(path, 'r') as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as e:
            print(e)


to_group_link = ''
client_ob = list()
clients = get_clients("config.yaml").values()
for client in clients:
    client_ob.append(Bot(client['api_id'], client['api_hash'], client['phone_number'],
                         client['session_name'], client['from_group_link'], to_group_link))


async def main():

    await asyncio.wait([
                       client.invite_user() for client in client_ob
                       ])


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
