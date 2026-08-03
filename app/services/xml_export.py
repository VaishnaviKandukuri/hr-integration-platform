from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom
from app.models.db_models import Employee


def employee_to_xml(employee: Employee) -> str:
    root = Element("PayrollRecord")

    SubElement(root, "EmployeeID").text = employee.id
    SubElement(root, "EmployeeNumber").text = employee.employee_number or ""
    SubElement(root, "FirstName").text = employee.first_name
    SubElement(root, "LastName").text = employee.last_name

    salary_elem = SubElement(root, "BaseSalary")
    salary_elem.text = str(employee.base_salary)
    salary_elem.set("currency", employee.currency)

    SubElement(root, "Department").text = employee.department
    SubElement(root, "JobTitle").text = employee.job_title
    SubElement(root, "EmploymentStatus").text = employee.employment_status

    rough_string = tostring(root, encoding="unicode")
    pretty = minidom.parseString(rough_string).toprettyxml(indent="  ")
    return pretty