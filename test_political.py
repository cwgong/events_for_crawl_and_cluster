import requests
import json


# data = {}
def requests_post(url, data):
    # 注意：
    #   data 可以是 dic，也可以是 list 等
    # data = json.dumps(params, ensure_ascii = False, indent = 2)
    data = json.dumps(data)
    # data = json.dumps(data).encode("UTF-8")
    response = requests.post(url, data=data)
    response = response.json()

    return response

# if __name__ == '__main__':
