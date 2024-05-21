import streamlit as st
import pandas as pd
import os
import json
import numpy as np
import datetime
from functions import get_oldData
from datetime import date, timedelta
import pickle
import streamlit.components.v1 as components
st.set_page_config(
    page_title="Project Planning",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded", 
)
from PIL import Image
image = Image.open('logo.PNG')
headercol1,headercol2,co3=st.columns([2,10,4])
with headercol1 : st.image(image,)
with headercol2 : st.header(f":blue[Production Planning]")
st.markdown("""---""")
from functions import get_oldData
DataUpdate_Con = st.container()
ScheduleUpdateCon=st.container()
DashboardCon=st.container()
cwd = os.getcwd()
    #print (cwd)
path_file_vend=r"C:\Users\JSaurabh\OneDrive - Bectochem Consultant & Engineers Pvt ltd\Documents\MIS\purchase\vendor master.XLSX"
path_file_po=r"C:\Users\JSaurabh\OneDrive - Bectochem Consultant & Engineers Pvt ltd\Documents\MIS\purchase\ekko.XLSX"
path_file_stock=r"C:\Users\JSaurabh\OneDrive - Bectochem Consultant & Engineers Pvt ltd\Documents\MIS\purchase\Stock Statement.XLSX"

def updatevendor():
        #get ekko-POfile
        st.toast("Getting PO details")
        po_df=pd.read_excel(f"{path_file_po}",skiprows=1,names=
                            ["Purchasing Document","Vendor","Document Date"],usecols =[0,11,24],converters={'Vendor':str})
        st.toast("Getting Vendor details")
        vend_df=pd.read_excel(f"{path_file_vend}",skiprows=1,names=
                            ["Vendor","Vendor Name"],usecols =[0,2],converters={'Vendor':str})
        vend_df.dropna(inplace=True)
        st.toast("Recorsd Updated...")
        st.dataframe(po_df)
        st.dataframe(vend_df)
        df_merged_po = pd.merge(po_df,vend_df, 
                            on=("Vendor"),
                            how = 'left')
        st.dataframe(df_merged_po)
        df_merged_po.to_pickle("df_merged_po.pkl")

def getCurrentStock():
        st.toast("Updating Curret Stock details")
        stock_df=pd.read_excel(f"{path_file_stock}",names=
                            ["Material","Special Stock","Unrestricted"],usecols =[0,4,8])
        
        indexAge = stock_df[ (stock_df['Special Stock'] == "Q")].index
        stock_df.drop(indexAge , inplace=True)
        #st.dataframe(stock_df)
        stock_df['Unrestricted'] = stock_df['Unrestricted'].astype(float)
        stock_df = stock_df.groupby("Material")["Unrestricted"].sum()
        
        st.dataframe(stock_df)
        stock_df.to_pickle("df_stock.pkl")

def dashboardShow():
    st.subheader(f":blue[Dash Board]")
    link="https://app.powerbi.com/reportEmbed?reportId=e3237b53-66d0-468f-9262-92837b70b4d9&autoAuth=true&ctid=195e4e28-1e1f-42a6-8c38-c5cae3e4fdac"
    #link="https://app.powerbi.com/reportEmbed?reportId=fb462431-ca83-4dc4-b448-0222f21ecda8&autoAuth=true&ctid=195e4e28-1e1f-42a6-8c38-c5cae3e4fdac"
    components.iframe(link,height=600,width=800,
                  scrolling=True)

def ShowScheduleUpdate():
    df_merged=get_oldData()
    #st.session_state['getnew']=False
    today = date.today()
    st.subheader(f":blue[To Update Double Click on Due Date ...]")

    #st.dataframe(df_merged)
    col1,col2,col3  =st.columns(3)
    a_prowbs=["All"]
    prowbs=df_merged['WBS'].unique().tolist()
    a_prowbs.extend(prowbs)

    with col1:
        sb_project=st.selectbox("Select ProjectWBS",key="sb_project",options=a_prowbs)
        if sb_project!="All":
        #show allprojects else only selected
            prowbs=[sb_project]
    #st.data_editor(totaldf.loc[totaldf['WBS'] == sb_project],hide_index=True)
    with col2:
        a_category=["All"]
        category=df_merged['Category'].loc[df_merged['WBS'].isin(prowbs)].unique().tolist()
        a_category.extend(category)
        sb_category=st.selectbox("Select Category",key="sb_category",options=a_category)
        if sb_category!="All":
        #show allprojects else only selected
            category=[sb_category]
    with col3:
        a_items=["All"]
        items=df_merged['Description'].loc[df_merged['WBS'].isin(prowbs)].unique().tolist()
        a_items.extend(items)
        sb_item=st.selectbox("Select Item",key="sb_item",options=a_items)
        if sb_item!="All":
        #show allprojects else only selected
            items=[sb_item]
    with st.form("Update Schedule"):
        df_merged_cop=df_merged.loc[df_merged['WBS'].isin(prowbs)& 
                                    df_merged['Description'].isin(items)&
                                    df_merged['Category'].isin(category)
                                    ]
        def highlight(s):
            if s['Last Due Date'] <np.datetime64(today):
                return ['color: red']*len(s)
            elif s["REQ QTY."]<s["Unrestricted"]:
                return ['color: blue']*len(s)
            elif s['Last Due Date']is None:
                return ['background-color: yellow']*len(s)
            else:
                return ['background-color: white']*len(s)
        #df_merged_cop['REQ QTY.'] = df_merged_cop['REQ QTY.'].astype(float)
        df_merged_cop['PO/PR No.'] = df_merged_cop['PO/PR No.'].astype(int)
        df_merged_cop['Last Due_Date'] = df_merged_cop['Last Due Date'].dt.strftime('%d-%m-%Y')
        
        st.data_editor(
            df_merged_cop.style.apply(highlight, axis=1),
            column_config={
                "Due Date": st.column_config.DateColumn(
                    "Due Date",
                    min_value=today,
                    format="DD-MM-YYYY",
                    step=1,
                )
            },key="editabledf",hide_index=True,
            column_order=('WBS','Item Code','Description','REQ QTY.','Unit','Proj. Qty.','Category','PO/PR No.','Last Due_Date','Due Date','Vendor Name','Unrestricted','Seq','id'),
            disabled=('WBS','Item Code','Description','REQ QTY.','Unit','Proj. Qty.','Category','PO/PR No.','Seq','id','Vendor Name','Unrestricted','Last Due_Date')
        )
        
        submit=st.form_submit_button("Submit")
        if submit:
            st.toast("Updating...")
            #get edited fields
            keysList = list(st.session_state.editabledf['edited_rows'].keys())
            vals=[]
            for k in keysList:
                val=json.dumps(list(st.session_state.editabledf['edited_rows'][k].values()))
                #st.write(val[1:-1])
                vals.append(val[2:-2])
            
            counter=0
            if st.session_state['Role']=="Purchase":
                 rights=["PurRqs","POitem","ProjSt"]
            elif st.session_state['Role']=="Production":
                 rights=["PldOrd","PrdOrd"]
            else:
                 rights=["No Rights"]

            for n in keysList:
                indx=df_merged_cop.iloc[n]['id']-1
                if df_merged_cop.iloc[n]['Category'] in rights:
                    #st.write(n,counter)
                    #st.write(n,counter,indx)
                    df_merged.loc[indx,"Due Date"] =str(vals[counter])
                else:
                    
                    st.write(f"Row No {indx+1} not updated: Access not Allowed.")
                counter=counter+1
            
            #totaldf['Due Date'] = totaldf['Due Date'].astype(str)
            #st.dataframe(df_merged)
            df_merged.drop(["id"],inplace=True,axis=1)
            #df_merged.drop(["Seq"],inplace=True,axis=1)
            #df_merged.drop(["Vendor Name"],inplace=True,axis=1)
            #df_merged.drop(["Unrestricted"],inplace=True,axis=1)
            #df_merged.drop(["Last Due Date"],inplace=True,axis=1)
            #df_merged.to_json("project.json",orient='records',index=False)
            df_merged.to_excel("project.xlsx",index=False)
            st.toast("Updated Completed...")
            #now next time update Old database
            #st.session_state['genew']=True
        

def showDataUpdate():

    with DataUpdate_Con:
        st.subheader(f":blue[Update Master Data]")
        update=st.button("Update Master Data",key="update")
        if update:
            updatevendor()
            getCurrentStock()
            st.success("All Masters Updated ...")

def ScheduleUpdate():
    with ScheduleUpdateCon:
          ShowScheduleUpdate()

def Dashboard():
      with DashboardCon:
            dashboardShow()
# with st.container():
#     tab1,tab2,tab3 =st.tabs(["Update Master Data","Update Production Schedule","Dashboard"],)    
#     with tab1:
#         showDataUpdate()
#     with tab2:
#         ScheduleUpdate()
#     with tab3:
#         Dashboard()
with st.sidebar:
    prOptions=st.radio("",["Update Master Data","Update Production Schedule","Dashboard"],key="rop_production")
    if prOptions=="Update Master Data":
          showDataUpdate()
    elif prOptions=="Update Production Schedule":
          ScheduleUpdate()
    else:
          Dashboard()