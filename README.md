# IMDB 电影数据库项目

一个全栈电影数据库 Web 应用，支持电影浏览、搜索、用户评分收藏，以及 AI 智能问答功能。

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | React + Vite + React Router |
| 后端 | Flask + Flask-CORS |
| 数据库 | MySQL |
| AI | Anthropic Claude API |

---

## 项目结构

```
imdb_database/
├── backend/                    # Flask 后端
│   ├── app.py                  # Flask 应用入口，注册蓝图和 CORS
│   ├── config.py               # 数据库连接、AI API Key 等配置
│   ├── db.py                   # MySQL 数据库连接工具
│   ├── requirements.txt        # Python 依赖列表
│   ├── models/
│   │   ├── movie.py            # 电影相关数据库操作（查询、筛选、评分等）
│   │   └── user.py             # 用户相关数据库操作（注册、登录、收藏等）
│   ├── routes/
│   │   ├── movie_routes.py     # 电影 API 路由（/api/movies/*）
│   │   ├── user_routes.py      # 用户 API 路由（/api/users/*）
│   │   └── ai_routes.py        # AI 问答 API 路由（/api/ai/*）
│   └── utils/
│       ├── auth.py             # JWT Token 生成与验证工具
│       └── ai_helper.py        # Claude AI 接口封装
│
├── frontend/                   # React 前端
│   ├── package.json            # Node.js 依赖和脚本
│   ├── vite.config.js          # Vite 构建配置（含 API 代理）
│   ├── index.html              # HTML 入口
│   └── src/
│       ├── main.jsx            # React 应用挂载入口
│       ├── App.jsx             # 根组件，定义路由结构
│       ├── api/
│       │   ├── movieApi.js     # 封装电影相关 HTTP 请求
│       │   └── userApi.js      # 封装用户相关 HTTP 请求
│       ├── context/
│       │   └── AuthContext.jsx # 全局用户认证状态管理（Context + localStorage）
│       ├── components/
│       │   ├── Navbar.jsx      # 顶部导航栏（含登录状态显示）
│       │   ├── MovieCard.jsx   # 电影卡片组件（封面、标题、评分）
│       │   └── SearchBar.jsx   # 搜索框组件
│       └── pages/
│           ├── MovieList.jsx   # 电影列表页（搜索、筛选、分页）
│           ├── MovieDetail.jsx # 电影详情页（评论、评分、收藏）
│           ├── AIPage.jsx      # AI 智能问答页面
│           ├── Login.jsx       # 登录页面
│           ├── Register.jsx    # 注册页面
│           └── Profile.jsx     # 个人主页（收藏、评分历史）
│
├── apidoc/                     # API 文档（apidoc 生成的静态页面）
│   └── index.html              # API 文档入口
│
└── .gitignore                  # Git 忽略配置
```

---

## 主要功能

- **电影浏览**：分页展示电影列表，支持按标题、类型、年份筛选和搜索
- **电影详情**：查看电影详细信息、用户评论和评分
- **用户系统**：注册、登录（JWT 认证）、个人资料页
- **收藏与评分**：登录用户可收藏电影、提交评分和评论
- **AI 问答**：集成 Claude API，支持自然语言查询电影相关信息

---

## 快速启动

### 后端

```bash
cd backend
pip install -r requirements.txt
python app.py
```

后端默认运行在 `http://localhost:5000`

### 前端

```bash
cd frontend
npm install
npm run dev
```

前端默认运行在 `http://localhost:5173`，已配置代理将 `/api` 请求转发至后端。

---

## 环境配置

在 `backend/config.py` 中配置以下内容：

```python
DB_HOST = "localhost"
DB_USER = "your_db_user"
DB_PASSWORD = "your_db_password"
DB_NAME = "imdb_database"
JWT_SECRET = "your_jwt_secret"
CLAUDE_API_KEY = "your_anthropic_api_key"
```

---

## API 文档

完整 API 文档见 `apidoc/index.html`，主要接口：

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/movies` | 获取电影列表（支持分页、筛选） |
| GET | `/api/movies/:id` | 获取电影详情 |
| POST | `/api/users/register` | 用户注册 |
| POST | `/api/users/login` | 用户登录 |
| GET | `/api/users/profile` | 获取当前用户信息 |
| POST | `/api/users/favorites` | 添加收藏 |
| POST | `/api/movies/:id/reviews` | 提交评分/评论 |
| POST | `/api/ai/chat` | AI 问答 |
