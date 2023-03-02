from BaseAPI import BaseAPI

class ChatAPI(BaseAPI):
    POST_WORLD_CHAT_ENDPOINT = '/api/world_chat/post_message'
    WORLD_CHAT_MESSAGE_ENDPOINT = '/api/world_chat/get_message_list'

    def __init__(self):
        BaseAPI.__init__(self)

    def post_world_chat(self, room, msg):
        payload = {
            'message': msg,
            'roomNumber': room
        }

        res = self.post(ChatAPI.POST_WORLD_CHAT_ENDPOINT, payload)

        return res['payload']

    def get_room_msg(self, room):
        # I believe language determines what language the original is translated to
        # lastId is the last message Id. Giving a last message id will cause it to only get messages posted
        # since that message
        # room number should refer to the chat rooms (e.g. Tokyo, Hokkaido, Osaka, etc). Each room is represented with a number
        # Tokyo = 0, Osaka = 1, Hokkaido = 2
        payload = {
            'language': 10,
            'lastId': 0,
            'roomNumber': room
        }
        res = self.post(ChatAPI.WORLD_CHAT_MESSAGE_ENDPOINT, payload)

        return res['payload']