#
# Copyright (C) 2025 by AnimeLord-Bots@Github, < https://github.com/AnimeLord-Bots >.
#
# This file is part of < https://github.com/AnimeLord-Bots/FileStore > project,
# and is released under the MIT License.
# Please see < https://github.com/AnimeLord-Bots/FileStore/blob/master/LICENSE >
#
# All rights reserved.

import motor.motor_asyncio
import logging
from config import DB_URI, DB_NAME
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

default_verify = {
    'is_verified': False,
    'verified_time': 0,
    'verify_token': "",
    'link': ""
}

class Mehedi:
    def __init__(self, DB_URI, DB_NAME):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(DB_URI)
        self.db = self.client[DB_NAME]
        self.channel_data = self.db['channels']
        self.admins_data = self.db['admins']
        self.user_data = self.db['users']
        self.sex_data = self.db['sex']
        self.banned_user_data = self.db['banned_user']
        self.autho_user_data = self.db['autho_user']
        self.del_timer_data = self.db['del_timer']
        self.fsub_data = self.db['fsub']
        self.rqst_fsub_data = self.db['request_forcesub']
        self.rqst_fsub_Channel_data = self.db['request_forcesub_channel']

    async def present_user(self, user_id: int):
        found = await self.user_data.find_one({'_id': user_id})
        return bool(found)

    async def add_user(self, user_id: int):
        await self.user_data.insert_one({'_id': user_id})
        logger.info(f"Added user {user_id} to database")
        return

    async def full_userbase(self):
        user_docs = await self.user_data.find().to_list(length=None)
        return [doc['_id'] for doc in user_docs]

    async def del_user(self, user_id: int):
        await self.user_data.delete_one({'_id': user_id})
        logger.info(f"Deleted user {user_id} from database")
        return

    async def admin_exist(self, admin_id: int):
        found = await self.admins_data.find_one({'_id': admin_id})
        return bool(found)

    async def add_admin(self, admin_id: int):
        if not await self.admin_exist(admin_id):
            await self.admins_data.insert_one({'_id': admin_id})
            logger.info(f"Added admin {admin_id} to database")
            return

    async def del_admin(self, admin_id: int):
        if await self.admin_exist(admin_id):
            await self.admins_data.delete_one({'_id': admin_id})
            logger.info(f"Deleted admin {admin_id} from database")
            return

    async def get_all_admins(self):
        users_docs = await self.admins_data.find().to_list(length=None)
        return [doc['_id'] for doc in users_docs]

    async def ban_user_exist(self, user_id: int):
        found = await self.banned_user_data.find_one({'_id': user_id})
        return bool(found)

    async def add_ban_user(self, user_id: int):
        if not await self.ban_user_exist(user_id):
            await self.banned_user_data.insert_one({'_id': user_id})
            logger.info(f"Banned user {user_id}")
            return

    async def del_ban_user(self, user_id: int):
        if await self.ban_user_exist(user_id):
            await self.banned_user_data.delete_one({'_id': user_id})
            logger.info(f"Unbanned user {user_id}")
            return

    async def get_ban_users(self):
        users_docs = await self.banned_user_data.find().to_list(length=None)
        return [doc['_id'] for doc in users_docs]

    async def set_del_timer(self, value: int):
        existing = await self.del_timer_data.find_one({})
        if existing:
            await self.del_timer_data.update_one({}, {'$set': {'value': value}})
        else:
            await self.del_timer_data.insert_one({'value': value})
        logger.info(f"Set delete timer to {value} seconds")

    async def get_del_timer(self):
        data = await self.del_timer_data.find_one({})
        return data.get('value', 600) if data else 0

    async def channel_exist(self, channel_id: int):
        found = await self.fsub_data.find_one({'_id': channel_id})
        return bool(found)

    async def add_channel(self, channel_id: int):
        if not await self.channel_exist(channel_id):
            await self.fsub_data.insert_one({'_id': channel_id, 'mode': 'off'})
            logger.info(f"Added channel {channel_id} to force-sub list")
            return

    async def rem_channel(self, channel_id: int):
        if await self.channel_exist(channel_id):
            await self.fsub_data.delete_one({'_id': channel_id})
            logger.info(f"Removed channel {channel_id} from force-sub list")
            return

    async def show_channels(self):
        channel_docs = await self.fsub_data.find().to_list(length=None)
        return [doc['_id'] for doc in channel_docs]

    async def get_channel_mode(self, channel_id: int):
        data = await self.fsub_data.find_one({'_id': channel_id})
        return data.get("mode", "off") if data else "off"

    async def set_channel_mode(self, channel_id: int, mode: str):
        await self.fsub_data.update_one(
            {'_id': channel_id},
            {'$set': {'mode': mode}},
            upsert=True
        )
        logger.info(f"Set channel {channel_id} mode to {mode}")

    async def req_user(self, channel_id: int, user_id: int):
        try:
            await self.rqst_fsub_Channel_data.update_one(
                {'_id': int(channel_id)},
                {'$addToSet': {'user_ids': int(user_id)}},
                upsert=True
            )
            logger.info(f"Added user {user_id} to request list for channel {channel_id}")
        except Exception as e:
            logger.error(f"Failed to add user {user_id} to request list for channel {channel_id}: {e}")

    async def del_req_user(self, channel_id: int, user_id: int):
        await self.rqst_fsub_Channel_data.update_one(
            {'_id': channel_id},
            {'$pull': {'user_ids': user_id}}
        )
        logger.info(f"Removed user {user_id} from request list for channel {channel_id}")

    async def req_user_exist(self, channel_id: int, user_id: int):
        try:
            found = await self.rqst_fsub_Channel_data.find_one({
                '_id': int(channel_id),
                'user_ids': int(user_id)
            })
            return bool(found)
        except Exception as e:
            logger.error(f"Failed to check user {user_id} in request list for channel {channel_id}: {e}")
            return False

    async def reqChannel_exist(self, channel_id: int):
        channel_ids = await self.show_channels()
        exists = channel_id in channel_ids
        logger.debug(f"Checked channel {channel_id} existence: {exists}")
        return exists

    async def db_verify_status(self, user_id):
        user = await self.user_data.find_one({'_id': user_id})
        return user.get('verify_status', default_verify) if user else default_verify

    async def db_update_verify_status(self, user_id, verify):
        await self.user_data.update_one({'_id': user_id}, {'$set': {'verify_status': verify}})
        logger.info(f"Updated verify status for user {user_id}")

    async def get_verify_status(self, user_id):
        return await self.db_verify_status(user_id)

    async def update_verify_status(self, user_id, verify_token="", is_verified=False, verified_time=0, link=""):
        current = await self.db_verify_status(user_id)
        current.update({
            'verify_token': verify_token,
            'is_verified': is_verified,
            'verified_time': verified_time,
            'link': link
        })
        await self.db_update_verify_status(user_id, current)

    async def set_verify_count(self, user_id: int, count: int):
        await self.sex_data.update_one({'_id': user_id}, {'$set': {'verify_count': count}}, upsert=True)
        logger.info(f"Set verify count to {count} for user {user_id}")

    async def get_verify_count(self, user_id: int):
        user = await self.sex_data.find_one({'_id': user_id})
        count = user.get('verify_count', 0) if user else 0
        return count

    async def reset_all_verify_counts(self):
        await self.sex_data.update_many({}, {'$set': {'verify_count': 0}})
        logger.info("Reset all verify counts")

    async def get_total_verify_count(self):
        pipeline = [{"$group": {"_id": None, "total": {"$sum": "$verify_count"}}}]
        result = await self.sex_data.aggregate(pipeline).to_list(length=1)
        return result[0]["total"] if result else 0

    async def set_protect_content(self, user_id: int, enabled: bool):
        await self.user_data.update_one({'_id': user_id}, {'$set': {'protect_content': enabled}}, upsert=True)
        logger.info(f"Set protect_content to {enabled} for user {user_id}")

    async def get_protect_content(self, user_id: int) -> bool:
        user_data = await self.user_data.find_one({'_id': user_id})
        return user_data.get('protect_content', True) if user_data else True

    async def set_hide_caption(self, user_id: int, enabled: bool):
        await self.user_data.update_one({'_id': user_id}, {'$set': {'hide_caption': enabled}}, upsert=True)
        logger.info(f"Set hide_caption to {enabled} for user {user_id}")

    async def get_hide_caption(self, user_id: int) -> bool:
        user_data = await self.user_data.find_one({'_id': user_id})
        return user_data.get('hide_caption', False) if user_data else False

    async def set_channel_button(self, user_id: int, enabled: bool):
        await self.user_data.update_one({'_id': user_id}, {'$set': {'channel_button': enabled}}, upsert=True)
        logger.info(f"Set channel_button to {enabled} for user {user_id}")

    async def get_channel_button(self, user_id: int) -> bool:
        user_data = await self.user_data.find_one({'_id': user_id})
        return user_data.get('channel_button', False) if user_data else False

db = Mehedi(DB_URI, DB_NAME)

#
# Copyright (C) 2025 by AnimeLord-Bots@Github, < https://github.com/AnimeLord-Bots >.
#
# This file is part of < https://github.com/AnimeLord-Bots/FileStore > project,
# and is released under the MIT License.
# Please see < https://github.com/AnimeLord-Bots/FileStore/blob/master/LICENSE >
#
# All rights reserved.
#