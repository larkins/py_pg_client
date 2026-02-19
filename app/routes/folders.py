from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.api_client import MailServerAPI, AuthenticationError, APIError, require_auth

folders_bp = Blueprint('folders', __name__)
api = MailServerAPI()

@folders_bp.route('/folders')
@require_auth
def list_folders():
    try:
        folders_data = api.get_folders(session['token'])
        # Handle both list and dict responses
        if isinstance(folders_data, list):
            folders_list = folders_data
        else:
            folders_list = folders_data.get('folders', [])
        return render_template('folders.html', folders=folders_list)
    except AuthenticationError:
        session.clear()
        flash('Session expired. Please log in again.', 'warning')
        return redirect(url_for('auth.login'))
    except APIError as e:
        flash(str(e), 'error')
        return render_template('folders.html', folders=[])

@folders_bp.route('/folders/create', methods=['POST'])
@require_auth
def create_folder():
    name = request.form.get('name', '').strip()
    if not name:
        flash('Folder name is required', 'error')
        return redirect(url_for('folders.list_folders'))
    
    try:
        api.create_folder(session['token'], name)
        flash(f'Folder "{name}" created', 'success')
    except AuthenticationError:
        session.clear()
        flash('Session expired', 'warning')
    except APIError as e:
        flash(str(e), 'error')
    
    return redirect(url_for('folders.list_folders'))

@folders_bp.route('/folders/<int:folder_id>/delete', methods=['POST'])
@require_auth
def delete_folder(folder_id):
    try:
        api.delete_folder(session['token'], folder_id)
        flash('Folder deleted', 'success')
    except AuthenticationError:
        session.clear()
        flash('Session expired', 'warning')
    except APIError as e:
        flash(str(e), 'error')
    
    return redirect(url_for('folders.list_folders'))
