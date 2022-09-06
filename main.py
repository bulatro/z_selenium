import time
from parsing import parse_page


def run():
    while True:
        parse_page()
        time.sleep(60 * 60 * 1)


if __name__ == '__main__':
    run()
