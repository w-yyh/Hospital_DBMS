from flask import render_template, Blueprint, jsonify, current_app
from app.utils.db import Database

bp = Blueprint('front', __name__)

@bp.route('/')
def index():
    """首页"""
    try:
        return render_template('dashboard.html')
    except Exception as e:
        current_app.logger.error(f"Error rendering template: {str(e)}")
        return f"Error loading page: {str(e)}", 500

@bp.route('/api/stats')
def get_stats():
    """获取基本统计信息"""
    try:
        stats = {
            'doctors': Database.fetch_one("SELECT COUNT(*) as count FROM doctors")['count'],
            'patients': Database.fetch_one("SELECT COUNT(*) as count FROM patients")['count'],
            'nurses': Database.fetch_one("SELECT COUNT(*) as count FROM nurses")['count'],
            'departments': Database.fetch_one("SELECT COUNT(*) as count FROM departments")['count']
        }
        return jsonify(stats)
    except Exception as e:
        current_app.logger.error(f"Error getting stats: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/test')
def test():
    """简单的测试页面"""
    return """
    <html>
        <body>
            <h1>测试页面</h1>
            <p>如果你能看到这个页面，说明服务器运行正常。</p>
        </body>
    </html>
    """