from predict import predict_patient

sample = {

    "age":72,

    "gender":"Male",

    "heart_rate":120,

    "systolic_bp":88,

    "diastolic_bp":55,

    "respiratory_rate":30,

    "temperature":39,

    "spo2":86,

    "gcs":7,

    "glucose":210,

    "hemoglobin":10,

    "wbc":18,

    "platelets":180,

    "creatinine":2.5,

    "bun":60,

    "sodium":130,

    "potassium":5.6,

    "lactate":5,

    "bilirubin":1.5,

    "urine_output":400,

    "ventilator":1,

    "diabetes":1,

    "hypertension":1,

    "ckd":1,

    "heart_disease":1

}

print(predict_patient(sample))