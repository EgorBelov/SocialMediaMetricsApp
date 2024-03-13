from owlready2 import *
import vk_api
import xes
import copy
import json
import pika
from datetime import datetime, timezone
import threading



class Ontology:
    def __init__(self, path):
        onto_path.append("web/onto/")

        self.path = path
        self.onto = get_ontology(self.path)
        self.onto_lock = threading.Lock()

    def create_ontology(self):
        self.onto.load()
        with self.onto:
            class Person(Thing):
                pass

            class Community(Thing):
                pass

            class Activity(Thing):
                pass

            class Post(Thing):
                pass

            class hasName(Community >> str):
                pass

            class hasFirstName(Person >> str):
                pass

            class hasLastName(Person >> str):
                pass

            class hasGender(Person >> str):
                pass

            class hasPhoto(Person >> str):
                pass

            class hasDomain(Person >> str):
                pass

            class hasBirthDay(Person >> str):
                pass

            class hasActivity(ObjectProperty):
                domain = [Person, Community]
                range = [Activity]
                pass

            class friendsWith(Person >> Person):
                pass

            class hasSubscriber(Community >> Person):
                pass

            class subscribedTo(ObjectProperty):
                domain = [Person]
                range = [Community]
                inverse_property = hasSubscriber
                pass

            class likedBy(Post >> Person):
                pass

            class hasTag(Post >> str):
                pass

            class liked(Person >> Post):
                inverse_property = likedBy
                pass

            class viewedBy(Post >> Person):
                pass

            class viewed(Person >> Post):
                inverse_property = viewedBy
                pass

            class postedBy(ObjectProperty):
                domain = [Post]
                range = [Person, Community]
                pass

            class posted(ObjectProperty):
                domain = [Person, Community]
                range = [Post]
                inverse_property = postedBy
                pass

            class isRepostOf(Post >> Post):
                pass

            class isAds(Post >> str):
                pass

            class hasDate(Post >> str):
                pass
        self.onto.save(self.path)

    def save_person(self, person):
        self.onto.load()
        onto_person = self.onto.Person(str(person.u_id))
        onto_person.hasFirstName = [person.first_name]
        onto_person.hasLastName = [person.last_name]
        onto_person.hasGender = [person.gender]
        onto_person.hasBirthDay = [person.birth_day]
        onto_person.hasDomain = [person.domain]
        onto_person.hasPhoto = [person.photo]
        onto_person.hasActivity = []
        onto_person.liked = []
        onto_person.viewed = []
        for friend in person.friends:
            onto_friend = self.onto.Person(str(friend))
            onto_person.friendsWith.append(onto_friend)
        for group in person.groups:
            onto_community = self.onto.Community(str(group))
            onto_person.subscribedTo.append(onto_community)
        self.onto.save(self.path)

    def save_community(self, community):
        self.onto.load()
        onto_community = self.onto.Community(str(community.g_id))
        onto_community.hasName = [community.name]
        onto_community.hasActivity = [self.onto.Activity(community.activity)]
        self.onto.save(self.path)

    def save_post(self, post):
        self.onto_lock.acquire()
        self.onto.load()
        onto_post = self.onto.Post(str(post.id))
        onto_post.postedBy = []
        onto_post.isRepostOf = []
        onto_post.viewedBy = []
        onto_post.likedBy = []
        onto_post.hasTag = []
        # check owner community or person
        if "-" in str(post.owner_id):
            onto_post.postedBy.append(self.onto.Community(str(post.owner_id)[1:]))
        else:
            onto_post.postedBy.append(self.onto.Person(str(post.owner_id)))
        for repost_id in post.copy_history:
            onto_post.isRepostOf.append(self.onto.Post(str(repost_id)))
        for tag in post.tags:
            onto_post.hasTag.append(tag)
        onto_post.isAds = [post.is_ads]
        self.onto.save(self.path)
        self.onto_lock.release()

    def post_viewed(self, user_id, post):
        self.onto_lock.acquire()
        self.onto.load()
        self.onto.Post(str(post.id)).viewedBy.append(self.onto.Person(str(user_id)))
        self.onto.Person(str(user_id)).viewed.append(self.onto.Post(str(post.id)))
        self.onto.save(self.path)
        self.onto_lock.release()

    def post_liked(self, user_id, post):
        self.onto_lock.acquire()
        self.onto.load()
        self.onto.Post(str(post.id)).likedBy.append(self.onto.Person(str(user_id)))
        self.onto.Person(str(user_id)).liked.append(self.onto.Post(str(post.id)))
        self.onto.save(self.path)
        self.onto_lock.release()


class VK:
    def __init__(self, token, target_users, target_groups):
        # try:
        #     vk_session = vk_api.VkApi(token="vk1.a.dScF8dJH-OaSOCsd1XVUdWACvXIcrujqc_MXyxpwk_hId-uId8JZPsN8EBJtpOqATcQ7mbmaU55jX-wjhTnVwcXq40s6WJjW9ri-9zSNv-h9Rps3tQo0qHHkkH2X6GlDWzbfr0x73pDIweZxY2blhLLgMdEEVjedLWwZXykR1QCkQdkMNr16QOPHbqTCZuMYfAFYRH8T6oyAROSGZv-KuQ")
        #     vk_session.auth()  # Попытка авторизации
        #     self.api = vk_session.get_api()
        #     self.user_info = vk_session.user  # Получение информации о пользователе
        #     print(f"Успешная авторизация. Пользователь: {self.user_info['first_name']} {self.user_info['last_name']}")
        # except vk_api.AuthError as e:
        #     print(f"Ошибка авторизации: {e}")
        #     # Обработка ошибки авторизации, например, повторная авторизация, запрос нового токена и т.д.
        self.api = vk_api.VkApi(token="vk1.a.dScF8dJH-OaSOCsd1XVUdWACvXIcrujqc_MXyxpwk_hId-uId8JZPsN8EBJtpOqATcQ7mbmaU55jX-wjhTnVwcXq40s6WJjW9ri-9zSNv-h9Rps3tQo0qHHkkH2X6GlDWzbfr0x73pDIweZxY2blhLLgMdEEVjedLWwZXykR1QCkQdkMNr16QOPHbqTCZuMYfAFYRH8T6oyAROSGZv-KuQ").get_api()
        self.target_users = target_users
        self.target_groups = target_groups

    # Get person from social network
    def get_person(self, user_id):
        vk_user_result = self.api.users.get(user_id=user_id,
                                            fields="bdate, photo_100, age, city, country, home_town, sex, games, online, domain, has_mobile, contacts, site, education, universities, schools, status, last_seen, followers_count, common_count, occupation, nickname, relatives, relation, personal, connections, exports, activities, interests, music, movies, tv, books, games, about, quotes, can_post, can_see_all_posts, can_see_audio")
        if len(vk_user_result) == 0:
            return
        vk_user = vk_user_result[0]
        photo = vk_user["photo_100"] if "photo_100" in vk_user else "unknown"
        gender = vk_user["sex"] if "sex" in vk_user else "unknown"
        birth_day = vk_user["bdate"] if "bdate" in vk_user else "unknown"
        friends = self.get_person_friends(user_id)
        groups = self.get_person_groups(user_id)
        person = Person(vk_user["id"], vk_user["first_name"], vk_user["last_name"], photo,
                        vk_user["domain"], gender=gender, birth_day=birth_day, friends=friends, groups=groups)

        return person

    # Load person"s friends from social network
    def get_person_friends(self, user_id):
        vk_friends_result = self.api.friends.get(user_id=user_id)

        friends = []
        for friend in vk_friends_result["items"]:
            if friend in self.target_users:
                friends.append(friend)
        return friends

    # Load person"s group from social network
    def get_person_groups(self, user_id):
        vk_groups_result = self.api.groups.get(user_id=user_id)
        groups = []
        for group in vk_groups_result["items"]:
            if group in self.target_groups:
                groups.append(group)
        return groups

    # Get community from social network
    def get_community(self, group_id):
        vk_group_result = self.api.groups.getById(group_id=group_id, fields="activity")
        if len(vk_group_result) == 0:
            return
        vk_group = vk_group_result[0]
        community = Community(vk_group["id"], vk_group["name"], vk_group["activity"])

        return community

    # Get posts from social network
    def get_posts(self, owner_id, count, last_post_id):
        posts = []

        try:
            items = self.api.wall.get(owner_id=owner_id, count=count)["items"]
        except:
            return []

        for post in items:
            if "is_pinned" in post and post["is_pinned"]:
                continue

            # Get only last day posts
            if (datetime.now() - datetime.fromtimestamp(post["date"])).days > 1:
                break

            p_id = str(owner_id) + "_" + str(post["id"])

            if p_id == last_post_id:
                break

            tags = [tag.strip("#") for tag in post["text"].split() if tag.startswith("#")]

            is_ads = 0
            if "marked_as_ads" in post and post["marked_as_ads"] == 1:
                is_ads = 1

            new_post = Post(p_id, owner_id, post["date"], post["post_type"], is_ads, tags)

            if "copy_history" in post and len(post["copy_history"]) > 0:
                for repost in post["copy_history"]:
                    new_post.add_history(str(repost["owner_id"]) + "_" + str(repost["id"]))

            posts.append(new_post)

        return posts

    def get_liked_posts(self, person):
        liked_posts = []

        for post in person.posts_seen:
            try:
                liked_post = self.api.likes.isLiked(user_id=person.u_id,
                                                    owner_id=post.id.split("_")[0],
                                                    item_id=post.id.split("_")[1],
                                                    type=post.type)
            except:
                continue

            if not (post in person.posts_liked) and liked_post["liked"]:
                liked_posts.append(post)

        return liked_posts

    def is_user_online(self, person):
        user = self.api.users.get(user_id=person.u_id, fields="online")[0]
        return user["online"] == 1


class NewsFeed:
    def __init__(self):
        self.global_news_feed = {}
        self.news_feed_lock = threading.Lock()

    def is_empty(self, owner_id):
        return owner_id not in self.global_news_feed or len(self.global_news_feed[owner_id]["items"]) == 0

    def get_last_post_id(self, owner_id):
        if self.is_empty(owner_id):
            return -1

        return self.global_news_feed[owner_id]["last_post"]

    def add_posts(self, owner_id, posts):
        if len(posts) == 0:
            return

        if self.is_empty(owner_id):
            self.global_news_feed[owner_id] = {
                "last_post": posts[0].id,
                "lock": threading.Lock(),
                "items": posts
            }
            return

        self.global_news_feed[owner_id]["lock"].acquire()
        try:
            self.global_news_feed[owner_id]["last_post"] = posts[0].id
            self.global_news_feed[owner_id]["items"] = posts + self.global_news_feed[owner_id]["items"]
        finally:
            self.global_news_feed[owner_id]["lock"].release()

    def get_user_news(self, person):
        news_feed = []

        for group_id in person.groups:
            group_id = "-" + str(group_id)
            if group_id in self.global_news_feed:
                self.global_news_feed[group_id]["lock"].acquire()
                try:
                    news_feed += self.global_news_feed[group_id]["items"]
                finally:
                    self.global_news_feed[group_id]["lock"].release()

        for friend_id in person.friends:
            if friend_id in self.global_news_feed:
                self.global_news_feed[friend_id]["lock"].acquire()
                try:
                    news_feed += self.global_news_feed[friend_id]["items"]
                finally:
                    self.global_news_feed[friend_id]["lock"].release()

        return sorted(news_feed, key=lambda p: p.date, reverse=True)


class EventLog:
    def __init__(self, log_path):
        self.log = xes.Log()
        self.log_lock = threading.Lock()
        self.log.classifiers = [
            xes.Classifier(name="org:resource", keys="org:resource"),
            xes.Classifier(name="concept:name", keys="concept:name")
        ]
        self.log_path = log_path

    def add_trace(self, trace):
        if len(trace.events) == 0:
            return

        self.log_lock.acquire()
        try:
            self.log.add_trace(trace)
        finally:
            self.log_lock.release()

    def write_log(self):
        time.sleep(time_to_write_log)
        while True:
            if len(self.log.traces) > 0:
                self.log_lock.acquire()
                try:
                    copy_log = copy.deepcopy(self.log)
                    with open(self.log_path + "/log.xes", "w") as file_to_write:
                        file_to_write.write(str(copy_log))
                        file_to_write.close()
                finally:
                    self.log_lock.release()

    @staticmethod
    def event_online(resource_id):
        e = xes.Event()
        e.attributes = [
            xes.Attribute(type="string", key="concept:name", value="online"),
            xes.Attribute(type="string", key="org:resource", value=str(resource_id)),
            xes.Attribute(type="string", key="user:name", value=str(resource_id)),
            xes.Attribute(type="date", key="time:timestamp", value=datetime.now(timezone.utc).isoformat())
        ]
        return e

    @staticmethod
    def event_offline(resource_id):
        e = xes.Event()
        e.attributes = [
            xes.Attribute(type="string", key="concept:name", value="offline"),
            xes.Attribute(type="string", key="org:resource", value=str(resource_id)),
            xes.Attribute(type="date", key="time:timestamp", value=datetime.now(timezone.utc).isoformat())
        ]
        return e

    @staticmethod
    def event_post_add(resource_id, post):
        e = xes.Event()
        e.attributes = [
            xes.Attribute(type="string", key="concept:name", value="post_add"),
            xes.Attribute(type="string", key="org:resource", value=str(resource_id)),
            xes.Attribute(type="string", key="post:id", value=str(post.id)),
            xes.Attribute(type="string", key="post:type", value=str(post.type)),
            xes.Attribute(type="string", key="post:is_ads", value=str(post.is_ads)),
            xes.Attribute(type="string", key="owner:id", value=str(post.owner_id)),
            xes.Attribute(type="date", key="time:timestamp",
                          value=datetime.fromtimestamp(post.date).astimezone(timezone.utc).isoformat())
        ]
        return e

    @staticmethod
    def event_post_seen(resource_id, post):
        e = xes.Event()
        e.attributes = [
            xes.Attribute(type="string", key="concept:name", value="post_seen"),
            xes.Attribute(type="string", key="org:resource", value=str(resource_id)),
            xes.Attribute(type="string", key="post:id", value=str(post.id)),
            xes.Attribute(type="string", key="post:type", value=str(post.type)),
            xes.Attribute(type="string", key="post:is_ads", value=str(post.is_ads)),
            xes.Attribute(type="date", key="post:date",
                          value=datetime.fromtimestamp(post.date).astimezone(timezone.utc).isoformat()),
            xes.Attribute(type="string", key="owner:id", value=str(post.owner_id)),
            xes.Attribute(type="date", key="time:timestamp", value=datetime.now(timezone.utc).isoformat())
        ]
        return e

    @staticmethod
    def event_post_liked(resource_id, post):
        e = xes.Event()
        e.attributes = [
            xes.Attribute(type="string", key="concept:name", value="post_liked"),
            xes.Attribute(type="string", key="org:resource", value=str(resource_id)),
            xes.Attribute(type="string", key="post:id", value=str(post.id)),
            xes.Attribute(type="string", key="post:type", value=str(post.type)),
            xes.Attribute(type="string", key="post:is_ads", value=str(post.is_ads)),
            xes.Attribute(type="date", key="post:date",
                          value=datetime.fromtimestamp(post.date).astimezone(timezone.utc).isoformat()),
            xes.Attribute(type="string", key="owner:id", value=str(post.owner_id)),
            xes.Attribute(type="date", key="time:timestamp", value=datetime.now(timezone.utc).isoformat())
        ]
        return e

    @staticmethod
    def event_post_copied(resource_id, post):
        e = xes.Event()
        e.attributes = [
            xes.Attribute(type="string", key="concept:name", value="post_copied"),
            xes.Attribute(type="string", key="org:resource", value=str(resource_id)),
            xes.Attribute(type="string", key="post:id", value=str(post.id)),
            xes.Attribute(type="string", key="post:type", value=str(post.type)),
            xes.Attribute(type="string", key="post:is_ads", value=str(post.is_ads)),
            xes.Attribute(type="string", key="owner:id", value=str(post.owner_id)),
            xes.Attribute(type="date", key="time:timestamp",
                          value=datetime.fromtimestamp(post.date).astimezone(timezone.utc).isoformat())
        ]
        return e


class Person:
    friends = []
    groups = []
    interests = []

    def __init__(self, u_id, first_name, last_name, photo, domain, gender, birth_day, friends, groups):
        self.u_id = u_id
        self.first_name = first_name
        self.last_name = last_name
        self.gender = gender
        self.birth_day = birth_day
        self.photo = photo
        self.domain = domain
        self.friends = friends
        self.groups = groups
        self.posts_seen = []
        self.posts_liked = []


class Community:
    def __init__(self, g_id, name, activity):
        self.g_id = g_id
        self.name = name
        self.activity = activity


class Post:
    def __init__(self, id, owner_id, date, type, is_ads, tags):
        self.id = id
        self.owner_id = owner_id
        self.date = date
        self.type = type
        self.is_ads = is_ads
        self.tags = tags
        self.copy_history = []

    def add_history(self, post_id):
        self.copy_history.append(post_id)

    def is_reposted(self):
        return len(self.copy_history) > 0


class GroupEventMiner(threading.Thread):
    def __init__(self, vk, news_feed, ontology, event_log, community):
        threading.Thread.__init__(self)
        self.community = community
        self.vk = vk
        self.news_feed = news_feed
        self.ontology = ontology
        self.event_log = event_log
        self.owner_id = "-" + str(self.community.g_id)
        self.trace = xes.Trace()

    def run(self):
        print("start mining events for community %s" % self.community.g_id)

        time_now = 0
        post_idx = 0
        posts = []
        posts_seen = {}

        while True:
            # Load or update news from community
            if time_now % time_to_update_news == 0:
                self.load_news_feed()

            # Update group event trace
            if time_now % time_to_update_group_trace == 0:
                self.event_log.add_trace(self.trace)
                self.trace = xes.Trace()

                time_now = 0

            # time tick
            time_now += time_tick
            time.sleep(time_tick)

    def load_news_feed(self):
        posts = self.vk.get_posts(self.owner_id, posts_count, self.news_feed.get_last_post_id(self.owner_id))

        for post in posts:
            self.ontology.save_post(post)
            if post.is_reposted():
                self.trace.add_event(self.event_log.event_post_copied(self.owner_id, post))
            else:
                self.trace.add_event(self.event_log.event_post_add(self.owner_id, post))

        self.news_feed.add_posts(self.owner_id, posts)


class UserEventMiner(threading.Thread):
    def __init__(self, vk, news_feed, ontology, event_log, person):
        threading.Thread.__init__(self)
        self.vk = vk
        self.news_feed = news_feed
        self.event_log = event_log
        self.ontology = ontology
        self.person = person
        self.owner_id = person.u_id
        self.user_online = False
        self.trace = xes.Trace()

    def run(self):
        print("start mining events for user %s" % self.person.u_id)

        time_now = 0
        post_idx = 0
        posts = []

        while True:
            # Check user likes and reposts
            if self.user_online and time_now % time_to_check_likes == 0:
                liked_posts = self.vk.get_liked_posts(self.person)

                for liked_post in liked_posts:
                    self.trace.add_event(self.event_log.event_post_liked(self.person.u_id, liked_post))
                    self.person.posts_liked.append(liked_post)
                    self.ontology.post_liked(self.person.u_id, liked_post)

            # Check user status
            if time_now % time_to_check_online == 0:
                is_online = self.vk.is_user_online(self.person)
                if not self.user_online and is_online:
                    print("user %s online" % self.person.u_id)
                    self.trace = xes.Trace()
                    self.trace.add_event(self.event_log.event_online(self.person.u_id))
                    self.user_online = True
                elif self.user_online and not is_online:
                    print("user %s offline" % self.person.u_id)
                    self.trace.add_event(self.event_log.event_offline(self.person.u_id))
                    self.event_log.add_trace(self.trace)
                    self.user_online = False
                    time_now = 0

            # Load user news feed
            if self.user_online and time_now % time_to_update_user_news == 0:
                time.sleep(10)
                posts = self.news_feed.get_user_news(self.person)
                post_idx = 0

            # Check user see new post
            if self.user_online and time_now % time_to_see_post == 0:
                if post_idx < len(posts):
                    self.trace.add_event(self.event_log.event_post_seen(self.person.u_id, posts[post_idx]))
                    self.person.posts_seen.append(posts[post_idx])
                    self.ontology.post_viewed(self.person.u_id, posts[post_idx])
                    post_idx += 1

            # Load or update news from person
            if self.user_online and time_now % time_to_update_news == 0:
                self.load_news_feed()

            # time tick
            time_now += time_tick
            time.sleep(time_tick)

    def load_news_feed(self):
        posts = self.vk.get_posts(self.owner_id, posts_count, self.news_feed.get_last_post_id(self.owner_id))

        for post in posts:
            self.ontology.save_post(post)
            if post.is_reposted():
                self.trace.add_event(self.event_log.event_post_copied(self.owner_id, post))
            else:
                self.trace.add_event(self.event_log.event_post_add(self.owner_id, post))

        self.news_feed.add_posts(self.owner_id, posts)


target_users = []
target_groups = []

posts_count = 3
time_tick = 15
time_to_see_post = 15
time_to_check_likes = 60
time_to_check_online = 60
time_to_update_news = 180
time_to_update_user_news = 600
time_to_update_group_trace = 600
time_to_write_log = 180

ontology = Ontology("../web/onto/social-model.owl")
ontology.create_ontology()
vk = VK('vk1.a.sJU2aMb7AmONW_HcUPZySeydOgeUBD5IA7o6yWn__ROGxE53_5OklI2Y4BwmDdrJZRsYF_N0EOdLMfPtYNyCba1DXK1SyvvPn9lSEbZBzMzJI9STx9AjNz_M2bcRuVM60WYi5wBOWBFFBRo1sMuLJw9n9H2XR9y8PopfGtxTK0HkNaQClsTH27xeilcz-KOZ_IHuawRSjTa4VIaAd4Pbpw', target_users, target_groups)
event_log = EventLog("../web/logs")
news_feed = NewsFeed()

# Rabbit connection declare
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.exchange_declare(exchange="social_data")
channel.exchange_declare(exchange="social_data_to_update")

channel.queue_declare(queue="social_data", durable=True)
channel.queue_declare(queue="social_data_to_update", durable=True,
                      arguments={
                          "x-message-ttl": 3 * 60 * 60 * 1000,  # 3 hours
                          "x-dead-letter-exchange": "social_data"
                      })

channel.queue_bind(exchange="social_data",
                   routing_key="",
                   queue="social_data")

channel.queue_bind(exchange="social_data_to_update",
                   routing_key="",
                   queue="social_data_to_update")

channel.queue_purge(queue="social_data_to_update")
channel.queue_purge(queue="social_data")


# Rabbit new message callback
def callback(ch, method, properties, body):
    data = json.loads(body)

    if data["type"] == "user":
        print("Processing user: %r" % data["user_id"])

        # Get person info from vk
        person = vk.get_person(data["user_id"])

        # Check new user
        if person.u_id not in target_users:
            vk.target_users.append(person.u_id)

            # Start mining events
            UserEventMiner(vk, news_feed, ontology, event_log, person).start()

        # Update info in ontology
        ontology.save_person(person)

        # Publish message to update entity after delay
        channel.basic_publish(exchange="social_data_to_update", routing_key="", body=body)

    if data["type"] == "group":
        print("Processing group: %r" % data["group_id"])

        # Get community from vk
        community = vk.get_community(data["group_id"])

        # Check new community
        if community.g_id not in target_groups:
            vk.target_groups.append(community.g_id)

            # Start mining events
            GroupEventMiner(vk, news_feed, ontology, event_log, community).start()

        # Update info in ontology
        ontology.save_community(community)

        # Publish message to update entity after delay
        channel.basic_publish(exchange="social_data_to_update", routing_key="", body=body)


channel.basic_consume(queue="social_data", on_message_callback=callback, auto_ack=True)

consumer_thread = threading.Thread(target=channel.start_consuming)
consumer_thread.start()
print(" [*] Ontology consumer started\n")

log_writer_thread = threading.Thread(target=event_log.write_log)
log_writer_thread.start()
print(" [*] To exit press CTRL+C")


