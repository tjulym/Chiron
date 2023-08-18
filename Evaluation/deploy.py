import requests
import sys

codes = []


if __name__ == '__main__':
    try:
        wrap_name = sys.argv[1]
        file_path = sys.argv[2]
    except Exception as e:
        raise e

    with open(file_path, "r") as f:
        lines = f.readlines()
        codes = ''.join(lines)

    url = "http://127.0.0.1:31112/function/%s" %  wrap_name

    res = requests.post(url, data=codes, headers={"update": "1"}).text
    print(res)