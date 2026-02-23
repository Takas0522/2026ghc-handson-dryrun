import pytest
from app import create_app


@pytest.fixture
def client():
    """テスト用の Flask クライアントを生成する"""
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestIndex:
    """GET / のテスト"""

    def test_returns_200(self, client):
        """ステータスコード 200 を返すこと"""
        response = client.get('/')
        assert response.status_code == 200

    def test_content_type_is_html(self, client):
        """Content-Type が HTML であること"""
        response = client.get('/')
        assert 'text/html' in response.content_type

    def test_contains_app_title(self, client):
        """ページに「ポモドーロタイマー」が含まれること"""
        response = client.get('/')
        html = response.data.decode('utf-8')
        assert 'ポモドーロタイマー' in html

    def test_contains_timer_display(self, client):
        """ページにタイマー表示 (25:00) が含まれること"""
        response = client.get('/')
        html = response.data.decode('utf-8')
        assert '25:00' in html

    def test_contains_start_button(self, client):
        """ページに「開始」ボタンが含まれること"""
        response = client.get('/')
        html = response.data.decode('utf-8')
        assert '開始' in html

    def test_contains_reset_button(self, client):
        """ページに「リセット」ボタンが含まれること"""
        response = client.get('/')
        html = response.data.decode('utf-8')
        assert 'リセット' in html

    def test_contains_progress_section(self, client):
        """ページに「今日の進捗」セクションが含まれること"""
        response = client.get('/')
        html = response.data.decode('utf-8')
        assert '今日の進捗' in html

    def test_contains_mode_label(self, client):
        """ページにモード表示「作業中」が含まれること"""
        response = client.get('/')
        html = response.data.decode('utf-8')
        assert '作業中' in html

    def test_contains_css_link(self, client):
        """ページに CSS へのリンクが含まれること"""
        response = client.get('/')
        html = response.data.decode('utf-8')
        assert '/static/css/style.css' in html

    def test_contains_js_scripts(self, client):
        """ページに timer.js と ui.js のスクリプトタグが含まれること"""
        response = client.get('/')
        html = response.data.decode('utf-8')
        assert '/static/js/timer.js' in html
        assert '/static/js/ui.js' in html

    def test_contains_svg_timer(self, client):
        """ページに SVG タイマーリングが含まれること"""
        response = client.get('/')
        html = response.data.decode('utf-8')
        assert 'timer-ring' in html
        assert '<circle' in html


class TestStaticFiles:
    """静的ファイルのテスト"""

    def test_css_returns_200(self, client):
        """CSS ファイルが取得できること"""
        response = client.get('/static/css/style.css')
        assert response.status_code == 200

    def test_timer_js_returns_200(self, client):
        """timer.js が取得できること"""
        response = client.get('/static/js/timer.js')
        assert response.status_code == 200

    def test_ui_js_returns_200(self, client):
        """ui.js が取得できること"""
        response = client.get('/static/js/ui.js')
        assert response.status_code == 200


class TestAppFactory:
    """アプリファクトリのテスト"""

    def test_create_app_returns_flask_app(self):
        """create_app() が Flask アプリを返すこと"""
        app = create_app()
        assert app is not None
        assert app.name == 'app'

    def test_create_app_returns_different_instances(self):
        """create_app() が毎回異なるインスタンスを返すこと"""
        app1 = create_app()
        app2 = create_app()
        assert app1 is not app2
