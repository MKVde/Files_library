
# University Files And Documents Library

University Files And Documents Library is a Streamlit web application that allows users to upload, browse, and delete files in a university documents library. The application utilizes Firebase Realtime Database for storing file metadata and Firebase Cloud Storage [**console.firebase.google**](https://console.firebase.google.com/)  for storing the actual files. It also uses Deta from [**deta.space**](https://deta.space/) database for user authentication.



## Installation

1. Clone the project repository:


```bash
  git clone https://github.com/your-username/university-files-library.git

```
    
2. Navigate to the project directory:



```bash
    cd university-files-library

```

3. cd university-files-library


```bash
    pip install -r requirements.txt

```

4. Set up Firebase and Deta:

    * Create a Firebase project and enable the Realtime Database and Cloud Storage services. Obtain the Firebase Admin SDK credentials file ("path/to/serviceAccountKey.json") and save it in the project directory.

   * Sign up for a Deta account and create a new Base. Obtain your Deta API key (DETA_KEY) and update the database.py file with your key.



5. Run the application:

```bash
    streamlit run app.py

```

The application will be running locally at http://localhost:8501.


## Environment Variables



`DETA_KEY`

`FIREBASE_ADMIN_CREDENTIALS`


## Usage/Examples

1. Open the web browser and navigate to http://localhost:8501.

2. Login
- Enter your username and password to log in. If the credentials are correct, you will be redirected to the main page. Otherwise, an error message will be displayed.

3. Main Page
- The main page displays a sidebar with a welcome message and options to select different pages: "Upload Files", "Browse Documents", and "Delete Files".
- The selected page is displayed in the main area.

The main page will be displayed with the available options:

### Upload Files:

The **Upload Files** function allows users to add files to the library. To upload a file, follow these steps:

1. Click on the **Upload Files** option in the main menu.

2. Choose the file you want to upload by clicking on the "Browse" or "Choose File" button. Select the desired file from your local file system.

3. (Optional) Edit the file name if necessary. You can modify the original name of the file to make it more descriptive or organized.

4. Specify the metadata associated with the file. This includes providing information such as the college, major, year, and course related to the file content. Fill in the corresponding fields or select from predefined options, if available.

5. Click on the **Upload** button to upload the file to the library.

The uploaded file will be stored in the library with its associated metadata. You can repeat these steps to upload multiple files.

### Browse Documents:

The Browse Documents function allows users to search for files in the library based on specific metadata filters. To browse documents, follow these steps:

1. Select the **Browse Documents** option from the main menu.

2. Choose the desired filters to refine your search. Select the college, major, year, and course from the available options to narrow down the results. You can choose one or multiple filters.

3. Click on the **Search** button to retrieve the documents that match the selected filters.

4. The search results will be displayed, showing the files that match the specified metadata filters. You can view the file details and download the files if needed.

### Delete Files:

The **Delete Files** function allows users to remove files from the library based on metadata filters. To delete files, follow these steps:

1. Click on the **Delete Files** option in the main menu.

2. Select the filters that correspond to the files you want to delete. Choose the college, major, year, and course to filter the files based on their metadata. You can select one or multiple filters.

3. Once the filters are applied, the files that match the selected metadata will be displayed.

4. Choose the files you want to delete by selecting the corresponding checkboxes next to each file.

5. Click on the **Delete** button to delete the selected files from the library.

> **Warning**
Please note that deleting files is a permanent action and cannot be undone. Exercise caution when deleting files from the library.


## Documentation

To obtain the `FIREBASE_ADMIN_CREDENTIALS` environment variable:

1. Create a Firebase project at [**console.firebase.google**](https://console.firebase.google.com/) if you haven't already.

2. Enable the Realtime Database and Cloud Storage services in your Firebase project.

3. Go to the Firebase console and navigate to **Project settings**.

4. In the **Service accounts** tab, click on **Generate new private key**.

5. Save the downloaded JSON file securely and set the path to this file as the value of the `FIREBASE_ADMIN_CREDENTIALS` environment variable.

### **To Obtain The `DETA_KEY` Environment Variable:**

1. Sign up for a Deta account at [**deta.space**](https://www.deta.space/) if you haven't already.

2. Create a new Collection in your Deta account.

3. Create a new Base.

3. Obtain your Deta API key from the Deta website.

4. Set the obtained Deta API key as the value of the `DETA_KEY` environment variable.

Please ensure that the values of these environment variables are kept secure and not shared publicly.
## Deployment

To deploy this project, you can follow these steps:

1. Set up a hosting service such as Heroku, AWS, or Google Cloud Platform.

2. Configure the necessary environment variables on the hosting platform, including the `DETA_KEY`.

3. Deploy the application code to the hosting platform.

4. Make sure to enable the Realtime Database and Cloud Storage services on your Firebase project and update the `firebase_admin.initialize_app()` function in `app.py` with your Firebase Admin SDK credentials and database URL.

5. Update the necessary URLs in the code (e.g., Firebase database URL, storage bucket) if you are using a different hosting setup.

6. Start the deployed application and access it through the hosting service provided URL.
## License

[MIT](https://choosealicense.com/licenses/mit/)

