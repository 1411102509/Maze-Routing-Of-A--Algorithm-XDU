import time
import numpy as np

# 单元格类型
# 0 - 路，1 - 墙，2-走过的路，3-死胡同，4-拓展过的节点
class CellType:
    ROAD = 0    # 路
    WALL = 1    # 墙
    WALKED = 2  # 走过的路
    DEAD = 3    # 死路
    EXPAND = 4  # 拓展过的节点


# 墙的方向
class Direction:
    LEFT = 0,
    UP = 1,
    RIGHT = 2,
    DOWN = 3,


def neighbors(maze, pos):
    x, y = pos
    t, r, d, l = valid(maze, x, y - 1), valid(maze, x + 1, y), valid(maze, x, y + 1), valid(maze, x - 1, y)
    return t, r, d, l

def valid(maze, x, y):
    if x < 0 or y < 0:
        return False
    if x >= len(maze) or y >= len(maze):
        return False
    val = maze[y][x]
    if val == CellType.WALL or val == CellType.DEAD:
        return False
    return val, x, y


def mark_walked(maze, pos):
    maze[pos[1]][pos[0]] = CellType.WALKED


def mark_dead(maze, pos):
    maze[pos[1]][pos[0]] = CellType.DEAD

def mark_expand(maze, pos):
    maze[pos[1]][pos[0]] = CellType.EXPAND

def suggest_pos(cells):
    arr = []
    for cell in cells:
        if cell:    #路
            arr.append(cell[0])
        else:       #死胡同
            arr.append(CellType.DEAD)
    return cells[arr.index(min(arr))]       #改这里

def expand_Note(MAZE,EXIT,OPEN,CLOSED,COST,expNote):
    t, r, d, l = neighbors(MAZE, expNote)
    for cell in (t, r, d, l):
        if cell:     #路,可以拓展
            notePos = [cell[1],cell[2]]
            if notePos not in CLOSED:
                COST[notePos[0]][notePos[1]].parentNote = expNote

                COST[notePos[0]][notePos[1]].G = COST[expNote[0]][expNote[1]].G + 1
                COST[notePos[0]][notePos[1]].H = abs(EXIT[0]-notePos[0]) + abs(EXIT[1]-notePos[1])
                COST[notePos[0]][notePos[1]].F = COST[notePos[0]][notePos[1]].G + COST[notePos[0]][notePos[1]].H

                OPEN.append(notePos)

def find_Expend_Note(OPEN,COST):
    minCost_F = 1024
    minCost_H = 1024
    minCost_Pos = [0,0]
    minCost_index = 0

    index = 0
    for note in OPEN:    #寻找OPEN表中代价最小的节点
        index += 1
        if COST[note[0]][note[1]].F < minCost_F:        #代价不同，取最小代价节点
            minCost_F = COST[note[0]][note[1]].F
            minCost_Pos = note
            minCost_index = index-1
        if COST[note[0]][note[1]].F == minCost_F:       #如果代价相同，则寻找到终点距离最近的节点
            if COST[note[0]][note[1]].H <= minCost_H:   #如果都相同，则取最后生成的节点
                minCost_F = COST[note[0]][note[1]].F
                minCost_Pos = note
                minCost_index = index-1
    return minCost_Pos,minCost_index


class Note():
    def __init__(self,f,g,h):
        self.F = f  #总代价
        self.G = g  #移动代价
        self.H = h  #该节点到终点的移动成本
        self.parentNote = []
    def print(self):
        print("F = ",self.F,"，G = ",self.G,
              "，H = ",self.H,"，parentNote = ",self.parentNote)

# A*算法寻路
def solve_maze(MAZE,ENTRANCE,EXIT,callback):
    #初始化OPEN表、CLOSED表和代价函数
    COST = []
    OPEN = [ENTRANCE]
    CLOSED = []
    for y in range(len(MAZE)):
        COST.append([])
        for x in range(len(MAZE)):
            if MAZE[y][x] == CellType.WALL:
                COST[y].append(Note(1024,1024,1024))
            else:
                COST[y].append(Note(0,0,0))
            # print("[",y,",",x,"] ",COST[y][x].F)

    #计算初始节点代价    
    COST[ENTRANCE[0]][ENTRANCE[1]].G = 0
    COST[ENTRANCE[0]][ENTRANCE[1]].H = abs(EXIT[0]-ENTRANCE[0]) + abs(EXIT[1]-ENTRANCE[1])
    COST[ENTRANCE[0]][ENTRANCE[1]].F = COST[ENTRANCE[0]][ENTRANCE[1]].G + COST[ENTRANCE[0]][ENTRANCE[1]].H
 
    #迭代拓展节点
    expNote = ENTRANCE
    while expNote != EXIT:
        time.sleep(0.005)
        #寻找待扩展节点
        expNote,index = find_Expend_Note(OPEN,COST) 
        OPEN.pop(index)             #移除OPEN表
        CLOSED.append(expNote)      #放入CLOSED表

        # print("扩展的节点：",expNote)
        #绘制图像
        mark_dead(MAZE,expNote)
        for open_note in OPEN:
            mark_expand(MAZE,open_note)
        callback(MAZE,(CellType.WALKED,expNote[0],expNote[1]))

        #拓展节点
        # COST[expNote[0]][expNote[1]].print()
        expand_Note(MAZE,EXIT,OPEN,CLOSED,COST,expNote)
        # print("扩展后的OPEN表：\n",np.array(OPEN))
        # print("扩展后的CLOSED表：\n",np.array(CLOSED),"\n\n")
    parent = EXIT
    mark_walked(MAZE,EXIT)
    road_list = [EXIT]
    while parent != ENTRANCE:
        parent = COST[parent[0]][parent[1]].parentNote
        road_list.insert(0,parent)

        mark_walked(MAZE,parent)
        callback(MAZE,(CellType.WALKED,parent[0],parent[1]))
   
    print(np.array(MAZE))
    print("exit:",EXIT)
    print("result:\n",np.array(road_list))

# #有路就走，没路就掉头 算法寻路
# def solve_maze(maze, pos, end, callback):
#     time.sleep(0.005)
#     # 到达出口
#     if pos[0] == end[0] and pos[1] == end[1]:
#         mark_walked(maze, pos)
#         return True
#     # 获取相邻4个位置
#     t, r, d, l = neighbors(maze, pos)
#     next_pos = suggest_pos((t, r, d, l))
#     if next_pos:
#         if next_pos[0] == CellType.WALKED:
#             mark_dead(maze, pos)
#         else:
#             mark_walked(maze, pos)
#         callback(maze, next_pos)
#         return solve_maze(maze, (next_pos[1], next_pos[2]), end, callback)
#     else:
#         mark_dead(maze, pos)
#         callback(maze, next_pos)
#         return False