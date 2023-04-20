import os
import gspread
from google.oauth2.service_account import Credentials
import streamlit as st
import pandas as pd
import numpy as np

if "invia" not in st.session_state:
    st.session_state.invia = False

if "scopri" not in st.session_state:
    st.session_state.scopri = False

#funzioni eCom
def find_user_row(sheet, email):
    rows = sheet.get_all_values()
    for index, row in enumerate(rows):
        if row[0] == email:
            return index + 1
    return None

# credenziali Sheet API
base_dir = os.path.dirname(os.path.abspath(__file__))
creds_file_path = os.path.join(base_dir, 'credentials.json')
scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
creds = Credentials.from_service_account_file(creds_file_path, scopes=scope)
file = gspread.authorize(creds)

# Sheet FIle ID
sheet = file.open_by_key('1tTAfCdqyD7ecXTSnFHmDPLLcdsIdCCcgZzGFIjPhzXk').sheet1


# Sidebar per Login e SignUP
menu = st.sidebar.selectbox('Menu', ['Sign Up', 'Log In'])

if menu == 'Sign Up':
    st.write('Create an account to access your analysis')
    email = st.sidebar.text_input('indirizzo email', key='signup_username')
    password = st.sidebar.text_input('Password', type='password', key='signup_password')
    fatturato= st.sidebar.text_input('Fatturato medio mensile', key='fatturato_medio')
    sito= st.sidebar.text_input('Sito Web', key='sito_web')
    submit = st.sidebar.button('Sign Up')

    # Se lo username è già stato
    if submit:
        cell_list = sheet.findall(email, in_column=1)
        if len(cell_list) > 0:
            st.sidebar.warning('Sorry, that username is already taken. Please try again with a different username.')
        else:
            sheet.append_row([email, password,fatturato,sito,0])
            st.sidebar.write(f'Successfully signed up as {email}! Please go to the Log In section to continue.')

elif menu == 'Log In':
    login_subheader = st.sidebar.subheader('Enter your username and password to log in:')
    email = st.sidebar.text_input('Email', key='login_username')
    password = st.sidebar.text_input('Password', type='password', key='login_password')
    submit = st.sidebar.checkbox('Log In')

    # Check tra Login data e DB
    if submit:
        cell_list = sheet.findall(email, in_column=1)
        if len(cell_list) == 0:
            st.sidebar.warning('Incorrect username or password. Please try again.')
        else:
                st.title('Benvenuto! Con il Calcolatore eCommerce di Hybrida Marketing puoi scoprire queste metriche:')

                st.markdown("""
                - AOV dei nuovi clienti
                - AOV dei clienti di ritorno
                - Tassi di riacquisto tra 1 e 2 acquisto
                - Tasso di riacquisto tra 2 e 3 acquisto
                - Costo acquisizione cliente overall

                Ecco come:
                Per scoprire questi dati devi avere il tuo export ordini strutturato in questo modo:

                - order_id	
                - customer_id : Deve contenere o Nome e Cognome del cliente oppure ID oppure email
                - order_total : il totale pagato. Non deve avere il simbolo dell'euro e come segno decimale deve avere il punto
                - order_date : data di ordine con il formato YYYY-MM-DD
                """)


                video_path='https://www.loom.com/share/521b9bfc03844421b556776dc7a6bac2'
                st.markdown(f'<a href="{video_path}"> Clicca qui per vedere come fare questo export Clienti da Shopify</a>', unsafe_allow_html=True)

                video_wordpress='https://www.loom.com/share/ac8bebac1793447f938806725dc4fd5c'
                st.markdown(f'<a href="{video_wordpress}"> Clicca qui per vedere come fare questo export Clienti da Woocommerce</a>', unsafe_allow_html=True)

                file=st.file_uploader('Carica il tuo file CSV Clienti')
                file_path='https://docs.google.com/spreadsheets/d/1stEgE4vlaY65MPQ1obn5MFUwLcbc2JMlwv8Dd5W2PIY/export?format=csv'
                st.markdown(f'<a href="{file_path}" download> Clicca qui per scaricare un CSV di esempioe</a>', unsafe_allow_html=True)
                st.write("") 
                st.write("") 
                budget=st.number_input('Inserisci qui il budget speso negli ultimi 3 mesi')

                invia=st.button('Invia il tuo file')
                

                invia_clicked = st.session_state.get("invia_clicked", False)

                if invia:
                    invia_clicked = not invia_clicked
                    st.session_state.invia_clicked = invia_clicked

                if invia_clicked:
                    df=pd.read_csv(file)
                    df['order_date']=pd.to_datetime(df['order_date'])
                    df['mese'] = df['order_date'].dt.strftime('%Y-%m')
                    first_order_date = df.groupby("customer_id")["order_date"].min()
                    df["primo_ordine"] = df["customer_id"].map(first_order_date)
                    df['order_type'] = np.where(df['order_date'] == df['primo_ordine'], 'New', 'Recurring')
                    df2=df[df['order_type']=='New'].groupby('mese')['order_id'].count()
                    nuoviclienti=np.mean(df2.iloc[-3:])
                    CAC=round(budget/nuoviclienti,2)
                    client = df['customer_id'].nunique()
                    orders_per_customer = df.groupby('customer_id')['order_id'].count()
                    dueordini = (orders_per_customer > 1).sum()
                    treordini = (orders_per_customer > 2).sum()
                    reprate_12 = round(dueordini / client *100,2)
                    reprate_23 = round(treordini / dueordini *100,2)

                    df2=df
                    client = df2['customer_id'].nunique()

                    orders_per_customer = df.groupby('customer_id')['order_id'].count()
                    dueordini = (orders_per_customer > 1).sum()
                    treordini = (orders_per_customer > 2).sum()
                    reprate_12 = round(dueordini / client *100,2)
                    reprate_23 = round(treordini / dueordini *100,2)

                    df3=df
                    df3['mese'] = df3['order_date'].dt.strftime('%Y-%m')
                    first_order_date = df3.groupby("customer_id")["order_date"].min()
                    df3["primo_ordine"] = df3["customer_id"].map(first_order_date)
                    df3['order_type'] = np.where(df3['order_date'] == df3['primo_ordine'], 'New', 'Recurring')
                    data=df3[df3['order_type']=='New'].groupby('mese')['order_id'].count()
                    nuoviclienti=np.mean(data.iloc[-3:])
                    CAC=round(budget/nuoviclienti,2)

                    df4=df
                    df4['mese'] = df4['order_date'].dt.strftime('%Y-%m')
                    first_order_date = df4.groupby("customer_id")["order_date"].min()
                    df4["primo_ordine"] = df4["customer_id"].map(first_order_date)
                    df4['order_type'] = np.where(df4['order_date'] == df4['primo_ordine'], 'New', 'Recurring')
                    data2=df4[df4['order_type']=='New'].groupby('mese')['order_id'].count()
                    nuoviclienti=np.mean(data2.iloc[-3:])
                    CAC=round(budget/nuoviclienti,2)

                    df5=df
                    first_order_date = df5.groupby("customer_id")["order_date"].min()
                    df5["primo_ordine"] = df5["customer_id"].map(first_order_date)
                    df5['order_type'] = np.where(df5['order_date'] == df5['primo_ordine'], 'New', 'Recurring')
                    data3=df5.groupby('order_type')['order_total','order_id'].agg({'order_total': 'sum', 'order_id': 'count'})
                    data3['aov']=round(data3['order_total']/(data3['order_id']),2)

                    st.title('Ecco i tuoi dati:')

                    st.write (f'Il {reprate_12}% dele persone fa più di un ordine')
                    st.write (f'Il {reprate_23}% dele persone che ha fatto 2 ordini, ha fatto almeno un terzo ordine')
                    st.write(f'Negli ultimi 3 mesi hai avuto un CAC di {CAC}€')
                    st.table(data3)

                    st.markdown("""
                    Puoi scoprire altre informazioni come:
                    - LTV a seconda di quale prodotto viene acquistato per primo
                    - Tempo di riacquisto medio tra ogni acquisto
                    - Costo Acquisizione Cliente dai canali Paid
                    - Numero di ordini medi per cliente
                    - Scoprire se con le Ads stai acquisendo clienti ricorrenti
                    Clicca qui sotto
                    """)
                    
                    scopri = st.button("Iscriviti alla waiting list", key="buttone")
                    scopri_clicked = st.session_state.get("scopri_clicked", False)

                    if scopri:
                        scopri_clicked = not scopri_clicked
                        st.session_state.scopri_clicked = scopri_clicked

                    if scopri_clicked:
                        user_row = cell_list[0].row
                        upload_count = sheet.cell(user_row, 5).value
                        sheet.update_cell(user_row, 5, 1)
                        st.write("Perfetto! Ti contatteremo quanto prima con tutto il file di LTV")






