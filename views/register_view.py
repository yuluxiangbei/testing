import tkinter as tk
from tkinter import messagebox
import hashlib
import re  # 新增：正则表达式校验
from utils.db_util import DBUtil
import pymysql
def show_register_window(return_callback):  # 新增：接收返回回调函数
    """显示注册窗口（新增返回按钮+手机号/邮箱校验）"""
    def do_register():
        """执行注册逻辑（新增格式校验）"""
        username = entry_username.get().strip()
        password = entry_pwd.get().strip()
        confirm_pwd = entry_confirm_pwd.get().strip()
        role = var_role.get()
        phone = entry_phone.get().strip()
        email = entry_email.get().strip()
        
        # 基础校验
        if not username or not password:
            messagebox.showerror("错误", "用户名和密码不能为空！")
            return
        if password != confirm_pwd:
            messagebox.showerror("错误", "两次输入的密码不一致！")
            return
        
        # 新增：手机号格式校验（非空时校验）
        if phone:
            phone_pattern = r'^1[3-9]\d{9}$'  # 中国大陆手机号规则
            if not re.match(phone_pattern, phone):
                messagebox.showerror("错误", "手机号格式不正确（请输入11位有效手机号）！")
                return
        
        # 新增：邮箱格式校验（非空时校验）
        if email:
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                messagebox.showerror("错误", "邮箱格式不正确（例：user@example.com）！")
                return
        
        # 密码加密（MD5）
        md5 = hashlib.md5()
        md5.update(password.encode('utf8'))
        pwd_md5 = md5.hexdigest()
        
        try:
            conn = DBUtil.get_connection()
            cursor = conn.cursor()
            
            # 检查用户名是否已存在
            cursor.execute("SELECT * FROM `user41` WHERE username = %s", (username,))
            if cursor.fetchone():
                messagebox.showerror("错误", "用户名已存在！")
                return
            
            # 插入用户数据
            sql = """
                INSERT INTO `user41` (username, password, role, phone, email) 
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (username, pwd_md5, role, phone, email))
            conn.commit()
            
            messagebox.showinfo("成功", "注册成功！请登录")
            root_register.destroy()
            return_callback()  # 注册成功后返回登录页
        except Exception as e:
            messagebox.showerror("错误", f"注册失败：{str(e)}")
        finally:
            DBUtil.close(conn, cursor)
    
    def on_return():
        """返回按钮逻辑"""
        if messagebox.askokcancel("提示", "确定返回登录页吗？未保存的信息将丢失"):
            root_register.destroy()
            return_callback()
    
    # 注册窗口初始化
    root_register = tk.Tk()
    root_register.title("校园二手平台 - 用户注册")
    root_register.geometry("450x420")
    root_register.resizable(False, False)
    
    # 新增：返回按钮
    btn_return = tk.Button(root_register, text="返回", font=("宋体", 10), command=on_return)
    btn_return.place(x=10, y=10)
    
    # 用户名
    tk.Label(root_register, text="用户名：", font=("宋体", 12)).place(x=80, y=40)
    entry_username = tk.Entry(root_register, font=("宋体", 12), width=25)
    entry_username.place(x=150, y=40)
    
    # 密码
    tk.Label(root_register, text="密码：", font=("宋体", 12)).place(x=80, y=90)
    entry_pwd = tk.Entry(root_register, font=("宋体", 12), width=25, show="*")
    entry_pwd.place(x=150, y=90)
    
    # 确认密码
    tk.Label(root_register, text="确认密码：", font=("宋体", 12)).place(x=80, y=140)
    entry_confirm_pwd = tk.Entry(root_register, font=("宋体", 12), width=25, show="*")
    entry_confirm_pwd.place(x=150, y=140)
    
    # 角色选择
    tk.Label(root_register, text="角色：", font=("宋体", 12)).place(x=80, y=190)
    var_role = tk.StringVar(value="user")
    tk.Radiobutton(root_register, text="普通用户", variable=var_role, value="user", font=("宋体", 10)).place(x=150, y=190)
    tk.Radiobutton(root_register, text="管理员", variable=var_role, value="admin", font=("宋体", 10)).place(x=250, y=190)
    
    # 手机号（新增格式提示）
    tk.Label(root_register, text="手机号：", font=("宋体", 12)).place(x=80, y=240)
    entry_phone = tk.Entry(root_register, font=("宋体", 12), width=25)
    entry_phone.place(x=150, y=240)
    tk.Label(root_register, text="（选填，11位手机号）", font=("宋体", 9), fg="gray").place(x=350, y=243)
    
    # 邮箱（新增格式提示）
    tk.Label(root_register, text="邮箱：", font=("宋体", 12)).place(x=80, y=290)
    entry_email = tk.Entry(root_register, font=("宋体", 12), width=25)
    entry_email.place(x=150, y=290)
    tk.Label(root_register, text="（选填，例：user@xxx.com）", font=("宋体", 9), fg="gray").place(x=350, y=293)
    
    # 注册按钮
    btn_register = tk.Button(root_register, text="注册", font=("宋体", 12), width=10, command=do_register)
    btn_register.place(x=180, y=340)
    
    root_register.mainloop()

if __name__ == "__main__":
    show_register_window(lambda: print("返回登录页"))  # 测试回调