import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from utils.db_util import DBUtil
import pymysql

def show_user_window(user_id):
    """显示普通用户主窗口（新增返回按钮）"""
    root_user = tk.Tk()
    root_user.title(f"校园二手平台 - 普通用户中心（用户ID：{user_id}）")
    root_user.geometry("900x600")
    
    # 新增：返回登录页按钮
    def on_return():
        if messagebox.askokcancel("提示", "确定退出并返回登录页吗？"):
            root_user.destroy()
            from views.login_view import show_login_window
            show_login_window()
    
    btn_return = tk.Button(root_user, text="返回登录", font=("宋体", 10), command=on_return)
    btn_return.place(x=10, y=10)
    
    # ========== 1. 发布物品模块（无核心修改） ==========
    def open_publish_goods():
        """打开发布物品窗口（新增返回按钮）"""
        def do_publish():
            goods_name = entry_g_name.get().strip()
            category_text = combo_category.get()
            buy_year = entry_buy_year.get().strip()
            new_degree = entry_new_degree.get().strip()
            price = entry_price.get().strip()
            location = entry_location.get().strip()
            
            # 校验
            if not goods_name or not category_text or not new_degree or not price or not location:
                messagebox.showerror("错误", "带*的字段不能为空！")
                return
            try:
                price_float = float(price)
                if price_float < 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("错误", "价格必须是正数！")
                return
            
            # 提取类别ID（格式："1 书籍教材"）
            category_id = category_text.split()[0]
            
            try:
                conn = DBUtil.get_connection()
                cursor = conn.cursor()
                sql = """
                    INSERT INTO goods41 (category_id, publisher_id, goods_name, buy_year, new_degree, price, location)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (category_id, user_id, goods_name, buy_year, new_degree, price_float, location))
                conn.commit()
                messagebox.showinfo("成功", "物品发布成功！")
                publish_window.destroy()
                load_goods_list()  # 刷新物品列表
            except Exception as e:
                messagebox.showerror("错误", f"发布失败：{str(e)}")
            finally:
                DBUtil.close(conn, cursor)
        
        def on_publish_return():
            publish_window.destroy()
        
        # 发布窗口
        publish_window = tk.Toplevel(root_user)
        publish_window.title("发布二手物品")
        publish_window.geometry("450x400")
        publish_window.resizable(False, False)
        
        # 新增：返回按钮
        btn_pub_return = tk.Button(publish_window, text="返回", font=("宋体", 10), command=on_publish_return)
        btn_pub_return.place(x=10, y=10)
        
        # 物品名称
        tk.Label(publish_window, text="物品名称*：", font=("宋体", 12)).place(x=50, y=30)
        entry_g_name = tk.Entry(publish_window, font=("宋体", 12), width=30)
        entry_g_name.place(x=130, y=30)
        
        # 物品类别
        tk.Label(publish_window, text="物品类别*：", font=("宋体", 12)).place(x=50, y=70)
        combo_category = ttk.Combobox(publish_window, font=("宋体", 12), width=28)
        # 加载类别
        try:
            conn = DBUtil.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT category_id, category_name FROM category41")
            categories = [f"{cid} {cname}" for cid, cname in cursor.fetchall()]
            combo_category['values'] = categories
            if categories:
                combo_category.current(0)
        except Exception as e:
            messagebox.showerror("错误", f"加载类别失败：{str(e)}")
        finally:
            DBUtil.close(conn, cursor)
        combo_category.place(x=130, y=70)
        
        # 购买年份
        tk.Label(publish_window, text="购买年份：", font=("宋体", 12)).place(x=50, y=110)
        entry_buy_year = tk.Entry(publish_window, font=("宋体", 12), width=30)
        entry_buy_year.place(x=130, y=110)
        tk.Label(publish_window, text="例：2023", font=("宋体", 10)).place(x=350, y=110)
        
        # 新旧程度
        tk.Label(publish_window, text="新旧程度*：", font=("宋体", 12)).place(x=50, y=150)
        entry_new_degree = tk.Entry(publish_window, font=("宋体", 12), width=30)
        entry_new_degree.place(x=130, y=150)
        tk.Label(publish_window, text="例：9成新", font=("宋体", 10)).place(x=350, y=150)
        
        # 转让价格
        tk.Label(publish_window, text="转让价格*：", font=("宋体", 12)).place(x=50, y=190)
        entry_price = tk.Entry(publish_window, font=("宋体", 12), width=30)
        entry_price.place(x=130, y=190)
        tk.Label(publish_window, text="元", font=("宋体", 10)).place(x=350, y=190)
        
        # 位置
        tk.Label(publish_window, text="位置*：", font=("宋体", 12)).place(x=50, y=230)
        entry_location = tk.Entry(publish_window, font=("宋体", 12), width=30)
        entry_location.place(x=130, y=230)
        
        # 发布按钮
        btn_publish = tk.Button(publish_window, text="发布", font=("宋体", 12), command=do_publish)
        btn_publish.place(x=200, y=280)
    
    # ========== 2. 物品列表/查询模块（无修改） ==========
    def load_goods_list(keyword=""):
        """加载物品列表（支持关键词查询）"""
        # 清空列表
        for item in tree_goods.get_children():
            tree_goods.delete(item)
        
        try:
            conn = DBUtil.get_connection()
            cursor = conn.cursor()
            sql = """
                SELECT g.goods_id, g.goods_name, c.category_name, g.new_degree, g.price, g.location, u.username
                FROM goods41 g
                JOIN category41 c ON g.category_id = c.category_id
                JOIN user41 u ON g.publisher_id = u.user_id
                WHERE g.status = 'on_shelf'
            """
            params = []
            if keyword:
                sql += " AND g.goods_name LIKE %s"
                params.append(f"%{keyword}%")
            cursor.execute(sql, params)
            for row in cursor.fetchall():
                tree_goods.insert("", tk.END, values=row)
        except Exception as e:
            messagebox.showerror("错误", f"加载物品失败：{str(e)}")
        finally:
            DBUtil.close(conn, cursor)
    
    def search_goods():
        """搜索物品"""
        keyword = entry_search.get().strip()
        load_goods_list(keyword)
    
    # ========== 3. 下单模块（无修改） ==========
    def create_order():
        """创建订单"""
        selected = tree_goods.selection()
        if not selected:
            messagebox.showerror("错误", "请选择要购买的物品！")
            return
        
        goods_info = tree_goods.item(selected[0])["values"]
        goods_id = goods_info[0]
        goods_name = goods_info[1]
        price = goods_info[4]
        
        # 模拟支付确认
        if messagebox.askyesno("确认", f"是否购买【{goods_name}】，价格：{price}元？"):
            try:
                conn = DBUtil.get_connection()
                cursor = conn.cursor()
                # 插入订单
                sql = """
                    INSERT INTO order41 (user_id, goods_id, amount, pay_status)
                    VALUES (%s, %s, %s, 'paid')
                """
                cursor.execute(sql, (user_id, goods_id, price))
                conn.commit()
                messagebox.showinfo("成功", "下单并支付成功！")
            except Exception as e:
                messagebox.showerror("错误", f"下单失败：{str(e)}")
            finally:
                DBUtil.close(conn, cursor)
    # 下单功能（新增购买后下架物品逻辑）
    def create_order():
        selected = tree_goods.selection()
        if not selected:
            messagebox.showerror("错误", "请选择要购买的物品！")
            return
        
        goods_info = tree_goods.item(selected[0])["values"]
        goods_id = goods_info[0]
        goods_name = goods_info[1]
        price = goods_info[4]  # 根据你的列顺序调整索引
        
        if messagebox.askyesno("确认", f"是否购买【{goods_name}】，价格：{price}元？"):
            try:
                conn = DBUtil.get_connection()
                # 开启事务（保证订单创建和下架操作原子性）
                conn.begin()
                
                cursor = conn.cursor()
                # 1. 创建订单
                sql_order = """
                    INSERT INTO order41 (user_id, goods_id, amount, pay_status)
                    VALUES (%s, %s, %s, 'paid')
                """
                cursor.execute(sql_order, (user_id, goods_id, price))
                
                # 2. 下架该物品（核心新增逻辑）
                sql_offline = """
                    UPDATE goods41 SET status = 'off_shelf' WHERE goods_id = %s
                """
                cursor.execute(sql_offline, (goods_id,))
                
                # 提交事务
                conn.commit()
                
                messagebox.showinfo("成功", f"购买【{goods_name}】成功！该物品已自动下架")
                # 刷新物品列表（让下架的物品从列表中消失）
                load_goods_list()
                
            except Exception as e:
                # 回滚事务（有一个操作失败则全部撤销）
                conn.rollback()
                messagebox.showerror("错误", f"购买失败：{str(e)}")
            finally:
                DBUtil.close(conn, cursor)
    # ========== 4. 收藏模块（无修改） ==========
    def collect_goods():
        """收藏物品"""
        selected = tree_goods.selection()
        if not selected:
            messagebox.showerror("错误", "请选择要收藏的物品！")
            return
        
        goods_info = tree_goods.item(selected[0])["values"]
        goods_id = goods_info[0]
        goods_name = goods_info[1]
        
        try:
            conn = DBUtil.get_connection()
            cursor = conn.cursor()
            # 检查是否已收藏
            cursor.execute("SELECT * FROM collection41 WHERE user_id = %s AND goods_id = %s", (user_id, goods_id))
            if cursor.fetchone():
                messagebox.showwarning("提示", f"已收藏【{goods_name}】！")
                return
            # 插入收藏
            cursor.execute("INSERT INTO collection41 (user_id, goods_id) VALUES (%s, %s)", (user_id, goods_id))
            conn.commit()
            messagebox.showinfo("成功", f"收藏【{goods_name}】成功！")
        except Exception as e:
            messagebox.showerror("错误", f"收藏失败：{str(e)}")
        finally:
            DBUtil.close(conn, cursor)
    
    # ========== 5. 投诉模块（新增返回按钮 + 投诉类别下拉框） ==========
    def open_complaint_window():
        """打开投诉窗口"""
        def load_user_orders():
            """加载用户已支付订单"""
            for item in tree_orders.get_children():
                tree_orders.delete(item)
            try:
                conn = DBUtil.get_connection()
                cursor = conn.cursor()
                sql = """
                    SELECT o.order_id, g.goods_name, o.order_time, o.amount
                    FROM order41 o
                    JOIN goods41 g ON o.goods_id = g.goods_id
                    WHERE o.user_id = %s AND o.pay_status = 'paid'
                """
                cursor.execute(sql, (user_id,))
                for row in cursor.fetchall():
                    tree_orders.insert("", tk.END, values=row)
            except Exception as e:
                messagebox.showerror("错误", f"加载订单失败：{str(e)}")
            finally:
                DBUtil.close(conn, cursor)
        
        def do_complaint():
            """提交投诉"""
            selected = tree_orders.selection()
            if not selected:
                messagebox.showerror("错误", "请选择要投诉的订单！")
                return
            
            # 从下拉框获取选中的投诉类别
            complaint_type = combo_complaint_type.get()
            if not complaint_type:
                messagebox.showerror("错误", "请选择投诉类别！")
                return
                
            order_info = tree_orders.item(selected[0])["values"]
            order_id = order_info[0]
            complaint_reason = text_reason.get("1.0", tk.END).strip()
            
            if not complaint_reason:
                messagebox.showerror("错误", "投诉原因不能为空！")
                return
            
            try:
                conn = DBUtil.get_connection()
                cursor = conn.cursor()
                # 检查是否已投诉
                cursor.execute("SELECT * FROM complaint41 WHERE order_id = %s", (order_id,))
                if cursor.fetchone():
                    messagebox.showwarning("提示", "该订单已投诉！")
                    return
                # 插入投诉
                sql = """
                    INSERT INTO complaint41 (order_id, complain_user_id, complaint_type, complaint_reason)
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(sql, (order_id, user_id, complaint_type, complaint_reason))
                conn.commit()
                messagebox.showinfo("成功", "投诉提交成功！等待管理员处理")
                complaint_window.destroy()
            except Exception as e:
                messagebox.showerror("错误", f"投诉失败：{str(e)}")
            finally:
                DBUtil.close(conn, cursor)
        
        def on_complaint_return():
            complaint_window.destroy()
        
        # 投诉窗口
        complaint_window = tk.Toplevel(root_user)
        complaint_window.title("订单投诉")
        complaint_window.geometry("600x400")
        
        # 新增：返回按钮
        btn_comp_return = tk.Button(complaint_window, text="返回", font=("宋体", 10), command=on_complaint_return)
        btn_comp_return.place(x=10, y=10)
        
        # 订单列表
        tk.Label(complaint_window, text="我的已支付订单：", font=("宋体", 12)).place(x=46, y=10)
        columns = ("订单ID", "物品名称", "下单时间", "金额")
        tree_orders = ttk.Treeview(complaint_window, columns=columns, show="headings", height=8)
        for col in columns:
            tree_orders.heading(col, text=col, anchor='center')
            tree_orders.column(col, width=120, anchor='center')
        tree_orders.place(x=20, y=50, width=560)
        load_user_orders()
        
        # --- 核心修改：投诉类别从 Entry 改为 Combobox ---
        tk.Label(complaint_window, text="投诉类别*：", font=("宋体", 12)).place(x=20, y=230)
        
        # 定义投诉类别选项
        complaint_types = [
            "物品与描述不符",
            "卖家未发货",
            "物品有质量问题",
            "卖家态度恶劣",
            "其他原因"
        ]
        combo_complaint_type = ttk.Combobox(complaint_window, font=("宋体", 12), width=28, values=complaint_types, state="readonly")
        combo_complaint_type.place(x=100, y=230)
        # 可以设置一个默认值，也可以留空
        # combo_complaint_type.current(0) 
        
        # 投诉原因
        tk.Label(complaint_window, text="投诉原因*：", font=("宋体", 12)).place(x=20, y=270)
        text_reason = scrolledtext.ScrolledText(complaint_window, font=("宋体", 12), width=50, height=4)
        text_reason.place(x=100, y=270)
        
        # 提交按钮
        btn_submit = tk.Button(complaint_window, text="提交投诉", font=("宋体", 12), command=do_complaint)
        btn_submit.place(x=250, y=350)

    # ========== 6. 查看投诉处理意见模块 ==========
    def open_view_complaints_window():
        """打开查看投诉处理意见的窗口"""
        def load_user_complaints():
            """加载用户的所有投诉记录（包括已处理和未处理）"""
            for item in tree_my_complaints.get_children():
                tree_my_complaints.delete(item)
            
            try:
                conn = DBUtil.get_connection()
                cursor = conn.cursor()
                sql = """
                    SELECT 
                        c.complaint_id,
                        g.goods_name,
                        c.complaint_type,
                        c.complaint_time,
                        c.handle_status,
                        ch.handle_opinion,
                        ch.handle_time
                    FROM complaint41 c
                    JOIN order41 o ON c.order_id = o.order_id
                    JOIN goods41 g ON o.goods_id = g.goods_id
                    LEFT JOIN complaint_handle41 ch ON c.complaint_id = ch.complaint_id
                    WHERE c.complain_user_id = %s
                    ORDER BY c.complaint_time DESC
                """
                cursor.execute(sql, (user_id,))
                for row in cursor.fetchall():
                    # 将 None 或空值替换为更友好的显示
                    complaint_id, goods_name, complaint_type, complaint_time, handle_status, handle_opinion, handle_time = row
                    handle_opinion = handle_opinion if handle_opinion else "--- 待处理 ---"
                    handle_time = handle_time if handle_time else "---"
                    display_status = "已处理" if handle_status == "handled" else "待处理"
                    
                    # 插入到Treeview中
                    tree_my_complaints.insert("", tk.END, values=(
                        complaint_id, goods_name, complaint_type, complaint_time, display_status, handle_opinion, handle_time
                    ))
            except Exception as e:
                messagebox.showerror("错误", f"加载投诉记录失败：{str(e)}")
            finally:
                DBUtil.close(conn, cursor)

        # 创建查看投诉窗口
        view_window = tk.Toplevel(root_user)
        view_window.title("我的投诉记录")
        view_window.geometry("1200x400")
        view_window.resizable(True, True)

        # 投诉记录列表
        tk.Label(view_window, text="我的投诉记录：", font=("宋体", 12)).place(x=20, y=20)
        columns = ("投诉ID", "物品名称", "投诉类型", "投诉时间", "处理状态", "处理意见", "处理时间")
        tree_my_complaints = ttk.Treeview(view_window, columns=columns, show="headings", height=15)
        
        # 设置列宽和居中对齐
        tree_my_complaints.heading("投诉ID", text="投诉ID", anchor='center')
        tree_my_complaints.column("投诉ID", width=60, anchor='center')
        
        tree_my_complaints.heading("物品名称", text="物品名称", anchor='center')
        tree_my_complaints.column("物品名称", width=120, anchor='center')
        
        tree_my_complaints.heading("投诉类型", text="投诉类型", anchor='center')
        tree_my_complaints.column("投诉类型", width=120, anchor='center')
        
        tree_my_complaints.heading("投诉时间", text="投诉时间", anchor='center')
        tree_my_complaints.column("投诉时间", width=150, anchor='center')
        
        tree_my_complaints.heading("处理状态", text="处理状态", anchor='center')
        tree_my_complaints.column("处理状态", width=80, anchor='center')
        
        tree_my_complaints.heading("处理意见", text="处理意见", anchor='center')
        tree_my_complaints.column("处理意见", width=200, anchor='center')
        
        tree_my_complaints.heading("处理时间", text="处理时间", anchor='center')
        tree_my_complaints.column("处理时间", width=200, anchor='center')
        
        tree_my_complaints.place(x=20, y=50)

        # 加载数据
        load_user_complaints()
  # ========== 界面布局（修复按钮重叠 + 优化坐标） ==========
    # 按钮区域（重新规划x坐标，避免重叠）
    btn_publish = tk.Button(root_user, text="发布物品", font=("宋体", 12), width=10, command=open_publish_goods)
    btn_publish.place(x=20, y=50)  # 第一个按钮

    btn_complaint = tk.Button(root_user, text="订单投诉", font=("宋体", 12), width=10, command=open_complaint_window)
    btn_complaint.place(x=120, y=50)  # 第二个按钮

    btn_view_complaints = tk.Button(root_user, text="查看投诉", font=("宋体", 12), width=10, command=open_view_complaints_window)
    btn_view_complaints.place(x=220, y=50)  # 第三个按钮（无重叠）

    # 搜索区域（右移x坐标，避开按钮）
    tk.Label(root_user, text="物品搜索：", font=("宋体", 12)).place(x=320, y=55)  # 原x=220 → 改为x=320
    entry_search = tk.Entry(root_user, font=("宋体", 12), width=30)
    entry_search.place(x=400, y=55)  # 原x=300 → 改为x=400
    btn_search = tk.Button(root_user, text="搜索", font=("宋体", 12), width=8, command=search_goods)
    btn_search.place(x=680, y=50)  # 原x=580 → 改为x=680

    # 物品列表（文字居中，保留原有配置）
    tk.Label(root_user, text="二手物品列表：", font=("宋体", 12)).place(x=20, y=100)
    columns = ("物品ID", "物品名称", "类别", "新旧程度", "价格（元）", "位置", "发布者")
    tree_goods = ttk.Treeview(root_user, columns=columns, show="headings", height=20)
    for col in columns:
        tree_goods.heading(col, text=col, anchor='center')
        tree_goods.column(col, width=110 if col == "物品名称" else 80, anchor='center')
    tree_goods.place(x=20, y=130, width=860)

    # 操作按钮（保留原有配置）
    btn_buy = tk.Button(root_user, text="立即购买", font=("宋体", 12), width=10, command=create_order)
    btn_buy.place(x=300, y=550)

    btn_collect = tk.Button(root_user, text="收藏物品", font=("宋体", 12), width=10, command=collect_goods)
    btn_collect.place(x=420, y=550)

    # 初始加载物品列表
    load_goods_list()
    root_user.mainloop()

if __name__ == "__main__":
    show_user_window(1)