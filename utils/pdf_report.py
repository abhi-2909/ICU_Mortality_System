import os
from datetime import datetime

from flask import (
    flash,
    redirect,
    send_file
)
from database.db_config import get_db_connection

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import inch

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image
)


def generate_pdf_report(patient_id):

    # ==========================================
    # Database Connection
    # ==========================================

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # ==========================================
    # Patient Details
    # ==========================================

    cursor.execute("""
        SELECT *
        FROM patients
        WHERE patient_id=%s
    """, (patient_id,))

    patient = cursor.fetchone()

    # ==========================================
    # Latest ICU Assessment
    # ==========================================

    cursor.execute("""
        SELECT *
        FROM icu_assessments
        WHERE patient_id=%s
        ORDER BY assessment_id DESC
        LIMIT 1
    """, (patient_id,))

    assessment = cursor.fetchone()

    # ==========================================
    # Latest Prediction
    # ==========================================

    cursor.execute("""
        SELECT *
        FROM predictions
        WHERE patient_id=%s
        ORDER BY prediction_id DESC
        LIMIT 1
    """, (patient_id,))

    prediction = cursor.fetchone()

    cursor.close()
    conn.close()

    # ==========================================
    # Validation
    # ==========================================

    if patient is None:
        flash("Patient not found.", "danger")
        return redirect("/patients")

    if assessment is None:
        flash("No ICU Assessment found.", "danger")
        return redirect(f"/patient/{patient_id}")

    if prediction is None:
        flash("No Prediction found.", "danger")
        return redirect(f"/patient/{patient_id}")

    # ==========================================
    # PDF Styles
    # ==========================================

    styles = getSampleStyleSheet()

    title_style = styles["Title"]
    title_style.alignment = TA_CENTER
    title_style.textColor = colors.darkblue

    heading_style = styles["Heading2"]
    heading_style.textColor = colors.darkred

    normal_style = styles["BodyText"]

    # ==========================================
    # Create Reports Folder
    # ==========================================

    os.makedirs("reports", exist_ok=True)

    pdf_path = f"reports/patient_{patient_id}_report.pdf"

    doc = SimpleDocTemplate(
        pdf_path,
        leftMargin=30,
        rightMargin=30,
        topMargin=30,
        bottomMargin=30
    )

    story = []

    # ==========================================
    # Current Date & Time
    # ==========================================

    report_date = datetime.now().strftime("%d-%b-%Y")
    report_time = datetime.now().strftime("%I:%M %p")
    
    # ==========================================
    # Hospital Logo
    # ==========================================

    logo_path = "static/images/hospital_logo.png"

    if os.path.exists(logo_path):

        logo = Image(
            logo_path,
            width=55,
            height=55
        )

        story.append(logo)

    # ==========================================
    # Hospital Header
    # ==========================================

    story.append(
        Paragraph(
            "<font size='22'><b>CITYCARE SUPER SPECIALITY HOSPITAL</b></font>",
            title_style
        )
    )

    story.append(
        Paragraph(
            "<font size='13'>AI Powered ICU Mortality Prediction System</font>",
            heading_style
        )
    )

    story.append(
        Paragraph(
            "<font size='10'>Jaipur, Rajasthan | NABH Accredited Hospital</font>",
            normal_style
        )
    )

    story.append(
        Paragraph(
            "<font size='10'>Phone : +91-9876543210 | Email : info@citycarehospital.com</font>",
            normal_style
        )
    )

    story.append(Spacer(1,15))

    # ==========================================
    # Report Information
    # ==========================================

    report_data = [

        ["Report ID", f"ICU-{patient_id:05d}"],

        ["Generated Date", report_date],

        ["Generated Time", report_time]

    ]

    report_table = Table(
        report_data,
        colWidths=[150,250]
    )

    report_table.setStyle(TableStyle([

        ("GRID",(0,0),(-1,-1),1,colors.grey),

        ("BACKGROUND",(0,0),(0,-1),colors.HexColor("#D6EAF8")),

        ("FONTNAME",(0,0),(-1,-1),"Helvetica-Bold"),

        ("BOTTOMPADDING",(0,0),(-1,-1),8),

        ("TOPPADDING",(0,0),(-1,-1),8),

        ("BACKGROUND",(1,0),(1,-1),colors.white)

    ]))

    story.append(report_table)

    story.append(Spacer(1,20))

    # ==========================================
    # PATIENT INFORMATION
    # ==========================================

    story.append(
        Paragraph(
            "<font size='15'><b>PATIENT INFORMATION</b></font>",
            heading_style
        )
    )

    story.append(Spacer(1,8))

    patient_data = [

        [
            "Patient ID",
            patient["patient_id"],
            "Admission Date",
            str(patient["admission_date"])
        ],

        [
            "Patient Name",
            patient["patient_name"],
            "Gender",
            patient["gender"]
        ],

        [
            "Age",
            f"{patient['age']} Years",
            "Phone",
            patient["phone"]
        ]

    ]

    patient_table = Table(
        patient_data,
        colWidths=[110,170,110,170]
    )

    patient_table.setStyle(TableStyle([

        ("GRID",(0,0),(-1,-1),1,colors.grey),

        ("BACKGROUND",(0,0),(0,-1),colors.HexColor("#EAF2F8")),

        ("BACKGROUND",(2,0),(2,-1),colors.HexColor("#EAF2F8")),

        ("FONTNAME",(0,0),(0,-1),"Helvetica-Bold"),

        ("FONTNAME",(2,0),(2,-1),"Helvetica-Bold"),

        ("FONTNAME",(1,0),(1,-1),"Helvetica"),

        ("FONTNAME",(3,0),(3,-1),"Helvetica"),

        ("BOTTOMPADDING",(0,0),(-1,-1),8),

        ("TOPPADDING",(0,0),(-1,-1),8),

        ("ALIGN",(0,0),(-1,-1),"LEFT"),

        ("VALIGN",(0,0),(-1,-1),"MIDDLE")

    ]))

    story.append(patient_table)

    story.append(Spacer(1,20))

    # ==========================================
    # ICU ASSESSMENT
    # ==========================================

    story.append(
        Paragraph(
            "<font size='15'><b>LATEST ICU ASSESSMENT</b></font>",
            heading_style
        )
    )

    story.append(Spacer(1,8))

    assessment_data = [

        ["Parameter", "Value"],

        ["Heart Rate (bpm)", assessment["heart_rate"]],

        ["Blood Pressure",
        f"{assessment['systolic_bp']}/{assessment['diastolic_bp']} mmHg"],

        ["Respiratory Rate", assessment["respiratory_rate"]],

        ["Temperature (°C)", assessment["temperature"]],

        ["SpO₂ (%)", assessment["spo2"]],

        ["GCS Score", assessment["gcs"]],

        ["Glucose (mg/dL)", assessment["glucose"]],

        ["Hemoglobin (g/dL)", assessment["hemoglobin"]],

        ["WBC (×10³/µL)", assessment["wbc"]],

        ["Platelets", assessment["platelets"]],

        ["Creatinine", assessment["creatinine"]],

        ["BUN", assessment["bun"]],

        ["Sodium", assessment["sodium"]],

        ["Potassium", assessment["potassium"]],

        ["Lactate", assessment["lactate"]],

        ["Bilirubin", assessment["bilirubin"]],

        ["Urine Output", assessment["urine_output"]],

        ["Ventilator",
        "YES" if assessment["ventilator"] else "NO"],

        ["Diabetes",
        "YES" if assessment["diabetes"] else "NO"],

        ["Hypertension",
        "YES" if assessment["hypertension"] else "NO"],

        ["CKD",
        "YES" if assessment["ckd"] else "NO"],

        ["Heart Disease",
        "YES" if assessment["heart_disease"] else "NO"]

    ]

    assessment_table = Table(
        assessment_data,
        colWidths=[220,220]
    )

    assessment_table.setStyle(TableStyle([

        ("GRID",(0,0),(-1,-1),1,colors.grey),

        ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#1F618D")),

        ("TEXTCOLOR",(0,0),(-1,0),colors.white),

        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),

        ("BACKGROUND",(0,1),(0,-1),colors.HexColor("#EBF5FB")),

        ("FONTNAME",(0,1),(-1,-1),"Helvetica"),

        ("BOTTOMPADDING",(0,0),(-1,-1),8),

        ("TOPPADDING",(0,0),(-1,-1),8),

        ("ALIGN",(0,0),(-1,-1),"CENTER"),

        ("VALIGN",(0,0),(-1,-1),"MIDDLE")

    ]))

    story.append(assessment_table)

    story.append(Spacer(1,20))

    # ==========================================
    # AI PREDICTION SUMMARY
    # ==========================================

    story.append(
        Paragraph(
            "<font size='15'><b>AI PREDICTION SUMMARY</b></font>",
            heading_style
        )
    )

    story.append(Spacer(1,8))

    # ------------------------------------------
    # Risk Color
    # ------------------------------------------

    if prediction["risk_level"] == "LOW":

        risk_color = colors.green

    elif prediction["risk_level"] == "MEDIUM":

        risk_color = colors.orange

    else:

        risk_color = colors.red

    # ------------------------------------------
    # Prediction Table
    # ------------------------------------------

    prediction_data = [

        ["Prediction Class",
        prediction["prediction_class"]],

        ["Mortality Probability",
        f"{prediction['mortality_probability']} %"],

        ["Confidence Score",
        f"{prediction['confidence_score']} %"],

        ["Risk Level",
        prediction["risk_level"]],

        ["Prediction Time",
        str(prediction["prediction_time"])]

    ]

    prediction_table = Table(
        prediction_data,
        colWidths=[200,240]
    )

    prediction_table.setStyle(TableStyle([

        ("GRID",(0,0),(-1,-1),1,colors.grey),

        ("BACKGROUND",(0,0),(0,-1),colors.HexColor("#FADBD8")),

        ("FONTNAME",(0,0),(0,-1),"Helvetica-Bold"),

        ("BOTTOMPADDING",(0,0),(-1,-1),8),

        ("TOPPADDING",(0,0),(-1,-1),8),

        ("VALIGN",(0,0),(-1,-1),"MIDDLE")

    ]))

    story.append(prediction_table)

    story.append(Spacer(1,15))

    # ==========================================
    # OVERALL RISK LEVEL
    # ==========================================

    risk_table = Table(

        [[
            f"OVERALL RISK LEVEL : {prediction['risk_level']}"
        ]],

        colWidths=[440]

    )

    risk_table.setStyle(TableStyle([

        ("BACKGROUND",(0,0),(-1,-1),risk_color),

        ("TEXTCOLOR",(0,0),(-1,-1),colors.white),

        ("ALIGN",(0,0),(-1,-1),"CENTER"),

        ("FONTNAME",(0,0),(-1,-1),"Helvetica-Bold"),

        ("FONTSIZE",(0,0),(-1,-1),16),

        ("BOTTOMPADDING",(0,0),(-1,-1),12),

        ("TOPPADDING",(0,0),(-1,-1),12)

    ]))

    story.append(risk_table)

    story.append(Spacer(1,20))

    # ==========================================
    # CLINICAL RECOMMENDATION
    # ==========================================

    story.append(
        Paragraph(
            "<font size='15'><b>CLINICAL RECOMMENDATION</b></font>",
            heading_style
        )
    )

    story.append(Spacer(1,8))

    recommendation_table = Table(

        [[prediction["recommendation"]]],

        colWidths=[440]

    )

    recommendation_table.setStyle(TableStyle([

        ("GRID",(0,0),(-1,-1),1,colors.green),

        ("BACKGROUND",(0,0),(-1,-1),colors.HexColor("#EAFAF1")),

        ("BOTTOMPADDING",(0,0),(-1,-1),12),

        ("TOPPADDING",(0,0),(-1,-1),12),

        ("LEFTPADDING",(0,0),(-1,-1),10),

        ("RIGHTPADDING",(0,0),(-1,-1),10)

    ]))

    story.append(recommendation_table)

    story.append(Spacer(1,20))

    # ==========================================
    # RISK METER
    # ==========================================

    story.append(
        Paragraph(
            "<font size='15'><b>RISK METER</b></font>",
            heading_style
        )
    )

    story.append(Spacer(1,8))

    probability = float(prediction["mortality_probability"])

    bar_width = int((probability / 100) * 40)

    meter = "█" * bar_width

    meter += "░" * (40 - bar_width)

    risk_meter = Table(

        [[meter]],

        colWidths=[440]

    )

    risk_meter.setStyle(TableStyle([

        ("GRID",(0,0),(-1,-1),1,colors.grey),

        ("BACKGROUND",(0,0),(-1,-1),colors.white),

        ("TEXTCOLOR",(0,0),(-1,-1),risk_color),

        ("FONTNAME",(0,0),(-1,-1),"Courier-Bold"),

        ("FONTSIZE",(0,0),(-1,-1),12),

        ("ALIGN",(0,0),(-1,-1),"CENTER"),

        ("BOTTOMPADDING",(0,0),(-1,-1),10),

        ("TOPPADDING",(0,0),(-1,-1),10)

    ]))

    story.append(risk_meter)

    story.append(Spacer(1,8))

    story.append(
        Paragraph(
            f"<b>Mortality Probability : {probability:.2f}%</b>",
            normal_style
        )
    )

    story.append(Spacer(1,20))

    # ==========================================
    # DOCTOR NOTES
    # ==========================================

    story.append(
        Paragraph(
            "<font size='15'><b>DOCTOR NOTES</b></font>",
            heading_style
        )
    )

    story.append(Spacer(1,8))

    doctor_notes = Table(

        [[
            "\n\n\n\n"
        ]],

        colWidths=[440],
        rowHeights=[90]

    )

    doctor_notes.setStyle(TableStyle([

        ("GRID",(0,0),(-1,-1),1,colors.black),

        ("BACKGROUND",(0,0),(-1,-1),colors.white)

    ]))

    story.append(doctor_notes)

    story.append(Spacer(1,20))

    # ==========================================
    # SIGNATURES
    # ==========================================

    story.append(
        Paragraph(
            "<font size='15'><b>AUTHORIZATION</b></font>",
            heading_style
        )
    )

    story.append(Spacer(1,10))

    signature_data = [

        [

            "Prepared By\n\nAI Decision Support System",

            "Reviewed By\n\nICU Consultant\n\n________________",

            "Approved By\n\nMedical Superintendent\n\n________________"

        ]

    ]

    signature_table = Table(

        signature_data,

        colWidths=[150,150,150]

    )

    signature_table.setStyle(TableStyle([

        ("GRID",(0,0),(-1,-1),1,colors.grey),

        ("ALIGN",(0,0),(-1,-1),"CENTER"),

        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),

        ("BOTTOMPADDING",(0,0),(-1,-1),25),

        ("TOPPADDING",(0,0),(-1,-1),25),

        ("FONTNAME",(0,0),(-1,-1),"Helvetica-Bold")

    ]))

    story.append(signature_table)

    story.append(Spacer(1,20))

    # ==========================================
    # FOOTER
    # ==========================================

    footer = Table(

        [[

            "Confidential Medical Report\n"
            "Generated Automatically by ICU Mortality Prediction System\n"
            f"Date : {report_date}      Time : {report_time}"

        ]],

        colWidths=[450]

    )

    footer.setStyle(TableStyle([

        ("BACKGROUND",(0,0),(-1,-1),colors.HexColor("#EBF5FB")),

        ("GRID",(0,0),(-1,-1),1,colors.grey),

        ("ALIGN",(0,0),(-1,-1),"CENTER"),

        ("BOTTOMPADDING",(0,0),(-1,-1),10),

        ("TOPPADDING",(0,0),(-1,-1),10),

        ("FONTNAME",(0,0),(-1,-1),"Helvetica")

    ]))

    story.append(footer)

    story.append(Spacer(1,15))

    # ==========================================
    # BUILD PDF
    # ==========================================

    doc.build(story)

    # ==========================================
    # DOWNLOAD PDF
    # ==========================================

    return send_file(

        pdf_path,

        as_attachment=True

    )