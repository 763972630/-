import tkinter as tk
from tkinter import messagebox
import random
import os
import ctypes

# 定义 Windows 输入法相关 API [2]()
user32 = ctypes.windll.user32
HKL_NEXT = 1
ENGLISH_LANGID = 0x0409


def force_english_input():
    """强制切换为英文输入法"""
    hwnd = user32.GetForegroundWindow()
    current_layout = user32.GetKeyboardLayout(0)
    if (current_layout & 0xFFFF) != ENGLISH_LANGID:
        user32.LoadKeyboardLayoutW("00000409", 1)
        user32.PostMessageW(hwnd, 0x0050, 0, ENGLISH_LANGID)


SCORE_FILE = "snake_scores.txt"

if not os.path.exists(SCORE_FILE):
    with open(SCORE_FILE, "w") as f:
        pass


def save_score(score):
    try:
        if os.path.exists(SCORE_FILE):
            with open(SCORE_FILE, "r") as f:
                scores = [int(line.strip()) for line in f if line.strip()]
        else:
            scores = []
        scores.append(score)
        scores = sorted(scores, reverse=True)[:100]
        with open(SCORE_FILE, "w") as f:
            f.write("\n".join(map(str, scores)))
    except Exception as e:
        print(f"保存分数错误: {e}")


def get_top3_scores():
    try:
        if os.path.exists(SCORE_FILE):
            with open(SCORE_FILE, "r") as f:
                scores = [int(line.strip()) for line in f if line.strip()]
                unique_scores = sorted(set(scores), reverse=True)
                scores = unique_scores[:3]
                return scores + [0] * (3 - len(scores))  # 修复此处语法错误
        else:
            return [0, 0, 0]
    except Exception as e:
        print(f"读取分数错误: {e}")
        return [0, 0, 0]


class Snake:
    def __init__(self, canvas):
        self.canvas = canvas
        self.reset()

    def reset(self):
        self.body = [[600, 400]]  # 初始位置居中
        self.direction = "RIGHT"
        self.last_direction = "RIGHT"
        self.dead = False
        self.score = 0
        self.wall_pass = False
        self.spawn_food()
        self.canvas.delete("all")
        self.draw()

    def spawn_food(self):
        while True:
            x = random.randrange(0, 1200, 20)
            y = random.randrange(0, 800, 20)
            if [x, y] not in self.body:  # 修复此处拼写错误
                self.food_pos = [x, y]
                break

    def move(self):
        if self.dead:
            return
        head = self.body[-1].copy()
        if self.direction == "RIGHT":
            head[0] += 20
        elif self.direction == "LEFT":
            head[0] -= 20
        elif self.direction == "UP":
            head[1] -= 20
        elif self.direction == "DOWN":
            head[1] += 20

        if self.wall_pass:
            head[0] = head[0] % 1200
            head[1] = head[1] % 800
        else:
            if head[0] < 0 or head[0] >= 1200 or head[1] < 0 or head[1] >= 800:
                self.dead = True

        if head in self.body:
            self.dead = True

        if self.dead:
            messagebox.showinfo(" 游戏结束", f"最终得分: {self.score}\n 按R键重新开始")
            save_score(self.score)
            return

        self.body.append(head)
        if head == self.food_pos:
            self.score += 10
            self.spawn_food()
        else:
            self.body.pop(0)

        self.last_direction = self.direction
        self.draw()

    def draw(self):
        self.canvas.delete("all")
        # 绘制蛇的身体（除头部）
        for pos in self.body[:-1]:
            self.canvas.create_rectangle(pos[0], pos[1], pos[0] + 20, pos[1] + 20, fill="green")
        # 绘制蛇的头部，使用黄色填充
        head_pos = self.body[-1]
        self.canvas.create_rectangle(head_pos[0], head_pos[1], head_pos[0] + 20, head_pos[1] + 20, fill="yellow")

        self.canvas.create_rectangle(self.food_pos[0], self.food_pos[1],
                                     self.food_pos[0] + 20, self.food_pos[1] + 20, fill="red")

        top3 = get_top3_scores()
        self.canvas.create_text(600, 20, text=f"得分: {self.score}     历史最高: {max(top3)}",
                                fill="white", font=('微软雅黑', 14))
        self.canvas.create_text(1100, 50, text="历史前三:", fill="white",
                                font=('微软雅黑', 12), anchor=tk.E)
        for i, score in enumerate(top3[:3]):
            self.canvas.create_text(1100, 80 + i * 30, text=f"{i + 1}. {score}",
                                    fill="white", anchor=tk.E)
        self.canvas.create_text(1100, 780, text=f" 穿墙模式(小写g切换): {'开启' if self.wall_pass else '关闭'}",
                                fill="white", anchor=tk.E)


def main():
    root = tk.Tk()
    root.title(" 贪吃蛇 - 老江")

    # 获取屏幕的宽度和高度
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # 定义窗口的宽度和高度
    window_width = 1200
    window_height = 800

    # 计算窗口左上角的坐标
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2

    # 设置窗口的位置和大小
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    canvas = tk.Canvas(root, width=1200, height=800, bg="black")
    canvas.pack()

    snake = Snake(canvas)

    def on_key_press(event):
        force_english_input()  # 每次按键都强制英文输入法
        key = event.keysym
        if key == 'q':
            root.destroy()
        elif key == 'r' and snake.dead:
            snake.reset()
        elif key == 'g':
            snake.wall_pass = not snake.wall_pass
            snake.draw()
        elif not snake.dead:
            if key in ['Up', 'w'] and snake.last_direction != "DOWN":
                snake.direction = "UP"
            elif key in ['Down', 's'] and snake.last_direction != "UP":
                snake.direction = "DOWN"
            elif key in ['Left', 'a'] and snake.last_direction != "RIGHT":
                snake.direction = "LEFT"
            elif key in ['Right', 'd'] and snake.last_direction != "LEFT":
                snake.direction = "RIGHT"

    root.bind("<Key>", on_key_press)

    def game_loop():
        snake.move()
        root.after(100, game_loop)

    game_loop()
    root.mainloop()


if __name__ == "__main__":
    main()