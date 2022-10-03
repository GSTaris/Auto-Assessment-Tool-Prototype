# encoding: utf-8
from flask import  session, flash, session, flash, redirect, url_for
from functools import wraps

from flask_sqlalchemy import SQLAlchemy 
db = SQLAlchemy(use_native_unicode='utf8')

def require_login(func):
    @wraps(func)
    def inner_func(*args, **kwargs):
        if not 'username' in session:
            flash('Please login it firslty!', 'danger')
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return inner_func
