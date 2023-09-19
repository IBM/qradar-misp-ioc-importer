# MISP-IOC-Importer-For-QRadar
This QRadar application allows users to import Indicators of Compromise (IOCs) from MISP to QRadar. Users input server details, API keys, and polling interval for automated data transfer. The app displays the last 10 imported IOCs and maintains operational logs for monitoring its activities and troubleshooting issues.


QRadar SDK documentation ``` https://www.ibm.com/support/pages/qradar-whats-new-app-framework-sdk-v200 ```

how to install QRadar SDK ``` https://www.ibm.com/support/pages/qradar-whats-new-app-framework-sdk-v200#i ```

To install the app on QRadar using the SDK, follow these simple steps:

Step 1: Identify Default Server and User Values (Optional)

``` qapp server -q <QRadar_server> -u <QRadar_user> ```

Step 2: Package the App

``` qapp package -p com.mycompany.myapp.zip ```

Step 3: Deploy the App to QRadar

``` qapp deploy -q <QRadar_server> -u <QRadar_user> -p com.mycompany.myapp.zip ```

Replace <QRadar_server> with the IP or hostname of your QRadar console and <QRadar_user> with the username of a user with the necessary permissions to deploy apps. The app will be uploaded to QRadar and installed for use.
nstall```

---> Route To run on QRadar ---> @viewsbp.route('/index', methods=['GET', 'POST']) # for QRadar

---> Route To run on Docker locally  ---> @viewsbp.route('/', methods=['GET', 'POST']) # for Local system

This application provides a web interface for users to import Indicators of Compromise (IOCs) from the MISP threat sharing platform to the QRadar security information and event management system. 

### Here are five tasks that the application carries out: ###

* Collecting User Input: The application provides an interface for users to input data necessary for importing IOCs from MISP to QRadar, including the MISP and QRadar server details, the API keys for both systems, the reference set name for QRadar, a polling interval, an event ID, and an IOC type.

* Initiating Import Process: Once the user has inputted all the necessary information and clicks the "Import IOC's" button, the application initiates the import process from MISP to QRadar.

* Displaying Last 10 IOCs: The application displays the last 10 imported IOCs in a table format for user reference.

* Displaying Application Logs: The application has a logging feature where it displays logs regarding the application's operations in real-time. These logs help users keep track of what the application is doing and if there are any errors occurring.

* Handling Polling Operations: The application handles automatic polling based on the user's inputted interval, fetching new IOCs from MISP and importing them to QRadar. This operation is performed regularly and is counted down in the application's interface.

### Potential improvements for the application could include: ###

* Validation of User Input: Currently, it seems like there is no validation for user input. Implementing validation checks for correct formats and data types can prevent errors in operation.

* Error Handling and Display: While the application does log error messages, it would be beneficial to display these errors more prominently to users, for instance, by using pop-up alerts.

* Secure Storage of API Keys: Right now, API keys are just inputted and transmitted. A more secure method of storing and transmitting these keys would be a significant improvement.

* User Authentication: The application does not currently have any form of user authentication. Implementing a user system would improve security and allow for more personalized experiences.

* Expand Supported IOC Types: Currently, the application supports a limited number of IOC types. Expanding this list to include other common IOC types can broaden the tool's usefulness.
