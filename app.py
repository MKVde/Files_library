# Login from databse using "deta.space" 
import streamlit as st
import os
from dotenv import load_dotenv
import database as dba
import streamlit_authenticator as stauth
import firebase_admin
from firebase_admin import credentials, initialize_app
from firebase_admin import db
from firebase_admin import storage
from datetime import datetime, timedelta
from metadata import COLLEGES
from cachetools import TTLCache
import hashlib
import tempfile

# --- USER AUTHENTICATION ---

users = dba.fetch_all_users()

usernames = [user["key"] for user in users]
names = [user["name"] for user in users]
hashed_passwords = [user["password"] for user in users]

cookie_expiry_days = 8

authenticator = stauth.Authenticate(names, usernames, hashed_passwords, "university_files_documents_library", "abcdef", cookie_expiry_days)

name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status == False:
    st.error("Username/password is incorrect")

if authentication_status == None:
    st.warning("Please enter your username and password")

if authentication_status:
    # Create a cache with a TTL (time-to-live) of 5 minutes
    cache = TTLCache(maxsize=100, ttl=300)
    
    # Initialize Firebase Admin SDK only once
    load_dotenv(".env")
    firebase_admin_credentials = os.getenv("FIREBASE_ADMIN_CREDENTIALS")
    # Create a temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.write(firebase_admin_credentials.encode())
    temp_file.close()
    if not firebase_admin._apps:
        cred = credentials.Certificate(temp_file.name)
        initialize_app(cred, {
            'databaseURL': 'https://streamlit-v2-default-rtdb.europe-west1.firebasedatabase.app',
            'storageBucket': 'streamlit-v2.appspot.com'
        })

    def generate_custom_id(user, metadata):
        # Concatenate relevant metadata fields
        data = user + metadata['college'] + metadata['course'] + metadata['year']

        # Generate a hash value from the concatenated data
        hashed_data = hashlib.sha256(data.encode()).hexdigest()

        # Take the first 10 characters of the hashed value as the custom ID
        custom_id = hashed_data[:10]

        return custom_id

    
    def find_existing_file(file_name, metadata):
        files_ref = db.reference('files')

        query = files_ref.order_by_child('fileName')
        if file_name is not None:
            query = query.equal_to(file_name)

        files = query.get()

        for file_id, file_data in files.items():
            if file_data.get('college') == metadata['college'] and \
                    file_data.get('major') == metadata['major'] and \
                    file_data.get('year') == metadata['year'] and \
                    file_data.get('course') == metadata['course']:
                return file_data

        return None

    
    def edit_file(file, edited_file_name):
        # Get the file extension
        file_extension = file.name.split(".")[-1]

        # Create the new file name with the edited name and original extension
        new_file_name = f"{edited_file_name}.{file_extension}"

        st.success(f"File '{file.name}' edited successfully with new name '{edited_file_name}'")
        return new_file_name
    
    # Function to upload file and metadata to the Firebase Realtime Database
    def upload_file(file, edited_file_name, metadata):
        with st.spinner("Uploading file..."):
            # Check if a file with the same name and metadata already exists
            existing_file = find_existing_file(edited_file_name, metadata)
            if existing_file:
                st.warning("File with the same name and metadata already exists.")
                return
            
            # Generate a unique ID for the file
            file_id = generate_custom_id(metadata['user'], metadata)

            # Get the current timestamp
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Use the original file name if edited_file_name is None
            if edited_file_name is None:
                edited_file_name = file.name

            # Store the file metadata in the database
            file_data = {
                "Id": file_id,
                "user": metadata['user'],
                "fileName": edited_file_name,
                "college": metadata['college'],
                "major": metadata['major'],
                "year": metadata['year'],
                "course": metadata['course'],
                "uploadedDate": timestamp,
                "lastModifiedDate": timestamp
            }
            db.reference('files').child(file_id).set(file_data)

            # Upload the file to Firebase Cloud Storage
            bucket = storage.bucket()
            blob = bucket.blob(edited_file_name)
            blob.upload_from_file(file)

        st.success("File uploaded successfully!")


    # Function to retrieve files based on metadata filters from the Firebase Realtime Database
    def get_files_by_metadata(metadata):
        with st.spinner("Searching for files..."):
            files_ref = db.reference('files')

            # Apply the metadata filters
            college = metadata['college']
            major = metadata['major']
            year = metadata['year']
            course = metadata['course']

            query = files_ref.order_by_child('college').equal_to(college)

            files = query.get()

            filtered_files = {}
            for file_id, file_data in files.items():
                if major == "All" or file_data.get('major') == major:
                    if year == "All" or file_data.get('year') == year:
                        if course == "All" or file_data.get('course') == course:
                            filtered_files[file_id] = file_data

            return filtered_files
    
    def delete_files_by_metadata(metadata, selected_files):
        with st.spinner("Deleting files..."):
            for file_id in selected_files:
                # Get the file data from the database
                file_data = db.reference('files').child(file_id).get()

                if file_data:
                    # Remove the file data from the database
                    db.reference('files').child(file_id).delete()

                    # Delete the file from Firebase Storage
                    bucket = storage.bucket()
                    file_blob = bucket.blob(file_data['fileName'])
                    
                    if file_blob.exists():
                        file_blob.delete()
                        st.success(f"File '{file_data['fileName']}' deleted successfully from Firebase Storage!")
                    else:
                        st.warning(f"File '{file_data['fileName']}' does not exist in Firebase Storage.")
                else:
                    st.warning(f"File with ID '{file_id}' does not exist in the Realtime Database.")

        st.success("Files deleted successfully!")


    # Streamlit app UI
    def main():
        st.title("University Files Documents Library")

        st.sidebar.title(f"🏁 Welcome {name}")
        page = st.sidebar.selectbox("Select a page", ["Upload Files", "Browse Documents", "Delete Files"])
        authenticator.logout("Logout", "sidebar")
        
        if page == "Upload Files":
            st.header("Upload Files")

            # File upload section
            file = st.file_uploader("Choose a file")

            if file is not None:
                # Checkbox for editing the file
                edit_file_checkbox = st.checkbox("Edit File")
                
                # Check if the "Edit File" checkbox is checked
                if edit_file_checkbox:
                    # Show the file edit name field
                    edited_file_name = st.text_input("Edited File Name")
                else:
                    edited_file_name = None
                
                # Metadata section
                st.subheader("Metadata")

                college = st.selectbox("College", list(COLLEGES.keys()))
                major = st.selectbox("Major", list(COLLEGES[college]['majors'].keys()))

                years = COLLEGES[college]['majors'][major]['years']
                year = st.selectbox("Year", list(years.keys()))

                courses = years[year]
                course = st.selectbox("Course", courses)

                metadata = {
                    'user': username,  # Fill User ID with the username
                    'college': college,
                    'major': major,
                    'year': year,
                    'course': course
                }

                # Upload button
                if st.button("Upload"):
                    if edit_file_checkbox:
                        edited_file_name = edit_file(file, edited_file_name)
                    upload_file(file, edited_file_name, metadata)                                                                                                                               


        elif page == "Browse Documents":
            st.header("Browse Documents")

            # Metadata filters
            st.subheader("Filter by Metadata")
            college = st.selectbox("College", ["All"] + list(COLLEGES.keys()))
            if college != "All":
                majors = list(COLLEGES[college]['majors'].keys())
                major = st.selectbox("Major", ["All"] + majors)
            else:
                major = "All"

            if major != "All":
                years = COLLEGES[college]['majors'][major]['years']
                year = st.selectbox("Year", ["All"] + list(years.keys()))
            else:
                year = "All"

            if year != "All":
                courses = years[year]
                course = st.selectbox("Course", ["All"] + courses)
            else:
                course = "All"

            metadata = {
                'college': college,
                'major': major,
                'year': year,
                'course': course
            }

            # Search button
            if st.button("Search"):
                files = get_files_by_metadata(metadata)
                st.write(f"Total documents: {len(files)}")

                # Display search results
                if files:
                    st.subheader("Search Results")
                    for file_id, file_data in files.items():
                        st.write(f"File Name: {file_data['fileName']}")
                        # Add a download hyperlink for each file
                        file_blob = storage.bucket().blob(file_data['fileName'])
                        expiration = timedelta(minutes=15)
                        url = file_blob.generate_signed_url(
                            version="v4",
                            expiration=expiration,
                            method="GET"
                        )
                        st.markdown(f"[Download File]({url})")

        elif page == "Delete Files":
            st.header("Delete Files")

            # Metadata filters
            st.subheader("Filter by Metadata")
            college = st.selectbox("College", ["All"] + list(COLLEGES.keys()))
            if college != "All":
                majors = list(COLLEGES[college]['majors'].keys())
                major = st.selectbox("Major", ["All"] + majors)
            else:
                major = "All"

            if major != "All":
                years = COLLEGES[college]['majors'][major]['years']
                year = st.selectbox("Year", ["All"] + list(years.keys()))
            else:
                year = "All"

            if year != "All":
                courses = years[year]
                course = st.selectbox("Course", ["All"] + courses)
            else:
                course = "All"

            metadata = {
                'college': college,
                'major': major,
                'year': year,
                'course': course
            }

            # Check if all metadata fields have been selected
            if college != "All" and major != "All" and year != "All" and course != "All":
                # Retrieve files based on metadata filters
                files = get_files_by_metadata(metadata)

                # Display file details and checkboxes for selection
                if files:
                    st.subheader("Files to Delete")
                    selected_files = []
                    for file_id, file_data in files.items():
                        file_name = file_data['fileName']
                        file_checkbox = st.checkbox(file_name, key=file_id)
                        if file_checkbox:
                            selected_files.append(file_id)

                    # Delete button
                    if st.button("Delete"):
                        delete_files_by_metadata(metadata, selected_files)
                else:
                    st.warning("No files found matching the metadata filters.")
            else:
                show_files = st.selectbox("Show Files to Delete", ["No", "Yes"])
                if show_files == "Yes":
                    files = get_files_by_metadata(metadata)
                    if files:
                        st.subheader("Files to Delete")
                        selected_files = []
                        for file_id, file_data in files.items():
                            file_name = file_data['fileName']
                            file_checkbox = st.checkbox(file_name, key=file_id)
                            if file_checkbox:
                                selected_files.append(file_id)

                        # Delete button
                        if st.button("Delete"):
                            delete_files_by_metadata(metadata, selected_files)
                    else:
                        st.warning("No files found matching the metadata filters.")

    # Run the app
    main()
    os.remove(temp_file.name)

# Another version with ROles Student and Admin versions


