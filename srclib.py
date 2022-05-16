import requests
from operator import itemgetter
from sys import argv
import sys
SRC_API = "https://www.speedrun.com/api/v1"

def conv_to_time(time):
	hours = int(time / 3600)
	time = time - hours*3600
	minutes = int(time / 60)
	time = round(time - minutes*60, 3)
	seconds = int(time)
	milliseconds = int(round((time - seconds)*1000, 0))
	if len(str(seconds)) == 1:
		seconds = "0" + str(seconds)
	if len(str(milliseconds)) == 1:
		milliseconds = "00" + str(milliseconds)
	elif len(str(milliseconds)) == 2:
		milliseconds = "0" + str(milliseconds)
	if hours == 0:
		if len(str(minutes)) == 1:
			minutes = "0" + str(minutes)
		return str(minutes) + ":" + str(seconds) + "." + str(milliseconds)
	return str(hours) + ":" + str(minutes) + ":" + str(seconds) + "." + str(milliseconds)

def spaces(list):
	len_list = []
	max_len = 0
	for i in list:
		len_list.append(len(i))
		if len(i) > max_len:
			max_len = len(i)
	for j in range(0, len(list)):
		list[j] = list[j] + " "*(max_len - len_list[j])
	return list

def get_player_name(id):
	try:
		return requests.get(f"{SRC_API}/users/{id}").json()['data']['names']['international']
	except KeyError:
		return None

def get_game_name(id):
	try:
		return requests.get(f"{SRC_API}/games/{id}").json()['data']['names']['international']
	except KeyError:
		return None

def get_level_name(id):
	try:
		return requests.get(f"{SRC_API}/levels/{id}").json()['data']['name']
	except KeyError:
		return None

def get_cat_name(id):
	try:
		return requests.get(f"{SRC_API}/categories/{id}").json()['data']['name']
	except KeyError:
		return None

def get_runs(username):
	return requests.get(f"{SRC_API}/runs?user={get_id(username)}").json()['data']

def get_run(id):
	try:
		run = requests.get(f"{SRC_API}/runs/{id}").json()['data']
	except KeyError:
		return {'error':'NameError', 'description':'No run found with given id'}
		sys.exit()
	game = get_game_name(run['game'])
	player = get_player_name(run['players'][0]['id'])
	cat = get_cat_name(run['category'])
	time = conv_to_time(run['times']['primary_t'])
	if run['level'] != None:
		level = get_level_name(run['level'])
		return {'player':player, 'game':game, 'level':level, 'category':cat, 'time':time, 'link':run['weblink']}
	else:
		return {'player':player, 'game':game, 'category':cat, 'time':time, 'link':run['weblink']}

def get_id(username):
	try:
		return requests.get(f"{SRC_API}/users/{username}").json()['data']['id']
	except KeyError:
		return None

def get_game_id(game):
	try:
		return requests.get(f"{SRC_API}/games/{game}").json()['data']['id']
	except KeyError:
		return None

def get_level_id(game_id, level):
	try:
		runs = requests.get(f"{SRC_API}/games/{game_id}/levels").json()['data']
	except KeyError:
		return None
	count = 0
	while True:
		try:
			if runs[count]['name'] == level or level == None:
				return runs[count]['id']
		except IndexError:
			return None
		count += 1

def get_cat_id(game_id, category):
	try:
		runs = requests.get(f"{SRC_API}/games/{game_id}/categories").json()['data']
	except KeyError:
		return input_error(3)
	count = 0
	while True:
		try:
			if (runs[count]['name'] == category or category == None) and runs[count]['type'] == 'per-game':
				return runs[count]['id']
			count += 1
		except (IndexError, KeyError):
			return {'error':'ValueError', 'description':'Could not find category in game'}

def get_il_cat_id(game_id, category):
	try:
		runs = requests.get(f"{SRC_API}/games/{game_id}/categories").json()['data']
	except KeyError:
		return input_error(3)
	count = 0
	while True:
		try:
			if (runs[count]['name'] == category or category == None) and runs[count]['type'] == 'per-level':
				return runs[count]['id']
			count += 1
		except (IndexError, KeyError):
			return {'error':'ValueError', 'description':'Could not find category in game'}

def get_cat_list(game):
	print("")
	try:
		cats = requests.get(f"{SRC_API}/games/{get_game_id(game)}/categories").json()['data']
	except KeyError:
		return input_error(2)
	list = []
	list.append(len(cats))
	for dict in cats:
		list.append({'category':dict['name'], 'type':dict['type']})
	return list

def get_level_list(game):
	print("")
	try:
		levels = requests.get(f"{SRC_API}/games/{get_game_id(game)}/levels").json()['data']
	except KeyError:
		return input_error(2)
	list = []
	list.append(len(levels))
	for dict in levels:
		list.append({'level':dict['name'], 'type':dict['type']})
	return list

def get_var_list(game):
	try:
		vars = requests.get(f"{SRC_API}/games/{get_game_id(game)}/variables").json()['data']
	except KeyError:
		return input_error(2)
	list = []
	for dict in vars:
		list.append({'variable':dict['name'], 'type':dict['scope']['type'], 'values':[]})
		for value in dict['values']['values'].values():
			list['values'].append(value['label'])
	return list

def get_discord(game):
	if game == "speedrun.com":
		return "https://discord.gg/0h6sul1ZwHVpXJmK"
	game_id = get_game_id(game)
	if game_id == None:
		return input_error(2)
	game = requests.get(f"{SRC_API}/games/{game_id}").json()['data']
	return {'game':get_game_name(game_id), 'discord':game['discord']}

def get_following(user):
	user_id = get_id(user)
	if user_id == None:
		return input_error(2)
	following = requests.get(f"https://www.speedrun.com/_fedata/user/stats?userId={user_id}").json()['followStats']
	list = []
	for game in following:
		list.append({'game':game['game']['name']})
	return list

def get_games(user):
	user_id = get_id(user)
	if user_id == None:
		return input_error(2)
	games = requests.get(f"https://www.speedrun.com/_fedata/user/stats?userId={user_id}").json()['gameStats']
	list = []
	for game in games:
		list.append({'game':game['game']['name']})
	return list

def get_run_count(username, game_id):
	offset = 0
	count = 0
	user_id = get_id(username)
	if user_id == None:
		return input_error(2)
	while True:
		if game_id != None:
			runs = requests.get(f"{SRC_API}/runs?user={user_id}&max=200&offset={offset}&game={game_id}").json()
			if runs['data'] == [] and offset == 0:
				return 0
			else:
				count += len(runs['data'])
		else:
			runs = requests.get(f"{SRC_API}/runs?user={user_id}&max=200&offset={offset}").json()
			if runs['data'] == [] and offset == 0:
				return 0
			else:
				count += len(runs['data'])
		if count % 200 == 0:
			offset += 200
			if offset == 10000:
				return 10000
			elif runs['data'] == []:
				return count
		else:
			return count

def get_wr_count(username):
	offset = 0
	count = 0
	user_id = get_id(username)
	if user_id == None:
		return input_error(2)
	username = get_player_name(user_id)
	while True:
		runs = requests.get(f"{SRC_API}/users/{user_id}/personal-bests?top=1&max=200&offset={offset}").json()['data']
		count += len(runs)
		if count % 200 == 0:
			offset += 200
			if offset == 10000:
				return {'player':username, 'wrs':10000}
			elif runs['data'] == []:
				return {'player':username, 'wrs':count}
		else:
			return {'player':username, 'wrs':count}

def get_podium_count(username):
	offset = 0
	count = 0
	user_id = get_id(username)
	if user_id == None:
		return input_error(2)
	username = get_player_name(user_id)
	while True:
		runs = requests.get(f"{SRC_API}/users/{user_id}/personal-bests?top=3&max=200&offset={offset}").json()['data']
		count += len(runs)
		if count % 200 == 0:
			offset += 200
			if offset == 10000:
				return {'player':username, 'podiums':10000}
			elif runs['data'] == []:
				return {'player':username, 'podiums':count}
		else:
			return {'player':username, 'podiums':count}

def get_num_runs(game_id, cat_id):
	offset = 0
	count = 0
	while True:
		try:
			count += len(requests.get(f"{SRC_API}/leaderboards/{game_id}/category/{cat_id}?max=200&offset={offset}").json()['data']['runs'])
		except KeyError:
			continue
		if count % 200 == 0:
			offset += 200
		else:
			return count

def get_il_num_runs(game_id, level_id, cat_id):
	offset = 0
	count = 0
	if level_id == None and level != None:
		return input_error(4)
	if cat_id == None and category != None:
		return input_error(5)
	while True:
		try:
			count += len(requests.get(f"{SRC_API}/leaderboards/{game_id}/level/{level_id}/{cat_id}?max=200&offset={offset}").json()['data']['runs'])
		except KeyError:
			continue
		if count % 200 == 0:
			offset += 200
		else:
			return count

def get_wr(game, category):
	game_id = get_game_id(game)
	if game_id == None:
		return input_error(3)
	cat_id = get_il_cat_id(game, category)
	try:
		run = requests.get(f"{SRC_API}/leaderboards/{game_id}/category/{cat_id}?top=1").json()['data']['runs'][0]['run']
	except KeyError:
		return input_error(4)
	player = get_player_name(run['players'][0]['id'])
	time = run['times']['primary_t']
	time = conv_to_time(time)
	link = run['weblink']
	if cat_id == None or category == None:
		category = requests.get(f"{SRC_API}/games/{game_id}/categories").json()['data'][0]['name']
	game = get_game_name(game_id)
	return {'game':game, 'category':category, 'player':player, 'time':time, 'link':link}

def get_il_wr(game, level, category):
	game_id = get_game_id(game)
	if game_id == None:
		return input_error(3)
	level_id = get_level_id(game, level)
	cat_id = get_il_cat_id(game, category)
	try:
		run = requests.get(f"{SRC_API}/leaderboards/{game_id}/level/{level_id}/{cat_id}?top=1").json()['data']['runs'][0]['run']
	except KeyError:
		return {'error':'NameError', 'description':'false category or level name'}
	player = get_player_name(run['players'][0]['id'])
	time = run['times']['primary_t']
	time = conv_to_time(time)
	link = run['weblink']
	if cat_id == None or category == None:
		category = requests.get(f"{SRC_API}/games/{game_id}/categories").json()['data'][0]['name']
	if level_id == None or level == None:
		level = requests.get(f"{SRC_API}/games/{game_id}/levels").json()['data'][0]['name']
	game = get_game_name(game_id)
	return {'game':game, 'level':level, 'category':category, 'player':player, 'time':time, 'link':link}

def get_pb(username, game, category):
	user_id = get_id(username)
	if user_id == None:
		return input_error(3)
	game_id = get_game_id(game)
	if game_id == None:
		return input_error(4)
	cat_id = get_cat_id(game_id, category)
	try:
		run = requests.get(f"{SRC_API}/runs?game={game_id}&category={cat_id}&user={user_id}&orderby=date").json()['data']
	except KeyError:
		return input_error(4)
	player = get_player_name(user_id)
	time = conv_to_time(run[-1]['times']['primary_t'])
	link = run[-1]['weblink']
	if cat_id == None or category == None:
		category = requests.get(f"{SRC_API}/games/{game_id}/categories").json()['data'][0]['name']
	game = get_game_name(game_id)
	return {'game':game, 'category':category, 'player':player, 'time':time, 'link':link}

def get_il_pb(username, game, level, category):
	user_id = get_id(username)
	if user_id == None:
		return input_error(3)
	game_id = get_game_id(game)
	if game_id == None:
		return input_error(4)
	level_id = get_level_id(game_id, level)
	cat_id = get_il_cat_id(game_id, category)
	try:
		run = requests.get(f"{SRC_API}/runs?game={game_id}&category={cat_id}&user={user_id}&level={level_id}&orderby=date").json()['data']
	except KeyError:
		return {'error':'NameError', 'description':'false category or level name'}
	player = get_player_name(user_id)
	time = conv_to_time(run[-1]['times']['primary_t'])
	link = run[-1]['weblink']
	if cat_id == None or category == None:
		category = requests.get(f"{SRC_API}/games/{game_id}/categories").json()['data'][0]['name']
	if level_id == None or level == None:
		level = requests.get(f"{SRC_API}/games/{game_id}/levels").json()['data'][0]['name']
	game = get_game_name(game_id)
	return {'game':game, 'level':level, 'category':category, 'player':player, 'time':time, 'link':link}

def get_verified(username, game):
	offset = 0
	count = 0
	user_id = get_id(username)
	if user_id == None:
		return input_error(2)
	game_id = get_game_id(game)
	if game != None and game_id == None:
		return input_error(3)
	while True:
		if game != None:
			runs = requests.get(f"{SRC_API}/runs?examiner={user_id}&max=200&offset={offset}&game={game_id}").json()
			try:
				if runs['data'] == [] and offset == 0:
					return 0
				else:
					count += len(runs['data'])
			except KeyError:
				continue
		else:
			runs = requests.get(f"{SRC_API}/runs?examiner={user_id}&max=200&offset={offset}").json()
			try:
				if runs['data'] == [] and offset == 0:		
					return 0
				else:
					count += len(runs['data'])
			except KeyError:
				continue
		if count % 200 == 0:
			offset += 200
			if offset == 10000:
				return 10000
			elif runs['data'] == []:
				return count
		else:
			return count

def get_pending(game):
	game_id = get_game_id(game)
	if game_id == None:
		return input_error(2)
	count = 0
	offset = 0
	while True:
		pending = requests.get(f"{SRC_API}/runs?game={game_id}&status=new&max=200&offset={offset}").json()['data']
		count += len(pending)
		if count % 200 == 0:
			offset += 200
			if offset == 10000 or len(pending) == 0:
				return {'game':get_game_name(game_id), 'runs':count}
		else:
			return {'game':get_game_name(game_id), 'runs':count}

def get_vlb(game):
	game_id = get_game_id(game)
	if game_id == None:
		return input_error(2)
	mod_list = requests.get(f"{SRC_API}/games/{game_id}?embed=moderators").json()['data']['moderators']['data']
	vlb_list = []
	for i in range(0, len(mod_list)):
		user = mod_list[i]['names']['international']
		vlb_list.append({'name':user, 'verified':get_verified(user, game)})
		vlb_list = sorted(vlb_list, key=itemgetter('verified'), reverse=True)
	return vlb_list

def get_vpg(user):
	user_id = get_id(user)
	if user_id == None:
		return input_error(2)
	mod_games = requests.get(f"{SRC_API}/games?moderator={user_id}&max=200").json()['data']
	vpg_list = []
	for games in mod_games:
		game = games['abbreviation']
		vpg_list.append({'game':game, 'verified':get_verified(user, game)})
		vpg_list = sorted(vpg_list, key=itemgetter('verified'), reverse=True)
	return vpg_list

def get_rpg(username):
	user_id = get_id(username)
	if user_id == None:
		return input_error(2)
	games = []
	pbs = requests.get(f"{SRC_API}/users/{user_id}/personal-bests?max=200").json()['data']
	for h in range(0, len(pbs)):
		try:
			games.index(pbs[h]['run']['game'])
		except ValueError:
			games.append(pbs[h]['run']['game'])
	rpg_list = []
	for game_id in games:
		game = get_game_name(game_id)
		rpg_list.append({'game':game, 'runs':get_run_count(username, game_id)})
		rpg_list = sorted(rpg_list, key=itemgetter('runs'), reverse=True)
	return rpg_list

def get_rpc(game):
	game_id = get_game_id(game)
	if game_id == None:
		return input_error(2)
	num_runs = {'game':get_game_name(game_id), 'categories':[]}
	cats = requests.get(f"{SRC_API}/games/{game_id}/categories?max=200").json()['data']
	for cat in cats:
		if cat['type'] == 'per-game':
			num_runs['categories'].append({'category':cat['name'], 'runs':get_num_runs(game_id, cat['id'])})
	return num_runs

def get_rplc(game, level):
	game_id = get_game_id(game)
	if game_id == None:
		return input_error(2)
	level_id = get_level_id(game_id, level)
	if level_id == None and level != None:
		return input_error(3)
	num_runs = {'game':get_game_name(game_id), 'level':get_level_name, 'categories':[]}
	cats = requests.get(f"{SRC_API}/games/{game_id}/categories?max=200").json()['data']
	for cat in cats:
		if cat['type'] == 'per-level':
			num_runs['categories'].append({'category':cat['name'], 'runs':get_il_num_runs(game_id, level_id, cat['id'])})
	return num_runs

def get_comsob(game, category):
	game_id = get_game_id(game)
	cat_id = get_il_cat_id(game_id, category)
	if game_id == None:
		return input_error(2)
	sob = 0
	offset = 0
	while True:
		runs = requests.get(f"{SRC_API}/games/{game_id}/records?top=1&max=200&scope=levels&offset={offset}").json()['data']
		for run in runs:
			if run['category'] == cat_id:
				try:
					sob += run['runs'][0]['run']['times']['primary_t']
				except IndexError:
					return {'error':'IndexError', 'description':'not all runs completed'}
		if len(runs) == 200:
			offset += 200
		elif len(runs) != 200:
			sob = conv_to_time(sob)
			return {'game':get_game_name(game_id), 'category':get_cat_name(cat_id), 'sob':sob}

def get_sob(user, game, category):
	user_id = get_id(user)
	game_id = get_game_id(game)
	cat_id = get_il_cat_id(game_id, category)
	if user_id == None:
		return input_error(2)
	if game_id == None:
		return input_error(3)
	sob = 0
	offset = 0
	level = 0
	while True:
		runs = requests.get(f"{SRC_API}/users/{user_id}/personal-bests?max=200&game={game_id}&offset={offset}").json()['data']
		for run in runs:
			if run['run']['category'] == cat_id:
				sob += run['run']['times']['primary_t']
				level += 1
		if len(runs) == 200:
			offset += 200
		elif len(runs) != 200:
			if level == len(requests.get(f"{SRC_API}/games/{game_id}/levels").json()['data']):
				sob = conv_to_time(sob)
				return {'user':get_player_name(user_id), 'game':get_game_name(game_id), 'category':get_cat_name(cat_id), 'sob':sob}
			else:
				return {'error':'IndexError', 'description':'not all runs completed'}

def get_avg_pos(user, game, category):
	user_id = get_id(user)
	game_id = get_game_id(game)
	cat_id = get_il_cat_id(game_id, category)
	if user_id == None:
		return input_error(2)
	if game_id == None:
		return input_error(3)
	pos = 0
	offset = 0
	level = 0
	while True:
		runs = requests.get(f"{SRC_API}/users/{user_id}/personal-bests?max=200&game={game_id}&offset={offset}").json()['data']
		for run in runs:
			if run['run']['category'] == cat_id:
				pos += run['place']
				level += 1
		if len(runs) == 200:
			offset += 200
		elif len(runs) != 200:
			pos = round(pos/level, 3)
			return {'user':get_player_name(user_id), 'game':get_game_name(game_id), 'category':get_cat_name(cat_id), 'pos':pos}

def input_error(missing):
	if a[missing] == None:
		return {'error':'VariableError', 'description':f'no variable found at {missing}'}
	elif a[missing] != None:
		return {'error':'VariableError', 'description':f'incorrect variable {a[missing]}'}