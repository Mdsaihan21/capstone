import os
from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)


# MYSQL CONFIG

app.config['MYSQL_HOST'] = os.getenv("MYSQL_HOST")
app.config['MYSQL_USER'] = os.getenv("MYSQL_USER")
app.config['MYSQL_PASSWORD'] = os.getenv("MYSQL_PASSWORD")
app.config['MYSQL_DB'] = os.getenv("MYSQL_DB")
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'


mysql = MySQL(app)



# CREATE TABLES

def create_tables():

    cursor = mysql.connection.cursor()


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS equipment(

        equipment_id INT AUTO_INCREMENT PRIMARY KEY,

        equipment_name VARCHAR(100) NOT NULL,

        serial_number VARCHAR(50) UNIQUE NOT NULL,

        department VARCHAR(100),

        purchase_date DATE,

        status ENUM(
        'Active',
        'Under Maintenance',
        'Decommissioned'
        ) DEFAULT 'Active'

    )
    """)



    cursor.execute("""
    CREATE TABLE IF NOT EXISTS maintenance_log(

        log_id INT AUTO_INCREMENT PRIMARY KEY,

        equipment_id INT,

        maintenance_date DATE,

        technician_name VARCHAR(100),

        issue_reported TEXT,

        resolution_notes TEXT,

        next_due_date DATE,


        FOREIGN KEY(equipment_id)
        REFERENCES equipment(equipment_id)
        ON DELETE CASCADE

    )
    """)


    mysql.connection.commit()

    cursor.close()



with app.app_context():
    create_tables()



# HOME - SHOW EQUIPMENT


@app.route("/")
def index():

    cursor=mysql.connection.cursor()

    cursor.execute(
    "SELECT * FROM equipment ORDER BY equipment_id DESC"
    )

    equipments=cursor.fetchall()

    cursor.close()


    return render_template(
        "index.html",
        equipments=equipments
    )



# ADD EQUIPMENT


@app.route("/equipment/add",
methods=["GET","POST"])

def add_equipment():

    if request.method=="POST":

        name=request.form["equipment_name"]
        serial=request.form["serial_number"]
        dept=request.form["department"]
        date=request.form["purchase_date"]
        status=request.form["status"]


        cursor=mysql.connection.cursor()


        cursor.execute(
        """
        INSERT INTO equipment
        (
        equipment_name,
        serial_number,
        department,
        purchase_date,
        status
        )
        VALUES(%s,%s,%s,%s,%s)

        """,
        (name,serial,dept,date,status)
        )


        mysql.connection.commit()

        cursor.close()


        return redirect(url_for("index"))


    return render_template(
        "add_equipment.html"
    )




# EDIT EQUIPMENT


@app.route("/equipment/edit/<int:id>",
methods=["GET","POST"])

def edit_equipment(id):

    cursor=mysql.connection.cursor()


    if request.method=="POST":


        cursor.execute(
        """
        UPDATE equipment SET

        equipment_name=%s,
        serial_number=%s,
        department=%s,
        purchase_date=%s,
        status=%s

        WHERE equipment_id=%s

        """,
        (
        request.form["equipment_name"],
        request.form["serial_number"],
        request.form["department"],
        request.form["purchase_date"],
        request.form["status"],
        id
        )
        )


        mysql.connection.commit()

        cursor.close()

        return redirect(url_for("index"))



    cursor.execute(
    "SELECT * FROM equipment WHERE equipment_id=%s",
    (id,)
    )


    equipment=cursor.fetchone()

    cursor.close()


    return render_template(
        "edit_equipment.html",
        equipment=equipment
    )




# DELETE EQUIPMENT


@app.route("/equipment/delete/<int:id>")

def delete_equipment(id):

    cursor=mysql.connection.cursor()


    cursor.execute(
    "DELETE FROM equipment WHERE equipment_id=%s",
    (id,)
    )


    mysql.connection.commit()

    cursor.close()


    return redirect(url_for("index"))





# VIEW MAINTENANCE LOGS


@app.route("/maintenance/<int:id>")

def maintenance(id):

    cursor=mysql.connection.cursor()


    cursor.execute(
    """
    SELECT *
    FROM maintenance_log
    WHERE equipment_id=%s
    ORDER BY log_id DESC
    """,
    (id,)
    )


    logs=cursor.fetchall()


    cursor.close()


    return render_template(
        "maintenance.html",
        logs=logs,
        equipment_id=id
    )





# ADD MAINTENANCE


@app.route("/maintenance/add/<int:id>",
methods=["GET","POST"])

def add_maintenance(id):


    if request.method=="POST":


        cursor=mysql.connection.cursor()


        cursor.execute(
        """
        INSERT INTO maintenance_log

        (
        equipment_id,
        maintenance_date,
        technician_name,
        issue_reported,
        resolution_notes,
        next_due_date
        )

        VALUES(%s,%s,%s,%s,%s,%s)

        """,
        (
        id,
        request.form["maintenance_date"],
        request.form["technician_name"],
        request.form["issue_reported"],
        request.form["resolution_notes"],
        request.form["next_due_date"]
        )
        )


        mysql.connection.commit()

        cursor.close()


        return redirect(
        url_for(
        "maintenance",
        id=id
        )
        )


    return render_template(
        "add_maintenance.html",
        equipment_id=id
    )




@app.route("/health")

def health():

    return {
    "status":"UP",
    "database":"CONNECTED"
    }




if __name__=="__main__":

    app.run(
    host="0.0.0.0",
    port=5000,
    debug=True
    )