import streamlit as st
import pandas as pd
import os
import sqlite3
import numpy as np

def get_oldData():

    cwd = os.getcwd()
    path_file=r"C:\Users\JSaurabh\OneDrive - Bectochem Consultant & Engineers Pvt ltd\Documents\MIS\co46"
    #Get all excel files in path folder for monthly sales
    #dfold=pd.read_json('project.json')
    oldcolumnames=['WBS','Item Code','Description','REQ QTY.','Unit','Proj. Qty.','Category','PO/PR No.','Due Date']
    dfold=pd.read_excel('project.xlsx',names=
                                oldcolumnames,usecols =[0,1,2,3,4,5,6,7,10])
    
    column_names = ['WBS','Item Code','Description','REQ QTY.','Unit','Proj. Qty.','Category','PO/PR No.']
    dfold[column_names]=dfold[column_names].fillna(0)
    
    str_column_names = ['WBS','Item Code','Description','Unit','Category']
    for col in str_column_names:
         dfold[col]=dfold[col].str.strip()
    #dfold.replace(r'^\s*$', np.nan, regex=True)
    dfold['Due Date'] = pd.to_datetime(dfold['Due Date'])
    dfold.rename({'Due Date': 'Last Due Date'}, axis=1, inplace=True)
    
    #st.dataframe(dfold)
    dfold['Seq'] = dfold.groupby(column_names).cumcount().add(1)
    
    dfold['REQ QTY.'] = dfold['REQ QTY.'].astype(float)
    #st.dataframe(dfold)
    #ge new files
    filelist=[]
    files = os.listdir(path_file)
    df=pd.DataFrame(columns = column_names)
    for file in files:
        if not file.startswith('~$'):
            if file.endswith('.xlsx') :
                filelist.append(file)
                        
    number_of_files=len(filelist)
    # Read all excel files and save to dataframe 

    totaldf=pd.DataFrame()
    for i in range(number_of_files):
        try:
            #st.write(path_file+r''+filelist[i])
            df=pd.read_excel(f"{path_file}\{filelist[i]}",skiprows=1,names=
                                column_names,usecols =[0,1,2,3,4,5,6,7])
            
            #add colum for monthname of that file
            fname=filelist[i][:-5]
            #st.write(fname)
            df['WBS'] = df['WBS'].fillna(fname)  
            #drop NA  Description
            df.dropna(subset = ['Description'], inplace=True)
            
            totaldf = pd.concat([totaldf, df], ignore_index=True)
            
            #st.dataframe(totaldf)
            
        except Exception as e:
            st.toast(f'{e}Erro in Importing Excel file!')
            #return(df)

    totaldf[column_names]=totaldf[column_names].fillna(0)
    totaldf['Seq'] = totaldf.groupby(column_names).cumcount().add(1)
    totaldf['REQ QTY.'] = totaldf['REQ QTY.'].astype(float)
    for col in str_column_names:
         totaldf[col]=totaldf[col].str.strip()
    #Add Vendors name from PO file

    vendor_df=pd.read_pickle("df_merged_po.pkl")
    #st.write(vendor_df)
    column_names.append("Seq")
    #st.dataframe(totaldf)
    df_merged = pd.merge(totaldf,dfold, 
                            on=column_names,
                            how = 'left')
    
    df_merged["id"] = df_merged.index + 1
    #st.dataframe(df_merged)
    # def calc_new_col(row):
    #         return row['Last Due Date']
    #df_merged["Due Date"]=df_merged.apply(calc_new_col, axis=1)
    df_merged["Due Date"] = df_merged['Last Due Date']
    #merge to get Vendors
    df_merged=pd.merge(df_merged,vendor_df[["Purchasing Document","Vendor Name"]],
                    left_on="PO/PR No.",right_on="Purchasing Document",
                    how='left').drop(columns = ['Purchasing Document'])
    #get stock details
    stock_df=pd.read_pickle("df_stock.pkl")

    df_merged=pd.merge(df_merged,stock_df,
                    left_on="Item Code",right_on="Material",
                    how='left')
    return (df_merged)
db_path='login.db'

def check_login(username,password) :
    try:
        sqliteConnection = sqlite3.connect(db_path)
        if username!="admin":
                    #sqliteConnection = sqlite3.connect(gdruve)
                    cursor = sqliteConnection.cursor()
                    cursor.execute(f"SELECT password from users where [User ID]='{username}'")
                    passworddb=cursor.fetchone()
                    #print(passworddb[0])
                    cursor.close()
                    #sqliteConnection.close()
                    #st.write(passworddb[0])
                    if passworddb:
                        if passworddb[0]==password:
                            st.session_state['loggedIn'] = True
                            st.session_state['User']=username
                            cursor = sqliteConnection.cursor()
                            cursor.execute(f"SELECT Role from users where [User ID]='{username}'")
                            roledb=cursor.fetchone()
                            #print(passworddb[0])
                            cursor.close()
                            cursor = sqliteConnection.cursor()
                            cursor.execute(f"SELECT [User Name] from users where [User ID]='{username}'")
                            usernamedb=cursor.fetchone()
                            #print(passworddb[0])
                            cursor.close()
                            #sqliteConnection.close()
                            st.session_state['UserName']=usernamedb[0]
                            st.session_state['Role']=roledb[0]
                            st.session_state['User']=username[0]
                            
                            return True
                        else:
                            st.session_state['loggedIn'] = False
                            st.toast("Invalid password")
                            return False
                    else:
                        st.session_state['loggedIn'] = False
                        st.success("Invalid user name ")
                        return False
            
        else:   
            if password=="AcePro123":
                #st.success("Admin")
                st.session_state['loggedIn'] = True
                st.session_state['User']="admin"
                st.session_state['UserName']="admin"
                st.session_state['Role']="Admin"
                
                return True
            else:
                st.toast("Invalid password")
                return False

               
    except sqlite3.Error as error:
        if sqliteConnection:
            sqliteConnection.close()
        st.toast(error)
        return False
    except :
        st.toast("Error...")
        return False

    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")

def update_password(usrid,oldpass,newpass):
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        #check if user id & password is correct
        cursor.execute(f"SELECT Password from users where [User ID]='{usrid}'")
        passworddb=cursor.fetchone()
        #print(passworddb[0])
        cursor.close()
        #sqliteConnection.close()
        #st.write(passworddb[0])
        if newpass : newpass=newpass.replace("'","''")
        if passworddb:
            if passworddb[0]==oldpass:
                cursor = sqliteConnection.cursor()
                query=f"UPDATE users SET Password ='{newpass}' WHERE [User ID] ='{usrid}'"
                cursor.execute(query)
                sqliteConnection.commit()
                cursor.close()
                        
                        # update with new password
               
                updatereply="Password Changed...."
            else:
                
                updatereply="Invalid Password"
        else:
            #st.session_state['loggedIn'] = False
            updatereply="Invalid user name "
                
    except sqlite3.Error as error:
        updatereply=error
    except :
        updatereply="Run time Error...Invalid Input or Data type Mismatch"
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
    return updatereply

def add_new_user(userid,username,password,role):
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        #st.success("Done1")
        #add DS name in table
        sqlite_insert_with_param = """INSERT INTO users
                          ([User ID],[User Name],Password,Role) 
                          VALUES (?,?,?,?);"""
        data_tuple = (userid,username,password,role)
        #st.success("Done2")
        cursor.execute(sqlite_insert_with_param, data_tuple)
        sqliteConnection.commit()
        cursor.close()
        return True
    except sqlite3.Error as error:
        message_verify=error
        return message_verify
    except Exception as e:
        message_verify=e
        return e
    finally:
        if sqliteConnection:
            sqliteConnection.close()

def get_users():
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        query="SELECT * from users"
        sql_query=pd.read_sql_query(query,sqliteConnection)
        cursor.close()
        return sql_query
    
    except Exception as e:
        return e
    finally:
        if sqliteConnection:
            sqliteConnection.close()

def delet_user(mylist,tnewlist):
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        #update audit status
        if len(mylist)>1:
            query=f"DELETE from users where id in{tnewlist}"
        else:
            query=f"DELETE from users where id={mylist[0]}"
        #query=f"SELECT Review from Audit_AR where DataSetName='{DsName}' AND CompanyName='{comp_name}'"
        #st.write(query)
        cursor.execute(query)
        sqliteConnection.commit()
        cursor.close()
        st.toast(f'Records Deleted...')
        return True
    except sqlite3.Error as error:
        st.toast(f'{error}')
        return error
    except Exception as e:
        st.toast(f'{e}')
        return e 
    finally:
        if sqliteConnection:
            sqliteConnection.close()

def update_user(userid,username,role):

    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        #update audit status
        query=f"UPDATE users SET [User Name] ='{username}', Role='{role}' WHERE [User Id] = '{userid}'"
        #query=f"SELECT Review from Audit_AR where DataSetName='{DsName}' AND CompanyName='{comp_name}'"
        #st.write(query)
        cursor.execute(query)
        sqliteConnection.commit()
        cursor.close()
        return True
    except sqlite3.Error as error:
        return error
    except Exception as e:
        return e 
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")

