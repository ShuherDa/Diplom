from pprint import pprint
import requests
import time
import json
import os
from sys import getdefaultencoding

MAIN_ID = 171691064
# TOKEN = '7b23e40ad10e08d3b7a8ec0956f2c57910c455e886b480b7d9fb59859870658c4a0b8fdc4dd494db19099'
TOKEN = 'b9ab9d541cf06f1caf5704d0102a2dcd166df7051f541ca8019438e58638b77d6daba53c6e6010406a79e'
URL_LONG = 2000 #Нашел инфу что лучше использовать не длиннее 2000 символов, ном может быть чуть больше

def vk_request(token, code):
    pprint('.')
    try:
        result = requests.get(f"https://api.vk.com/method/execute?v=5.80&access_token={token}&code={code}").json()
        time.sleep(0.1)
    except:
         result = {'error': {'error_code': -1, 'error_msg': 'Ошибка выполнения запроса'}}

    if 'error' in result:
         print('Ошибка при получении данных пользователя: {} ({})'.format(result['error']['error_code'],
                                                                          result['error']['error_msg']))
         return dict()
    if 'response' in result.keys():
        return result['response']
    else:
        return dict()

def get_groups(friends):
    pprint('.')
    my_friends_group = []
    code = 'return {'
    url_len = 152 #длина начала url в функции vk_request
    index = 0
    for id in friends:
        index += 1
        part_code = '"%s": API.groups.get({"user_id":%s, "fields":"members_count", "extended":%s}),' % (id, id, 1)
        code = '%s%s' % (code, part_code)
        url_len += len(part_code)
        if url_len >= URL_LONG or index == len(friends):
            url_len = 152
            code = '%s%s' % (code, '};')
            friends_group = vk_request(TOKEN, code)
            for friends_id in friends_group:
                if friends_group[friends_id] and 'items' in friends_group[friends_id]:
                    for group_id in friends_group[friends_id]['items']:
                        if 'members_count' in group_id.keys():
                            my_friends_group.append({'id': group_id['id'], 'name': group_id['name'],
                                                     'members_count': group_id['members_count']})
                        else:
                            my_friends_group.append({'id': group_id['id'], 'name': group_id['name'],
                                                     'members_count': 0})
            code = 'return {'
    return my_friends_group

def write_json(filename, data):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    current_dir = os.path.join(current_dir, filename)
    with open(current_dir, "w", encoding=getdefaultencoding()) as file:
        json.dump(data, file, ensure_ascii=False)

def get_friends(id):
    print('.')
    code = '%s%s' % ('return{', '"%s": API.friends.get({"user_id":%s})};' % (id, id))
    friends = vk_request(TOKEN, code)
    if str(id) in friends.keys():
        friends = friends[str(id)]
        if 'items' in friends.keys():
            friends = friends['items']
        else:
            friends = {}
    else:
        friends = {}
    return friends

def get_file(my_groups, my_friends_group):
    new_group = []
    difference_group = set(group_id['id'] for group_id in my_groups).difference(set(group_id['id'] for group_id in
                                                                                    my_friends_group))
    for group_id in difference_group:
        for group in my_groups:
            if group['id'] == group_id:
                new_group.append({'name': group['name'], 'gid': group['id'], 'members_count': group['members_count']})
    return new_group


friends = get_friends(MAIN_ID)

my_groups = get_groups({MAIN_ID})

my_friends_group = get_groups(friends)

write_json("groups.json", get_file(my_groups, my_friends_group))