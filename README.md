# Project Setup Guide

This guide will walk you through setting up the project, including installing Python, creating a virtual environment, installing dependencies, and running the script.

## Prerequisites

Before setting up the project, ensure you have the following installed:

- Python (version 3.10 or higher)

 If you don't have Python installed, you can download and install it from the official website:  
[Download Python](https://www.python.org/downloads/)

After installing, verify that Python is installed by running the following command in your terminal or command prompt:

```bash
python --version
```
This should display the installed version of Python.

## Setup Steps  

1. **Create a Virtual Environment**
   
   It's recommended to use a virtual environment to manage dependencies for this project. To create one, run the following commands in your terminal:

   ```bash
   # Navigate to the project directory
   cd path/to/your/project

   # Create a virtual environment
   python -m venv venv
   ```
   After running the above commands, a new virtual environment will be created in a folder named `venv`.
2. **Activate the Virtual Environment**
   
   To activate the virtual environment, run the appropriate command based on your operating system:

   * On Windows:
   ```bash
   .\venv\Scripts\activate
   ```

   * On macOS/Linux:
   ```bash
   source venv/bin/activate
   ```
3. **Install Dependencies**
   
   With the virtual environment activated, install the required dependencies using the `requirements.txt` file:
   ```bash
   pip install -r requirements.txt
   ```
4. **Create a `.env` File**
   Copy the `.env.template` file to a new file named `.env`:
   
   ```bash
   cp .env.template .env
   ```

   Open the `.env` file and update the necessary environment variables as instructed in the file.
   * `UHD_` variables are optional. It is only needed if you are running multiple radarr instances for HD and UHD.
5. **Run the Script**
   
   To run the script, navigate to the project directory in your terminal and execute the following command:

    ```bash
    python overseerr_sync.py
    ```
## Additional Notes
   * Ensure all the required environment variables in the `.env` file are set up properly for the script to work correctly.
   * If you encounter any issues or need further help, refer to the project's documentation or open an issue on the GitHub repository.