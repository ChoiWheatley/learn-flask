import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

# 'auth'라는 이름을 가진 블루프린트를 생성한다.
bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    """`/auth/register`에 들어가면 회원가입 화면이 보이게끔."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        # validate that username and password are not empty
        if not username:
            error = "Username is required."
        elif not password:
            error = "Password is required."

        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                # redirect to the login page
                return redirect(url_for("auth.login"))

        # flash stores messages that can be retrieved when rendering the template
        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """`/auth/login`에 들어가면 로그인 화면이 보이게"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            # 정상적으로 로그인 된 상황. user_id가 새 세션에 저장이 된다.
            # 세션정보는 사용자의 브라우저의 쿠키에 저장이 된다고?
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    """현재 세션에 저장된 id와 세션 
    생성(login)시 저장했던 id를 서로 비교"""
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()


@bp.route('/logout')
def logout():
    """현재 세션을 버리고 초기 페이지로 돌아간다."""
    session.clear()
    return redirect(url_for('index'))


def login_required(view):
    """이 데코레이터 함수는 Creating, editing, deleting blog posts 에 대해
    로그인 여부를 조사해야함."""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
