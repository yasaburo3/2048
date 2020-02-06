# -*- coding: utf-8 -*-
#curses 用来在终端上显示图形界面
import curses
#random用来生成随机数
from random import randrange, choice
#collection提供了字典的子类defaultdict
from collections import defaultdict

actions = ['Up','Left','Down','Right','Restart','Exit']

#ord函数返回参数对应的ASCII数值
letter_codes = [ord(ch) for ch in 'WASDRQwasdrq']

#将输入与行为对应
actions_dict = dict(zip(letter_codes, actions * 2))

#print(actions_dict)



def get_user_action(keyboard):
    char = 'N'
    while char not in actions_dict:
        #返回按下键值的 ASCII 码值
        char = keyboard.getch()
    #返回输入键位对应的行为
    return actions_dict[char]

#矩阵转置
def transpose(field):
    return [list(row) for row in zip(*field)]

#矩阵逆转
def invert(field):
    return [row[::-1] for row in field]

class GameField(object):
    def __init__(self, height=4, width=4, win=2048):
        self.height = height    #高
        self.width = width      #宽
        self.win_value = win    #过关分数
        self.score = 0          #当前分数
        self.highscore = 0      #最高分
        self.reset()            #棋盘重置

    def reset(self):
        #更新分数
        if self.score > self.highscore:
            self.highscore = self.score
        self.score = 0
        #初始化游戏开始界面:
        self.field = [[0 for i in range(self.width)] for j in range(self.height)]
        self.spawn()
        self.spawn()

    def move(self,direction):
        def move_row_left(row):
            def tighten(row):
                #把零散的非零单元挤在一起
                #先将非零元素全拿出来加入新列表
                new_row = [i for i in row if i != 0]
                #按照原列表的大小，给新列表补零
                new_row += [0 for i in range(len(row) - len(new_row))]
                return  new_row

            def merge (row):
                #对临近元素进行合并
                pair = False
                new_row = []
                for i in range(len(row)):
                    if pair:
                        #合并后，在0元素后面加入乘2后的元素
                        new_row.append(2 * row[i])
                        #更新分数
                        self.score += 2 * row[i]
                        pair = False
                    else:
                        #判断临近元素是否能合并
                        if i + 1 < len(row) and row[i] == row[i + 1]:
                            pair = True
                            #可以合并时，新列表加入元素0
                            new_row.append(0)
                        else:
                            #不能合并，新列表中加入该元素
                            new_row.append(row[i])
                assert len(new_row) == len(row)
                return new_row
    
            return tighten(merge(tighten(row)))
    
        moves = {}
        moves['Left'] = lambda field: [move_row_left(row) for row in field]
        moves['Right'] = lambda field: invert(moves['Left'](invert(field)))
        moves['Up'] = lambda field: transpose(moves['Left'](transpose(field)))
        moves['Down'] = lambda field: transpose(moves['Right'](transpose(field)))
        #判断棋盘操作是否存在且可行
        if direction in moves:
            if self.move_is_possible(direction):
                self.field = moves[direction](self.field)
                self.spawn()
                return True
            else:
                return False

    def is_win(self):
        #任意一个位置的数大于设定的值时，游戏胜利
        return any(any(i >= self.win_value for i in row) for row in self.field)

    def is_gameover(self):
        #无法移动和合并时，游戏失败
        return not any (self.move_is_possible(move) for move in actions)

    def draw(self,screen):
        help_string1 = '(W)Up (S)Down (A)Left (D)Right'
        help_string2 = '(R)Restart (Q)Exit'
        gameover_string = '         GAMEOVER'
        win_string = '          YOU WIN!'

        #绘制函数
        def cast(string):
            # addstr()方法将内容展示到终端
            screen.addstr(string + '\n')

        #绘制水平分割线的函数
        def draw_hor_separator():
            line = '+' + ('+------' * self.width + '+')[1:]
            cast(line)

        #绘制竖直分割线的函数
        def draw_row(row):
            cast(''.join('|{: ^5} '.format(num) if num > 0 else '|      ' for num in row) + '|')
            ###此处为format的用法，{: ^5}表示最大宽度是5，^表示居中显示，<或默认表示左对齐，>表示右对齐
        
        #清空屏幕
        screen.clear()
        #绘制分数和最高分
        cast('SCORE: ' + str(self.score))
        if 0 != self.highscore:
            cast('HIGHSCORE: ' + str(str.highscore))

        #绘制行列边框分割线
        for row in self.field:
            draw_hor_separator()
            draw_row(row)
        draw_hor_separator()

        #绘制提示文字
        if self.is_win():
            cast(win_string)
        else:
            if self.is_gameover():
                cast(gameover_string)
            else:
                cast(help_string1)
        cast(help_string2)

    #随机生成一个2或4
    def spawn(self):
        #从100中取一个随机数，若这个数大于89，则生成4
        #否则生成2
        new_element = 4 if randrange(100) > 89 else 2
        #得到一个随机空白位置的坐标
        (i,j) = choice([(i,j) for i in range(self.width) for j in range(self.height) if self.field[i][j] == 0])
        self.field[i][j] = new_element

    def move_is_possible(self, direction):
        '''传入要移动的方向
        判断能否向这个方向移动
        '''
        def row_is_left_movable(row):
            '''判断一行里面能否有元素进行左移动或合并
            '''
            def change(i):
                #当左边有空位0，右边有数字时，可以向左移动
                if row[i] == 0 and row[i + 1] != 0:
                    return True
                #当左边有一个数和右边数相等时，可以向左合并
                if row[i] != 0 and row[i] == row[i + 1]:
                    return True
                return False
            return any(change(i) for i in range(len(row) - 1))

        #检查能否移动或合并
        check = {}
        check['Left'] = lambda field: any(row_is_left_movable(row) for row in field)
        check['Right'] = lambda field: check['Left'](invert(field))
        check['Up'] = lambda field: check ['Left'](transpose(field))
        check['Down'] = lambda field: check['Right'](transpose(field))

        #如果 direction 是'左右上下'中的操作，那就执行对应的动作
        if direction in check:
            return check[direction](self.field)
        else:
            return False


def main(stdscr):
    def init():
        #初始化游戏棋盘
        game_field.reset()
        return 'Game'

    def not_game(state):
        #显示游戏结束界面
        game_field.draw(stdscr)
        #读取用户的动作，判断是重启游戏还是结束游戏
        action = get_user_action(stdscr)

        responses = defaultdict(lambda: state)
        responses['Restart'] = 'Init'
        responses['Exit'] = 'Exit'
        return responses[action]

    def game():
        #画出当前棋盘状态
        game_field.draw(stdscr)
        #读取用户输入的action
        action = get_user_action(stdscr)
        
        if action == 'Restart':
            return 'Init'
        if action == 'Exit':
            return 'Exit'
        #移动一步以后要判断游戏状态
        if game_field.move(action):
            if game_field.is_win():
                return 'Win'
            if game_field.is_gameover():
                return 'Gameover'
        #继续游戏，返回游戏中的状态
        return 'Game'

    state_action = {
        'Init': init,
        'Win': lambda: not_game('Win'),
        'Gameover': lambda: not_game('Gameover'),
        'Game': game
    }

    #使用颜色配置默认值
    curses.use_default_colors()

    #实例化游戏界面对象并设置游戏获胜条件为2048
    game_field = GameField(win=2048)

    state = 'Init'

    #状态机开始循环
    while state != 'Exit':
        state = state_action[state]()

curses.wrapper(main)
