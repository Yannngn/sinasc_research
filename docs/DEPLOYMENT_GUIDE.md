# Deployment Guide: SINASC Dashboard on Render

This guide provides step-by-step instructions for deploying the SINASC dashboard, which uses a PostgreSQL backend, to Render.com.

## 1. Architecture on Render

The deployed application will consist of two main components on Render:

1.  **PostgreSQL Database**: A managed database instance that will serve as our cloud production database.
2.  **Web Service**: The Python Dash application, which connects to the PostgreSQL database to fetch data and serve the dashboard.

The data will be populated into the Render database by running our local `promote.py` script configured to target the cloud instance.

```
┌──────────────────────────────┐      ┌──────────────────────────────┐
│      Local Machine           │      │         Render Cloud         │
└──────────────┬───────────────┘      └──────────────┬───────────────┘
               │                                     │
┌──────────────▼──────────────┐      ┌──────────────▼──────────────┐
│      promote.py              │      │      PostgreSQL Database     │
│  (--target render)           ├─────►│ (Cloud Production DB)        │
└──────────────────────────────┘      └──────────────▲──────────────┘
                                                     │
                                      ┌──────────────┴──────────────┐
                                      │         Web Service          │
                                      │ (Dash App running Gunicorn)  │
                                      └──────────────────────────────┘
```

## 2. Step-by-Step Deployment

### Step 1: Create the PostgreSQL Database on Render

1.  Log in to your Render account.
2.  From the dashboard, click **New +** > **PostgreSQL**.
3.  Provide a unique **Name** for your database (e.g., `sinasc-prod-db`).
4.  Select a **Region** close to you.
5.  Click **Create Database**.
6.  Once the database is created, go to its "Info" page and copy the **Internal Database URL**. You will need this for your local `.env` file and for the web service configuration.

### Step 2: Update Your Local Environment

1.  Open your local `.env` file.
2.  Paste the copied **Internal Database URL** as the value for `PROD_RENDER_DATABASE_URL`.

    ```env
    # .env
    STAGING_DATABASE_URL=postgresql://user:password@localhost:5433/sinasc_db_staging
    PROD_LOCAL_DATABASE_URL=postgresql://user:password@localhost:5434/sinasc_db_prod_local
    PROD_RENDER_DATABASE_URL=postgres://user:xxxxxxxx@dpg-xxxxxxxx.frankfurt-a.oregon-postgres.render.com/sinasc_prod_db
    ```

### Step 3: Promote Data to the Cloud Database

Now, run the promotion script from your local machine, targeting the newly created Render database.

```bash
# Ensure your local Docker databases are running if you need to rebuild from scratch
# docker-compose up -d

# Run the promotion script targeting the cloud 'render' environment
python -m dashboard.data.promote --target render
```

This script will connect to your staging database, read the clean `fact_*` and `dim_*` tables, and copy them to your Render PostgreSQL database. This may take a few minutes depending on your internet connection.

### Step 4: Deploy the Web Service on Render

1.  Push your latest code, including the `render.yaml` file, to your GitHub repository.
2.  On the Render dashboard, click **New +** > **Web Service**.
3.  Select your GitHub repository.
4.  Render will automatically detect and use the `render.yaml` file for configuration. You need to add the database connection string as an environment variable.
5.  Go to the **Environment** tab for your new web service.
6.  Click **Add Environment Group** and select the group associated with your Render PostgreSQL database. This will automatically link the `DATABASE_URL` variable.
7.  Alternatively, click **Add Environment Variable** and create a variable with:
    -   **Key**: `DATABASE_URL`
    -   **Value**: Paste the **Internal Database URL** from your Render database.
8.  Click **Create Web Service**.

Render will now build and deploy your application. The `buildCommand` will install dependencies, and the `startCommand` will run the Gunicorn server.

### Step 5: Verify the Deployment

Once the deployment is live, visit your `onrender.com` URL. The dashboard should load and display data fetched from your Render PostgreSQL database.

Check the logs in the Render dashboard for any errors.

## 3. `render.yaml` Configuration

Your `render.yaml` file in the `deployment/` directory should look like this. It defines the build and start commands for the web service.

```yaml
# deployment/render.yaml
services:
  - type: web
    name: sinasc-dashboard
    env: python
    plan: free # Or a paid plan for better performance
    buildCommand: "uv sync"
    startCommand: "gunicorn dashboard.app:server"
    envVars:
      - key: PYTHON_VERSION
        value: 3.12.4
      - key: DATABASE_URL
        fromDatabase:
          name: sinasc-prod-db # Must match the name of your Render DB
          property: internalConnectionString
```

**Note**: The `fromDatabase` key is the recommended way to link your database, as it will automatically update if the connection string changes.

## 4. Security and Maintenance

-   **Database Access**: By default, your Render database is only accessible from other Render services within your account. To connect from your local machine (for the `promote.py` script), you may need to add your local IP address to the "Access" list in the database settings.
-   **Re-promoting Data**: If you update your ETL pipeline and need to refresh the production data, simply re-run the `promote.py --target render` command from your local machine.
-   **Free Tier Limitations**: Render's free web service tier may "spin down" after a period of inactivity. The first request to a sleeping service may take 30-60 seconds to respond. The free database tier does not spin down.
