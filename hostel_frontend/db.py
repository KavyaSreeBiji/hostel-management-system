import pymysql
import pymysql.cursors
from pymysql import Error
import os

DB_CONFIG = {
    'host': os.environ.get("MYSQLHOST", "switchback.proxy.rlwy.net"),
    'database': os.environ.get("MYSQL_DATABASE", "railway"),
    'user': os.environ.get("MYSQLUSER", "root"),
    'password': os.environ.get("MYSQLPASSWORD", "ZSItBptgvtNkvmymAcBFgGmNePMHBjNj"),
    'port': int(os.environ.get("MYSQLPORT", 32270))
}

def create_connection():
    try:
        connection = pymysql.connect(**DB_CONFIG, cursorclass=pymysql.cursors.DictCursor)
        return connection
    except Exception as e:
        print(f"Error while connecting to MySQL: {e}")
        return None

def execute_query(query, params=None):
    connection = create_connection()
    if not connection:
        return False
    try:
        cursor = connection.cursor()
        cursor.execute(query, params or ())
        connection.commit()
        return True
    except Error as e:
        print(f"Error executing query: {e}")
        return False
    finally:
        try:
            cursor.close()
            connection.close()
        except:
            pass

def _fetch_data(query, params=None, fetch_one=False):
    connection = create_connection()
    if not connection:
        return None
    try:
        cursor = connection.cursor()
        cursor.execute(query, params or ())
        if fetch_one:
            result = cursor.fetchone()
        else:
            result = cursor.fetchall()
        return result
    except Error as e:
        print(f"Error executing fetch query: {e}")
        return None
    finally:
        try:
            cursor.close()
            connection.close()
        except:
            pass

def check_room_availability():
    query = "SELECT * FROM Rooms WHERE Availability_Status = 'Available'"
    return _fetch_data(query)

def fetch_all_rooms():
    query = "SELECT * FROM Rooms"
    return _fetch_data(query)

def add_room(capacity, price):
    query = "INSERT INTO Rooms (Capacity, Occupancy, Availability_Status, Price) VALUES (%s, 0, 'Available', %s)"
    return execute_query(query, (capacity, price))

def get_billing_by_student(student_id):
    query = "SELECT * FROM Billing WHERE Student_ID = %s ORDER BY Due_Date DESC"
    return _fetch_data(query, (student_id,))

def allocate_room(student_id, room_id):
    connection = create_connection()
    if not connection:
        return False
    try:
        cursor = connection.cursor()
        connection.begin()

        cursor.execute("UPDATE Students SET Room_ID = %s WHERE Student_ID = %s", (room_id, student_id))
        cursor.execute(
            "UPDATE Rooms SET Occupancy = Occupancy + 1, Availability_Status = IF(Occupancy + 1 >= Capacity, 'Full', 'Available') WHERE Room_ID = %s",
            (room_id,)
        )
        cursor.execute("SELECT Price FROM Rooms WHERE Room_ID = %s", (room_id,))
        room_data = cursor.fetchone()
        if room_data and 'Price' in room_data:
            cursor.execute(
                "INSERT INTO Billing (Student_ID, Amount, Issue_Date, Due_Date, Status) VALUES (%s, %s, CURDATE(), DATE_ADD(CURDATE(), INTERVAL 10 DAY), 'Not Paid')",
                (student_id, room_data['Price'])
            )
        connection.commit()
        return True
    except Error as e:
        print(f"Error allocating room: {e}")
        connection.rollback()
        return False
    finally:
        try:
            cursor.close()
            connection.close()
        except:
            pass

def remove_student_from_room(student_id, room_id):
    connection = create_connection()
    if not connection:
        return False
    try:
        cursor = connection.cursor()
        connection.begin()
        cursor.execute("UPDATE Students SET Room_ID = NULL WHERE Student_ID = %s", (student_id,))
        cursor.execute(
            "UPDATE Rooms SET Occupancy = GREATEST(0, Occupancy - 1), Availability_Status = 'Available' WHERE Room_ID = %s",
            (room_id,)
        )
        connection.commit()
        return True
    except Error as e:
        connection.rollback()
        return False
    finally:
        try:
            cursor.close()
            connection.close()
        except:
            pass

def process_payment(bill_id):
    query = "UPDATE Billing SET Status = 'Paid' WHERE Bill_ID = %s"
    return execute_query(query, (bill_id,))

def submit_complaint(student_id, category, description):
    query = "INSERT INTO Complaints (Student_ID, Category, Description, Status) VALUES (%s, %s, %s, 'Pending')"
    return execute_query(query, (student_id, category, description))

def fetch_all_complaints():
    query = """
    SELECT c.Complaint_ID, c.Student_ID, s.Name, c.Category, c.Description, c.Status 
    FROM Complaints c 
    JOIN Students s ON c.Student_ID = s.Student_ID 
    ORDER BY c.Status DESC, c.Complaint_ID ASC
    """
    return _fetch_data(query)

def fetch_student_complaints(student_id):
    query = "SELECT * FROM Complaints WHERE Student_ID = %s ORDER BY Complaint_ID DESC"
    return _fetch_data(query, (student_id,))

def resolve_complaint(complaint_id):
    query = "UPDATE Complaints SET Status = 'Resolved' WHERE Complaint_ID = %s"
    return execute_query(query, (complaint_id,))

def fetch_pending_requests():
    query = "SELECT * FROM Room_Requests WHERE Status = 'Pending' ORDER BY Request_ID ASC"
    return _fetch_data(query)

def fetch_all_students():
    query = "SELECT Student_ID, Name, Room_ID FROM Students"
    return _fetch_data(query)

def create_room_request(student_id, room_id):
    query = "INSERT INTO Room_Requests (Student_ID, Room_ID, Status) VALUES (%s, %s, 'Pending')"
    try:
        execute_query(query, (student_id, room_id))
        return True, "Request submitted successfully!"
    except Error as e:
        if e.args[0] == 1452:
            return False, "Student ID does not exist in the database."
        return False, str(e)

def resolve_request(request_id, action):
    req_query = "SELECT Student_ID, Room_ID FROM Room_Requests WHERE Request_ID = %s"
    req = _fetch_data(req_query, (request_id,), fetch_one=True)
    if not req:
        return False, "Request not found."

    if action == "Reject":
        success = execute_query("UPDATE Room_Requests SET Status = 'Rejected' WHERE Request_ID = %s", (request_id,))
        return success, "Rejected"
    elif action == "Approve":
        student_profile = fetch_student_profile(req['Student_ID'])
        if student_profile and student_profile.get('Room_ID') is not None:
            execute_query("UPDATE Room_Requests SET Status = 'Rejected' WHERE Request_ID = %s", (request_id,))
            return False, "Approval failed: Student already holds an active room assignment."
        if allocate_room(req['Student_ID'], req['Room_ID']):
            execute_query("UPDATE Room_Requests SET Status = 'Approved' WHERE Request_ID = %s", (request_id,))
            return True, "Approved"
        return False, "Allocation failed due to capacity."

def register_student(name, email, phone, password):
    query = "INSERT INTO Students (Name, Email, Phone, Password) VALUES (%s, %s, %s, %s)"
    connection = create_connection()
    if not connection:
        return False, "Database error"
    try:
        cursor = connection.cursor()
        cursor.execute(query, (name, email, phone, password))
        student_id = cursor.lastrowid
        connection.commit()
        return True, student_id
    except Error as e:
        if e.args[0] == 1062:
            return False, "Email already exists in the database."
        return False, str(e)
    finally:
        try:
            cursor.close()
            connection.close()
        except:
            pass

def authenticate_student(student_id, password):
    query = "SELECT Student_ID, Name FROM Students WHERE Student_ID = %s AND Password = %s"
    res = _fetch_data(query, (student_id, password), fetch_one=True)
    if res:
        return True, res['Name']
    return False, "Invalid Student ID or Password"

def fetch_student_profile(student_id):
    query = """
    SELECT s.Student_ID, s.Name, s.Email, s.Phone, r.Room_ID, r.Capacity, r.Price,
           (SELECT SUM(Amount) FROM Billing WHERE Student_ID = s.Student_ID AND Status = 'Not Paid') as Total_Due
    FROM Students s
    LEFT JOIN Rooms r ON s.Room_ID = r.Room_ID
    WHERE s.Student_ID = %s
    """
    return _fetch_data(query, (student_id,), fetch_one=True)

def update_student_profile(student_id, name, email, phone, password=None):
    if password and password.strip():
        query = "UPDATE Students SET Name=%s, Email=%s, Phone=%s, Password=%s WHERE Student_ID=%s"
        return execute_query(query, (name, email, phone, password, student_id))
    else:
        query = "UPDATE Students SET Name=%s, Email=%s, Phone=%s WHERE Student_ID=%s"
        return execute_query(query, (name, email, phone, student_id))

def authenticate_admin(admin_username, password):
    query = "SELECT Admin_ID, Username FROM Admin WHERE Username = %s AND Password = %s"
    res = _fetch_data(query, (admin_username, password), fetch_one=True)
    if res:
        return True, res['Username'], res['Admin_ID']
    return False, "Invalid Admin Credentials", None

def fetch_all_billing():
    query = "SELECT * FROM Billing"
    return _fetch_data(query)