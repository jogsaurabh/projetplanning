import streamlit as st
import pandas as pd
import os
import datetime
import re
from functions import update_user,delet_user,check_login,update_password,add_new_user,get_users
st.set_page_config(
    page_title="Project Planning",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded", 
)
regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
from PIL import Image
image = Image.open('logo.PNG')
headercol1,headercol2,co3=st.columns([2,10,4])
with headercol1 : st.image(image,)
with headercol2 : st.header(f":blue[Dec Bectochem Planning System]")

st.markdown("""---""")
#st.header(f":blue[Project Planning]")
headerSection = st.container()
mainSection = st.container()
loginSection = st.container()
logOutSection = st.container()
superadmin_con = st.container()
today=datetime.datetime.now()

def show_login_page():
    with loginSection:
        #with co3:st.write(f"User:-{st.session_state['User']} | Role:-{st.session_state['Role']}")
        tab1,tab2 =st.tabs(["Login ","   Change Password   "])
        with tab1:
            
            if st.session_state['loggedIn'] == False:
                #st.session_state['username'] = ''
                st.title(f":blue[Login]") 
                userName = st.text_input (label="User Name", value="", placeholder="Enter your user name",key="k1")
                password = st.text_input (label="Password", value="",placeholder="Enter password", type="password",key="k2")
                st.button ("Login", on_click=check_login, args= (userName, password))
                   
        with tab2:
            with st.form("New User",clear_on_submit=True):
                
                st.title(f":blue[Change Password]")
                userid = st.text_input (label="User Id", value="", placeholder="Enter your user ID",key="k5")
                password = st.text_input (label="Password", value="",placeholder="Enter Current Password", type="password",key="k6")
                new_pass = st.text_input (label="New Password", value="", placeholder="Enter New Password", type="password",key="k3")
                renew_pass = st.text_input (label="New Password", value="", placeholder="ReEnter New Password", type="password",key="k4")
                submit_user =st.form_submit_button("Submit")
                if submit_user:
                    if new_pass == renew_pass:
                        #createuser=create_user(displayname,userid,password,designation)
                        newpass=update_password(userid,password,new_pass)
                        st.toast(newpass)
                    else:
                        st.error('New Password and ReEntered Password not matching...')
                #st.form_submit_button("Submit",on_click=Register_Clicked, args= (userid, password,designation,displayname))
                #st.button ("Register", on_click=Register_Clicked, args= (userid, password,designation,displayname))

def add_new():
    placeholder = st.empty()
    def newlice(userid,username,password,role):
        #1st check email
        if(re.fullmatch(regex, userid)):
             clearfields=["usrid_ti","usrname_ti"]
             allfields= False
             for i in clearfields:
                  if len(st.session_state[f'{i}'])<1:
                    
                       allfields=True
             #if (len(names)<1 or len(names1)<1 or len(names2)<1):
             if allfields:
                st.toast("Enter All Manadtory Fields *")
             else:
                #now add record
                addrecord= add_new_user(st.session_state.usrid_ti,st.session_state.usrname_ti,st.session_state.password_ti,st.session_state.userrolsb)
                #placeholder.empty()
                
                if addrecord==True:
                    st.toast("Record Added Successfully...Continue to Add more", icon="👍")
                                
                else:
                    st.toast(f"Error:-{addrecord}", icon="👎")
                    st.toast("Try Again")
                #clear text fields on form
                for i in clearfields:
                        #st.write(st.session_state[f'{i}'])
                    st.session_state[f'{i}']=""
        else:
            #st.toast(email)
            st.toast("User ID not in email format...")


    with placeholder.container(border=True):
        
        st.subheader("Add New User")
        
        Userid=st.text_input(f"Enter User ID :red[*]",key="usrid_ti")
        UserName=st.text_input(f"Enter User Name :red[*]",key="usrname_ti")
        passwordst=st.text_input(f"Enter Default Password :red[*]",key="password_ti")
        role=st.selectbox("Assign Role",options=["Admin","View","Purchase","Production","Projects"],key="userrolsb")
        
        st.button("Submit",on_click=newlice,
                                    args=[Userid,UserName,passwordst,role])

def view_user():
    vew_lic_con  = st.empty()
    with vew_lic_con.container(border=True):
        st.subheader("List of Users")
        df=get_users()
        if isinstance(df, pd.DataFrame):
            st.dataframe(df,hide_index=True)
        else:
            st.toast(df)
            st.toast("error")   

def del_user():
    del_lic_con  = st.empty()

    #def updatelic(name,Expiry_Date,time_zone,email):
    
    with del_lic_con.container(border=True):
        st.subheader("Delete User")
        st.info("Select Rows to Delete...")
        df=get_users()
        if df is False:
            st.toast(f"No records...{df}")
        else:
            if "df" not in st.session_state:
                st.session_state.df = pd.DataFrame()
            # Get dataframe row-selections from user with st.data_editor
            df.insert(0, "Select", False)
            edited_df = st.data_editor(
                df,
                hide_index=True,
                column_config={"Select": st.column_config.CheckboxColumn(required=True)},
                disabled=st.session_state.df.columns,key="seldfdel"
            )
            # Filter the dataframe using the temporary column, then drop the column
            selected_rows = edited_df[edited_df.Select]
            selected_rows= selected_rows.drop('Select', axis=1)
            if len(selected_rows)>0:
                col1, col2= st.columns([3,1])
                with col1: 
                    st.error("Are you Sure you want to Delete following rows:")
                    st.dataframe(selected_rows,hide_index=True)
                with col2:
                    
                    mylist=selected_rows["id"].tolist()
                    tnewlist=tuple(mylist)
                    #st.write(mylist)
                    #st.write(tnewlist)
                    yesbutton=st.button("Yes",key="yes",on_click=delet_user,args=(mylist,tnewlist))
    
def user_update():
    update_lic_con  = st.empty()
    
    def updatelic(userid,username,role):
        uplic= update_user(userid,username,role)
                #placeholder.empty()
                
        if uplic==True:
            st.toast("Record Updated Successfully...", icon="👍")
            st.session_state.selemail="------"
                        
        else:
            st.toast(f"Error:-{uplic}", icon="👎")
            st.toast("Try Again")
        
    with update_lic_con.container(border=True):
        st.subheader("Update User")
        df=get_users()
        st.dataframe(df)
        email_list = df["User ID"].tolist()
        #add item at beginning of list 
        email_list.insert(0,"------")
        email_sel=st.selectbox("Select User ID to Update Record",options=email_list,key="selemail",placeholder="Choose as Option")
        if email_sel !="------":
            #get data for selected email& show as default value of widgets
            #name=df.query(f"email=='{email_sel}'")["name"].item()
            name=df['User Name'][df['User ID'] == email_sel].values[0]
            role=df['Role'][df['User ID'] == email_sel].values[0]
            #name=df.query(f"User ID=='{email_sel}'")["User Name"].item()
            #role=df.query(f"User ID=='{email_sel}'")["Role"].item()
            #time_zone=df.query(f"User Id=='{email_sel}'")["time_zone"].item()
            #st.write(name,Expiry_Date,time_zone)
            mname=st.text_input(f"Update User Name :red[*]",value=name,key="upname")
            mRole=st.selectbox("Assign Role",options=["Admin","View","Purchase","Production","Projects"],key="userrolsb1",placeholder=role)
            
            if len(mname)>1:
                st.button("Update",key="upadtelic",on_click=updatelic,args=[email_sel,mname,mRole])

def show_view():
    st.write(f"Welcom: {st.session_state['UserName']} |Role: {st.session_state['Role']}")
    
    

def show_admin():
    st.write(f"{st.session_state['UserName']} | {st.session_state['Role']} |")
    add_t,view_t, modify_t,del_t= st.tabs(["✔️**Add New**","📋**View**","✏️**Update**","❌Delete"])
    with add_t:
        add_new()
    with view_t:
        view_user()
    with modify_t:
        user_update()
    with del_t:
        del_user()

def LoggedOut_Clicked():
    st.session_state['loggedIn'] = False

def show_logout_page():
    loginSection.empty()
    with logOutSection:
        st.sidebar.button ("Log Out", key="logout", on_click=LoggedOut_Clicked)

#main login code
with headerSection:
    # for login checking
    if 'User' not in st.session_state:
        st.session_state['User'] = ""
    
    if 'UserName' not in st.session_state:
        st.session_state['UserName'] = ""
    
    if 'Role' not in st.session_state:
        st.session_state['Role'] = ""
    
    if 'loggedIn' not in st.session_state:
        st.session_state['loggedIn'] = False
        show_login_page()
                
    else:
        if st.session_state['loggedIn']:
            show_logout_page()   
            if st.session_state['Role'] == "View":
                show_view()
            elif st.session_state['Role'] == "Purchase":
                show_view()
            elif st.session_state['Role'] == "Production":
                show_view()
            elif st.session_state['Role'] == "Projects":
                show_view()
            else:
                #st.session_state['Role'] =="Admin":
                show_admin()
            
        else:
            show_login_page()
