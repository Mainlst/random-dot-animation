import tkinter as tk
import random
import math
from PIL import Image, ImageTk, ImageDraw, ImageFilter


class RandomDotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ランダムドット")
        self.canvas = tk.Canvas(root, width=800, height=600, bg="black")
        self.canvas.pack()

        # 設定パラメータ
        self.num_dots = 10
        self.dot_size = 10
        self.speed = 1
        self.max_line_distance = 200
        self.max_connections = 1
        self.color_change_speed = 0.02

        self.dots = []
        self.directions = []
        self.target_colors = []
        self.current_colors = []

        # 背景画像と描画用画像
        self.background_image = Image.new("RGB", (800, 600), "black")
        self.draw_image = Image.new("RGBA", (800, 600), (0, 0, 0, 0))

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

            self.dots.append({"x": x, "y": y, "direction": direction})

        self.update_canvas()

    def update_canvas(self):
        # 描画用画像をクリア
        self.draw_image = Image.new("RGBA", (800, 600), (0, 0, 0, 0))
        draw = ImageDraw.Draw(self.draw_image)

        # ドットの更新と描画
        for i, dot in enumerate(self.dots):
            x, y = dot["x"], dot["y"]
            direction = dot["direction"]

            # 色を連続的に変化
            current_r, current_g, current_b = [
                int(self.current_colors[i][j : j + 2], 16) for j in range(1, 7, 2)
            ]
            target_r, target_g, target_b = [
                int(self.target_colors[i][j : j + 2], 16) for j in range(1, 7, 2)
            ]
            new_r = int(current_r + (target_r - current_r) * self.color_change_speed)
            new_g = int(current_g + (target_g - current_g) * self.color_change_speed)
            new_b = int(current_b + (target_b - current_b) * self.color_change_speed)

            self.current_colors[i] = "#{:02x}{:02x}{:02x}".format(new_r, new_g, new_b)
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

            # ドットを描画
            dot_color = (new_r, new_g, new_b, 255)
            draw.ellipse((x, y, x + self.dot_size, y + self.dot_size), fill=dot_color)

            # 壁に当たったら反射
            if (
                x + direction[0] * self.speed <= 0
                or x + direction[0] * self.speed + self.dot_size >= 800
            ):
                direction[0] *= -1
            if (
                y + direction[1] * self.speed <= 0
                or y + direction[1] * self.speed + self.dot_size >= 600
            ):
                direction[1] *= -1

            # 新しい位置を計算
            dot["x"] += direction[0] * self.speed
            dot["y"] += direction[1] * self.speed

        # 描画用画像にブラーを適用
        blurred_image = self.draw_image.filter(ImageFilter.GaussianBlur(radius=2))

        # キャンバスに描画
        combined_image = Image.alpha_composite(
            Image.new(
                "RGBA",
                self.background_image.size,
                self.background_image.getpixel((0, 0)),
            ),
            blurred_image,
        )
        self.tk_image = ImageTk.PhotoImage(combined_image)
        self.canvas.create_image(0, 0, image=self.tk_image, anchor="nw")

        self.root.after(20, self.update_canvas)


if __name__ == "__main__":
    root = tk.Tk()
    app = RandomDotApp(root)
    root.mainloop()
