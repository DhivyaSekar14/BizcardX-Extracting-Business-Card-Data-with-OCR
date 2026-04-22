import streamlit as st
from streamlit_option_menu import option_menu
import easyocr
from PIL import Image
import pandas as pd
import numpy as np
import re
import io
import mysql.connector

def image_to_text(path):
    input_image = Image.open(path)
    
    #Converting image to array
    image_array = np.array(input_image)
    
    reader = easyocr.Reader(['en'])
    text = reader.readtext(image_array, detail = 0)
    return text, input_image


def extracted_details(texts):
    extracted_dict = {"NAME": [], "DESIGNATION": [], "COMPANY_NAME": [], "CONTACT": [], "EMAIL": [], "WEBSITE": [], 
                     "ADDRESS": [], "PINCODE": []}

    extracted_dict["NAME"].append(texts[0])
    extracted_dict["DESIGNATION"].append(texts[1])

    for i in range(2, len(texts)):
        if texts[i].startswith("+") or (texts[i].replace("-", "").isdigit() and '-' in texts[i]):
            extracted_dict["CONTACT"].append(texts[i])

        elif "@" in texts[i] and ".com" in texts[i]:
            extracted_dict["EMAIL"].append(texts[i])

        elif "WWW" in texts[i] or "www" in texts[i] or "Www" in texts[i] or "wWw" in texts[i] or "wwW" in texts[i]:
            smallcase = texts[i].lower()
            extracted_dict["WEBSITE"].append(smallcase)

        elif "Tamil Nadu" in texts[i] or "TamilNadu" in texts[i] or texts[i].isdigit():
            extracted_dict["PINCODE"].append(texts[i])

        elif re.match(r'^[A-Za-z]', texts[i]):
            extracted_dict["COMPANY_NAME"].append(texts[i])

        else:
            remove_char = re.sub(r'[,;]', '', texts[i])
            extracted_dict["ADDRESS"].append(remove_char)    
            
    for key,value in extracted_dict.items():
        if len(value)>0:
            concat = " ".join(value)
            extracted_dict[key] = [concat]
        else:
            value = "NA"
            extracted_dict[key] = [value]
        
    return extracted_dict


#streamlit part

st.set_page_config(layout = "wide")
st.title("Extracting Business Card Data with 'OCR'")

with st.sidebar:
    select = option_menu("Main Menu", ["Home", "Upload & Modify", "Delete"])

if select == "Home":
    # --- Hero Section ---
    st.title("📇 BizCard OCR")
    st.markdown("### The ultimate tool for digitizing business cards effortlessly.")
    st.info("Streamline your networking by converting physical cards into structured digital data.")
    
    st.markdown("---")

    # --- Feature Section: Two Column Layout ---
    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.subheader("📥 Feature 1: Easy Upload & Modify")
        st.write(
            """
            Experience seamless data entry with our intelligent OCR system.
            * **Smart Scanning:** Upload your card images.
            * **Live Modification:** Review extracted text and fix errors on the fly.
            * **Instant Validation:** Ensure phone numbers and emails are formatted correctly before saving.
            """
        )

    with col2:
        st.subheader("🗑️ Feature 2: Manage & Delete")
        st.write(
            """
            Take full control over your digital Rolodex.
            * **Data Overview:** View all scanned contacts in a clean, organized table.
            * **Search & Filter:** Find specific contacts by name or company instantly.
            * **One-Click Delete:** Clean up your database by removing outdated or duplicate records.
            """
        )

    st.markdown("---")

    # --- Visual Footer / Call to Action ---
    st.markdown("### How it works")
    
    step1, step2, step3 = st.columns(3)
    
    with step1:
        st.markdown("#### 1. Upload")
        st.caption("Drag and Drop a JPG or PNG image of any business card.")
        
    with step2:
        st.markdown("#### 2. Process")
        st.caption("The app extracts names, emails, contact numbers and other datas.")
        
    with step3:
        st.markdown("#### 3. Save")
        st.caption("Modify the details and save them to your secure database.")

    # Bottom Banner
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.divider()
    st.center = st.write("Built with ❤️ using Streamlit | 2026 BizCard Solutions")

elif select == "Upload & Modify":
    image = st.file_uploader("Upload the Image", type=["png", "jpg", "jpeg"])
    
    if image is not None:
        st.image(image, width = 300)

        text_details, input_image = image_to_text(image)
        text_dict = extracted_details(text_details)
        if text_dict:
            st.success("Data extracted successfully!")

        df = pd.DataFrame(text_dict)

        #converting image to bytes
        Image_bytes = io.BytesIO()
        input_image.save(Image_bytes, format = "PNG")
        
        image_data = Image_bytes.getvalue()
        
        #creating dictionaries
        data = {"IMAGE" : [image_data]}
        
        df_1 = pd.DataFrame(data)
        
        concat_df = pd.concat([df, df_1], axis = 1) #column wise - 1

        st.dataframe(concat_df)

        button_1 = st.button("SAVE", use_container_width = True)

        if button_1:
            #mysql
            sqlconnection = mysql.connector.connect(
                host='localhost',
                user='root',
                password='**your own password**',
                database='bizcard_data'
            )
            cursor = sqlconnection.cursor()
            
            #table creation

            create_table_query = '''CREATE TABLE IF NOT EXISTS bizcard_details(name varchar(255),
                                                                                designation varchar(255),
                                                                                company_name varchar(255),
                                                                                contact_number varchar(255),
                                                                                email varchar(255),
                                                                                website text,
                                                                                address text,
                                                                                pincode varchar(255),
                                                                                image longblob)'''
            
            cursor.execute(create_table_query)
            sqlconnection.commit()

            # Insert query
            
            insert_query = '''INSERT INTO bizcard_details(name, designation, company_name, contact_number, email, website, address, pincode, image)
                                                        values(%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
            
            datas = concat_df.values.tolist()[0]
            cursor.execute(insert_query, datas)
            sqlconnection.commit()

            st.success("Data saved successfully!")

    method = st.radio("Select the Method", ["None", "Preview", "Modify"])
    
    if method == "None":
        st.write("")
    
    if method == "Preview":
        sqlconnection = mysql.connector.connect(
                host='localhost',
                user='root',
                password='**your own password**',
                database='bizcard_data'
            )
        cursor = sqlconnection.cursor()
        #select query

        select_query = "SELECT * FROM bizcard_details"
        
        cursor.execute(select_query)
        table = cursor.fetchall()
        sqlconnection.commit()
        
        table_df = pd.DataFrame(table, columns = ("NAME", "DESIGNATION", "COMPANY_NAME", "CONTACT_NUMBER", "EMAIL", "WEBSITE", "ADDRESS", "PINCODE", "IMAGE"))
        st.dataframe(table_df)
        
    elif method == "Modify":
        sqlconnection = mysql.connector.connect(
                host='localhost',
                user='root',
                password='**your own password**',
                database='bizcard_data'
            )
        cursor = sqlconnection.cursor()
        #select query

        select_query = "SELECT * FROM bizcard_details"
        
        cursor.execute(select_query)
        table = cursor.fetchall()
        sqlconnection.commit()
        
        table_df = pd.DataFrame(table, columns = ("NAME", "DESIGNATION", "COMPANY_NAME", "CONTACT_NUMBER", "EMAIL", "WEBSITE", "ADDRESS", "PINCODE", "IMAGE"))

        col1, col2 = st.columns(2)
        with col1:
            selected_name = st.selectbox("Select the name", table_df["NAME"])

        df_3 = table_df[table_df["NAME"] == selected_name]

        df_4 = df_3.copy()       

        col1, col2 = st.columns(2)
        with col1:
            mod_name = st.text_input("Name", df_3["NAME"].unique()[0])
            mod_desg = st.text_input("Designation", df_3["DESIGNATION"].unique()[0])
            mod_comp_name = st.text_input("Company_Name", df_3["COMPANY_NAME"].unique()[0])
            mod_con_num = st.text_input("Contact_Number", df_3["CONTACT_NUMBER"].unique()[0])
            mod_email = st.text_input("Email", df_3["EMAIL"].unique()[0])

            df_4["NAME"] = mod_name
            df_4["DESIGNATION"] = mod_desg
            df_4["COMPANY_NAME"] = mod_comp_name
            df_4["CONTACT_NUMBER"] = mod_con_num
            df_4["EMAIL"] = mod_email
            
        with col2:
            mod_web = st.text_input("Website", df_3["WEBSITE"].unique()[0])
            mod_add = st.text_input("Address", df_3["ADDRESS"].unique()[0])
            mod_pin = st.text_input("Pincode", df_3["PINCODE"].unique()[0])
            mod_image = st.text_input("Image", df_3["IMAGE"].unique()[0])

            df_4["WEBSITE"] = mod_web
            df_4["ADDRESS"] = mod_add
            df_4["PINCODE"] = mod_pin
            df_4["IMAGE"] = mod_image
            
        st.dataframe(df_4)

        col1, col2 = st.columns(2)
        with col1:
            button_3 = st.button("Modify", use_container_width = True)

            if button_3:
                sqlconnection = mysql.connector.connect(
                host='localhost',
                user='root',
                password='**your own password**',
                database='bizcard_data'
                )
                cursor = sqlconnection.cursor()
            
                cursor.execute(f"DELETE FROM bizcard_details WHERE NAME = '{selected_name}'")
                sqlconnection.commit()

                # Insert query
            
                insert_query = '''INSERT INTO bizcard_details(name, designation, company_name, contact_number, email, website, address, pincode, image)
                                                            values(%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
                
                datas = df_4.values.tolist()[0]
                cursor.execute(insert_query, datas)
                sqlconnection.commit()
    
                st.success("Data modified successfully!")
                
elif select == "Delete":

        sqlconnection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='**your own password**',
        database='bizcard_data'
        )
        cursor = sqlconnection.cursor()

        col1, col2 = st.columns(2)
        with col1:
            
            select_query = "SELECT NAME FROM bizcard_details"
            
            cursor.execute(select_query)
            table1 = cursor.fetchall()
            sqlconnection.commit()
            
            names = []
            
            for i in table1:
                names.append(i[0])
    
            name_select = st.selectbox("Select the name", names)
    
        with col2:
            
            select_query = f"SELECT DESIGNATION FROM bizcard_details WHERE NAME = '{name_select}'"
            
            cursor.execute(select_query)
            table2 = cursor.fetchall()
            sqlconnection.commit()
            
            designation = []
            
            for j in table2:
                designation.append(j[0])
    
            desg_select = st.selectbox("Select the designation", designation)
        if name_select and desg_select:
            col1, col2, col3 = st.columns(3)
    
            with col1:
                st.write(f"Selected Name: {name_select}")
                st.write("")
                st.write("")
                st.write(f"Selected Designation: {desg_select}")
    
            with col2:
                st.write("")
                st.write("")
                st.write("")
                st.write("")
    
            remove = st.button("Delete", use_container_width = True)
    
            if remove:
                cursor.execute(f"DELETE FROM bizcard_details WHERE NAME = '{name_select}' AND DESIGNATION = '{desg_select}'")
                sqlconnection.commit()
                st.warning("DELETED!")
