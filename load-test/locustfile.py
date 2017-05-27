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


class NavegacaoTasks(TaskSet):

    
    @task
    def load(self):
        
        self.client.get("/")

        login(self)            
        
        self.client.get("/category.html")

        catalogue = self.client.get("/catalogue").json()
        item_id = "03fef6ac-1896-4ce8-bd69-b798f85c6e0b"        
        self.client.get("/detail.html?id={}".format(item_id))
        
        self.client.delete("/cart")        
        self.client.post("/cart", json={"id": item_id, "quantity": 1})

        self.client.get("/basket.html")    
    
        with self.client.post("/orders", catch_response=True) as response:
            if response.status_code == 406:
                response.success()


class API(HttpLocust):
    user = Faker().simple_profile()
    password = Faker().password()    
    task_set = NavegacaoTasks
    min_wait = 0
    max_wait = 0
    stop_timeout = 120