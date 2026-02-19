from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.api_client import require_auth
from app.db import get_db

whitelist_bp = Blueprint('whitelist', __name__)

@whitelist_bp.route('/whitelist')
@require_auth
def list_whitelist():
    db = get_db()
    try:
        domains = db.execute(
            "SELECT * FROM domain_whitelist ORDER BY domain ASC",
            fetch=True
        )
        return render_template('whitelist.html', domains=domains or [])
    except Exception as e:
        flash(f'Error loading whitelist: {str(e)}', 'error')
        return render_template('whitelist.html', domains=[])
    finally:
        db.close()

@whitelist_bp.route('/whitelist/add', methods=['POST'])
@require_auth
def add_domain():
    domain = request.form.get('domain', '').strip().lower()
    notes = request.form.get('notes', '').strip()
    
    if not domain:
        flash('Domain is required', 'error')
        return redirect(url_for('whitelist.list_whitelist'))
    
    # Basic domain validation
    if '.' not in domain or ' ' in domain:
        flash('Invalid domain format', 'error')
        return redirect(url_for('whitelist.list_whitelist'))
    
    db = get_db()
    try:
        db.execute(
            "INSERT INTO domain_whitelist (domain, notes) VALUES (%s, %s)",
            (domain, notes)
        )
        flash(f'Domain "{domain}" added to whitelist', 'success')
    except Exception as e:
        if 'unique' in str(e).lower():
            flash(f'Domain "{domain}" is already whitelisted', 'warning')
        else:
            flash(f'Error adding domain: {str(e)}', 'error')
    finally:
        db.close()
    
    return redirect(url_for('whitelist.list_whitelist'))

@whitelist_bp.route('/whitelist/<int:domain_id>/remove', methods=['POST'])
@require_auth
def remove_domain(domain_id):
    db = get_db()
    try:
        db.execute(
            "DELETE FROM domain_whitelist WHERE id = %s",
            (domain_id,)
        )
        flash('Domain removed from whitelist', 'success')
    except Exception as e:
        flash(f'Error removing domain: {str(e)}', 'error')
    finally:
        db.close()
    
    return redirect(url_for('whitelist.list_whitelist'))

@whitelist_bp.route('/whitelist/check/<domain>')
@require_auth
def check_domain(domain):
    """Check if a domain is whitelisted"""
    db = get_db()
    try:
        result = db.execute_one(
            "SELECT * FROM domain_whitelist WHERE domain = %s",
            (domain.lower(),)
        )
        
        is_whitelisted = result is not None
        return {
            'domain': domain,
            'is_whitelisted': is_whitelisted,
            'entry': dict(result) if result else None
        }
    except Exception as e:
        return {'error': str(e)}, 500
    finally:
        db.close()
