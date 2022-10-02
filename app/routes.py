from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm, RPForm, BookForm
from app.models import User,  Book, Request, Borrowed



@app.route('/user/manage', methods=['GET', 'POST'])
@login_required
def manage_users():
    if current_user.is_authenticated and current_user.isAdmin !=True:
        return redirect(url_for('index'))
    users = User.query.all()
    return render_template('manage_user.html', users=users)

@app.route('/user/resetpassword/<int:id>')
@login_required
def reset_password(id):
    if current_user.is_authenticated and current_user.isAdmin !=True:
        return redirect(url_for('index'))
    user = User.query.get(id)
    user.set_password("default")
    db.session.add(user)
    db.session.commit()
    flash("Password has been reset.")
    return redirect(url_for('manage_users'))

@app.route('/user/delete/<int:id>')
@login_required
def delete_user(id):
    if current_user.is_authenticated and current_user.isAdmin !=True:
        return redirect(url_for('user_dashboard'))
    user = User.query.get(id)
    db.session.delete(user)
    db.session.commit()
    flash("User deleted.!")
    return redirect(url_for('manage_users'))



@app.route('/',  methods=['GET', 'POST'])
@app.route('/login/', methods=['GET', 'POST'])
def user_login():
    if current_user.is_authenticated:
        return redirect(url_for('user_dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('user_login'))
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('user_dashboard')
        return redirect(next_page)
    return render_template('login.html', form=form)

    
@app.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect(url_for('user_login'))


@app.route('/user/add', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated and current_user.isAdmin !=True:
        return redirect(url_for('user_login'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('New User Added')
        return redirect(url_for('register'))
    return render_template('register.html', form=form)


@app.route('/book/dashboard', methods=['GET', 'POST'])
def manage_book():
    if current_user.is_authenticated and current_user.isAdmin !=True:
        return redirect(url_for('user_dashboard'))
    books = Book.query.all()
    books_ordered = Book.query.order_by(Book.title).all()
    return render_template('manage_book.html', books_ordered=books_ordered)


@app.route('/book/add', methods=['GET', 'POST'])
@login_required
def add_book():
    if current_user.is_authenticated and current_user.isAdmin !=True:
        return redirect(url_for('user_dashboard'))
    form = BookForm()
    if form.validate_on_submit():
        book = Book(title=form.title.data, author=form.author.data, qty = form.qty.data, img=form.image.data)
        db.session.add(book)
        db.session.commit()
        flash('Book added successfully')
        return redirect(url_for('add_book'))
    return render_template('add_book.html', form=form)

@app.route('/book/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_book(id):
    if current_user.is_authenticated and current_user.isAdmin !=True:
        return redirect(url_for('user_dashboard'))
    form = BookForm()
    book = Book.query.get(id)
    if form.validate_on_submit():
        try:
            book.title = form.title.data
            book.author = form.author.data
            book.qty = form.qty.data
            book.img = form.image.data
            db.session.add(book)
            db.session.commit()
            flash('Book Edited successfully')
            return redirect(url_for('edit_book', id=id))
        except:
            flash('Something went wrong')
            return redirect(url_for('edit_book', id=id))
    return render_template('edit_book.html', form=form, book=book)

@app.route('/book/delete/<int:id>')
@login_required
def delete_book(id):
    if current_user.is_authenticated and current_user.isAdmin !=True:
        return redirect(url_for('user_dashboard'))
    user = Book.query.get(id)
    db.session.delete(user)
    db.session.commit()
    flash("Book deleted.!")
    return redirect(url_for('manage_book'))

@app.route('/rb/manage', methods=['GET', 'POST'])
@login_required
def rb_dashboard():
    if current_user.is_authenticated and  current_user.isAdmin == False :
        return redirect(url_for('user_dashboard'))
    request = Request.query.all()
    borrows = Borrowed.query.order_by(Borrowed.date).all()
    request_ordered = Request.query.order_by(Request.book_name).all()
    return render_template('manage_request_and_borrows.html', requests=request_ordered, borrows=borrows,  id=current_user.id, username=current_user.username)

@app.route('/rb/approverequest/<int:id>')
@login_required
def approve_request(id):
        if current_user.is_authenticated and current_user.isAdmin == False:
            return redirect(url_for('user_dashboard'))
        request = Request.query.get(id)
        request.status = "Approved"
        db.session.add(request)
        db.session.commit()
        flash('Request has been approved.')
        return redirect(url_for('rb_dashboard'))

@app.route('/rb/delete/<int:id>')
@login_required
def delete_request(id):
        if current_user.is_authenticated and current_user.isAdmin == False:
            return redirect(url_for('user_dashboard'))
        request = Request.query.get(id)
        db.session.delete(request)
        book  = Book.query.filter_by(title = request.book_name).first()
        book.qty = book.qty + 1
        db.session.add(book)        
        db.session.commit()
        flash('Request has been deleted.')
        return redirect(url_for('rb_dashboard'))

@app.route('/rb/borrow/<int:id>')
@login_required
def borrow(id):
        request = Request.query.get(id)
        borrow = Borrowed(book_name = request.book_name, user_id = request.user_id)
        db.session.add(borrow)
        db.session.delete(request)
        db.session.commit()
        flash('A Book has been borrowed.')
        return redirect(url_for('rb_dashboard'))

@app.route('/rb/delete_borrowed/<int:id>')
@login_required
def delete_borrowed(id):
        if current_user.is_authenticated and current_user.isAdmin == False:
            return redirect(url_for('manage_book'))
        borrowed = Borrowed.query.get(id)
        db.session.delete(borrowed)
        book  = Book.query.filter_by(title = borrowed.book_name).first()
        book.qty = book.qty + 1
        db.session.add(book)
        db.session.commit()
        flash('Book has been returned.')
        return redirect(url_for('rb_dashboard'))

@app.route('/user/dashboard', methods=['GET', 'POST'])  
@login_required
def user_dashboard():
    if current_user.is_authenticated and  current_user.isAdmin == True :
        return redirect(url_for('manage_book'))
    books = Book.query.all()
    books_ordered = Book.query.order_by(Book.title).all()
    return render_template('user_dashboard.html', books_ordered =books_ordered, username=current_user.username)

@app.route('/user/book/request/<int:id>')
@login_required
def request_book(id):
    if current_user.is_authenticated and current_user.isAdmin == True:
        return redirect(url_for('manage_book'))
    book  = Book.query.get(id)
    request = Request(book_name = book.title , user_id=current_user.id, status  = "Pending")
    db.session.add(request)
    db.session.commit()
    book.qty = book.qty - 1
    db.session.add(book)
    db.session.commit()
    flash("Request Submitted.!")
    return redirect(url_for('user_dashboard'))



@app.route('/user/request')
@login_required
def user_request():
    if current_user.is_authenticated and current_user.isAdmin == True:
        return redirect(url_for('manage_book'))
    requests = Request.query.filter(Request.user_id == current_user.id).order_by(Request.status).all()
    return render_template('user_request.html', requests = requests, username=current_user.username)

@app.route('/user/currentbooks')
@login_required
def current_books():
    if current_user.is_authenticated and current_user.isAdmin == True:
        return redirect(url_for('manage_book'))
    borrow = Borrowed.query.filter(Borrowed.user_id == current_user.id).order_by(Borrowed.date).all()
    return render_template('user_current_books.html', current_books = borrow, username=current_user.username)

@app.route('/user/resetpassword', methods=['GET', 'POST'])
@login_required
def user_reset_password():
    if current_user.is_authenticated and current_user.isAdmin == True:
        return redirect(url_for('manage_book'))
    form = RPForm()
    if form.validate_on_submit():
        user = User.query.get(current_user.id)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Password has been reset")
        return redirect(url_for('user_reset_password'))
    return render_template('user_reset_password.html', form = form, username=current_user.username)
    

