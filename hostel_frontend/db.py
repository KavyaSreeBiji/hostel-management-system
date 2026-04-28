import pymysql
import pymysql.cursors
pymysql.install_as_MySQLdb()
import MySQLdb as mysql_connector
from MySQLdb import Error
import os

# Reads from environment variables (Streamlit Cloud) or falls back to Railway public URL for local dev
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
    """
    Helper function to execute general SQL tasks like INSERT, UPDATE, DELETE.
    """
    connection = create_connection()
    if not connection:
        return False
        
    try:
        cursor = connection.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        connection.commit()
        return True
    except Error as e:
        print(f"Error executing query: {e}")
        return False
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def reset_database():
    """
    Completely obliterates and resyncs the active hostel database natively against init.sql parameters.
    """
    try:
        conn = mysql.connector.connect(host="localhost", user="root", password="Leena!123")
        cursor = conn.cursor()
        with open("hostel_database/init.sql", "r") as file:
            sql_script = file.read()
        for command in sql_script.split(';'):
            if command.strip():
                cursor.execute(command)
        conn.commit()
        return True
    except Error as e:
        print(f"Critical Reset Error: {e}")
        return False
    finally:
        if 'cursor' in locals() and cursor: cursor.close()
        if 'conn' in locals() and conn.is_connected(): conn.close()

def _fetch_data(query, params=None, fetch_one=False):
    """
    Internal helper function for executing SELECT queries and fetching data.
    Returns dictionaries so the frontend can easily access fields by name.
    """
    connection = create_connection()
    if not connection:
        return None
        
    try:
        # Using dictionary=True returns rows as dicts instead of tuples
        cursor = connection.cursor(dictionary=True) 
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
            
        if fetch_one:
            result = cursor.fetchone()
        else:
            result = cursor.fetchall()
        return result
    except Error as e:
        print(f"Error executing fetch query: {e}")
        return None
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def fetch_student_profile(student_id):
    """
    Fetches the profile of a specific student by ID, including their room details.
    """
    query = """
        SELECT s.Student_ID, s.Name, s.Email, s.Phone, r.Room_ID, r.Capacity, r.Availability_Status
        FROM Students s
        LEFT JOIN Rooms r ON s.Room_ID = r.Room_ID
        WHERE s.Student_ID = %s
    """
    return _fetch_data(query, (student_id,), fetch_one=True)

def check_room_availability():
    """
    Fetches a list of all rooms currently available.
    """
    query = "SELECT * FROM Rooms WHERE Availability_Status = 'Available'"
    return _fetch_data(query)

def fetch_all_rooms():
    """
    Fetches all rooms for the admin dashboard.
    """
    query = "SELECT * FROM Rooms"
    return _fetch_data(query)

def add_room(capacity, price):
    """
    Adds a new empty room with the specified capacity and price.
    """
    query = "INSERT INTO Rooms (Capacity, Occupancy, Availability_Status, Price) VALUES (%s, 0, 'Available', %s)"
    return execute_query(query, (capacity, price))

def get_billing_by_student(student_id):
    """
    Fetches all billing records for a specific student.
    """
    query = "SELECT * FROM Billing WHERE Student_ID = %s ORDER BY Due_Date DESC"
    return _fetch_data(query, (student_id,))

def allocate_room(student_id, room_id):
    """
    Updates the Students table with the assigned room and increments Occupancy in Rooms.
    """
    connection = create_connection()
    if not connection:
        return False
        
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Start transaction to ensure both updates succeed or fail together
        connection.start_transaction()
        
        # Update student record
        query_student = "UPDATE Students SET Room_ID = %s WHERE Student_ID = %s"
        cursor.execute(query_student, (room_id, student_id))
        
        # Increment room occupancy and automatically flip status to 'Full' if capacity is met
        query_room = "UPDATE Rooms SET Occupancy = Occupancy + 1, Availability_Status = IF(Occupancy >= Capacity, 'Full', 'Available') WHERE Room_ID = %s"
        cursor.execute(query_room, (room_id,))
        
        # Automate Billing Generation
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
        # Roll back changes in case of error
        connection.rollback()
        return False
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def remove_student_from_room(student_id, room_id):
    """
    Removes a student's room assignment and safely decrements the room's occupancy.
    """
    connection = create_connection()
    if not connection: return False
    try:
        connection.start_transaction()
        cursor = connection.cursor()
        
        # Nullify student room
        cursor.execute("UPDATE Students SET Room_ID = NULL WHERE Student_ID = %s", (student_id,))
        
        # Decrement room occupancy and open status
        query_room = "UPDATE Rooms SET Occupancy = GREATEST(0, Occupancy - 1), Availability_Status = 'Available' WHERE Room_ID = %s"
        cursor.execute(query_room, (room_id,))
        
        connection.commit()
        return True
    except Error as e:
        connection.rollback()
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def process_payment(bill_id):
    """
    Updates the Status in the Billing table to 'Paid'.
    """
    query = "UPDATE Billing SET Status = 'Paid' WHERE Bill_ID = %s"
    return execute_query(query, (bill_id,))

def submit_complaint(student_id, category, description):
    """
    Handles student service requests by inserting a new record into a Complaints table.
    """
    query = "INSERT INTO Complaints (Student_ID, Category, Description, Status) VALUES (%s, %s, %s, 'Pending')"
    return execute_query(query, (student_id, category, description))

def fetch_all_complaints():
    """
    Fetches all complaints with student details.
    """
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
    """
    Fetches all pending room requests in strictly chronological order.
    """
    query = "SELECT * FROM Room_Requests WHERE Status = 'Pending' ORDER BY Request_ID ASC"
    return _fetch_data(query)

def fetch_all_students():
    """
    Fetches all students from the database.
    """
    query = "SELECT Student_ID, Name, Room_ID FROM Students"
    return _fetch_data(query)

def create_room_request(student_id, room_id):
    """
    Creates a new room request in the database without upfront restrictions.
    """
    query = "INSERT INTO Room_Requests (Student_ID, Room_ID, Status) VALUES (%s, %s, 'Pending')"
    try:
        execute_query(query, (student_id, room_id))
        return True, "Request submitted successfully!"
    except Error as e:
        if e.errno == 1452:
            return False, "Student ID does not exist in the database."
        return False, str(e)


def resolve_request(request_id, action):
    """
    Approves or rejects a room request subject to Admin-side verification.
    """
    # Fetch details
    req_query = "SELECT Student_ID, Room_ID FROM Room_Requests WHERE Request_ID = %s"
    req = _fetch_data(req_query, (request_id,), fetch_one=True)
    if not req: return False, "Request not found."
    
    if action == "Reject":
        success = execute_query("UPDATE Room_Requests SET Status = 'Rejected' WHERE Request_ID = %s", (request_id,))
        return success, "Rejected"
    elif action == "Approve":
        # Check if student already has a room!
        student_profile = fetch_student_profile(req['Student_ID'])
        if student_profile and student_profile.get('Room_ID') is not None:
            # Manually reject the query to clear it out since they have a room
            execute_query("UPDATE Room_Requests SET Status = 'Rejected' WHERE Request_ID = %s", (request_id,))
            return False, "Approval failed: Student already holds an active room assignment."
            
        # Execute allocation
        if allocate_room(req['Student_ID'], req['Room_ID']):
            execute_query("UPDATE Room_Requests SET Status = 'Approved' WHERE Request_ID = %s", (request_id,))
            return True, "Approved"
        return False, "Allocation failed due to capacity."

def register_student(name, email, phone, password):
    """
    Registers a new student into the database and returns their auto-generated Student_ID.
    """
    query = "INSERT INTO Students (Name, Email, Phone, Password) VALUES (%s, %s, %s, %s)"
    connection = create_connection()
    if not connection: return False, "Database error"
    try:
        cursor = connection.cursor()
        cursor.execute(query, (name, email, phone, password))
        student_id = cursor.lastrowid
        connection.commit()
        return True, student_id
    except Error as e:
        if e.errno == 1062: # MySQL error code for Duplicate entry
            return False, "Email already exists in the database."
        return False, str(e)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def authenticate_student(student_id, password):
    """
    Validates a student login attempt against the live database rows.
    """
    query = "SELECT Student_ID, Name FROM Students WHERE Student_ID = %s AND Password = %s"
    res = _fetch_data(query, (student_id, password), fetch_one=True)
    if res:
        return True, res['Name']
    return False, "Invalid Student ID or Password"

def fetch_student_profile(student_id):
    """
    Fetches comprehensive student details including room assignments and billing totals.
    """
    query = """
    SELECT s.Student_ID, s.Name, s.Email, s.Phone, r.Room_ID, r.Capacity, r.Price,
           (SELECT SUM(Amount) FROM Billing WHERE Student_ID = s.Student_ID AND Status = 'Not Paid') as Total_Due
    FROM Students s
    LEFT JOIN Rooms r ON s.Room_ID = r.Room_ID
    WHERE s.Student_ID = %s
    """
    return _fetch_data(query, (student_id,), fetch_one=True)

def update_student_profile(student_id, name, email, phone, password=None):
    """
    Updates student demographic and authentication records.
    """
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
