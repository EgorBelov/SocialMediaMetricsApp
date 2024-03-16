import json
from datetime import datetime

import networkx as nx
import psycopg2
from matplotlib import pyplot as plt

from App.mutual_friends.main import VkFriends
from App.mutual_friends.settings import token, my_id, api_v, max_workers, delay, deep


class D3(VkFriends):
	"""
	Генерит json, дабы можно было заюзать http://bl.ocks.org/mbostock/4062045
	{
		"nodes":[
			{"name":"Myriel","group":1},
			{"name":"Napoleon","group":1},
			{"name":"Mlle.Baptistine","group":1}
		],
		"links":[
			{"source":1,"target":0,"value":1},
			{"source":2,"target":0,"value":8}
		]
	}
	target - Myriel, source 1 - Napoleon
	"""

	def __init__(self, token, my_id, api_v, max_workers):
		VkFriends.__init__(self, token, my_id, api_v, max_workers)
		self.friendships = self.common_friends()
		self.js = {"nodes": [], "links": []}
		self.dict_friends = self.to_json()
		self.write_json(self.to_json())

	def to_json(self):
		"""
		Из self.friendships сначала составляем узлы, затем ребра
		Если одновременно, то ребра вначале могут ссылаться на несуществующие узлы
		Group везде одинаковый, но добавлено photo
		"""
		for i in self.friendships:
			self.js['nodes'].append({"name": "%s %s" % (i[0]['first_name'], i[0]['last_name']),
									 												"group": 1, "photo": i[0]['photo']})
		for i in self.friendships:
			if i[1]:
				find_world = '%s %s' % (i[0]['first_name'], i[0]['last_name'])
				for d in self.js["nodes"]:
					if find_world in d.values():
						for c in i[1]:
							find_friend = '%s %s' % (c['first_name'], c['last_name'])
							for e in self.js["nodes"]:
								if find_friend in e.values():
									self.js['links'].append({"source": self.js["nodes"].index(e),
															 		"target": self.js["nodes"].index(d), "value": 1})

		return json.JSONEncoder().encode(self.js)


	def write_json(self, json):
		with open("static/miserables.json", "w") as f:
			f.write(json)

if __name__ == '__main__':
	conn = psycopg2.connect(
		database="SocialMediaMetrics",
		user="postgres",
		password="123321",
		host="localhost",
		port="5432"
	)

	# Создание курсора
	cursor = conn.cursor()

	# Запрос на выбор всех пользователей из таблицы vk_users
	cursor.execute('SELECT * FROM vk_users')
	users_data = cursor.fetchall()

	a = D3(token, users_data[0][1], api_v, max_workers)
	# Создание пустого графа
	G = nx.Graph()

	# Добавление узлов
	for node_data in a.js["nodes"]:
		G.add_node(node_data["name"], group=node_data["group"], photo=node_data["photo"])

	# Добавление ребер
	for link in a.js["links"]:
		source = a.js["nodes"][link["source"]]["name"]
		target = a.js["nodes"][link["target"]]["name"]
		G.add_edge(source, target, value=link["value"])


	# Отобразите граф (если необходимо)
	plt.show()
	# Сохранение изменений и закрытие соединения
	cursor.close()
	conn.close()

