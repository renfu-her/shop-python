# Flask 應用程式調試指南

## 1. 啟用 Debug 模式

### 方法一：使用 run.py（開發環境）
```bash
python run.py
```
`run.py` 已經配置了 `debug=True`，會自動啟用：
- 自動重載（代碼變更自動重啟）
- 詳細錯誤頁面
- 調試器（可在瀏覽器中使用）

### 方法二：設置環境變數
```bash
# Windows (PowerShell)
$env:FLASK_DEBUG="true"
python run.py

# Windows (CMD)
set FLASK_DEBUG=true
python run.py

# Linux/Mac
export FLASK_DEBUG=true
python run.py
```

### 方法三：直接在代碼中啟用
在 `run.py` 中已經設置了 `debug=True`

## 2. 使用 Python Debugger (pdb)

### 在代碼中插入斷點
```python
import pdb; pdb.set_trace()
```

### 範例：在控制器中添加斷點
```python
from app.controllers.product_controller import product_bp

@product_bp.route('/')
def index():
    import pdb; pdb.set_trace()  # 斷點
    # 你的代碼...
```

### pdb 常用命令
- `n` (next): 執行下一行
- `s` (step): 進入函數內部
- `c` (continue): 繼續執行
- `l` (list): 顯示當前代碼
- `p variable_name`: 打印變數值
- `pp variable_name`: 美化打印變數
- `q` (quit): 退出調試器

## 3. 使用 Flask Debug Toolbar（可選）

### 安裝
```bash
pip install flask-debugtoolbar
```

### 配置（添加到 requirements.txt 和 app/__init__.py）
```python
from flask_debugtoolbar import DebugToolbarExtension

if app.debug:
    toolbar = DebugToolbarExtension(app)
```

## 4. 日誌記錄

### 使用 Flask 內建 logger
```python
from flask import current_app

@app.route('/example')
def example():
    current_app.logger.debug('Debug message')
    current_app.logger.info('Info message')
    current_app.logger.warning('Warning message')
    current_app.logger.error('Error message')
    return 'Check console/logs'
```

### 查看日誌
- 開發模式：日誌會顯示在終端機
- 生產模式：日誌保存在 `logs/shop.log`

## 5. 瀏覽器開發者工具

### Chrome/Edge DevTools
- `F12` 或 `Ctrl+Shift+I` (Windows)
- `Cmd+Option+I` (Mac)
- 查看 Console、Network、Application 等標籤

### 檢查 Flask 錯誤頁面
當發生錯誤時，Flask debug 模式會顯示：
- 錯誤堆疊追蹤
- 本地變數值
- 互動式調試器（可在瀏覽器中執行 Python 代碼）

## 6. 常見調試場景

### 調試資料庫查詢
```python
# 在 config.py 中設置 SQLALCHEMY_ECHO = True
# 會打印所有 SQL 查詢到控制台
```

### 調試模板渲染
```python
# 在模板中使用
{{ variable|pprint }}  # 美化打印變數
{{ variable|tojson|safe }}  # 查看 JSON 格式
```

### 調試表單提交
```python
# 在路由中添加
@app.route('/submit', methods=['POST'])
def submit():
    print(request.form)  # 查看表單數據
    print(request.files)  # 查看文件上傳
    return 'Check console'
```

### 調試 Session
```python
from flask import session

# 查看 session 內容
print(session)
print(session.get('member_id'))
```

## 7. 錯誤處理最佳實踐

### 添加自定義錯誤處理器
```python
@app.errorhandler(500)
def internal_error(error):
    import traceback
    app.logger.error(traceback.format_exc())
    return render_template('errors/500.html'), 500
```

### 使用 try-except
```python
try:
    # 你的代碼
    result = some_function()
except Exception as e:
    app.logger.error(f'Error: {str(e)}', exc_info=True)
    flash('發生錯誤，請重試', 'error')
    return redirect(url_for('index'))
```

## 8. 使用 VS Code 調試器

### 創建 .vscode/launch.json
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Flask",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/run.py",
            "env": {
                "FLASK_APP": "run.py",
                "FLASK_ENV": "development",
                "FLASK_DEBUG": "1"
            },
            "args": [],
            "jinja": true,
            "justMyCode": false
        }
    ]
}
```

然後按 `F5` 開始調試。

## 9. 快速調試技巧

### 檢查變數值
```python
print(f"Variable value: {variable}")
app.logger.debug(f"Variable value: {variable}")
```

### 檢查請求數據
```python
print(f"Request method: {request.method}")
print(f"Request args: {request.args}")
print(f"Request form: {request.form}")
print(f"Request json: {request.json}")
```

### 檢查資料庫連接
```python
from app.utils.db import get_db_connection
conn = get_db_connection()
print(f"Database connected: {conn is not None}")
conn.close()
```

## 10. 性能調試

### 使用 Flask-Profiler
```bash
pip install flask-profiler
```

### 檢查慢查詢
啟用 SQLAlchemy echo 模式查看所有 SQL 查詢

## 注意事項

⚠️ **安全警告**：
- **永遠不要**在生產環境啟用 `debug=True`
- Debug 模式會暴露敏感信息
- 使用環境變數控制 debug 模式

✅ **最佳實踐**：
- 開發環境：啟用 debug 模式
- 測試環境：關閉 debug，啟用日誌
- 生產環境：關閉 debug，使用適當的錯誤處理和日誌記錄

