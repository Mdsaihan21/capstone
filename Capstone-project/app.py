import os
from flask import Flask, render_template, request, redirect
from flask_mysqldb import MySQL
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# MySQL Configuration
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)


# Create Tables
def create_tables():
    with app.app_context():
        cursor = mysql.connection.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS equipment (
            equipment_id INT AUTO_INCREMENT PRIMARY KEY,
            equipment_name VARCHAR(100) NOT NULL,
            serial_number VARCHAR(50) UNIQUE NOT NULL,
            department VARCHAR(100),
            purchase_date DATE,
            status VARCHAR(50)
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS maintenance (
            log_id INT AUTO_INCREMENT PRIMARY KEY,
            equipment_id INT NOT NULL,
            maintenance_date DATE,
            technician_name VARCHAR(100),
            issue_reported TEXT,
            resolution_notes TEXT,
            next_due_date DATE,
            FOREIGN KEY (equipment_id)
            REFERENCES equipment(equipment_id)
            ON DELETE CASCADE
        )
        """)

        mysql.connection.commit()
        cursor.close()


create_tables()


@app.route('/')
def index():

    cursor = mysql.connection.cursor()

    # Total Equipment
    cursor.execute("SELECT COUNT(*) AS total FROM equipment")
    total_equipment = cursor.fetchone()['total']

    # Active Equipment
    cursor.execute("""
        SELECT COUNT(*) AS active
        FROM equipment
        WHERE status='Active'
    """)
    active_equipment = cursor.fetchone()['active']

    # Maintenance Equipment
    # Total Maintenance Records
    cursor.execute("""
        SELECT COUNT(*) AS maintenance
        FROM equipment
        WHERE status='Under Maintenance'
    """)
    maintenance_count = cursor.fetchone()['maintenance']
    
   # Equipment List
    cursor.execute("""
        SELECT *
        FROM equipment
        ORDER BY equipment_id DESC
    """)
    equipments = cursor.fetchall()

    cursor.close()

    return render_template(
        'dashboard.html',
        equipments=equipments,
        total_equipment=total_equipment,
        active_equipment=active_equipment,
        maintenance_count=maintenance_count
    )

@app.route('/equipment/add', methods=['GET', 'POST'])
def add_equipment():

    if request.method == 'POST':

        equipment_name = request.form['equipment_name']
        serial_number = request.form['serial_number']
        department = request.form['department']
        purchase_date = request.form['purchase_date']
        status = request.form['status']

        cursor = mysql.connection.cursor()

        cursor.execute("""
            INSERT INTO equipment
            (equipment_name, serial_number, department, purchase_date, status)
            VALUES (%s,%s,%s,%s,%s)
        """,
        (
            equipment_name,
            serial_number,
            department,
            purchase_date,
            status
        ))

        mysql.connection.commit()
        cursor.close()

        return redirect('/')

    return render_template('add_equipment.html')


@app.route('/maintenance/<int:equipment_id>')
def maintenance(equipment_id):

    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT *
        FROM maintenance
        WHERE equipment_id=%s
        ORDER BY maintenance_date DESC
    """, (equipment_id,))

    records = cursor.fetchall()

    cursor.execute("""
        SELECT *
        FROM equipment
        WHERE equipment_id=%s
    """, (equipment_id,))

    equipment = cursor.fetchone()

    cursor.close()

    return render_template(
        'maintenance.html',
        records=records,
        equipment=equipment
    )


@app.route('/maintenance/add/<int:equipment_id>',
           methods=['GET', 'POST'])
def add_maintenance(equipment_id):

    if request.method == 'POST':

        maintenance_date = request.form['maintenance_date']
        technician_name = request.form['technician_name']
        issue_reported = request.form['issue_reported']
        resolution_notes = request.form['resolution_notes']
        next_due_date = request.form['next_due_date']

        cursor = mysql.connection.cursor()

        cursor.execute("""
            INSERT INTO maintenance
            (
                equipment_id,
                maintenance_date,
                technician_name,
                issue_reported,
                resolution_notes,
                next_due_date
            )
            VALUES (%s,%s,%s,%s,%s,%s)
        """,
        (
            equipment_id,
            maintenance_date,
            technician_name,
            issue_reported,
            resolution_notes,
            next_due_date
        ))

        mysql.connection.commit()
        cursor.close()

        return redirect(f'/maintenance/{equipment_id}')

    return render_template(
        'add_maintenance.html',
        equipment_id=equipment_id
    )


@app.route('/equipment/delete/<int:equipment_id>')
def delete_equipment(equipment_id):

    cursor = mysql.connection.cursor()

    cursor.execute("""
        DELETE FROM equipment
        WHERE equipment_id=%s
    """, (equipment_id,))

    mysql.connection.commit()
    cursor.close()

    return redirect('/')


@app.route('/health')
def health():
    return {
        "status": "UP"
    }


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
