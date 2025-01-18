from io import BytesIO
import tkinter as tk
import random
import math
from PIL import Image, ImageTk, ImageFilter


class RandomDotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ランダムドット")
        self.canvas = tk.Canvas(root, width=800, height=600, bg="black")
        self.canvas.pack()

        # 設定パラメータ
        self.num_dots = 10
        self.dot_size = 5
        self.speed = 1
        self.max_line_distance = 200
        self.max_connections = 1
        self.color_change_speed = 0.02

        self.dots = []
        self.directions = []
        self.target_colors = []
        self.current_colors = []

        for _ in range(self.num_dots):
            x = random.randint(0, 800 - self.dot_size)
            y = random.randint(0, 600 - self.dot_size)
            direction = [random.uniform(-1, 1), random.uniform(-1, 1)]
            magnitude = math.hypot(direction[0], direction[1])
            direction = [direction[0] / magnitude, direction[1] / magnitude]

            initial_color = "#{:02x}{:02x}{:02x}".format(
                random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)
            )
            target_color = "#{:02x}{:02x}{:02x}".format(
                random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)
            )
            self.current_colors.append(initial_color)
            self.target_colors.append(target_color)

            dot = self.canvas.create_oval(
                x,
                y,
                x + self.dot_size,
                y + self.dot_size,
                fill=initial_color,
                outline=initial_color,
            )
            self.dots.append(dot)
            self.directions.append(direction)

        self.move_dots()

    def move_dots(self):
        self.canvas.delete("line")
        centers = []

        for dot in self.dots:
            x1, y1, x2, y2 = self.canvas.coords(dot)
            centers.append(((x1 + x2) / 2, (y1 + y2) / 2))

        for i, dot in enumerate(self.dots):
            current_r, current_g, current_b = [
                int(self.current_colors[i][j : j + 2], 16) for j in range(1, 7, 2)
            ]
            target_r, target_g, target_b = [
                int(self.target_colors[i][j : j + 2], 16) for j in range(1, 7, 2)
            ]

            new_r = int(current_r + (target_r - current_r) * self.color_change_speed)
            new_g = int(current_g + (target_g - current_g) * self.color_change_speed)
            new_b = int(current_b + (target_b - current_b) * self.color_change_speed)

            new_color = "#{:02x}{:02x}{:02x}".format(new_r, new_g, new_b)
            self.current_colors[i] = new_color
            self.canvas.itemconfig(dot, fill=new_color, outline=new_color)

            if (
                abs(new_r - target_r) < 5
                and abs(new_g - target_g) < 5
                and abs(new_b - target_b) < 5
            ):
                self.target_colors[i] = "#{:02x}{:02x}{:02x}".format(
                    random.randint(0, 255),
                    random.randint(0, 255),
                    random.randint(0, 255),
                )

        connections = {i: 0 for i in range(len(centers))}
        for i in range(len(centers)):
            for j in range(i + 1, len(centers)):
                if (
                    connections[i] >= self.max_connections
                    or connections[j] >= self.max_connections
                ):
                    continue
                x1, y1 = centers[i]
                x2, y2 = centers[j]
                dist = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
                if dist <= self.max_line_distance:
                    self.canvas.create_line(x1, y1, x2, y2, fill="white", tags="line")
                    connections[i] += 1
                    connections[j] += 1

        for i, dot in enumerate(self.dots):
            x1, y1, x2, y2 = self.canvas.coords(dot)
            direction = self.directions[i]
            new_x1 = x1 + direction[0] * self.speed
            new_x2 = x2 + direction[0] * self.speed
            new_y1 = y1 + direction[1] * self.speed
            new_y2 = y2 + direction[1] * self.speed

            if new_x1 <= 0 or new_x2 >= 800:
                direction[0] *= -1
            if new_y1 <= 0 or new_y2 >= 600:
                direction[1] *= -1

            self.canvas.move(dot, direction[0] * self.speed, direction[1] * self.speed)

        self.apply_blur()
        self.root.after(20, self.move_dots)

    def apply_blur(self):
        ps = self.canvas.postscript(colormode="color")
        img = Image.open(BytesIO(ps.encode("utf-8")))
        blurred = img.filter(ImageFilter.GaussianBlur(radius=2))
        self.blurred_image = ImageTk.PhotoImage(blurred)
        self.canvas.create_image(0, 0, image=self.blurred_image, anchor="nw")
        for dot in self.dots:
            self.canvas.tag_raise(dot)
        self.canvas.tag_raise("line")


if __name__ == "__main__":
    root = tk.Tk()
    app = RandomDotApp(root)
    root.mainloop()
