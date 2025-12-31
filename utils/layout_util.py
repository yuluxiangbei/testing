import tkinter as tk

def center_window(window, width=None, height=None):
    """
    窗口居中显示
    :param window: 目标窗口对象
    :param width: 窗口宽度（None则使用窗口当前宽度）
    :param height: 窗口高度（None则使用窗口当前高度）
    """
    # 获取屏幕宽高
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    
    # 计算窗口坐标
    if width and height:
        window.geometry(f"{width}x{height}")
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
    else:
        # 自动获取窗口尺寸
        window.update_idletasks()
        win_width = window.winfo_width()
        win_height = window.winfo_height()
        x = (screen_width - win_width) // 2
        y = (screen_height - win_height) // 2
    
    window.geometry(f"+{x}+{y}")

def make_resizable(window, widgets_config):
    """
    设置窗口可缩放，并配置控件自适应
    :param window: 根窗口
    :param widgets_config: 控件权重配置，格式：[(widget, row, column, row_weight, col_weight, sticky)]
    """
    # 允许窗口缩放
    window.resizable(True, True)
    
    # 配置行列权重（让行列随窗口缩放）
    for config in widgets_config:
        widget, row, col, row_weight, col_weight, sticky = config
        # 设置行列权重
        window.grid_rowconfigure(row, weight=row_weight)
        window.grid_columnconfigure(col, weight=col_weight)
        # 放置控件并设置粘性（填充单元格）
        widget.grid(row=row, column=col, padx=10, pady=10, sticky=sticky)