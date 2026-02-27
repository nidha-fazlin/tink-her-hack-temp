from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app=Flask(__name__)
app.secret_key = 'change-this-secret'

#create database table
def init_db():
    conn = sqlite3.connect('database.db')
    c=conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS complaints(id INTEGER PRIMARY KEY AUTOINCREMENT,complaint_text TEXT NOT NULL,is_anonymous TEXT,name TEXT ,room_no TEXT,phone_no TEXT,status TEXT DEFAULT 'Pending')''')
    conn.commit()
    conn.close()

init_db()

#Home Page
@app.route('/')
def home():
    return render_template('index.html')

#complaint page 
@app.route('/complaint')
def complaint():
    return render_template('complaint.html')

#submit complaint 
@app.route('/submit', methods=['POST'])
def submit():
    text=request.form['complaint_text']

    #validate form 
    if text.strip() == "":
        return "Error:Complaint cannot be empty!"
    anonymous=request.form.get("anonymous")

    if anonymous:
        anonymous = "Yes"
        name = None
        room_no = None
        phone_no = None
    else:
        anonymous = "No"
        name = request.form['name']
        room_no = request.form['room_no']
        phone_no = request.form['phone_no']
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    #store complaint 
    c.execute("""INSERT INTO complaints (complaint_text, is_anonymous,name,room_no,phone_no)VALUES(?,?,?,?,?)""",(text,anonymous,name,room_no,phone_no))
    #generate ComplaintID
    complaint_id = c.lastrowid

    conn.commit()
    conn.close()
    #Show Succes Message with Card
    return render_template('success.html', complaint_id=complaint_id)

#Admin Page 
@app.route('/admin')
def admin():
    # require login
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM complaints")
    data = c.fetchall()
    conn.close()

    return render_template('admin.html', complaints=data)


@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    # Simple hardcoded admin credentials as requested
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'admin' and password == 'admin@123':
            session['admin_logged_in'] = True
            return redirect(url_for('admin'))
        else:
            return render_template('admin_login.html', error='Invalid credentials')
    return render_template('admin_login.html')


@app.route('/admin_logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

#Update complaint status
@app.route('/update_status/<int:complaint_id>/<new_status>', methods=['POST'])
def update_status(complaint_id, new_status):
    # Validate status
    valid_statuses = ['Pending', 'Verified', 'Resolved', 'In Progress']
    if new_status not in valid_statuses:
        return {'error': 'Invalid status'}, 400
    
    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        
        # Update the status in database
        c.execute("UPDATE complaints SET status = ? WHERE id = ?", (new_status, complaint_id))
        conn.commit()
        conn.close()
        
        return {'success': True, 'message': f'Status updated to {new_status}'}, 200
    except Exception as e:
        return {'error': str(e)}, 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)


