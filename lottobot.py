import discord
import json
import random
import re
from pathlib import Path
client = discord.Client()
KEY_PATH = Path('../key.txt')
prefix = '!'
scratch_symbols = ['  ', 'L', 'E', '1', '$']
scratch_prices = {
    '  ': 0,
    'L': 1,
    'E': 10,
    '1': 1000,
    '$': 100000
}
scratch_weights = [400, 190, 130, 30, 7]
last_msg = None
help_message = """
Match 3 in a row to win.
L - $1
E - $10
1 - $1000
$ - $100,000
"""


@client.event
async def on_ready():
    print('Online.')


@client.event
async def on_message(message):
    command = message.content
    if command[0] != prefix:
        return
    if   does_match_command('lotto', command):
        await scratchoff_sender(message)
    elif does_match_command('help', command):
        await client.send_message(message.channel, help_message)
    elif does_match_command('money', command):
        current_money = get_player_money(message.author.id)
        await client.send_message(message.channel, f'You have: ${current_money}')


def does_match_command(cmd, msg):
    pattern = re.compile('.*'+prefix+'.*'+cmd+'.*')
    if pattern.fullmatch(msg.lower()):
        return True
    return False
    
    
def load_money_file():
    with open('moneys.txt', 'r') as f:
        pinnies = json.load(f)
    return pinnies


def write_money_file(dic):
    with open('moneys.txt', 'w') as f:
        json.dump(dic, f)


# returns a players money, and gives them $10 if new
def get_player_money(pid):
    pid = str(pid)
    dic = load_money_file()
    try:
        return dic[pid]
    except KeyError:
        write_player_money(pid, 10)
        # now they have $10
        return 10


# updates how much money a player has
def write_player_money(pid, money):
    pid = str(pid)
    dic = load_money_file()
    dic[pid] = money
    write_money_file(dic)


async def scratchoff_sender(message):
    # get the scratch off, find the users money
    scratchoff = ScratchOff()
    curr_money = get_player_money(message.author.id)
    outmessage = ''
    # display current money or berate them for overspending
    if curr_money == 0:
        await client.send_message(message.channel, "You're too poor. now going into debt to pay for scratchoffs.\n")
    else:
        outmessage = f'Spent $1 on a ticket. (Now: ${curr_money-1})\n'
    # display scratchoff
    outmessage += scratchoff.get_message_text()
    # add any winnings
    new_money = curr_money - 1 + scratchoff.get_winnings()
    await client.send_message(message.channel, outmessage)
    write_player_money(message.author.id, new_money)

    
class ScratchOff:
    def __init__(self):
        arr = [[], [], []]
        for i in range(3):
            for _ in range(3):
                choice = random.choices(scratch_symbols, scratch_weights, k=1)[0]
                arr[i].append(choice)
        self.arr = arr
        
    def get_message_text(self):
        out = '+------Scratch Off!-------+\n'
        out += '|      $$$                    $$$     |\n'
        out += '|           +-----------+           |\n'
        out += '|           |'
        out += ' ||  ' + self.arr[0][0] + '  ||||  ' + self.arr[0][1] + '  ||||  ' + self.arr[0][2] + '  || '
        out += '|            |\n'
        out += '|           |'
        out += ' ||  ' + self.arr[1][0] + '  ||||  ' + self.arr[1][1] + '  ||||  ' + self.arr[1][2] + '  || '
        out += '|            |\n'
        out += '|           |'
        out += ' ||  ' + self.arr[2][0] + '  ||||  ' + self.arr[2][1] + '  ||||  ' + self.arr[2][2] + '  || '
        out += '|            |\n'
        out += '|           +-----------+           |\n'
        out += '|      $$$                    $$$     |\n'
        out += '+---------------------------+'
        return out
    
    # calculates winnings from this ticket
    def get_winnings(self):
        profit = 0
        for i in range(3):
            # horizontal
            if self.arr[i][0] == self.arr[i][1] == self.arr[i][2]:
                profit += scratch_prices[self.arr[i][0]]
            # vertical
            if self.arr[0][i] == self.arr[1][i] == self.arr[2][i]:
                profit += scratch_prices[self.arr[0][i]]
        # diagonals
        if self.arr[0][0] == self.arr[1][1] == self.arr[2][2]:
            profit += scratch_prices[self.arr[0][0]]
        if self.arr[2][0] == self.arr[1][1] == self.arr[0][2]:
            profit += scratch_prices[self.arr[0][2]]
        return profit


# file is stored in a seperate file (outside the repo).
# This is to keep the key off github
def main():
    try:
        with open(KEY_PATH, 'r') as f:
            key = f.read()
    except OSError:
        print('You forgot to make the keyfile dummy. Make a key.txt one level above the bot')
        return
    client.run(key)

if __name__ == "__main__":
    main()