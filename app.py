from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
from database.db_config import get_db_connection
from datetime import datetime
from predict import predict_patient
from flask import send_file
import os
import json
from utils.pdf_report import generate_pdf_report
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)
from reportlab.lib.styles import getSampleStyleSheet
app = Flask(__name__)

# Secret Key for Session
app.secret_key = "icu_mortality_secret_key_2026"


# ===========================
# LOGIN PAGE
# ===========================
@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()

        if conn is None:
            flash("Database Connection Failed", "danger")
            return redirect(url_for("login"))

        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM staff WHERE username=%s",
            (username,)
        )

        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user and check_password_hash(user["password"], password):

            session["logged_in"] = True
            session["staff_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]

            return redirect(url_for("dashboard"))

        else:
            flash("Invalid Username or Password", "danger")

    return render_template("login.html")


# ===========================
# DASHBOARD
# ===========================
@app.route("/dashboard")
def dashboard():

    # ----------------------------
    # Login Check
    # ----------------------------
    if "logged_in" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # ----------------------------
    # Total Patients
    # ----------------------------
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM patients
    """)
    total_patients = cursor.fetchone()["total"]

    # ----------------------------
    # Total Predictions
    # ----------------------------
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM predictions
    """)
    total_predictions = cursor.fetchone()["total"]

    # ----------------------------
    # Low Risk
    # ----------------------------
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM predictions
        WHERE risk_level='LOW'
    """)
    low_risk = cursor.fetchone()["total"]

    # ----------------------------
    # Medium Risk
    # ----------------------------
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM predictions
        WHERE risk_level='MEDIUM'
    """)
    medium_risk = cursor.fetchone()["total"]

    # ----------------------------
    # High Risk
    # ----------------------------
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM predictions
        WHERE risk_level='HIGH'
    """)
    high_risk = cursor.fetchone()["total"]

    # ----------------------------
    # Monthly Predictions
    # ----------------------------
    cursor.execute("""
        SELECT
            DATE_FORMAT(prediction_time,'%b') AS month,
            COUNT(*) AS total
        FROM predictions
        GROUP BY
            MONTH(prediction_time),
            DATE_FORMAT(prediction_time,'%b')
        ORDER BY
            MONTH(prediction_time)
    """)

    monthly_predictions = cursor.fetchall()
        # ----------------------------
    # Average Mortality Probability
    # ----------------------------
    cursor.execute("""
        SELECT ROUND(AVG(mortality_probability),2) AS avg_probability
        FROM predictions
    """)
    avg_probability = cursor.fetchone()["avg_probability"] or 0

    # ----------------------------
    # Average Confidence Score
    # ----------------------------
    cursor.execute("""
        SELECT ROUND(AVG(confidence_score),2) AS avg_confidence
        FROM predictions
    """)
    avg_confidence = cursor.fetchone()["avg_confidence"] or 0

    # ----------------------------
    # Today's New Patients
    # ----------------------------
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM patients
        WHERE DATE(admission_date)=CURDATE()
    """)
    today_patients = cursor.fetchone()["total"]

    # ----------------------------
    # Today's Predictions
    # ----------------------------
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM predictions
        WHERE DATE(prediction_time)=CURDATE()
    """)
    today_predictions = cursor.fetchone()["total"]

    # ----------------------------
    # Critical Patients
    # ----------------------------
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM predictions
        WHERE risk_level='HIGH'
    """)
    critical_patients = cursor.fetchone()["total"]

    # ----------------------------
    # Recent Predictions
    # ----------------------------
    cursor.execute("""
        SELECT
            p.patient_name,
            pr.risk_level,
            pr.mortality_probability,
            pr.confidence_score,
            pr.prediction_time
        FROM predictions pr
        INNER JOIN patients p
            ON pr.patient_id = p.patient_id
        ORDER BY pr.prediction_time DESC
        LIMIT 5
    """)

    recent_predictions = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "dashboard.html",
        username=session["username"],
        role=session["role"],
        total_patients=total_patients,
        total_predictions=total_predictions,
        low_risk=low_risk,
        medium_risk=medium_risk,
        high_risk=high_risk,
        monthly_predictions=monthly_predictions,
        recent_predictions=recent_predictions,

        avg_probability=avg_probability,
        avg_confidence=avg_confidence,
        today_patients=today_patients,
        today_predictions=today_predictions,
        critical_patients=critical_patients
    )

@app.route("/patient-form", methods=["GET", "POST"])
def patient_form():

    if "logged_in" not in session:
        return redirect("/")

    if request.method == "POST":

        patient_name = request.form["patient_name"]
        age = request.form["age"]
        gender = request.form["gender"]
        phone = request.form["phone"]
        admission_date = request.form["admission_date"]

        height = request.form["height"]
        weight = request.form["weight"]
        blood_group = request.form["blood_group"]
        address = request.form["address"]
        emergency_contact = request.form["emergency_contact"]

        conn = get_db_connection()
        cursor = conn.cursor()

        sql = """
        INSERT INTO patients
        (
            patient_name,
            age,
            gender,
            phone,
            admission_date,
            height,
            weight,
            blood_group,
            address,
            emergency_contact
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """

        values = (
            patient_name,
            age,
            gender,
            phone,
            admission_date,
            height,
            weight,
            blood_group,
            address,
            emergency_contact
        )

        cursor.execute(sql, values)

        conn.commit()

        cursor.close()
        conn.close()

        flash("Patient Registered Successfully", "success")

        return redirect("/patient-form")

    return render_template("patient_form.html")


@app.route("/patients")
def patients():

    if "logged_in" not in session:
        return redirect("/")

    conn = get_db_connection()

    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM patients ORDER BY patient_id DESC")

    patient_data = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "patients.html",
        patients=patient_data
    )
    
# ==========================================
# PATIENT PROFILE
# ==========================================
# =====================================================
# PATIENT PROFILE
# =====================================================
@app.route("/patient/<int:patient_id>")
def patient_profile(patient_id):

    # ----------------------------
    # Login Check
    # ----------------------------
    if "logged_in" not in session:
        return redirect("/")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # ----------------------------
    # Patient Details
    # ----------------------------
    cursor.execute("""
        SELECT *
        FROM patients
        WHERE patient_id=%s
    """, (patient_id,))

    patient = cursor.fetchone()

    if patient is None:
        flash("Patient not found.", "danger")
        cursor.close()
        conn.close()
        return redirect("/patients")

    # ----------------------------
    # Latest ICU Assessment
    # ----------------------------
    cursor.execute("""
        SELECT *
        FROM icu_assessments
        WHERE patient_id=%s
        ORDER BY assessment_date DESC
        LIMIT 1
    """, (patient_id,))

    assessment = cursor.fetchone()

    if assessment is None:
        flash("No ICU Assessment found.", "warning")
        cursor.close()
        conn.close()
        return redirect("/patients")

    # ----------------------------
    # Latest Prediction
    # ----------------------------
    cursor.execute("""
        SELECT *
        FROM predictions
        WHERE assessment_id IN
        (
            SELECT assessment_id
            FROM icu_assessments
            WHERE patient_id=%s
        )
        ORDER BY prediction_time DESC
        LIMIT 1
    """, (patient_id,))

    prediction = cursor.fetchone()

    # ----------------------------
    # Debug Output
    # ----------------------------
    print("Prediction:")
    print(prediction)

    # ----------------------------
    # Decode SHAP Summary
    # ----------------------------
    shap_data = []

    if prediction and prediction["shap_summary"]:

        try:
            shap_data = json.loads(
                prediction["shap_summary"]
            )

        except Exception as e:
            print("SHAP Decode Error:", e)
            shap_data = []

    print("SHAP Data:")
    print(shap_data)

    # ----------------------------
    # Close Database
    # ----------------------------
    cursor.close()
    conn.close()

    # ----------------------------
    # Render Template
    # ----------------------------
    return render_template(
        "patient_profile.html",
        patient=patient,
        assessment=assessment,
        prediction=prediction,
        shap_data=shap_data
    )
@app.route("/prediction-list")
def prediction_list():

    if "logged_in" not in session:
        return redirect("/")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            p.patient_id,
            p.patient_name,
            p.age,
            p.gender,
            p.admission_date,
            (
                SELECT COUNT(*)
                FROM icu_assessments a
                WHERE a.patient_id = p.patient_id
            ) AS assessments
        FROM patients p
        ORDER BY p.patient_name
    """)

    patients = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "prediction_list.html",
        patients=patients
    )

@app.route("/prediction", methods=["GET", "POST"])
def prediction():

    if "logged_in" not in session:
        return redirect("/")

    result = None

    if request.method == "POST":

        patient_data = {

            "age": float(request.form["age"]),
            "gender": request.form["gender"],
            "heart_rate": float(request.form["heart_rate"]),
            "systolic_bp": float(request.form["systolic_bp"]),
            "diastolic_bp": float(request.form["diastolic_bp"]),
            "respiratory_rate": float(request.form["respiratory_rate"]),
            "temperature": float(request.form["temperature"]),
            "spo2": float(request.form["spo2"]),
            "gcs": float(request.form["gcs"]),
            "glucose": float(request.form["glucose"]),
            "hemoglobin": float(request.form["hemoglobin"]),
            "wbc": float(request.form["wbc"]),
            "platelets": float(request.form["platelets"]),
            "creatinine": float(request.form["creatinine"]),
            "bun": float(request.form["bun"]),
            "sodium": float(request.form["sodium"]),
            "potassium": float(request.form["potassium"]),
            "lactate": float(request.form["lactate"]),
            "bilirubin": float(request.form["bilirubin"]),
            "urine_output": float(request.form["urine_output"]),
            "ventilator": int(request.form["ventilator"]),
            "diabetes": int(request.form["diabetes"]),
            "hypertension": int(request.form["hypertension"]),
            "ckd": int(request.form["ckd"]),
            "heart_disease": int(request.form["heart_disease"]),

            # Engineered Features
            "map": (
                float(request.form["systolic_bp"]) +
                2 * float(request.form["diastolic_bp"])
            ) / 3,

            "pulse_pressure": (
                float(request.form["systolic_bp"]) -
                float(request.form["diastolic_bp"])
            ),

            "shock_index": (
                float(request.form["heart_rate"]) /
                float(request.form["systolic_bp"])
            ),

            "bun_creatinine_ratio": (
                float(request.form["bun"]) /
                (float(request.form["creatinine"]) + 0.01)
            ),

            "oxygen_deficit": (
                100 -
                float(request.form["spo2"])
            ),

            "elderly": int(float(request.form["age"]) >= 65)
        }

        result = predict_patient(patient_data)

    return render_template(
        "prediction.html",
        result=result
    )


@app.route("/history")
def history():

    if "logged_in" not in session:
        return redirect("/")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            p.patient_id,
            p.patient_name,
            pr.prediction_time,
            pr.risk_level,
            pr.mortality_probability,
            pr.confidence_score
        FROM predictions pr
        INNER JOIN patients p
            ON pr.patient_id = p.patient_id
        ORDER BY pr.prediction_time DESC
    """)

    predictions = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "history.html",
        predictions=predictions
    )

@app.route("/reports")
def reports():

    if "logged_in" not in session:
        return redirect("/")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            patient_id,
            patient_name,
            age,
            gender,
            admission_date
        FROM patients
        ORDER BY patient_name
    """)

    patients = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "reports.html",
        patients=patients
    )
@app.route("/reports/<int:patient_id>")
def download_report(patient_id):

    if "logged_in" not in session:
        return redirect("/")

    return generate_pdf_report(patient_id)
@app.route("/predict/<int:patient_id>")
def predict_patient_route(patient_id):

    # --------------------------------
    # Login Check
    # --------------------------------
    if "logged_in" not in session:
        return redirect("/")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # --------------------------------
    # Get Patient Information
    # --------------------------------
    cursor.execute("""
        SELECT *
        FROM patients
        WHERE patient_id=%s
    """, (patient_id,))

    patient = cursor.fetchone()

    if patient is None:
        flash("Patient not found.", "danger")
        cursor.close()
        conn.close()
        return redirect("/patients")

    # --------------------------------
    # Get Latest ICU Assessment
    # --------------------------------
    cursor.execute("""
        SELECT *
        FROM icu_assessments
        WHERE patient_id=%s
        ORDER BY assessment_id DESC
        LIMIT 1
    """, (patient_id,))

    assessment = cursor.fetchone()

    if assessment is None:
        flash("No ICU Assessment Found.", "warning")
        cursor.close()
        conn.close()
        return redirect("/patients")

    # --------------------------------
    # Build Features Dictionary
    # --------------------------------
    features = {

        "age": patient["age"],
        "gender": patient["gender"],

        "heart_rate": assessment["heart_rate"],
        "systolic_bp": assessment["systolic_bp"],
        "diastolic_bp": assessment["diastolic_bp"],
        "respiratory_rate": assessment["respiratory_rate"],
        "temperature": assessment["temperature"],
        "spo2": assessment["spo2"],
        "gcs": assessment["gcs"],

        "glucose": assessment["glucose"],
        "hemoglobin": assessment["hemoglobin"],
        "wbc": assessment["wbc"],
        "platelets": assessment["platelets"],

        "creatinine": assessment["creatinine"],
        "bun": assessment["bun"],
        "sodium": assessment["sodium"],
        "potassium": assessment["potassium"],

        "lactate": assessment["lactate"],
        "bilirubin": assessment["bilirubin"],
        "urine_output": assessment["urine_output"],

        "ventilator": assessment["ventilator"],
        "diabetes": assessment["diabetes"],
        "hypertension": assessment["hypertension"],
        "ckd": assessment["ckd"],
        "heart_disease": assessment["heart_disease"]
    }

        # --------------------------------
    # AI Prediction
    # --------------------------------
    result = predict_patient(features)
    import json

    shap_summary = json.dumps(result["shap"])

    # --------------------------------
    # Save Prediction
    # --------------------------------
    sql = """
    INSERT INTO predictions
    (
        patient_id,
        assessment_id,
        model_name,
        prediction_class,
        mortality_probability,
        risk_level,
        confidence_score,
        recommendation,
        shap_summary
    )
    VALUES
    (
        %s,%s,%s,%s,%s,%s,%s,%s,%s
    )
    """

    values = (

    patient_id,

    assessment["assessment_id"],

    "Stacking Ensemble",

    result["prediction"],

    result["probability"],

    result["risk"],

    result["confidence"],

    result["recommendation"],

    shap_summary

)

    cursor.execute(sql, values)
    conn.commit()

    cursor.close()
    conn.close()

    flash("Prediction Completed Successfully!", "success")

    return redirect(
        url_for(
            "patient_profile",
            patient_id=patient_id
        )
    )
@app.route("/prediction-history/<int:patient_id>")
def prediction_history(patient_id):

    if "logged_in" not in session:
        return redirect("/")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Patient Details
    cursor.execute("""
        SELECT *
        FROM patients
        WHERE patient_id=%s
    """, (patient_id,))

    patient = cursor.fetchone()

    # Prediction History
    cursor.execute("""
        SELECT *
        FROM predictions
        WHERE patient_id=%s
        ORDER BY prediction_time DESC
    """, (patient_id,))

    history = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "prediction_history.html",
        patient=patient,
        history=history
    )
# ===========================
# LOGOUT
# ===========================
@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))

@app.route("/icu-assessment", methods=["GET", "POST"])
def icu_assessment():

    if "logged_in" not in session:
        return redirect("/")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":

        # ==========================
        # Patient Information
        # ==========================
        patient_id = request.form["patient_id"]

        # ==========================
        # Vital Signs
        # ==========================
        heart_rate = request.form["heart_rate"]
        systolic_bp = request.form["systolic_bp"]
        diastolic_bp = request.form["diastolic_bp"]
        respiratory_rate = request.form["respiratory_rate"]
        temperature = request.form["temperature"]
        spo2 = request.form["spo2"]
        gcs = request.form["gcs"]

        # ==========================
        # Laboratory Values
        # ==========================
        glucose = request.form["glucose"]
        hemoglobin = request.form["hemoglobin"]
        wbc = request.form["wbc"]
        platelets = request.form["platelets"]
        creatinine = request.form["creatinine"]
        bun = request.form["bun"]
        sodium = request.form["sodium"]
        potassium = request.form["potassium"]
        lactate = request.form["lactate"]
        bilirubin = request.form["bilirubin"]
        urine_output = request.form["urine_output"]

        # ==========================
        # Medical History
        # ==========================
        ventilator = request.form["ventilator"]
        diabetes = request.form["diabetes"]
        hypertension = request.form["hypertension"]
        ckd = request.form["ckd"]
        heart_disease = request.form["heart_disease"]

        # ==========================
        # Insert into Database
        # ==========================
        sql = """
        INSERT INTO icu_assessments
        (
            patient_id,
            heart_rate,
            systolic_bp,
            diastolic_bp,
            respiratory_rate,
            temperature,
            spo2,
            gcs,
            glucose,
            hemoglobin,
            wbc,
            platelets,
            creatinine,
            bun,
            sodium,
            potassium,
            lactate,
            bilirubin,
            urine_output,
            ventilator,
            diabetes,
            hypertension,
            ckd,
            heart_disease
        )
        VALUES
        (
            %s,%s,%s,%s,%s,%s,%s,%s,
            %s,%s,%s,%s,%s,%s,%s,%s,
            %s,%s,%s,%s,%s,%s,%s,%s
        )
        """

        values = (
            patient_id,
            heart_rate,
            systolic_bp,
            diastolic_bp,
            respiratory_rate,
            temperature,
            spo2,
            gcs,
            glucose,
            hemoglobin,
            wbc,
            platelets,
            creatinine,
            bun,
            sodium,
            potassium,
            lactate,
            bilirubin,
            urine_output,
            ventilator,
            diabetes,
            hypertension,
            ckd,
            heart_disease
        )

        cursor.execute(sql, values)
        conn.commit()

        flash("ICU Assessment Saved Successfully", "success")

        cursor.close()
        conn.close()

        return redirect("/icu-assessment")

    # ==========================
    # Load Patient List
    # ==========================
    cursor.execute("""
        SELECT patient_id, patient_name
        FROM patients
        ORDER BY patient_name
    """)

    patients = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "icu_assessment.html",
        patients=patients
    )

# ===========================
# MAIN
# ===========================
if __name__ == "__main__":
    app.run(debug=True)