from websocket import create_connection
import json

class ma_websocket(object):

    def __init__(self, uri, login, pw):
        self.uri = uri
        self.user = login
        self.pw = pw
        self.ws = create_connection(uri, timeout = 40) 
        self.session = 0
        print("Created Connection")
        print(self.ws.recv())
        message = '{"session":' + str(self.session) + '}'
        self.ws.send(message)
        resp = json.loads(self.ws.recv())
        self.session = resp["session"]
        print("session: " +  str(self.session))
        self.active_attributes = []

    def login(self):
        message = '{"requestType":"login","username":"' + self.user + '","password":' + self.pw + ',"session":' + str(self.session) + ',"maxRequests":10}'
        self.ws.send(message)
        return(self.ws.recv())


    #page: current executor page - 1 ;button: Executor Number (101); state: 1 or 0; id: 0, 1 or 2 (Button 1, 2 or 3) 
    def set_button(self, page, button, state, id):
        if state == 1:
            message = '{"requestType":"playbacks_userInput","cmdline":"","execIndex":' + str(button - 1) + ',"pageIndex":' + str(page) + ',"buttonId":' + str(id) + ',"pressed":true,"released":false,"type":0,"session":'+str(self.session)+',"maxRequests":0}'
        if state == 0:
            message = '{"requestType":"playbacks_userInput","cmdline":"","execIndex":'+ str(button - 1) + ',"pageIndex":' + str(page) + ',"buttonId":' + str(id) + ',"pressed":false,"released":true,"type":0,"session":'+str(self.session)+',"maxRequests":0}'

        self.ws.send(message)
        data = self.ws.recv()
        
    def keep_alive(self):
        print("Keep Alive")
        self.ws.send(f'{{"session":{self.session}}}' )
        #print(self.ws.recv())
    #                                                            exec      on/off name    Color   function
    #returns an array of 50 buttons for the specified page, 50x ['101', 'LT', 1, 'Sequ', '#FFFFFF', 'Go']
    def playbacks(self, page):
        message = '{"requestType":"playbacks","startIndex":[0],"itemsCount":[50],"pageIndex":' + str(page) + ',"itemsType":[3],"view":3,"execButtonViewMode":2,"buttonsViewMode":0,"session":' + str(self.session) + ',"maxRequests":1}'
        self.ws.send(message)
        raw = self.ws.recv()
        exec_json = json.loads(raw)
        try:
            data = exec_json['itemGroups'][0]['items']
            exec_data = []
            for data_set in data:
                for entry in data_set:
                    entry_data = [entry["i"]["t"], entry["oType"]["t"], entry["isRun"], entry["tt"]["t"], entry["bdC"]]
                    if entry["oType"]["t"] != "" and entry["oI"]["t"] != "":
                        entry_data.append(entry["bottomButtons"]["items"][0]["n"]["t"])
                    exec_data.append(entry_data)
            return exec_data
        except:
            print(raw)
            return None

    def get_static_exec_status(self):
        self.ws.send(f'{{"requestType":"playbacks","startIndex":[0],"itemsCount":[10],"pageIndex":0,"itemsType":[2],"view":2,"execButtonViewMode":1,"buttonsViewMode":0,"session":{self.session},"maxRequests":1}}' )
        raw = self.ws.recv()
        exec_json = json.loads(raw)
        try:
            data = exec_json['itemGroups'][0]['items']
            exec_data = []
            for data_set in data:
                for entry in data_set:
                   exec_data.append([entry["executorBlocks"][0]["button1"]["t"], entry["isRun"]])
            return exec_data
        except:
            print(raw)
            return None

    # returns the values for the faders 16 - 25
    def playback_fader(self, page):
        self.ws.send(f'{{"requestType":"playbacks","startIndex":[15],"itemsCount":[10],"pageIndex":{page},"itemsType":[2],"view":2,"execButtonViewMode":1,"buttonsViewMode":0,"session":{self.session},"maxRequests":1}}' )
        raw = self.ws.recv()
        exec_json = json.loads(raw)
        try:
            data = exec_json['itemGroups'][0]['items']
            exec_data = []
            for data_set in data:
                for entry in data_set:
                   exec_data.append(entry["executorBlocks"][0]["fader"]["v"])
            return exec_data
        except:
            print(raw)
            return None
        
    # set a fader value
    def set_fader(self, page, id, value):
        fVal = value / 127.0
        mssg = '{"requestType":"playbacks_userInput","execIndex":' + str(id) + ',"pageIndex":' + str(page) + ',"faderValue":' + str(fVal) + ',"type":1,"session":' + str(self.session) + ',"maxRequests":0}'
        self.ws.send(mssg)
        self.ws.recv()

    def send_command(self, command):
        self.ws.send('{"command":"' + command + '","session":' + str(self.session) + ',"requestType":"command","maxRequests":0}')
        self.ws.recv()

    def restart(self):
        self.ws.connect(self.uri)

    def logoff(self):
        self.ws.close()
        
