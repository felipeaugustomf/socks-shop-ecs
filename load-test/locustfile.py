import base64

from faker import Faker
from locust import HttpLocust, TaskSet, task
from random import randint, choice

def register(l):
    _user = getattr(l, 'user', getattr(l.parent, 'user', Faker().simple_profile()))
    _password = getattr(l, 'password', getattr(l.parent, 'password', Faker().password()))
    details = {
        "username": _user.get('username'),
        "first_name": _user.get('name').split(' ')[0],
        "last_name": _user.get('name').split(' ')[1],
        "email": _user.get('mail'),
        "password": _password
    }
    response = l.client.post("/register", json=details)
    return response

def login(l):
    _user = getattr(l, 'user', getattr(l.parent, 'user', Faker().simple_profile()))
    _password = getattr(l, 'password', getattr(l.parent, 'password', Faker().password()))
    users = l.client.get("/customers").json().get("_embedded", {}).get("customer", [])
    user = [user for user in users if user.get('username') == _user.get('username')]
    if not user:
        register(l)

    base64string = base64.encodestring('%s:%s' % (_user.get('username'), _password)).replace('\n', '')
    response = l.client.get("/login", headers={"Authorization":"Basic %s" % base64string})
    return response

def create_card(l):
    data = {
        "longNum": Faker().credit_card_number(),
        "expires": Faker().credit_card_expire(start="now", end="+10y", date_format="%m/%y"),
        "ccv": Faker().credit_card_security_code()
    }
    response = l.client.post("/cards", json=data)
    return response

def create_address(l):
    data = {
        "number": str(Faker().random_int(min=1, max=9999)),
        "street": Faker().street_name(),
        "city": Faker().city(),
        "postcode": Faker().postcode(),
        "country": Faker().country()
    }
    response = l.client.post("/addresses", json=data)
    return response


class NavegacaoTasks(TaskSet):

    
    @task
    def load(self):
        
		self.client.get("/")

		self.user = Faker().simple_profile()
		self.password = Faker().password()

		login(self)            

		self.client.get("/category.html")

		tags = self.client.get("/tags").json().get("tags")
		tag = ["brown","blue"] 
		self.client.get("/category.html?tags={}".format('&'.join(tag)))

		catalogue = self.client.get("/catalogue").json()
		item_id = "3395a43e-2d88-40de-b95f-e00e1502085b"        
		self.client.get("/detail.html?id={}".format(item_id))

		self.client.post("/cart", json={"id": item_id, "quantity": 1})

		self.client.get("/basket.html")

		create_card(self)
		create_address(self)

		self.client.post("/orders")


class API(HttpLocust):
	task_set = NavegacaoTasks
	min_wait = 0
	max_wait = 0
	stop_timeout = 900