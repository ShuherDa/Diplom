from pprint import pprint
import requests
import time
import json
import os
from sys import getdefaultencoding

main_id = 171691064
token = '7b23e40ad10e08d3b7a8ec0956f2c57910c455e886b480b7d9fb59859870658c4a0b8fdc4dd494db19099'

def get_user_info(token, code):
    pprint('.')
    try:
        response = requests.get('https://api.vk.com/method/execute?v=5.80&access_token=' + token + '&code=' + code)
    except:
        time.sleep(2)
        response = requests.get('https://api.vk.com/method/execute?v=5.80&access_token=' + token + '&code=' + code)

    return response.json()['response']

def get_friends(token,id):
    pprint('.')
    response = requests.get('https://api.vk.com/method/friends.get',
                            params=dict(
                            access_token=token,
                            user_id=id,
                            v=5.80
                            )).json()['response']
    return {item for item in response['items']}

def get_groups(token, code):
    pprint('.')
    try:
        response = requests.get('https://api.vk.com/method/execute?v=5.80&access_token=' + token + '&code=' + code)
    except:
        time.sleep(2)
        response = requests.get('https://api.vk.com/method/execute?v=5.80&access_token=' + token + '&code=' + code)

    return response.json()['response']

def parts(lst, n=25):
    """ разбиваем список на части - по 25 в каждой """
    return [lst[i:i + n] for i in iter(range(0, len(lst), n))]

def wright_json(data):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    current_dir = os.path.join(current_dir, "groups.json")
    with open(current_dir, "w", encoding=getdefaultencoding()) as file:
        json.dump(data, file)


friends = get_friends(token, main_id)
code = '%s%s' % ('return{', '"%s": API.groups.get({"user_id":%s, "fields":"members_count", "extended":%s})};' %
                 (main_id, main_id, 1))
my_groups = get_groups(token, code)[str(main_id)]['items']
my_groups_set = set(group_id['id'] for group_id in my_groups)

my_friends_group = []
for friend in parts(list(friends)):
    code = 'return {'
    for id in friend:
         code = '%s%s' % (code, '"%s": API.users.get({"user_ids":%s}),' % (id, id))
    code = '%s%s' % (code, '};')
    information = get_user_info(token, code)
    code = 'return {'
    for user_info in information:
        if not 'deactivated' in information[user_info][0].keys():
            code = '%s%s' % (code, '"%s": API.groups.get({"user_id":%s, "extended":%s}),' % (
                                                                              information[user_info][0]['id'],
                                                                              information[user_info][0]['id'],
                                                                              1))
    code = '%s%s' % (code, '};')
    friends_group = get_groups(token, code)
    for friends_id in friends_group:
        if friends_group[friends_id]:
            for group_id in friends_group[friends_id]['items']:
                if not 'deactivated' in group_id.keys():
                    my_friends_group.append(group_id['id'])

difference_group = my_groups_set.difference(set(my_friends_group))
new_group = []
for group_id in difference_group:
    for group in my_groups:
        if group['id'] == group_id:
            new_group.append({'name': group['name'], 'gid': group['id'], 'members_count': group['members_count']})

wright_json(new_group)