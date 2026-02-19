from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.api_client import MailServerAPI, AuthenticationError, APIError, require_auth

blacklist_bp = Blueprint('blacklist', __name__)
api = MailServerAPI()

@blacklist_bp.route('/blacklist')
@require_auth
def list_blacklist():
    try:
        source = request.args.get('source')
        page = request.args.get('page', 1, type=int)
        limit = 50
        
        # Get blacklist entries
        blacklist_data = api.get_blacklist(session['token'], source=source, page=page, limit=limit)
        
        # Get statistics
        stats_data = api.get_blacklist_stats(session['token'])
        
        # Handle both list and dict responses
        if isinstance(blacklist_data, list):
            entries_list = blacklist_data
            total_entries = len(blacklist_data)
        else:
            entries_list = blacklist_data.get('blacklisted_ips', [])
            total_entries = blacklist_data.get('total', len(entries_list))
        
        return render_template('blacklist.html',
                             entries=entries_list,
                             total=total_entries,
                             page=page,
                             limit=limit,
                             stats=stats_data,
                             current_source=source)
    except AuthenticationError:
        session.clear()
        flash('Session expired. Please log in again.', 'warning')
        return redirect(url_for('auth.login'))
    except APIError as e:
        flash(str(e), 'error')
        return render_template('blacklist.html', entries=[], total=0, page=1, limit=50, stats=None)

@blacklist_bp.route('/blacklist/<int:ip_id>/remove', methods=['POST'])
@require_auth
def remove_ip(ip_id):
    try:
        api.remove_from_blacklist(session['token'], ip_id)
        flash('IP removed from blacklist', 'success')
    except AuthenticationError:
        session.clear()
        flash('Session expired', 'warning')
    except APIError as e:
        flash(str(e), 'error')
    
    return redirect(url_for('blacklist.list_blacklist'))

@blacklist_bp.route('/blacklist/check')
@require_auth
def check_ip():
    ip_address = request.args.get('ip', '').strip()
    if not ip_address:
        flash('Please enter an IP address', 'error')
        return redirect(url_for('blacklist.list_blacklist'))
    
    try:
        result = api.check_ip_blacklist(session['token'], ip_address)
        is_blacklisted = result.get('is_blacklisted', False)
        
        if is_blacklisted:
            flash(f'IP {ip_address} is blacklisted: {result.get("entry", {}).get("reason", "No reason given")}', 'warning')
        else:
            flash(f'IP {ip_address} is not blacklisted', 'success')
        
        return redirect(url_for('blacklist.list_blacklist'))
    except AuthenticationError:
        session.clear()
        flash('Session expired', 'warning')
        return redirect(url_for('auth.login'))
    except APIError as e:
        flash(str(e), 'error')
        return redirect(url_for('blacklist.list_blacklist'))
