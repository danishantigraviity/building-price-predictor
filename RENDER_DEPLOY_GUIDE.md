# Render Deployment Guide

This guide helps you deploy your **Building Price Predictor** project to [Render](https://render.com/).

## 1. Connect Your GitHub
1.  Log in to [Render](https://dashboard.render.com/).
2.  Click **"New +"** and select **"Blueprint"**.
3.  Connect your GitHub repository: `building-price-predictor`.

## 2. Let Render Automate Everything
Since I've added a `render.yaml` file to your project, Render will automatically:
-   Detect the project as a **Web Service**.
-   Build your **React frontend** (in `client/`).
-   Install your **Python dependencies**.
-   Start the server using **Gunicorn**.

## 3. Manual Web Service (Alternative)
If you prefer to set it up manually without Blueprints:
1.  Click **"New +"** -> **"Web Service"**.
2.  **Runtime**: `Python 3`.
3.  **Build Command**:
    ```bash
    npm install --prefix client && npm run build --prefix client && pip install -r requirements.txt
    ```
4.  **Start Command**:
    ```bash
    gunicorn wsgi:application
    ```
5.  **Environment Variables**:
    -   `DATABASE_URL`: `sqlite:///instance/site.db`
    -   `PYTHON_VERSION`: `3.12.1`
    -   `NODE_VERSION`: `20.x`

## 4. Why Render?
-   **Persistent SSD Storage**: Unlike Vercel, Render allows you to keep your database files on a disk (though you need a paid disk for permanent SQLite storage, or just use their free PostgreSQL service).
-   **Automatic Scaling**: It handles traffic spikes well.

> [!TIP]
> After clicking "Deploy", you can watch the "Events" or "Logs" tab to see the build progress. It will take about 2-3 minutes to finish the React build and Python setup.
