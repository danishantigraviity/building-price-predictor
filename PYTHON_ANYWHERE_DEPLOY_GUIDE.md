# PythonAnywhere Deployment Guide

This guide outlines the steps to deploy your **Building Price Predictor** project to [PythonAnywhere](https://www.pythonanywhere.com/).

## 1. Upload Your Code
1.  **Git Clone**: Open a "Bash" console on PythonAnywhere and clone your repository:
    ```bash
    git clone https://github.com/danishantigraviity/building-price-predictor.git
    cd building-price-predictor
    ```
2.  **Pull Latest**: If you've already cloned it, make sure you have the latest code:
    ```bash
    git pull origin main
    ```

## 2. Set Up Virtual Environment
1.  In the Bash console, create and activate a virtual environment:
    ```bash
    mkvirtualenv --python=/usr/bin/python3.12 building-price-env
    pip install -r requirements.txt
    ```

## 3. Configure the Web App
1.  Go to the **"Web"** tab on PythonAnywhere dashboard.
2.  Click **"Add a new web app"**.
3.  Choose **"Manual Configuration"** (Important: Do not choose Flask/Django presets).
4.  Choose **Python 3.12**.
5.  **WSGI Configuration**:
    - Under the "Code" section, find the **WSGI configuration file** link and click it.
    - Delete everything in that file and paste the following (provided in your project as `wsgi.py`):
    ```python
    import sys
    import os

    # Your username and project folder
    path = '/home/danishappu33/building-price-predictor'
    if path not in sys.path:
        sys.path.insert(0, path)

    from app import app as application
    ```
    - Click **Save**.

## 4. Environment Variables & Virtualenv
1.  **Virtualenv Path**: Back on the "Web" tab, go to the "Virtualenv" section and enter:
    `/home/danishappu33/.virtualenvs/building-price-env`
2.  **Static Files**: Go to the "Static Files" section and add:
    - **URL**: `/`
    - **Path**: `/home/danishappu33/building-price-predictor/client/dist`

## 5. Reload & Verify
1.  Click the big green **"Reload"** button at the top of the Web tab.
2.  Visit your site at `http://YOUR_USERNAME.pythonanywhere.com/`.

> [!NOTE]
> PythonAnywhere is a persistent environment. Unlike Vercel, your database (`instance/site.db`) will be saved permanently and will not be deleted when the server restarts.
