from params import *
from pyngrok import ngrok
from flask import Flask, request
import requests
from Database import ContractsDatabase
from BlockchainConnector import BlockchainConnector


class Bot:
    def __init__(self, token, server_url):
        self.token = token
        self.server_url = server_url
        self.set_webhook()

    def make_api_url(self, method):
        return f"https://api.telegram.org/bot{self.token}/{method}"

    def set_webhook(self):
        method = "setWebhook"
        api_url = self.make_api_url(method)
        post_data = {
            "url": self.server_url,
        }
        req = requests.post(api_url, data=post_data, headers={'header': 'Content-Type: application/json'})
        return req.json()

    def send_message(self, chat_id, text):
        method = "sendMessage"
        url = self.make_api_url(method)
        data = {"chat_id": chat_id, "text": text}
        requests.post(url, data=data)

setmyaccount_flag = False
setnewowner_flag = False
mintnft_flag = False

def open_tunnel():
    port = 5000
    ngrok.set_auth_token(ngrok_token)

    # Open a ngrok tunnel to the HTTP server
    public_url = ngrok.connect(port).public_url
    print(" * ngrok tunnel \"{}\" -> \"http://127.0.0.1:{}\"".format(public_url, port))

    app = Flask(__name__)

    # Update any base URLs to use the public ngrok URL
    app.config["BASE_URL"] = "https" + public_url.split('http')[1]
    print(app.config["BASE_URL"])

    bot = Bot(bot_token, app.config["BASE_URL"])

    connector = BlockchainConnector()
    db = ContractsDatabase()


    @app.route("/", methods=["GET", "POST"])
    def receive_update():
        message = None
        if request.method == "POST":
            print(request.json)
            message = request.json["message"]
            chat_id = message["chat"]["id"]
            # photos = message.get("photo")
            uid = message["from"]["id"]
            global setmyaccount_flag
            global setnewowner_flag
            global mintnft_flag
            connector.load_contract()
            connector.key_to_account()
            messages = ["/start", "/setmyaccount", "/setnewowner", "/mintnft"]

            # Start command
            if "entities" in message and message["text"] == "/start" and message["entities"][0]["type"] == "bot_command":
                setmyaccount_flag = False
                setnewowner_flag = False
                mintnft_flag = False
                if not db.get_user_by_uid(uid):
                    bot.send_message(chat_id,
                                     "Hello, %s! Please send me your account data with command /setmyaccount"
                                     % (message["from"]["first_name"]))
                else:
                    bot.send_message(chat_id,
                                     "Hello, %s! Do you want to mint some NFTs?" % (message["from"]["first_name"]))

            elif ("entities" in message and message["text"] == "/setmyaccount" and message["entities"][0]["type"] == "bot_command")\
                    or (setmyaccount_flag and message["text"] not in [value for value in messages if value not in ["/setmyaccount"]]):
                try:
                    setnewowner_flag = False
                    mintnft_flag = False
                    if setmyaccount_flag and "text" in message:
                        key = message["text"]
                        '''
                        To Do добавить проверку ключа
                        '''
                        connector.key = key
                        connector.key_to_account(key)
                        if db.get_user_by_uid(uid) is None or db.get_user_by_uid(uid) == []:
                            db.insert_new_user(uid, key)
                        else:
                            db.update_user_key(uid, key)
                        bot.send_message(chat_id, "New data saved successfully")
                        setmyaccount_flag = False
                    else:
                        bot.send_message(chat_id,
                                         "%s, please enter your account data below"
                                         % (message["from"]["first_name"]))
                        setmyaccount_flag = True
                except Exception as e:
                    bot.send_message(chat_id, 'An error occurred, please try again')
                    print(e)

            elif ("entities" in message and message["text"] == "/setnewowner" and message["entities"][0]["type"] == "bot_command")\
                    or (setnewowner_flag and message["text"] not in [value for value in messages if value not in ["/setnewowner"]]):
                try:
                    setmyaccount_flag = False
                    mintnft_flag = False
                    if setnewowner_flag and "text" in message:
                        new_owner_address = message["text"]
                        '''
                        To Do добавить проверку адреса нового владельца
                        '''
                        connector.ownership_transfer(new_owner_address)
                        bot.send_message(chat_id, "Owner changed successfully")
                        setnewowner_flag = False
                    else:
                        if connector.get_contract_owner() == connector.account.address:
                            bot.send_message(chat_id,
                                             "%s, please enter your new owner data below"
                                             % (message["from"]["first_name"]))
                            setnewowner_flag = True
                        else:
                            bot.send_message(chat_id,
                                             "Your address does not match match with contract owner's, you must "
                                             "change the data")
                except Exception as e:
                    bot.send_message(chat_id, 'An error occurred, please try again')
                    print(e)

            elif ("entities" in message and message["text"] == "/mintnft" and message["entities"][0]["type"] == "bot_command")\
                    or (mintnft_flag and message["text"] not in [value for value in messages if value not in ["/mintnft"]]):
                try:
                    setmyaccount_flag = False
                    setnewowner_flag = False
                    if mintnft_flag and "text" in message:
                        nft_address = message["text"]
                        '''
                        To Do добавить проверку ссылки на объект
                        '''
                        connector.mint_NFT(nft_address)
                        bot.send_message(chat_id, "Token minted successfully")
                        mintnft_flag = False
                    else:
                        if connector.get_contract_owner() == connector.account.address:
                            bot.send_message(chat_id,
                                             "%s, please enter below the address of the object in IPFS in format: "
                                             "ipfs://[object's address] "
                                             % (message["from"]["first_name"]))
                            mintnft_flag = True
                        else:
                            bot.send_message(chat_id, "Your address does not match match with contract owner's, "
                                                      "you must change the data")
                except Exception as e:
                    bot.send_message(chat_id, 'An error occurred, please try again')
                    print(e)

            # Otherwise
            else:
                bot.send_message(chat_id, "Please try again")

        return message
    app.run()
