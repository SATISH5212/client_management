from flask import Flask, request, render_template, redirect, url_for
import mysql.connector
import qrcode
import os

app = Flask(__name__)

# Configure MySQL connection
db_config = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', '123456'),  # Update with your MySQL password
    'database': os.getenv('MYSQL_DB', 'client_management')
}

# Create directories for storing photos and QR codes if they don't exist
if not os.path.exists('static/photos'):
    os.makedirs('static/photos')
if not os.path.exists('static/qr_codes'):
    os.makedirs('static/qr_codes')

@app.route('/')
def index():
    return redirect(url_for('add_client'))

@app.route('/add_client', methods=['GET', 'POST'])
def add_client():
    if request.method == 'POST':
        # Fetch client details from form
        name = request.form['name']
        age = request.form['age']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        meeting_city = request.form['meeting_city']
        venue = request.form['venue']
        date = request.form['date']
        payment = request.form['payment']
        topic = request.form['topic']
        checkin = request.form['checkin']
        checkout = request.form['checkout']
        food = request.form['food']
        photo = request.files['photo']

        # Save photo file
        photo_path = os.path.join('static/photos', photo.filename)
        photo.save(photo_path)

        # Generate QR code
        qr_code_path = generate_qr_code(email)

        # Save client details to database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO clients (name, age, email, phone, address, meeting_city, venue, date, payment, topic, checkin, checkout, food, photo_path, qr_code_path)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (name, age, email, phone, address, meeting_city, venue, date, payment, topic, checkin, checkout, food, photo_path, qr_code_path))
        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for('client_details', email=email))
    
    return render_template('add_client.html')

@app.route('/client_details/<email>', methods=['GET'])
def client_details(email):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clients WHERE email = %s", (email,))
    client = cursor.fetchone()
    cursor.close()
    conn.close()

    if client:
        client_data = {
            'name': client[1],
            'age': client[2],
            'email': client[3],
            'phone': client[4],
            'address': client[5],
            'meeting_city': client[6],
            'venue': client[7],
            'date': client[8],
            'payment': client[9],
            'topic': client[10],
            'checkin': client[11],
            'checkout': client[12],
            'food': client[13],
            'photo_path': client[14],
            'qr_code_path': client[15]
        }
    else:
        client_data = None

    return render_template('client_details.html', client=client_data)

def generate_qr_code(email):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url_for('client_details', email=email, _external=True))
    qr.make(fit=True)
    qr_code_path = os.path.join('static/qr_codes', f"{email}.png")
    qr.make_image(fill='black', back_color='white').save(qr_code_path)
    return qr_code_path

if __name__ == '__main__':
    app.run(debug=True)
