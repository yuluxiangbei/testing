import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from utils.db_util import DBUtil

def show_admin_window(admin_id):
    """显示管理员主窗口（新增解冻用户功能）"""
    root_admin = tk.Tk()
    root_admin.title(f"校园二手平台 - 管理员中心（管理员ID：{admin_id}）")
    root_admin.geometry("900x600")
    
    # 新增：返回登录页按钮（原有逻辑）
    def on_return():
        if messagebox.askokcancel("提示", "确定退出并返回登录页吗？"):
            root_admin.destroy()
            from views.login_view import show_login_window
            show_login_window()
    
    btn_return = tk.Button(root_admin, text="返回登录", font=("宋体", 10), command=on_return)
    btn_return.place(x=10, y=10)
    
    # ========== 原有：下架物品模块（无修改） ==========
    def load_all_goods():
        """加载所有上架物品"""
        for item in tree_goods.get_children():
            tree_goods.delete(item)
        try:
            conn = DBUtil.get_connection()
            cursor = conn.cursor()
            sql = """
                SELECT g.goods_id, g.goods_name, c.category_name, u.username, g.price, g.status
                FROM goods41 g
                JOIN category41 c ON g.category_id = c.category_id
                JOIN user41 u ON g.publisher_id = u.user_id
            """
            cursor.execute(sql)
            for row in cursor.fetchall():
                tree_goods.insert("", tk.END, values=row)
        except Exception as e:
            messagebox.showerror("错误", f"加载物品失败：{str(e)}")
        finally:
            DBUtil.close(conn, cursor)
    
    def offline_goods():
        """下架物品"""
        selected = tree_goods.selection()
        if not selected:
            messagebox.showerror("错误", "请选择要下架的物品！")
            return
        
        goods_info = tree_goods.item(selected[0])["values"]
        goods_id = goods_info[0]
        goods_name = goods_info[1]
        
        if messagebox.askyesno("确认", f"是否下架【{goods_name}】？"):
            try:
                conn = DBUtil.get_connection()
                cursor = conn.cursor()
                cursor.execute("UPDATE goods41 SET status = 'off_shelf' WHERE goods_id = %s", (goods_id,))
                conn.commit()
                messagebox.showinfo("成功", f"【{goods_name}】已下架！")
                load_all_goods()
            except Exception as e:
                messagebox.showerror("错误", f"下架失败：{str(e)}")
            finally:
                DBUtil.close(conn, cursor)
    
    # ========== 原有：处理投诉模块（无修改） ==========
    def load_unhandled_complaints():
        """加载未处理投诉"""
        for item in tree_complaints.get_children():
            tree_complaints.delete(item)
        try:
            conn = DBUtil.get_connection()
            cursor = conn.cursor()
            sql = """
                SELECT c.complaint_id, c.order_id, u.username, c.complaint_type, c.complaint_time
                FROM complaint41 c
                JOIN user41 u ON c.complain_user_id = u.user_id
                WHERE c.handle_status = 'unhandled'
            """
            cursor.execute(sql)
            for row in cursor.fetchall():
                tree_complaints.insert("", tk.END, values=row)
        except Exception as e:
            messagebox.showerror("错误", f"加载投诉失败：{str(e)}")
        finally:
            DBUtil.close(conn, cursor)
    
    def handle_complaint():
        """处理投诉"""
        selected = tree_complaints.selection()
        if not selected:
            messagebox.showerror("错误", "请选择要处理的投诉！")
            return
        
        complaint_info = tree_complaints.item(selected[0])["values"]
        complaint_id = complaint_info[0]
        handle_opinion = text_opinion.get("1.0", tk.END).strip()
        
        if not handle_opinion:
            messagebox.showerror("错误", "处理意见不能为空！")
            return
        
        try:
            conn = DBUtil.get_connection()
            cursor = conn.cursor()
            # 插入处理记录（触发器自动更新投诉状态）
            sql = """
                INSERT INTO complaint_handle41 (complaint_id, admin_id, handle_opinion)
                VALUES (%s, %s, %s)
            """
            cursor.execute(sql, (complaint_id, admin_id, handle_opinion))
            conn.commit()
            messagebox.showinfo("成功", "投诉处理完成！")
            load_unhandled_complaints()
            text_opinion.delete("1.0", tk.END)
        except Exception as e:
            messagebox.showerror("错误", f"处理失败：{str(e)}")
        finally:
            DBUtil.close(conn, cursor)
    
    # ========== 原有：冻结用户 + 新增：解冻用户 ==========
    def freeze_user():
        """冻结用户（原有逻辑）"""
        user_id = entry_user_id.get().strip()
        if not user_id:
            messagebox.showerror("错误", "用户ID不能为空！")
            return
        
        try:
            conn = DBUtil.get_connection()
            cursor = conn.cursor()
            # 调用存储过程
            cursor.callproc("sp_freeze_user41", (user_id,))
            result = cursor.fetchone()
            conn.commit()
            messagebox.showinfo("结果", result[0])
            entry_user_id.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("错误", f"冻结失败：{str(e)}")
        finally:
            DBUtil.close(conn, cursor)
    
    # 新增：解冻用户逻辑
    def unfreeze_user():
        """解冻用户"""
        user_id = entry_user_id.get().strip()
        if not user_id:
            messagebox.showerror("错误", "用户ID不能为空！")
            return
        
        try:
            conn = DBUtil.get_connection()
            cursor = conn.cursor()
            # 调用新增的解冻存储过程
            cursor.callproc("sp_unfreeze_user41", (user_id,))
            result = cursor.fetchone()
            conn.commit()
            messagebox.showinfo("结果", result[0])
            entry_user_id.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("错误", f"解冻失败：{str(e)}")
        finally:
            DBUtil.close(conn, cursor)
    
    # ========== 界面布局（新增解冻按钮） ==========
    # 左侧：物品管理（无修改）
    tk.Label(root_admin, text="物品管理（下架违规物品）", font=("宋体", 12, "bold")).place(x=20, y=50)
    
    # 物品列表
    columns_goods = ("物品ID", "物品名称", "类别", "发布者", "价格（元）", "状态")
    tree_goods = ttk.Treeview(root_admin, columns=columns_goods, show="headings", height=12)
    for col in columns_goods:
        tree_goods.heading(col, text=col, anchor='center')
        tree_goods.column(col, width=100, anchor='center')
    tree_goods.place(x=20, y=80, width=860)
    
    btn_offline = tk.Button(root_admin, text="下架选中物品", font=("宋体", 12), command=offline_goods)
    btn_offline.place(x=20, y=330)
    
    # 中间：投诉处理（无修改）
    tk.Label(root_admin, text="投诉处理", font=("宋体", 12, "bold")).place(x=20, y=370)
    
    # 投诉列表
    columns_complaint = ("投诉ID", "订单ID", "投诉用户", "投诉类别", "投诉时间")
    tree_complaints = ttk.Treeview(root_admin, columns=columns_complaint, show="headings", height=6)
    for col in columns_complaint:
        tree_complaints.heading(col, text=col)
        tree_complaints.column(col, width=120)
    tree_complaints.place(x=20, y=400, width=860)
    
    # 处理意见
    tk.Label(root_admin, text="处理意见：", font=("宋体", 12)).place(x=20, y=530)
    text_opinion = scrolledtext.ScrolledText(root_admin, font=("宋体", 12), width=60, height=3)
    text_opinion.place(x=100, y=530)
    
    btn_handle = tk.Button(root_admin, text="提交处理意见", font=("宋体", 12), command=handle_complaint)
    btn_handle.place(x=700, y=530)
    
    # 右侧：用户冻结/解冻（新增解冻按钮）
    tk.Label(root_admin, text="用户管理（冻结/解冻）", font=("宋体", 12, "bold")).place(x=650, y=300)
    tk.Label(root_admin, text="用户ID：", font=("宋体", 12)).place(x=650, y=330)
    entry_user_id = tk.Entry(root_admin, font=("宋体", 12), width=10)
    entry_user_id.place(x=720, y=330)
    
    # 原有冻结按钮 + 新增解冻按钮
    btn_freeze = tk.Button(root_admin, text="冻结用户", font=("宋体", 12), command=freeze_user, bg="#ffcccc")
    btn_freeze.place(x=650, y=360)
    
    btn_unfreeze = tk.Button(root_admin, text="解冻用户", font=("宋体", 12), command=unfreeze_user, bg="#ccffcc")
    btn_unfreeze.place(x=740, y=360)
    
    # 初始加载数据
    load_all_goods()
    load_unhandled_complaints()
    
    root_admin.mainloop()

if __name__ == "__main__":
    show_admin_window(2)