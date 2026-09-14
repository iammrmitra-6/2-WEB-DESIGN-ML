from pydantic import BaseModel

class patient(BaseModel):
    name:str
    age:int


def insert_patient_data(patient :patient):
    print(patient.name)
    print(patient.age)
    print('inserted')

def update_patient_data(patient :patient):
    print(patient.name)
    print(patient.age)
    print('updated')


patient_info={'name' :'nitish','age':30}

patient1 =patient(**patient_info)

insert_patient_data(patient1)
update_patient_data(patient1)
