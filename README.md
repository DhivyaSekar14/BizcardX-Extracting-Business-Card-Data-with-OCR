# BizcardX-Extracting-Business-Card-Data-with-OCR
BizCard OCR is a Streamlit web application that digitizes business cards instantly. Using EasyOCR, it extracts text from images and categorizes data like Name, Email, Contact Numbers and so on. Built with Streamlit and MySQL, it offers a full CRUD interface to upload, modify, and manage your professional contacts in one database.

## Features
- **OCR Extraction:** Automatically extracts Name, Designation, Company, Contact, Email, Website, Address, and Pincode.
- **Data Management:** Save extracted details directly to a MySQL database.
- **Interactive UI:** Preview, Modify, and Delete records effortlessly.
- **Visuals:** Displays the uploaded card image alongside extracted data.

## Technologies Used
- **Python**
- **Streamlit** (UI Framework)
- **EasyOCR** (Optical Character Recognition)
- **MySQL** (Database Management)
- **Pandas** (Data Manipulation)

## Setup Instructions

1. **Clone the Repository:**
   git clone [https://github.com/DhivyaSekar14/BizcardX-Extracting-Business-Card-Data-with-OCR.git](https://github.com/DhivyaSekar14/BizcardX-Extracting-Business-Card-Data-with-OCR.git)
2. **Install Dependencies:**
     pip install -r requirements.txt
3. **Database Configuration:**
     Ensure you have MySQL installed and running.
     Update the host, user, and password in bizcardapp.py to match your local MySQL credentials.
4. **Run the App:**
     streamlit run bizcardapp.py

## Usage
  1.Navigate to the Home section for an overview.
  
  2.Go to Upload & Modify to scan a new card and save it.
  
  3.Use the Preview or Modify radio buttons to view or edit existing records.
  
  4.Use the Delete menu to remove specific entries from the database.
