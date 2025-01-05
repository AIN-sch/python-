# 作者：AleOsh
# 日期：2025年1月5日

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import shutil
import threading
import time
from datetime import datetime
import webbrowser
from concurrent.futures import ThreadPoolExecutor
from queue import Queue, Empty
import requests

class FileTypeSelector:
    def __init__(self, parent, initial_types=None):
        self.window = tk.Toplevel(parent)
        self.window.title("选择文件类型")
        self.window.geometry("600x600")  
        self.window.transient(parent)
        self.window.grab_set()
        
        # 设置整体样式
        style = ttk.Style()
        style.configure('FileType.TFrame', padding=10)
        
        # 创建主框架
        main_frame = ttk.Frame(self.window, style='FileType.TFrame')
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # 文件类型分类
        self.file_types = {
            "图片格式": [
                ("JPG 图片", "jpg"),
                ("JPEG 图片", "jpeg"),
                ("PNG 图片", "png"),
                ("GIF 动图", "gif"),
                ("BMP 图片", "bmp"),
                ("WEBP 图片", "webp"),
                ("TIFF 图片", "tiff"),
                ("ICO 图标", "ico")
            ],
            "视频格式": [
                ("MP4 视频", "mp4"),
                ("AVI 视频", "avi"),
                ("MKV 视频", "mkv"),
                ("MOV 视频", "mov"),
                ("WMV 视频", "wmv"),
                ("FLV 视频", "flv"),
                ("WEBM 视频", "webm"),
                ("M4V 视频", "m4v")
            ],
            "音频格式": [
                ("MP3 音频", "mp3"),
                ("WAV 音频", "wav"),
                ("FLAC 音频", "flac"),
                ("AAC 音频", "aac"),
                ("M4A 音频", "m4a"),
                ("OGG 音频", "ogg"),
                ("WMA 音频", "wma")
            ],
            "文档格式": [
                ("PDF 文档", "pdf"),
                ("Word 文档", "doc"),
                ("Word 文档", "docx"),
                ("Excel 表格", "xls"),
                ("Excel 表格", "xlsx"),
                ("文本文件", "txt"),
                ("PPT 演示", "ppt"),
                ("PPT 演示", "pptx")
            ],
            "压缩格式": [
                ("ZIP 压缩包", "zip"),
                ("RAR 压缩包", "rar"),
                ("7Z 压缩包", "7z"),
                ("TAR 压缩包", "tar"),
                ("GZ 压缩包", "gz")
            ]
        }
        
        # 创建选项卡
        notebook = ttk.Notebook(main_frame)
        notebook.pack(expand=True, fill='both', padx=5, pady=5)
        
        # 存储所有的复选框变量
        self.selected_types = {}
        
        # 为每个分类创建一个选项卡
        for category, types in self.file_types.items():
            frame = ttk.Frame(notebook, padding=10)
            notebook.add(frame, text=category)
            
            # 创建滚动框架
            canvas = tk.Canvas(frame, highlightthickness=0)
            scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e, canvas=canvas: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            # 添加文件类型选项
            for desc, ext in types:
                var = tk.BooleanVar(value=False)
                if initial_types and ext in initial_types:
                    var.set(True)
                self.selected_types[ext] = var
                
                chk = ttk.Checkbutton(
                    scrollable_frame,
                    text=desc,
                    variable=var,
                    command=self.update_selection
                )
                chk.pack(anchor='w', pady=5, padx=10)
            
            # 布局滚动组件
            canvas.pack(side="left", fill="both", expand=True, padx=(0, 5))
            scrollbar.pack(side="right", fill="y")
        
        # 自定义类型输入框
        custom_frame = ttk.LabelFrame(main_frame, text="自定义文件类型", padding=10)
        custom_frame.pack(fill='x', pady=10)
        
        self.custom_type = tk.StringVar()
        custom_entry = ttk.Entry(custom_frame, textvariable=self.custom_type, width=20)
        custom_entry.pack(side='left', padx=5)
        
        custom_btn = ttk.Button(
            custom_frame,
            text="添加自定义类型",
            command=self.add_custom_type
        )
        custom_btn.pack(side='left', padx=5)
        
        # 已选类型显示框架
        selected_frame = ttk.LabelFrame(main_frame, text="已选择的类型", padding=10)
        selected_frame.pack(fill='x', pady=10)
        
        self.selected_label = ttk.Label(selected_frame, text="", wraplength=500)
        self.selected_label.pack(fill='x')
        
        # 确认按钮
        self.confirm_btn = ttk.Button(
            main_frame,
            text="确定",
            command=self.confirm,
            width=20
        )
        self.confirm_btn.pack(pady=10)
        
        self.result = None
        self.update_selection()
    
    def update_selection(self):
        selected = [ext for ext, var in self.selected_types.items() if var.get()]
        if selected:
            self.selected_label['text'] = "已选择: " + ", ".join(selected)
            self.confirm_btn.config(state='normal')
        else:
            self.selected_label['text'] = "未选择任何类型"
            self.confirm_btn.config(state='disabled')
    
    def add_custom_type(self):
        custom = self.custom_type.get().strip()
        if custom:
            if not custom.startswith('.'):
                custom = '.' + custom
            if custom not in self.selected_types:
                var = tk.BooleanVar(value=True)
                self.selected_types[custom] = var
                self.update_selection()
                self.custom_type.set("")
    
    def confirm(self):
        self.result = [ext for ext, var in self.selected_types.items() if var.get()]
        self.window.destroy()

class FileOrganizer:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("文件整理工具 - By AleOsh")
        self.window.geometry("768x889")  
        
        # 设置整体样式
        style = ttk.Style()
        style.configure('TButton', padding=5)
        style.configure('TLabelframe', padding=10)
        style.configure('TRadiobutton', padding=5)
        
        # 配置进度条样式
        style.configure("Hacker.Horizontal.TProgressbar",
                       troughcolor='black',
                       background='#00ff00',
                       darkcolor='#00ff00',
                       lightcolor='#00ff00',
                       bordercolor='black',
                       thickness=20)
        
        # 创建主框架，添加滚动条
        self.main_canvas = tk.Canvas(self.window)
        self.main_canvas.pack(side='left', fill='both', expand=True)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(self.window, orient='vertical', command=self.main_canvas.yview)
        scrollbar.pack(side='right', fill='y')
        
        self.main_canvas.configure(yscrollcommand=scrollbar.set)
        
        # 创建内部框架
        self.main_frame = ttk.Frame(self.main_canvas, padding="20")
        self.main_canvas.create_window((0, 0), window=self.main_frame, anchor='nw', width=880)
        
        # 显示程序位置
        program_path = os.path.abspath(__file__).replace('/', '\\')
        path_label = ttk.Label(self.main_frame, text=f"程序位置：{program_path}", wraplength=800)
        path_label.pack(fill='x', pady=(0, 20))
        
        # 源文件夹选择框架
        self.source_frame = ttk.LabelFrame(self.main_frame, text="文件位置", padding=10)
        self.source_frame.pack(fill='x', pady=(0, 10))
        
        self.source_path = tk.StringVar()
        self.source_entry = ttk.Entry(self.source_frame, textvariable=self.source_path, width=80)
        self.source_entry.pack(side='left', padx=(0, 5), fill='x', expand=True)
        
        self.source_btn = ttk.Button(self.source_frame, text="选择文件夹", command=self.select_source)
        self.source_btn.pack(side='right')
        
        # 处理模式选择框架
        self.mode_frame = ttk.LabelFrame(self.main_frame, text="处理模式", padding=10)
        self.mode_frame.pack(fill='x', pady=(0, 10))
        
        self.process_mode = tk.StringVar(value="direct")  
        ttk.Radiobutton(self.mode_frame, text="模式1：直接搜索并复制（速度快）", 
                       variable=self.process_mode, value="direct",
                       command=self.on_mode_change).pack(anchor='w', pady=5)
        ttk.Radiobutton(self.mode_frame, text="模式2：先搜索后复制（可显示准确进度）", 
                       variable=self.process_mode, value="scan_first",
                       command=self.on_mode_change).pack(anchor='w', pady=5)
        
        # 文件类型选择框架
        self.type_frame = ttk.LabelFrame(self.main_frame, text="文件类型", padding=10)
        self.type_frame.pack(fill='x', pady=(0, 10))
        
        self.file_types = tk.StringVar()
        self.type_label = ttk.Label(self.type_frame, textvariable=self.file_types, wraplength=700)
        self.type_label.pack(side='left', padx=(0, 5), fill='x', expand=True)
        
        self.type_btn = ttk.Button(self.type_frame, text="选择类型", command=self.select_type)
        self.type_btn.pack(side='right')
        
        # 目标文件夹选择框架
        self.dest_frame = ttk.LabelFrame(self.main_frame, text="输出位置", padding=10)
        self.dest_frame.pack(fill='x', pady=(0, 10))
        
        self.dest_path = tk.StringVar()
        self.dest_entry = ttk.Entry(self.dest_frame, textvariable=self.dest_path, width=80)
        self.dest_entry.pack(side='left', padx=(0, 5), fill='x', expand=True)
        
        self.dest_btn = ttk.Button(self.dest_frame, text="选择文件夹", command=self.select_dest)
        self.dest_btn.pack(side='right')
        
        # 进度框架（初始隐藏）
        self.progress_frame = ttk.LabelFrame(self.main_frame, text="处理进度", padding=10)
        
        # 创建带有黑客风格的进度条
        self.progress = ttk.Progressbar(self.progress_frame, 
                                      length=300, 
                                      mode='determinate',
                                      style="Hacker.Horizontal.TProgressbar")
        self.progress.pack(fill='x', pady=5)
        
        # 进度标签使用绿色文字
        self.progress_label = ttk.Label(self.progress_frame, 
                                      text="0%",
                                      foreground='#00ff00',
                                      background='black',
                                      font=('Consolas', 10, 'bold'))
        self.progress_label.pack(side='left', padx=5)
        
        self.status_label = ttk.Label(self.progress_frame, 
                                    text="",
                                    foreground='#00ff00',
                                    background='black',
                                    font=('Consolas', 10))
        self.status_label.pack(side='left', padx=5)
        
        # 终端输出框架
        self.terminal_frame = ttk.LabelFrame(self.main_frame, text="处理日志", padding=10)
        self.terminal_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # 创建文本框和滚动条
        self.terminal = tk.Text(self.terminal_frame, height=15, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(self.terminal_frame, orient="vertical", command=self.terminal.yview)
        self.terminal.configure(yscrollcommand=scrollbar.set)
        
        # 布局文本框和滚动条
        self.terminal.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 设置文本框样式
        self.terminal.configure(state='disabled', bg='black', fg='white')
        
        # 按钮框架
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(pady=20)
        
        # 开始按钮
        self.start_btn = ttk.Button(self.button_frame, text="开始处理", command=self.start_organize)
        self.start_btn.pack(side='left', padx=5)
        
        # 联系作者按钮
        self.contact_btn = ttk.Button(self.button_frame, text="联系作者", command=self.show_contact)
        self.contact_btn.pack(side='left', padx=5)
        
        # 暂停按钮（初始隐藏）
        self.pause_btn = ttk.Button(self.button_frame, text="暂停", command=self.toggle_pause)
        
        # 取消按钮（初始隐藏）
        self.exit_btn = ttk.Button(self.button_frame, text="取消", command=self.stop_processing)
        
        # 处理状态变量
        self.processing = False
        self.paused = False
        self.current_file_type = None
        
        # 初始化日志目录和文件
        self.log_dir = os.path.join(os.path.dirname(__file__), "file_organizer.log")
        os.makedirs(self.log_dir, exist_ok=True)
        
        # 设置日志文件路径
        current_time = time.strftime("%Y-%m-%d_%H-%M-%S")
        self.log_file = os.path.join(self.log_dir, f"organize_{current_time}.log")
        
        # 创建日志文件
        with open(self.log_file, 'w', encoding='utf-8') as f:
            f.write(f"文件整理工具日志 - {current_time}\n")
            f.write("-" * 50 + "\n\n")
        
        # 绑定事件处理窗口大小变化
        self.main_frame.bind('<Configure>', self._on_frame_configure)
        self.window.bind('<Configure>', self._on_window_configure)
        
        # 初始化时根据默认模式设置UI
        self.on_mode_change()

    def toggle_pause(self):
        """切换暂停状态"""
        self.paused = not self.paused
        if self.paused:
            self.pause_btn.configure(text="继续")
            self.log_message("处理已暂停")
        else:
            self.pause_btn.configure(text="暂停")
            self.log_message("处理已继续")
    
    def stop_processing(self):
        """停止处理"""
        self.processing = False
        self.paused = False
        self.terminal.configure(state='normal')
        self.terminal.delete(1.0, tk.END)
        self.terminal.configure(state='disabled')
        self.log_message("处理已取消")
        self.reset_ui()

    def reset_ui(self):
        # 重置界面状态
        self.start_btn.pack(side='left', padx=5)
        self.pause_btn.pack_forget()
        self.exit_btn.pack_forget()
        self.progress['value'] = 0
        self.progress_label['text'] = "0%"
        self.status_label['text'] = ""
        
    def select_source(self):
        path = filedialog.askdirectory()
        if path:
            self.source_path.set(path.replace('/', '\\'))
            
    def select_dest(self):
        path = filedialog.askdirectory()
        if path:
            self.dest_path.set(path.replace('/', '\\'))
            
    def select_type(self):
        """选择要处理的文件类型"""
        selector = FileTypeSelector(self.window)
        self.window.wait_window(selector.window)
        if selector.result:
            self.current_file_type = selector.result
            self.file_types.set(f"已选择: {', '.join(selector.result)}")
            
    def start_organize(self):
        """开始整理文件"""
        source = self.source_path.get()
        dest = self.dest_path.get()
        
        if not source or not dest:
            messagebox.showwarning("警告", "请选择源文件夹和目标文件夹！")
            return
            
        if not hasattr(self, 'current_file_type') or not self.current_file_type:
            messagebox.showwarning("警告", "请选择要处理的文件类型！")
            return
            
        self.processing = True
        self.paused = False
        
        # 显示暂停和退出按钮
        self.start_btn.pack_forget()
        self.pause_btn.pack(side='left', padx=5)
        self.exit_btn.pack(side='left', padx=5)
        
        # 重置进度条
        self.progress['value'] = 0
        
        # 启动进度更新
        self.window.after(100, self.update_progress)
        
        # 启动处理线程
        threading.Thread(target=lambda: self.process_files(
            source, dest, self.current_file_type)).start()

    def process_files(self, source, dest, file_types):
        """处理文件的核心函数"""
        if not os.path.exists(source) or not os.path.exists(dest):
            self.log_message("源文件夹或目标文件夹不存在！")
            self.processing = False
            self.reset_ui()
            return

        self.log_message(f"开始扫描文件夹: {source}")
        self.log_message(f"文件类型: {', '.join(file_types)}")
        
        # 创建目标文件夹
        for ext in file_types:
            ext_folder = os.path.join(dest, ext.lstrip('.').upper())
            os.makedirs(ext_folder, exist_ok=True)

        if self.process_mode.get() == "direct":
            # 模式1：直接搜索并复制
            self.process_files_direct(source, dest, file_types)
        else:
            # 模式2：先搜索后复制
            self.process_files_scan_first(source, dest, file_types)

    def process_files_direct(self, source, dest, file_types):
        """模式1：直接搜索并复制（边搜索边复制）"""
        try:
            self.log_message("开始搜索并处理文件...")
            self.log_message(f"源文件夹: {source}")
            self.log_message(f"目标文件夹: {dest}")
            self.log_message(f"文件类型: {', '.join(file_types)}")
            processed_count = 0
            
            for root, _, files in os.walk(source):
                if not self.processing:
                    return
                    
                for file in files:
                    if not self.processing:
                        return
                        
                    while self.paused:
                        if not self.processing:
                            return
                        time.sleep(0.1)
                        
                    file_path = os.path.join(root, file)
                    file_ext = os.path.splitext(file)[1].lower()
                    
                    # 检查文件扩展名是否在选定的类型中
                    if any(file_ext.endswith(ft.lower()) for ft in file_types):
                        try:
                            relative_path = os.path.relpath(root, source)
                            self.log_message(f"找到文件: {file}")
                            self.log_message(f"源路径: {file_path}")
                            
                            # 立即复制文件
                            ext_folder = os.path.join(dest, file_ext.lstrip('.').upper())
                            os.makedirs(ext_folder, exist_ok=True)
                            
                            filename = os.path.basename(file_path)
                            dst_path = os.path.join(ext_folder, filename)
                            
                            # 处理重名文件
                            if os.path.exists(dst_path):
                                base, ext = os.path.splitext(filename)
                                counter = 1
                                while os.path.exists(dst_path):
                                    new_filename = f"{base}_{counter}{ext}"
                                    dst_path = os.path.join(ext_folder, new_filename)
                                    counter += 1
                                filename = new_filename
                            
                            # 复制文件
                            shutil.copy2(file_path, dst_path)
                            processed_count += 1
                            self.log_message(f"已复制到: {dst_path}")
                            
                        except Exception as e:
                            self.log_message(f"处理文件失败: {file_path}")
                            self.log_message(f"错误信息: {str(e)}")
            
            self.log_message(f"处理完成！共处理 {processed_count} 个文件")
            self.log_message("=" * 50)
            
        except Exception as e:
            self.log_message(f"处理过程出错: {str(e)}")
        finally:
            self.processing = False
            self.reset_ui()

    def process_files_scan_first(self, source, dest, file_types):
        """模式2：先搜索后复制（显示准确进度）"""
        try:
            self.total_files = 0
            self.current_file_index = 0
            self.files_to_copy = []  # 存储待复制的文件信息
            
            self.log_message("开始扫描文件...")
            self.log_message(f"源文件夹: {source}")
            self.log_message(f"目标文件夹: {dest}")
            self.log_message(f"文件类型: {', '.join(file_types)}")
            
            # 第一阶段：扫描文件
            for root, dirs, files in os.walk(source):
                if not self.processing:
                    return
                
                # 如果当前目录是输出目录或其子目录，跳过
                if self.should_skip_directory(root, dest):
                    self.log_message(f"跳过输出目录: {root}")
                    dirs.clear()  # 清空目录列表，阻止继续遍历子目录
                    continue
                    
                for file in files:
                    if not self.processing:
                        return
                        
                    while self.paused:
                        if not self.processing:
                            return
                        time.sleep(0.1)
                        
                    file_path = os.path.join(root, file)
                    file_ext = os.path.splitext(file)[1].lower()
                    
                    if any(file_ext.endswith(ft.lower()) for ft in file_types):
                        self.total_files += 1
                        self.log_message(f"找到文件: {file}")
                        self.log_message(f"源路径: {file_path}")
                        self.files_to_copy.append((file_path, file_ext))
            
            if not self.processing:
                return
                
            self.log_message(f"扫描完成，共找到 {self.total_files} 个文件")
            self.log_message("=" * 50)
            
            if self.total_files == 0:
                self.log_message("未找到符合条件的文件")
                return
                
            # 设置进度条最大值
            self.progress['maximum'] = self.total_files
            self.progress['value'] = 0
            
            # 第二阶段：复制文件
            self.log_message("开始复制文件...")
            
            for src_path, ext in self.files_to_copy:
                if not self.processing:
                    break
                    
                while self.paused:
                    if not self.processing:
                        break
                    time.sleep(0.1)
                    
                try:
                    # 创建目标文件夹
                    ext_folder = os.path.join(dest, ext.lstrip('.').upper())
                    os.makedirs(ext_folder, exist_ok=True)
                    
                    # 准备目标路径
                    filename = os.path.basename(src_path)
                    dst_path = os.path.join(ext_folder, filename)
                    
                    # 处理重名文件
                    if os.path.exists(dst_path):
                        base, ext = os.path.splitext(filename)
                        counter = 1
                        while os.path.exists(dst_path):
                            new_filename = f"{base}_{counter}{ext}"
                            dst_path = os.path.join(ext_folder, new_filename)
                            counter += 1
                        filename = new_filename
                    
                    # 复制文件
                    shutil.copy2(src_path, dst_path)
                    self.current_file_index += 1
                    
                    # 更新进度（使用after方法避免闪烁）
                    def update_progress():
                        progress = int((self.current_file_index / self.total_files) * 100)
                        self.progress['value'] = self.current_file_index
                        self.progress_label['text'] = f"{progress}%"
                        self.status_label['text'] = f"处理中... {self.current_file_index}/{self.total_files}"
                    
                    self.window.after(0, update_progress)
                    self.log_message(f"已复制到: {dst_path}")
                    
                except Exception as e:
                    self.log_message(f"处理文件失败: {src_path}")
                    self.log_message(f"错误信息: {str(e)}")
            
            if self.current_file_index == self.total_files:
                self.log_message("所有文件处理完成！")
                self.status_label['text'] = "处理完成"
            else:
                self.log_message(f"处理完成 {self.current_file_index}/{self.total_files} 个文件")
            
            self.log_message("=" * 50)
            
        except Exception as e:
            self.log_message(f"处理过程出错: {str(e)}")
        finally:
            self.processing = False
            self.reset_ui()

    def should_skip_directory(self, dir_path, dest_path):
        """检查是否应该跳过该目录"""
        # 转换为绝对路径进行比较
        abs_dir = os.path.abspath(dir_path)
        abs_dest = os.path.abspath(dest_path)
        
        # 检查是否是输出目录或其子目录
        return abs_dir.startswith(abs_dest)

    def log_message(self, message):
        """记录日志消息到终端和文件"""
        try:
            # 获取当前时间
            current_time = time.strftime("%Y-%m-%d %H:%M:%S")
            log_message = f"[{current_time}] {message}\n"
            
            # 更新终端显示
            self.terminal.configure(state='normal')
            self.terminal.insert(tk.END, log_message)
            self.terminal.see(tk.END)
            self.terminal.configure(state='disabled')
            
            # 写入日志文件
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_message)
                
        except Exception as e:
            print(f"写入日志时出错: {str(e)}")

    def update_progress(self):
        """更新进度条"""
        if self.processing and self.process_mode.get() == "scan_first":
            if hasattr(self, 'current_file_index') and hasattr(self, 'total_files'):
                progress = int((self.current_file_index / max(1, self.total_files)) * 100)
                self.progress['value'] = self.current_file_index
                self.progress_label['text'] = f"{progress}%"
            self.window.after(50, self.update_progress)  # 降低更新频率，减少闪烁
    
    def show_contact(self):
        """显示作者联系信息窗口"""
        contact_window = tk.Toplevel(self.window)
        contact_window.title("联系作者")
        contact_window.geometry("302x289")  # 修改窗口大小
        
        # 设置窗口样式
        style = ttk.Style()
        style.configure('Contact.TLabel', font=('微软雅黑', 10))
        style.configure('Contact.TButton', font=('微软雅黑', 10))
        
        # 创建主框架
        main_frame = ttk.Frame(contact_window, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # 显示联系信息
        ttk.Label(main_frame, text="作者：AleOsh", 
                 style='Contact.TLabel').pack(fill='x', pady=2)
        ttk.Label(main_frame, text="邮箱：AyhowZero@gmail.com", 
                 style='Contact.TLabel').pack(fill='x', pady=2)
        
        # 创建按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=20)
        
        def open_github():
            webbrowser.open("https://github.com/AleOsh")
            
        def open_csdn():
            webbrowser.open("https://blog.csdn.net/2301_76829730")
            
        def download_source_code():
            """下载源代码"""
            try:
                # 禁用所有按钮
                for widget in button_frame.winfo_children():
                    if isinstance(widget, ttk.Button):
                        widget.configure(state='disabled')
                
                # 获取桌面路径
                desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
                current_time = time.strftime("%Y%m%d_%H%M%S")
                file_name = f"file_organizer_{current_time}.py"
                file_path = os.path.join(desktop, file_name)
                
                # 读取当前文件内容
                with open(__file__, 'r', encoding='utf-8') as f:
                    source_code = f.read()
                
                # 添加文件头
                header = """# 此程序用Python代码编写
# ====================================
# 作者：AleOsh
# GitHub: https://github.com/AleOsh
# CSDN: https://blog.csdn.net/2301_76829730
# 下载时间：{}
# ====================================

""".format(time.strftime("%Y-%m-%d %H:%M:%S"))
                
                # 写入文件
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(header + source_code)
                
                # 显示成功消息
                messagebox.showinfo("完成", f"Over！成功保存，位置在：\n{file_path}")
                
            except Exception as e:
                messagebox.showerror("错误", f"下载失败：{str(e)}")
            finally:
                # 恢复按钮状态
                for widget in button_frame.winfo_children():
                    if isinstance(widget, ttk.Button):
                        widget.configure(state='normal')
        
        # 添加按钮
        ttk.Button(button_frame, text="访问作者GitHub", style='Contact.TButton', 
                  command=open_github).pack(fill='x', pady=2)
        ttk.Button(button_frame, text="访问作者CSDN", style='Contact.TButton', 
                  command=open_csdn).pack(fill='x', pady=2)
        ttk.Button(button_frame, text="下载源代码", style='Contact.TButton',
                  command=download_source_code).pack(fill='x', pady=2)
    
    def on_mode_change(self):
        """处理模式改变时的UI更新"""
        if self.process_mode.get() == "scan_first":
            self.progress_frame.pack(fill='x', pady=(0, 10))
        else:
            self.progress_frame.pack_forget()
    
    def _on_frame_configure(self, event=None):
        """更新画布的滚动区域"""
        self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))
        
    def _on_window_configure(self, event=None):
        """处理窗口大小变化"""
        # 更新画布大小
        width = self.window.winfo_width() - 20  # 减去滚动条的宽度
        self.main_canvas.itemconfig(1, width=width)
    
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = FileOrganizer()
    app.run()
