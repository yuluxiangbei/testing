import tkinter as tk
from tkinter import messagebox
import hashlib
from utils.db_util import DBUtil
from views.user_view import show_user_window
from views.admin_view import show_admin_window
import pymysql
def show_login_window():
    """显示登录窗口（优化注册回调）"""
    current_user = None  # 存储当前登录用户信息
    
    def do_login():
        """执行登录逻辑（无修改）"""
        username = entry_username.get().strip()
        password = entry_pwd.get().strip()
        
        if not username or not password:
            messagebox.showerror("错误", "用户名和密码不能为空！")
            return
        
        # 密码加密
        md5 = hashlib.md5()
        md5.update(password.encode('utf8'))
        pwd_md5 = md5.hexdigest()
        
        try:
            conn = DBUtil.get_connection()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            
            # 查询用户
            cursor.execute("""
                SELECT user_id, username, role, status 
                FROM `user41` 
                WHERE username = %s AND password = %s
            """, (username, pwd_md5))
            user = cursor.fetchone()
            
            if not user:
                messagebox.showerror("错误", "用户名或密码错误！")
                return
            
            # 检查账号状态
            if user["status"] == "frozen":
                messagebox.showerror("错误", "账号已被冻结，无法登录！")
                return
            
            current_user = user
            messagebox.showinfo("成功", f"欢迎{username}登录！")
            root_login.destroy()
            
            # 根据角色打开对应窗口
            if user["role"] == "admin":
                show_admin_window(user["user_id"])
            else:
                show_user_window(user["user_id"])
                
        except Exception as e:
            messagebox.showerror("错误", f"登录失败：{str(e)}")
        finally:
            DBUtil.close(conn, cursor)
    
    def open_register():
        """打开注册窗口（传递返回回调）"""
        root_login.destroy()
        from views.register_view import show_register_window
        show_register_window(show_login_window)  # 注册后返回登录页
    
    # 登录窗口初始化
    root_login = tk.Tk()
    root_login.title("校园二手平台 - 登录")
    root_login.geometry("400x300")
    root_login.resizable(False, False)
    
    # 用户名
    tk.Label(root_login, text="用户名：", font=("宋体", 14)).place(x=80, y=60)
    entry_username = tk.Entry(root_login, font=("宋体", 14), width=20)
    entry_username.place(x=150, y=60)
    
    # 密码
    tk.Label(root_login, text="密  码：", font=("宋体", 14)).place(x=80, y=120)
    entry_pwd = tk.Entry(root_login, font=("宋体", 14), width=20, show="*")
    entry_pwd.place(x=150, y=120)
    
    # 登录按钮
    btn_login = tk.Button(root_login, text="登录", font=("宋体", 12), width=10, command=do_login)
    btn_login.place(x=120, y=180)
    
    # 注册按钮
    btn_register = tk.Button(root_login, text="注册", font=("宋体", 12), width=10, command=open_register)
    btn_register.place(x=220, y=180)
    
    root_login.mainloop()

if __name__ == "__main__":
    show_login_window()