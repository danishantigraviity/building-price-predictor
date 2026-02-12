import os
import sqlite3
import hashlib
import random
import smtplib
import ssl
from datetime import datetime, timedelta
from email.message import EmailMessage
from io import BytesIO
import json

import streamlit as st
import pandas as pd

# === Import Accurate ML Modules (Assuming these modules exist and work) ===
# Note: For this application to run correctly, you must have blueprint_features.py,
# and cost_model.py in the same directory, and the necessary ML libraries installed.
try:
    from blueprint_features import extract_blueprint_features
    from cost_model import load_models, compute_cost_breakdown, load_unit_costs
except ImportError as e:
    st.error(f"Missing custom module: {e}. Please ensure 'blueprint_features.py' and 'cost_model.py' are present.")
    # Mock implementations for demonstration if modules are missing
    def extract_blueprint_features(data): return {"area_sqft_estimate": 1000, "rooms_estimate": 4, "wall_length_ft": 150}
    def load_models(): return type('MockModel', (object,), {'predict': lambda self, X: [ [5000, 500, 2000, 100, 300] ]})(), type('MockModel', (object,), {'predict': lambda self, X: [ 5000000 ]})()
    def load_unit_costs(): return {"unit_cost_bricks": 10, "unit_cost_cement": 350, "unit_cost_steel": 70, "unit_cost_paint": 400, "unit_cost_worker_day": 800}
    def compute_cost_breakdown(qty_pred, city, quality, cfg):
        return {
            "breakdown": {
                "Bricks Cost": qty_pred.get("bricks_count", 0) * cfg["unit_cost_bricks"],
                "Cement Cost": qty_pred.get("cement_bags", 0) * cfg["unit_cost_cement"],
                "Steel Cost": qty_pred.get("steel_kg", 0) * cfg["unit_cost_steel"],
                "Paint Cost": qty_pred.get("paint_liters", 0) * cfg["unit_cost_paint"],
                "Labor Cost": qty_pred.get("worker_days", 0) * cfg["unit_cost_worker_day"],
            }
        }

# -------- OPTIONAL: PDF generation (reportlab) ----------
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas
    REPORTLAB_OK = True
except Exception:
    REPORTLAB_OK = False


# =========================
#  APP CONFIG
# =========================
st.set_page_config(page_title="Blueprint → Building Price Prediction", layout="wide", initial_sidebar_state="expanded")


# =========================
#  APP CONSTANTS
# =========================
CITIES = [
    "Chennai", "Bengaluru", "Mumbai", "Delhi", "Hyderabad", 
    "Kolkata", "Pune", "Ahmedabad", "Jaipur", "Coimbatore"
]
QUALITIES = ["basic", "standard", "premium"]
DEFAULT_CITY = "Chennai"
DEFAULT_QUALITY = "standard"

# --- HARDCODED ADMIN CREDENTIALS (Username: admin, Password: 2103) ---
ADMIN_EMAIL = "admin"
ADMIN_PASS_HASH = hashlib.sha256("2103".encode()).hexdigest()
# --- HARDCODED ADMIN CREDENTIALS ---


# =========================
#  UTILITIES
# =========================
def sha256(s: str) -> str:
    """Generate SHA256 hash for secure password storage."""
    return hashlib.sha256(s.encode()).hexdigest()

def now() -> str:
    """Get current UTC time formatted for DB storage."""
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

def send_email(to_addr: str, subject: str, body: str) -> bool:
    """Send email via SMTP env vars. If not configured, print body in UI (dev mode)."""
    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT", "0") or "0")
    user = os.getenv("SMTP_USER")
    pwd  = os.getenv("SMTP_PASS")
    from_addr = os.getenv("SMTP_FROM", user or "no-reply@example.com")

    if not (host and port and user and pwd):
        st.info(f"📧 (DEV MODE) Email to **{to_addr}**\n\n**Subject:** {subject}\n\n```\n{body}\n```")
        return False

    try:
        msg = EmailMessage()
        msg["From"] = from_addr
        msg["To"] = to_addr
        msg["Subject"] = subject
        msg.set_content(body)

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(host, port, context=context) as server:
            server.login(user, pwd)
            server.send_message(msg)
        return True
    except Exception as e:
        st.warning(f"Email send failed: {e}")
        return False

# =========================
#  DB SETUP
# =========================
@st.cache_resource
def get_db_connection():
    """Get a cached connection to the SQLite database."""
    return sqlite3.connect("app.db", check_same_thread=False)

conn = get_db_connection()
cur = conn.cursor()

# Create necessary tables
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE,
    password_hash TEXT NOT NULL,
    full_name TEXT,
    default_city TEXT,
    default_quality TEXT,
    is_admin INTEGER DEFAULT 0,
    created_at TEXT
)""")

cur.execute("""
CREATE TABLE IF NOT EXISTS otps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT,
    otp TEXT,
    expires_at TEXT
)""")

cur.execute("""
CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_email TEXT,
    inputs_json TEXT,
    quantities_json TEXT,
    cost_breakdown_json TEXT,
    total REAL,
    created_at TEXT
)""")
conn.commit()


# =========================
#  SESSION
# =========================
if "user" not in st.session_state:
    st.session_state.user = None

def set_user(email: str):
    """Fetches user details from DB and updates session state."""
    # This function is used for regular DB users
    cur.execute("SELECT email, full_name, default_city, default_quality, is_admin FROM users WHERE email=?", (email,))
    row = cur.fetchone()
    if row:
        st.session_state.user = {
            "email": row[0],
            "full_name": row[1] or "",
            "default_city": row[2] or DEFAULT_CITY,
            "default_quality": row[3] or DEFAULT_QUALITY,
            "is_admin": bool(row[4])
        }
        
        # Ensure at least one DB user is admin if the hardcoded admin isn't used for management
        # This is a legacy/first-run logic to ensure there is a fallback admin in the DB.
        cur.execute("SELECT 1 FROM users WHERE is_admin=1")
        if not cur.fetchone():
            # Only set the first registered user as admin
            cur.execute("UPDATE users SET is_admin=1 WHERE email=?", (email,))
            conn.commit()
            set_user(email) # Re-fetch to update session


# =========================
#  AUTH SCREENS
# =========================
def screen_login():
    """Handles user and hardcoded admin login."""
    with st.container(border=True):
        st.markdown("### 🔑 Login")
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pass")
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Login", use_container_width=True, type="primary"):
                
                # --- START HARDCODED ADMIN CHECK ---
                if email == ADMIN_EMAIL and sha256(password) == ADMIN_PASS_HASH:
                    st.session_state.user = {
                        "email": ADMIN_EMAIL,
                        "full_name": "Site Administrator",
                        "default_city": DEFAULT_CITY,
                        "default_quality": DEFAULT_QUALITY,
                        "is_admin": True # Crucial for access to the Admin tab
                    }
                    st.success("Welcome, Site Administrator! Access the Admin tab for management.")
                    st.rerun()
                    return # Exit the function after successful admin login
                # --- END HARDCODED ADMIN CHECK ---

                # --- Regular User Login ---
                cur.execute("SELECT password_hash FROM users WHERE email=?", (email,))
                row = cur.fetchone()
                if row and row[0] == sha256(password):
                    set_user(email)
                    st.success("Welcome back!")
                    st.rerun()
                else:
                    st.error("Invalid email or password.")
        with c2:
            if st.button("Create Account", use_container_width=True):
                st.session_state.view = "register"
                st.rerun()

        st.divider()
        st.markdown("Forgot your password?")
        if st.button("Send OTP to Email", use_container_width=True):
            if not email:
                st.warning("Enter your email first.")
            elif email == ADMIN_EMAIL:
                st.error("The hardcoded admin password cannot be reset.")
            else:
                cur.execute("SELECT 1 FROM users WHERE email=?", (email,))
                if not cur.fetchone():
                    st.error("User not found.")
                    return
                
                otp = f"{random.randint(100000, 999999)}"
                expires = (datetime.utcnow() + timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M:%S")
                cur.execute("DELETE FROM otps WHERE email=?", (email,))
                cur.execute("INSERT INTO otps (email, otp, expires_at) VALUES (?, ?, ?)", (email, otp, expires))
                conn.commit()
                ok = send_email(email, "Your password reset OTP", f"Your OTP is: {otp}\nThis OTP expires in 10 minutes.")
                st.success("OTP sent!" if ok else "OTP displayed above (dev mode).")
                st.session_state.reset_email = email
                st.session_state.view = "reset"
                st.rerun()

def screen_register():
    """Handles new user registration."""
    with st.container(border=True):
        st.markdown("### 📝 Create Account")
        email = st.text_input("Email", key="reg_email")
        full_name = st.text_input("Full name", key="reg_name")
        password = st.text_input("Password", type="password", key="reg_pass")
        
        city = st.selectbox("Default City", CITIES, index=CITIES.index(DEFAULT_CITY))
        quality = st.selectbox("Default Quality", QUALITIES, index=QUALITIES.index(DEFAULT_QUALITY))

        if st.button("Register", use_container_width=True, type="primary"):
            if not (email and password):
                st.error("Email and password are required.")
            else:
                # Prevent registration if the user tries to use the hardcoded admin email
                if email == ADMIN_EMAIL:
                    st.error(f"The email '{ADMIN_EMAIL}' is reserved.")
                    return
                
                try:
                    cur.execute("""
                        INSERT INTO users (email, password_hash, full_name, default_city, default_quality, is_admin, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (email, sha256(password), full_name, city, quality, 0, now()))
                    conn.commit()
                    send_email(email, "Welcome to Building Cost Predictor",
                               f"Hi {full_name or email},\n\nYour account is ready. Enjoy predicting your project costs!\n\n— Team")
                    st.success("Account created! Please sign in.")
                    st.session_state.view = "login"
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.error("That email is already registered.")
        
        if st.button("Back to Login", use_container_width=True):
            st.session_state.view = "login"
            st.rerun()

def screen_reset_password():
    """Handles password reset using OTP."""
    with st.container(border=True):
        st.markdown("### 🔐 Reset Password")
        email = st.session_state.get("reset_email", "")
        st.text_input("Email", value=email, disabled=True)
        otp = st.text_input("Enter OTP")
        new_pass = st.text_input("New Password", type="password")

        if st.button("Reset Password", use_container_width=True, type="primary"):
            cur.execute("SELECT otp, expires_at FROM otps WHERE email=?", (email,))
            row = cur.fetchone()
            if not row:
                st.error("No OTP found. Request a new OTP.")
            else:
                otp_db, exp = row
                if datetime.utcnow() > datetime.strptime(exp, "%Y-%m-%d %H:%M:%S"):
                    st.error("OTP expired. Request a new one.")
                elif otp != otp_db:
                    st.error("Invalid OTP.")
                else:
                    cur.execute("UPDATE users SET password_hash=? WHERE email=?", (sha256(new_pass), email))
                    cur.execute("DELETE FROM otps WHERE email=?", (email,))
                    conn.commit()
                    st.success("Password updated. Please login.")
                    st.session_state.view = "login"
                    st.rerun()
        
        if st.button("Back", use_container_width=True):
            st.session_state.view = "login"
            st.rerun()


# =========================
#  LOGGED-IN APP SCREENS
# =========================
def make_invoice_pdf(pred_row: dict) -> bytes:
    """Generate a simple PDF invoice (ReportLab)."""
    if not REPORTLAB_OK:
        st.info("Install reportlab to enable PDF invoices: pip install reportlab")
        return b''

    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    W, H = A4

    y = H - 30*mm
    c.setFont("Helvetica-Bold", 16); c.drawString(20*mm, y, "Building Cost Estimate")
    y -= 10*mm
    c.setFont("Helvetica", 10)
    c.drawString(20*mm, y, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}    User: {pred_row['user_email']}")
    y -= 10*mm

    c.setFont("Helvetica-Bold", 12); c.drawString(20*mm, y, "Inputs")
    y -= 7*mm; c.setFont("Helvetica", 10)
    for k,v in pred_row["inputs"].items():
        c.drawString(25*mm, y, f"{k}: {v}"); y -= 6*mm

    y -= 3*mm
    c.setFont("Helvetica-Bold", 12); c.drawString(20*mm, y, "Quantities")
    y -= 7*mm; c.setFont("Helvetica", 10)
    for k,v in pred_row["quantities"].items():
        c.drawString(25*mm, y, f"{k}: {v:,.0f}"); y -= 6*mm # Format quantities with commas

    y -= 3*mm
    c.setFont("Helvetica-Bold", 12); c.drawString(20*mm, y, "Cost Breakdown (₹)")
    y -= 7*mm; c.setFont("Helvetica", 10)
    for k,v in pred_row["breakdown"].items():
        c.drawString(25*mm, y, f"{k}: {v:,.0f}"); y -= 6*mm # Format costs with commas

    y -= 6*mm
    c.setFont("Helvetica-Bold", 14); c.drawString(20*mm, y, f"TOTAL: ₹ {pred_row['total']:,.0f}")
    c.showPage(); c.save()
    return buf.getvalue()

def screen_profile():
    """Allows authenticated users to update their profile details."""
    with st.container(border=True):
        st.markdown("### 👤 Profile")
        u = st.session_state.user
        
        # Prevent the hardcoded admin from changing their profile
        if u["email"] == ADMIN_EMAIL:
            st.info("The profile for the hardcoded administrator cannot be modified.")
            st.text_input("Email", value=u["email"], disabled=True)
            st.text_input("Full name", value=u["full_name"], disabled=True)
            st.selectbox("Default city", CITIES, index=CITIES.index(u["default_city"]), disabled=True)
            st.selectbox("Default quality", QUALITIES, index=QUALITIES.index(u["default_quality"]), disabled=True)
            return

        default_city = u["default_city"] or DEFAULT_CITY
        default_quality = u["default_quality"] or DEFAULT_QUALITY
        
        city_index = CITIES.index(default_city) if default_city in CITIES else 0
        quality_index = QUALITIES.index(default_quality) if default_quality in QUALITIES else 1

        full_name = st.text_input("Full name", value=u["full_name"])
        city = st.selectbox("Default city", CITIES, index=city_index)
        quality = st.selectbox("Default quality", QUALITIES, index=quality_index)
        
        if st.button("Save Profile", use_container_width=True, type="primary"):
            cur.execute("UPDATE users SET full_name=?, default_city=?, default_quality=? WHERE email=?",
                        (full_name, city, quality, u["email"]))
            conn.commit()
            set_user(u["email"]) # Refresh session state
            st.success("Saved!")

def screen_admin():
    """Admin dashboard showing registered users and recent activity."""
    if not st.session_state.user.get("is_admin"):
        st.error("Access Denied.")
        return

    with st.container(border=True):
        st.markdown("### 🛠️ Admin Dashboard")
        
        # This section shows who has registered
        st.write("#### Registered Users (DB Users)")
        cur.execute("SELECT email, full_name, default_city, default_quality, is_admin, created_at FROM users ORDER BY created_at DESC")
        users = pd.DataFrame(cur.fetchall(), columns=["email (Username)","full_name","default_city", "default_quality", "is_admin","created_at"])
        st.dataframe(users, use_container_width=True)

        # This section shows user activity (predictions)
        st.write("#### User Activity (Recent Predictions)")
        cur.execute("SELECT id, user_email, total, created_at FROM predictions ORDER BY created_at DESC LIMIT 200")
        preds = pd.DataFrame(cur.fetchall(), columns=["id","user_email","total","created_at"])
        preds['total'] = preds['total'].apply(lambda x: f"₹ {x:,.0f}")
        st.dataframe(preds, use_container_width=True)

def screen_predict():
    """Main prediction interface."""
    with st.container(border=True):
        st.markdown("### 🏗️ Blueprint → Price Prediction")
        st.caption(f"Signed in as **{st.session_state.user['email']}** ·  {'Admin' if st.session_state.user['is_admin'] else 'User'}")
        
        # Load models on app start/first prediction
        try:
            qty_model, total_cost_model = load_models()
        except Exception as e:
            st.warning(f"Prediction models could not be loaded or trained. Check module files and data: {e}")
            return

        if not qty_model or not total_cost_model:
            st.warning("Prediction models could not be loaded or trained. Check module files and data.")
            return

        default_city = st.session_state.user["default_city"] or DEFAULT_CITY
        default_quality = st.session_state.user["default_quality"] or DEFAULT_QUALITY
        
        city_index = CITIES.index(default_city) if default_city in CITIES else 0
        quality_index = QUALITIES.index(default_quality) if default_quality in QUALITIES else 1

        c1, c2 = st.columns(2)
        with c1:
            city = st.selectbox("City", CITIES, index=city_index)
            quality = st.selectbox("Quality", QUALITIES, index=quality_index)
            floors = st.number_input("Floors", 1, 10, 2)
            carpet_ratio = st.slider("Carpet Area Ratio", 0.5, 0.95, 0.72, 0.01)
        with c2:
            uploaded = st.file_uploader("Upload Blueprint (PNG/JPG)", type=["png","jpg","jpeg"])
            area_override = st.number_input("Override Area (sqft)", 0, 10000, 0, help="Set to 0 to use blueprint estimate.")
            rooms_override = st.number_input("Override Rooms", 0, 20, 0, help="Set to 0 to use blueprint estimate.")
            wall_override = st.number_input("Override Wall Length (ft)", 0, 3000, 0, help="Set to 0 to use blueprint estimate.")

        st.divider()
        st.subheader("1) Extracted Features")
        
        feats = {}
        if uploaded:
            try:
                # Use the actual file content for extraction
                feats = extract_blueprint_features(uploaded.read())
            except Exception as e:
                st.error(f"Error extracting features from image: {e}. Using mock data.")
                feats = {"area_sqft_estimate": 900, "rooms_estimate": 5, "wall_length_ft": 120}
        else:
            # Mock features if no file is uploaded
            feats = {"area_sqft_estimate": 900, "rooms_estimate": 5, "wall_length_ft": 120}
        
        if area_override: feats["area_sqft_estimate"] = area_override
        if rooms_override: feats["rooms_estimate"] = rooms_override
        if wall_override: feats["wall_length_ft"] = wall_override
        st.dataframe(pd.Series(feats).to_frame(name='Value'), use_container_width=True)

        st.divider()
        st.subheader("2) Predict")
        if st.button("🔍 Predict Cost", use_container_width=True, type="primary"):
            
            # --- PREDICTION LOGIC ---
            
            # Prepare input features for the model
            X = pd.DataFrame([{
                "city": city,
                "quality": quality,
                "floors": floors,
                "rooms": feats["rooms_estimate"],
                "area_sqft": feats["area_sqft_estimate"],
                "wall_length_ft": feats["wall_length_ft"],
                "carpet_ratio": carpet_ratio
            }])

            # 1. Predict Quantities (using Quantity Model)
            qty_cols = ["bricks_count","cement_bags","steel_kg","paint_liters","worker_days"]
            q = qty_model.predict(X)[0] 
            # Ensure quantities are non-negative integers
            qty_pred = dict(zip(qty_cols, [int(round(max(0, v))) for v in q]))

            # 2. Calculate Cost Breakdown (using unit cost config)
            cfg = load_unit_costs()
            cost_breakdown_result = compute_cost_breakdown(qty_pred, city, quality, cfg)
            
            # 3. Predict Final Total Cost (using the specialized Total Cost Model for higher accuracy)
            total_predicted = total_cost_model.predict(X)[0]
            total_predicted = max(0, total_predicted) # Ensure total cost is non-negative

            # --- DISPLAY RESULTS ---
            st.success("Prediction complete!")
            cL, cR = st.columns(2)
            with cL:
                st.write("##### Materials")
                # Format quantities for display
                qty_display = pd.Series({k: f"{v:,.0f}" for k, v in qty_pred.items()})
                st.dataframe(qty_display.to_frame(name='Quantity'), use_container_width=True)
            with cR:
                st.write("##### Cost breakdown (₹)")
                # Format breakdown costs for display
                brk_display = pd.Series({k: f"₹ {v:,.0f}" for k, v in cost_breakdown_result["breakdown"].items()})
                st.dataframe(brk_display.to_frame(name='Cost (INR)'), use_container_width=True)
                
            st.metric("TOTAL (Accurate Prediction)", f"₹ {total_predicted:,.0f}", help="This total is the final prediction from the specialized ML model.") 

            # --- SAVE TO DB (Skip for hardcoded admin to keep DB clean) ---
            inputs = dict(city=city, quality=quality, floors=floors, carpet_ratio=carpet_ratio, **feats)
            if st.session_state.user["email"] != ADMIN_EMAIL:
                cur.execute("INSERT INTO predictions (user_email, inputs_json, quantities_json, cost_breakdown_json, total, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                            (st.session_state.user["email"], json.dumps(inputs), json.dumps(qty_pred), json.dumps(cost_breakdown_result["breakdown"]), float(total_predicted), now()))
                conn.commit()

            # --- PDF DOWNLOAD ---
            if REPORTLAB_OK:
                row = {"user_email": st.session_state.user["email"], "inputs": inputs, "quantities": qty_pred, "breakdown": cost_breakdown_result["breakdown"], "total": total_predicted}
                pdf_bytes = make_invoice_pdf(row)
                st.download_button("📄 Download Invoice (PDF)", data=pdf_bytes, file_name="estimate.pdf", mime="application/pdf", use_container_width=True)


def screen_history():
    """Shows user's prediction history (or all history for admin)."""
    with st.container(border=True):
        st.markdown("### 🕘 Prediction History")
        
        # Hardcoded admin sees all history. Regular users see only their own.
        if st.session_state.user["email"] == ADMIN_EMAIL:
            cur.execute("SELECT id, user_email, total, created_at FROM predictions ORDER BY created_at DESC")
            cols = ["id", "user_email", "total", "created_at"]
        else:
            cur.execute("SELECT id, total, created_at FROM predictions WHERE user_email=? ORDER BY created_at DESC", (st.session_state.user["email"],))
            cols = ["id", "total", "created_at"]

        df = pd.DataFrame(cur.fetchall(), columns=cols)
        
        if df.empty:
            st.info("No predictions yet.")
        else:
            df_display = df.copy()
            df_display['total'] = df_display['total'].apply(lambda x: f"₹ {x:,.0f}")
            st.dataframe(df_display, use_container_width=True, hide_index=True)
            
            sel = st.selectbox("Select a prediction ID to view / export", df["id"].tolist())
            if sel:
                cur.execute("SELECT inputs_json, quantities_json, cost_breakdown_json, total FROM predictions WHERE id=?", (int(sel),))
                row = cur.fetchone()
                if row:
                    inputs = json.loads(row[0]); qty = json.loads(row[1]); brk = json.loads(row[2]); tot = row[3]
                    
                    st.write("##### Inputs")
                    st.dataframe(pd.Series(inputs).to_frame(name='Value'), use_container_width=True)

                    c1, c2 = st.columns(2)
                    with c1:
                        st.write("##### Quantities")
                        qty_display = pd.Series({k: f"{v:,.0f}" for k, v in qty.items()})
                        st.dataframe(qty_display.to_frame(name='Quantity'), use_container_width=True)
                    with c2:
                        st.write("##### Cost Breakdown")
                        brk_display = pd.Series({k: f"₹ {v:,.0f}" for k, v in brk.items()})
                        st.dataframe(brk_display.to_frame(name='Cost (INR)'), use_container_width=True)
                    
                    st.metric("TOTAL", f"₹ {tot:,.0f}")

                    if REPORTLAB_OK:
                        pdf = make_invoice_pdf({"user_email": st.session_state.user["email"], "inputs": inputs, "quantities": qty, "breakdown": brk, "total": tot})
                        st.download_button("📄 Download Invoice (PDF)", data=pdf, file_name=f"estimate_{sel}.pdf", mime="application/pdf", use_container_width=True)


# =========================
#  NAV + ROUTING
# =========================
def navbar():
    """Application header with title and logout button."""
    col1, col_mid, col2 = st.columns([3, 5, 1.5])
    
    with col1:
        st.markdown("### 🏗️ Building Price Predictor")
    with col_mid:
        st.write("") 
    with col2:
        if st.button("Logout", key="logout_btn", use_container_width=True):
            st.session_state.user = None
            st.session_state.view = "login"
            st.rerun()

def app_logged_in():
    """Main application layout for authenticated users."""
    navbar()
    
    tabs_list = ["Predict", "History", "Profile"]
    if st.session_state.user.get("is_admin"):
        tabs_list.append("Admin")
        
    tabs = st.tabs(tabs_list)

    with tabs[0]:
        screen_predict()
    with tabs[1]:
        screen_history()
    with tabs[2]:
        screen_profile()
    if st.session_state.user.get("is_admin"):
        with tabs[3]:
            screen_admin()

# =========================
#  MAIN ROUTER
# =========================

# 1. Set first-time route
if "view" not in st.session_state:
    st.session_state.view = "login"

# 2. Route to the correct layout
if st.session_state.user:
    # --- LOGGED-IN LAYOUT ---
    app_logged_in()
else:
    # --- AUTH LAYOUT ---
    # Centered column for auth screens
    st.title("Welcome to the Building Cost Predictor")
    st.markdown("Please log in or create an account to start your prediction.")
    st.divider()
    _, c_main, _ = st.columns([1, 1.2, 1]) 
    with c_main:
        if st.session_state.view == "login":
            screen_login()
        elif st.session_state.view == "register":
            screen_register()
        else:
            screen_reset_password()