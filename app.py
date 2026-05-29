from flask import Flask, render_template, request, redirect, jsonify
import config

app = Flask(__name__)

# =========================================================
# LOGIN
# =========================================================

@app.route("/")
def home():
    config.reconnect_db()
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():
    config.reconnect_db()

    username = request.form["username"]
    password = request.form["password"]

    query = """
    SELECT *
    FROM users
    WHERE username=%s AND password=%s
    """

    config.cursor.execute(query, (username, password))
    user = config.cursor.fetchone()

    if user:
        if user["role"] == "admin":
            return redirect("/admin")
        elif user["role"] == "supervisor":
            return redirect("/supervisor_dashboard")

    return "Invalid Login"


# =========================================================
# PAGE ROUTES
# =========================================================

@app.route("/admin")
def admin():
    config.reconnect_db()
    return render_template("admin_dashboard.html")


@app.route("/supervisor_dashboard")
def supervisor_dashboard():
    config.reconnect_db()
    return render_template("supervisor_dashboard.html")


@app.route("/allocation")
def allocation():
    config.reconnect_db()
    return render_template("allocation.html")


@app.route("/attendance")
def attendance():
    config.reconnect_db()

    query = """
    SELECT *
    FROM employee
    ORDER BY emp_id
    """

    config.cursor.execute(query)
    employees = config.cursor.fetchall()

    return render_template(
        "attendance.html",
        employees=employees
    )


# =========================================================
# OPERATOR APIs
# =========================================================

@app.route("/api/get_operators")
def get_operators():
    config.reconnect_db()

    query = """
    SELECT *
    FROM employee
    ORDER BY emp_id
    """

    config.cursor.execute(query)
    rows = config.cursor.fetchall()

    return jsonify(rows)


@app.route("/api/add_operator", methods=["POST"])
def add_operator():
    config.reconnect_db()
    data = request.json or {}

    query = """
    INSERT INTO employee(
        emp_id,
        emp_name,
        skill_level,
        shift_name,
        operator_type,
        joining_date,
        mobile,
        status
    )
    VALUES(%s,%s,%s,%s,%s,%s,%s,'Active')
    """

    config.cursor.execute(
        query,
        (
            data.get("emp_id"),
            data.get("emp_name"),
            data.get("skill_level", ""),
            data.get("shift_name", ""),
            data.get("operator_type", ""),
            data.get("joining_date") or None,
            data.get("mobile", "")
        )
    )

    config.db.commit()

    return jsonify({
        "message": "Operator Added Successfully"
    })


@app.route("/api/delete_operator/<emp_id>", methods=["DELETE"])
def delete_operator(emp_id):
    config.reconnect_db()

    query = """
    DELETE FROM employee
    WHERE emp_id=%s
    """

    config.cursor.execute(query, (emp_id,))
    config.db.commit()

    return jsonify({
        "message": "Operator Deleted"
    })


# =========================================================
# MACHINE APIs
# =========================================================

@app.route("/api/get_machines")
def get_machines():
    config.reconnect_db()

    query = """
    SELECT
        md.id,
        p.machine_name,
        p.part_number,
        md.shop_name,
        md.station_name,
        md.required_manpower,
        md.skill_required
    FROM master_data md
    JOIN products p
    ON md.product_id = p.product_id
    ORDER BY md.id DESC
    """

    config.cursor.execute(query)
    rows = config.cursor.fetchall()

    return jsonify(rows)


@app.route("/api/add_machine", methods=["POST"])
def add_machine():
    config.reconnect_db()
    data = request.json or {}

    machine_name = data.get("machine_name")
    part_number = data.get("part_number")
    shop_name = data.get("shop_name")
    station_name = data.get("station_name")
    required_manpower = data.get("required_manpower")
    skill_required = data.get("skill_required", "L1")

    query = """
    SELECT *
    FROM products
    WHERE machine_name=%s
    AND part_number=%s
    """

    config.cursor.execute(query, (machine_name, part_number))
    product = config.cursor.fetchone()

    if product:
        product_id = product["product_id"]
    else:
        insert_product = """
        INSERT INTO products(
            machine_name,
            part_number
        )
        VALUES(%s,%s)
        """

        config.cursor.execute(
            insert_product,
            (machine_name, part_number)
        )

        config.db.commit()
        product_id = config.cursor.lastrowid

    insert_master = """
    INSERT INTO master_data(
        product_id,
        shop_name,
        station_name,
        required_manpower,
        skill_required
    )
    VALUES(%s,%s,%s,%s,%s)
    """

    config.cursor.execute(
        insert_master,
        (
            product_id,
            shop_name,
            station_name,
            required_manpower,
            skill_required
        )
    )

    config.db.commit()

    return jsonify({
        "message": "Machine Added Successfully"
    })


@app.route("/api/delete_machine/<id>", methods=["DELETE"])
def delete_machine(id):
    config.reconnect_db()

    query = """
    DELETE FROM master_data
    WHERE id=%s
    """

    config.cursor.execute(query, (id,))
    config.db.commit()

    return jsonify({
        "message": "Machine Deleted"
    })


# =========================================================
# ATTENDANCE APIs
# =========================================================

@app.route("/api/save_attendance", methods=["POST"])
def save_attendance():
    config.reconnect_db()
    data = request.json

    delete_query = """
    DELETE FROM attendance
    WHERE date = CURDATE()
    """

    config.cursor.execute(delete_query)

    for row in data:
        insert_query = """
        INSERT INTO attendance(
            emp_id,
            date,
            status
        )
        VALUES(%s,CURDATE(),%s)
        """

        config.cursor.execute(
            insert_query,
            (
                row["emp_id"],
                row["status"]
            )
        )

    config.db.commit()

    return jsonify({
        "message": "Attendance Saved Successfully"
    })


@app.route("/api/get_available_operators")
def get_available_operators():
    config.reconnect_db()

    query = """
    SELECT
        e.emp_id,
        e.emp_name,
        e.skill_level
    FROM employee e
    JOIN attendance a
    ON e.emp_id = a.emp_id
    WHERE a.status='Present'
    AND a.date = CURDATE()
    """

    config.cursor.execute(query)
    rows = config.cursor.fetchall()

    return jsonify(rows)


# =========================================================
# MASTER DATA FOR ALLOCATION
# =========================================================

@app.route("/api/get_master_data")
def get_master_data():
    config.reconnect_db()

    query = """
    SELECT
        md.id,
        p.machine_name,
        p.part_number,
        md.shop_name,
        md.station_name,
        md.required_manpower
    FROM master_data md
    JOIN products p
    ON md.product_id = p.product_id
    ORDER BY p.machine_name
    """

    config.cursor.execute(query)
    rows = config.cursor.fetchall()

    structured = {}

    for r in rows:
        machine = r["machine_name"]
        part_number = r["part_number"]
        station = r["shop_name"] + " - " + r["station_name"]

        if machine not in structured:
            structured[machine] = {}

        if part_number not in structured[machine]:
            structured[machine][part_number] = {}

        structured[machine][part_number][station] = {
            "required_manpower": r["required_manpower"],
            "master_data_id": r["id"]
        }

    return jsonify(structured)


# =========================================================
# SAVE ALLOCATION
# =========================================================

@app.route("/api/save_allocation", methods=["POST"])
def save_allocation():
    config.reconnect_db()
    data = request.json

    for row in data:
        check_query = """
        SELECT *
        FROM allocation
        WHERE emp_id=%s
        AND master_data_id=%s
        AND allocation_date=CURDATE()
        """

        config.cursor.execute(
            check_query,
            (
                row["emp_id"],
                row["master_data_id"]
            )
        )

        exists = config.cursor.fetchone()

        if not exists:
            insert_query = """
            INSERT INTO allocation(
                emp_id,
                master_data_id,
                allocation_date
            )
            VALUES(%s,%s,CURDATE())
            """

            config.cursor.execute(
                insert_query,
                (
                    row["emp_id"],
                    row["master_data_id"]
                )
            )

    config.db.commit()

    return jsonify({
        "message": "Allocation Saved Successfully"
    })


# =========================================================
# GET TODAY ALLOCATION
# =========================================================

@app.route("/api/get_today_allocations")
def get_today_allocations():
    config.reconnect_db()

    query = """
    SELECT
        a.allocation_id,
        e.emp_name,
        e.emp_id,
        p.machine_name,
        p.part_number,
        md.shop_name,
        md.station_name
    FROM allocation a
    JOIN employee e
    ON a.emp_id = e.emp_id
    JOIN master_data md
    ON a.master_data_id = md.id
    JOIN products p
    ON md.product_id = p.product_id
    WHERE a.allocation_date = CURDATE()
    ORDER BY p.machine_name
    """

    config.cursor.execute(query)
    rows = config.cursor.fetchall()

    return jsonify(rows)


# =========================================================
# GET SAVED ALLOCATIONS BY MASTER ID
# =========================================================

@app.route("/api/get_allocations_by_master/<master_id>")
def get_allocations_by_master(master_id):
    config.reconnect_db()

    query = """
    SELECT
        a.allocation_id,
        e.emp_id,
        e.emp_name
    FROM allocation a
    JOIN employee e
    ON a.emp_id = e.emp_id
    WHERE a.master_data_id=%s
    AND a.allocation_date = CURDATE()
    """

    config.cursor.execute(query, (master_id,))
    rows = config.cursor.fetchall()

    return jsonify(rows)


# =========================================================
# DELETE ALLOCATION
# =========================================================

@app.route("/api/delete_allocation/<allocation_id>", methods=["DELETE"])
def delete_allocation(allocation_id):
    config.reconnect_db()

    query = """
    DELETE FROM allocation
    WHERE allocation_id=%s
    """

    config.cursor.execute(query, (allocation_id,))
    config.db.commit()

    return jsonify({
        "message": "Allocation Deleted"
    })


# =========================================================
# DASHBOARD DATA API
# =========================================================

@app.route("/api/dashboard_data")
def dashboard_data():
    config.reconnect_db()

    config.cursor.execute("""
    SELECT COUNT(*) AS total
    FROM master_data
    """)
    total_stations = config.cursor.fetchone()["total"]

    config.cursor.execute("""
    SELECT IFNULL(SUM(required_manpower),0) AS total
    FROM master_data
    """)
    operators_required = config.cursor.fetchone()["total"]

    config.cursor.execute("""
    SELECT COUNT(*) AS total
    FROM attendance
    WHERE status='Present'
    AND date = CURDATE()
    """)
    operators_available = config.cursor.fetchone()["total"]

    config.cursor.execute("""
    SELECT setting_value
    FROM settings
    WHERE setting_name='buffer_required'
    """)
    buffer_row = config.cursor.fetchone()

    if buffer_row:
        buffer_required = int(buffer_row["setting_value"])
    else:
        buffer_required = 0

    buffer_available = operators_available - operators_required
    if buffer_available < 0:
        buffer_available = 0

    config.cursor.execute("""
    SELECT
        skill_level,
        COUNT(*) AS required
    FROM employee
    GROUP BY skill_level
    """)
    required_data = config.cursor.fetchall()

    skills = []
    for row in required_data:
        skill = row["skill_level"]
        required = row["required"]

        config.cursor.execute("""
        SELECT COUNT(*) AS available
        FROM employee e
        JOIN attendance a
        ON e.emp_id = a.emp_id
        WHERE e.skill_level=%s
        AND a.status='Present'
        AND a.date = CURDATE()
        """, (skill,))

        available = config.cursor.fetchone()["available"]

        skills.append({
            "skill": skill,
            "required": required,
            "available": available
        })

    return jsonify({
        "total_stations": total_stations,
        "operators_required": operators_required,
        "operators_available": operators_available,
        "buffer_required": buffer_required,
        "buffer_available": buffer_available,
        "skills": skills
    })


# =========================================================
# SAVE SETTINGS
# =========================================================

@app.route("/api/save_settings", methods=["POST"])
def save_settings():
    config.reconnect_db()
    data = request.json

    queries = [
        ("total_stations", data["total_stations"]),
        ("buffer_required", data["buffer_required"])
    ]

    for name, value in queries:
        config.cursor.execute("""
        SELECT *
        FROM settings
        WHERE setting_name=%s
        """, (name,))
        exists = config.cursor.fetchone()

        if exists:
            config.cursor.execute("""
            UPDATE settings
            SET setting_value=%s
            WHERE setting_name=%s
            """, (value, name))
        else:
            config.cursor.execute("""
            INSERT INTO settings(
                setting_name,
                setting_value
            )
            VALUES(%s,%s)
            """, (name, value))

    config.db.commit()

    return jsonify({
        "message": "Settings Saved Successfully"
    })


# =========================================================
# GET SETTINGS
# =========================================================

@app.route("/api/get_settings")
def get_settings():
    config.reconnect_db()

    config.cursor.execute("""
    SELECT *
    FROM settings
    """)
    rows = config.cursor.fetchall()

    settings = {}
    for row in rows:
        settings[row["setting_name"]] = row["setting_value"]

    return jsonify(settings)


# =========================================================
# GRAPH DATA API
# =========================================================

@app.route("/graph-data")
def graph_data():
    config.reconnect_db()
    chart = request.args.get("chart")

    labels = []
    values = []

    for i in range(6, -1, -1):
        config.cursor.execute("""
        SELECT DATE_FORMAT(
            DATE_SUB(CURDATE(), INTERVAL %s DAY),
            '%%d-%%m'
        ) AS label
        """, (i,))
        day = config.cursor.fetchone()["label"]
        labels.append(day)

        if chart == "manpowerChart":
            config.cursor.execute("""
            SELECT COUNT(*) AS total
            FROM attendance
            WHERE status='Present'
            AND date = DATE_SUB(CURDATE(), INTERVAL %s DAY)
            """, (i,))
            total = config.cursor.fetchone()["total"]
            values.append(total)

        elif chart == "absenteeChart":
            config.cursor.execute("""
            SELECT COUNT(*) AS total
            FROM attendance
            WHERE status='Absent'
            AND date = DATE_SUB(CURDATE(), INTERVAL %s DAY)
            """, (i,))
            total = config.cursor.fetchone()["total"]
            values.append(total)

        elif chart == "bufferChart":
            config.cursor.execute("""
            SELECT COUNT(*) AS total
            FROM attendance
            WHERE status='Present'
            AND date = DATE_SUB(CURDATE(), INTERVAL %s DAY)
            """, (i,))
            available = config.cursor.fetchone()["total"]

            config.cursor.execute("""
            SELECT IFNULL(SUM(required_manpower),0) AS total
            FROM master_data
            """)
            required = config.cursor.fetchone()["total"]

            buffer = available - required
            if buffer < 0:
                buffer = 0
            values.append(buffer)

        elif chart == "attritionChart":
            config.cursor.execute("""
            SELECT COUNT(*) AS total
            FROM employee
            WHERE status='Inactive'
            """)
            total = config.cursor.fetchone()["total"]
            values.append(total)

    return jsonify({
        "labels": labels,
        "values": values
    })


# =========================================================
# DATABASE CONNECTION CLEANUP
# =========================================================

@app.teardown_appcontext
def shutdown_session(exception=None):
    try:
        config.close_request_connection()
    except Exception as e:
        app.logger.error(f"Error releasing pool connection during teardown: {e}")


# =========================================================
# GET ALLOCATIONS BY SPECIFIC DATE
# =========================================================

@app.route("/api/get_allocations_by_date")
def get_allocations_by_date():
    config.reconnect_db()
    target_date = request.args.get("date")
    
    if not target_date:
        return jsonify([])

    query = """
    SELECT
        a.allocation_id,
        e.emp_name,
        e.emp_id,
        p.machine_name,
        p.part_number,
        md.shop_name,
        md.station_name,
        a.allocation_date
    FROM allocation a
    JOIN employee e ON a.emp_id = e.emp_id
    JOIN master_data md ON a.master_data_id = md.id
    JOIN products p ON md.product_id = p.product_id
    WHERE a.allocation_date LIKE %s
    ORDER BY p.machine_name
    """
    
    config.cursor.execute(query, (f"%{target_date}%",))
    rows = config.cursor.fetchall()

    return jsonify(rows)


# =====================================================================
# BUFFER ALLOCATION ROUTES (MODERN COMPLIANT SYNTAX)
# =====================================================================

@app.route('/api/get_buffer_allocations', methods=['GET'])
def get_buffer_allocations():
    try:
        config.reconnect_db()
        
        query = """
            SELECT ba.buffer_index, ba.emp_id, e.emp_name 
            FROM buffer_allocations ba
            JOIN employee e ON ba.emp_id = e.emp_id
        """
        config.cursor.execute(query)
        rows = config.cursor.fetchall()

        results = []
        for r in rows:
            if isinstance(r, dict):
                results.append({
                    "buffer_index": r["buffer_index"],
                    "emp_id": r["emp_id"],
                    "emp_name": r["emp_name"]
                })
            else:
                results.append({
                    "buffer_index": r[0],
                    "emp_id": r[1],
                    "emp_name": r[2]
                })
        
        return jsonify(results), 200
    except Exception as e:
        print(f"Fetch Error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/save_buffer_allocations', methods=['POST'])
def save_buffer_allocations():
    try:
        config.reconnect_db()
        allocations = request.get_json() or []
        
        if not allocations:
            return jsonify({"error": "No data received"}), 400

        emp_ids = [item.get('emp_id') for item in allocations if item.get('emp_id')]
        if len(emp_ids) != len(set(emp_ids)):
            return jsonify({"error": "Validation failed: Same operator cannot be allocated to multiple buffers!"}), 400

        for item in allocations:
            query = """
                INSERT INTO buffer_allocations (emp_id, buffer_index, station_name)
                VALUES (%s, %s, %s)
                AS new_data 
                ON DUPLICATE KEY UPDATE 
                    buffer_index = new_data.buffer_index,
                    station_name = new_data.station_name
            """
            config.cursor.execute(query, (item['emp_id'], item['buffer_index'], item['station_name']))

        config.db.commit()
        return jsonify({"message": "Buffer configurations saved securely!"}), 200
    except Exception as e:
        print(f"Save Error: {str(e)}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)