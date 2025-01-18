import tkinter as tk
import random
import math
from PIL import Image, ImageTk, ImageDraw, ImageFilter


class RandomDotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ランダムドット")
        self.canvas_width = 800
        self.canvas_height = 600
        self.dot_size = 5  # ドットの中心サイズ
        self.glow_size = 0  # 発光エフェクトの広がり
        self.num_dots = 10
        self.speed = 2
        self.max_line_distance = 200
        self.max_connections = 1
        self.color_change_speed = 0.2
        self.bluer_radius = 0.5

        # キャンバスの初期化
        self.canvas = tk.Canvas(
            root, width=self.canvas_width, height=self.canvas_height, bg="black"
        )
        self.canvas.pack()

        # 描画用のオフスクリーンバッファ
        self.offscreen_image = Image.new(
            "RGBA", (self.canvas_width, self.canvas_height), "black"
        )
        self.draw = ImageDraw.Draw(self.offscreen_image)

        # ドット情報を初期化
        self.dots = []
        self.directions = []
        self.target_colors = []
        self.current_colors = []
        for _ in range(self.num_dots):
            x = random.randint(0, self.canvas_width - self.dot_size)
            y = random.randint(0, self.canvas_height - self.dot_size)
            direction = [random.uniform(-1, 1), random.uniform(-1, 1)]
            magnitude = math.hypot(direction[0], direction[1])
            direction = [direction[0] / magnitude, direction[1] / magnitude]

            initial_color = "#{:02x}{:02x}{:02x}".format(
                random.randint(200, 255),
                random.randint(200, 255),
                random.randint(200, 255),
            )
            target_color = "#{:02x}{:02x}{:02x}".format(
                random.randint(200, 255),
                random.randint(200, 255),
                random.randint(200, 255),
            )
            self.current_colors.append(initial_color)
            self.target_colors.append(target_color)
            self.dots.append({"x": x, "y": y, "direction": direction})

        self.update_canvas()

    def update_canvas(self):
        # オフスクリーン画像をクリア
        self.offscreen_image = Image.new(
            "RGBA", (self.canvas_width, self.canvas_height), "black"
        )
        self.draw = ImageDraw.Draw(self.offscreen_image)

        # ドットの中心座標を計算
        centers = []

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
                    random.randint(200, 255),
                    random.randint(200, 255),
                    random.randint(200, 255),
                )

            # ドットを描画（発光効果）
            glow_color = (new_r, new_g, new_b, 50)  # 半透明の色
            for glow_radius in range(self.glow_size, 0, -5):
                alpha = int(255 * (glow_radius / self.glow_size))  # 外側ほど薄く
                self.draw.ellipse(
                    (
                        x - glow_radius,
                        y - glow_radius,
                        x + glow_radius + self.dot_size,
                        y + glow_radius + self.dot_size,
                    ),
                    fill=(new_r, new_g, new_b, alpha),
                )
            # ドットの中心を描画
            self.draw.ellipse(
                (x, y, x + self.dot_size, y + self.dot_size),
                fill=(new_r, new_g, new_b, 255),
            )

            centers.append((x + self.dot_size / 2, y + self.dot_size / 2))

            # 壁に当たったら反射
            if (
                x + direction[0] * self.speed <= 0
                or x + direction[0] * self.speed + self.dot_size >= self.canvas_width
            ):
                direction[0] = -direction[0]  # X方向の反転
            if (
                y + direction[1] * self.speed <= 0
                or y + direction[1] * self.speed + self.dot_size >= self.canvas_height
            ):
                direction[1] = -direction[1]  # Y方向の反転

            # 新しい位置を計算
            dot["x"] = max(
                0,
                min(
                    self.canvas_width - self.dot_size,
                    dot["x"] + direction[0] * self.speed,
                ),
            )
            dot["y"] = max(
                0,
                min(
                    self.canvas_height - self.dot_size,
                    dot["y"] + direction[1] * self.speed,
                ),
            )

        # 線を描画
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
                    self.draw.line((x1, y1, x2, y2), fill="white", width=1)
                    connections[i] += 1
                    connections[j] += 1

        # 描画用画像にブラーを適用
        blurred_image = self.offscreen_image.filter(
            ImageFilter.GaussianBlur(radius=self.bluer_radius)
        )

        # キャンバスに描画
        self.tk_image = ImageTk.PhotoImage(blurred_image)
        self.canvas.create_image(0, 0, image=self.tk_image, anchor="nw")

        self.root.after(20, self.update_canvas)


if __name__ == "__main__":
    root = tk.Tk()
    app = RandomDotApp(root)
    root.mainloop()
