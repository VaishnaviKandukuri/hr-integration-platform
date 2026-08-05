import csv
import os
from datetime import datetime
from app.database import SessionLocal
from app.models.db_models import Employee


def generate_batch_file() -> str:
    db = SessionLocal()
    try:
        employees = db.query(Employee).filter(Employee.employment_status == "active").all()

        os.makedirs("outbound", exist_ok=True)
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"outbound/payroll_batch_{timestamp}.csv"

        with open(filename, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["employee_number", "first_name", "last_name", "department", "job_title", "base_salary", "currency"])
            for emp in employees:
                writer.writerow([
                    emp.employee_number,
                    emp.first_name,
                    emp.last_name,
                    emp.department,
                    emp.job_title,
                    emp.base_salary,
                    emp.currency,
                ])

        return filename
    finally:
        db.close()


def upload_via_sftp(local_filepath: str):
    """
    Real SFTP upload logic, using paramiko. Not executed in this project since
    we have no live SFTP server/credentials to target - shown to demonstrate
    the correct pattern for a real deployment.
    """
    import paramiko

    transport = paramiko.Transport(("sftp.example-payroll-vendor.com", 22))
    transport.connect(username="our-sftp-user", password="would-come-from-env-vars")
    sftp = paramiko.SFTPClient.from_transport(transport)

    remote_path = f"/incoming/{local_filepath.split('/')[-1]}"
    sftp.put(local_filepath, remote_path)

    sftp.close()
    transport.close()


if __name__ == "__main__":
    filepath = generate_batch_file()
    print(f"Batch file generated: {filepath}")
    print("(SFTP upload not executed - no live server configured. See upload_via_sftp() for the real implementation pattern.)")