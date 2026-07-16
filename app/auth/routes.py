from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

from app.auth.forms import LoginForm
from app.services.auth_service import authenticate_user
from app.models import Log
from app.utils.constants import MSG_LOGIN_SUCCESS, MSG_LOGOUT_SUCCESS

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if current_user.is_authenticated:
        return _redirect_by_role(current_user)

    form = LoginForm()

    if form.validate_on_submit():
        user = authenticate_user(form.username.data, form.password.data)
        if user:
            login_user(user, remember=True)
            Log.log(
                action='login',
                detail=f'Login berhasil untuk {user.username}',
                user_id=user.id,
                ip_address=request.remote_addr,
            )
            flash(MSG_LOGIN_SUCCESS, 'success')

            # Redirect to requested page or dashboard
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return _redirect_by_role(user)

        flash('Username atau password salah.', 'danger')

    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    """Handle user logout."""
    Log.log(
        action='logout',
        detail=f'Logout oleh {current_user.username}',
        user_id=current_user.id,
        ip_address=request.remote_addr,
    )
    logout_user()
    flash(MSG_LOGOUT_SUCCESS, 'info')
    return redirect(url_for('auth.login'))


def _redirect_by_role(user):
    """Redirect user to the appropriate dashboard based on their role."""
    if user.role == 'admin':
        return redirect(url_for('dashboard.admin_dashboard'))
    if user.role == 'dosen':
        return redirect(url_for('dashboard.dosen_dashboard'))
    return redirect(url_for('dashboard.mahasiswa_dashboard'))
