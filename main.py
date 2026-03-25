import customtkinter as ctk
from tkinter import filedialog, messagebox, PhotoImage # 引入 PhotoImage
from PIL import Image, ImageTk # 新增引入 PIL 库
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import re
import random
import sys
import os

# === 新增：PyInstaller 资源路径解析黑科技 ===
def resource_path(relative_path):
    """获取资源的绝对路径，兼容开发环境和 PyInstaller 打包环境"""
    try:
        # PyInstaller 打包后会将资源释放到 sys._MEIPASS 的临时目录中
        base_path = sys._MEIPASS
    except Exception:
        # 开发环境下，直接使用当前绝对路径
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
# ============================================

# ================== 核心配置区域 ==================
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# 字体防乱码设置 (跨平台支持中英文)
support_fonts = ['Microsoft YaHei', 'SimHei', 'PingFang SC', 'Heiti TC', 'Arial Unicode MS']
for font in support_fonts:
    try:
        plt.rcParams['font.sans-serif'] = [font]
        break
    except Exception:
        continue
plt.rcParams['axes.unicode_minus'] = False

# 中文颜色映射 (英文如 'red' 会被 matplotlib 原生支持)
COLOR_MAPPING = {
    '蓝色': '#5B9BD5', '绿色': '#70AD47', '黄褐色': '#ED7D31', '橙色': '#ED7D31',
    '亮黄色': '#FFC000', '黄色': '#FFC000', '红色': '#FF0000', '紫色': '#7030A0',
    '灰色': '#A6A6A6', '粉色': '#FF99CC', '青色': '#00B0F0', '黑色': '#000000', '白色': '#FFFFFF'
}

# ================== 国际化 (i18n) 语言包 ==================
LANGUAGES = {
    "zh": {
        "app_title": "万象数图",
        "left_title": "📝 智能解析区",
        "left_desc": "支持识别 [柱状图/折线图等]\n格式：项目名称：数值+单位（颜色）",
        "btn_parse": "✨ 智能解析并预览",
        "right_title": "📊 图表实时预览",
        "lbl_type": "图表类型:",
        "lbl_zoom": "图表缩放:",
        "lbl_font": "标签字号:",
        "lbl_x": "图例左右 (X):",
        "lbl_y": "图例上下 (Y):",
        "btn_save": "💾 保存图表到本地",
        "types": ["饼状图", "柱状图", "条形图", "折线图"],
        "chart_total": "总计",
        "chart_legend": "数据明细",
        "msg_empty": "文本框为空，请先输入内容。",
        "msg_fail_t": "解析失败",
        "msg_fail_d": "未识别到符合格式的有效数据。",
        "msg_save_s": "图表已成功保存！",
        "examples": {
            0: "我的二月份财务复盘\n总支出：8600元（这行不解析）\n餐饮开销：3200元（红色） \n房租水电：2800元（蓝色） \n交通出行：650.5元（绿色） \n服饰购物：1200元（橙色） \n娱乐交友：750元（亮黄色）",
            1: "各部门第一季度业绩统计\n无用信息不解析\n销售部：120w（红色）\n市场部：85w（蓝色）\n技术部：150w（绿色）\n运营部：90w（橙色）",
            2: "2024年最受欢迎编程语言\nPython：85分（蓝色）\nJava：70分（橙色）\nC++：60分（绿色）\nJavaScript：80分（亮黄色）",
            3: "某产品近半年活跃用户数走势\n1月份：100人（蓝色）\n2月份：150人（橙色）\n3月份：120人（绿色）\n4月份：200人（红色）\n5月份：250人（紫色）\n6月份：230人（亮黄色）"
        }
    },
    "en": {
        "app_title": "OmniChart",
        "left_title": "📝 Smart Parsing Area",
        "left_desc": "Auto-detects [Bar/Line Chart] etc.\nFormat: Item: Value+Unit (Color)",
        "btn_parse": "✨ Parse & Preview",
        "right_title": "📊 Real-time Preview",
        "lbl_type": "Chart Type:",
        "lbl_zoom": "Chart Zoom:",
        "lbl_font": "Font Size:",
        "lbl_x": "Legend Pos (X):",
        "lbl_y": "Legend Pos (Y):",
        "btn_save": "💾 Save Chart Locally",
        "types": ["Pie Chart", "Bar Chart", "H-Bar Chart", "Line Chart"],
        "chart_total": "Total",
        "chart_legend": "Data Details",
        "msg_empty": "Textbox is empty. Please input data.",
        "msg_fail_t": "Parsing Failed",
        "msg_fail_d": "No valid data format recognized.",
        "msg_save_s": "Chart saved successfully!",
        "examples": {
            0: "My February Financial Review\nTotal: $8600 (Ignored)\nFood: 3200$ (red) \nRent: 2800$ (blue) \nTransport: 650.5$ (green) \nShopping: 1200$ (orange) \nEntertainment: 750$ (gold)",
            1: "Q1 Department Performance\nIgnore this line\nSales: 120k (red)\nMarketing: 85k (blue)\nTech: 150k (green)\nOps: 90k (orange)",
            2: "Most Popular Programming Languages 2024\nPython: 85pts (blue)\nJava: 70pts (orange)\nC++: 60pts (green)\nJavaScript: 80pts (gold)",
            3: "Active Users Trend - Last 6 Months\nJan: 100 users (blue)\nFeb: 150 users (orange)\nMar: 120 users (green)\nApr: 200 users (red)\nMay: 250 users (purple)\nJun: 230 users (gold)"
        }
    }
}


class UniversalChartApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # 默认语言设定
        self.lang = "zh"
        self.texts = LANGUAGES[self.lang]

        self.title(self.texts["app_title"])

        # ==========================================
        # === 核心修改区：使用 iconphoto 强制设置图标 ===
        # ==========================================
        try:
            icon_path = resource_path("app_icon.ico")
            # 1. 使用 PIL 打开图标文件（兼容性更强）
            icon_image = Image.open(icon_path)
            # 2. 转换为 tkinter 可以识别的 PhotoImage 格式
            icon_photo = ImageTk.PhotoImage(icon_image)
            # 3. 强制设置为窗口和任务栏的图标
            # 参数 True 表示同时应用到该窗口产生的所有子窗口（例如弹窗）
            self.iconphoto(True, icon_photo)

            # 为了防止被垃圾回收器回收导致图标丢失，将其绑定在实例上
            self._icon_photo = icon_photo

            # 备用方案：如果上面的失败了，再尝试一次旧方法
            self.iconbitmap(icon_path)
        except Exception as e:
            print(f"Icon loaded failed. Error: {e}")
        # ==========================================

        self.geometry("1150x750")
        self.minsize(1050, 650)

        self.parsed_data = {}
        self.parsed_colors = {}
        self.extracted_title = ""
        self.primary_unit = ""
        self.current_type_idx = 0

        self.fig = None
        self.ax = None
        self.canvas = None

        self.setup_ui()
        self.init_static_canvas()

    def setup_ui(self):
        # --- 左侧面板 ---
        self.left_frame = ctk.CTkFrame(self, width=380, corner_radius=15)
        self.left_frame.pack(side="left", fill="y", padx=20, pady=20)
        self.left_frame.pack_propagate(False)

        # 语言切换组件
        self.lang_switch = ctk.CTkSegmentedButton(
            self.left_frame,
            values=["中文", "English"],
            command=self.change_language
        )
        self.lang_switch.set("中文")
        self.lang_switch.pack(pady=(15, 0), padx=20, fill="x")

        self.ui_title_left = ctk.CTkLabel(self.left_frame, text=self.texts["left_title"], font=("Arial", 20, "bold"))
        self.ui_title_left.pack(pady=(15, 5))

        text_color = "black" if ctk.get_appearance_mode() == "Light" else "white"
        self.ui_desc_left = ctk.CTkLabel(self.left_frame, text=self.texts["left_desc"], text_color=text_color,
                                         font=("Arial", 12))
        self.ui_desc_left.pack(pady=(0, 10))

        self.textbox = ctk.CTkTextbox(self.left_frame, height=360, corner_radius=10, font=("Arial", 14))
        self.textbox.pack(fill="x", padx=20, pady=10)
        self.textbox.insert("0.0", self.texts["examples"][self.current_type_idx])

        self.btn_parse = ctk.CTkButton(self.left_frame, text=self.texts["btn_parse"], font=("Arial", 14, "bold"),
                                       height=40, command=self.parse_and_preview)
        self.btn_parse.pack(pady=10, padx=20, fill="x")

        # --- 右侧面板 ---
        self.right_frame = ctk.CTkFrame(self, corner_radius=15)
        self.right_frame.pack(side="right", fill="both", expand=True, padx=(0, 20), pady=20)

        self.ui_title_right = ctk.CTkLabel(self.right_frame, text=self.texts["right_title"], font=("Arial", 20, "bold"))
        self.ui_title_right.pack(pady=(15, 5))

        self.control_frame = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        self.control_frame.pack(fill="x", padx=10, pady=(0, 5))

        row1 = ctk.CTkFrame(self.control_frame, fg_color="transparent")
        row1.pack(fill="x", pady=5)

        self.ui_lbl_type = ctk.CTkLabel(row1, text=self.texts["lbl_type"], font=("Arial", 12, "bold"))
        self.ui_lbl_type.pack(side="left", padx=(0, 5))

        self.chart_type_var = ctk.StringVar(value=self.texts["types"][self.current_type_idx])
        self.chart_type_dropdown = ctk.CTkOptionMenu(
            row1, variable=self.chart_type_var, values=self.texts["types"], command=self.on_chart_type_change, width=100
        )
        self.chart_type_dropdown.pack(side="left", padx=(0, 20))

        self.ui_lbl_zoom = ctk.CTkLabel(row1, text=self.texts["lbl_zoom"], font=("Arial", 12, "bold"))
        self.ui_lbl_zoom.pack(side="left", padx=(0, 5))
        self.pie_size_slider = ctk.CTkSlider(row1, from_=0.5, to=1.6, width=120, command=self.on_slider_change)
        self.pie_size_slider.set(1.0)
        self.pie_size_slider.pack(side="left", padx=(0, 20))

        self.ui_lbl_font = ctk.CTkLabel(row1, text=self.texts["lbl_font"], font=("Arial", 12, "bold"))
        self.ui_lbl_font.pack(side="left", padx=(0, 5))
        self.font_size_slider = ctk.CTkSlider(row1, from_=8, to=18, width=120, command=self.on_slider_change)
        self.font_size_slider.set(10)
        self.font_size_slider.pack(side="left")

        row2 = ctk.CTkFrame(self.control_frame, fg_color="transparent")
        row2.pack(fill="x", pady=5)

        self.ui_lbl_x = ctk.CTkLabel(row2, text=self.texts["lbl_x"], font=("Arial", 12, "bold"))
        self.ui_lbl_x.pack(side="left", padx=(0, 5))
        self.pos_x_slider = ctk.CTkSlider(row2, from_=0.5, to=2.0, width=150, command=self.on_slider_change)
        self.pos_x_slider.set(1.15)
        self.pos_x_slider.pack(side="left", padx=(0, 20))

        self.ui_lbl_y = ctk.CTkLabel(row2, text=self.texts["lbl_y"], font=("Arial", 12, "bold"))
        self.ui_lbl_y.pack(side="left", padx=(0, 5))
        self.pos_y_slider = ctk.CTkSlider(row2, from_=-0.5, to=1.5, width=150, command=self.on_slider_change)
        self.pos_y_slider.set(0.5)
        self.pos_y_slider.pack(side="left")

        self.canvas_container = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        self.canvas_container.pack(fill="both", expand=True, padx=10, pady=5)

        self.btn_save = ctk.CTkButton(self.right_frame, text=self.texts["btn_save"], font=("Arial", 14, "bold"),
                                      height=40, fg_color="#2ECC71", hover_color="#27AE60", state="disabled",
                                      command=self.save_image)
        self.btn_save.pack(pady=(0, 15), padx=20)

    def change_language(self, value):
        new_lang = "zh" if value == "中文" else "en"
        if self.lang == new_lang: return

        self.lang = new_lang
        self.texts = LANGUAGES[self.lang]

        self.title(self.texts["app_title"])
        self.ui_title_left.configure(text=self.texts["left_title"])
        self.ui_desc_left.configure(text=self.texts["left_desc"])
        self.btn_parse.configure(text=self.texts["btn_parse"])
        self.ui_title_right.configure(text=self.texts["right_title"])
        self.ui_lbl_type.configure(text=self.texts["lbl_type"])
        self.ui_lbl_zoom.configure(text=self.texts["lbl_zoom"])
        self.ui_lbl_font.configure(text=self.texts["lbl_font"])
        self.ui_lbl_x.configure(text=self.texts["lbl_x"])
        self.ui_lbl_y.configure(text=self.texts["lbl_y"])
        self.btn_save.configure(text=self.texts["btn_save"])

        self.chart_type_dropdown.configure(values=self.texts["types"])
        self.chart_type_var.set(self.texts["types"][self.current_type_idx])

        current_text = self.textbox.get("1.0", "end-1c").strip()
        is_example = False
        for ex in LANGUAGES["zh"]["examples"].values():
            if current_text == ex.strip(): is_example = True
        for ex in LANGUAGES["en"]["examples"].values():
            if current_text == ex.strip(): is_example = True

        if is_example:
            self.textbox.delete("1.0", "end")
            self.textbox.insert("0.0", self.texts["examples"][self.current_type_idx])

        if self.parsed_data:
            self.refresh_chart()

    def init_static_canvas(self):
        self.fig = Figure(figsize=(9, 4.5), dpi=100)
        self.fig.patch.set_facecolor('#F0F0F0' if ctk.get_appearance_mode() == "Light" else '#2B2B2B')
        self.ax = self.fig.add_axes([0.1, 0.15, 0.6, 0.7])
        self.ax.axis('off')
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.canvas_container)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def _is_valid_color(self, color_str):
        color_str = color_str.strip()
        if color_str in COLOR_MAPPING: return True
        if mcolors.is_color_like(color_str): return True
        return False

    def _get_hex_color(self, color_str):
        color_str = color_str.strip()
        if color_str in COLOR_MAPPING: return COLOR_MAPPING[color_str]
        return color_str

    def on_chart_type_change(self, value):
        self.current_type_idx = self.texts["types"].index(value)

        current_text = self.textbox.get("1.0", "end-1c").strip()
        is_example = any(current_text == ex.strip() for ex in self.texts["examples"].values())
        if is_example:
            self.textbox.delete("1.0", "end")
            self.textbox.insert("0.0", self.texts["examples"][self.current_type_idx])
            self._parse_data_from_text()

        if self.parsed_data:
            self.refresh_chart()

    def _parse_data_from_text(self):
        text = self.textbox.get("1.0", "end-1c").strip()
        lines = text.split('\n')
        raw_title = lines[0].strip() if lines else "Data Overview"

        extracted_title = re.sub(r'(帮我)?(生成|画一个|做一个)?.*(柱状图|折线图|饼状图|条形图)[:：\s]*', '', raw_title)
        extracted_title = re.sub(r'(please\s+)?(generate|draw|create|make)?\s*(a\s+)?(pie|bar|line)\s*chart[:：\s]*', '',
                                 extracted_title, flags=re.IGNORECASE)

        if not extracted_title: extracted_title = "Data Overview"

        temp_data = {}
        temp_colors = {}
        primary_unit = ""

        pattern = re.compile(r'(.+?)[:：]\s*(\d+(?:\.\d+)?)\s*([^(（\s]+)?\s*[(（](.+?)[)）]')

        for line in lines[1:]:
            line = line.strip()
            if not line: continue

            match = pattern.search(line)
            if match:
                color_name = match.group(4).strip()
                if not self._is_valid_color(color_name):
                    continue

                cat_name = match.group(1).strip()
                val = float(match.group(2))
                unit = match.group(3)

                if unit:
                    unit = unit.strip()
                    if not primary_unit:
                        primary_unit = unit

                temp_data[cat_name] = val
                temp_colors[cat_name] = self._get_hex_color(color_name)

        if not temp_data: return False

        self.extracted_title = extracted_title
        self.parsed_data = temp_data
        self.parsed_colors = temp_colors
        self.primary_unit = primary_unit
        return True

    def parse_and_preview(self):
        text = self.textbox.get("1.0", "end-1c").strip()
        if not text:
            messagebox.showwarning("Warning", self.texts["msg_empty"])
            return

        text_lower = text.lower()
        if "柱状图" in text or "bar chart" in text_lower:
            self.current_type_idx = 1
        elif "折线图" in text or "line chart" in text_lower:
            self.current_type_idx = 3
        elif "条形图" in text or "h-bar chart" in text_lower:
            self.current_type_idx = 2
        elif "饼状图" in text or "饼图" in text or "pie chart" in text_lower:
            self.current_type_idx = 0

        self.chart_type_var.set(self.texts["types"][self.current_type_idx])

        success = self._parse_data_from_text()

        if success:
            self.refresh_chart()
            self.btn_save.configure(state="normal")
        else:
            messagebox.showwarning(self.texts["msg_fail_t"], self.texts["msg_fail_d"])

    def on_slider_change(self, value):
        if self.parsed_data:
            self.refresh_chart()

    def refresh_chart(self):
        self.ax.clear()

        zoom_factor = float(self.pie_size_slider.get())
        current_fontsize = int(self.font_size_slider.get())
        current_x = float(self.pos_x_slider.get())
        current_y = float(self.pos_y_slider.get())

        labels = list(self.parsed_data.keys())
        sizes = list(self.parsed_data.values())
        colors = [self.parsed_colors[l] for l in labels]
        total_val = sum(sizes)
        unit_display = self.primary_unit if self.primary_unit else ""
        text_color = "black" if ctk.get_appearance_mode() == "Light" else "white"

        if self.current_type_idx == 0:
            self.ax.set_aspect('equal')
            self.ax.axis('off')
            wedges, texts, autotexts = self.ax.pie(
                sizes, colors=colors, autopct='%1.1f%%',
                startangle=90, pctdistance=0.75, radius=zoom_factor,
                textprops={'fontsize': 10, 'fontweight': 'bold', 'color': 'black'}
            )
            self.ax.set_xlim(-1.8, 1.8)
            self.ax.set_ylim(-1.8, 1.8)
            legend_handles = wedges
        else:
            self.ax.set_aspect('auto')
            self.ax.axis('on')
            self.ax.tick_params(colors=text_color, labelsize=current_fontsize - 2)
            for spine in self.ax.spines.values():
                spine.set_color(text_color)

            labels_text = [f"{val:g} {unit_display}" for val in sizes]

            if self.current_type_idx == 1:
                bars = self.ax.bar(labels, sizes, color=colors, width=0.6 * zoom_factor)
                legend_handles = bars
                self.ax.bar_label(bars, labels=labels_text, padding=3, color=text_color, fontsize=current_fontsize - 2)

            elif self.current_type_idx == 2:
                bars = self.ax.barh(labels, sizes, color=colors, height=0.6 * zoom_factor)
                legend_handles = bars
                self.ax.bar_label(bars, labels=labels_text, padding=3, color=text_color, fontsize=current_fontsize - 2)

            elif self.current_type_idx == 3:
                self.ax.plot(labels, sizes, color='#A6A6A6', linewidth=2 * zoom_factor, linestyle='--', zorder=1)
                scatter = self.ax.scatter(labels, sizes, color=colors, s=150 * zoom_factor, zorder=2)
                import matplotlib.patches as mpatches
                legend_handles = [mpatches.Patch(color=c) for c in colors]
                for i, txt in enumerate(sizes):
                    self.ax.annotate(f"{txt:g} {unit_display}", (labels[i], sizes[i]), textcoords="offset points",
                                     xytext=(0, 10), ha='center', color=text_color, fontsize=current_fontsize - 2)

            self.ax.relim()
            self.ax.autoscale_view()

            if self.current_type_idx in [1, 3]:
                y_lim = self.ax.get_ylim()
                self.ax.set_ylim(y_lim[0], y_lim[1] * (1 / zoom_factor))
            elif self.current_type_idx == 2:
                x_lim = self.ax.get_xlim()
                self.ax.set_xlim(x_lim[0], x_lim[1] * (1 / zoom_factor))

        legend_labels = [f"{label} ({size:g}{unit_display})" for label, size in zip(labels, sizes)]
        legend = self.ax.legend(legend_handles, legend_labels, title=self.texts["chart_legend"],
                                loc="center left", bbox_to_anchor=(current_x, current_y),
                                fontsize=current_fontsize, frameon=False)

        plt.setp(legend.get_texts(), color=text_color)
        plt.setp(legend.get_title(), color=text_color, fontweight='bold', fontsize=current_fontsize + 1)

        display_title = f'{self.extracted_title}\n({self.texts["chart_total"]}: {total_val:g} {unit_display})'
        self.fig.suptitle(display_title, fontsize=16, fontweight='bold', color=text_color, y=0.98)
        self.fig.patch.set_facecolor('#F0F0F0' if ctk.get_appearance_mode() == "Light" else '#2B2B2B')
        self.ax.set_facecolor('#F0F0F0' if ctk.get_appearance_mode() == "Light" else '#2B2B2B')

        self.canvas.draw()

    def save_image(self):
        if not self.fig: return
        safe_filename = re.sub(r'[\\/*?:"<>|]', "", f"{self.extracted_title}_{self.chart_type_var.get()}")
        default_file = f"{safe_filename}.png"
        save_path = filedialog.asksaveasfilename(
            title="Save Chart", defaultextension=".png",
            filetypes=[("PNG Image", "*.png"), ("JPEG Image", "*.jpg")],
            initialfile=default_file
        )
        if save_path:
            try:
                self.fig.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
                messagebox.showinfo("Success", self.texts["msg_save_s"])
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save:\n{str(e)}")


if __name__ == "__main__":
    app = UniversalChartApp()
    app.mainloop()