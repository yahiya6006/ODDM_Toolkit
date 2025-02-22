# About 

ODDM-Toolkit is a comprehensive data management tool designed for handling object detection datasets. It provides a user-friendly interface for creating projects, adding and managing datasets, and controlling user access with role-based permissions. Users can modify, review, and verify dataset updates through a structured task system. Once the data is finalized, it can be exported in various formats, including YOLO and Pascal VOC. The toolkit streamlines the entire dataset lifecycle, from organization to versioned releases, ensuring efficient and controlled dataset management.

## 🎬 Episode 2.1 - Host Setup & Admin Initialization
This repository contains the code for Episode 2.1 of the ODDM-Toolkit series. In this episode, we set up the host system, initialize the database, and configure the admin user.

📌 Stay tuned for upcoming episodes as we expand User Management further! 🚀

## Requirements

**System Requirements**
| package    | version |
|------------|---------|
| python     | 3.10.11 |
| postgreSQL | 16.6    |

**Python Dependencies**
| package                  | version |
|--------------------------|---------|
| pyside6                  | 6.8.2.1 |
| cryptography             | 44.0.0  |
| psycopg2                 | 2.9.10  |
| argon2-cffi              | 23.1.0  |
| google-api-python-client | 2.160.0 |
| google_auth_oauthlib     | 1.2.1   |

To set up your python environment execute the below command.
```sh
pip install -r python_dependencies.txt
```

If you encounter any errors installing psycopg2 then modify the python_dependencies.txt file and replace **psycopg2** with **psycopg2-binary**

to start the host app navigate to the folder host_app and execute.
```sh
python host_setup.py
```
or
```sh
python3 host_setup.py
```