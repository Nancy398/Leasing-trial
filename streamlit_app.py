import streamlit as st
import pandas as pd

# 数据文件路径
USERS_FILE = "users.csv"
# DEALS_FILE = "data/deals.csv"
# FEEDBACKS_FILE = "data/feedbacks.csv"

# 读取数据
users_df = pd.read_csv(USERS_FILE)
# deals_df = pd.read_csv(DEALS_FILE)
# feedbacks_df = pd.read_csv(FEEDBACKS_FILE)

# 保存数据
def save_data(df, file_path):
    df.to_csv(file_path, index=False)

# Streamlit 应用主入口
def main():
    st.title("佣金计算系统")

    # 登录或注册界面选择
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        option = st.sidebar.selectbox("选择操作", ["登录", "注册"])

        if option == "登录":
            login()
        elif option == "注册":
            register()

        return

    # 已登录用户界面
    st.sidebar.header(f"欢迎, {st.session_state.user['name']}")
    if st.sidebar.button("退出登录"):
        st.session_state.logged_in = False
        return

    # 根据角色显示对应界面
    if st.session_state.user["role"] == "admin":
        admin_dashboard()
    else:
        sales_dashboard()

# 登录功能
def login():
    st.sidebar.header("登录")
    username = st.sidebar.text_input("用户名")
    password = st.sidebar.text_input("密码", type="password")
    if st.sidebar.button("登录"):
        user = authenticate(username, password)
        if user:
            st.session_state.logged_in = True
            st.session_state.user = user
            st.success(f"欢迎 {user['name']}！")
        else:
            st.sidebar.error("用户名或密码错误！")

# 注册功能
def register():
    st.sidebar.header("注册")
    name = st.sidebar.text_input("姓名")
    username = st.sidebar.text_input("用户名")
    password = st.sidebar.text_input("密码", type="password")
    role = st.sidebar.radio("角色", ["sales", "admin"], format_func=lambda x: "销售" if x == "sales" else "管理员")

    if st.sidebar.button("注册"):
        if not name or not username or not password:
            st.sidebar.error("请填写所有字段！")
        elif username_exists(username):
            st.sidebar.error("用户名已存在！")
        else:
            new_user = {"username": username, "password": password, "name": name, "role": role}
            add_user(new_user)
            st.sidebar.success("注册成功！请返回登录。")

# 检查用户名是否存在
def username_exists(username):
    return not users_df[users_df["username"] == username].empty

# 添加新用户
def add_user(user):
    global users_df
    users_df = users_df.append(user, ignore_index=True)
    save_data(users_df, USERS_FILE)

# 用户身份验证
def authenticate(username, password):
    user = users_df[(users_df["username"] == username) & (users_df["password"] == password)]
    if not user.empty:
        return user.iloc[0].to_dict()
    return None

# 销售界面
def sales_dashboard():
    global deals_df, feedbacks_df
    user = st.session_state.user
    st.header("销售界面")

    # 查看自己的成单
    user_deals = deals_df[deals_df["sales"] == user["username"]]
    st.subheader("我的成单")
    st.table(user_deals)

    # 提交反馈
    st.subheader("提交反馈")
    selected_deal_id = st.selectbox("选择要反馈的成单", user_deals["id"])
    feedback = st.text_area("反馈内容", "")
    if st.button("提交反馈"):
        if feedback:
            new_feedback = {"id": len(feedbacks_df) + 1, "sales": user["username"], "deal_id": selected_deal_id, "feedback": feedback, "status": "待处理"}
            feedbacks_df = feedbacks_df.append(new_feedback, ignore_index=True)
            save_data(feedbacks_df, FEEDBACKS_FILE)
            st.success("反馈提交成功！")
        else:
            st.warning("请输入反馈内容。")

    # 查看自己提交的反馈
    st.subheader("我的反馈")
    user_feedbacks = feedbacks_df[feedbacks_df["sales"] == user["username"]]
    st.table(user_feedbacks)

# 管理员界面
def admin_dashboard():
    global feedbacks_df
    st.header("管理员界面")

    # 查看所有反馈
    st.subheader("所有反馈")
    all_feedbacks = feedbacks_df
    st.table(all_feedbacks)

    # 更新反馈处理状态
    st.subheader("处理反馈")
    feedback_id = st.selectbox("选择反馈ID", all_feedbacks["id"])
    feedback_status = st.radio("反馈状态", ["待处理", "已处理"], index=0 if all_feedbacks[all_feedbacks["id"] == feedback_id]["status"].values[0] == "待处理" else 1)
    if st.button("更新状态"):
        feedbacks_df.loc[feedbacks_df["id"] == feedback_id, "status"] = feedback_status
        save_data(feedbacks_df, FEEDBACKS_FILE)
        st.success("反馈状态更新成功！")

if __name__ == "__main__":
    main()
