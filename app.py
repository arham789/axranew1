from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd
import os
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Better way to set a secret key

# Initialize LoginManager
login_manager = LoginManager()
login_manager.init_app(app)

# Admin credentials
admin_username = 'Arham@786'
admin_password = 'Arjun@shazaib'

# Create an in-memory user object for admin
class User(UserMixin):
    pass

@login_manager.user_loader
def load_user(user_id):
    if user_id == admin_username:
        user = User()
        user.id = user_id
        return user
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/book_tuition', methods=['GET', 'POST'])
def book_tuition():
    if request.method == 'POST':
        name = request.form.get('name', '')
        mobile = request.form.get('mobile', '')
        class_name = request.form.get('class', '')
        address = request.form.get('address', '')
        school = request.form.get('school', '')

        save_submission('Book Tuition', name, mobile, address=address, school=school, class_name=class_name)
        flash('Tuition booking submitted successfully!')
        return redirect(url_for('thank_you'))
    
    return render_template('book_tuition.html')

@app.route('/join-tutor', methods=['GET', 'POST'])
def join_tutor():
    if request.method == 'POST':
        name = request.form.get('name', '')
        mobile = request.form.get('mobile', '')
        email = request.form.get('email', '')
        qualification = request.form.get('qualification', '')
        address = request.form.get('address', '')
        city = request.form.get('city', '')
        pin = request.form.get('pin', '')

        save_submission('Join Tutor', name, mobile, email=email, qualification=qualification, address=address, city=city, pin=pin)

        flash('Tutor application submitted successfully!')
        return redirect(url_for('thank_you'))
    
    return render_template('join_tutor.html')

# Path to the Excel file
EXCEL_FILE = 'submissions.xlsx'

def save_submission(category, name, mobile, email=None, qualification=None, address=None, city=None, pin=None, class_name=None, school=None):
    # Load existing submissions or create a new DataFrame
    if os.path.exists(EXCEL_FILE):
        df = pd.read_excel(EXCEL_FILE)
    else:
        df = pd.DataFrame(columns=['Category', 'Name', 'Mobile', 'Email', 'Qualification', 'Address', 'City', 'Pin', 'Class', 'School'])

    # Create a new submission as a DataFrame
    new_submission = pd.DataFrame([{
        'Category': category,
        'Name': name,
        'Mobile': mobile,
        'Email': email,
        'Qualification': qualification,
        'Address': address,
        'City': city,
        'Pin': pin,
        'Class': class_name,
        'School': school
    }])

    # Use pd.concat to add new submission to existing DataFrame
    df = pd.concat([df, new_submission], ignore_index=True) 

    # Save the updated DataFrame back to the Excel file
    df.to_excel(EXCEL_FILE, index=False)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == admin_username and password == admin_password:
            user = User()
            user.id = admin_username
            login_user(user)
            return redirect(url_for('admin_panel'))
        else:
            flash('Invalid login credentials', 'danger')

    return render_template('admin.html')

@app.route('/admin-panel')
@login_required
def admin_panel():
    if os.path.exists(EXCEL_FILE):
        submissions = pd.read_excel(EXCEL_FILE).to_dict(orient='records')
    else:
        submissions = []
    return render_template('admin_panel.html', submissions=submissions)

@app.route('/delete_entry/<int:index>', methods=['POST'])
def delete_entry(index):
    df = pd.read_excel(EXCEL_FILE)
    if 0 <= index < len(df):
        df.drop(index, inplace=True)
        df.reset_index(drop=True, inplace=True)  # Reset index after deletion
        df.to_excel(EXCEL_FILE, index=False)
        flash('Entry deleted successfully!')
    else:
        flash('Invalid entry index.')
    return redirect(url_for('admin_panel'))
    
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('admin'))

@app.route('/thank_you')
def thank_you():
    return render_template('thank_you.html')

if __name__ == '__main__':
    app.run(debug=True)
