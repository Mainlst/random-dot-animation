import tkinter as tk
import random
import math
from PIL import Image, ImageTk, ImageDraw, ImageFilter


class RandomDotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ランダムドット")
        self.canvas_width = 1920
        self.canvas_height = 1080
        self.dot_size = 5
        self.num_dots = 200
        self.speed = 3  # 初期速度
        self.min_speed = 3  # 最小速度
        self.max_boost_speed = 30  # キーによる最大速度
        self.mouse_boost_speed = 20  # マウスで弾く際の速さ
        self.mouse_radius = 300  # マウスの影響範囲
        self.max_line_distance = 100
        self.max_connections = 2
        self.color_change_speed = 0.3
        self.blur_radius = 3
        self.fade_opacity = 5
        self.line_segments = 20
        self.boost_decay = 0.9  # 減速率（1未満）

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
        self.speeds = []
        self.target_colors = []
        self.current_colors = []
        for _ in range(self.num_dots):
            x = random.randint(0, self.canvas_width - self.dot_size)
            y = random.randint(0, self.canvas_height - self.dot_size)
            direction = [random.uniform(-1, 1), random.uniform(-1, 1)]
            magnitude = math.hypot(direction[0], direction[1])
            direction = [direction[0] / magnitude, direction[1] / magnitude]

            # 鮮やかな初期色を設定
            initial_color = "#{:02x}{:02x}{:02x}".format(
                random.randint(100, 255),
                random.randint(50, 255),
                random.randint(100, 255),
            )
            target_color = "#{:02x}{:02x}{:02x}".format(
                random.randint(100, 255),
                random.randint(50, 255),
                random.randint(100, 255),
            )
            self.current_colors.append(initial_color)
            self.target_colors.append(target_color)
            self.dots.append({"x": x, "y": y, "direction": direction})
            self.speeds.append(self.speed)

        # スペースキーのイベントをバインド
        self.root.bind("<space>", self.boost_dots)
        # マウスクリックのイベントをバインド
        self.canvas.bind("<Button-1>", self.mouse_boost)

        self.update_canvas()

    def boost_dots(self, event):
        """スペースキーが押されたときに点をランダムな方向に加速"""
        for i in range(len(self.dots)):
            # ランダムな方向に変更
            direction = [random.uniform(-1, 1), random.uniform(-1, 1)]
            magnitude = math.hypot(direction[0], direction[1])
            self.dots[i]["direction"] = [
                direction[0] / magnitude,
                direction[1] / magnitude,
            ]

            # 加速
            self.speeds[i] = self.max_boost_speed

    def mouse_boost(self, event):
        """マウスクリックでカーソル付近の点を弾く"""
        mouse_x, mouse_y = event.x, event.y

        for i, dot in enumerate(self.dots):
            x, y = dot["x"], dot["y"]
            # マウスからの距離を計算
            distance = math.sqrt((mouse_x - x) ** 2 + (mouse_y - y) ** 2)
            if distance <= self.mouse_radius:
                # マウスからの反射方向を計算
                direction = [x - mouse_x, y - mouse_y]
                magnitude = math.hypot(direction[0], direction[1])
                if magnitude != 0:  # ゼロ除算を防止
                    direction = [direction[0] / magnitude, direction[1] / magnitude]
                else:
                    direction = [random.uniform(-1, 1), random.uniform(-1, 1)]
                self.dots[i]["direction"] = direction
                # 加速
                self.speeds[i] = self.mouse_boost_speed

    def update_canvas(self):
        # 透明度を管理するフェードアウトマスクを作成
        fade_mask = Image.new(
            "RGBA",
            (self.canvas_width, self.canvas_height),
            (0, 0, 0, self.fade_opacity),  # 段階的に薄くする透明度
        )

        # 古い軌跡に対してフェードアウトを適用
        self.offscreen_image = Image.alpha_composite(
            Image.new("RGBA", (self.canvas_width, self.canvas_height), "black"),
            self.offscreen_image,
        )
        self.offscreen_image = Image.alpha_composite(self.offscreen_image, fade_mask)

        # 軌跡にブラーを適用
        self.offscreen_image = self.offscreen_image.filter(
            ImageFilter.GaussianBlur(radius=self.blur_radius)
        )

        # 描画用のオフスクリーンバッファ
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
                    random.randint(100, 255),
                    random.randint(50, 255),
                    random.randint(100, 255),
                )

            # ドットの中心を描画
            self.draw.ellipse(
                (x, y, x + self.dot_size, y + self.dot_size),
                fill=(new_r, new_g, new_b, 255),
            )

            centers.append((x + self.dot_size / 2, y + self.dot_size / 2))

            # 壁に当たったら反射
            if (
                x + direction[0] * self.speeds[i] <= 0
                or x + direction[0] * self.speeds[i] + self.dot_size
                >= self.canvas_width
            ):
                direction[0] = -direction[0]
            if (
                y + direction[1] * self.speeds[i] <= 0
                or y + direction[1] * self.speeds[i] + self.dot_size
                >= self.canvas_height
            ):
                direction[1] = -direction[1]

            # 新しい位置を計算
            dot["x"] = max(
                0,
                min(
                    self.canvas_width - self.dot_size,
                    dot["x"] + direction[0] * self.speeds[i],
                ),
            )
            dot["y"] = max(
                0,
                min(
                    self.canvas_height - self.dot_size,
                    dot["y"] + direction[1] * self.speeds[i],
                ),
            )

            # 減速
            self.speeds[i] = max(self.min_speed, self.speeds[i] * self.boost_decay)

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
                    # 点の色を取得
                    color1 = [
                        int(self.current_colors[i][j : j + 2], 16)
                        for j in range(1, 7, 2)
                    ]
                    color2 = [
                        int(self.current_colors[j][j : j + 2], 16)
                        for j in range(1, 7, 2)
                    ]
                    # 線をセグメントに分割して色を補間
                    for k in range(self.line_segments):
                        t = k / (self.line_segments - 1)
                        r = int(color1[0] * (1 - t) + color2[0] * t)
                        g = int(color1[1] * (1 - t) + color2[1] * t)
                        b = int(color1[2] * (1 - t) + color2[2] * t)
                        x_start = x1 + (x2 - x1) * t
                        y_start = y1 + (y2 - y1) * t
                        x_end = x1 + (x2 - x1) * (t + 1 / self.line_segments)
                        y_end = y1 + (y2 - y1) * (t + 1 / self.line_segments)
                        self.draw.line(
                            (x_start, y_start, x_end, y_end),
                            fill=(r, g, b, 255),
                            width=1,
                        )
                    connections[i] += 1
                    connections[j] += 1

        # キャンバスに描画
        self.tk_image = ImageTk.PhotoImage(self.offscreen_image)
        self.canvas.create_image(0, 0, image=self.tk_image, anchor="nw")

        self.root.after(16, self.update_canvas)


if __name__ == "__main__":
    root = tk.Tk()
    app = RandomDotApp(root)
    root.mainloop()
